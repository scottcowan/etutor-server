---
created: 2026-07-15T12:49:51Z
title: E-ink illustration library — etched/engraved line art tagged to curriculum topics
area: ui
files: []
---

## Problem

The Primer's core mechanic — "zoom into a carrot root hair and see the mitochondria", "look at Saturn's rings from 800 million miles away" — requires a visual layer tied to curriculum topics. etutor currently has no illustration system. The device is e-ink; all visuals must be high-contrast line art (no photos, no greyscale gradients).

The correct aesthetic is woodcut / pseudo-engraved / pen-and-ink line art — exactly what Hackworth used ("pseudo-engraved style"). This renders crisply on e-ink, is the native aesthetic of scientific and natural history illustration, and is almost entirely available as public domain material.

**Scope**: e-ink hardware only. The browser prototype can display the same SVGs but the design constraint is e-ink-first: black line art, no fills, no gradients, crisp at 300dpi e-ink.

## Solution

**Format**: SVG with stroke (not fill). Scales to any display DPI. Tiny file size. Renders as crisp black lines on e-ink.

**Style constraint**: woodcut / etching / Victorian engraving style — fine lines, hatching, no smooth gradients. Think Audubon, Dürer, Haeckel, Vesalius anatomy plates.

**Sources (all public domain)**:
- Biodiversity Heritage Library (natural history: animals, plants, geology)
- Wellcome Collection (anatomy, medicine, microscopy)
- British Library digitised collections (history, geography, maps)
- NASA/ESA image archive (astronomy — convert photos to high-contrast line tracings)

**For topics without a period illustration** (e.g. "how a CPU works", circuit logic, maths concepts):
- Use diagrammatic line art: circuit diagrams, cross-sections, flow charts, geometric constructions
- These are already e-ink-native — they're naturally high-contrast line art

**Integration**:
- Add `has_illustration: bool` and `illustration_path: str | None` to the `Topic` dataclass in `services/curriculum.py`
- Store illustrations in `assets/illustrations/{topic_id}.svg`
- When a topic is active and `has_illustration=True`, the tutor can reference it: "let me show you what this looks like"
- The API returns `illustration_url` alongside the tutor response — the device renders it

**Prioritise**:
1. Natural sciences (biology cells, anatomy, geology, astronomy) — best coverage from period sources
2. Geography (maps, topography)
3. History (period illustration, architecture)
4. Mathematics (geometric constructions, diagrams)
5. Computer science (circuit diagrams, Turing machine tape, logic gate diagrams)

**Voice carries the scale narrative** — the illustration is the anchor, not the entire experience. "And if we went even smaller than that root hair, we'd find..." is TTS. The image gives the child something to look at while they listen.
