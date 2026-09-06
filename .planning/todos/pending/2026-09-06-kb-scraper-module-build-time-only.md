---
created: 2026-09-06T11:51:38.960Z
title: Use kb-scraper for corpus sourcing at module-build time only (not runtime)
area: general
files:
  - docs/corpus/
  - services/corpus_mcp/
---

## Problem

Phase 4.1 built the corpus with manual curation only (D-09/D-18) and deliberately no auto-ingest pipeline. But `~/Projects/scottcowan/knowledgebase/` (a separate personal SWE knowledgebase) already has working fetch infrastructure — `kb-scraper` (shared repo, `KB_SCRAPER_HOME`), which does curl→pandoc → Jina Reader → headless browser fallback, with rate-limit detection and clean markdown output to `source/<domain>/<slug>.md`.

Rebuilding this for etutor's corpus would duplicate existing, working tooling.

## Solution

Confirmed design: content sourcing happens at **module-build time**, never at runtime. The tutor never fetches live web content mid-session — it only serves from the pre-built static corpus (Phase 5 SYNC-03 content packages).

Workflow when building a new training module for topic X:
1. Use `kb-scraper` (or a thin etutor-specific wrapper around it) to fetch/convert source material into `docs/corpus/source/<domain>/<slug>.md` — same L0/L1 convention as the `knowledgebase` repo
2. Author the L3 topic page in `docs/corpus/wiki/topics/` (AI-assisted, per existing D-08/D-09)
3. Phase 5's module-builder packages the topic page + experiments into a deterministic content package for the device

Do NOT adopt kb-scraper's cron-based auto-enrichment (feed monitoring, automatic L2/L3 promotion) — that conflicts with the locked "manually curated, not a living entity" decision (D-18 in Phase 4.1 CONTEXT.md). Only reuse the fetch/convert tooling, invoked manually per-module.

Relevant to: Phase 5 planning (module builder design) and any future corpus content-authoring session.
