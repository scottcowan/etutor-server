---
created: 2026-07-13T11:29:38
title: Buddy avatar that grows with the child and reflects topics covered
area: ui
files:
  - services/profiles.py
  - services/curriculum.py
  - web/child/templates/chat.html
---

## Problem

The e-ink device needs a persistent companion character that:
1. Gives the child continuity and emotional connection across sessions
2. Visibly grows/evolves as the child learns — reflecting mastery and breadth
3. Shows traits from the topics they've actually covered — not generic

Without this, each session is stateless from the child's perspective. A child
returning to the device should see their buddy and know "that's mine, we've
been on adventures together."

## Design Concept

**The Buddy** is a creature/character that starts as a small simple form and
evolves over time. It has:

- **Visual evolution** — starts as a seed/egg/simple blob, grows features and
  complexity as topics are mastered. More topics = more elaborate appearance.

- **Topic traits** — the buddy's appearance and behaviour reflects what the
  child has studied:
  - Covered astronomy topics → buddy has star patterns or telescope accessory
  - Strong in history → medieval/Roman costume elements
  - Music topics → musical instrument it carries
  - Science topics → lab coat detail or periodic table markings
  - Cooking/vocational → chef's hat or tool belt

- **Mastery signal** — the buddy's confidence/posture reflects mastery state:
  - New topics = curious, tentative
  - In-progress = engaged, active
  - Solid mastery = confident, shows that knowledge off

- **Emotional continuity** — the buddy remembers the last session:
  "Last time we were exploring volcanoes — want to keep going?"

## Technical Approach

### Avatar representation
Rather than a single image, the buddy is **compositional** — a base form plus
a set of trait badges/accessories stored as a list in the child's profile.

```python
# In ChildProfile:
buddy_name: str = "Pip"  # child names their buddy
buddy_traits: list[str] = []  # e.g. ["astronomy", "history_medieval", "cooking"]
buddy_level: int = 0  # 0=egg, 1=hatchling, 2=juvenile, 3=companion, 4=sage
```

Buddy level could be derived from:
- Number of solid-mastery KCs: 0=0, 1=5+, 2=20+, 3=50+, 4=100+

### E-ink rendering
On e-ink (no animation, no colour): the buddy is a simple line-drawn character
described in SVG or generated as ASCII art. Each trait adds a small visual element.

For the web/browser interface: could use a simple sprite sheet with composited
layers, or a CSS-drawn character with trait badges.

### System prompt integration
The buddy's current state is mentioned in the system prompt:
"The child's buddy [name] has traits reflecting their knowledge of [areas].
Reference the buddy naturally — it's their companion, not just a tool."

The tutor can involve the buddy:
"What do you think [buddy name] would say about this?"
"[Buddy] seems excited — they love astronomy, and we're about to talk about
black holes."

### Child-facing features
- Child names their buddy in the first session
- Buddy visually updates after each session (new trait or growth)
- Parent dashboard shows buddy evolution timeline
- Buddy can be "asked" things as a way to probe recall:
  "Ask [buddy] what they remember about the water cycle"
  (Child then explains it, consolidating retrieval practice)

## Research backing
- Character continuity (Kodi the bear in Khan Academy Kids) — emotional
  connection without manipulation (see pedagogy.md Khan Academy analysis)
- Self-reference effect: associating learning with a personal companion
  increases encoding (pedagogy-montessori.md §5 — self-reference framing)
- The buddy as "explain-back" target gives a natural low-stakes audience
  for retrieval practice (pedagogy.md §2 — retrieval practice)

## Open questions
- Does the buddy speak? (Could be voiced by Piper/Kokoro — consistent voice)
- Is the buddy a separate AI agent or a persona within the same prompt?
- How do siblings' buddies differ? (Both boys need distinct buddies)
- Does the buddy have a fixed species (dragon, robot, creature) or is it
  abstract and child-defined?
- Can the buddy "visit" topics the child hasn't covered yet and come back
  curious? ("I was reading about the Romans while you were at school...")
