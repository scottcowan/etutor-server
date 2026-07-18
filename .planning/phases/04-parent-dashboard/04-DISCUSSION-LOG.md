# Phase 4: Parent Dashboard - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-18
**Phase:** 4-parent-dashboard
**Areas discussed:** Auth, Mastery map layout, Alert definitions, Profile editor scope

---

## UI Aesthetic (pre-discussion)

| Option | Description | Selected |
|--------|-------------|----------|
| Keep white-card style | Existing dashboard.html design (white cards, #7a9e7e green, clean sans-serif) | ✓ |
| E-ink aesthetic | Near-black on off-white, minimal colour, no shadows | |
| Fold the todo — decide later | Note idea for future polish | |

**User's choice:** "no limit on parent dashboard" — keep white-card style, no e-ink constraint.
**Notes:** Todo "Web-first UI that replicates e-ink experience" reviewed but not folded. May apply to Phase 5 child interface.

---

## Auth

| Option | Description | Selected |
|--------|-------------|----------|
| Fixed passphrase in .env | Password set in config, simplest possible | ✓ (v1) |
| Token in .env | Long random token, bookmark URL or cookie | |

**User's choice:** "fixed initially, basic user management after then OpenID support later"
**Notes:** v1 is passphrase-only. Auth code should be structured so the middleware is easy to swap.

| Option | Description | Selected |
|--------|-------------|----------|
| Server-side session (httpOnly cookie) | Browser sends cookie, server validates, XSS-safe | ✓ |
| Signed token in URL or localStorage | XSS-vulnerable | |

**User's choice:** Server-side session (httpOnly cookie)

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal login (password field + submit) | One field, one button | ✓ |
| Child selector at login | After password, show child name/avatar | |

**User's choice:** Minimal

| Option | Description | Selected |
|--------|-------------|----------|
| Redirect to /parent/login with no message | Clean, minimal | ✓ |
| Redirect with reason banner | "Session expired" or "Wrong password" shown | |

**User's choice:** Redirect with no message

---

## Mastery Map Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Subject accordion | 28 subjects collapsed, expand to see topics | ✓ |
| Grid by mastery bucket | Four columns: not_started/fragile/in_progress/solid | |

**User's choice:** Subject accordion

| Option | Description | Selected |
|--------|-------------|----------|
| Name + colour dot only | Compact | |
| Name + colour dot + last studied date | Clean and informative | ✓ |
| Name + colour dot + p_mastery % + last studied | Full detail | |

**User's choice:** "parents get a full page but the kids are on an eink" — clarified to name + dot + last studied date.
**Notes:** Parent is on full browser, no e-ink constraint. Richer display is fine.

| Option | Description | Selected |
|--------|-------------|----------|
| All 777 topics (show not_started as grey) | Full curriculum visible | ✓ (collapsed) |
| Only studied topics + subject headers | Shorter list | |

**User's choice:** "777 is daunting it should be collapsed" — all topics visible but subjects default to collapsed.

---

## Alert Definitions

| Option | Description | Selected |
|--------|-------------|----------|
| >3 hints on same KC | ROADMAP suggestion, simple count-based | ✓ |
| Repeated wrong answers >3 | Stuck loop detection | |

**User's choice:** >3 hints triggers frustration alert
**Notes:** User insight: system should auto-drop to remedial sub-topic when frustration is high. Deferred to Phase 6.

| Option | Description | Selected |
|--------|-------------|----------|
| New tag not in interests list, 3+ turns | Uses Phase 3 extraction | ✓ |
| Topic outside age-gate | Flags above-bloom-target exploration | |

**User's choice:** Child mentions topic not in interests list, 3+ turns

| Option | Description | Selected |
|--------|-------------|----------|
| Keyword list match | Curated terms, simple | |
| Claude's safety classification | Use existing eval infrastructure | ✓ |

**User's choice:** Claude's safety classification → resolved to `safety_flag` field on `InteractionEventModel` set via keyword list at `log_turn()` time

| Option | Description | Selected |
|--------|-------------|----------|
| Add safety_flag to InteractionEventModel at log_turn | No extra LLM call | ✓ |
| Post-process on session end | Keeps chat latency clean | |

**User's choice:** Add safety_flag field, set at log_turn time

| Option | Description | Selected |
|--------|-------------|----------|
| Chronological list with type badges | Most recent first, badge per type | ✓ |
| Grouped by alert type | Three sections by category | |

**User's choice:** Chronological list with type badges

---

## Profile Editor

| Option | Description | Selected |
|--------|-------------|----------|
| Reading level | beginner/developing/fluent enum | ✓ |
| Neurodivergence flags | Multi-select checkboxes | ✓ |
| Interests | Add/remove tags | ✓ |
| Child name and age | Beyond REQUIREMENTS.md but useful | ✓ |

**User's choice:** All four field categories

| Option | Description | Selected |
|--------|-------------|----------|
| Free-text list (JSON array) | Flexible | |
| Fixed set: dyslexia, ADHD, dyscalculia, autism, hyperlexia | Constrained and clear | |

**User's choice:** "whatever works best" — Claude's discretion. Using fixed checkbox set.

| Option | Description | Selected |
|--------|-------------|----------|
| Immediately on next chat turn | Meets ROADMAP success criterion | ✓ |
| On next session start only | Simpler, doesn't meet criterion | |

**User's choice:** Immediately on next chat turn

---

## Claude's Discretion

- Session cookie implementation (itsdangerous vs starlette SessionMiddleware)
- Exact HTML structure of accordion (pure CSS vs minimal JS)
- Interests tag editor UI (comma-separated input is fine)
- Alert keyword list contents
- Neurodivergence storage format (fixed checkbox set deemed best)
- Exact DB query structure for hint count tally

## Deferred Ideas

- Adaptive remediation routing (>3 hints → auto-drop to remedial sub-topic) — Phase 6
- Alert push/email notifications — not in requirements
- Multi-child household — out of scope v1
- OpenID/OAuth parent auth — future evolution
- Web-first e-ink UI — applies to Phase 5 child interface
- Buddy avatar — Phase 5/6 scope
- E-ink illustration library — Phase 5 scope
- Parent read-aloud recording — Phase 5 device sync
- Session end via inactivity — Phase 5 client scope
