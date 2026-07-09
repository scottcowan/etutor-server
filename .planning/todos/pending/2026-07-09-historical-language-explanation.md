---
created: 2026-07-09T21:10:00
title: Explain historical and offensive language encountered in old books
area: api
files:
  - services/tutor.py
  - docs/pedagogy.md
  - docs/wanted-books.md
---

## Problem

Classic children's books contain language that is offensive by modern standards or
has changed meaning entirely. A child reading these books will encounter words they
don't understand or that feel wrong. The tutor must handle these moments well —
neither ignoring the word, nor over-reacting, nor leaving the child confused.

Categories of problem language in the reading list:

**Words that have changed meaning:**
- "gay" — means happy/bright in Victorian/Edwardian text (Wind in the Willows,
  Treasure Island, etc.). A child may be confused or giggle. Needs a calm,
  matter-of-fact explanation: "In this book, gay just means cheerful. The word
  has a different meaning today."
- "queer" — means strange/odd in older text (The Secret Garden, many others).
  Same situation.
- "faggot" — means a bundle of sticks in British English; appears in historical
  texts and some regional usage. Needs explanation without drama.

**Ableist insults used casually in older books:**
- "idiot", "imbecile", "moron", "cretin" — originally clinical terms, now insults.
  Roald Dahl uses them freely (Charlie and the Chocolate Factory, James and the
  Giant Peach). A child from a family with a disabled member may find these
  upsetting.
- "stupid", "dumb" — less charged but still worth noting when used as casual
  cruelty in a text.
- "mad", "lunatic", "insane" — casual in older texts; stigmatising for children
  with mental health in the family.

**Racial language:**
- Some older books (pre-1970s editions) contain racial slurs or caricatures.
  The reading list has been curated to avoid the worst offenders, but context
  notes are needed for The Jungle Book (Kipling's imperial assumptions) and
  for any book set in the American South (Roll of Thunder, To Kill a Mockingbird).

**Gendered assumptions:**
- Older books assume male default, passive female characters. Worth noting when
  a child notices the pattern rather than steering around it.

## Solution

**Per-book context notes in the curriculum/books metadata:**
- Add a `language_notes` field to the book record (Calibre-Web metadata or a
  local JSON/YAML file)
- Each note flags: specific words to watch for, their historical meaning, and
  a suggested tutor response
- Example entry:
  ```yaml
  book: "The Wind in the Willows"
  language_notes:
    - word: "gay"
      context: "Used to mean cheerful or bright. Pages 3, 17, 44."
      tutor_response: "In this book, gay just means happy and bright. The word
        has a different meaning now, but Kenneth Grahame wrote this in 1908."
  ```

**Tutor behaviour when a child asks about a flagged word:**
1. Don't hesitate or deflect — explain directly
2. Give the historical meaning first, then note how usage has changed
3. Don't editoralise about whether the old usage was "wrong"
4. For slurs used as insults in older texts: name that it's unkind, note that
   people don't use it that way now, move on without dwelling
5. Never refuse to explain — a child asking "what does faggot mean?" deserves
   an honest answer matched to their age

**Age-calibrated explanations:**
- Ages 6–8: "That word means something different here — it means [X]."
- Ages 9–11: "In [year/era], people used that word to mean [X]. It has a
  different meaning today, and some people find the old usage hurtful."
- Ages 12+: Full historical context including why language changes and what
  that tells us about the society that used it

**System prompt addition:**
Add to the tutor system prompt a section on historical language:
"If a child asks about a word that appears in an old book and seems offensive
or confusing, explain its historical meaning calmly and factually. Do not
refuse, do not over-react, do not lecture. Match the explanation to the
child's age. If the word is a slur by modern standards, say so simply and
move on."

**Parent dashboard flag:**
- Log when the tutor explains historical language so parents can follow up
- Parent can mark topics as "handled" or flag for further conversation
- Particularly important for racial language — some parents will want to have
  that conversation themselves first
