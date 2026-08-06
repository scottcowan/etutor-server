---
created: 2026-07-29T00:00:00.000Z
title: Wiki for retaining raw course source material
area: ui
files:
  - docs/wiki/source-material/
  - api/parent.py
  - services/curriculum.py
---

## Problem

Raw source material (video essays, books, articles, experiments, films) that could become curriculum topics or tutor reference material is being discussed and then lost. There's no place to store it in a way that:
1. Is browsable by educators/parents
2. Stays linked to the curriculum topics it relates to
3. Preserves the original transcript/content alongside curriculum tagging

Currently dumping things into `docs/wiki/source-material/` as markdown files — but there's no UI or API to browse, search, or link this material to topics.

## Solution

A lightweight wiki/resource library at `/parent/resources` (parent-gated) or a separate admin interface.

Each resource entry has:
- Title, source, date captured
- Raw content (transcript, summary, or link)
- Curriculum topic tags (linking to `services/curriculum.py` topic IDs)
- Suggested level band (100/200/300/400)
- Type: video / book / article / experiment / film

Minimum viable: a DB table (`ResourceModel`) + CRUD + a read-only page at `/parent/resources` listing resources with their topic tags. Educator can browse and see "what source material supports the Manipulation 300-level topics."

Longer term: ingest pipeline — paste a YouTube URL or local video path, auto-transcribe with Whisper, auto-tag to curriculum topics via keyword matching, store in DB.

For now: raw markdown files in `docs/wiki/source-material/` are the interim store. First item: `happiness-in-slavery-markradulich.md`.
