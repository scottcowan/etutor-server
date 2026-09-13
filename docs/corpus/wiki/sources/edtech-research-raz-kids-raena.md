---
title: "Edtech Research: Raz-Kids / Learning A-Z and Raena.ai"
type: article
source_url: ""
author: "(internal research)"
captured: 2026-08-19
topic_ids: [reading_comprehension_ks1, reading_comprehension_ks2, phonics_and_sounds]
level: 200
prerequisite_topics: []
curation_note: ""
---

# Edtech Research: Raz-Kids / Learning A-Z and Raena.ai

**Researched:** 2026-08-19
**Purpose:** Evaluate content/pedagogy/integration opportunities for Phase 4.1 corpus and Phase 5 child interface.

---

## Raena.ai — Not What Was Intended

The product at raena.ai is a general-purpose AI study tool for university/secondary students (PDF/notes → flashcards, quizzes, podcasts). Founded 2024, Brisbane, ~1.4M users. **Not a children's reading product** — no relevance to etutor.

If a children's AI reading tutor was intended, the closest real products are:
- **Ello** — AI reading tutor ages 3–8, voice interaction, real-time feedback during oral reading
- **Amira Learning** — AI oral reading assessment for K-3, speech recognition generates running-record-equivalent data, used in US schools

Worth a follow-up research pass on Amira Learning specifically — its speech-recognition-driven running records model is closer to etutor's voice-first architecture than anything else surveyed.

---

## Raz-Kids / Learning A-Z

**No API. No content licensing path.** Private-equity-owned SaaS (~$120–130/teacher/year), fully proprietary content, no developer program.

### What's worth adopting (not IP — standard literacy assessment practice)

1. **29-level taxonomy: aa, a–z, Z1, Z2** — finer granularity than Lexile at the emergent-reader end (ages 5–7), which is where most etutor device users start.
2. **Running record accuracy thresholds:** ≥96% = independent, 90–95% = instructional, <90% = frustration. Standard, well-researched, freely usable.
3. **Pre/during/post reading scaffold:** vocabulary preview before text, comprehension prompts during, quiz after.
4. **Comprehension question taxonomy:** literal recall, inferential, vocabulary-in-context, author's purpose.

### What NOT to adopt

- Meaning-cueing / miscue analysis as primary method — conflicts with the "science of reading" consensus (phonics-first). etutor should prefer **decodability tagging** (phonics pattern sequencing: CVC → CCVC → digraphs → CVCe → vowel teams) over Fountas & Pinnell-style levelling for the 6–8 age band.
- Closed multiple-choice-only comprehension checks — etutor's Socratic model is already better pedagogy here.

### UX patterns adaptable to e-ink

- Chunked short paragraphs (not full-page text walls) — fits 300ms partial refresh constraint
- Word-highlighting for audio sync → bold current word instead of animated highlight on e-ink
- Page count progress ("Page 3 of 8") more motivating for young readers than percentage
- Quiz per 2–3 pages, not end-of-book only — spaced retrieval within a single text

---

## Open Content Sources for Phase 4.1 Corpus

Since Raz-Kids content is closed, these are the viable levelled-reading sources:

| Source | Licensing | Best for | Notes |
|--------|-----------|---------|-------|
| **ReadWorks** | Free (some CC) | Non-fiction + comprehension Qs, Grade 1–12 | Strongest starting point — comes with questions already |
| **StoryWeaver** | CC BY 4.0 | 200,000+ levelled children's stories, multi-language | Second strongest — huge volume, open license |
| **BookDash** | CC BY | High-quality illustrated picture books, Level 1–5 | Good for youngest band |
| **African Storybook** | CC BY | Level 1–7, phonics-aware levelling | |
| **CommonLit** | Some CC | Ages 5–12, Lexile-levelled | US-focused |
| **Project Gutenberg** | Public domain | Older texts, needs re-levelling | Not written for children — use for older/advanced band only |
| **Simple English Wikipedia** | CC BY-SA | Non-fiction, level n–z range | Needs chunking |
| **Newsela** | Freemium, gated API | News articles, 5 levels, ages 8–12 | API exists but gated — check terms |
| **OpenStax** | CC BY | Textbook-level | Too advanced for primary; useful for Z1–Z2 |

**Recommendation: ReadWorks + StoryWeaver as the primary Phase 4.1 corpus sources** — open licensing, sufficient volume, ReadWorks ships with comprehension questions matching the pre/during/post scaffold above.

---

## Confidence Notes

Raz-Kids specifics (level count, book count, pricing) are drawn from training knowledge, not live-verified — the domain blocked scraping during this research session. Directionally reliable but verify specific numbers (book count, current pricing) before citing externally. Raena.ai identity was live-verified via direct fetch and LinkedIn.
