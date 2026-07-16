---
phase: 2
slug: knowledge-tracing-backend
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-16
---

# Phase 2 — Validation Strategy

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | `pytest.ini` (exists — `asyncio_mode = auto`) |
| **Quick run command** | `pytest tests/services/ tests/api/ -x -q` |
| **Full suite command** | `pytest tests/ -q` (evals skip without ANTHROPIC_API_KEY) |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/services/ tests/api/ -x -q`
- **After every plan wave:** Run `pytest tests/ -x -q`
- **Before `/gsd-verify-work`:** Full suite green + evals green (requires API key)
- **Max feedback latency:** ~10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 02-01 | 1 | KT-01, KT-02 | — | N/A | manual | `alembic upgrade head` (SQLite) | ❌ W0 | ⬜ pending |
| 2-01-02 | 02-01 | 1 | KT-01, KT-04 | — | N/A | unit | `python -c "from db.crud import log_turn; print('OK')"` | ❌ W0 | ⬜ pending |
| 2-01-03 | 02-01 | 1 | KT-02 | — | N/A | unit | `python -c "from db.crud import upsert_child_fsrs_params; print('OK')"` | ❌ W0 | ⬜ pending |
| 2-02-01 | 02-02 | 2 | KT-01 | — | N/A | tdd | `pytest tests/services/test_knowledge_tracing.py -x -q` | ❌ W0 | ⬜ pending |
| 2-03-01 | 02-03 | 3 | KT-02 | — | N/A | tdd | `pytest tests/services/test_knowledge_tracing.py -x -q` | ❌ W0 | ⬜ pending |
| 2-04-01 | 02-04 | 4 | KT-03, KT-05 | — | N/A | tdd | `pytest tests/services/test_knowledge_tracing.py -x -q` | ❌ W0 | ⬜ pending |
| 2-05-01 | 02-05 | 4 | KT-04 | — | N/A | tdd | `pytest tests/api/test_session_end.py -x -q` | ❌ W0 | ⬜ pending |
| 2-06-01 | 02-06 | 5 | KT-05 | — | N/A | unit | `pytest tests/services/test_tutor.py -x -q` | ❌ W0 | ⬜ pending |
| 2-06-02 | 02-06 | 5 | KT-05 | — | N/A | eval | `pytest tests/evals/ -x -q` (evals skip without API key) | ✅ existing | ⬜ pending |
| 2-reg-01 | all | final | regression | — | Evals still pass | eval | `pytest tests/evals/ -q` | ✅ existing | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/services/__init__.py` — package marker
- [ ] `tests/services/test_knowledge_tracing.py` — stubs covering KT-01, KT-02, KT-03, KT-05
- [ ] `tests/api/test_session_end.py` — stubs for POST /sessions/{id}/end
- [ ] `tests/services/test_tutor.py` — mastery_context param tests

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `alembic upgrade head` with child_fsrs_params table | KT-02 | Requires subprocess | `cd project && alembic upgrade head && echo "OK"` |
| Per-child FSRS weights persist across server restart | KT-02 | Requires running server | Start server, trigger session end, restart, verify weights in DB |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
