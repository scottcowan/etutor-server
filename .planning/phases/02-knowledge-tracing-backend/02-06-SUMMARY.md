---
phase: 02-knowledge-tracing-backend
plan: "06"
subsystem: api
tags: [fastapi, prompt-engineering, bkt, knowledge-tracing, tutor]

# Dependency graph
requires:
  - phase: 02-knowledge-tracing-backend/02-04
    provides: mastery_context_for_prompt() in services/knowledge_tracing.py
  - phase: 02-knowledge-tracing-backend/02-05
    provides: KT-01 through KT-04 complete, end-to-end BKT/FSRS pipeline

provides:
  - build_system_prompt() extended with optional mastery_context param
  - Mastery bucket labels (fragile/in_progress/not_started) injected into every LLM system prompt
  - api/chat.py wired to call mastery_context_for_prompt() before every prompt build

affects:
  - phase-03-session-management
  - phase-04-auth
  - any phase touching api/chat.py or services/tutor.py

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Append-after-format pattern: mastery context appended after SYSTEM_PROMPT_TEMPLATE.format() to avoid breaking evals that use template directly"
    - "Optional[list]=None default: backward-compatible extension of async functions"

key-files:
  created:
    - tests/services/test_tutor.py
  modified:
    - services/tutor.py
    - api/chat.py

key-decisions:
  - "Append mastery block after SYSTEM_PROMPT_TEMPLATE.format() (not inside template) so evals using template directly are unaffected"
  - "mastery_ctx or None collapses empty list to None in chat.py, preserving no-op path in build_system_prompt"
  - "solid bucket silently filtered in _format_mastery_context (should never reach this function per D-08)"
  - "Used Optional[list] instead of list | None for Python 3.9 compatibility"

patterns-established:
  - "MASTERY_CONTEXT_TEMPLATE + _format_mastery_context(): private helper returns empty string when no lines, template appended only when non-empty"

requirements-completed:
  - KT-05

# Metrics
duration: 8min
completed: "2026-07-16"
---

# Phase 2 Plan 06: Wire Mastery Context into System Prompt Summary

**Mastery bucket labels (fragile/in_progress/not_started) injected into every LLM system prompt via optional mastery_context param on build_system_prompt() and wired through api/chat.py**

## Performance

- **Duration:** 8 min
- **Started:** 2026-07-16T15:10:00Z
- **Completed:** 2026-07-16T15:18:00Z
- **Tasks:** 2 (Task 1 TDD + Task 2 wiring)
- **Files modified:** 3

## Accomplishments

- Extended `build_system_prompt()` with `mastery_context: Optional[list] = None` — backward-compatible (all existing evals unchanged)
- `_format_mastery_context()` renders fragile/in_progress/not_started bucket labels in "Focus topics this session:" block
- `api/chat.py` now calls `mastery_context_for_prompt(child_id, session, limit=5)` before every prompt build
- All 6 unit tests pass; all 61 non-eval tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1 RED: test_tutor.py** - `d4dbb7e` (test)
2. **Task 1 GREEN: extend build_system_prompt** - `c4ef35f` (feat)
3. **Task 2: wire chat.py** - `6fbc836` (feat)

_Note: Task 1 used TDD — RED commit (failing tests) before GREEN commit (implementation)_

## Files Created/Modified

- `tests/services/test_tutor.py` - 6 unit tests for mastery_context extension (created)
- `services/tutor.py` - Added MASTERY_CONTEXT_TEMPLATE, _format_mastery_context(), extended build_system_prompt()
- `api/chat.py` - Added import + mastery_context_for_prompt() call before build_system_prompt()

## Decisions Made

- Used `Optional[list]` not `list | None` (Python 3.9 compatibility — the venv is Python 3.14 but system Python is 3.9; plan's spec used `|` syntax which fails on system Python)
- `mastery_ctx or None` pattern in chat.py collapses `[]` to `None`, preserving no-op path
- Append-after-format pattern (not inside SYSTEM_PROMPT_TEMPLATE) protects evals that use template directly

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Python 3.9 incompatible type union syntax**
- **Found during:** Task 1 (GREEN implementation)
- **Issue:** Plan spec used `list | None` which is Python 3.10+ syntax; system Python 3.9 raised TypeError at import
- **Fix:** Used `Optional[list]` from `typing` module, added `from typing import Optional` import
- **Files modified:** `services/tutor.py`
- **Verification:** Module imports successfully; all 6 tests pass
- **Committed in:** c4ef35f (Task 1 GREEN commit)

---

**Total deviations:** 1 auto-fixed (1 bug — Python version compatibility)
**Impact on plan:** Minimal — single type annotation syntax change. No behaviour change.

## Issues Encountered

- Eval suite (141 tests) all fail due to missing `ANTHROPIC_API_KEY` and asyncio event loop issue in Python 3.14 — pre-existing before this plan, not caused by changes. Verified via RESEARCH.md: evals use `SYSTEM_PROMPT_TEMPLATE.format()` directly, never call `build_system_prompt()`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- KT-05 complete — mastery context appears in every LLM system prompt when mastery state exists for child
- All Phase 2 requirements KT-01 through KT-05 now covered across Plans 02-01 to 02-06
- Phase 3 session management can build on the complete knowledge-tracing pipeline

## Self-Check: PASSED

Files verified:
- tests/services/test_tutor.py: FOUND
- services/tutor.py: FOUND (contains mastery_context)
- api/chat.py: FOUND (contains mastery_context_for_prompt)

Commits verified:
- d4dbb7e: test(02-06) RED commit
- c4ef35f: feat(02-06) GREEN commit
- 6fbc836: feat(02-06) chat.py wiring commit

---
*Phase: 02-knowledge-tracing-backend*
*Completed: 2026-07-16*
