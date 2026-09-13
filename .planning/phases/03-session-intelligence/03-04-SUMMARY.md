---
phase: "03"
plan: "04"
subsystem: api
tags: [session-intelligence, wiring, history-context, prereq-tree, interests, HIST-01, HIST-02, HIST-03, CURR-01, CURR-02, CURR-03]
dependency_graph:
  requires: [03-01, 03-02, 03-03]
  provides: [HIST-03-endpoint, build_system_prompt-with-history-prereq, chat-wired-intelligence, end_session-interest-extraction]
  affects: [api/chat.py, api/sessions.py, services/tutor.py]
tech_stack:
  added: []
  patterns: [service-before-prompt anti-pattern-1-compliance, D-07-escalation-counter, D-08-catch-up-idempotency]
key_files:
  created:
    - tests/api/test_session_turns.py
  modified:
    - services/tutor.py
    - api/sessions.py
    - api/chat.py
    - tests/services/test_tutor.py
    - tests/api/test_session_end.py
    - tests/services/test_session_intelligence.py
decisions:
  - build_system_prompt receives pre-fetched data only — no DB calls inside (RESEARCH.md Anti-Pattern 1 compliance)
  - D-06 reset guard is present in non-streaming path; correct/kc_id not yet resolved (Phase 4 BKT probe detection will populate these fields)
  - TDD RED/GREEN committed as single commit (both in d3c82b3) — tests were verified failing before implementation was added
metrics:
  duration: "~30 minutes"
  completed: "2026-07-17T17:24:06Z"
  tasks_completed: 3
  files_modified: 6
---

# Phase 3 Plan 04: API Wiring for Session Intelligence Summary

Wired all Phase 3 session intelligence service functions into the API layer: extended `build_system_prompt()` with history/prereq context params, added the HIST-03 turns endpoint, wired interest extraction into session end, and connected all six intelligence functions into `api/chat.py`.

## What Was Built

### Task 1: Extend build_system_prompt() (services/tutor.py)

- New optional params: `history_context: Optional[list]`, `prereq_tree: Optional[list]`, `session_prereq_state: Optional[dict]` — all default to None (backward-compatible)
- `HISTORY_CONTEXT_TEMPLATE` + `_format_history_context()` — renders "Recent topics: X, Y" block (HIST-01)
- `PREREQ_TREE_TEMPLATE` + `_format_escalation_signal()` + `_format_prereq_tree()` — renders per-prereq lines with D-07 escalation signals: Turn 1 = "engage and hint", Turn 2 = "gentle probe", Turn 3+ = "active steer"
- Escalation lookup uses `entry["prereq_kc_id"]` keyed to `session_prereq_state` dict — matches counter key set by `increment_prereq_turn()`
- 5 new tests in `tests/services/test_tutor.py`; all 11 tests pass

### Task 2: HIST-03 endpoint + interest extraction (api/sessions.py)

- `GET /sessions/{session_id}/turns` endpoint returns `{"session_id": ..., "turns": [...]}`; IDOR note per CR-02 documented
- `POST /sessions/{id}/end` now calls `extract_and_update_interests()` after BKT/FSRS updates (CURR-03 fast path)
- New `tests/api/test_session_turns.py` with full fixture stack
- New `test_end_session_extracts_interests` appended to `tests/api/test_session_end.py`
- 6/6 API tests pass

### Task 3: Wire intelligence into chat() (api/chat.py)

- Imports: `build_24hr_history_context`, `build_prereq_tree_context`, `get_session_prereq_state`, `increment_prereq_turn`, `reset_prereq_turn`, `extract_and_update_interests`, `get_most_recent_ended_session`
- All new calls execute BEFORE `build_system_prompt()` — RESEARCH.md Anti-Pattern 1 compliance
- D-07: `increment_prereq_turn()` called for each entry in `prereq_tree` on every chat turn — escalation counter now advances
- D-08: `extract_and_update_interests()` catch-up trigger on `get_most_recent_ended_session()` — idempotent
- D-06: `reset_prereq_turn()` guard present; operational when `correct=True` and `kc_id` matches a prereq entry (Phase 4 will populate `kc_id` from BKT probe detection)
- `build_system_prompt()` receives `history_context`, `prereq_tree`, `session_prereq_state` params
- Pipeline integration test `test_prereq_tree_to_system_prompt_pipeline` added to `tests/services/test_session_intelligence.py`
- 88/88 tests pass (full suite, excluding evals which have pre-existing litellm import error)

## TDD Gate Compliance

Task 1 was tagged `type="tdd"`. Tests were written and confirmed failing before implementation. Due to git staging sequence, both test and implementation changes share commit `d3c82b3`. Tests were verified failing (TypeError: unexpected keyword argument 'history_context') before implementation was applied.

| Gate | Commit | Status |
|------|--------|--------|
| RED — failing tests confirmed | verified manually before staging | PASS |
| GREEN — all tests pass | `d3c82b3` | PASS |

## Deviations from Plan

### Auto-fixed Issues

None.

### Minor Deviations

**1. [TDD process] Single commit for RED+GREEN (Task 1)**
- **Found during:** Task 1 commit
- **Issue:** Test and implementation files staged together into `d3c82b3`
- **Why acceptable:** Tests were verified failing via `pytest` output before implementation was added; the TDD contract (tests-first) was honored in practice even if not reflected in separate commits
- **Impact:** None — code correctness and test coverage unaffected

**2. D-06 reset guard in non-streaming path only**
- The `reset_prereq_turn()` guard is wired in the non-streaming (`else`) path. The streaming `generate()` closure doesn't have access to `prereq_tree` from the outer scope currently. Phase 4 (BKT probe detection wiring) will address both paths when `correct`/`kc_id` are populated.
- **Impact:** D-06 is structurally wired; it has no practical effect until Phase 4 populates `turn.correct` and `turn.kc_id` for probe answers.

## Verification

```
pytest tests/services/test_tutor.py -x -q            → 11 passed
pytest tests/api/test_session_turns.py -x -q          → 1 passed
pytest tests/api/test_session_end.py -x -q            → 5 passed (4 existing + 1 new)
pytest tests/services/test_session_intelligence.py -x -q → 10 passed (9 existing + 1 new pipeline test)
pytest tests/ -x -q (excluding evals)                 → 88 passed
grep "history_context=" api/chat.py                   → history_context=history_ctx or None
grep "increment_prereq_turn" api/chat.py              → 2 occurrences (import + call)
grep "extract_and_update_interests" api/sessions.py   → 2 occurrences (import + call)
```

Note: `tests/evals/` fail with pre-existing `ModuleNotFoundError: No module named 'litellm'` — unrelated to this plan.

## Known Stubs

None — all functions are fully wired implementations.

## Threat Flags

No new security surface beyond what is documented in the plan's threat model. T-3-04-01 (IDOR on HIST-03) documented in code comment per plan's `accept` disposition.

## Self-Check: PASSED

- `services/tutor.py` modified — FOUND
- `api/sessions.py` modified — FOUND
- `api/chat.py` modified — FOUND
- `tests/api/test_session_turns.py` created — FOUND
- `tests/services/test_session_intelligence.py` modified — FOUND
- Commit `d3c82b3` (Task 1) — FOUND
- Commit `90383f5` (Task 2) — FOUND
- Commit `8cea66e` (Task 3) — FOUND
- `history_context: Optional` in services/tutor.py — FOUND (1 occurrence)
- `prereq_tree: Optional` in services/tutor.py — FOUND (1 occurrence)
- `build_24hr_history_context` in api/chat.py — FOUND (2 occurrences)
- `extract_and_update_interests` in api/sessions.py — FOUND (2 occurrences)
