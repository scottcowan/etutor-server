# etutor-server

AI tutoring server for the [eink-tutor](https://github.com/scottcowan/hardware) hardware device.

Provides:
- OpenAI-compatible STT endpoint (Whisper base)
- AI tutoring inference (Claude / GPT / Gemma routing)
- Per-child profiles, learning plans, session history
- Calibre-Web integration for book recommendations
- Parent dashboard API
- Child web interface (browser-based testing without hardware)

---

## Architecture

```
etutor-server/
├── api/              # FastAPI — all HTTP endpoints
│   ├── stt.py        # POST /v1/audio/transcriptions (Whisper, OpenAI-compatible)
│   ├── chat.py       # POST /v1/chat/completions (tutor inference)
│   ├── sync.py       # GET/POST /v1/devices/:id/sync (content packages)
│   ├── sessions.py   # Session logging and replay
│   └── dashboard.py  # Parent dashboard API
├── services/
│   ├── tutor.py      # Socratic tutoring logic, system prompt builder
│   ├── profiles.py   # Per-child profile management
│   ├── planner.py    # Learning plan generation and content packaging
│   ├── recommender.py# Book recommendation engine (Calibre-Web integration)
│   ├── interests.py  # Interest graph inference from session history
│   └── sync.py       # Content package generation and device sync
├── web/
│   ├── child/        # Child-facing browser interface (testing without hardware)
│   └── parent/       # Parent dashboard web UI
├── config/
│   ├── settings.py   # Environment config
│   └── prompts/      # System prompt templates per age group
├── data/
│   └── migrations/   # Alembic DB migrations
└── tests/
```

## Stack

- **API:** FastAPI + uvicorn
- **Database:** SQLite (dev) / PostgreSQL (prod) via SQLAlchemy
- **STT:** faster-whisper (local) or OpenAI Whisper API (fallback)
- **Inference:** Anthropic / OpenAI / Ollama via litellm router
- **Books:** Calibre-Web REST API integration
- **Auth:** Simple JWT — parent vs child tokens

## Quick Start

```bash
cp config/.env.example config/.env
# edit config/.env with your API keys and Calibre-Web URL

pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

Child web interface: http://localhost:8000/child
Parent dashboard: http://localhost:8000/parent

## Device Integration

Devices POST audio to `/v1/audio/transcriptions` (OpenAI-compatible).
Devices POST chat to `/v1/chat/completions` with `X-Device-ID` header.
Devices sync content via `/v1/devices/{id}/sync`.

---

## Related

- [hardware](https://github.com/scottcowan/hardware) — eink-tutor device hardware
- [cyberharness](https://github.com/scottcowan/cyberharness) — cyberdeck AI harness
