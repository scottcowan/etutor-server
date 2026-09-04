"""Tests for services.corpus_mcp — index building and keyword search.

Uses a small synthetic fixture corpus under tests/fixtures/corpus/ so tests
never depend on the real, evolving docs/corpus/ content (04.1-CONTEXT.md D-14).
"""

from pathlib import Path

from services.corpus_mcp.index import build_index

FIXTURE_ROOT = Path(__file__).parent.parent / "fixtures" / "corpus"


def test_build_index_returns_expected_buckets_and_topic_count():
    index = build_index(FIXTURE_ROOT)

    assert set(index.keys()) == {"topics", "sources", "experiments", "people"}
    assert set(index["topics"].keys()) == {"fixture_topic_one", "fixture_topic_two"}


def test_build_index_entries_have_metadata_content_and_path():
    index = build_index(FIXTURE_ROOT)

    entry = index["topics"]["fixture_topic_one"]
    assert isinstance(entry["metadata"], dict)
    assert isinstance(entry["content"], str)
    assert isinstance(entry["path"], Path)
    assert entry["metadata"]["topic_ids"] == ["fixture_topic_one"]


def test_build_index_skips_index_md():
    index = build_index(FIXTURE_ROOT)

    for bucket in index.values():
        assert "index" not in bucket


def test_build_index_empty_bucket_is_empty_dict_not_missing_key():
    index = build_index(FIXTURE_ROOT)

    assert "people" in index
    assert index["people"] == {}
