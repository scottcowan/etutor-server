---
phase: 04-parent-dashboard
plan: "03"
subsystem: api/parent-views
tags: [parent-dashboard, jinja2, views, authentication, mastery-map, session-replay, alert-feed]
dependency_graph:
  requires: [04-01, 04-02]
  provides: [PARENT-01, PARENT-02, PARENT-03, PARENT-04, PARENT-05]
  affects: [api/parent.py, web/parent/templates, tests/api/test_parent_views.py]
tech_stack:
  added: []
  patterns:
    - FastAPI HTMLResponse with Jinja2Templates
    - require_parent_auth Depends() on all five protected routes
    - Native HTML details/summary accordion (zero JavaScript)
    - SQLAlchemy async ORM for all DB reads
key_files:
  created:
    - web/parent/templates/session_replay.html
    - web/parent/templates/child_profile.html
    - web/parent/templates/alert_feed.html
    - tests/api/test_parent_views.py
  modified:
    - api/parent.py
    - web/parent/templates/dashboard.html
    - db/crud.py
decisions:
  - list_sessions_for_child() added to db/crud.py rather than reusing get_session_history() (which returns InteractionEventModel rows, not SessionModel rows)
  - dashboard GET passes recent_alerts and recent_sessions (not the old sessions dict); dashboard.html rewritten to use new context variables
  - v1 single-child assumption: alert/session queries use children[0] when no child_id in URL
metrics:
  duration: "~30 minutes"
  completed: "2026-07-20T00:19:40Z"
  tasks_completed: 2
  files_modified: 7
---

# Phase 04 Plan 03: Parent Dashboard Views Summary

Five authenticated HTML views for the parent dashboard wired to CRUD functions from wave 2: dashboard overview with child cards, alert summary, and session list; session turn-by-turn replay with safety flag markers; child profile editor with mastery map accordion; and a 30-day alert feed — all gated by `require_parent_auth`.

## Tasks Completed

| # | Task | Commit | Status |
|---|------|--------|--------|
| 1 | RED: failing test_parent_views.py (8 tests) | 1879e63 | PASS |
| 2 | GREEN: five routes in api/parent.py + four templates | 41252a1 | PASS |

## What Was Built

### Routes (api/parent.py)

- **GET /parent (extended):** Added `recent_alerts` and `recent_sessions` to dashboard context; removed obsolete `sessions` dict placeholder from Phase 1.
- **GET /parent/sessions/{session_id}:** Returns 404 if session not found; passes `session_obj` and `turns` to session_replay.html. `session_obj` named to avoid collision with SQLAlchemy `session` parameter.
- **GET /parent/children/{child_id}:** Fetches mastery rows via `get_all_mastery_for_child`, groups topics by subject from `CURRICULUM`, computes bucket via `_mastery_bucket`, passes `subjects_sorted` (alphabetical).
- **POST /parent/children/{child_id}:** Parses form fields, validates `reading_level` against allowlist, calls `update_child_profile`, returns 303 redirect.
- **GET /parent/alerts:** Fetches 30-day alerts for v1 single child; passes `alerts` and `child` to alert_feed.html.

All five protected routes include `_: None = Depends(require_parent_auth)` (T-4-03-01).

### Templates

- **dashboard.html (extended):** Child cards link to `/parent/children/{child.id}`; "Recent Alerts" section with badge colours per UI-SPEC; "Recent Sessions" section with session links. Sign out link in header.
- **session_replay.html (new):** Turn-by-turn Q/A with `Q:` prefix in grey, `A:` in green accent, 🚩 Flagged inline for safety_flag turns. `← Back` link.
- **child_profile.html (new):** Profile editor form (name/age/reading_level/neurodivergence checkboxes/interests) + Learning Map accordion using native `<details>/<summary>`. Mastery dots colour-coded per UI-SPEC (not_started=#b0b0b0, fragile=#e6a817, in_progress=#4a90d9, solid=#7a9e7e). Zero JS.
- **alert_feed.html (new):** Chronological alert rows with timestamp, badge (frustrated/sensitive/new-interest) using UI-SPEC colours, snippet text. `← Dashboard` link.

### db/crud.py addition

`list_sessions_for_child(child_id, session, limit)` — returns `list[SessionModel]` ordered started_at DESC. Needed because `get_session_history()` returns `InteractionEventModel` rows (turns), not session-level rows.

## Test Results

```
8 view tests pass (test_parent_views.py)
113 total tests pass (full suite, no regressions)
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] dashboard.html rewritten, not just extended**
- **Found during:** Task 2
- **Issue:** The old dashboard.html used `sessions.items()` (a dict of `{child_id: [turns]}`) but the new route passes `recent_sessions` (a list of SessionModel rows). Template would raise `UndefinedError: 'sessions' is undefined`.
- **Fix:** Rewrote dashboard.html to use the new context variables (`recent_alerts`, `recent_sessions`). Visual structure and CSS preserved; all section headings and empty states match the Copywriting Contract.
- **Files modified:** web/parent/templates/dashboard.html
- **Commit:** 41252a1

**2. [Rule 2 - Missing functionality] list_sessions_for_child() added to db/crud.py**
- **Found during:** Task 1 route implementation
- **Issue:** No function existed to fetch a list of `SessionModel` rows for a child. `get_session_history()` returns `InteractionEventModel` (turns), not sessions.
- **Fix:** Added `list_sessions_for_child(child_id, session, limit=10)` to db/crud.py.
- **Files modified:** db/crud.py
- **Commit:** 41252a1

## Security Verification

| Threat | Status |
|--------|--------|
| T-4-03-01: All /parent/* routes missing require_parent_auth | MITIGATED — 5 Depends() present, verified by grep |
| T-4-03-02: IDOR on sessions (v1 single-family) | ACCEPTED — documented |
| T-4-03-03: XSS via Jinja2 template variables | MITIGATED — no `|safe` filter on user content |
| T-4-03-05: reading_level arbitrary string | MITIGATED — server-validates against allowlist before DB write |

## Known Stubs

None — all template variables are wired to live DB data via CRUD functions.

## Self-Check: PASSED

- api/parent.py: 5 routes with require_parent_auth — FOUND
- web/parent/templates/session_replay.html — FOUND
- web/parent/templates/child_profile.html — FOUND
- web/parent/templates/alert_feed.html — FOUND
- tests/api/test_parent_views.py — FOUND
- Commits 1879e63, 41252a1 — FOUND in git log
- 113 tests pass — VERIFIED
