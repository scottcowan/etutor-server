# Requirements — etutor-server

## v1 Requirements

### DB-01: Persistent Database
- [x] **DB-01**: SQLite database with SQLAlchemy ORM and Alembic migrations replaces in-memory stores
- [x] **DB-02**: ChildProfile persisted (name, age, reading_level, interests, neurodivergence, device_id)
- [x] **DB-03**: Session records persisted (session_id, child_id, started_at, ended_at, turn count)
- [x] **DB-04**: Interaction events persisted (kc_id, correct, response_ms, hint_used, timestamp)
- [x] **DB-05**: Concept mastery state persisted per child×KC (BKT params + FSRS params)

### KT-01: Knowledge Tracing
- [ ] **KT-01**: BKT mastery model per child per KC (p_mastery, p_learn, p_slip, p_guess)
- [ ] **KT-02**: FSRS scheduling fields per child×KC (stability, difficulty_d, card_state, next_review)
- [ ] **KT-03**: next_topics() uses mastery state + FSRS next_review to recommend session content
- [ ] **KT-04**: After each session, BKT params updated from interaction log
- [ ] **KT-05**: Mastery bucket labels (not_started / fragile / in_progress / solid) injected into system prompt

### HIST-01: Session History Injection
- [ ] **HIST-01**: Last 24hr session summary injected into every system prompt
- [ ] **HIST-02**: Prerequisite skill gaps surfaced in prompt context
- [ ] **HIST-03**: Session turn log stored and retrievable per session_id

### CURR-01: Curriculum Integration
- [ ] **CURR-01**: Tutor session selects focus topics from curriculum.py using next_topics() + child interests
- [ ] **CURR-02**: Topic prerequisites enforced — tutor cannot ask questions about a locked topic
- [ ] **CURR-03**: Interest tags updated from session history (child mentions volcanoes → tag added)
- [ ] **CURR-04**: Model progression topics (supersedes field) unlock when prerequisite mastered to bloom_target

### PARENT-01: Parent Dashboard
- [ ] **PARENT-01**: Parent can view session history (turn-by-turn replay)
- [ ] **PARENT-02**: Parent can view child's mastery map (topics × mastery bucket)
- [ ] **PARENT-03**: Parent can set/edit child profile (interests, neurodivergence flags, reading level)
- [ ] **PARENT-04**: Parent receives flags for: sensitive topic questions, frustration signals, off-plan interest spikes
- [ ] **PARENT-05**: Parent dashboard web UI accessible at /parent

### CHILD-01: Child Web Interface
- [ ] **CHILD-01**: Browser-based child interface functional for testing without hardware (at /child)
- [ ] **CHILD-02**: Voice input works via browser microphone (WebRTC → STT endpoint)
- [ ] **CHILD-03**: TTS responses play automatically in browser

### SAFETY-01: Safety and Guardrails
- [ ] **SAFETY-01**: Multi-turn safety monitoring (not just per-message filtering)
- [ ] **SAFETY-02**: Child age injected into every system prompt (improves safety 10-47% per KIDBench)
- [ ] **SAFETY-03**: Pedagogical safety: answer-reveal rate monitored per session, logged if >10%
- [ ] **SAFETY-04**: Parasocial relationship signals flagged to parent dashboard

### SYNC-01: Device Sync
- [ ] **SYNC-01**: /v1/devices/{id}/sync returns: focus concepts for session, mastery state buckets, spaced-rep schedule
- [ ] **SYNC-02**: Device POSTs interaction events back after session
- [ ] **SYNC-03**: Content packages (pre-generated questions, book excerpts) bundled in sync response

### LATENCY-01: Performance
- [ ] **LATENCY-01**: End-to-end latency profiled (mic → Whisper → LLM → Piper first word)
- [ ] **LATENCY-02**: Common session-start responses pre-generated and cached
- [ ] **LATENCY-03**: Acknowledgment audio plays within 500ms of VAD end

## v2 Requirements (deferred)

- Calibre-Web book recommendation integration
- Fine-grained interest graph (vector embeddings of session transcript)
- Parent read-aloud recording playback (captured in .planning/todos/)
- Historical language two-pass modernisation system
- Per-book language notes (modernised vs original text flag)
- FSRS per-child parameter personalisation (requires 50+ interactions per KC)
- Experiment guides interactive mode (tutor walks through lab step-by-step)

## Out of Scope (v1)

- Fine-tuning open-weights models — API routing sufficient
- Native mobile parent app — web dashboard adequate
- Multi-child household management — single child per device
- Social/peer features — solo tutoring only
- Video content — e-ink hardware constraint
- Billing/subscription — internal/family use

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DB-01 | Phase 1: Database Foundation | Complete |
| DB-02 | Phase 1: Database Foundation | Complete |
| DB-03 | Phase 1: Database Foundation | Complete |
| DB-04 | Phase 1: Database Foundation | Complete |
| DB-05 | Phase 1: Database Foundation | Complete |
| KT-01 | Phase 2: Knowledge Tracing Backend | Pending |
| KT-02 | Phase 2: Knowledge Tracing Backend | Pending |
| KT-03 | Phase 2: Knowledge Tracing Backend | Pending |
| KT-04 | Phase 2: Knowledge Tracing Backend | Pending |
| KT-05 | Phase 2: Knowledge Tracing Backend | Pending |
| HIST-01 | Phase 3: Session Intelligence | Pending |
| HIST-02 | Phase 3: Session Intelligence | Pending |
| HIST-03 | Phase 3: Session Intelligence | Pending |
| CURR-01 | Phase 3: Session Intelligence | Pending |
| CURR-02 | Phase 3: Session Intelligence | Pending |
| CURR-03 | Phase 3: Session Intelligence | Pending |
| CURR-04 | Phase 3: Session Intelligence | Pending |
| PARENT-01 | Phase 4: Parent Dashboard | Pending |
| PARENT-02 | Phase 4: Parent Dashboard | Pending |
| PARENT-03 | Phase 4: Parent Dashboard | Pending |
| PARENT-04 | Phase 4: Parent Dashboard | Pending |
| PARENT-05 | Phase 4: Parent Dashboard | Pending |
| CHILD-01 | Phase 5: Child Interface + Device Sync | Pending |
| CHILD-02 | Phase 5: Child Interface + Device Sync | Pending |
| CHILD-03 | Phase 5: Child Interface + Device Sync | Pending |
| SYNC-01 | Phase 5: Child Interface + Device Sync | Pending |
| SYNC-02 | Phase 5: Child Interface + Device Sync | Pending |
| SYNC-03 | Phase 5: Child Interface + Device Sync | Pending |
| SAFETY-01 | Phase 6: Safety, Performance, and Polish | Pending |
| SAFETY-02 | Phase 6: Safety, Performance, and Polish | Pending |
| SAFETY-03 | Phase 6: Safety, Performance, and Polish | Pending |
| SAFETY-04 | Phase 6: Safety, Performance, and Polish | Pending |
| LATENCY-01 | Phase 6: Safety, Performance, and Polish | Pending |
| LATENCY-02 | Phase 6: Safety, Performance, and Polish | Pending |
| LATENCY-03 | Phase 6: Safety, Performance, and Polish | Pending |
