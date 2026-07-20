---
phase: 04-parent-dashboard
verified: 2026-07-20T00:45:00Z
status: human_needed
score: 13/13 must-haves verified
overrides_applied: 0
human_verification:
  - test: "Log in at /parent with the PARENT_PASSWORD passphrase"
    expected: "Login page at /parent/login renders a single-field passphrase form; correct password redirects to /parent dashboard; wrong password redirects back to /parent/login with no error message shown"
    why_human: "Visual form appearance and browser-level cookie/redirect behaviour cannot be fully confirmed by grep or unit test alone"
  - test: "Navigate to a completed session replay at /parent/sessions/{id}"
    expected: "Turn-by-turn Q/A rows visible with Q: prefix in grey and A: in green; 🚩 Flagged marker shown for any turn with safety_flag=True"
    why_human: "Rendered HTML appearance and correct inline flag placement needs a real browser render"
  - test: "Navigate to /parent/children/{child_id} and inspect the Learning Map accordion"
    expected: "All subjects appear as collapsed <details> elements; tapping a subject expands it showing topic rows with colour-coded mastery dots (grey=not_started, orange=fragile, blue=in_progress, green=solid) and last-practiced date"
    why_human: "Accordion expand/collapse and mastery dot colour correctness requires visual inspection"
  - test: "Edit the child profile form at /parent/children/{child_id}"
    expected: "Name, age, reading level select (Beginner/Developing/Fluent), neurodivergence checkboxes (Dyslexia/ADHD/Dyscalculia/Autism/Hyperlexia), and interests comma field all present; Save changes redirects back to the same page"
    why_human: "Form field rendering and POST round-trip best verified with a real browser session"
  - test: "Navigate to /parent/alerts"
    expected: "30-day alert feed shows rows with timestamp, coloured badge (frustrated=yellow, sensitive=red, new-interest=teal) and truncated snippet text; empty state shows 'No alerts in the last 30 days.'"
    why_human: "Badge colour rendering and layout correctness requires visual inspection"
---

# Phase 04: Parent Dashboard Verification Report

**Phase Goal:** A parent can log in at /parent, review session replays, inspect their child's mastery map, edit the child's profile, and receive alerts for flagged moments.
**Verified:** 2026-07-20T00:45:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | GET /parent without session cookie redirects to /parent/login | VERIFIED | `require_parent_auth` dep raises `ParentAuthRequired`; `app.exception_handler` in `api/main.py:48-52` returns 303 to /parent/login; `test_dashboard_unauthenticated_redirects` passes |
| 2 | POST /parent/login with correct passphrase sets session cookie and redirects to /parent | VERIFIED | `api/parent.py:51-64` — `hmac.compare_digest` check, `request.session["parent_authenticated"] = True`, `RedirectResponse("/parent", 303)`; `test_login_sets_cookie_and_redirects` passes |
| 3 | POST /parent/login with wrong passphrase redirects to /parent/login with no error message | VERIFIED | `api/parent.py:63-64` — mismatch returns `RedirectResponse("/parent/login", 303)` with no body; `test_wrong_passphrase_redirects_no_error` passes |
| 4 | POST /parent/logout clears session and redirects to /parent/login | VERIFIED | `api/parent.py:67-71` — `request.session.clear()` + redirect; `test_logout_clears_session` passes |
| 5 | GET /parent/sessions/{session_id} returns turn-by-turn replay with safety_flag markers | VERIFIED | Route at `api/parent.py:102-121` calls `get_turns_by_session_id`; `session_replay.html:49` renders `{% if turn.safety_flag %}🚩 Flagged{% endif %}`; `test_session_replay_returns_turns` passes |
| 6 | GET /parent/children/{child_id} returns mastery accordion with all subjects, colour-coded dots, last-practiced date | VERIFIED | Route at `api/parent.py:124-156` calls `get_all_mastery_for_child`, groups by CURRICULUM subject, computes `_mastery_bucket`; `child_profile.html:137-155` uses native `<details>/<summary>` accordion with mastery dot colours; `test_child_profile_get_returns_200` passes |
| 7 | POST /parent/children/{child_id} updates profile and redirects to /parent/children/{child_id} | VERIFIED | Route at `api/parent.py:159-190` parses form, validates reading_level, calls `update_child_profile`, returns `RedirectResponse(f"/parent/children/{child_id}", 303)`; `test_child_profile_post_updates_and_redirects` passes |
| 8 | GET /parent/alerts returns 30-day alert feed with badge type and snippet | VERIFIED | Route at `api/parent.py:193-212` calls `get_alerts_for_child(child.id, session, days=30)`; `alert_feed.html` renders badge colours for frustrated/sensitive/new-interest; `test_alert_feed_returns_200` passes |
| 9 | All /parent/* routes (except login/logout) redirect when session cookie absent | VERIFIED | 5 `Depends(require_parent_auth)` wired at lines 78, 107, 129, 164, 197; view tests verify unauthenticated redirects for dashboard, session replay, child profile, and alert feed |
| 10 | frustration tally creates AlertModel row with alert_type='frustrated' when hint_used > 3 for same kc_id | VERIFIED | `db/crud.py:464-490` `run_frustration_tally` uses `func.count()` GROUP BY kc_id where hint_used=True; wired into `api/sessions.py:93` at end_session; `test_frustration_alert_created_at_end_session` passes |
| 11 | log_turn sets safety_flag=True AND creates AlertModel row with alert_type='sensitive' when keyword detected | VERIFIED | `db/crud.py:32-42` `_SAFETY_KEYWORDS` frozenset + `_has_safety_flag()`; `db/crud.py:197-225` log_turn sets `safety_flag=_has_safety_flag(question)` and calls `create_alert(..., "sensitive", ...)`; `test_safety_flag_set_on_keyword_match` and `test_sensitive_alert_created_on_keyword_match` pass |
| 12 | extract_and_update_interests creates new-interest alert when a new interest tag is added | VERIFIED | `services/session_intelligence.py:338-352` — captures pre-update interests, compares after update, writes `create_alert(child_id, "new-interest", db, snippet=tag)` for each net-new tag |
| 13 | Profile form shows neurodivergence checkboxes and reading level select | VERIFIED | `child_profile.html:100-115` — `<select>` for reading_level (beginner/developing/fluent); `child_profile.html:110` — checkbox loop for dyslexia/adhd/dyscalculia/autism/hyperlexia |

**Score:** 13/13 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `api/parent.py` | 5 authenticated routes + require_parent_auth | VERIFIED | 5 routes with `Depends(require_parent_auth)` at lines 78, 107, 129, 164, 197; `parent_dashboard`, `session_replay`, `child_profile_get`, `child_profile_post`, `alert_feed` all present |
| `api/main.py` | SessionMiddleware wired | VERIFIED | Line 45: `app.add_middleware(SessionMiddleware, secret_key=get_settings().secret_key, https_only=False)`; exception handler at lines 48-52 |
| `db/models.py` | AlertModel + safety_flag column | VERIFIED | `AlertModel` class at lines 96-113 with all required columns; `safety_flag` on `InteractionEventModel` at line 72 |
| `db/crud.py` | get_all_mastery_for_child, get_alerts_for_child, create_alert, update_child_profile | VERIFIED | All four functions present at lines 368, 400, 428, 448; plus `_SAFETY_KEYWORDS`/`_has_safety_flag` at lines 32-42 and `run_frustration_tally` at line 464 |
| `web/parent/templates/login.html` | Single-field passphrase login form | VERIFIED | File exists; form renders single `password` field |
| `web/parent/templates/dashboard.html` | Child cards + alert summary + session links | VERIFIED | File exists; rewritten by plan 03 to use `recent_alerts` and `recent_sessions` context variables |
| `web/parent/templates/session_replay.html` | Turn-by-turn Q/A + safety_flag markers | VERIFIED | File exists; line 49 renders `🚩 Flagged` for `turn.safety_flag` |
| `web/parent/templates/child_profile.html` | Profile editor + mastery accordion | VERIFIED | File exists; `<details>/<summary>` accordion at lines 137-155; neurodivergence checkboxes at line 110; reading level select at lines 100-103 |
| `web/parent/templates/alert_feed.html` | 30-day alert feed with badges | VERIFIED | File exists; badge CSS classes at lines 31-33; badge rendering for all 3 alert types at lines 58-60 |
| `config/settings.py` | parent_password field | VERIFIED | Line 12: `parent_password: str = "change-me-in-env"` |
| `requirements.txt` | itsdangerous | VERIFIED | Line 21: `itsdangerous>=2.1.2` |
| `api/sessions.py` | frustration tally at end_session | VERIFIED | Line 93: `await run_frustration_tally(session_id, session_row.child_id, db)` |
| `services/session_intelligence.py` | new-interest alert at extract_and_update_interests | VERIFIED | Lines 349-352: loop writes `create_alert(child_id, "new-interest", ...)` for each net-new tag |
| `tests/api/test_parent_auth.py` | Auth tests (6) | VERIFIED | 6 test functions; all 6 pass |
| `tests/api/test_parent_views.py` | View tests (8) | VERIFIED | 8 test functions; all 8 pass |
| `tests/db/test_crud_parent.py` | CRUD TDD tests (11) | VERIFIED | 11 test functions; all 11 pass |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `api/main.py` | `starlette.middleware.sessions.SessionMiddleware` | `app.add_middleware` | WIRED | Line 45 wires SessionMiddleware after CORSMiddleware |
| `api/parent.py:require_parent_auth` | `request.session['parent_authenticated']` | `Depends(require_parent_auth)` on 5 routes | WIRED | `require_parent_auth` at line 39 checks session; 5 route params include dep |
| `api/parent.py:do_login` | `settings.parent_password` | `hmac.compare_digest` | WIRED | Line 61 calls `hmac.compare_digest(str(password), settings.parent_password)` |
| `api/parent.py:child_profile_get` | `db/crud.py:get_all_mastery_for_child` | returns `{kc_id: MasteryStateModel}` | WIRED | Line 136 calls `get_all_mastery_for_child(child_id, session)` |
| `web/parent/templates/child_profile.html` | `services.curriculum.CURRICULUM` | subjects dict in template context | WIRED | Route loops CURRICULUM (line 140), passes `subjects_sorted` to template |
| `api/parent.py:session_replay` | `db/crud.py:get_turns_by_session_id` | turns list in template context | WIRED | Line 116 calls `get_turns_by_session_id(session_id, session)` |
| `api/parent.py:alert_feed` | `db/crud.py:get_alerts_for_child` | alerts list in template context | WIRED | Line 206 calls `get_alerts_for_child(child.id, session, days=30)` |
| `api/sessions.py:end_session` | `db/crud.py:run_frustration_tally` | called after BKT updates | WIRED | Line 93: `await run_frustration_tally(session_id, session_row.child_id, db)` |
| `db/crud.py:log_turn` | `InteractionEventModel.safety_flag + db/crud.py:create_alert` | `_has_safety_flag()` keyword check | WIRED | Lines 200, 219 set `safety_flag` and call `create_alert(..., "sensitive", ...)` |
| `services/session_intelligence.py:extract_and_update_interests` | `db/crud.py:create_alert` | new-interest detection loop | WIRED | Lines 349-352 call `create_alert(child_id, "new-interest", db, snippet=tag)` |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| `dashboard.html` | `recent_alerts`, `recent_sessions`, `children` | `get_alerts_for_child`, `list_sessions_for_child`, `list_children` in `parent_dashboard` | Yes — SQLAlchemy SELECT queries against `alerts`, `sessions`, `child_profiles` tables | FLOWING |
| `session_replay.html` | `turns`, `session_obj` | `get_turns_by_session_id`, `get_session` in `session_replay` | Yes — SELECT from `interaction_events` and `sessions` tables | FLOWING |
| `child_profile.html` | `child`, `subjects_sorted` | `get_child_by_id`, `get_all_mastery_for_child` in `child_profile_get` | Yes — SELECT from `child_profiles` and `mastery_state` tables; topics from CURRICULUM constant | FLOWING |
| `alert_feed.html` | `alerts`, `child` | `get_alerts_for_child`, `list_children` in `alert_feed` | Yes — SELECT from `alerts` with 30-day window filter | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 25 parent tests pass | `.venv/bin/python -m pytest tests/api/test_parent_auth.py tests/api/test_parent_views.py tests/db/test_crud_parent.py -q` | 25 passed in 1.41s | PASS |
| Full suite 113 tests, no regressions | `.venv/bin/python -m pytest tests/ -q --ignore=tests/evals` | 113 passed in 2.57s | PASS |
| `require_parent_auth` wired on all 5 protected routes | `grep -c "require_parent_auth" api/parent.py` | 7 (def + 5 Depends + 1 class) | PASS |
| Accordion uses native details/summary (no JS) | `grep -l "<details" web/parent/templates/child_profile.html` | file found | PASS |
| No `\|safe` filter on user content | `grep "\|safe" web/parent/templates/*.html` | no output | PASS |

---

### Probe Execution

Step 7c: SKIPPED — no probe scripts declared in PLAN files; no `scripts/*/tests/probe-*.sh` found.

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| PARENT-01 | 04-03 | Parent can view session history (turn-by-turn replay) | SATISFIED | `GET /parent/sessions/{session_id}` in `api/parent.py:102-121`; `session_replay.html` renders Q/A rows with safety flag markers |
| PARENT-02 | 04-03 | Parent can view child's mastery map (topics × mastery bucket) | SATISFIED | `GET /parent/children/{child_id}` in `api/parent.py:124-156`; `child_profile.html` accordion with mastery dots |
| PARENT-03 | 04-03 | Parent can set/edit child profile (interests, neurodivergence flags, reading level) | SATISFIED | `POST /parent/children/{child_id}` in `api/parent.py:159-190`; form includes all fields; `update_child_profile` partial-patch pattern |
| PARENT-04 | 04-02, 04-03 | Parent receives flags for sensitive topic questions, frustration signals, off-plan interest spikes | SATISFIED | `_SAFETY_KEYWORDS`/`_has_safety_flag` (sensitive), `run_frustration_tally` (frustrated), `new-interest` alert loop; `GET /parent/alerts` exposes all via 30-day feed |
| PARENT-05 | 04-01, 04-03 | Parent dashboard web UI accessible at /parent | SATISFIED | `GET /parent` route with auth gate; `SessionMiddleware` wired; passphrase login at `/parent/login` |

No orphaned PARENT-* requirements found — all 5 appear in plan frontmatter and are satisfied.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `api/main.py` | 45 | `https_only=False` on SessionMiddleware | Info | Correct for local dev HTTP; production requires `https_only=True` to prevent signed cookie interception on plain HTTP. Documented in 04-01-SUMMARY.md threat surface table. Not a blocker — dev-only default. |

No TBD, FIXME, or XXX debt markers found in any modified file.

---

### Human Verification Required

Five visual/browser checks needed to confirm the UI experience a parent would have:

### 1. Login page appearance and passphrase gate

**Test:** Open a browser to `/parent/login`. Inspect the form layout. Attempt login with wrong password, then correct password.
**Expected:** Single-field passphrase form with "Passphrase" label and "Sign in" button; wrong password redirects back to login with no error message; correct password redirects to /parent dashboard.
**Why human:** CSS rendering, form appearance, and the absence of an error message on wrong passphrase require a live browser to observe.

### 2. Session replay turn display and safety flag marker

**Test:** Navigate to `/parent/sessions/{a_session_id}` for a session that has at least one turn with `safety_flag=True`.
**Expected:** Q/A rows visible with Q: prefix in grey and A: in green accent; 🚩 Flagged marker shown inline after the question text of the flagged turn.
**Why human:** Inline rendering of the flag marker and visual Q/A row appearance require browser inspection.

### 3. Mastery map accordion and colour-coded dots

**Test:** Navigate to `/parent/children/{child_id}` and click to expand a subject accordion.
**Expected:** All subjects appear collapsed; expanding reveals topic rows with colour-coded dots (grey=not started, orange=fragile, blue=in progress, green=solid) and last-practiced date.
**Why human:** Accordion expand/collapse interaction and mastery dot colour correctness require visual inspection.

### 4. Profile editor form fields and POST round-trip

**Test:** Load the child profile page, edit the name and tick "ADHD" if not already ticked, submit. Reload the page.
**Expected:** Name field, age input, reading level dropdown, neurodivergence checkboxes (Dyslexia/ADHD/Dyscalculia/Autism/Hyperlexia), and interests comma field all render; after Save the page reloads with updated values.
**Why human:** Form field selection state (checked/selected) and successful POST round-trip are best confirmed in a real browser session.

### 5. Alert feed badge colours and empty state

**Test:** Visit `/parent/alerts`. If the DB has alerts, inspect badge colours. Also test the empty state by checking with no alerts for a fresh child.
**Expected:** frustrated badge in yellow (#fff3cd), sensitive in red (#f8d7da), new-interest in teal (#d1ecf1); empty state reads "No alerts in the last 30 days."
**Why human:** Badge colour rendering and visual layout require browser inspection.

---

### Gaps Summary

No gaps found. All 13 observable truths verified, all required artifacts exist and are substantively implemented, all key links are wired, and data flows from real DB queries to every template. The 5 human verification items are visual/browser checks only — the automated evidence (25 passing tests, 113-test full suite, grep confirmations) provides high confidence that all functional requirements are met.

---

_Verified: 2026-07-20T00:45:00Z_
_Verifier: Claude (gsd-verifier)_
