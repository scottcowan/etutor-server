---
phase: 1
slug: database-foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-14
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | `pytest.ini` (Wave 0 gap — does not exist yet) |
| **Quick run command** | `pytest tests/db/ -x -q` |
| **Full suite command** | `pytest tests/ -q` (evals skip without ANTHROPIC_API_KEY) |
| **Estimated runtime** | ~5 seconds (DB unit tests only) |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/db/ -x -q`
- **After every plan wave:** Run `pytest tests/ -x -q`
- **Before `/gsd-verify-work`:** Full suite must be green + evals green (requires ANTHROPIC_API_KEY)
- **Max feedback latency:** ~5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01-01 | 1 | DB-01 | T-SQL-injection | Parameterised ORM queries only | unit | `pytest tests/db/test_session.py -x` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01-01 | 1 | DB-02 | T-PII | No real names in seed data | unit | `pytest tests/db/test_crud_profiles.py -x` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01-01 | 1 | DB-03 | — | N/A | unit | `pytest tests/db/test_crud_sessions.py -x` | ❌ W0 | ⬜ pending |
| 1-01-04 | 01-01 | 1 | DB-04 | — | N/A | unit | `pytest tests/db/test_crud_events.py -x` | ❌ W0 | ⬜ pending |
| 1-01-05 | 01-01 | 1 | DB-05 | — | N/A | unit | `pytest tests/db/test_crud_mastery.py -x` | ❌ W0 | ⬜ pending |
| 1-02-01 | 01-02 | 2 | DB-02 | — | N/A | tdd | `pytest tests/db/test_crud_profiles.py -x` | ❌ W0 | ⬜ pending |
| 1-02-02 | 01-02 | 2 | D-06 | T-PII | Seeds idempotent; no PII | tdd | `pytest tests/db/test_seeds.py -x` | ❌ W0 | ⬜ pending |
| 1-03-01 | 01-03 | 3 | DB-03 | — | N/A | tdd | `pytest tests/db/test_crud_sessions.py -x` | ❌ W0 | ⬜ pending |
| 1-03-02 | 01-03 | 3 | DB-04 | T-SQL-injection | ORM parameterised; no string interpolation | tdd | `pytest tests/db/test_crud_events.py -x` | ❌ W0 | ⬜ pending |
| 1-03-03 | 01-03 | 3 | DB-05 | — | N/A | tdd | `pytest tests/db/test_crud_mastery.py -x` | ❌ W0 | ⬜ pending |
| 1-04-01 | 01-04 | 2 | DB-01 | — | N/A | manual | `alembic upgrade head` (SQLite) | ❌ W0 | ⬜ pending |
| 1-05-01 | 01-05 | 4 | DB-02, DB-03, DB-04 | — | N/A | unit | `pytest tests/db/ -x -q` | ❌ W0 | ⬜ pending |
| 1-06-01 | 01-06 | 5 | DB-01, DB-02, DB-03, DB-04 | — | N/A | unit | `pytest tests/db/ -x -q` | ❌ W0 | ⬜ pending |
| 1-07-01 | 01-07 | 5 | DB-01, DB-02, DB-03 | — | N/A | unit | `pytest tests/ -x -q` | ✅ existing (evals) | ⬜ pending |
| 1-reg-01 | all | final | eval regression | — | Evals still pass | eval | `pytest tests/evals/ -q` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pytest.ini` — `asyncio_mode = auto` for pytest-asyncio
- [ ] `tests/conftest.py` — `db_session` fixture (async in-memory SQLite, create_all)
- [ ] `tests/db/__init__.py` — package marker
- [ ] `tests/db/test_crud_profiles.py` — stubs for DB-02
- [ ] `tests/db/test_crud_sessions.py` — stubs for DB-03
- [ ] `tests/db/test_crud_events.py` — stubs for DB-04 (must include kc_id, correct, response_ms, hint_used columns)
- [ ] `tests/db/test_crud_mastery.py` — stubs for DB-05
- [ ] `tests/db/test_seeds.py` — stubs for D-06 idempotency

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `alembic upgrade head` on fresh SQLite | DB-01 | Requires subprocess; env path setup | `cd project && alembic upgrade head && echo "OK"` |
| Server restart persists profiles | DB-01 goal | Requires running server | Start server, create profile via API, restart, verify profile returns |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
