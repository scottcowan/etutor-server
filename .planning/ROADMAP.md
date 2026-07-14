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

- [ ] **Phase 1: Database Foundation** - Persistent SQLite/PostgreSQL storage replaces all in-memory stores
- [ ] **Phase 2: Knowledge Tracing Backend** - BKT mastery model + FSRS scheduling per child × KC
- [ ] **Phase 3: Session Intelligence** - History injection, curriculum routing, and interest graph
- [ ] **Phase 4: Parent Dashboard** - Session replay, mastery map, profile editor, and alert feed
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

- [ ] 01-03-PLAN.md — TDD: Session, InteractionEvent, MasteryState CRUD

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 01-05-PLAN.md — Migrate services/profiles.py and services/sessions.py to thin wrappers; remove stt.py dead import

**Wave 5** *(blocked on Wave 4 completion)*

- [ ] 01-06-PLAN.md — Wire DB into api/main.py lifespan + api/chat.py session injection
- [ ] 01-07-PLAN.md — Session injection into remaining 5 API routes; remove vars() serialisation

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

**Plans**: TBD

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

**Plans**: TBD

**Key decisions / risks:**

- HIST-01 history summary must be token-budget-aware — inject last N turns, not unlimited history
- CURR-02 prerequisite enforcement needs a decision: hard block (tutor refuses) vs. soft redirect (tutor steers away) — log decision in PROJECT.md
- CURR-03 interest inference can start as keyword extraction; vector-embedding approach is v2
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

**Plans**: TBD

**Key decisions / risks:**

- Auth for parent dashboard: simple token/session cookie is fine for v1 (single-family use); do not over-engineer
- Mastery map with 777 topics needs a browsable UI — consider subject-grouped accordion, not a flat list
- PARENT-04 alert generation requires defining "frustration signal" heuristics (e.g., >3 hint requests on same KC)

**UI hint**: yes

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

**Execution Order:** 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Database Foundation | 3/7 | In Progress|  |
| 2. Knowledge Tracing Backend | 0/TBD | Not started | - |
| 3. Session Intelligence | 0/TBD | Not started | - |
| 4. Parent Dashboard | 0/TBD | Not started | - |
| 5. Child Interface + Device Sync | 0/TBD | Not started | - |
| 6. Safety, Performance, and Polish | 0/TBD | Not started | - |
