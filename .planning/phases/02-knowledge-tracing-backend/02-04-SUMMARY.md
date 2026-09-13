---
phase: 02-knowledge-tracing-backend
plan: 04
subsystem: knowledge-tracing
tags: [tdd, next_topics, mastery_context, FSRS, ranking]
dependency_graph:
  requires: [02-03]
  provides: [next_topics, mastery_context_for_prompt]
  affects: [services/knowledge_tracing.py, tests/services/test_knowledge_tracing.py]
tech_stack:
  added: []
  patterns: [FSRS-aware ranking, mastery bucket thresholds, SQLAlchemy parameterised select]
key_files:
  created: []
  modified:
    - services/knowledge_tracing.py
    - tests/services/test_knowledge_tracing.py
decisions:
  - "Used limit=20 in test_next_topics_due_first to capture both KCs given 15 age-6 topics; the assertion is about relative order, not absolute position"
  - "mastery_context_for_prompt makes a second DB call for mastery rows after next_topics() (simplicity over premature optimisation, per plan spec)"
metrics:
  duration_minutes: 30
  completed_date: "2026-07-16"
  tasks_completed: 2
  files_modified: 2
---

# Phase 2 Plan 04: next_topics Ranking + mastery_context_for_prompt Summary

**One-liner:** FSRS-aware topic ranking with mastery bucket sorting (fragile-first) and solid-KC exclusion, plus prompt-context formatter returning list[dict] with name+bucket.

## What Was Built

Two functions added to `services/knowledge_tracing.py`:

**`next_topics(child_id, db, limit=10) -> list[Topic]`** (KT-03)
- Loads child profile and all mastery_state rows for the child.
- Builds mastered_ids (p_mastery >= 0.95) and delegates candidate pool to `curriculum_next_topics()` which already enforces age-gating and prerequisites.
- Ranks candidates by `(is_due, -overdue_days, BUCKET_ORDER[bucket])` — overdue first, most overdue first, then fragile < in_progress < not_started within each tier.
- Excludes solid KCs (p_mastery >= 0.95) with future next_review only; solid KCs that are overdue are kept.
- KCs with no mastery_state row treated as not_started / due today (D-09).
- Parameterised SQLAlchemy select() for child_id (T-2-08).
- Returns [] for unknown child_id.

**`mastery_context_for_prompt(child_id, db, limit=5) -> list[dict]`** (KT-05 partial)
- Calls `next_topics()` then loads mastery rows for the returned topic IDs.
- Formats each as `{"name": topic.name, "bucket": "fragile"|"in_progress"|"not_started"}`.
- Defensive filter: solid KCs never appear in the output.
- Returns [] if child unknown or no topics available.

**Private helper: `_mastery_bucket(p_mastery) -> str`** (D-12 thresholds)
- None or < 0.1 → "not_started"
- 0.1 – 0.7 → "fragile"
- 0.7 – 0.95 → "in_progress"
- >= 0.95 → "solid"

**`BUCKET_ORDER` dict** — maps bucket names to sort priority integers.

## TDD Gate Compliance

| Gate | Commit | Status |
|------|--------|--------|
| RED: failing test commit | b5ccd96 | PASS — ImportError confirmed before implementation |
| GREEN: passing implementation commit | 622b98f | PASS — 25/25 tests pass, 51/51 suite passes |

## Test Coverage Added (10 new tests)

| Test | Behaviour Verified |
|------|--------------------|
| test_next_topics_due_first | Overdue KC before future-review KC |
| test_next_topics_bucket_ranking | Fragile before in_progress (same due tier) |
| test_next_topics_excludes_solid_future | Solid+future KC excluded from results |
| test_next_topics_no_mastery_row | No-row KC appears as not_started (D-09) |
| test_next_topics_limit | len(result) <= limit |
| test_next_topics_returns_empty_for_unknown_child | Unknown child → [] |
| test_mastery_context_for_prompt_shape | Returns list[dict] with name+bucket keys |
| test_mastery_context_for_prompt_bucket_values | Bucket values ∈ {fragile, in_progress, not_started} |
| test_mastery_context_no_solid | "solid" never in any bucket value |
| test_mastery_context_returns_empty_for_unknown_child | Unknown child → [] |

## Verification

All three verification commands passed:
1. `pytest tests/services/test_knowledge_tracing.py -x -v` — 25/25 passed
2. `pytest tests/ -x --ignore=tests/evals` — 51/51 passed
3. `python -c "from services.knowledge_tracing import next_topics, mastery_context_for_prompt; print('OK')"` — OK

## Deviations from Plan

### Test Adjustment

**1. [Rule 1 - Bug] test_next_topics_due_first used limit=10 but age-6 has 15 eligible topics**
- **Found during:** GREEN phase first run
- **Issue:** With `limit=10`, not_started KCs ranked above the future-review KC, pushing it out of the top 10 result. Test assertion `"counting_numbers" in ids` failed.
- **Fix:** Changed test to use `limit=20` to capture all 15 age-6 topics. The assertion about relative order (overdue before future) is still meaningful and now correct.
- **Files modified:** tests/services/test_knowledge_tracing.py
- **Commit:** 622b98f (included in GREEN commit)

## Known Stubs

None — both functions are fully wired and tested.

## Threat Flags

No new security-relevant surface beyond what the plan's threat model covers (T-2-08: parameterised child_id selects verified in implementation).

## Self-Check: PASSED

- `services/knowledge_tracing.py` — FOUND, contains `async def next_topics` and `async def mastery_context_for_prompt`
- `tests/services/test_knowledge_tracing.py` — FOUND, contains `test_next_topics_due_first`
- RED commit b5ccd96 — FOUND in git log
- GREEN commit 622b98f — FOUND in git log
