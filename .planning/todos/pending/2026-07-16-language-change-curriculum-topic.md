---
created: 2026-07-16T00:37:34Z
title: Language change as a curriculum topic — how words shift meaning across eras
area: api
files:
  - services/tutor.py
  - services/curriculum.py
---

## Problem

Children reading older books will encounter words that have changed meaning. This
is currently treated as a guardrail problem (handle gracefully, don't alarm the
child). But it is also a rich curriculum opportunity that belongs in the English
curriculum as a topic in its own right.

"How do words change meaning?" is a KS2/KS3 English language topic that connects
to: etymology, cultural history, how language reflects society, critical reading,
and media literacy.

Examples the children will encounter in the corpus:
- "gay" (cheerful → LGBTQ+ identity marker)
- "queer" (strange → reclaimed identity term)
- "awful" (originally: awe-inspiring → terrible)
- "nice" (originally: foolish, precise → pleasant)
- "silly" (originally: blessed, then pitiable → foolish)
- "wicked" (bad → excellent in modern slang)
- "literally" (its own evolution in real time)
- "villain" (originally: farm worker, serf)

The Narnia and Tolkien passages in the corpus are good entry points — Lewis uses
"gay" and "queer" in their historical senses, which creates a natural teaching
moment when a child notices.

## Solution

Add curriculum topics to `services/curriculum.py` for:
- `english-language-change-semantic-shift` — how word meanings drift over time
- `english-etymology-word-origins` — where words come from
- `english-historical-language` — reading texts from different eras

Tag the existing book passages that contain shifted-meaning words to these topics,
so `next_topics()` can surface the language-change topic when a child is working
through older fiction.

System prompt addition for when these topics are in focus:
> When the child encounters a word that has changed meaning, use it as a teaching
> moment: ask them to guess the meaning from context first, then explain the
> historical usage, then discuss how and why meanings shift. This is vocabulary
> and critical reading at the same time.

## When to do this

Phase 3 (Session Intelligence) — when curriculum integration with session history
is built. The topic tags on passages are the data dependency.

Related: `2026-07-09-historical-language-explanation.md` (handles the guardrail
side), `2026-07-16-book-passage-content-review.md` (the passage review pass).
