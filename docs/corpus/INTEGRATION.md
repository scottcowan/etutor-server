# Corpus Integration Point — Phase 5 SYNC-03

**Status:** This phase (04.1) does NOT implement SYNC-03 (device sync content
packages). It only guarantees that the corpus structure Phase 5 will consume
is stable and won't require a schema change (D-15).

## What Phase 5 needs to build

`api/sync.py`'s `sync_device` endpoint currently returns `"packages": []`
with a comment: `# content packages — populated when learning plan system is
built`. Phase 5's SYNC-03 work is to populate that list by bundling relevant
corpus content for a child's current focus knowledge components (KCs).

## Two supported consumption paths (D-15)

Both are valid; pick whichever fits the sync endpoint's runtime shape best.
Neither requires a schema change to the corpus itself.

### Path A — Import the tool-implementation functions directly (recommended)

Since `api/sync.py` runs in the same FastAPI process/deployment as the
corpus, there is no need to spawn the MCP stdio subprocess or go over
JSON-RPC. Import the plain functions directly:

```python
from pathlib import Path
from services.corpus_mcp.index import build_index
from services.corpus_mcp.tools import get_topic_impl, get_experiments_impl, list_sources_impl

INDEX = build_index(Path("docs/corpus"))  # build once, e.g. at app startup / module load

topic_page = get_topic_impl(INDEX, focus_kc_id, level="200")
experiments = get_experiments_impl(INDEX, focus_kc_id, min_age=child.age)
sources = list_sources_impl(INDEX, focus_kc_id)
```

This is the same in-memory index the MCP server (`services/corpus_mcp/server.py`)
builds at import time — same-process Python import, no subprocess/stdio
involved. See `services/corpus_mcp/tools.py` for the full function contract
(D-13):

- `get_topic_impl(index, topic_id, level=None) -> dict`
- `list_sources_impl(index, topic_id, type_=None) -> list`
- `search_corpus_impl(index, query, subject=None, level=None, type_=None) -> list`
- `get_experiments_impl(index, topic_id, min_age=None) -> list`
- `list_topics_impl(index, subject=None) -> list`

### Path B — Glob the corpus directories directly

If Phase 5 prefers not to depend on `services/corpus_mcp` internals, the two
directories that matter for content packages are:

- `docs/corpus/wiki/topics/<topic_id>.md` — one page per curriculum topic ID,
  with H2 level-band sections (`## 100 — Introduction`, `## 200 — Developing`,
  etc. per `04.1-CONTEXT.md` D-03)
- `docs/corpus/wiki/experiments/<slug>.md` — age-gated practical activities,
  frontmatter includes `topic_ids`, `min_age`, `flagged_dangerous` (D-07)

Each file uses YAML frontmatter (parsed via the `frontmatter` package, same
as `services/corpus_mcp/index.py::build_index`). A given topic's page is
`docs/corpus/wiki/topics/{topic_id}.md`, matching `services/curriculum.py`
`Topic.id` exactly (04.1-CONTEXT.md canonical refs).

## Age gating carries through automatically

`get_experiments_impl`'s `min_age` parameter already implements D-06's dual
gate (hard gate for `flagged_dangerous: true`, permissive otherwise) — Phase
5 does not need to re-implement age-gating logic if it uses Path A. If Phase
5 uses Path B (direct glob), it must re-implement the same D-06 gate itself
by reading each experiment's frontmatter.

## What does NOT change

- No new corpus directories, no new frontmatter fields, no schema migration
  is required to support SYNC-03. The `topics/` and `experiments/` structure
  already carries everything a content package needs (topic_ids, min_age,
  flagged_dangerous, level bands).
- If Phase 5 needs additional fields later (e.g. estimated read time), that
  is an additive frontmatter change, not a breaking one — existing readers
  (this phase's MCP tools) will simply ignore unknown keys via `post.metadata`.

## Out of scope for this phase

- The actual `packages: [...]` bundling logic in `api/sync.py` (SYNC-03 itself)
- Any caching/invalidation strategy for `INDEX` if corpus content changes
  after server startup (v1 builds the index once at import time, per D-14 —
  Phase 5 should decide whether a hot-reload is needed for its use case)
