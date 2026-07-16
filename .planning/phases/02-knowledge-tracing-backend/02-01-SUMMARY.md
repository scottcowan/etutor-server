---
phase: 02-knowledge-tracing-backend
plan: 01
subsystem: db
tags: [fsrs, bkt, alembic, crud, models]
dependency_graph:
  requires: []
  provides: [ChildFSRSParamsModel, upsert_child_fsrs_params, get_child_fsrs_params, log_turn-kc_id-correct, child_fsrs_params-migration]
  affects: [db/models.py, db/crud.py, services/sessions.py, requirements.txt]
tech_stack:
  added: [fsrs[optimizer]>=6.3.1]
  patterns: [SQLAlchemy JSON column, session.get() PK upsert, keyword-only params for backward compat]
key_files:
  created: [migrations/versions/d8909e3e5f75_add_child_fsrs_params.py]
  modified: [requirements.txt, db/models.py, db/crud.py, services/sessions.py]
decisions:
  - "Use JSON column (not String) for ChildFSRSParamsModel.weights — idiomatic, avoids manual json.dumps/loads"
  - "kc_id and correct as keyword-only params in log_turn — existing positional callers unaffected"
metrics:
  duration: ~20min
  completed: 2026-07-16
---

# Phase 2 Plan 01: FSRS Data Layer Bootstrap Summary

**One-liner:** Per-child FSRS weight table (child_fsrs_params), CRUD functions, and kc_id/correct fields wired into log_turn — prevents silent BKT no-op (Pitfall 1).

## Tasks Completed

| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Verify fsrs package legitimacy | (checkpoint — human approved) | — |
| 2 | ChildFSRSParamsModel, FSRS CRUD, extend log_turn, requirements | e19a2e5 | requirements.txt, db/models.py, db/crud.py, services/sessions.py |
| 3 | Alembic migration for child_fsrs_params | b3b9cd8 | migrations/versions/d8909e3e5f75_add_child_fsrs_params.py |

## What Was Built

### ChildFSRSParamsModel (db/models.py)
- `child_id`: String PK, ForeignKey to `child_profiles.id`
- `weights`: JSON column (list of 21 floats — FSRS-5 weight vector)
- `updated_at`: DateTime(timezone=True)

### CRUD Functions (db/crud.py)
- `get_child_fsrs_params(child_id, session)` — PK lookup via `session.get()`
- `upsert_child_fsrs_params(child_id, weights, session)` — get-or-create pattern, parameterised (T-2-02)

### log_turn Extension (db/crud.py + services/sessions.py)
- Added `kc_id: Optional[str] = None` and `correct: Optional[bool] = None` as keyword-only params
- Both forwarded through to `InteractionEventModel` constructor
- Existing callers unaffected (backward-compatible)

### Alembic Migration
- Revision: `d8909e3e5f75`, `down_revision = '9f229414e92b'`
- Creates `child_fsrs_params` table with JSON weights column and FK constraint
- upgrade/downgrade round-trip verified clean

## Verification

```
python3 -c "from db.models import ChildFSRSParamsModel, MasteryStateModel; print('OK')"  # OK
python3 -c "from db.crud import log_turn, upsert_child_fsrs_params, get_child_fsrs_params; ..."  # CRUD OK
python3 -m alembic upgrade head  # clean
python3 -m alembic downgrade -1 && python3 -m alembic upgrade head  # round-trip clean
grep fsrs[optimizer] requirements.txt  # found
pytest tests/db/ -x -q  # 23 passed
```

## Deviations from Plan

None — plan executed exactly as written.

Note: `pytest tests/ -x -q --ignore=tests/evals` exits with import error on `tests/api/test_chat_db_wiring.py` due to `fastapi` not installed in the test venv. This is a pre-existing environment issue unrelated to this plan's changes. The plan's target scope `pytest tests/db/` passes cleanly (23 passed).

## Known Stubs

None — this plan only adds schema/CRUD, no UI-facing data flows.

## Threat Flags

None — new surface is internal CRUD only; both CRUD functions use parameterised ORM operations (T-2-01, T-2-02 mitigated).

## Self-Check: PASSED

- [x] `db/models.py` contains `class ChildFSRSParamsModel`
- [x] `db/crud.py` contains `upsert_child_fsrs_params` and `get_child_fsrs_params`
- [x] `requirements.txt` contains `fsrs[optimizer]>=6.3.1`
- [x] Migration file `d8909e3e5f75_add_child_fsrs_params.py` exists
- [x] Commits e19a2e5 and b3b9cd8 exist in git log
- [x] 23 db tests pass
