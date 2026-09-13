---
created: 2026-07-20T16:42:41.023Z
title: Parents should be able to skip topics
area: ui
files:
  - services/curriculum.py
  - api/parent.py
  - web/parent/templates/child_profile.html
---

## Problem

The mastery map accordion shows all curriculum topics, but parents currently have no way to exclude topics they don't want surfaced for their child — e.g. topics that are religiously sensitive, developmentally inappropriate for their specific child, or simply not relevant to their family's context.

Without topic-skipping, the tutor may keep surfacing topics the parent has actively decided against, and `next_topics()` will keep recommending them regardless.

## Solution

Add a `skipped_topics: list[str]` field to `ChildProfileModel` (JSON column, same pattern as `interests`). 

In the mastery map (`/parent/children/{child_id}`), add a "Skip" button or toggle next to each topic row. A skipped topic shows with a strikethrough or muted style and a "Restore" button.

`next_topics()` in `services/knowledge_tracing.py` should filter out skipped topics from recommendations. `build_system_prompt()` should note skipped topics so the tutor doesn't initiate them.

Phase 4 or 5 is the right time to implement — profile editor already exists, mastery map UI is live.
