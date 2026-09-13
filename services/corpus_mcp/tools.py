"""5 locked MCP tool-implementation functions (04.1-CONTEXT.md D-13).

Plain, independently-testable Python functions built on top of the
index/search primitives from 04.1-02 — no MCP/FastMCP decorator wiring here
(that is 04.1-04's job, per research Pattern 2: keep tool logic decoupled
from transport).

All lookups go through `index[bucket].get(key)` — never `Path(root) /
f"{arg}.md"` — so a caller-supplied topic_id can never be used to construct
a filesystem path. This makes path traversal structurally impossible
(04.1-RESEARCH.md Security Domain, T-04.1-05).
"""

from typing import Optional

from services.corpus_mcp.search import search_corpus_impl as search_corpus_impl  # noqa: F401  (thin re-export, D-13)


def get_topic_impl(index: dict, topic_id: str, level: Optional[str] = None) -> dict:
    """Return the full L3 wiki page entry for `topic_id`.

    If `level` is provided, return only the matching `## {level} —` H2
    section content instead of the whole page. A missing `topic_id` (or a
    path-traversal-style string) returns a not-found error dict — it never
    raises and never touches the filesystem, because the lookup is a plain
    dict `.get()` against the pre-built index, not a `Path` construction.
    """
    entry = index["topics"].get(topic_id)
    if entry is None:
        return {"error": f"topic not found: {topic_id}"}

    if level is None:
        return entry

    heading_prefix = f"## {level} "
    lines = entry["content"].splitlines()
    section_lines: list = []
    in_section = False
    for line in lines:
        if line.startswith("## "):
            in_section = line.startswith(heading_prefix)
            if not in_section:
                continue
        if in_section:
            section_lines.append(line)

    section_content = "\n".join(section_lines).strip()
    return {**entry, "content": section_content}


def list_sources_impl(
    index: dict, topic_id: str, type_: Optional[str] = None
) -> list:
    """Return source entries tagged to `topic_id`, optionally filtered by `type`."""
    results = []
    for key, entry in index["sources"].items():
        metadata = entry["metadata"]
        if topic_id not in (metadata.get("topic_ids") or []):
            continue
        if type_ is not None and metadata.get("type") != type_:
            continue
        results.append({"id": key, "metadata": metadata, "content": entry["content"]})
    return results


def get_experiments_impl(
    index: dict, topic_id: str, min_age: Optional[int] = None
) -> list:
    """Return age-gated experiment entries tagged to `topic_id`.

    D-06 hard gate: when `min_age` is provided, an entry flagged
    `flagged_dangerous: true` is excluded whenever the requested `min_age`
    is below the entry's own `min_age`.
    D-06 permissive gate: non-dangerous entries are returned regardless of
    `min_age`.
    """
    results = []
    for key, entry in index["experiments"].items():
        metadata = entry["metadata"]
        if topic_id not in (metadata.get("topic_ids") or []):
            continue

        if (
            min_age is not None
            and metadata.get("flagged_dangerous")
            and min_age < metadata.get("min_age", 0)
        ):
            continue

        results.append({"id": key, "metadata": metadata, "content": entry["content"]})
    return results


def list_topics_impl(index: dict, subject: Optional[str] = None) -> list:
    """Return all topic ids in the index's "topics" bucket, optionally filtered by subject."""
    results = []
    for key, entry in index["topics"].items():
        if subject is not None and entry["metadata"].get("subject") != subject:
            continue
        results.append(key)
    return results
