---
created: 2026-07-16T00:37:34Z
title: Review book-passages corpus for anachronistic language before tutor use
area: api
files:
  - docs/book-passages/children-series.json
  - docs/book-passages/children-fiction-and-philosophy.json
  - docs/book-passages/science.json
---

## Problem

The 53 passages in `docs/book-passages/` were extracted directly from EPUBs and
have not been reviewed for language that is harmless in historical context but
confusing or alarming to a 6-12 year old.

Known categories of concern in the current corpus:

**Meaning-shifted words** (British English, historical):
- "gay" = cheerful (Wind in the Willows era, Narnia, Tolkien)
- "queer" = strange (Lewis, Le Guin era)
- "fag"/"faggot" = cigarette/bundle of sticks (appears in older British text)
- "ejaculated" as speech attribution (common in Victorian/Edwardian prose)
- "niggardly" (unrelated etymology but visually jarring)

**Casual ableism in Dahl** (confirmed in corpus):
- "idiot", "imbecile", "moron" used as casual character insults in BFG, Witches

**Gendered assumptions** (Tolkien, Lewis):
- Male default, passive female characters worth noting if the child asks

## Solution

Add two fields to every passage object in the JSON schema:

```json
{
  "content_warning": null,
  "language_notes": [
    {
      "word": "fag",
      "context": "British English for cigarette",
      "tutor_response": "In this book, 'fag' means cigarette — it's old British slang."
    }
  ]
}
```

Then do a pass over all 53 passages and:
1. Flag any passage containing problematic language in `content_warning`
2. Add inline `language_notes` for specific words
3. For ages 6-9 passages: provide a `modernised_text` alternative where the
   word is swapped silently (e.g. "fag" → "cigarette")
4. For ages 10-12 passages: keep original, add language_note

When the tutor pulls a passage, it checks the child's age:
- age < 10: serve `modernised_text` if present, else original
- age >= 10: serve original, inject language_notes into system prompt

## When to do this

Before Phase 3 (Session Intelligence) wires the passages into the tutor system
prompt. The passages should not be injected into prompts without this review.

This is a one-time manual + automated scan — probably 2-3 hours of work.
