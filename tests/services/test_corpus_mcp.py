"""Tests for services.corpus_mcp — index building and keyword search.

Uses a small synthetic fixture corpus under tests/fixtures/corpus/ so tests
never depend on the real, evolving docs/corpus/ content (04.1-CONTEXT.md D-14).
"""

from pathlib import Path

from services.corpus_mcp.index import build_index
from services.corpus_mcp.search import search_corpus_impl
from services.corpus_mcp.tools import (
    get_experiments_impl,
    get_topic_impl,
    list_sources_impl,
    list_topics_impl,
)

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


def test_search_corpus_finds_matches_across_topics_bucket():
    index = build_index(FIXTURE_ROOT)

    results = search_corpus_impl(index, query="fixture")

    assert len(results) > 0
    topic_results = [r for r in results if r["bucket"] == "topics"]
    assert {r["id"] for r in topic_results} == {"fixture_topic_one", "fixture_topic_two"}
    for r in results:
        assert "bucket" in r and "id" in r and "metadata" in r


def test_search_corpus_no_match_returns_empty_list():
    index = build_index(FIXTURE_ROOT)

    results = search_corpus_impl(index, query="nonexistent-token-xyz")

    assert results == []


def test_search_corpus_subject_filter_excludes_nonmatching_metadata():
    index = build_index(FIXTURE_ROOT)

    results = search_corpus_impl(index, query="fixture", subject="NoSuchSubject")

    assert results == []


def test_search_corpus_query_is_case_insensitive():
    index = build_index(FIXTURE_ROOT)

    lower_results = search_corpus_impl(index, query="fixture")
    upper_results = search_corpus_impl(index, query="FIXTURE")

    lower_keys = {(r["bucket"], r["id"]) for r in lower_results}
    upper_keys = {(r["bucket"], r["id"]) for r in upper_results}
    assert lower_keys == upper_keys


# --- tools.py: 5 locked MCP tool behaviors (D-13) ---------------------------


def test_tools_get_topic_impl_returns_full_entry():
    index = build_index(FIXTURE_ROOT)

    result = get_topic_impl(index, "fixture_topic_one")

    assert result["metadata"]["topic_ids"] == ["fixture_topic_one"]
    assert "Introduction" in result["content"]


def test_tools_get_topic_impl_level_filter_returns_only_matching_section():
    index = build_index(FIXTURE_ROOT)

    result = get_topic_impl(index, "fixture_topic_one", level="100")

    assert "## 100" in result["content"]
    assert "fixture content for topic one" in result["content"]


def test_tools_get_topic_impl_missing_id_returns_error_dict():
    index = build_index(FIXTURE_ROOT)

    result = get_topic_impl(index, "does_not_exist")

    assert "error" in result


def test_tools_list_sources_impl_filters_by_topic_id():
    index = build_index(FIXTURE_ROOT)

    matched = list_sources_impl(index, topic_id="fixture_topic_one")
    unmatched = list_sources_impl(index, topic_id="fixture_topic_two")

    assert len(matched) == 1
    assert matched[0]["metadata"]["topic_ids"] == ["fixture_topic_one"]
    assert unmatched == []


def test_tools_list_sources_impl_type_filter_narrows_results():
    index = build_index(FIXTURE_ROOT)

    matched = list_sources_impl(index, topic_id="fixture_topic_one", type_="article")
    unmatched = list_sources_impl(index, topic_id="fixture_topic_one", type_="video")

    assert len(matched) == 1
    assert unmatched == []


def test_tools_get_experiments_impl_hard_gate_excludes_dangerous_below_min_age():
    index = build_index(FIXTURE_ROOT)

    results = get_experiments_impl(index, topic_id="fixture_topic_one", min_age=8)

    ids = {r["id"] for r in results}
    assert "fixture_experiment_one" in ids
    assert "fixture_experiment_two" not in ids


def test_tools_get_experiments_impl_permissive_gate_allows_non_dangerous_regardless():
    index = build_index(FIXTURE_ROOT)

    results_low_age = get_experiments_impl(index, topic_id="fixture_topic_one", min_age=1)
    results_no_age = get_experiments_impl(index, topic_id="fixture_topic_one", min_age=None)

    assert "fixture_experiment_one" in {r["id"] for r in results_low_age}
    assert "fixture_experiment_one" in {r["id"] for r in results_no_age}
    assert "fixture_experiment_two" in {r["id"] for r in results_no_age}


def test_tools_list_topics_impl_returns_all_ids_and_filters_by_subject():
    index = build_index(FIXTURE_ROOT)

    all_topics = list_topics_impl(index)
    filtered = list_topics_impl(index, subject="FixtureSubject")
    filtered_none = list_topics_impl(index, subject="NoSuchSubject")

    assert set(all_topics) == {"fixture_topic_one", "fixture_topic_two"}
    assert set(filtered) == {"fixture_topic_one", "fixture_topic_two"}
    assert filtered_none == []


def test_tools_get_topic_impl_path_traversal_string_returns_not_found():
    index = build_index(FIXTURE_ROOT)

    result = get_topic_impl(index, "../../../etc/passwd")

    assert "error" in result
