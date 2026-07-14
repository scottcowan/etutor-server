---
created: 2026-07-14T20:59:31Z
title: Web-first UI that replicates e-ink experience
area: ui
files: []
---

## Problem

The e-ink device is the eventual target but the browser is the first iteration. The child web interface (Phase 5, `/child`) risks being designed as a fully interactive web app when it should look and feel like an e-ink device — minimal animation, high-contrast, low-refresh, voice-first.

## Solution

When designing the child web interface, constrain it to the e-ink aesthetic:
- No animations or transitions (300ms+ refresh minimum on real hardware)
- No drag-and-drop
- High contrast, large text, minimal chrome
- Voice-first — microphone is primary input, tap/click secondary
- Simulate e-ink partial refresh in CSS (optional: brief grey flash on content update)
- Not "not overly interactive" — simple state transitions only (waiting → listening → responding)

The web UI should be a faithful enough replica that testing on browser gives confidence it will work on hardware. Design decisions made for web should be compatible with the e-ink constraints.
