# etutor-server

## What This Is

An AI-powered tutoring server for a child's e-ink reading device (Kobo/Kindle-class hardware). Children aged 6–12 interact with an AI tutor through voice — Whisper STT converts speech to text, Claude/Haiku responds with Socratic questions calibrated to the child's age, reading level, and neurodivergence profile, and Piper TTS reads responses aloud. The device syncs content and session history with this FastAPI server.

The tutor follows evidence-based pedagogy: Socratic questioning, spaced repetition, interleaving, retrieval practice, and hint ladders. It never gives away answers unprompted (zero-shot LLMs do this 66% of the time — the evals gate on <10%).

The curriculum covers 777 topics across 28 subjects, from English NC KS1–KS3 through world religions, aerospace, music theory/production, sports medicine, performing arts, and model progressions ("lies to children" refined by mastery). Topics have prerequisites, Bloom entry/target levels, age-gating, and exceed-level flags.

## Core Value

A child should be able to ask any question, follow it as far as their curiosity takes them — including to university-level depth — and have a tutor that meets them at their level, remembers everything they've studied, and never has a ceiling.

## Context

**Stack:** FastAPI + uvicorn | SQLite (dev) / PostgreSQL (prod) via SQLAlchemy | faster-whisper (STT) | Piper TTS | litellm routing (Claude/GPT/Ollama) | Calibre-Web integration

**What exists (implemented):**
- `services/tutor.py` — system prompt builder, age/reading-level/neurodivergence instructions, hint ladder
- `services/curriculum.py` — 777 topics, prerequisites, Bloom levels, interest matching, exceed-level, model progressions
- `api/chat.py` — OpenAI-compatible chat completions endpoint
- `api/stt.py` — Whisper transcription endpoint
- `services/profiles.py` — in-memory child profiles (NOT persistent)
- `services/sessions.py` — session logging stub
- `tests/evals/` — four passing evals: answer-reveal rate, Socratic quality, hint ladder, curriculum accuracy
- `docs/pedagogy.md` — grounded design principles with research citations
- `docs/research.md` — deep literature review (100+ papers with DOIs/arXiv IDs)
- `docs/pedagogy-montessori.md` — Montessori evidence synthesis
- `docs/wanted-books.md` — reference library and reading samples

**What does NOT exist yet:**
- Database (everything is in-memory — no persistence across restarts)
- Knowledge tracing (BKT + FSRS — designed, not implemented)
- Session history injection into prompts
- Interest graph inference
- Learning plan generation (planner service stub)
- Parent dashboard (scaffolded empty)
- Child web interface (templates present, untested)
- Calibre-Web integration (recommender stub)
- STT/TTS latency profiling

## Users

**Primary:** Children ages 6–12 using an e-ink device (voice-first interaction).
**Secondary:** Parents — set up profiles, review session history, add books, configure neurodivergence flags.
**Tertiary:** The device itself — syncs content packages, submits audio, receives AI responses.

## Constraints

- E-ink display: 300ms partial refresh minimum — no animations, no drag-and-drop
- Voice-first: all interaction through Whisper STT + Piper TTS
- Offline-capable: device caches content for low-connectivity use
- Privacy: COPPA-compliant (children under 13) — minimal data collection, no raw audio stored
- Whisper WER on child speech: ~13-18% for ages 8-11, ~37% for ages 6-7 — UI must tolerate errors
- <2s end-to-end latency target (mic → Whisper → LLM → Piper first word)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Socratic-first prompting | MathDial (EMNLP 2023): zero-shot LLMs give away answers 66% of the time; eval gates on <10% | Implemented in system prompt + eval |
| Verify-then-generate for hints | Daheim et al. EMNLP 2024: error localization before feedback reduces hallucinations | Specified, not implemented |
| simpleKT + FoLiBiKT for knowledge tracing | Best fair-evaluation baseline; forgetting-curve bias drop-in | Designed, not built |
| FSRS over SM-2 for spaced repetition | Handles overdue cards, no ease hell, personalises per child | Designed, not built |
| No ceiling on curriculum depth | A curious child should reach university-level depth without hitting an age wall | Implemented via accelerated_ok, model_level, supersedes fields |
| Neurodivergence as prompt flags | 7 flags (dyslexia, ADHD, autism, etc.) adjust tutor behaviour without changing the child's experience | Implemented in tutor.py |
| Piper → Kokoro-82M for TTS | Piper archived read-only Oct 2025, GPL-3.0 successor; Kokoro is Apache 2.0, higher quality | Noted, not migrated |

## Requirements

### Validated

- ✓ Socratic tutoring with age-appropriate Bloom level — eval-tested
- ✓ Answer-reveal rate <10% — eval-tested (0% on Haiku)
- ✓ Reading level calibration by grade (grade 1 through 8+)
- ✓ Neurodivergence profile flags wired into system prompt
- ✓ 777-topic curriculum with prerequisites, Bloom levels, exceed-level
- ✓ Voice STT endpoint (Whisper, OpenAI-compatible)
- ✓ Chat endpoint (litellm routing)

### Active

- [ ] Persistent database (SQLite → PostgreSQL via SQLAlchemy/Alembic)
- [ ] Per-child session history (last 24hr injected into prompt — +6.1% correctness, Khanmigo data)
- [ ] Knowledge tracing backend (BKT per-concept mastery + FSRS scheduling)
- [ ] Curriculum integration with tutor (topic graph → session context)
- [ ] Interest graph inference from session history
- [ ] Learning plan generation
- [ ] Parent dashboard API + UI
- [ ] Child web interface (browser-based testing without hardware)
- [ ] Calibre-Web book integration
- [ ] Device sync endpoint (content packages)
- [ ] STT/TTS latency profiling + <2s target validation
- [ ] Safety guardrails (SafeTutors benchmark: pedagogical safety, not just content filtering)
- [ ] Multi-turn safety monitoring (foot-in-the-door attacks; 94% success rate on frontier models)

### Out of Scope (v1)

- Fine-tuning open-weights models — API-based routing sufficient for v1
- Native mobile app — device uses browser-based interface
- Multi-child family dashboard — single child per device for v1
- Social features — solo tutoring only
- Video content — e-ink can't render it

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions

---
*Last updated: 2026-07-15 after Phase 1: Database Foundation*
