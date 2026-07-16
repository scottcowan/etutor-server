import re
import time
from typing import Optional

import httpx

from config.settings import get_settings
from db.models import ChildProfileModel

# ---------------------------------------------------------------------------
# Module-level session cookie cache — re-auth only when cookie expires
# ---------------------------------------------------------------------------
_session_cookies: Optional[httpx.Cookies] = None
_session_cookie_expires: float = 0.0
_SESSION_TTL: float = 3600.0  # seconds before forcing a re-auth

# ---------------------------------------------------------------------------
# Reading level → approximate max page count (rough heuristic)
# Calibre-Web books rarely carry page_count, so this is a best-effort filter
# that falls back gracefully when the field is absent.
# ---------------------------------------------------------------------------
_GRADE_PAGE_LIMITS: dict[str, int] = {
    "grade 1": 64,
    "grade 2": 96,
    "grade 3": 128,
    "grade 4": 200,
    "grade 5": 280,
    "grade 6": 350,
    "grade 7": 450,
    "grade 8": 550,
    "grade 9": 650,
    "grade 10": 750,
    "grade 11": 900,
    "grade 12": 1000,
}


def _grade_page_limit(reading_level: str) -> Optional[int]:
    """Return approximate max page count for a reading level string, or None."""
    return _GRADE_PAGE_LIMITS.get(reading_level.lower().strip())


async def _get_session_cookies(client: httpx.AsyncClient) -> Optional[httpx.Cookies]:
    """
    Authenticate with Calibre-Web and return a valid session Cookies object.

    Caches the result module-level; re-authenticates only after _SESSION_TTL
    seconds have elapsed.  Returns None on any failure so callers can bail out
    cleanly.
    """
    global _session_cookies, _session_cookie_expires

    # Return cached cookies if still valid
    if _session_cookies is not None and time.monotonic() < _session_cookie_expires:
        return _session_cookies

    settings = get_settings()
    base_url = settings.calibre_web_url.rstrip("/")

    try:
        # Step 1: GET /login to harvest the CSRF token
        get_resp = await client.get(f"{base_url}/login")
        get_resp.raise_for_status()

        # Try both common patterns Calibre-Web uses for the hidden CSRF field
        match = re.search(r'name="csrf_token"[^>]+value="([^"]+)"', get_resp.text)
        if not match:
            match = re.search(r'csrf_token["\s]+value="([^"]+)"', get_resp.text)
        if not match:
            return None
        csrf = match.group(1)

        # Step 2: POST credentials with the CSRF token
        post_resp = await client.post(
            f"{base_url}/login",
            data={
                "username": settings.calibre_web_admin_user,
                "password": settings.calibre_web_admin_password,
                "remember_me": "on",
                "csrf_token": csrf,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            follow_redirects=False,
            cookies=get_resp.cookies,
        )

        # A successful login produces a 302 redirect (or occasionally 200)
        if post_resp.status_code not in (200, 302):
            return None

        _session_cookies = post_resp.cookies
        _session_cookie_expires = time.monotonic() + _SESSION_TTL
        return _session_cookies

    except Exception:
        return None


def _score_book(book: dict, interest_words: set) -> int:
    """
    Count how many interest words appear in the book's title, tags, and
    comments (case-insensitive).  Higher score = better match.
    """
    title = book.get("title", "").lower()

    raw_tags = book.get("tags", "")
    tags = " ".join(raw_tags).lower() if isinstance(raw_tags, list) else str(raw_tags).lower()

    comments = book.get("comments", "").lower()

    text = f"{title} {tags} {comments}"
    return sum(1 for w in interest_words if w in text)


async def get_recommendations(child: ChildProfileModel, limit: int = 5) -> list[dict]:
    """
    Fetch books from Calibre-Web that match the child's interests and reading
    level.  Returns an empty list on any error — never raises.

    Algorithm:
    1. Authenticate (cached session cookie).
    2. Search /ajax/listbooks with interest terms; paginate up to 500 results.
    3. Remove titles already in child.current_books.
    4. Apply optional page-count cap derived from reading_level.
    5. Score each remaining book by interest-word overlap.
    6. Return the top `limit` books by score.
    """
    if not child.interests:
        return []

    settings = get_settings()
    base_url = settings.calibre_web_url.rstrip("/")

    interest_words: set = set(" ".join(child.interests).lower().split())
    # Calibre-Web search works best with a few focused terms
    search_query = " ".join(child.interests[:3])

    current_titles: set = {t.lower().strip() for t in (child.current_books or [])}
    page_limit = _grade_page_limit(child.reading_level or "")

    all_books: list[dict] = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            cookies = await _get_session_cookies(client)
            if cookies is None:
                return []

            offset = 0
            fetch_limit = 100

            while True:
                resp = await client.get(
                    f"{base_url}/ajax/listbooks",
                    params={"offset": offset, "limit": fetch_limit, "search": search_query},
                    cookies=cookies,
                )
                resp.raise_for_status()
                data = resp.json()

                rows: list[dict] = data.get("rows", [])
                total: int = data.get("total", 0)

                all_books.extend(rows)

                # Stop when we have all results, hit our safety cap, or got no rows
                if not rows or len(all_books) >= total or len(all_books) >= 500:
                    break

                offset += fetch_limit

    except Exception:
        return []

    # Filter out books the child is already reading
    filtered = [
        b for b in all_books
        if b.get("title", "").lower().strip() not in current_titles
    ]

    # Apply reading-level page-count cap when data is available
    if page_limit is not None:
        level_filtered = [
            b for b in filtered
            if b.get("page_count") is None or int(b.get("page_count") or 0) <= page_limit
        ]
        # Fall back to the unfiltered list if page data is missing for everything
        if level_filtered:
            filtered = level_filtered

    # Score and rank
    scored = sorted(
        ((b, _score_book(b, interest_words)) for b in filtered),
        key=lambda x: x[1],
        reverse=True,
    )
    # Drop zero-score books (no interest overlap at all)
    scored = [(b, s) for b, s in scored if s > 0]

    return [b for b, _ in scored[:limit]]


async def build_recommendation_message(child: ChildProfileModel) -> str:
    books = await get_recommendations(child)
    if not books or not child.interests:
        return ""
    titles = ", ".join(f'"{b["title"]}"' for b in books[:3])
    return f"Based on your interest in {child.interests[0]}, you might enjoy: {titles}."
