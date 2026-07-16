---
name: adaptive-compliance-training
created: 2026-07-16
trigger: when etutor-server reaches v1 completion and the BKT+FSRS layer is proven
status: seed
---

## Idea

Fork etutor-server into a separate product for corporate compliance training.
Current compliance platforms are static (click-through video + multiple choice).
The etutor architecture — Socratic questioning, BKT mastery tracking, FSRS spaced
repetition, consequence-based learning — is a direct solution to why compliance
training doesn't produce behaviour change.

## Why Now

The etutor architecture is solving the same problem compliance training has always
failed at:
- People click through without engaging → answer-reveal rate gate solves this
- Annual recertification forgotten by month two → FSRS spaced repetition solves this
- Pass/fail doesn't prove understanding → BKT mastery score per concept is a better
  evidence artefact for regulators
- Static content, same for everyone → role/department/risk-profile gating solves this

Constable Moore's line applies directly: "It will make you highly educated but never
intelligent." Compliance training produces people who pass the test on the day and
retain nothing. The Primer's pedagogy is the product differentiation.

## What Transfers (~70%)

- FastAPI + SQLAlchemy + Alembic DB layer
- BKT + FSRS knowledge tracing (unchanged)
- Session management, history injection
- Socratic system prompt structure
- Hint ladder + consequence-based scenarios
- Eval suite (answer-reveal rate, hint ladder discipline)
- Parent dashboard → Manager/L&D dashboard

## What Needs Rebuilding (~30%)

- **Content layer** — compliance scenarios instead of curriculum topics;
  versioned, jurisdiction-tagged (UK GDPR, US SOX, APAC, sector-specific)
- **Audit trail API** — legally defensible completion records: timestamps,
  content version, answers given, BKT mastery score per concept per date.
  This is the regulatory evidence artefact that replaces binary pass/fail.
- **Tone** — adult peer register in system prompt, not teacher/pupil
- **Multi-jurisdiction content branching** — same scenario, different legal
  outcomes by jurisdiction (UK vs US FCPA on the Wimbledon tickets scenario)
- **Integrations** — LMS/HR systems (Workday, SAP SuccessFactors), SSO

## The Product in One Sentence

"What if compliance training actually worked — because it remembered what you
know, only tested you on what you've forgotten, and never let you click past
a wrong answer without understanding why it was wrong?"

## Trigger Conditions

- etutor-server v1 ships (Phase 6 complete)
- BKT+FSRS layer proven in production with real children
- There is a specific compliance domain worth targeting first (GDPR is the
  obvious entry point — universal, expensive to get wrong, current training
  is universally terrible)

## Repo Strategy

Separate product repo. Could import etutor-server's BKT/FSRS/session layer
as a library, or fork and diverge. Do not add compliance features to
etutor-server itself — different audience, different regulatory context,
different product.
