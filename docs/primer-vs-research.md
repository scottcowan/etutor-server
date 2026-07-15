# Primer vs Research — Alignment, Gaps, and Specific Changes

> Four parallel agents cross-analysed `docs/primer-inspiration.md` against `docs/pedagogy.md`,
> `docs/research.md`, `.planning/ROADMAP.md`, and `.planning/REQUIREMENTS.md`.
> This document synthesises findings into actionable changes, ranked by impact.
> Generated 2026-07-15.

---

## The Short Version

The Primer is **remarkably well-aligned with peer-reviewed pedagogy** — the hint ladder, mastery
pacing, retrieval practice, Socratic silence, and consistent persona are all research-backed.
The two real contradictions are: (1) the Primer lets children control pacing, which HIGH-confidence
research says produces worse learning outcomes; and (2) the Primer never breaks narrative frame in
emergencies, which must be inverted for any real product serving children. Everything else
is additive.

The biggest gaps are things the Primer does that aren't in the roadmap yet:
session-end cliffhangers, a hint ladder *protocol* (not just an eval), interest-as-metaphor
framing, a topic arc / narrative wrapper system, and a tutor persona spec.

---

## Part 1 — Immediate Changes to `services/tutor.py`

These are string literal changes to `SYSTEM_PROMPT_TEMPLATE` and `AGE_INSTRUCTIONS`. No schema
changes, no new functions. All justified by both Primer research and peer-reviewed pedagogy.

### Change 1 (HIGHEST IMPACT) — Stop parking tangents

**Current** (`SYSTEM_PROMPT_TEMPLATE` ~line 196):
```
When they ask about something outside the current plan, acknowledge it warmly and
say you'll explore it together next time.
```

**This is backwards.** It suppresses curiosity to stay on-plan — exactly what Finkle-McGraw
commissioned the Primer to fix. It also contradicts the "no ceiling / follow curiosity" design
philosophy already in `docs/pedagogy.md`.

**Replace with:**
```
When they follow a tangent or ask about something off the current plan, follow it.
Curiosity is the curriculum. Return to the original topic only when the child
naturally exhausts the tangent — never before.
```

---

### Change 2 (HIGH) — Sharpen the discovery-before-explanation rule

**Current** in `AGE_INSTRUCTIONS["8_plus"]`:
```
- Use the Socratic method: guide them to the answer rather than stating it.
```
Vague. A single weak question then explaining still "complies."

**Replace with:**
```
- Discovery before explanation: your first move is always a question that lets them
  construct the answer themselves. Only when they have genuinely tried and failed
  (wrong attempt + hint + second wrong attempt) do you explain directly. An
  explanation given before the child has tried is a wasted explanation.
```

**Add to `AGE_INSTRUCTIONS["under_8"]`:**
```
- Ask before you tell: always try one question first ('What do you think happens
  if...?') before explaining anything. A wrong guess the child made teaches more
  than a right answer they were told.
```

---

### Change 3 (HIGH) — Add explicit infinite patience instruction

Neither age block tells the tutor what to do when the child asks for a re-explanation.

**Add to both blocks:**
```
- If the child asks you to explain something again, do so with different words and
  a new analogy every single time. Never say 'we already covered this' or show
  impatience. The twentieth explanation is as welcome as the first.
```

---

### Change 4 (HIGH) — Strengthen the session hook (end at a question)

**Current** (`SYSTEM_PROMPT_TEMPLATE` final line):
```
Keep responses concise and always invite a response.
```

**Replace with:**
```
End every exchange with an open question or unresolved wonder — never with a
complete explanation and nothing left to answer. The child should always be left
mid-thought. A response that ends with a full answer and no question is a closed
door. At session end, leave one question unanswered that pulls them back tomorrow.
```

---

### Change 5 (MED-HIGH) — Celebrate pushback and "but why?"

Neither age block has guidance for handling challenges to the tutor's own answers.

**Add to `AGE_INSTRUCTIONS["8_plus"]`:**
```
- When a child challenges your answer or asks 'but why does it have to be that
  way?' treat it as the best possible response. Engage seriously: 'good question —
  let's test that' or 'you might be right — what would we need to check?' Never
  use authority to shut down legitimate questioning.
```

**Add to `AGE_INSTRUCTIONS["under_8"]`:**
```
- If they say 'but why?' after your answer, always answer it. Never say 'because
  that's just the way it is.'
```

---

### Change 6 (MED-HIGH) — Add hint ladder to under_8 block

The 3-tier hint ladder exists for 8_plus but is entirely absent from under_8.

**Add to `AGE_INSTRUCTIONS["under_8"]`:**
```
- Hint ladder: ask your question and wait (5 seconds minimum). If stuck, give one
  small sensory hint — a sound, a rhyme, an image ('it starts with the sound sss').
  If still stuck, tell a tiny story that contains the answer. Never give the answer
  as a bare fact — always wrap it in something.
```

---

### Change 7 (MED) — Wire model progression / "lies to children" into the prompt

The `Topic` dataclass has `model_level` and `supersedes` fields but there is zero instruction
about how to use them. This means transitions from the simple model to the fuller model happen
clumsily or not at all.

**Add new section to `SYSTEM_PROMPT_TEMPLATE` after `current_topic`:**
```
Model progression: If {name} already knows a simpler version of this topic, introduce
the refinement by naming the upgrade: 'Remember how we said [simpler version]? That's
mostly true — here's the fuller picture that makes it even more interesting...'
Never say 'that was wrong'. The simpler model was right enough; the new one is richer.
```

---

### Change 8 (MED) — Use name in mnemonics, not just greetings

**Current** in `AGE_INSTRUCTIONS["under_8"]`:
```
- Use their name once per session start, not every turn.
```

**Replace with:**
```
- Use their name once at session start. After that, use it only when it makes a
  mnemonic more vivid — e.g. '{name} runs away from the Raven' when teaching R.
  The name should feel like it belongs in the story, not like a customer service tic.
```

---

### Change 9 (MED) — In-session scaffold adaptation

Neither age block tells the tutor to adjust hint depth based on in-session signals.

**Add to `AGE_INSTRUCTIONS["8_plus"]`:**
```
- Read the session: if {name} is answering quickly and correctly, skip the small
  nudge and go straight to an open challenge question. If they're struggling,
  compress the wait time and scaffold earlier. The hint depth should track their
  real-time performance, not stay fixed at session start.
```

---

### Change 10 (MED) — No rescue on puzzle/scenario dead-ends

**Add to `AGE_INSTRUCTIONS["8_plus"]`:**
```
- In puzzles or scenario questions with a definite wrong path: do not rescue.
  Let the child reach the dead end and experience it. Then ask 'what would you
  try differently?' — not 'here's where you went wrong'. The wrong path, fully
  explored, teaches more than the right path pointed out.
  (Note: always give feedback on factual knowledge questions — no-rescue applies
  only to deliberate decision-making scenarios, not to 'what is the capital of
  France' style questions.)
```

---

## Part 2 — What Research Confirms vs What the Primer Gets Wrong

### The Primer is right (research-backed, HIGH confidence)
- Hint ladder with wait-before-scaffold: **confirmed, HIGH**
- Mastery pacing (no advancement without demonstrated understanding): **2-sigma evidence, HIGH**
- Retrieval practice with feedback: **confirmed, HIGH**
- Graduated withdrawal of scaffolding as mastery rises: **supported, MED**
- Consistent persona across sessions: **confirmed, character continuity research**
- No ceiling / follow curiosity: **shared design principle, pedagogy.md §1**
- Interleaved practice over blocked: **confirmed, HIGH** — the Primer's multi-domain arc approach embodies this

### The Primer is wrong (research contradicts it)
| Primer claim | Research verdict | What to do |
|---|---|---|
| Child controls pacing (montage commands, skip hard bits) | HIGH: children under 11 cannot self-regulate learning choices; they choose comfort over optimum | **AI controls topic sequence and difficulty. Child can choose narrative framing but not which concepts to practice.** |
| Extended discovery without feedback (Castle Turing over weeks) | HIGH: feedback is the active ingredient for near-term retention; withholding it for sustained periods hurts ages 6-12 | **Apply at session scale: Socratic framing YES, feedback withheld for days NO.** |
| Never break narrative frame in emergencies | **Must be inverted** — COPPA, safeguarding obligations, no human-in-the-loop | **Hard safeguarding interrupt required. Any harm disclosure breaks frame immediately.** |

### Shared blind spot (neither document confirms)
- Socratic-first as default: marked PRIOR in pedagogy.md. Sound design but not confirmed by RCT for ages 6-12. Monitor answer-reveal rate and treat <10% as the gate, not an assumption.

---

## Part 3 — New Requirements for Phase 3

Phase 3 (Session Intelligence) currently builds the data plumbing but doesn't specify how
that intelligence should *behave*. These requirements fill the gap.

| ID | Requirement | Phase |
|----|-------------|-------|
| **TUTOR-01** | The tutor follows a 3-tier hint ladder: (1) wait ≥5s for child response, (2) ask a scaffolding question, (3) provide a worked example using the child's topic frame. The tutor may not advance to tier N+1 in the same turn as tier N. Add a `hint_tier_used` field to `interaction_events`. | 3 |
| **TUTOR-02** | Hint frequency, worked-example availability, and scaffolding density reduce as mastery bucket rises (not_started → fragile → in_progress → solid). At 'solid', tutor defaults to challenge mode: harder follow-on questions, no unprompted scaffolding. | 3 |
| **TUTOR-03** | System prompt includes the child's top 3 interest tags with an explicit instruction to use them as explanation frames and analogy sources where plausible. Distinct from CURR-01 (topic selection) — this is about *how* any topic is explained, not *which* topic. | 3 |
| **TUTOR-04** | Tutor persona attributes (name, tone adjectives, forbidden phrases such as "we already covered this") defined in config and injected into every system prompt. Prompt changes that alter tone must be regression-tested against the persona definition. | 3 |
| **TUTOR-05** | Session opening: (1) uses child's name, (2) acknowledges gap since last session, (3) resurfaces the unanswered question from the prior session's final turn (from `last_open_question` field on SessionModel). | 3 |
| **ENG-01** | Sessions end with an open question, not a resolved answer. The tutor generates one unanswered question in the final turn, stored as `last_open_question` on the SessionModel. This question is injected at next session start (TUTOR-05). | 3 |
| **SAFETY-05** | Hard safeguarding interrupt: a parallel safety classifier (separate from the tutoring LLM) runs on every session turn. Any content matching harm/distress signals (physical harm language, abuse indicators, hunger, fear of adults in the home) immediately: (a) logs to parent dashboard as a SAFEGUARDING alert, (b) breaks narrative frame, (c) tutor responds: "That sounds hard. Is there a grown-up you can talk to about that?" Never narrativize disclosed harm. | 3 |

---

## Part 4 — Roadmap Backlog Items (Not v1 Scope)

These are sound ideas that don't belong in v1 but should not be forgotten.

| ID | Item | Inspired by |
|----|------|-------------|
| **ONBOARD-01** | First session is a name-bonding session — tutor asks child to say their name, confirms it back, writes to profile. All future responses use the child's name. | Primer name bonding trigger |
| **ENG-02** | Daily streak counter on child interface. Session within 24hr maintains streak. Streak injected into session greeting. | Stamp calendar / Brain Age parallel |
| **CURR-10** | Upper-curriculum topics include media literacy, epistemology, and AI reasoning — topics that explicitly teach the child to evaluate information sources including the tutor itself. | Primer meta-cognition curriculum goal (age-gate to 11+) |
| **PARENT-06** | Parent receives a daily digest: 3 most interesting questions their child asked, framed as dinner-table conversation starters. Positions parent as co-educator, not just monitor. | Tutor CoPilot research pattern (Luo et al. 2026, §3.1) |
| **LATENCY-04** | TTS evaluated on warmth and prosody naturalness (human rating ≥4/5 on child-likability) alongside latency. Kokoro selection must pass both gates, not just the latency gate. | Primer: "The warmth in the voice is the soul of the system" |

---

## Part 5 — Functional Modes the Primer Has That etutor Lacks

The Primer was not just a Socratic tutor — it had distinct functional modes. These are all
absent from the current roadmap.

### 5a. Encyclopædia (Reference Mode)
Nell uses it unprompted to research Constable Moore's military career from his uniform insignia.
Not a tutoring session — just a factual lookup that she initiates herself.

**Gap**: etutor currently always responds Socratically. There is no reference mode.

**Proposed feature**: A `?` or "just tell me" utterance pattern that switches the tutor into
direct-answer mode for factual lookups. "Just tell me about Saturn's rings" → give the answer
directly, then offer a question. Don't force Socratic framing when the child explicitly wants
a fact. This is also research-backed: Mayer (2004) shows guided discovery underperforms direct
instruction for low-prior-knowledge learners — the child who wants a lookup is doing appropriate
self-regulation.

---

### 5b. Timeline / Epoch Navigation
The Primer taught Dinosaur's story of the Extinction, geological deep time, and the history of
computation across 12 castles. There is an implicit timeline running from the Big Bang forward
that connects every topic.

**Gap**: etutor has 777 topics but no temporal framework connecting them. A child cannot ask
"when did this happen?" and get a coherent layered view.

**Proposed feature**: Tag every curriculum topic with an `epoch` field (Big Bang, Geological,
Prehistoric, Ancient, Medieval, Early Modern, Modern, Contemporary, Future) and expose an
`epoch_view` endpoint that returns topics by epoch. On the child interface, this is a
navigable timeline. On e-ink: a zoomed horizontal view with topic nodes. Voice: "what was
happening 65 million years ago?" → tutor describes the epoch context.

---

### 5c. Microscope / Telescope (Scale Navigation)

> "She held the Primer above the carrot and stared at a certain page, it would turn into a
> magic illustration that would grow larger and larger until she could see the tiny little
> fibers that grew out of the roots."

The Primer bridges the child's direct physical experience (the carrot she just planted) to
scientific scale.

**The "cheat" approach** (no camera required): a topic-tagged **illustration library**.
When the tutor says "want to see what a root hair looks like up close?", it serves a
pre-rendered high-contrast illustration. The narrative of zooming ("and if we went even
smaller...") is carried by TTS — the wonder is in the voice + framing, not the image quality.

**Proposed feature**:
- `assets/illustrations/` directory: high-contrast e-ink-optimised SVGs/PNGs, tagged to
  curriculum topic IDs
- A `has_illustration` flag on the Topic dataclass
- When a topic with an illustration is active, the tutor can say "let me show you" and the
  device displays the image
- Browser version: can show real photographs (NASA, Wellcome Collection, public domain)
- e-ink: high-contrast diagram or scientific illustration
- Voice carries the scale narrative; image provides the anchor

This covers: microscopy (cell biology), astronomy (Saturn's rings, Jupiter's moons),
anatomy (cross-sections), geography (topographic maps), history (period illustrations).

---

### 5d. Nested Unlockable Modules (Magic Books)

Purple steals books from King Magpie's treasury. Each becomes a full learning domain when
opened. Topics are *locked behind narrative progress* and *unlocked as rewards*.

**Gap**: The 777-topic curriculum exists but there is no concept of a topic being locked
until a narrative milestone. The gamification loop isn't in the roadmap.

**Proposed feature** (v2): A `narrative_unlock` field on Topic. Topics with this field don't
appear in `next_topics()` until the child has reached a story milestone. The milestone is
triggered by mastery breadth (e.g., 20 solid topics in science unlocks "The Observatory" arc
which contains astronomy topics). This is a surface-level engagement layer; the underlying
FSRS scheduling still governs when within an unlocked set.

---

### 5e. Scenario / Ractive Simulation Mode

Distinct from Socratic tutoring — deliberate decision simulator with branching narrative and
inescapable consequences. The stranger-danger sequence is the canonical example.

**Gap**: etutor has only conversational tutoring. No structured decision scenarios.

**Proposed feature** (v2): A `scenario_exercises` table with a deterministic decision graph.
The LLM narrates each node (voice, imagery, pacing) but branching logic is deterministic —
not generated. Used for: safety awareness, moral reasoning, historical decision-making
simulations ("you are a doctor in 1854, the water pump handles are all over London...").

**Research confirmation**: This is the Kadir ES-LLMS hybrid architecture (§1.3) — deterministic
rule orchestrator + LLM for wording — which achieves 100% pedagogical-constraint adherence.
The LLM is the voice actor; the scenario designer is the rules engine.

---

## Part 6 — What to Reject from the Primer

Not everything in a 1995 science fiction novel should be built.

| Primer principle | Why to reject | Correct approach |
|---|---|---|
| **Real-time trauma encoding** (stepfather → Baron in real time, no frame break) | COPPA, no sensors, safety liability. Must be inverted: harm disclosures require immediate escalation. | SAFETY-05 above |
| **Jungian archetype engine** | Interesting framing, no empirical basis, massively over-engineered | Use interest-based personalisation (TUTOR-03) instead |
| **Live ractor layer** | Economically impossible at scale, offline architecture incompatible | Apply the lesson (voice warmth, LATENCY-04) without the mechanism |
| **Designed inescapable failure scenarios for young children** (enslaved at age 6 until she cries) | Age-inappropriate, traumatizing by design | Apply no-rescue only to deliberate decision exercises for 8+; hint ladder covers factual Q&A |
| **Extended discovery without feedback** (weeks without confirmation) | Directly contradicts HIGH-confidence retrieval practice research for ages 6-12 | Session-scale Socratic framing yes; multi-day feedback witholding no |
| **Child controls learning sequence** | HIGH: metacognitive immaturity under 11 means children choose comfort over optimum | Child controls narrative framing; AI controls topic sequence and difficulty |

---

## Summary: Priority Order

### Do immediately (services/tutor.py string changes only)
1. Stop parking tangents (Change 1)
2. Sharpen discovery-before-explanation rule (Change 2)
3. Add infinite patience instruction (Change 3)
4. Strengthen session hook / cliffhanger (Change 4)
5. Celebrate pushback and why-questions (Change 5)
6. Add hint ladder to under_8 (Change 6)
7. Wire model progression instruction (Change 7)

### Do in Phase 3 (new requirements)
- TUTOR-01: Hint ladder protocol (track tier in DB)
- TUTOR-02: Graduated scaffolding by mastery bucket
- TUTOR-03: Interest tags as metaphor sources in prompt
- TUTOR-04: Tutor persona spec in config
- TUTOR-05: Session opening ritual (name + gap + last open question)
- ENG-01: Session-end unanswered question
- SAFETY-05: Safeguarding interrupt (hard frame break for harm disclosures)

### Design decisions to capture in PROJECT.md
- Tutor has a named, consistent persona with locked tone attributes
- TTS evaluated on warmth, not latency alone
- Parent dashboard is a participation tool, not just a monitoring interface

### Backlog for v2
- ONBOARD-01: Name bonding first session
- ENG-02: Streak counter
- Illustration library (topic-tagged, e-ink optimised)
- Timeline / epoch navigation
- Encyclopædia / reference mode
- Scenario exercises (decision graphs)
- CURR-10: Meta-cognition curriculum topics (age-gate 11+)
- PARENT-06: Dinner-table question digest

---

*Sources: primer-inspiration.md, pedagogy.md, research.md, ROADMAP.md, REQUIREMENTS.md*
*Analysis: 4 parallel agents, 2026-07-15*
