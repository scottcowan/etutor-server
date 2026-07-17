---
phase: "03"
plan: "02"
subsystem: knowledge-tracing
tags: [bkt, curriculum, supersedes, model-progression, tdd]
dependency_graph:
  requires: []
  provides: [CURR-04-supersedes-unlock]
  affects: [services/knowledge_tracing.py, tests/services/test_knowledge_tracing.py]
tech_stack:
  added: []
  patterns: [reverse-index-at-import, BKT-solid-threshold-0.95, module-level-dict]
key_files:
  created: []
  modified:
    - services/knowledge_tracing.py
    - tests/services/test_knowledge_tracing.py
decisions:
  - "D-14 confirmed: unlock trigger is p_mastery >= 0.95 (BKT solid bucket). bloom_target is a Bloom integer (1-6); p_mastery is 0.0-1.0 — scales are incommensurable. The solid bucket threshold is the correct proxy for 'reached bloom_target mastery'."
  - "Reverse index _superseded_by built at module import time (O(N) over 870 topics, 14 have supersedes). Zero runtime cost per request."
metrics:
  duration: "~12 minutes"
  completed: "2026-07-17"
  tasks_completed: 3
  files_changed: 2
---

# Phase 03 Plan 02: CURR-04 Supersedes Unlock in next_topics() Summary

Implements the CURR-04 model-progression unlock: when a child solidly masters a KC (p_mastery >= 0.95), any topic in CURRICULUM whose `supersedes` field points to that KC is automatically injected into `next_topics()` candidates. This enables the "lies to children" refinement mechanic — e.g., once a child solidly masters `particle_model`, `atom_bohr_to_quantum` (Bohr model to quantum mechanics) becomes a recommendation candidate.

## Tasks Completed

| Task | Type | Commit | Description |
|------|------|--------|-------------|
| RED | test | aef6f40 | Add 3 failing TDD tests for supersedes unlock |
| GREEN | feat | db7eb7e | Implement _superseded_by index + inject block |
| REFACTOR | — | (none needed) | Loop var already uses `_t`, no functional changes required |

## What Was Built

**`_superseded_by` reverse index** (module-level, `services/knowledge_tracing.py`):
- Built at import time from CURRICULUM (14 of 870 topics have `supersedes` set)
- Maps `{superseded_topic_id: [superseding_topic_id, ...]}` for O(1) lookup per mastered KC
- D-14 comment documents the bloom_target vs p_mastery scale mismatch

**Inject block in `next_topics()`**:
- Runs after `curriculum_next_topics()` returns `candidates`, before sort/filter/limit
- For each solidly-mastered KC (p_mastery >= 0.95), looks up any topics that supersede it
- Only injects if: the superseding topic exists in `_by_id`, it is not already in `mastered_ids`, and it is not already in `candidates` (no duplicates)

## TDD Gate Compliance

RED commit (`aef6f40`) precedes GREEN commit (`db7eb7e`). Gate sequence valid.

- RED: `test(03-02): add failing tests for CURR-04 supersedes unlock` — 1 test failed as expected
- GREEN: `feat(03-02): implement CURR-04 supersedes unlock in next_topics()` — all 3 new tests pass
- REFACTOR: no changes needed (loop var was already `_t`, style already clean)

## Verification Results

```
tests/services/test_knowledge_tracing.py: 28 passed (all tests including 3 new)
tests/ (excluding tests/evals): 64 passed
```

Acceptance criteria:
- `grep -c "_superseded_by" services/knowledge_tracing.py` = 3 (definition loop + dict decl + inject block)
- No literal `p_mastery >= bloom_target` comparison exists
- D-14 comment in two places explains `p_mastery >= 0.95` as unlock trigger and bloom_target scale mismatch

## Deviations from Plan

None — plan executed exactly as written.

Note: `tests/evals/test_answer_reveal.py` has 10 pre-existing failures (Python 3.14 removed `asyncio.get_event_loop()` on MainThread). These are out of scope and pre-date this plan.

## Known Stubs

None.

## Threat Flags

None — `_superseded_by` is built from static CURRICULUM data at import time, never modified at runtime. No new network endpoints, auth paths, or trust boundary crossings introduced.

## Self-Check: PASSED

- `services/knowledge_tracing.py` exists and contains `_superseded_by` (3 occurrences)
- `tests/services/test_knowledge_tracing.py` exists and contains `test_supersedes_unlock_adds_candidate`
- Commits aef6f40 and db7eb7e verified in git log
- All 28 knowledge-tracing tests pass
