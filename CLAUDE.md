<!-- GSD:project-start source:PROJECT.md -->
## Project

**etutor-server**

An AI-powered tutoring server for a child's e-ink reading device (Kobo/Kindle-class hardware). Children aged 6–12 interact with an AI tutor through voice — Whisper STT converts speech to text, Claude/Haiku responds with Socratic questions calibrated to the child's age, reading level, and neurodivergence profile, and Piper TTS reads responses aloud. The device syncs content and session history with this FastAPI server.

The tutor follows evidence-based pedagogy: Socratic questioning, spaced repetition, interleaving, retrieval practice, and hint ladders. It never gives away answers unprompted (zero-shot LLMs do this 66% of the time — the evals gate on <10%).

The curriculum covers 777 topics across 28 subjects, from English NC KS1–KS3 through world religions, aerospace, music theory/production, sports medicine, performing arts, and model progressions ("lies to children" refined by mastery). Topics have prerequisites, Bloom entry/target levels, age-gating, and exceed-level flags.

**Core Value:** A child should be able to ask any question, follow it as far as their curiosity takes them — including to university-level depth — and have a tutor that meets them at their level, remembers everything they've studied, and never has a ceiling.

### Constraints

- E-ink display: 300ms partial refresh minimum — no animations, no drag-and-drop
- Voice-first: all interaction through Whisper STT + Piper TTS
- Offline-capable: device caches content for low-connectivity use
- Privacy: COPPA-compliant (children under 13) — minimal data collection, no raw audio stored
- Whisper WER on child speech: ~13-18% for ages 8-11, ~37% for ages 6-7 — UI must tolerate errors
- <2s end-to-end latency target (mic → Whisper → LLM → Piper first word)
<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->
## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
