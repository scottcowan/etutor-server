"""
Eval 1: Answer-Reveal Rate Audit
=================================
Measures what % of tutor responses reveal the answer directly when a child
makes a wrong attempt, rather than scaffolding with a hint.

Baseline from research: zero-shot LLMs give away the answer ~66% of the time
(Macina et al., MathDial EMNLP 2023, arXiv:2305.14536).
Target for etutor: <10% reveal rate.

Run:
    ANTHROPIC_API_KEY=... pytest tests/evals/test_answer_reveal.py -v

Each case scores as SCAFFOLD (pass) or REVEAL (fail).
A reveal is when the response contains the correct answer unprompted.
"""

import asyncio
import os
import re
import pytest
import litellm
from dataclasses import dataclass
from services.tutor import AGE_INSTRUCTIONS, SYSTEM_PROMPT_TEMPLATE


# ---------------------------------------------------------------------------
# Test cases: (topic, wrong_attempt, correct_answer, bloom_level)
# The correct_answer is what we check for in the tutor response.
# ---------------------------------------------------------------------------
@dataclass
class Case:
    topic: str
    child_age: int
    question_asked: str
    wrong_attempt: str
    correct_answer: str  # string(s) that would constitute a reveal
    bloom_level: str


CASES = [
    # --- Maths ---
    Case(
        topic="multiplication",
        child_age=9,
        question_asked="What is 7 times 8?",
        wrong_attempt="I think it's 54",
        correct_answer="56",
        bloom_level="remember",
    ),
    Case(
        topic="fractions",
        child_age=10,
        question_asked="What is half of 3/4?",
        wrong_attempt="I think it's 1/2",
        correct_answer="3/8",
        bloom_level="apply",
    ),
    Case(
        topic="place value",
        child_age=8,
        question_asked="What is the value of the 3 in 345?",
        wrong_attempt="Three",
        correct_answer="300",
        bloom_level="understand",
    ),

    # --- Science ---
    Case(
        topic="photosynthesis",
        child_age=10,
        question_asked="What do plants need to make their food?",
        wrong_attempt="They eat soil",
        correct_answer="sunlight",
        bloom_level="remember",
    ),
    Case(
        topic="states of matter",
        child_age=9,
        question_asked="What happens to water when it reaches 100 degrees?",
        wrong_attempt="It becomes solid",
        correct_answer="boil",
        bloom_level="understand",
    ),
    Case(
        topic="the water cycle",
        child_age=11,
        question_asked="What is the process called when water turns into vapour from the sea?",
        wrong_attempt="Condensation",
        correct_answer="evaporation",
        bloom_level="remember",
    ),

    # --- Geography ---
    Case(
        topic="capitals",
        child_age=9,
        question_asked="What is the capital of Australia?",
        wrong_attempt="Sydney",
        correct_answer="Canberra",
        bloom_level="remember",
    ),

    # --- Literacy ---
    Case(
        topic="story comprehension",
        child_age=8,
        question_asked="Why did the character feel scared at the start of the story?",
        wrong_attempt="Because he was hungry",
        correct_answer="dark forest",  # context-dependent — checks for over-specific reveal
        bloom_level="understand",
    ),

    # --- Vocabulary ---
    Case(
        topic="vocabulary",
        child_age=10,
        question_asked="What does 'enormous' mean?",
        wrong_attempt="It means fast",
        correct_answer="very large",
        bloom_level="remember",
    ),

    # --- Higher-order ---
    Case(
        topic="ecosystems",
        child_age=12,
        question_asked="Why would removing wolves from an ecosystem affect the plants?",
        wrong_attempt="Because wolves eat plants",
        correct_answer="deer",  # the indirect link — checks if tutor gives the chain away
        bloom_level="analyse",
    ),
]


def build_test_prompt(case: Case) -> list[dict]:
    age_key = "under_8" if case.child_age < 8 else "8_plus"
    system = SYSTEM_PROMPT_TEMPLATE.format(
        age_instructions=AGE_INSTRUCTIONS[age_key],
        name="Alex",
        age=case.child_age,
        interests="dinosaurs, Minecraft",
        reading_level="age-appropriate",
        current_topic=case.topic,
        current_books="none currently",
        top_interest="dinosaurs",
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": case.wrong_attempt},
    ]


def response_reveals_answer(response: str, correct_answer: str) -> bool:
    """
    Returns True if the tutor response contains the correct answer.
    Case-insensitive. Checks for the answer as a word boundary match
    to avoid false positives (e.g. "56" matching "256").
    """
    pattern = r'\b' + re.escape(correct_answer.lower()) + r'\b'
    return bool(re.search(pattern, response.lower()))


async def run_case(case: Case, model: str) -> tuple[bool, str]:
    messages = build_test_prompt(case)
    response = await litellm.acompletion(
        model=model,
        messages=messages,
        max_tokens=200,
        temperature=0.3,
    )
    content = response.choices[0].message.content
    revealed = response_reveals_answer(content, case.correct_answer)
    return revealed, content


# ---------------------------------------------------------------------------
# Pytest tests — one per case so failures are individually visible
# ---------------------------------------------------------------------------

MODEL = os.environ.get("ETUTOR_EVAL_MODEL", "claude-haiku-4-5-20251001")

@pytest.mark.parametrize("case", CASES, ids=[c.topic + "_age" + str(c.child_age) for c in CASES])
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping live eval"
)
def test_does_not_reveal_answer(case):
    """Tutor must not give away the correct answer when child makes a wrong attempt."""
    revealed, response = asyncio.get_event_loop().run_until_complete(
        run_case(case, MODEL)
    )
    assert not revealed, (
        f"\n\nREVEAL DETECTED on topic='{case.topic}' age={case.child_age}\n"
        f"Question: {case.question_asked}\n"
        f"Child said: '{case.wrong_attempt}'\n"
        f"Correct answer: '{case.correct_answer}'\n"
        f"Tutor responded: {response}\n"
    )


# ---------------------------------------------------------------------------
# Summary runner — use this for a quick report outside pytest
# ---------------------------------------------------------------------------

async def run_all(model: str = MODEL):
    results = []
    for case in CASES:
        revealed, response = await run_case(case, model)
        results.append({
            "topic": case.topic,
            "age": case.child_age,
            "bloom": case.bloom_level,
            "revealed": revealed,
            "response": response,
        })
    reveals = [r for r in results if r["revealed"]]
    reveal_rate = len(reveals) / len(results) * 100
    print(f"\n{'='*60}")
    print(f"Answer-reveal rate: {reveal_rate:.0f}%  ({len(reveals)}/{len(results)} cases)")
    print(f"Target: <10%   Baseline (zero-shot): ~66%")
    print(f"{'='*60}")
    for r in results:
        status = "REVEAL" if r["revealed"] else "ok    "
        print(f"  {status}  [{r['bloom']:10s}] age={r['age']}  {r['topic']}")
        if r["revealed"]:
            print(f"          Response: {r['response'][:120]}...")
    return reveal_rate, results


if __name__ == "__main__":
    rate, _ = asyncio.run(run_all())
    exit(0 if rate < 10 else 1)
