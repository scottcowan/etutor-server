"""In-memory index builder for the knowledge corpus (04.1-CONTEXT.md D-14).

Scans a corpus root directory once (no DB, no per-request rescans) and builds
a plain dict keyed by bucket ("topics", "sources", "experiments", "people"),
each mapping filename stem -> {"metadata", "content", "path"}.

No MCP/stdio dependency here — this module is a pure filesystem-to-dict
transform so it can be unit tested without a running MCP process.
"""

from pathlib import Path

import frontmatter

BUCKETS = ("topics", "sources", "experiments", "people")


def build_index(root: Path) -> dict:
    """Build the in-memory corpus index rooted at `root`.

    `root` is expected to contain a `wiki/` subdirectory with one folder per
    bucket (topics/sources/experiments/people). Buckets are always present
    in the returned dict, even if the corresponding directory doesn't exist
    on disk (callers should never need `index.get("people", {})`).

    Never touches the real docs/corpus/ tree directly — `root` is always an
    explicit parameter, so tests can point this at a synthetic fixture tree.
    """
    index: dict = {bucket: {} for bucket in BUCKETS}

    for md_file in root.rglob("*.md"):
        if md_file.name == "index.md":
            continue

        bucket = md_file.parent.name
        if bucket not in index:
            continue

        key = md_file.stem
        post = frontmatter.load(md_file)
        index[bucket][key] = {
            "metadata": post.metadata,
            "content": post.content,
            "path": md_file,
        }

    return index
