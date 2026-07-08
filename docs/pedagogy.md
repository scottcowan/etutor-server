# Pedagogy — Design Principles

Grounding document for eTutor interaction design, system prompts, and content structure.
References: Khan Academy Kids, Intelligent Tutoring Systems research, Bloom's taxonomy, Pimsleur method.

---

## What the Research Says Works

### Intelligent Tutoring Systems (ITS)
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

## Spaced Repetition

Vocabulary and concepts should resurface at optimal intervals (Pimsleur GIR principle):

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
