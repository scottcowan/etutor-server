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

## The Cynicism Problem

Corporate compliance buyers (legal/risk teams) don't primarily want better learning
outcomes. They want a defensible audit trail: employee X was shown content version Y
on date Z and passed. Static click-through achieves that cheaply. Adaptive training
costs more to build and doesn't automatically make the audit trail stronger.

**Where the product actually wins:**
- FCA, ICO, and some US federal regulators are shifting from "did you train them"
  to "was the training effective." BKT mastery score per concept is a stronger
  evidence artefact than a binary pass/fail when effectiveness is the question.
- Risk-tiered records: someone in procurement has deeper anti-bribery training
  than someone in IT — adaptive naturally produces differentiated records that
  show proportionate effort.
- Repeat near-miss tracking: if an employee has two expense-report incidents,
  the system resurfaces that module and logs it automatically. Genuinely useful
  defensively.

**The product that works:** adaptive enough to produce better learning outcomes,
but with audit trail and evidence artefacts front-and-centre so legal teams can
still buy it for the right (cynical) reasons. BKT mastery score as evidence
artefact is the bridge — it gives compliance teams something to show regulators,
and it actually means something about whether the person understands.

## Regulatory Trajectory

The shift from "did you train them" to "was training effective" is already in motion:

- **UK FCA Consumer Duty (2023)** — firms must demonstrate employees *understand*
  their obligations. "Tick-box compliance" explicitly called out as insufficient.
- **ICO Interserve (£4.4m fine, 2022)** — staff clicked phishing links despite
  "completed" training. ICO used failure rates as evidence training was ineffective,
  not just absent. Establishes the precedent: completion + pass/fail is not enough.
- **US DOJ Corporate Compliance Guidance (2023)** — prosecutors explicitly ask
  whether training is "tested and updated" and whether employees *understand* it.
- **EU AI Act (2024)** — requires "AI literacy" for staff working with AI systems.
  No specification yet on what "adequate" means — creates the same gap.

The pattern: regulators write outcome-based standards, enforcement creates precedent
defining what "effective" means operationally, the market needs evidence artefacts
that map to those precedents.

**The arbitrage:** the gap between what buyers currently accept as proof
(completion + pass/fail) and what regulators are moving toward (demonstrated
retention over time, behaviour change evidence, risk-tiered depth). A product
that produces per-concept mastery scores with decay curves + timestamped spaced
revisiting evidence + risk-tiered depth can be sold on existing grounds while
being defensible against the next generation of enforcement.

**Why the window is open:** Workday, Cornerstone, SAP SuccessFactors are LMS
infrastructure with bolted-on compliance modules. They won't rebuild their
assessment models around BKT — platform lock-in makes architectural change slow.
The learning science is available, the regulatory direction is visible, and the
incumbents can't move fast enough.

**The risk:** regulators move slowly and unpredictably. The hedge is that better
learning outcomes are also a real selling point to compliance officers and culture
teams inside the firm, not just to legal teams managing regulatory exposure.

## Repo Strategy

Separate product repo. Could import etutor-server's BKT/FSRS/session layer
as a library, or fork and diverge. Do not add compliance features to
etutor-server itself — different audience, different regulatory context,
different product.
