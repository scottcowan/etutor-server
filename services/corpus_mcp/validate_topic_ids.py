"""Topic-ID drift check (04.1-CONTEXT.md D-13/CORPUS-04, 04.1-RESEARCH.md Pitfall 3).

Diffs `docs/corpus/wiki/topics/*.md` filenames against
`services.curriculum.CURRICULUM` topic ids so a renamed or typo'd corpus
filename doesn't silently break Phase 5's downstream sync consumer
(T-04.1-06).

`find_mismatches` is a plain function taking an explicit directory and id
set — independently importable/testable without touching the real
docs/corpus/ tree. The `if __name__ == "__main__":` guard below wires it up
as a CLI script.
"""

import sys
from pathlib import Path


def find_mismatches(corpus_topics_dir: Path, valid_ids: set) -> dict:
    """Diff corpus topic filenames against `valid_ids`.

    Returns {"orphans": [...], "missing": [...]} where "orphans" are corpus
    files with no matching curriculum id, and "missing" are curriculum ids
    with no corresponding corpus file. Both lists are sorted for stable
    output.
    """
    corpus_ids = {
        f.stem for f in corpus_topics_dir.glob("*.md") if f.stem != "index"
    }
    orphans = sorted(corpus_ids - valid_ids)
    missing = sorted(valid_ids - corpus_ids)
    return {"orphans": orphans, "missing": missing}


def main() -> int:
    from services.curriculum import CURRICULUM

    valid_ids = {t.id for t in CURRICULUM}
    result = find_mismatches(Path("docs/corpus/wiki/topics"), valid_ids)

    print(f"Orphans (corpus files with no curriculum id): {len(result['orphans'])}")
    for orphan in result["orphans"]:
        print(f"  - {orphan}")

    print(f"Missing (curriculum ids with no corpus file): {len(result['missing'])}")
    for missing_id in result["missing"]:
        print(f"  - {missing_id}")

    return 1 if result["orphans"] else 0


if __name__ == "__main__":
    sys.exit(main())
