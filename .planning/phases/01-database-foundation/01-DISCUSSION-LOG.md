# Phase 1: Database Foundation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-14
**Phase:** 1-Database Foundation
**Areas discussed:** Service Migration Style, List Field Storage, Dev Seed Strategy, Eval DB Fixture Approach

---

## Service Migration Style

| Option | Description | Selected |
|--------|-------------|----------|
| Rewrite in-place | Replace _profiles/_sessions dicts directly inside existing service files | |
| New db/ layer | db/models.py + db/crud.py + db/session.py; services thin-wrap db/ | ✓ |
| Hybrid | New db/models.py only; CRUD stays in service files | |

**User's choice:** New db/ layer

---

| Option | Description | Selected |
|--------|-------------|----------|
| db/session.py | Exports AsyncEngine, AsyncSessionLocal, get_db(); api/main.py initialises on startup | ✓ |
| config/settings.py | Engine initialised in settings module | |

**User's choice:** db/session.py (Recommended)

---

| Option | Description | Selected |
|--------|-------------|----------|
| FastAPI Depends injection | Route handlers get session via Depends(get_db); evals use pytest fixture | ✓ |
| Module-level async session | Service functions open own session internally; no signature change | |
| You decide | Leave session wiring to planner | |

**User's choice:** FastAPI Depends injection

---

## List Field Storage

| Option | Description | Selected |
|--------|-------------|----------|
| JSON column | Single TEXT/JSON column per list; zero joins | ✓ |
| Association tables | child_interests(child_id, interest) + child_neurodivergence(child_id, flag) | |
| Separate JSON columns (explicit naming) | Same as JSON column but naming made explicit | |

**User's choice:** JSON column

---

| Option | Description | Selected |
|--------|-------------|----------|
| Each Turn = own row | Separate interaction_events table; needed for Phase 2 BKT + Phase 3 history | ✓ |
| JSON array on Session row | Simpler for Phase 1; would require re-migration in Phase 2 | |

**User's choice:** Each Turn = own row

---

## Dev Seed Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Idempotent upsert on startup | INSERT OR IGNORE on server start; no-op on warm DB | ✓ |
| Alembic data migration | Seed rows in initial migration | |
| Remove seed entirely | Manual setup required before dev use | |

**User's choice:** Idempotent upsert on startup
**Notes:** User clarified that seed profiles represent real children — use generic identifiers (KidA, KidB) in all code and planning artifacts.

---

| Option | Description | Selected |
|--------|-------------|----------|
| seeds.py | db/seeds.py with async seed_dev_data(session); called from main.py lifespan | ✓ |
| Inline in main.py | Seed logic and data in the lifespan handler | |

**User's choice:** seeds.py

---

## Eval DB Fixture Approach

| Option | Description | Selected |
|--------|-------------|----------|
| pytest fixture with in-memory SQLite | Fresh sqlite:///:memory: per eval run; Alembic migrations applied | ✓ |
| Shared test DB file | Single tests/test.db; seeded once; state can leak | |
| Monkeypatch service layer | Override get_child_by_id() with mock; never touches DB | |

**User's choice:** pytest fixture with in-memory SQLite

---

| Option | Description | Selected |
|--------|-------------|----------|
| Inject session via fixture | Evals call service functions with db_session argument | ✓ |
| Override Depends globally | app.dependency_overrides; full HTTP stack via TestClient | |

**User's choice:** Inject session via fixture

---

## Claude's Discretion

- Exact column names, table names, SQLAlchemy model class names (standard conventions apply)
- Whether db/models.py and db/crud.py are single files or split further
- Alembic env.py configuration details (standard boilerplate)

## Deferred Ideas

None — discussion stayed within phase scope.
