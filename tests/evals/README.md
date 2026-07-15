# Etutor Evals

Behavioural test suite for the AI tutoring system. These are not unit tests —
they make live LLM calls and measure pedagogical properties of tutor responses.

Evals run against **any litellm-compatible model** — Anthropic, OpenAI, Ollama,
AWS Bedrock, Groq, Mistral, etc. They skip automatically when no LLM backend
is configured.

## Evals

| File | What it measures | Target | Research basis |
|---|---|---|---|
| `test_answer_reveal.py` | % of responses that give away the answer when child is wrong | <10% reveal rate | MathDial: zero-shot LLMs reveal 66% of the time |
| `test_socratic_quality.py` | Ends with question, one question only, no sycophancy, age-appropriate length | 100% on each dimension | pedagogy.md §Interaction Design |
| `test_hint_ladder.py` | 3-level hint sequence: no reveal at L1/L2, reveal + follow-up at L3 | All 4 checks pass | pedagogy.md §3, Dey Tithi 2025 (75% hint accuracy baseline) |
| `test_curriculum_accuracy.py` | Factual correctness on deterministic questions | 0 hallucinations on known-wrong answers | Herklotz 2025: ~7% error rate with GPT-4; model drift guard |
| `test_tangent_following.py` | Tutor follows curiosity tangents rather than redirecting back to original topic | 0% redirect rate | Diamond Age Primer: "Curiosity is the curriculum" |
| `test_session_end_hook.py` | Session-end response leaves an open question or cliffhanger | 100% hook rate | Primer cliffhanger mechanic; retrieval practice (unanswered question overnight) |
| `test_patience.py` | Re-explanations use different words/analogies; no impatience phrases | 0% impatience, <0.7 word overlap | Primer: "The twentieth explanation is as welcome as the first" |

## Running

```bash
# Anthropic (default model)
ANTHROPIC_API_KEY=sk-... pytest tests/evals/ -v

# OpenAI
OPENAI_API_KEY=sk-... ETUTOR_EVAL_MODEL=gpt-4o-mini pytest tests/evals/

# Ollama (local, no key needed)
ETUTOR_EVAL_MODEL=ollama/llama3.2 pytest tests/evals/

# AWS Bedrock
AWS_PROFILE=myprofile ETUTOR_EVAL_MODEL=bedrock/anthropic.claude-3-haiku-20240307-v1:0 pytest tests/evals/

# Override the model under test (any litellm model string)
ETUTOR_EVAL_MODEL=claude-sonnet-5 ANTHROPIC_API_KEY=sk-... pytest tests/evals/ -v

# Standalone report for a single eval
ANTHROPIC_API_KEY=sk-... python tests/evals/test_answer_reveal.py
```

Evals skip with a clear message when no backend is configured — safe to include
in `pytest tests/` without credentials.

## When to run

| Trigger | Evals to run |
|---|---|
| System prompt change | `test_answer_reveal`, `test_socratic_quality`, `test_hint_ladder`, `test_tangent_following`, `test_patience` |
| Model version update | All |
| Before a release | All |
| Weekly CI | All (with credentials) |

## Interpreting results

**test_answer_reveal** — any reveal rate above 10% means the system prompt is
failing the Socratic constraint. Compare against the 66% zero-shot baseline.

**test_socratic_quality** — `one_question_per_turn` failures are the most
common. The model tends to ask "What do you think? And do you know why?"

**test_hint_ladder** — `hint2_reveals` failures mean the model is giving up
scaffolding too early. `explain_missing_followup` means it ends on the answer
without restoring confidence.

**test_curriculum_accuracy** — any hallucination on deterministic fact questions
(arithmetic, capitals, boiling point) is a hard failure. Run after every model
version change in `config/settings.py`.

**test_tangent_following** — any redirect detected means the system prompt is
still suppressing curiosity. Gate: 0% redirect rate.

**test_session_end_hook** — any response that ends without a question or
cliffhanger when the child says goodbye is a failure. Gate: 100% hook rate.

**test_patience** — impatience phrases ("we already covered this") or near-
verbatim re-explanations (>0.7 word overlap) are failures. Gate: 0 impatience,
<0.7 overlap across two re-explanation requests.
