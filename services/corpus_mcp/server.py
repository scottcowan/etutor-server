"""stdio MCP server wiring the 5 D-13 tool functions to the `mcp` SDK.

**Live API verification note (resolves RESEARCH.md Open Question 2):** The
04.1-RESEARCH.md code examples assumed a training-era `mcp` 1.x pattern —
`from mcp.server.fastmcp import FastMCP`. That import path does NOT exist in
the installed 2.1.1 release; importing it raises a `ModuleNotFoundError`
whose message explains the class was renamed:

    FastMCP was renamed to MCPServer (from mcp.server.mcpserver import
    MCPServer) and other APIs changed.

This was confirmed live via `pip show mcp` (Version: 2.1.1) and
`help(MCPServer)` on the installed package before writing any code below —
the decorator is `@mcp_app.tool()` (unchanged in spirit from the 1.x
pattern) and the run entrypoint is the synchronous `mcp_app.run(transport=
"stdio")` (default transport is already "stdio", passed explicitly here for
clarity).

The index is built once at import time (module-level `INDEX`), and each
tool below is a thin pass-through wrapper over the matching
`services/corpus_mcp/tools.py` `*_impl` function (Pattern 2) — no logic
lives here, so `tools.py` stays independently testable without a running
MCP process.
"""

from pathlib import Path
from typing import Optional

from mcp.server.mcpserver import MCPServer

from services.corpus_mcp.index import build_index
from services.corpus_mcp.tools import (
    get_experiments_impl,
    get_topic_impl,
    list_sources_impl,
    list_topics_impl,
    search_corpus_impl,
)

# Built once at module load. `docs/corpus` is the root containing the
# `wiki/` subdirectory (per index.py's build_index docstring and the
# FIXTURE_ROOT convention used in tests/services/test_corpus_mcp.py).
INDEX = build_index(Path("docs/corpus"))

mcp_app = MCPServer(name="etutor-corpus")


@mcp_app.tool()
def get_topic(topic_id: str, level: Optional[str] = None) -> dict:
    """Return the L3 wiki page for `topic_id`, optionally a single level-band section."""
    return get_topic_impl(INDEX, topic_id, level=level)


@mcp_app.tool()
def list_sources(topic_id: str, type_: Optional[str] = None) -> list:
    """Return source entries tagged to `topic_id`, optionally filtered by `type_`."""
    return list_sources_impl(INDEX, topic_id, type_=type_)


@mcp_app.tool()
def search_corpus(
    query: str,
    subject: Optional[str] = None,
    level: Optional[int] = None,
    type_: Optional[str] = None,
) -> list:
    """Free-text keyword search across all corpus buckets."""
    return search_corpus_impl(INDEX, query, subject=subject, level=level, type_=type_)


@mcp_app.tool()
def get_experiments(topic_id: str, min_age: Optional[int] = None) -> list:
    """Return age-gated experiments tagged to `topic_id`."""
    return get_experiments_impl(INDEX, topic_id, min_age=min_age)


@mcp_app.tool()
def list_topics(subject: Optional[str] = None) -> list:
    """List all topic IDs in the corpus, optionally filtered by `subject`."""
    return list_topics_impl(INDEX, subject=subject)


if __name__ == "__main__":
    mcp_app.run(transport="stdio")
