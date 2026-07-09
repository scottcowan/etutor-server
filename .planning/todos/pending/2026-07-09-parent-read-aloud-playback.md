---
created: 2026-07-09T21:05:12
title: Parent read-aloud recording played back on child's device
area: api
files:
  - services/profiles.py
  - api/sessions.py
  - docs/wanted-books.md
---

## Problem

Parents want to read books to their children but can't always be present. The
idea is to record a parent reading aloud and have that audio played back on the
child's e-ink device as the read-along narration — instead of (or alongside)
the Piper TTS voice.

This personalises the experience significantly: the child hears their own parent's
voice. Research supports that familiar voices aid comprehension and emotional
engagement (see `docs/research.md` §7.3 — CDS prosodic contour is what current
TTS can't replicate; a parent's voice is the real thing).

## Solution

**Recording side (parent app/dashboard):**
- Parent opens a book in Calibre-Web, gets a page-by-page recording interface
- Records each page/passage as a short audio clip (WAV/MP3)
- Clips are uploaded to the server and associated with `book_id + page_number`

**Playback side (child device):**
- When child opens a book in read-along mode, device checks for parent recordings
- If a parent clip exists for the current page: play that instead of Piper TTS
- If not: fall back to Piper TTS as usual

**Server:**
- New table: `parent_recordings (id, child_id, book_id, page_number, audio_path, duration_ms, created_at)`
- New API endpoint: `GET /v1/books/{book_id}/recordings` — returns available page clips
- New API endpoint: `POST /v1/books/{book_id}/recordings/{page}` — upload a clip
- Sync: include recording metadata in device sync payload so device knows what's available offline

**Tablet delivery:**
- The clip is streamed to a tablet (web-based player) or downloaded to the e-ink device
- If tablet-based: HTML5 audio with autoplay on page turn
- If e-ink device: pre-cache clips during sync, play via on-device audio

**Privacy consideration:**
- Audio is stored server-side only (not sent to any external API)
- Parent consent implied by account ownership; no child voice stored at this stage
- Clips should be deletable per-book per-page from the parent dashboard
