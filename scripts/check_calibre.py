#!/usr/bin/env python3
"""
Verify Calibre-Web connectivity and search for specific books.
Usage: python scripts/check_calibre.py
       python scripts/check_calibre.py "fire upon the deep"
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.recommender import _get_session_cookies, get_recommendations
from config.settings import get_settings
import httpx


async def search_book(query: str):
    settings = get_settings()
    base_url = settings.calibre_web_url.rstrip("/")
    print(f"Connecting to Calibre-Web at {base_url} ...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        cookies = await _get_session_cookies(client)
        if not cookies:
            print("ERROR: Could not authenticate with Calibre-Web.")
            print(f"  URL:  {base_url}")
            print(f"  User: {settings.calibre_web_admin_user}")
            return

        print(f"Authenticated. Searching for: '{query}' ...")
        resp = await client.get(
            f"{base_url}/ajax/listbooks",
            params={"offset": 0, "limit": 20, "search": query},
            cookies=cookies,
        )
        resp.raise_for_status()
        data = resp.json()
        rows = data.get("rows", [])
        total = data.get("total", 0)

        print(f"Found {total} result(s):\n")
        for book in rows:
            title   = book.get("title", "Unknown")
            authors = book.get("authors", [])
            author  = authors[0].get("name", "Unknown") if authors else "Unknown"
            tags    = ", ".join(book.get("tags", [])) or "—"
            pages   = book.get("page_count") or "?"
            bid     = book.get("id", "?")
            print(f"  [{bid}] {title}")
            print(f"       Author : {author}")
            print(f"       Tags   : {tags}")
            print(f"       Pages  : {pages}")
            print()


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "fire upon the deep"
    asyncio.run(search_book(query))
