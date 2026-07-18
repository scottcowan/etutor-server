# Phase 4: Parent Dashboard - Context

**Gathered:** 2026-07-18
**Status:** Ready for planning

<domain>
## Phase Boundary

A logged-in parent can access `/parent` to: replay session turns, browse a colour-coded mastery map of all 777 curriculum topics, edit their child's profile (name, age, reading level, neurodivergence flags, interests), and see a chronological alert feed flagging frustration signals, sensitive-topic questions, and off-plan interest spikes. No child-facing UI in this phase — that is Phase 5.

Requirements: PARENT-01, PARENT-02, PARENT-03, PARENT-04, PARENT-05

</domain>

<decisions>
## Implementation Decisions

### Auth (PARENT-05)
- **D-01:** v1 auth is a fixed passphrase stored in `.env` (e.g. `PARENT_PASSWORD=xxxx`). No multi-tenant, no email signup. Planned evolution: basic user management → OpenID support in later phases.
- **D-02:** Auth state lives in a server-side httpOnly session cookie. Set on successful login at `POST /parent/login`. No JS needed for auth.
- **D-03:** Login page at `/parent/login` is minimal — one password field, one submit button, matching the white-card aesthetic. No username field (single-family v1).
- **D-04:** On failed login or expired session: redirect to `/parent/login` with no error message (clean, minimal).
- **D-05:** All `/parent/*` routes (except `/parent/login`) require a valid session cookie. Redirect to login if missing or invalid. This also fixes CR-02 (IDOR on session endpoints) — session endpoints must verify the authenticated parent's child_id matches.

### Mastery Map (PARENT-02)
- **D-06:** Layout is a subject-grouped accordion: 28 subjects collapsed by default, each expands to show its topics. Parent is on a full browser (no e-ink constraint).
- **D-07:** Each topic row shows: name + colour-coded mastery dot + last studied date. No p_mastery % in v1 (keep it accessible for non-technical parents).
- **D-08:** Mastery buckets mapped to colours: `not_started` = grey, `fragile` = amber, `in_progress` = blue, `solid` = green (using the existing `#7a9e7e` green accent).
- **D-09:** All 777 topics appear (not_started shown as grey), but subjects default to collapsed. Parent opens subjects they care about — avoids a 777-item firehose.

### Alert Feed (PARENT-04)
- **D-10:** Frustration signal: `hint_used` count > 3 on the same KC in a single session triggers an alert. Logged at session end when `POST /sessions/{id}/end` tallies per-KC hint counts.
- **D-11:** Off-plan interest spike: child mentions a topic (tag match) not in their `interests` list, 3+ turns in a session. Detected by the existing Phase 3 interest extraction — if a new topic appears in extracted interests that wasn't in the profile before, surface it as a "new interest" alert.
- **D-12:** Sensitive-topic flag: add `safety_flag: bool` field to `InteractionEventModel`. Set at `log_turn()` time via a curated keyword list check on the child's question text. No extra LLM call.
- **D-13:** Alert feed format: chronological list (most recent first), each row shows timestamp, child name, alert type badge (`frustrated` / `sensitive` / `new-interest`), and a snippet of the triggering text.
- **D-14:** Alert retention: show alerts from the last 30 days (matches session replay window from ROADMAP success criterion).

### Profile Editor (PARENT-03)
- **D-15:** Editable fields on the profile form: name, age, reading level (enum: beginner / developing / fluent), neurodivergence flags (multi-select checkboxes), interests (add/remove tags).
- **D-16:** Neurodivergence flags are a fixed set of checkboxes: dyslexia, ADHD, dyscalculia, autism, hyperlexia. Stored as a JSON array in `ChildProfileModel.neurodivergence`. Claude has discretion on the exact DB storage format.
- **D-17:** Profile changes take effect immediately on the next chat turn — `api/chat.py` must re-read the child profile from DB on each request (not cache). ROADMAP success criterion requires this.
- **D-18:** Form is inline on the child's profile page at `/parent/children/{child_id}` — not a modal. Simple HTML form with POST action.

### UI Style
- **D-19:** Parent dashboard uses the existing white-card aesthetic (white cards, `#e0e0e0` borders, `border-radius: 12px`, `#7a9e7e` green accent, `-apple-system` sans-serif). No e-ink constraint on the parent side — full browser.

### Claude's Discretion
- Session cookie implementation details (itsdangerous signing vs starlette SessionMiddleware)
- Exact HTML structure of accordion (pure CSS or minimal JS toggle)
- Interests tag editor UI (comma-separated input field is fine)
- Alert keyword list contents (planner assembles from common child-safety word lists)
- Exact DB query for tallying hint counts at session end

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing API and DB
- `api/parent.py` — Jinja2 router scaffolded at `/parent`; Phase 4 extends this file
- `api/sessions.py` — `GET /sessions/{child_id}` and `GET /sessions/{session_id}/turns` (HIST-03); Phase 4 adds auth middleware here
- `api/chat.py` — must re-read child profile on each request (D-17); Phase 4 verifies this is already the case
- `db/models.py` — `ChildProfileModel` fields (name, age, reading_level, interests, neurodivergence, device_id); `InteractionEventModel` (hint_used field for D-10; add safety_flag for D-12)
- `db/crud.py` — `update_interests()`, `get_session_history()`, `get_turns_by_session_id()` — reuse for session replay and alert queries

### Existing Templates and Style
- `web/parent/templates/dashboard.html` — existing white-card aesthetic; Phase 4 extends with auth, mastery map, alert feed, profile editor sections
- `web/child/templates/` — cross-reference for any shared template patterns

### Requirements
- `.planning/REQUIREMENTS.md` §PARENT-01–05 — exact acceptance criteria
- `.planning/ROADMAP.md` §Phase 4 — success criteria and key decisions

### Phase 3 Integration
- `services/session_intelligence.py` — `extract_and_update_interests()` output feeds the "new interest" alert detection (D-11)
- `.planning/phases/03-session-intelligence/03-CONTEXT.md` — D-08 dual-trigger interest extraction already wired; Phase 4 reads the result

### Known Bugs to Fix
- `.planning/phases/02-knowledge-tracing-backend/02-REVIEW.md` — CR-02 (IDOR on session endpoints): Phase 4 auth gate is the right time to fix this. Session endpoints must verify the authenticated parent's child_id.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `api/parent.py` — router and `Jinja2Templates` already wired; extend with new routes (login, children, mastery-map, alerts)
- `web/parent/templates/dashboard.html` — base template with established CSS variables (card style, green accent, header pattern); extend rather than rewrite
- `db/crud.py` — `get_session_history()`, `get_turns_by_session_id()`, `update_interests()` all available for session replay and profile editing
- `services/knowledge_tracing.py` — `mastery_context_for_prompt()` returns mastery buckets per KC; reuse for mastery map rendering

### Established Patterns
- Jinja2 + HTMLResponse (server-rendered HTML, no JS framework) — used throughout `api/parent.py` and `api/child.py`
- `Depends(get_db)` pattern for DB sessions in all API routes — Phase 4 adds `Depends(require_parent_auth)` alongside it
- `Optional[X]` typing (not `X | None`) for Python 3.9 compat
- `datetime.now(timezone.utc)` (never `datetime.utcnow()`)

### Integration Points
- `api/chat.py` — D-17: verify child profile is re-read from DB per request (not cached in memory); the Phase 3 wiring already calls `get_db()` per request, so this should be satisfied
- `api/sessions.py` — add auth guard to `GET /sessions/{child_id}` and `GET /sessions/{session_id}/turns` (CR-02 fix)
- `db/models.py` — add `safety_flag: bool` column to `InteractionEventModel` with Alembic migration (D-12)
- `api/sessions.py end_session()` — add hint count tally per KC and write frustration alert records (D-10)

</code_context>

<specifics>
## Specific Ideas

- **Frustration → remediation (deferred):** User insight: when a child needs >3 hints on a KC, the system should auto-drop to a remedial sub-topic and come back up when they understand it. This is adaptive remediation routing — deferred to Phase 6 safety/polish. Phase 4 only logs the alert.
- **Parent sees full browser:** No e-ink constraint on parent UI — can use richer layouts (accordion with CSS transitions, colour-coded dots, date formatting).
- **Auth evolution path:** Fixed passphrase → basic user management → OpenID. v1 is passphrase-only; the code should be structured so auth middleware is easy to swap.

</specifics>

<deferred>
## Deferred Ideas

- **Adaptive remediation routing** — when hint count > 3, auto-route child to remedial sub-topic and resume. Phase 6 scope.
- **Alert notification mechanism** (push/email) — not in PARENT requirements; v1 is dashboard-only.
- **Multi-child household** — out of scope (PROJECT.md); single child per device v1.
- **OpenID / OAuth parent auth** — planned future evolution; v1 passphrase only.

### Reviewed Todos (not folded)
- "Web-first UI that replicates e-ink experience" — parent has no e-ink constraint; user confirmed "no limit on parent dashboard". Deferred; may apply to Phase 5 child interface.
- "Buddy avatar that grows with the child" — Phase 5/6 scope; not in PARENT requirements.
- "E-ink illustration library" — Phase 5 child interface scope.
- "Parent read-aloud recording played back on child's device" — Phase 5 device sync scope.
- "Session end triggered by inactivity" — Phase 5 device/client scope.

</deferred>

---

*Phase: 4-parent-dashboard*
*Context gathered: 2026-07-18*
