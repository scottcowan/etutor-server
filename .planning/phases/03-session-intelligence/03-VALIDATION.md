---
phase: 3
slug: session-intelligence
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-07-17
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest-asyncio (established in Phase 1) |
| **Config file** | `pytest.ini` / `pyproject.toml` |
| **Quick run command** | `pytest tests/ -x -q` |
| **Full suite command** | `pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x -q`
- **After every plan wave:** Run `pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | HIST-03 | — | N/A | unit | `pytest tests/db/test_crud_session_intelligence.py -k test_get_turns_by_session_id -v` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 1 | CURR-04 | — | N/A | unit | `pytest tests/services/test_session_intelligence.py -k test_history_summary -v` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 1 | HIST-02 | — | N/A | unit | `pytest tests/services/test_session_intelligence.py -k test_prereq_tree -v` | ❌ W0 | ⬜ pending |
| 03-02-03 | 02 | 1 | CURR-02 | — | Tutor steered away from unmastered topics | unit | `pytest tests/services/test_session_intelligence.py -k test_prereq_state -v` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 2 | CURR-03 | — | N/A | unit | `pytest tests/services/test_session_intelligence.py -k test_extract_interests -v` | ❌ W0 | ⬜ pending |
| 03-03-02 | 03 | 2 | CURR-04 | — | N/A | unit | `pytest tests/services/test_session_intelligence.py -k test_supersedes_unlock -v` | ❌ W0 | ⬜ pending |
| 03-04-01 | 04 | 3 | HIST-01, HIST-02, CURR-01, CURR-02 | — | Prompt enrichment non-breaking | integration | `pytest tests/api/test_chat.py -v` | ❌ W0 | ⬜ pending |
| 03-04-02 | 04 | 3 | CURR-03 | — | N/A | integration | `pytest tests/api/test_sessions.py -k test_end_session_interest_extraction -v` | ❌ W0 | ⬜ pending |
| 03-04-03 | 04 | 3 | HIST-03 | — | N/A | integration | `pytest tests/api/test_sessions.py -k test_get_turns -v` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/db/test_crud_session_intelligence.py` — stub for `test_get_turns_by_session_id` (HIST-03)
- [ ] `tests/services/test_session_intelligence.py` — stubs for HIST-01, HIST-02, CURR-01–04 unit tests
- [ ] `tests/api/test_chat.py` — stub for prompt enrichment integration test (HIST-01, HIST-02, CURR-01, CURR-02)
- [ ] `tests/api/test_sessions.py` — stubs for interest extraction and turn retrieval integration tests

*Existing `tests/services/conftest.py` provides `db_session` async fixture — reuse it.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Rubber-band escalation cadence (Turn 1 → Turn 3 feels natural) | CURR-02 | Subjective UX quality | Run a manual chat session, ask about an unmastered topic, observe 3-turn escalation |
| Token budget of combined prompt ≤ 1,200 tokens | HIST-01, HIST-02 | Requires live Haiku call | Start a session for a returning child, capture system prompt, count tokens |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
