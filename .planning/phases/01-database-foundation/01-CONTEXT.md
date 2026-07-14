# Phase 1: Database Foundation - Context

**Gathered:** 2026-07-14
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace all in-memory stores (`_profiles` dict in `services/profiles.py`, `_sessions` dict in `services/sessions.py`) with a persistent SQLAlchemy + Alembic layer. Introduce a `db/` package containing ORM models, async session management, CRUD operations, and dev seed data. Existing callers (chat, STT, eval tests) must continue to work after the migration — all 4 passing evals must remain green.

</domain>

<decisions>
## Implementation Decisions

### Service Migration Style
- **D-01:** Introduce a new `db/` layer that owns ORM models and CRUD. Services thin-wrap `db/` rather than being rewritten in-place.
- **D-02:** `db/session.py` exports `AsyncEngine`, `AsyncSessionLocal`, and a `get_db()` FastAPI dependency. `api/main.py` initialises the engine in its lifespan handler.
- **D-03:** Services receive the DB session via FastAPI `Depends(get_db)`. API route handlers get the session and pass it down to service functions (or service functions become thin route logic). Evals use a `db_session` pytest fixture to inject sessions directly — no HTTP layer required.

### List Field Storage
- **D-04:** `interests: list[str]` and `neurodivergence: list[str]` are stored as JSON columns (single TEXT/JSON column per list). No separate association tables in Phase 1.
- **D-05:** Each session turn (`Turn`) is its own row in an `interaction_events` table (not a JSON blob on a session row). This aligns with DB-03/DB-04 and makes Phase 2 BKT updates and Phase 3 history injection possible without re-migration.

### Dev Seed Strategy
- **D-06:** Dev seed profiles are idempotent upserts (`INSERT OR IGNORE` / `ON CONFLICT DO NOTHING`) run on server startup inside a `lifespan` handler in `api/main.py`. Seeds only run when `settings.env != 'production'`.
- **D-07:** Seed data lives in `db/seeds.py` as an async `seed_dev_data(session)` function — not inline in `main.py`.
- **D-08:** Seed profiles use generic identifiers for the two child profiles (KidA, KidB). Do not use real names in code, comments, or planning artifacts.

### Eval DB Fixture Approach
- **D-09:** Each eval run gets a fresh in-memory SQLite database (`sqlite:///:memory:`). `tests/conftest.py` creates the engine, applies Alembic migrations, inserts a fixture child profile, and provides a `db_session` fixture.
- **D-10:** Evals call service functions directly with `db_session` as an explicit argument. FastAPI's `app.dependency_overrides` is not used for evals — the service function signature is the integration point.

### Approved Scope Narrowings
- **D-11 (PostgreSQL verification):** `alembic upgrade head` is verified against SQLite only in Phase 1. PostgreSQL execution verification is explicitly deferred to Phase 6 (Safety, Performance, and Polish). The async `env.py` pattern is PostgreSQL-compatible by design; this deferral is an environmental constraint, not a code incompatibility.
- **D-12 (eval fixture):** `tests/conftest.py` uses `Base.metadata.create_all` instead of programmatic Alembic invocation for the in-memory test fixture. Produces an identical schema for Phase 1 (single initial migration, no data migration steps) and is simpler. Revisit if migration script correctness must be exercised in tests.

### Claude's Discretion
- Exact column names, table names, and SQLAlchemy model class names — standard FastAPI/SQLAlchemy conventions apply.
- Whether `db/models.py` and `db/crud.py` are single files or split further — planner decides based on number of models.
- Alembic env.py configuration details (target_metadata, run_migrations_online/offline) — standard boilerplate.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §DB-01 through DB-05 — the 5 DB requirements this phase must satisfy (child profile, session record, interaction event, mastery state schema)
- `.planning/ROADMAP.md` §Phase 1 — goal statement, success criteria, key decisions/risks

### Existing code to migrate
- `services/profiles.py` — in-memory `ChildProfile` dataclass and `_profiles`/`_device_map` dicts to replace
- `services/sessions.py` — in-memory `Turn` dataclass and `_sessions` dict to replace
- `config/settings.py` — `database_url` setting already present (`sqlite+aiosqlite:///./data/etutor.db`)
- `api/main.py` — lifespan handler location for DB init and seed calls

### Evals (must stay green)
- `tests/evals/test_answer_reveal.py`
- `tests/evals/test_hint_ladder.py`
- `tests/evals/test_socratic_quality.py`
- `tests/evals/test_lesson_questions.py`
- `tests/evals/test_curriculum_accuracy.py`

No external specs — requirements fully captured in decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `config/settings.py` `Settings.database_url`: already defaults to `sqlite+aiosqlite:///./data/etutor.db` — use this as the engine URL; no new config needed
- `ChildProfile` dataclass fields: all fields are defined; ORM model mirrors these exactly (id, name, age, device_id, interests, reading_level, current_topic, current_books, session_count, neurodivergence)
- `Turn` dataclass fields: id, child_id, question, answer, timestamp, topic — maps directly to `interaction_events` table columns

### Established Patterns
- All service functions are `async` — SQLAlchemy async (`AsyncSession`, `aiosqlite`) is required; do not use sync ORM
- Callers never pass a session today — the session signature change to service functions is the main refactor surface
- `seed_dev_profiles()` is called at module import time — this must be removed/replaced; importing `services/profiles.py` must not trigger DB I/O

### Integration Points
- `services/tutor.py` calls `get_child_by_id()` and `get_session_history()` — these function signatures must stay compatible (or callers updated simultaneously)
- `api/chat.py` calls `get_child_by_device_id()`, `get_child_by_id()`, `log_turn()` — all three become DB-backed
- `api/stt.py` — check if it calls any profile/session service (grep before implementing)

</code_context>

<specifics>
## Specific Ideas

- Seed profiles should be identified generically as KidA / KidB (or similar), not with real names, in all code and planning artifacts.
- The `data/` directory (for `etutor.db`) should be gitignored and created at startup if absent.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 1-Database Foundation*
*Context gathered: 2026-07-14*
