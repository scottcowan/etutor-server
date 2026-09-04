# Roadmap: etutor-server

## Overview

The server core (Socratic tutor, 777-topic curriculum, chat and STT endpoints, passing evals) already
exists. This roadmap covers the six phases needed to go from a working-but-stateless prototype to a
fully persistent, pedagogically intelligent tutoring system with parent oversight, child browser
interface, device sync, and production-grade safety and latency guarantees. Each phase is a
self-contained capability that the phase after it depends on.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Database Foundation** - Persistent SQLite/PostgreSQL storage replaces all in-memory stores (completed 2026-07-14)
- [x] **Phase 2: Knowledge Tracing Backend** - BKT mastery model + FSRS scheduling per child × KC (completed 2026-07-16)
- [x] **Phase 3: Session Intelligence** - History injection, curriculum routing, and interest graph (completed 2026-07-17)
- [x] **Phase 4: Parent Dashboard** - Session replay, mastery map, profile editor, and alert feed (completed 2026-07-20)
- [ ] **Phase 5: Child Interface + Device Sync** - Browser testing UI and e-ink device sync endpoints
- [ ] **Phase 6: Safety, Performance, and Polish** - Multi-turn safety monitoring and <2s latency validation

## Phase Details

### Phase 1: Database Foundation

**Goal**: All child profiles, sessions, interaction events, and mastery state survive server restarts via SQLAlchemy models and Alembic migrations.
**Depends on**: Nothing (first phase — brownfield, so existing in-memory code migrates to DB)
**Requirements**: DB-01, DB-02, DB-03, DB-04, DB-05
**Success Criteria** (what must be TRUE):

  1. Server restart does not lose child profiles, session records, or mastery state
  2. `alembic upgrade head` runs cleanly on a fresh SQLite file and on PostgreSQL
  3. Existing chat and STT endpoints continue to pass their evals after the migration
  4. Interaction events (kc_id, correct, response_ms, hint_used, timestamp) are written on every chat turn

**Plans**: 7 plans

Plans:
**Wave 1**

- [x] 01-01-PLAN.md — Bootstrap db/ package: install deps, ORM models, session factory, dev seeds, pytest-asyncio fixture

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 01-02-PLAN.md — TDD: ChildProfile CRUD (create, read by id/device_id, list, update_interests) + seed idempotency
- [x] 01-04-PLAN.md — Alembic init, async env.py, initial migration (all 4 tables), upgrade/downgrade verified

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 01-03-PLAN.md — TDD: Session, InteractionEvent, MasteryState CRUD

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 01-05-PLAN.md — Migrate services/profiles.py and services/sessions.py to thin wrappers; remove stt.py dead import

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 01-06-PLAN.md — Wire DB into api/main.py lifespan + api/chat.py session injection
- [x] 01-07-PLAN.md — Session injection into remaining 5 API routes; remove vars() serialisation

**Key decisions / risks:**

- In-memory `services/profiles.py` and `services/sessions.py` stubs must be replaced; eval fixtures must still pass
- Alembic env must support both SQLite (dev) and PostgreSQL (prod) without engine-specific SQL
- DB-05 (mastery state table) is a FK child of DB-02 (child profile) — schema order matters

---

### Phase 2: Knowledge Tracing Backend

**Goal**: The server computes per-child per-KC mastery (BKT) and spaced-repetition schedule (FSRS), and surfaces topic recommendations from that state.
**Depends on**: Phase 1
**Requirements**: KT-01, KT-02, KT-03, KT-04, KT-05
**Success Criteria** (what must be TRUE):

  1. `next_topics(child_id)` returns an ordered list of KCs ranked by FSRS next_review and mastery bucket
  2. After a simulated session that includes correct and incorrect events, BKT p_mastery updates as expected (unit test)
  3. Mastery bucket labels (not_started / fragile / in_progress / solid) appear in the rendered system prompt
  4. A KC whose FSRS next_review is in the future is deprioritised in next_topics() output

**Plans**: 6 plans

Plans:
**Wave 1**

- [x] 02-01-PLAN.md — DB scaffold: ChildFSRSParamsModel, FSRS CRUD, log_turn kc_id/correct, Alembic migration, fsrs dependency

**Wave 2** *(blocked on Wave 1)*

- [x] 02-02-PLAN.md — TDD: BKT update_bkt() + update_bkt_for_session() (KT-01)

**Wave 3** *(blocked on Wave 2)*

- [x] 02-03-PLAN.md — TDD: FSRS update_fsrs_schedule() + fit_fsrs_params() (KT-02)

**Wave 4** *(blocked on Wave 3, parallel pair)*

- [x] 02-04-PLAN.md — TDD: next_topics() + mastery_context_for_prompt() (KT-03, KT-05 partial)
- [x] 02-05-PLAN.md — TDD: POST /sessions/{id}/end endpoint (KT-04)

**Wave 5** *(blocked on Wave 4)*

- [x] 02-06-PLAN.md — build_system_prompt() mastery_context extension + api/chat.py wiring (KT-05)

**Key decisions / risks:**

- simpleKT / FoLiBiKT are the target models; a simpler closed-form BKT is acceptable for v1 and upgradeable later
- FSRS implementation can use the `fsrs-python` reference library — avoid re-implementing the algorithm
- KT-05 (prompt injection) couples this phase to `services/tutor.py`; must not break existing evals

---

### Phase 3: Session Intelligence

**Goal**: Every chat turn is informed by the child's last 24 hours of study — history injected into prompts, prerequisite gaps surfaced, and interest tags updated automatically.
**Depends on**: Phase 2
**Requirements**: HIST-01, HIST-02, HIST-03, CURR-01, CURR-02, CURR-03, CURR-04
**Success Criteria** (what must be TRUE):

  1. The system prompt for a returning child includes a 24-hour session summary (verified in prompt log)
  2. The tutor does not ask questions about a topic whose prerequisites are not yet mastered (enforced, not just advisory)
  3. If a child mentions "volcanoes" twice in a session, "volcanoes" appears as an interest tag in their profile by session end
  4. A topic in the `supersedes` chain unlocks automatically once the prerequisite hits `bloom_target` mastery

**Plans**: 4 plans

Plans:
**Wave 1** *(parallel pair — no shared files)*

- [x] 03-01-PLAN.md — TDD: get_24hr_history, get_turns_by_session_id, get_most_recent_ended_session CRUD functions (HIST-03)
- [x] 03-02-PLAN.md — TDD: supersedes unlock in next_topics() via _superseded_by reverse index (CURR-04)

**Wave 2** *(blocked on Wave 1 — Plan 01)*

- [x] 03-03-PLAN.md — TDD: services/session_intelligence.py — build_24hr_history_context, build_prereq_tree_context, escalation counter, extract_and_update_interests (HIST-01, HIST-02, CURR-02, CURR-03)

**Wave 3** *(blocked on Wave 2)*

- [x] 03-04-PLAN.md — Wiring: extend build_system_prompt(), add HIST-03 endpoint, wire interest extraction in end_session(), wire all intelligence calls in chat() (HIST-01, HIST-02, HIST-03, CURR-01, CURR-02, CURR-03)

**Key decisions / risks:**

- HIST-01 history summary must be token-budget-aware — inject last N turns, not unlimited history
- CURR-02 prerequisite enforcement: rubber-band escalation pattern (D-04) — soft redirect with escalating probe cadence, not hard block
- CURR-03 interest inference: keyword/tag extraction (v1); vector-embedding approach is v2
- CURR-04 unlock trigger: p_mastery >= 0.95 (solid threshold) — bloom_target is a Bloom integer (1-6), incommensurable with p_mastery (0.0-1.0)
- Phase 3 is the first phase where curriculum.py and the DB are tightly coupled; integration tests required

**UI hint**: no

---

### Phase 4: Parent Dashboard

**Goal**: A parent can log in at `/parent`, review session replays, inspect their child's mastery map, edit the child's profile, and receive alerts for flagged moments.
**Depends on**: Phase 3
**Requirements**: PARENT-01, PARENT-02, PARENT-03, PARENT-04, PARENT-05
**Success Criteria** (what must be TRUE):

  1. Parent can view a turn-by-turn replay of any session from the last 30 days at `/parent/sessions/{id}`
  2. A colour-coded mastery map shows all 777 topics bucketed as not_started / fragile / in_progress / solid
  3. Parent can update neurodivergence flags and reading level and the next chat turn reflects the change
  4. Dashboard displays an alert feed showing sensitive-topic questions, frustration signals, and off-plan interest spikes

**Plans**: 3 plans

Plans:

**Wave 1**

- [x] 04-01-PLAN.md — Auth infrastructure: itsdangerous dep, SessionMiddleware, login/logout routes, AlertModel + safety_flag migration (PARENT-05)

**Wave 2** *(blocked on Wave 1)*

- [x] 04-02-PLAN.md — TDD: Alert CRUD layer + frustration tally at end_session + safety_flag keyword check at log_turn (PARENT-04)

**Wave 3** *(blocked on Waves 1 + 2)*

- [x] 04-03-PLAN.md — Dashboard views: /parent, /parent/sessions/{id}, /parent/children/{id}, /parent/alerts + Jinja2 templates (PARENT-01, PARENT-02, PARENT-03, PARENT-04, PARENT-05)

**Key decisions / risks:**

- Auth: fixed passphrase in .env, itsdangerous-signed session cookie — simple, upgradeable (D-01, D-02)
- Mastery map: 870 topics / 44 subjects (live curriculum count) in subject-grouped accordion using native HTML details/summary
- Alert detection: frustration = hint_used count > 3 per KC per session; sensitive = keyword frozenset; new-interest = Phase 3 interest extraction output

**UI hint**: yes

---

### Phase 4.1: Knowledge Corpus and MCP Server

**Goal**: A manually curated, layered knowledge corpus covering all curriculum topics — with an MCP server that makes it queryable by educators via Claude Code and consumable by the device sync pipeline.
**Depends on**: Phase 4
**Requirements**: CORPUS-01, CORPUS-02, CORPUS-03, CORPUS-04
**Success Criteria** (what must be TRUE):

  1. An MCP server running locally exposes the corpus — an educator can ask "what source material exists for Political Systems 300-level?" and get relevant entries
  2. At least one complete subject (e.g. Political Systems or Manipulation) has L3 wiki pages written for all its topics at appropriate level bands
  3. The source material catalog includes all existing docs/wiki/source-material/ entries tagged to curriculum topic IDs
  4. The device sync endpoint (SYNC-03) can draw pre-generated questions and book passage references from the corpus

**Plans**: 5 plans

Plans:
**Wave 1** *(parallel pair — no shared files)*

- [x] 04.1-01-PLAN.md — Scaffold docs/corpus/ + migrate docs/wiki/source-material/ and docs/experiment-guides/ (CORPUS-02)
- [x] 04.1-02-PLAN.md — TDD: build_index() + search_corpus_impl() against a synthetic fixture corpus (CORPUS-03)

**Wave 2** *(blocked on Wave 1 — parallel pair)*

- [x] 04.1-03-PLAN.md — TDD: 5 MCP tool functions (get_topic/list_sources/search_corpus/get_experiments/list_topics) + validate_topic_ids.py (CORPUS-03, CORPUS-04)
- [x] 04.1-04-PLAN.md — Pilot subject content: 21 Manipulation L3 topic pages (CORPUS-01)

**Wave 3** *(blocked on Wave 2 — Plan 03)*

- [ ] 04.1-05-PLAN.md — Wire FastMCP server, register .mcp.json, document CORPUS-04/Phase 5 integration point (CORPUS-03, CORPUS-04)

**Key decisions / risks:**

- Corpus is manually curated, not auto-ingested from news/feeds — no automation pipeline needed
- L3 wiki pages are the "stable API" — written by hand or Claude-assisted from L1 source material
- MCP server reads from the filesystem (markdown files) or SQLite — no additional service required
- CORPUS-04 feeds Phase 5 SYNC-03 — corpus must be in place before device sync content packages can be built
- **Scope resolution:** CORPUS-01's "all curriculum subjects" is satisfied this phase via full infrastructure + one fully-populated pilot subject (Manipulation, 21 topics); the remaining ~954 topics are an explicit post-phase backlog item, not a phase failure
- MCP registration uses `.mcp.json` at repo root (current Claude Code convention), not `.claude/settings.json`
- Books from Calibre-Web (22,838 titles at 192.168.0.25:8083) are source material for L1 passages; retrieval is manual for v1

**UI hint**: no

---

### Phase 5: Child Interface + Device Sync

**Goal**: A child can interact with the tutor via a browser (for hardware-free testing), and an e-ink device can sync its content package and POST interaction events back to the server.
**Depends on**: Phase 4
**Requirements**: CHILD-01, CHILD-02, CHILD-03, SYNC-01, SYNC-02, SYNC-03
**Success Criteria** (what must be TRUE):

  1. Browser at `/child` accepts voice input via microphone, sends audio to the STT endpoint, and plays back TTS audio automatically
  2. `GET /v1/devices/{id}/sync` returns a valid JSON payload containing focus KCs, mastery buckets, and spaced-rep schedule
  3. `POST /v1/devices/{id}/events` accepts a batch of interaction events and updates the DB mastery state correctly
  4. Content packages (pre-generated questions, book excerpts) are included in the sync response and cache-friendly (ETag / Last-Modified)

**Plans**: TBD

**Key decisions / risks:**

- Browser microphone requires HTTPS in production; localhost exemption works for dev
- E-ink device is offline-capable — sync payload must be self-contained and versioned so stale payloads are rejected gracefully
- CHILD-03 TTS playback: confirm whether server streams Piper/Kokoro audio or returns a URL; decision affects JS client design
- Piper → Kokoro-82M migration noted in PROJECT.md — Phase 5 is the right time to evaluate the switch

**UI hint**: yes

---

### Phase 6: Safety, Performance, and Polish

**Goal**: The tutor meets its <2s end-to-end latency target and passes multi-turn safety checks, with all safety signals wired to the parent dashboard alert feed.
**Depends on**: Phase 5
**Requirements**: SAFETY-01, SAFETY-02, SAFETY-03, SAFETY-04, LATENCY-01, LATENCY-02, LATENCY-03
**Success Criteria** (what must be TRUE):

  1. End-to-end latency benchmark (mic → Whisper → LLM → first Piper/Kokoro word) is profiled and meets <2s on target hardware for 80th percentile
  2. A 500ms acknowledgment audio ("Hmm, let me think...") plays within 500ms of VAD end, verified by automated timing test
  3. The multi-turn safety monitor detects a simulated foot-in-the-door escalation sequence and logs an alert (unit test with synthetic turns)
  4. Answer-reveal rate per session is logged; any session exceeding 10% triggers a PEDAGOGICAL_SAFETY alert in the parent dashboard

**Plans**: TBD

**Key decisions / risks:**

- LATENCY-02 pre-generated cache: key by (child_id, topic, mastery_bucket) — invalidate on profile change
- SAFETY-01 multi-turn monitoring: stateless LLM calls miss context; monitor must read session turn log from DB
- SAFETY-02 child age injection is a one-line change to tutor.py but must be regression-tested against existing evals
- KIDBench and SafeTutors benchmarks are the reference; log pass/fail against them in the eval suite

---

## Progress

**Execution Order:** 1 → 2 → 3 → 4 → 4.1 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Database Foundation | 7/7 | Complete    | 2026-07-14 |
| 2. Knowledge Tracing Backend | 6/6 | Complete   | 2026-07-16 |
| 3. Session Intelligence | 4/4 | Complete   | 2026-07-17 |
| 4. Parent Dashboard | 3/3 | Complete   | 2026-07-20 |
| 4.1. Knowledge Corpus and MCP Server | 4/5 | In Progress|  |
| 5. Child Interface + Device Sync | 0/TBD | Not started | - |
| 6. Safety, Performance, and Polish | 0/TBD | Not started | - |
