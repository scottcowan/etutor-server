"""Plain keyword search over the in-memory corpus index (04.1-CONTEXT.md D-14).

No vector embeddings, no fuzzy matching (rapidfuzz explicitly rejected for
v1) — substring matching against content + tags/topic_ids, case-insensitive.
Takes the index as an explicit function argument (not a module-level global)
so it can be exercised in tests without a running MCP process.
"""

from typing import Optional


def search_corpus_impl(
    index: dict,
    query: str,
    subject: Optional[str] = None,
    level: Optional[int] = None,
    type_: Optional[str] = None,
) -> list:
    """Search every bucket/entry in `index` for `query`.

    Metadata filters (`subject`, `level`, `type_`) are applied first — an
    entry is skipped entirely if a provided filter doesn't match, even if
    the raw query would otherwise match its content.
    """
    query_lower = query.lower()
    results = []

    for bucket_name, bucket in index.items():
        for key, entry in bucket.items():
            metadata = entry["metadata"]

            if subject is not None and metadata.get("subject") != subject:
                continue
            if level is not None and metadata.get("level") != level:
                continue
            if type_ is not None and metadata.get("type") != type_:
                continue

            tags = metadata.get("tags", []) or []
            topic_ids = metadata.get("topic_ids", []) or []
            haystack = (entry["content"] + " " + " ".join(tags + topic_ids)).lower()

            if query_lower in haystack:
                results.append({"bucket": bucket_name, "id": key, "metadata": metadata})

    return results
