---
created: 2026-07-15T11:06:37Z
title: Strong guardrails to prevent inappropriate content reaching the learner
area: api
files: []
---

## Problem

The etutor serves children aged 6–12 via a voice-first interface. There are currently no content guardrails beyond the system prompt's Socratic framing. A child could ask about anything, and the LLM could respond with age-inappropriate content (violence, sexual content, extremist material, adult topics). The code review for Phase 1 flagged CORS wildcard + no auth (CR-05), but content filtering is a separate and deeper concern.

Known gaps:
- No input filtering on child speech (before LLM call)
- No output filtering on LLM response (before TTS)
- No per-message safety classification
- Phase 6 tracks multi-turn safety monitoring, but per-message filtering is not scoped

COPPA compliance requires minimising exposure of harmful content to under-13s. SAFETY-01 (multi-turn safety) and SAFETY-02 (child age injection) are Phase 6 requirements but per-turn content guardrails should be considered earlier.

## Solution

When this is planned (Phase 6 or earlier):
- Input guardrail: classify or filter child speech before sending to LLM (detect if the question is attempting to elicit harmful content)
- Output guardrail: run LLM response through a content filter before TTS playback (block/replace responses that contain inappropriate material)
- Consider Claude's built-in safety vs. an additional classifier layer
- Evaluate SafeTutors benchmark coverage (already referenced in ROADMAP Phase 6)
- Consider foot-in-the-door attack patterns (94% success rate on frontier models — ROADMAP Phase 6)
- Age injection into every prompt (SAFETY-02) is the cheapest quick win
