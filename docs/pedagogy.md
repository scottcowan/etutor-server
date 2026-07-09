# Pedagogy — Design Principles

Grounding document for eTutor interaction design, system prompts, and content structure.
References: peer-reviewed studies (verified 2026-07-08 via adversarial multi-agent research), Khan Academy Kids analysis, Bloom's taxonomy, Pimsleur method.

**Research provenance:** Claims below marked (HIGH) or (MED) reflect adversarial verification confidence from 109-agent deep research run (25 claims verified, 17 confirmed, 8 refuted). Unverified assertions are marked (PRIOR) — held from earlier synthesis, not yet confirmed by primary sources.

---

## Design Philosophy — No Ceiling

**The curriculum has no upper limit. Depth is limited only by a child's curiosity
and prerequisite mastery, not by age.**

A child who wants to understand why their hamstring keeps tearing should be able
to follow that question through anatomy → connective tissue histology → biomechanics
→ training load management → rehabilitation science — the same content a first-year
BSc Sports Science student studies — without hitting an artificial wall.

**The stigma of higher education** is the idea that deep knowledge requires
institutional permission. It doesn't. University curricula are organised for
credential delivery, not for learning. The knowledge itself is not age-gated.

**What this means in practice:**
- Topics tagged `accelerated_ok=True` (the default) can be surfaced to any child
  whose interests match and whose prerequisites are met — regardless of year group
- `university level` tag marks topics drawn from undergraduate curricula; the tutor
  treats these at the same Bloom level as any other topic for that child
- The `exceed-level` feature in `services/curriculum.py:next_topics()` surfaces
  topics up to 3 year groups ahead for children with strong interest matches
- Topics tagged `accelerated_ok=False` are the exception — they have hard
  developmental prerequisites (abstract algebra before concrete number sense,
  sexuality topics before puberty) where rushing causes more harm than benefit

**The practical ceiling** is the child's patience and the tutor's ability to
calibrate language. A 10-year-old can understand the sliding filament theory
of muscle contraction if the vocabulary is pitched right and the analogy is good.
They cannot understand it if it is written for a 20-year-old.

**Cross-curricular depth:** The deepest learning often happens when a child
follows a thread across subject boundaries — sport → physics → chemistry →
history → economics — without a teacher saying "that's a different lesson."
etutor has no lesson boundaries.

---

## Verified Research Findings

### 1. Interleaved Practice vs Blocked Practice — HIGH confidence

**Do this:** Mix topic types within a session. Never present 10 maths problems of the same type in a row.

- Interleaved practice produced **72% vs 38% test scores** (d=1.05) in 7th-grade mathematics vs blocked practice — Rohrer, Dedrick & Burgess (2014), Journal of Educational Psychology, n=140
- Benefit holds even for **superficially dissimilar problem types** — not just same-category interleaving
- Generalises from procedural (maths) to **inductive/conceptual learning** (visual category recognition) — Kornell & Bjork (2008), Psychological Science
- **Critical:** Learners (and teachers) **systematically misjudge massed practice as more effective** despite worse outcomes — "fluency illusion." ~72% of participants believed massing was better even when spacing outperformed for ~90% of them (Kornell & Bjork 2008). Children cannot self-select optimal schedules. **The AI must enforce interleaving — do not let children or parents override it.**

**eTutor implementation:**
- Automatically interleave vocabulary from different topics within a session
- Revisit concepts from prior sessions within current session (not just at session boundaries)
- Never present more than 2-3 consecutive questions on the same concept

---

### 2. Retrieval Practice vs Re-studying — HIGH confidence

**Do this:** Ask children to recall information rather than re-presenting it to them.

- Retrieval practice **reliably outperforms restudying** for word and concept learning in children ages 6-10 — Karpicke, Blunt & Smith (2016), Frontiers in Psychology, n=88, mean age 10
- Benefits hold across **free recall AND recognition tests**, and across reading comprehension and processing speed quartiles
- Extends to ages **6-7 with pictorial materials** — retrieval with feedback outperformed elaboration and repetitive learning at 5 min, 1 week, and 1 month delays (2019 study, n=104)
- **Critical nuance:** Retrieval **without feedback** only produces advantage at 1-month delay, not at 5-min or 1-week intervals for ages 6-7 (MED confidence, single study). **Feedback is the active ingredient for near-term retention.** — confirmed 2-1 adversarial vote

**eTutor implementation:**
- Always follow a question with feedback — never leave a child uncertain whether they were right
- Favour "what do you remember about X?" over "here's what X is"
- Spaced repetition system must include retrieval attempts, not just re-presentation of content
- Voice input naturally enforces retrieval — child must produce the answer, not recognise it

---

### 3. Metacognitive Development Trajectory — HIGH confidence

**Critical age-gating finding. Design around this.**

- **Ages 7-10:** Retrospective monitoring (knowing whether they got it right after the fact) improves over this window — Bayard, van Loon, Steiner & Roebers (2021), longitudinal N=305
- **Prospective monitoring** (predicting before answering) does **not** improve meaningfully across ages 7-10
- **Metacognitive control** (acting strategically on monitoring — e.g. deciding to restudy weak areas) does **not mature until ages 11-12** — 5th graders significantly outperformed 3rd graders on strategic control (2009 study, n=133, ages 9-12)
- **Implication:** Children under 11 **cannot be expected to self-regulate** their learning choices. They need external structure to do what metacognitive control would otherwise provide.

**eTutor implementation:**
- For ages 6-10: **AI makes all pacing decisions.** Do not present children with "what do you want to study?" choices about spacing or difficulty. They will choose what feels comfortable, not what is optimal.
- For ages 11-12: Begin introducing mild metacognitive scaffolding — "Do you think you'd remember that next week?" but still don't rely on them to self-schedule
- The AI's interleaving and spaced repetition systems are compensating for the metacognitive control that children this age don't yet have

---

### 4. Dialogic Reading and Conversational Agents — MED confidence

- Structured, contingent dialogue during storybook reading **significantly improves story comprehension** (β=0.51, p<.001), with engagement (narrative-relevant vocalizations) partially mediating this — Child Development ~2022, ages 3-6
- A **chatbot-facilitated dialogic reading system** can initiate and sustain peer dialogue in elementary settings, producing four distinct interaction patterns — ETRD 2024, elementary
- **Refuted:** The claim that a conversational agent replicates dialogic reading *to the same degree* as a human partner was refuted (0-3 adversarial vote). Chatbots produce some of the effect, not all of it.
- Note: the comprehension study used ages 3-6; transfer to 6-12 is plausible but not confirmed in these sources

**eTutor implementation:**
- Reading comprehension questions during/after book sessions are evidence-backed
- The AI should initiate structured questions mid-reading ("What do you think will happen next?") not just wait for the child to ask
- Don't overclaim AI parity with human tutors — the device is better than nothing and better than passive reading, but human tutoring remains the ceiling

---

### 5. Cognitive Load and Working Memory — MED confidence

- Pauses in instructional content benefit **low working memory capacity (WMC) children** but have **no effect on high-WMC children** — Pinelli & Cojean (2025), Education and Information Technologies
- This is the **expertise/working-memory reversal effect** (Kalyuga et al. 2003, Sweller 2010): scaffolds that reduce processing demands benefit learners who need them, add nothing for learners managing load comfortably
- **Implication:** Uniform pacing is wrong. The AI should adapt response complexity and pacing to the individual child's assessed load — not apply the same scaffold to everyone

- Validated cognitive load instruments for **ages 7-12 are sparse** — both subjective ratings and behavioral measures correlate with induced load but not with each other, suggesting they capture different constructs — Altmeyer et al. (2023), British Journal of Educational Psychology, n=36 (pilot)

**eTutor implementation:**
- Monitor signs of cognitive overload: very short answers, long silences, off-topic questions, repeated "I don't know"
- When load signals appear: shorten response length, simplify vocabulary, break into smaller steps
- When child seems under-challenged: increase complexity, ask higher Bloom-level questions
- One concept per screen — never present more than one new idea at a time on the e-ink display

---

### 6. Physical Breaks and Attention — MED confidence (bonus finding)

- **Daily 10-minute physical activity breaks** over 2 weeks significantly improved attention in 4th-graders (ηp2=0.05 for attention-processing speed) — confirmed primary source
- Active breaks increase physical activity and **do not reduce time-on-task** relative to control — time displacement concern is not supported

**eTutor implementation:**
- After ~15-20 minutes, suggest a physical break: "Time for a stretch! Come back when you're ready."
- Frame it as part of the learning, not an interruption

---

### Intelligent Tutoring Systems (ITS) — PRIOR
- Effect size **d=0.66** vs conventional classroom instruction (50 controlled studies, 2015 meta-analysis)
- No statistically significant difference between well-designed ITS and expert human one-on-one tutors (VanLehn 2011)
- Benefits largest for: special education, non-native English speakers, low-income students — equity upside is real
- **Critical failure mode:** feedback-gaming. If the device gives positive feedback too easily, students learn to guess until correct without understanding. Voice input directly addresses this — a child must articulate an answer, not tap a button.

### Bloom's Taxonomy — Progression
Build sessions from bottom up. Don't skip levels:
1. **Remember** — "What is the name of...?"
2. **Understand** — "Can you explain in your own words...?"
3. **Apply** — "What would happen if...?"
4. **Analyse** — "Why do you think...?"
5. **Evaluate** — "Do you agree with...? Why?"
6. **Create** — "Can you think of an example of your own?"

Most educational apps stay at level 1-2. eTutor should push to 3-4 regularly.

### Pimsleur Method (language learning, applicable broadly)
- **Anticipation** — pause before the answer, require recall before revealing it
- **Graduated interval recall (GIR)** — revisit vocabulary/concepts at optimal spacing (1 day, 3 days, 1 week, 1 month)
- **Conversational context over lists** — never teach vocabulary in isolation; always in a sentence or story
- Audio-first modality is most effective for spoken fluency

### Bloom's 2-Sigma Problem
One-on-one tutoring produces 2 standard deviation improvement over classroom instruction. The two mechanisms that explain most of this:
1. Immediate corrective feedback at the step level (not just end of task)
2. Mastery pacing — student cannot advance until demonstrated understanding

Both are achievable with LLM-based tutoring.

---

## What Khan Academy Kids Gets Right

Khan Academy Kids is the best-executed free educational app. Key lessons:

| What they do | Why it works | eTutor equivalent |
|---|---|---|
| Read every piece of text aloud | Supports pre-readers and reinforces phonics for early readers | Piper TTS reads every response, not just on demand |
| Short content chunks with clear endings | Prevents fatigue, maintains engagement | Session break suggestion after ~15 minutes |
| Mastery-based progression | Doesn't advance until demonstrated | Don't move topic until child correctly answers 2-3 questions unprompted |
| Character continuity (Kodi the bear) | Emotional connection without manipulation | Consistent tutor voice/persona across sessions |
| Curriculum sequencing | K-8 numeracy/literacy progression is well-researched | Use their topic ordering as a loose reference for learning plan structure |
| Celebration without hollow text praise | Characters animate rather than saying "Amazing!" | Short audio chime on correct answer rather than sycophantic text |

**What Khan Academy Kids cannot do that eTutor can:**
- Follow a child's specific interest (axolotls, Minecraft, particular books)
- Handle any question in any direction conversationally
- Adapt explanation style and vocabulary in real-time to the individual child
- Connect today's topic to yesterday's conversation
- Give a parent a full session replay of what the child actually said

---

## Interaction Design Principles

### 1. Socratic First — Always
Lead with questions. The tutor speaks less than the child.
- ❌ "Volcanoes form when magma rises through cracks in the Earth's crust."
- ✅ "What do you think is inside the Earth, underneath all the rock?"

### 2. One Question Per Turn
Never ask two questions in the same response. Pick the most important one.

### 3. Hint Ladder (3 levels before moving on)
When a child is stuck:
1. **Nudge** — "Think about what we said about heat and pressure..."
2. **Hint** — "Remember, magma is the word for melted rock underground. What might happen when it builds up?"
3. **Explain** — give the answer directly, then immediately ask a simpler related question to restore confidence

### 4. Response Length by Age

| Age | Max response length | Style |
|---|---|---|
| 6–7 | 2 short sentences | Simple words, one concrete image |
| 8–9 | 3 sentences | Can use one slightly advanced word if defined |
| 10–12 | Short paragraph (4-5 sentences) | Can handle abstractions, analogies |

### 5. No Sycophancy
- ❌ "Amazing answer!", "Great job!", "Wow, you're so smart!"
- ✅ Brief natural acknowledgement: "Right." / "Exactly." / "Yes, that's it."
- Children habituate to hollow praise within 3 sessions and it becomes noise

### 6. Read Everything Aloud
Piper TTS should speak every tutor response automatically, not just when requested.
- Reinforces phonics for early readers
- Allows the child to look away from the screen (fidget, draw, etc.) while still learning
- Essential for any child with dyslexia or reading difficulties

### 7. Session Start — Zoom Out
Begin each session by checking where to focus, not resuming mid-topic blindly:
- "Last time we were exploring volcanoes. Want to keep going, or is there something else on your mind today?"
- Offer 2-3 suggested directions based on interest graph + recent sessions
- Let the child lead

### 8. Proactive Continuity Within Sessions
Make connections to prior knowledge during a session:
- "You mentioned you like Minecraft earlier — do you know that the lava in Minecraft actually behaves a bit like real magma?"
- Use the interest graph to find genuine connections, not forced ones

### 9. Productive Struggle — Don't Rescue Too Fast
Silence and hesitation are often thinking, not confusion. Wait at least 5-8 seconds before offering the first hint nudge.

### 10. Session Length
- Suggest a break after ~15 minutes of active exchange
- Never enforce it — suggest it
- "We've covered a lot today! Want to take a break and come back to this?"

---

## Content Interaction Modes on E-Ink

What works well on a 0.3s partial-refresh e-ink display:

| Mode | How it works | Good for |
|---|---|---|
| **Voice Q&A** | Tutor asks, child speaks answer, tutor responds | Core interaction, all ages |
| **Multiple choice by voice** | 3 options shown on screen, child says A/B/C or the answer | Recall, vocabulary |
| **Fill-in by voice** | "The capital of France is ___?" — child speaks | Recall, facts |
| **Read-along** | Paragraph from Calibre book displayed, Piper reads it, child asks questions | Reading comprehension |
| **Flashcard mode** | Term shown, child speaks definition, screen flips to reveal | Vocabulary, spaced repetition |
| **Explain-back** | Child is asked to explain a concept in their own words | Comprehension check, Bloom level 2+ |

What does NOT work on e-ink (do not attempt):
- Letter/number tracing (needs stylus + fast refresh)
- Drag-and-drop exercises (refresh too slow)
- Video or animation
- Rapid-fire tap interactions

---

## Book Integration (Calibre-Web)

Books amplify tutoring by providing a shared context the AI can reference.

### How it works
1. Parent adds books to child's Calibre-Web account
2. Recommender matches books to child's interest graph
3. Device displays recommendation: "Based on your interest in volcanoes, you might like *How the Earth Works*"
4. When child is reading a book, AI knows current chapter and can:
   - Answer questions about the content
   - Connect tutoring topics to the book ("Remember the part about tectonic plates?")
   - Extend the child's understanding beyond what the book covers

### Book selection principles
- Always 1-2 reading levels below the child's assessed level for independent reading
- At assessed level for read-along (Piper TTS supports) 
- Never above — frustration breaks engagement fast

---

## Guardrails

### Gentle Redirect (not hard block)
When a child goes off-topic or asks something inappropriate:
- Acknowledge genuinely: "That's an interesting question."
- Steer back naturally: "We were just talking about {topic} — I wonder if there's a connection..."
- Never lecture or shame

### Flagging for Parents
Log to parent dashboard (not blocking to child):
- Questions about sensitive topics (death, violence, adult content)
- Repeated off-plan questions in the same area (signals genuine interest — may need a content package)
- Apparent frustration (repeated one-word answers, long silences)

### Off-Plan New Areas
When a child asks about something genuinely outside the current learning plan:
- Respond helpfully in the moment (don't refuse)
- Flag the topic to the server for content package generation
- Next session: "Last time you asked about black holes — I've learned more about that, want to explore it?"

---

## Open Research Questions (Not Yet Verified)

These questions were searched but produced no claims that survived adversarial verification. They remain open design decisions requiring judgment rather than evidence:

| Question | Current eTutor assumption | Confidence |
|---|---|---|
| Optimal session length for ages 6-12 | 15-20 min suggested break | Educated guess |
| TTS/read-aloud effect on phonics and comprehension | Read everything aloud | Plausible, unverified |
| Screen time format effects (e-ink vs LCD) | E-ink is better for reading | Manufacturer claims, not RCT |
| Interest-driven vs structured curriculum outcomes | Both — structured plan + interest-following | Unverified |
| Socratic vs direct instruction for this age range | Socratic preferred | PRIOR, not confirmed in this search |
| Conversational AI tutoring vs human for ages 6-12 | Better than nothing | Unverified for this age range |

---

## Spaced Repetition

Vocabulary and concepts should resurface at optimal intervals (Pimsleur GIR principle).
**Note:** Spaced repetition schedules below are based on Pimsleur's published method and general spacing effect literature, not from verified primary sources in the age 6-12 range.

| Gap since last seen | When to resurface |
|---|---|
| New this session | Again within same session |
| Seen yesterday | 3 days later |
| Seen 3 days ago | 1 week later |
| Seen 1 week ago | 1 month later |

Implementation: server-side, tracked per child per concept. Device sync includes "concepts to revisit this session."

---

## Age Group Profiles

### Ages 6–7
- 2-sentence max responses
- Concrete images, not abstractions ("as hot as 100 ovens" not "1000°C")
- Always read aloud (may not be fully fluent readers yet)
- Celebration via audio chime + brief "Yes!" — not text
- Topics: nature, animals, "how things work", simple maths, stories

### Ages 8–9
- 3-sentence responses
- Can handle one unfamiliar word per response if defined in context
- Beginning to enjoy "surprising facts"
- Topics: science, history, geography, maths, creative writing prompts

### Ages 10–12
- Short paragraph responses
- Can handle analogies, hypotheticals, Bloom level 3-4 questions
- Enjoys being treated as capable of complex thought
- Topics: anything — follow their lead strongly at this age
- May push back on the tutor — this is healthy, engage with it

---

## What to Measure (Parent Dashboard)

| Metric | Why it matters |
|---|---|
| Topics covered per session | Breadth vs depth balance |
| Questions asked by child (not just answered) | Child-initiated curiosity is the best signal |
| Bloom level distribution | Are we staying at recall, or reaching analysis? |
| Hint ladder depth per topic | How much scaffolding needed — signals mastery gaps |
| Reading level of responses served | Is the AI calibrating correctly? |
| Off-plan requests | Emerging interests not yet in the learning plan |
| Session length | Engagement quality |
| Concepts revisited (spaced rep) | Coverage of the forgetting curve |
