# etutor

A private AI tutor for children aged 6–12. It runs on your home server and talks to your kids through a Boox e-ink device.

Your child asks a question by voice. The tutor responds with a question back — not an answer. It remembers everything studied, calibrates to their reading level, and never hits a ceiling. A ten-year-old who wants to understand why their hamstring keeps tearing can follow that thread through anatomy, biomechanics, and sports science without the tutor saying "that's too advanced."

---

## What it does

**Teaches through questions, not answers.** Standard LLMs hand over the answer 66% of the time. This tutor's evals gate on under 10%.

**Remembers everything.** Every session is stored. The tutor opens the next session by picking up where you left off.

**Follows curiosity off-plan.** If your child asks about volcanoes in the middle of a fractions lesson, the tutor follows it. Curiosity is the curriculum.

**Adapts to the child.** Reading level, age, neurodivergence flags (dyslexia, ADHD, autism, dyscalculia, anxiety, giftedness) all change how the tutor speaks and what it asks.

**777 topics, no ceiling.** English KS1–KS3, maths, sciences, history, geography, world religions, music theory, aerospace, sports medicine, coding, and more. Topics have prerequisites and Bloom entry levels. A curious child can reach undergraduate depth.

**Parent dashboard.** Session replays, mastery maps, alert feed for sensitive topics or frustration signals.

---

## Curriculum

The 777 topics span 28 subjects. A sample:

**Core:** English reading and writing (KS1–KS3), maths (number sense through calculus), sciences (biology, chemistry, physics, earth science), history, geography, religious studies

**Breadth:** Music theory and production, aerospace engineering, sports medicine and physiology, performing arts, computer science, world economies, philosophy, psychology, forensic science, Norse mythology, surveillance and privacy, the history of corruption

**No artificial ceiling.** A topic tagged `accelerated_ok` can be surfaced to any child whose prerequisites are met, regardless of year group. Topics have Bloom entry and target levels. A solid understanding of fractions unlocks the next layer; university-level content is available when the child is ready for it, not when they turn 16.

**Model progressions.** Many topics have a "lies to children" version and a more accurate one. When a child masters the simpler model, the tutor introduces the refinement: "remember how we said light travels in straight lines? That's mostly true — here's the fuller picture."

---

## Philosophy

> *"I just wish it were a completely self-contained system."*
> *"It might as well be, sir."*
> — Lord Finkle-McGraw commissioning the Primer, *The Diamond Age*

The design starts with a question Finkle-McGraw puts to Hackworth: do you think our schools accomplish the goal of making a child's intellectual life interesting? Or are they like the schools Wordsworth complained of — children noosed and stringed like a poor man's heifer at its feed?

The answer drives everything. A curious child who follows questions wherever they lead, across subject boundaries, into university-level depth, without a teacher saying "that's a different lesson" or "that's too advanced" — that is the product.

> *"Nell... the difference between ignorant and educated people is that the latter know more facts. But that has nothing to do with whether they are stupid or intelligent. The difference between stupid and intelligent people — and this is true whether or not they are well-educated — is that intelligent people can handle subtlety."*
> — Constable Moore, *The Diamond Age*

The tutor's job is not to fill a child with facts. It is to build the habit of following a question until it runs out. Facts accumulate along the way.

> *"She began to speak, the words rushing from her mouth as easily as if she had been reading them from the pages of the Primer."*
> — Nell addressing the Mouse Army, *The Diamond Age*

That sentence describes the tutor's highest goal. When the child no longer needs the tutor because its voice has become their own.

---

## Design decisions

**Socratic first.** The tutor asks before it tells. Every exchange ends with an open question. The standard LLM gives away the answer 66% of the time; this system is built and evaluated to stay under 10%.

**No ceiling.** The child's curiosity is the only limit. The tutor follows tangents rather than redirecting back to the lesson plan.

**Adapted to the child.** Seven neurodivergence flags (dyslexia, ADHD, autism, dyscalculia, dyspraxia, anxiety, giftedness) change the tutor's language, pacing, and approach — not the child's experience of it. Reading level is tracked per grade and adjusts vocabulary and sentence length.

**Hint ladder.** When a child is stuck: wait, then nudge, then hint, then explain. Never skip a tier. The tutor re-explains with different words every time, without impatience.

**Spaced repetition.** BKT mastery tracking per concept, FSRS scheduling for review. The tutor knows what was fragile last week and surfaces it today.

**Inspired by the Primer.** The educational design draws on Neal Stephenson's *Young Lady's Illustrated Primer* from *The Diamond Age* — a fictional AI tutor that adapts stories to the child's life and teaches through consequence rather than instruction. See [`docs/primer-inspiration.md`](docs/primer-inspiration.md).

---

## Hardware

An [Onyx Boox](docs/hardware-boox.md) Android e-ink device runs the client app. The child speaks to it; the server handles everything else. The web browser works as a stand-in during development.

---

## Status

The server is in active development. The Socratic tutoring engine, 777-topic curriculum, STT and chat endpoints, and behavioural evals all work. Persistent database, knowledge tracing, and the parent dashboard are being built now.

See the [roadmap](.planning/ROADMAP.md) for what's next.

---

## Self-hosting

```bash
git clone https://github.com/scottcowan/etutor-server
cd etutor-server
cp config/.env.example config/.env
# add your API key to config/.env
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

Browser testing: http://localhost:8000/child  
Parent dashboard: http://localhost:8000/parent

---

## Behavioural evals

```bash
ANTHROPIC_API_KEY=sk-... pytest tests/evals/ -v

# or with Ollama (no key required)
ETUTOR_EVAL_MODEL=ollama/llama3.2 pytest tests/evals/ -v
```

Evals measure: answer-reveal rate (gate <10%), Socratic quality, hint ladder discipline, tangent-following, session-end hooks, patience on re-explanation.

---

## Technical reference

**Stack:** FastAPI + uvicorn, SQLAlchemy (SQLite dev / PostgreSQL prod), Alembic, faster-whisper, litellm (Claude / GPT / Ollama routing), Piper TTS

**Docs:**
- [`docs/pedagogy.md`](docs/pedagogy.md) — design principles with research citations
- [`docs/research.md`](docs/research.md) — ITS/LLM literature review (100+ papers)
- [`docs/primer-inspiration.md`](docs/primer-inspiration.md) — design notes from *The Diamond Age*
- [`docs/primer-vs-research.md`](docs/primer-vs-research.md) — where the novel and the research agree and disagree
- [`docs/hardware-boox.md`](docs/hardware-boox.md) — Boox device integration guide

**Layout:**
```
api/          HTTP endpoints (chat, STT, sync, sessions, dashboard)
services/     Tutor logic, curriculum, profiles, knowledge tracing
db/           ORM models, CRUD, session factory, seeds
tests/evals/  Behavioural eval suite
docs/         Research, pedagogy, hardware
.planning/    GSD roadmap and phase plans
```

**Related:** [hardware](https://github.com/scottcowan/hardware)
