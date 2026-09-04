"""Tests for services.corpus_mcp.validate_topic_ids — topic-ID drift check
(04.1-CONTEXT.md D-13/CORPUS-04, 04.1-RESEARCH.md Pitfall 3).

Uses a synthetic tmp_path directory of `.md` files rather than the real,
evolving docs/corpus/wiki/topics/ tree.
"""

from pathlib import Path

from services.corpus_mcp.validate_topic_ids import find_mismatches


def test_find_mismatches_reports_orphans_and_missing(tmp_path: Path):
    corpus_dir = tmp_path / "topics"
    corpus_dir.mkdir()
    (corpus_dir / "not_a_real_id.md").write_text("---\n---\n")

    result = find_mismatches(corpus_dir, valid_ids={"real_id"})

    assert result["orphans"] == ["not_a_real_id"]
    assert result["missing"] == ["real_id"]


def test_find_mismatches_empty_when_all_match(tmp_path: Path):
    corpus_dir = tmp_path / "topics"
    corpus_dir.mkdir()
    (corpus_dir / "real_id.md").write_text("---\n---\n")

    result = find_mismatches(corpus_dir, valid_ids={"real_id"})

    assert result["orphans"] == []
    assert result["missing"] == []


def test_find_mismatches_ignores_index_md(tmp_path: Path):
    corpus_dir = tmp_path / "topics"
    corpus_dir.mkdir()
    (corpus_dir / "real_id.md").write_text("---\n---\n")
    (corpus_dir / "index.md").write_text("---\n---\n")

    result = find_mismatches(corpus_dir, valid_ids={"real_id"})

    assert result["orphans"] == []
    assert result["missing"] == []
