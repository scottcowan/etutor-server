---
status: partial
phase: 04-parent-dashboard
source: [04-VERIFICATION.md]
started: 2026-07-20T00:45:00Z
updated: 2026-07-20T00:45:00Z
---

## Current Test

[awaiting human testing]

## Tests

### 1. Login page appearance and auth flow
expected: Login page at /parent/login renders a single-field passphrase form; correct password redirects to /parent dashboard; wrong password redirects back to /parent/login with no error message shown
result: [pending]

### 2. Session replay rendering
expected: Turn-by-turn Q/A rows visible with Q: prefix in grey and A: in green; 🚩 Flagged marker shown for any turn with safety_flag=True
result: [pending]

### 3. Learning map accordion + mastery dots
expected: All subjects appear as collapsed <details> elements; tapping a subject expands it showing topic rows with colour-coded mastery dots (grey=not_started, orange=fragile, blue=in_progress, green=solid) and last-practiced date
result: [pending]

### 4. Profile editor form fields + POST round-trip
expected: Name, age, reading level select (Beginner/Developing/Fluent), neurodivergence checkboxes (Dyslexia/ADHD/Dyscalculia/Autism/Hyperlexia), and interests comma field all present; Save changes redirects back to the same page
result: [pending]

### 5. Alert feed badges
expected: 30-day alert feed shows rows with timestamp, coloured badge (frustrated=yellow, sensitive=red, new-interest=teal) and truncated snippet text; empty state shows 'No alerts in the last 30 days.'
result: [pending]

## Summary

total: 5
passed: 0
issues: 0
pending: 5
skipped: 0
blocked: 0

## Gaps
