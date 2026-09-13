# Phase 3: Session Intelligence - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-16
**Phase:** 03-session-intelligence
**Areas discussed:** History summary format, Prerequisite enforcement, Interest extraction, Prerequisite gap surfacing

---

## History Summary Format

| Option | Description | Selected |
|--------|-------------|----------|
| Topic list only | List distinct topics covered in 24hr, minimal tokens | ✓ |
| Turn-count summary per topic | Include kc_id/correct signal per topic | |
| Last N raw Q&A pairs | Verbatim turns, high token cost | |

**User's choice:** Topic list only

| Option | Description | Selected |
|--------|-------------|----------|
| ~50 tokens | ~5-8 topic names | ✓ |
| ~150 tokens | 15-20 topic names | |
| You decide | Leave to planner | |

**User's choice:** ~50 tokens

| Option | Description | Selected |
|--------|-------------|----------|
| Flat list, most recent first | Simple, order implies recency | ✓ |
| Add session boundary marker | Group by session/day | |
| You decide | Leave to planner | |

**User's choice:** Flat list, most recent first

---

## Prerequisite Enforcement

| Option | Description | Selected |
|--------|-------------|----------|
| Soft redirect | Acknowledge, explain prereq, steer | |
| Hard block | Tutor refuses the topic | |
| Prerequisite hint only | Advisory context only | |

**User's choice (free text):** "rubber band, allow them to stray but the steer should start soft and then pull them back eventually"

**Notes:** The rubber-band metaphor captures escalating redirect pressure. Key insight from follow-up: the harder redirect should *probe* understanding of the prerequisite, not assume ignorance — `p_mastery` is low but the child may already know the material from outside the system.

| Option | Description | Selected |
|--------|-------------|----------|
| 2 turns soft, then redirect | Turn 1 hint, Turn 2 suggestion, Turn 3 active steer | |
| 3 turns soft, then redirect | More breathing room | |
| You decide | Leave cadence to planner | |

**User's choice (free text):** "you're assuming the child doesn't know the prerequisite. the harder redirect could be to check their understanding of the pre-reqs"

**Notes:** This reframed the escalation: turn 1 = engage + hint, turn 2 = probe the child's understanding, turn 3+ = active steer only if probe reveals genuine gap.

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — and update mastery state | Correct probe → write p_mastery + continue | ✓ |
| Yes — but don't update mastery state | Unlock for session only | |
| No — probe advisory only | No unlock | |

**User's choice (free text):** "yes, but they deserve a refresher too"

**Notes:** Correct probe → (a) update `p_mastery`, AND (b) give brief refresher before proceeding. Both required.

---

## Interest Extraction

| Option | Description | Selected |
|--------|-------------|----------|
| At session end | After POST /sessions/{id}/end | |
| After each turn | Real-time, adds latency | |
| Scheduled async job | Background task, extra infrastructure | |

**User's choice (free text):** "session end might not exist if child ends early"

**Notes:** Correct concern — device disconnects will leave sessions without a /end call. This forced the dual-trigger decision.

| Option | Description | Selected |
|--------|-------------|----------|
| On session start, over previous session | Always catches previous session | |
| Both: on /end AND on next session start | Belt-and-suspenders | ✓ |
| After each turn | Always fires | |

**User's choice:** Both: on /end AND on next session start

| Option | Description | Selected |
|--------|-------------|----------|
| Match against curriculum topic tags | Use existing Topic.tags | ✓ |
| Extract any noun/topic words | NLP-based, needs new dep | |
| LLM extraction call | High accuracy, adds API cost | |

**User's choice:** Match against curriculum topic tags

---

## Prerequisite Gap Surfacing

| Option | Description | Selected |
|--------|-------------|----------|
| List of blocked topics with missing prereqs | Flat blocked list | |
| Promote prerequisites into next_topics list | next_topics() handles routing | |
| Separate gap list alongside mastery context | Two prompt sections | |

**User's choice (free text):** "short a topic tree with the topics and what they unlock"

**Notes:** Not just a blocked list — show the unlock structure. A child's in-progress topic (e.g., rock_types) shows what it unlocks (plate_tectonics, volcanoes). Motivational framing, not just gap notification.

| Option | Description | Selected |
|--------|-------------|----------|
| One level deep | Direct prereq → unlocks only | ✓ |
| Two levels deep | Fuller path, more tokens | |
| You decide | Leave to planner | |

**User's choice (free text):** "1. but you might need to truncate the next tier topics list"

**Notes:** One level deep, but truncate the unlocks list (cap at 3 per prerequisite). Order by FSRS urgency.

---

## Claude's Discretion

- SQL query structure for 24-hour history (join sessions table vs. filter by timestamp directly)
- Whether to create `services/session_intelligence.py` or extend existing modules
- Whether HIST-03 needs a new endpoint or reuses existing `get_session_history()`

## Deferred Ideas

- Vector-embedding interest graph (v2 — already in REQUIREMENTS.md)
- Deep prerequisite tree rendering (2+ levels) — Phase 6 polish
- Per-turn interest extraction — latency concern ruled it out for v1
