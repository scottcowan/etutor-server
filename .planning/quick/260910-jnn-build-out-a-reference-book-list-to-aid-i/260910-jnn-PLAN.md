---
phase: quick
plan: 01
type: execute
wave: 1
depends_on: []
files_modified: [docs/wanted-books.md]
autonomous: true
requirements: ["N/A — quick task, content/documentation only, no ROADMAP requirement ID"]

must_haves:
  truths:
    - "docs/wanted-books.md contains a new top-level section aimed specifically at Phase 4.1+ corpus authoring (not Calibre-Web library seeding)"
    - "The new section covers the subjects from services/curriculum.py with the thinnest existing coverage in wanted-books.md, excluding Manipulation (already has pilot corpus content) and excluding subjects that already have dedicated sections (History, Science, Geography, World Economies, Sociology, Religion, Psychology, Computer Science, Engineering, Mathematics, Music, English/Shakespeare/Poetry/Drama, Cultural Capital, Dissent, Surveillance, Art/Comics, Health/PE/Sports Medicine)"
    - "Each recommended book lists title, author, why it's a good corpus source (specific topic_ids or topic themes it supports), and a target level band (100-400) or age/reading-level note"
    - "Books are organised by subject cluster matching services/curriculum.py subject names"
  artifacts:
    - path: "docs/wanted-books.md"
      provides: "New section(s) covering corpus source material for thin-coverage subjects"
      contains: "## Reference Books for Corpus Authoring"
  key_links:
    - from: "docs/wanted-books.md new section"
      to: "services/curriculum.py subjects()"
      via: "subject cluster headings matching subject names exactly"
      pattern: "Vocational|Political Systems|Growing Up|How Things Are Made|Aerospace|Grand Narrative|Social Intelligence|Corruption"
---

<objective>
Extend `docs/wanted-books.md` with a new section of reference book recommendations
specifically for authoring Phase 4.1+ corpus topic pages (`docs/corpus/wiki/topics/`),
prioritising the `services/curriculum.py` subjects with the thinnest existing source
material coverage in the file today.

Purpose: The corpus currently has real content for only the Manipulation subject
(21 topics, Phase 4.1 pilot). `docs/wanted-books.md` already has deep coverage for
History, Science, Geography, World Economies, Sociology, Religion, Psychology,
Computer Science, Engineering, Mathematics, Music, English/Shakespeare/Poetry/Drama,
Cultural Capital, Dissent, Surveillance, Art/Comics, and Health/PE/Sports Medicine —
but zero coverage for several large subjects. This task closes that gap so future
corpus-authoring sessions have a starting reading list instead of a blank page.

Output: A new `## Reference Books for Corpus Authoring — Priority Subjects (Phase 4.1+)`
top-level section appended to `docs/wanted-books.md`, organised into subject-cluster
subsections, each with book entries (title, author, why-it's-a-good-source, level/age).
No code changes — this is a documentation-only task.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/STATE.md
@docs/corpus/wiki/index.md
@.planning/phases/04.1-knowledge-corpus-and-mcp-server/04.1-CONTEXT.md

docs/wanted-books.md already exists with these top-level sections (confirmed via
`grep -n "^## " docs/wanted-books.md`): Core History Reference, Connections and How
the World Works, British Empire, History for Children, Children's Fiction, Older
Texts and Primary Sources, Art/Visual Language/Comics, Cultural Capital and Class,
Dissent and Authority, Surveillance/Privacy, Science Reference (Kavita + Calibre-Web),
Health/PE/Wellbeing (Kavita + Calibre-Web), Geography (Kavita + Calibre-Web), World
Economies (Kavita + Calibre-Web), Sociology and Anthropology, World Religions,
Philosophy (Kavita + Calibre-Web), Psychology, Computer Science and Programming,
Electronics and Engineering, Mathematics, Technology History and Culture, Making and
Physical Computing, Coding/Tech Biographies/How Computers Work/Robotics for Children,
Comics and Graphic Novels, English Literature/Shakespeare/Poetry/Linguistics/Drama,
Music Theory and History, Classic Children's Literature, Poetry/Picture
Books/Plays/Music Books for Children, Mythology and Folklore, Levelled Reading Schemes.

`services/curriculum.py subjects()` returns 44 subjects with these topic counts
(from a live query, confirms which subjects have NO existing wanted-books.md section):

Vocational 92, Science 46, Music 46, Religion 45, History 40, How Things Are Made 37,
Aerospace 33, Maths 33, Materials 30, Growing Up 29, Political Systems 29, Sports
Medicine 29, Social Intelligence 27, Manipulation 21 (has pilot corpus — EXCLUDE),
Film 20, Geography 22, Optics 22, Critical Thinking 20, Sport 20, Grand Narrative 19,
English 19, Cultural Capital 16 (has section), Vocabulary 16, Computing 15, Medicine
14, World Economies 13 (has section), Computer Science 13, Surveillance 12 (has
section), Psychology 12 (has section), Engineering 12 (has section), Connections 12
(has section), Social Patterns 12, Corruption 11, Dissent 10 (has section), Art 10
(has section), Architecture 10, Performing Arts 10, Sociology 10 (has section),
Linguistics 9 (has section), PPE 7, Law 5, PSHE 4, Experiment 52 (separate
`wiki/experiments/` content type per D-02, not a topic-page subject).

Cross-referencing subject list against existing sections identifies subjects with
ZERO dedicated coverage today, ranked by topic count: **Vocational (92, by far the
largest gap), Political Systems (29), Growing Up (29), How Things Are Made (37,
only touched tangentially inside the Connections section), Aerospace (33), Social
Intelligence (27), Grand Narrative (19), Film (20), Optics (22, touched tangentially
inside AQA Physics A-Level entry), Corruption (11), Architecture (10), Performing
Arts (10), Social Patterns (12), Vocabulary (16), Law (5), PPE (7), PSHE (4)**.

Per D-18 in 04.1-CONTEXT.md, corpus is manually curated and sourced at module-build
time (not scraped ahead of time) — this book list is reading/reference material to
ground topic-page authoring, following the same "Reference (Kavita)" /
"for Children (Calibre-Web)" pattern already used throughout wanted-books.md for
other subjects.
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add corpus-authoring book list for the 4 largest thin-coverage subjects</name>
  <files>docs/wanted-books.md</files>
  <action>
    Append a new top-level section `## Reference Books for Corpus Authoring — Priority
    Subjects (Phase 4.1+)` to the end of docs/wanted-books.md (after the existing
    `## Missing from Library` section, or before it if that section is meant to stay
    last — check the tail of the file and place this new section immediately before
    any trailing "Missing from Library" / changelog-style section so the book list
    reads as primary content).

    Open with 2-3 sentences of framing: this section targets `docs/corpus/wiki/topics/`
    authoring per the Phase 4.1 corpus (see .planning/phases/04.1-knowledge-corpus-and-mcp-server/04.1-CONTEXT.md),
    prioritising subjects from services/curriculum.py with no existing coverage above,
    following the same Kavita (reference/lesson-source, no age ceiling) / Calibre-Web
    (child-facing, age-gated) split used elsewhere in this file.

    Add four subject-cluster subsections (use `### Vocational — Reference (Kavita)`
    style headings matching the existing file's convention exactly), each with 4-6
    book entries in the file's established format (bold title/author/publisher/year,
    italic one-line description, `*Use for:*` line naming specific topic_id-style
    themes, `**Age suitability**` or `**Library:**`/`**Age group:**` line):

    1. **Vocational (92 topics — largest gap in the file).** This subject spans trades,
       careers, and applied skills. Recommend books covering: apprenticeship/trades
       history, career exploration for children (e.g. "Dream Jobs" / "What Do People
       Do All Day?" — Richard Scarry style), a general vocational-skills reference
       (e.g. a trades encyclopedia), and at least one Kavita-tier reference on
       vocational education theory/history (e.g. work on the history of apprenticeship
       or vocational pedagogy).
    2. **Political Systems (29 topics, no dedicated section — Dissent/Surveillance
       sections exist but don't cover systems of government themselves).** Recommend:
       a comparative government/political-systems textbook (Kavita reference), a
       children's introduction to how government works (e.g. DK "Government and
       Politics" style), and one narrative/historical account of a specific political
       system transition (democracy, monarchy, communism, etc.) suitable for the
       11-13 band.
    3. **Growing Up (29 topics — likely puberty, identity, independence, emotional
       development for a children's tutor).** Recommend age-appropriate, non-clinical
       reference books on child development and growing up (e.g. well-regarded puberty
       education books for the relevant age bands), plus one Kavita-tier developmental
       psychology reference if distinct from the existing Psychology section's scope.
    4. **How Things Are Made (37 topics — currently only touched tangentially via
       The Way Things Work in the Connections section).** Recommend a dedicated
       manufacturing/how-it's-made reference for children (e.g. "How It's Made"
       companion books, DK "Machines and How They Work"), and one Kavita-tier
       industrial-processes/engineering-manufacturing reference for deeper topic pages.

    Follow the exact formatting conventions already used in the file (read the
    existing "Science Reference — Kavita" and "Science for Children — Calibre-Web"
    sections as the format template before writing — do not invent a new format).
    Every entry must name specific curriculum-relevant themes in a `*Use for:*` line
    even if exact topic_ids in services/curriculum.py aren't known — describe the
    theme in plain language matching how the subject would be tutored.
  </action>
  <verify>
    <automated>grep -c "^### " docs/wanted-books.md | awk '{ if ($1 >= 4) exit 0; else exit 1 }'</automated>
  </verify>
  <done>
    docs/wanted-books.md contains a new `## Reference Books for Corpus Authoring —
    Priority Subjects (Phase 4.1+)` section with four subject-cluster subsections
    (Vocational, Political Systems, Growing Up, How Things Are Made), each with
    4-6 book entries in the file's established format.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add corpus-authoring book list for the remaining thin-coverage subjects</name>
  <files>docs/wanted-books.md</files>
  <action>
    Continue the section added in Task 1 (same `## Reference Books for Corpus
    Authoring` top-level section) with subject-cluster subsections for the remaining
    thin-coverage subjects, grouping the smallest subjects into combined clusters to
    keep the list proportionate to topic count:

    1. **Aerospace (33 topics — standalone cluster).** Recommend a flight/aerospace
       reference for children (e.g. DK Eyewitness Flight, aviation history), a
       Kavita-tier aerodynamics/aerospace-engineering reference for deeper topic
       pages, and one narrative book on a specific aerospace milestone (Wright
       Brothers, Apollo program, jet engine invention) with strong Socratic-question
       potential.
    2. **Social Intelligence (27 topics) + Social Patterns (12 topics) — combined
       cluster** (related themes: reading social cues, group dynamics, social norms).
       Recommend a children's social-skills reference, one Kavita-tier social
       psychology / group dynamics reference, and one narrative book illustrating
       social dynamics for the 9-13 age band.
    3. **Grand Narrative (19 topics) + Optics (22 topics) — combined cluster of
       otherwise-unrelated small gaps** (list under two separate `###` subheadings
       within this bullet's cluster, not merged into one book list): for Grand
       Narrative, recommend a "big history"/universal-history style reference (e.g.
       David Christian's "Origin Story" or "Big History" school-edition materials);
       for Optics, recommend a dedicated light/optics reference for children (e.g.
       DK Eyewitness Light) plus one Kavita-tier optics/photonics reference beyond
       what the existing AQA Physics entry covers.
    4. **Film (20 topics) + Performing Arts (10 topics) — combined cluster.**
       Recommend a film-history/film-literacy reference for children, a Kavita-tier
       film theory/history reference, and a performing-arts (theatre/dance) reference
       for children.
    5. **Corruption (11) + Law (5) + Architecture (10) + Vocabulary (16) + PPE (7)
       + PSHE (4) — smallest-gap catch-all cluster.** For each of these six subjects,
       add one focused book recommendation each (not a full multi-book treatment,
       given their smaller topic counts) rather than a full subsection — a short
       `### Smaller Gaps — One Book Each` subsection with a compact table: subject |
       book | author | why it's a good source | level/age. Prioritise books that
       are genuinely strong single-source references over padding the list.

    Follow the same formatting conventions established in Task 1 and the rest of the
    file. End the whole new top-level section with a one-paragraph note stating which
    subjects were deliberately excluded and why (Manipulation — has pilot corpus
    content; History/Science/Geography/etc. — already have dedicated sections above;
    Experiment — separate `wiki/experiments/` content type per 04.1-CONTEXT.md D-02,
    not a topic-page subject).
  </action>
  <verify>
    <automated>grep -c "^### " docs/wanted-books.md | awk '{ if ($1 >= 10) exit 0; else exit 1 }'</automated>
  </verify>
  <done>
    docs/wanted-books.md's new corpus-authoring section now covers Aerospace, Social
    Intelligence, Social Patterns, Grand Narrative, Optics, Film, Performing Arts,
    Corruption, Law, Architecture, Vocabulary, PPE, and PSHE, plus a closing note
    explaining excluded subjects. Combined with Task 1, all 13-17 thin-coverage
    subjects identified in the audit are addressed.
  </done>
</task>

</tasks>

<verification>
Run `grep -n "^## Reference Books for Corpus Authoring" docs/wanted-books.md` to
confirm the section exists exactly once. Run `grep -n "^### " docs/wanted-books.md`
and manually confirm subject-cluster subsections cover: Vocational, Political
Systems, Growing Up, How Things Are Made, Aerospace, Social Intelligence/Social
Patterns, Grand Narrative, Optics, Film, Performing Arts, and the smaller-gaps
catch-all (Corruption, Law, Architecture, Vocabulary, PPE, PSHE).
</verification>

<success_criteria>
- New section exists in docs/wanted-books.md dedicated to Phase 4.1+ corpus authoring
- All subjects with zero existing coverage in the file (per the subject audit in
  <context>) are addressed, excluding Manipulation (has pilot content) and subjects
  scoped to `wiki/experiments/` rather than topic pages
- Every book entry names specific topics/themes it supports and a level band or age
- No code files modified — documentation only
</success_criteria>

<output>
No SUMMARY.md required for quick tasks — this plan's completion is verified by the
<verify> commands and the updated docs/wanted-books.md file itself.
</output>
