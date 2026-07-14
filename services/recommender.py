import httpx
from config.settings import get_settings
from db.models import ChildProfileModel


async def get_recommendations(child: ChildProfileModel, limit: int = 5) -> list[dict]:
    """
    Fetch books from Calibre-Web matching child's interests and reading level.
    Falls back to empty list if Calibre-Web is unavailable.
    """
    settings = get_settings()
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{settings.calibre_web_url}/api/books",
                auth=(settings.calibre_web_admin_user, settings.calibre_web_admin_password),
                params={"per_page": 50},
            )
            resp.raise_for_status()
            books = resp.json().get("books", [])
    except Exception:
        return []

    # Score books by interest match
    interest_words = set(" ".join(child.interests).lower().split())
    scored = []
    for book in books:
        title = book.get("title", "").lower()
        tags = " ".join(book.get("tags", [])).lower()
        text = f"{title} {tags}"
        score = sum(1 for w in interest_words if w in text)
        if score > 0:
            scored.append((score, book))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [b for _, b in scored[:limit]]


async def build_recommendation_message(child: ChildProfileModel) -> str:
    books = await get_recommendations(child)
    if not books:
        return ""
    titles = ", ".join(f'"{b["title"]}"' for b in books[:3])
    return f"Based on your interest in {child.interests[0]}, you might enjoy: {titles}."
