---
created: 2026-07-15T13:10:00Z
title: Session end triggered by inactivity — device POSTs close event to server
area: api
files:
  - api/sessions.py
  - api/sync.py
---

## Problem

Sessions currently have no close trigger. The `/sessions/{id}/end` endpoint (planned for Phase 2, D-03) assumes the client explicitly calls it. But on an e-ink device, sessions will most likely end from inactivity — the child puts down the device, walks away, falls asleep. There is no guaranteed explicit close.

For Phase 2 to work (BKT batch update fires on session end, FSRS re-fitting fires on session end), the session close must happen reliably even when the device disconnects silently.

## Solution

**On the device**: track time since last interaction. After N minutes of inactivity (suggest 5-10 minutes configurable), the device automatically POSTs a close event to the server:
```
POST /v1/devices/{device_id}/session-end
body: { session_id, ended_at, reason: "inactivity" }
```

**On next session start**: the device checks whether its last session was properly closed. If not (e.g. crash, no connectivity), it sends a backdated close event when it next connects:
```
POST /v1/devices/{device_id}/session-end
body: { session_id, ended_at: <last_interaction_timestamp>, reason: "reconnect_close" }
```

**The server-side endpoint** (`/sessions/{id}/end`) must be idempotent — calling it twice on the same session should be a no-op on the second call.

**BKT/FSRS trigger**: fires only when `reason != "reconnect_close"` for live sessions, but fires always for reconnect-close to ensure no session goes unprocessed.

**Alternative if device comms is unreliable**: a server-side cron (or APScheduler job) that sweeps for sessions older than 30 minutes with no `ended_at` and force-closes them. Lower fidelity on timestamp but guarantees processing. Phase 2 can start with this as a fallback.

## Notes

- `ended_at` on SessionModel is currently nullable (by design, Phase 1). This todo is about when/how it gets populated.
- The eval `test_session_end_hook.py` tests the tutor's conversational behaviour, not this infrastructure concern — both are needed.
- Phase 5 (Device Sync) is where this should be scoped — the sync endpoint already handles device↔server comms.
