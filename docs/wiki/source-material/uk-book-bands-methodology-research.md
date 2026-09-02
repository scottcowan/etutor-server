# UK Book Bands — Structural/Methodology Research (No Content Reuse)

**Researched:** 2026-08-19
**Purpose:** Extract the freely-adoptable *structure and pedagogy* of UK guided reading practice for Phase 4.1 corpus, without reusing any publisher's actual book text. Follow-up to `edtech-research-raz-kids-raena.md` and the Cambridge Reading Adventures evaluation in `docs/wanted-books.md`.

---

## 1. Full Book Bands Colour Scale — VERIFIED (Oxford Owl / OUP)

| Book Band | Oxford Reading Tree Level |
|---|---|
| Lilac | 1 |
| Pink | 1+ |
| Red | 2 |
| Yellow | 3 |
| Light Blue | 4 |
| Green | 5 |
| Orange | 6 |
| Turquoise | 7 |
| Purple | 8 |
| Gold | 9 |
| White | 10 |
| Lime | 11 |
| Lime+ | 12 |
| Brown | 8–14 (range) |
| Grey | 12–14 (range) |
| Dark Blue | 15–16 |
| Dark Red | 17–20 |

Cross-publisher UK standard (also used by Collins Big Cat, Cambridge Reading Adventures). Originates with the Institute of Education/CLPE Book Bands handbook (Bickler, Baker, Hobsbaum) — not independently re-verified this session, but Oxford Owl's rendering is a faithful, widely-cited restatement.

## 2. Book Band → NC Year Group — VERIFIED (Oxford Owl / OUP)

| Year Group | Age | Typical Bands |
|---|---|---|
| Nursery | up to 4 | Lilac |
| Reception | 4–5 | Lilac, Pink, Red, Yellow |
| Y1 | 5–6 | Light Blue, Green, Orange |
| Y2 | 6–7 | Turquoise, Purple, Gold, White, Lime, Lime+ |
| Y3 | 7–8 | Brown, Grey (start) |
| Y4 | 8–9 | Grey, Dark Blue |
| Y5 | 9–10 | Dark Blue, Dark Red |
| Y6 | 10–11 | Dark Red |

**Important:** bands are proficiency guidelines, never age locks. This is standard UK practice and matches etutor's own "no ceiling" core value — a child reading above or below their year group's typical band range is expected, not corrected.

## 3. Cross-System Correlation (F&P / Reading Recovery / Lexile) — UNVERIFIED, DO NOT LOCK

Reconstructed table exists (see agent transcript) but could not be live-verified this session — publishers disagree on crosswalks, and early-level Lexile correspondence is especially unreliable. **Do not hardcode this into any spec.** If a precise crosswalk is ever needed, re-run research with live web search, or better: calibrate empirically against etutor's own corpus once populated.

## 4. Running Records Methodology — VERIFIED (mechanism), thresholds UNCONFIRMED

Running records are a genuine, non-proprietary assessment technique (Marie Clay / Reading Recovery origin): an adult marks errors/self-corrections while a child reads aloud, then calculates percentage accuracy.

Three-tier model (confirmed as real, cross-publisher practice):
- **Independent/Easy** — high accuracy, fluent without support
- **Instructional** — the "teaching zone," target for guided reading
- **Frustration/Hard** — text too difficult for instruction

Exact percentage cutoffs vary by source (90/95/96 rounding differs) — do not hardcode a specific number without further verification.

**Self-correction rate** is a standard companion metric — a child who self-corrects often is monitoring their own reading well even at lower raw accuracy. Worth considering as a secondary mastery signal if etutor ever builds oral reading assessment (Phase 5/6).

## 5. Comprehension Question Taxonomy — VERIFIED against DfE KS2 framework

Four categories, matching the National Curriculum's own KS2 reading test content domains (not a publisher's invention):
- **Literal** (retrieval) — "What did the character do?"
- **Inferential** — "Why do you think she felt that way?"
- **Vocabulary-in-context** — "What does 'reluctant' mean here?"
- **Prediction** — "What do you think happens next?"

Because this is the DfE's own framework, it aligns with etutor's NC-first design better than importing a different taxonomy.

## 6. Guided Reading Session Structure — VERIFIED as standard UK practice

Three phases:
- **Before:** activate prior knowledge, "book talk" (cover/title prediction, picture walk), preview 1–2 new vocabulary words in context
- **During:** child reads; adult uses hint-ladder cueing ("What can you try? Does that look right? Does that make sense?") rather than supplying the word
- **After:** comprehension discussion using the four-category taxonomy above, plus fluency/expression check

**Notable alignment:** the "during" phase hint-ladder cueing is functionally identical to etutor's existing Socratic hint-ladder philosophy (see project CLAUDE.md). No new tutor behaviour needed — this validates the existing approach rather than requiring a new one.

"Book talk" sentence starters (generic, non-proprietary, traceable to reciprocal-reading frameworks): "I think this book will be about... because...", "This reminds me of...", "I wonder why the character...", "If I were the character I would..."

## 7. Band-Pack Sizing / Fiction:Non-Fiction Ratio — UNVERIFIED, DO NOT LOCK

Reconstructed estimates (~6 titles/band, ~60:40 or 70:30 fiction:non-fiction) could not be verified against any live publisher source. Do not treat as a target — size etutor's own content packages empirically based on what's actually available from open sources (ReadWorks, StoryWeaver, BookDash, African Storybook), not a borrowed ratio.

## 8. Early-Band Phonics/Decodability Mapping — DIRECTIONALLY SOLID, DETAILS UNVERIFIED

Early bands (Lilac through Green/Orange, roughly Reception–Y1) are decodability-mapped to phonics progression in commercial schemes (Letters and Sounds Phase 2–5). The general direction (early bands = decodable, later bands = free/vocabulary-driven) is solid; exact phase-to-band alignment is not verified and shouldn't be copied precisely — informs etutor's own `decodability_tags` design (see Phase 4.1 CONTEXT.md D-17) without importing a specific publisher's phase numbering.

---

## What This Means for Phase 4.1 (Decisions D-16 through D-21)

See `.planning/phases/04.1-knowledge-corpus-and-mcp-server/04.1-CONTEXT.md` — this research produced:
- **D-16 / D-16a:** Book Bands scale + NC year mapping as `reading_level` schema (locked, verified)
- **D-16b:** DfE four-category question taxonomy for comprehension prompts (locked, verified)
- **D-16c:** Before/during/after session structure for future read-along mode, noting existing alignment with etutor's hint-ladder philosophy (locked as design reference, Phase 5+ feature)
- **D-16d:** Running records model as directional reference, exact thresholds explicitly NOT locked
- **D-21:** Band-pack sizing explicitly NOT locked to any borrowed ratio — corpus sized empirically
