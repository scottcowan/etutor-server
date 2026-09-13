---
phase: 4
slug: parent-dashboard
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-18
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest-asyncio (established in Phase 1) |
| **Config file** | `pytest.ini` / `pyproject.toml` |
| **Quick run command** | `pytest tests/ -x -q --ignore=tests/evals` |
| **Full suite command** | `pytest tests/ -v --ignore=tests/evals` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q --ignore=tests/evals`
- **After every plan wave:** Run `pytest tests/ -v --ignore=tests/evals`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | PARENT-05 | T-04-01 | Unauthenticated /parent → redirect to /parent/login | unit+integration | `pytest tests/api/test_parent_auth.py -v` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 2 | PARENT-04 | — | safety_flag set on keyword match | unit | `pytest tests/db/test_crud_parent.py -k test_safety_flag -v` | ❌ W0 | ⬜ pending |
| 04-02-02 | 02 | 2 | PARENT-04 | — | hint count tally fires alert | unit | `pytest tests/db/test_crud_parent.py -k test_frustration_alert -v` | ❌ W0 | ⬜ pending |
| 04-03-01 | 03 | 3 | PARENT-01 | — | Session replay shows turns | integration | `pytest tests/api/test_parent_views.py -k test_session_replay -v` | ❌ W0 | ⬜ pending |
| 04-03-02 | 03 | 3 | PARENT-02 | — | Mastery map accordion renders all subjects | integration | `pytest tests/api/test_parent_views.py -k test_mastery_map -v` | ❌ W0 | ⬜ pending |
| 04-03-03 | 03 | 3 | PARENT-03 | — | Profile edit takes effect on next chat turn | integration | `pytest tests/api/test_parent_views.py -k test_profile_edit -v` | ❌ W0 | ⬜ pending |
| 04-03-04 | 03 | 3 | PARENT-04 | — | Alert feed shows chronological badges | integration | `pytest tests/api/test_parent_views.py -k test_alert_feed -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `requirements.txt` — add `itsdangerous` (Wave 0 blocker: starlette SessionMiddleware fails without it)
- [ ] `tests/api/test_parent_auth.py` — stubs for auth tests (login, session, redirect, IDOR fix)
- [ ] `tests/db/test_crud_parent.py` — stubs for safety_flag and hint-count alert tests (shared with PARENT-03 CRUD stubs)
- [ ] `tests/api/test_parent_views.py` — stubs for session replay, mastery map, profile editor, alert feed

*Existing `tests/services/conftest.py` provides `db_session` async fixture — reuse it.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Mastery accordion expands/collapses correctly in browser | PARENT-02 | CSS/JS interaction, no Jinja2 unit test | Open /parent in browser, click subject headers |
| Profile change reflected in next chat turn (live session) | PARENT-03 | Requires live LLM + DB session | Start chat session, edit profile via /parent, observe next prompt |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
