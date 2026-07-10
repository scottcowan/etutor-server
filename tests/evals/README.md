# Etutor Evals

Behavioural test suite for the AI tutoring system. These are not unit tests —
they make live LLM calls and measure pedagogical properties of tutor responses.

## Evals

| File | What it measures | Target | Research basis |
|---|---|---|---|
| `test_answer_reveal.py` | % of responses that give away the answer when child is wrong | <10% reveal rate | MathDial: zero-shot LLMs reveal 66% of the time |
| `test_socratic_quality.py` | Ends with question, one question only, no sycophancy, age-appropriate length | 100% on each dimension | pedagogy.md §Interaction Design |
| `test_hint_ladder.py` | 3-level hint sequence: no reveal at L1/L2, reveal + follow-up at L3 | All 4 checks pass | pedagogy.md §3, Dey Tithi 2025 (75% hint accuracy baseline) |
| `test_curriculum_accuracy.py` | Factual correctness on deterministic questions | 0 hallucinations on known-wrong answers | Herklotz 2025: ~7% error rate with GPT-4; model drift guard |

## Running

```bash
# Run all evals (requires API key)
ANTHROPIC_API_KEY=sk-... pytest tests/evals/ -v

# Run a specific eval
ANTHROPIC_API_KEY=sk-... pytest tests/evals/test_answer_reveal.py -v

# Run as a standalone report (cleaner output)
ANTHROPIC_API_KEY=sk-... python tests/evals/test_answer_reveal.py
ANTHROPIC_API_KEY=sk-... python tests/evals/test_socratic_quality.py
ANTHROPIC_API_KEY=sk-... python tests/evals/test_hint_ladder.py
ANTHROPIC_API_KEY=sk-... python tests/evals/test_curriculum_accuracy.py

# Override the model under test
ANTHROPIC_API_KEY=sk-... ETUTOR_EVAL_MODEL=claude-sonnet-5 pytest tests/evals/ -v
```

## When to run

| Trigger | Evals to run |
|---|---|
| System prompt change | `test_answer_reveal`, `test_socratic_quality`, `test_hint_ladder` |
| Model version update | All four |
| Before a release | All four |
| Weekly CI | All four |

## Interpreting results

**test_answer_reveal** — any reveal rate above 10% means the system prompt is
failing the Socratic constraint. Compare against the 66% zero-shot baseline
to understand how much the prompt is doing.

**test_socratic_quality** — `one_question_per_turn` failures are the most
common. The model tends to ask "What do you think? And do you know why?" Fix
by adding explicit "ONE question only" to the system prompt.

**test_hint_ladder** — `hint2_reveals` failures indicate the model is giving
up scaffolding too early. `explain_missing_followup` failures mean the model
is ending on the answer without restoring confidence.

**test_curriculum_accuracy** — any hallucination on the deterministic fact
questions (arithmetic, capital cities, boiling point) is a hard failure.
Run this after every `model_under_8` or `model_8_plus` version change in
`config/settings.py`.
