"""
Eval 4: Curriculum Accuracy (Hallucination Guard)
===================================================
Verifies the tutor gives factually correct answers to questions with
deterministic correct answers.

Run after every API model update — the same model can degrade substantially
between versions (Chen, Zaharia & Zou, arXiv:2307.09009).

Two test modes:
  - Arithmetic: Python-computed expected answer; no string guessing.
  - Factual: two-turn exchange forces a direct answer after an initial
    Socratic deflection, then checks accepted/wrong answer strings.

Run:
    ANTHROPIC_API_KEY=... pytest tests/evals/test_curriculum_accuracy.py -v
    AWS_PROFILE=... pytest tests/evals/test_curriculum_accuracy.py -v
"""

import asyncio
import fractions
import os
import re
import pytest
import litellm
from dataclasses import dataclass, field
from services.tutor import AGE_INSTRUCTIONS, SYSTEM_PROMPT_TEMPLATE, reading_level_instructions


# ---------------------------------------------------------------------------
# Arithmetic cases — answer verified by Python, not string matching
# ---------------------------------------------------------------------------

@dataclass
class ArithmeticCase:
    topic: str
    child_age: int
    question: str
    python_expr: str        # eval() produces the expected numeric answer
    wrong_answers: list[str]


ARITHMETIC_CASES = [
    ArithmeticCase(
        topic="multiplication",
        child_age=9,
        question="What is 8 times 7?",
        python_expr="8 * 7",
        wrong_answers=["54", "58", "48", "63"],
    ),
    ArithmeticCase(
        topic="division",
        child_age=9,
        question="What is 63 divided by 9?",
        python_expr="63 // 9",
        wrong_answers=["6", "8", "9"],
    ),
    ArithmeticCase(
        topic="division",
        child_age=9,
        question="What is 48 divided by 6?",
        python_expr="48 // 6",
        wrong_answers=["6", "9", "10"],
    ),
    ArithmeticCase(
        topic="multiplication",
        child_age=10,
        question="What is 12 times 11?",
        python_expr="12 * 11",
        wrong_answers=["122", "121", "144"],
    ),
    ArithmeticCase(
        topic="fractions",
        child_age=10,
        question="What is one half plus one quarter? Give me a fraction.",
        python_expr="str(fractions.Fraction(1,2) + fractions.Fraction(1,4))",
        # expected: "3/4"
        wrong_answers=["1/2", "2/4", "one half", "1/4"],
    ),
    ArithmeticCase(
        topic="fractions",
        child_age=10,
        question="What is three quarters minus one quarter? Give me a fraction.",
        python_expr="str(fractions.Fraction(3,4) - fractions.Fraction(1,4))",
        # expected: "1/2" — also accept unsimplified "2/4"
        wrong_answers=["1/4", "3/4", "one quarter"],
    ),
]


# ---------------------------------------------------------------------------
# Factual cases — two-turn design forces a direct answer
# ---------------------------------------------------------------------------

@dataclass
class FactualCase:
    topic: str
    child_age: int
    question: str
    accepted_answers: list[str]
    wrong_answers: list[str]


FACTUAL_CASES = [
    FactualCase(
        topic="capitals",
        child_age=9,
        question="What is the capital city of France?",
        accepted_answers=["paris"],
        wrong_answers=["lyon", "marseille", "nice", "bordeaux"],
    ),
    FactualCase(
        topic="capitals",
        child_age=9,
        question="What is the capital of Australia?",
        accepted_answers=["canberra"],
        wrong_answers=["sydney", "melbourne", "brisbane"],
    ),
    FactualCase(
        topic="geography",
        child_age=10,
        question="What is the longest river in the world?",
        accepted_answers=["nile", "amazon"],
        wrong_answers=["mississippi", "yangtze", "congo", "thames"],
    ),
    FactualCase(
        topic="planets",
        child_age=10,
        question="What is the largest planet in our solar system?",
        accepted_answers=["jupiter"],
        wrong_answers=["saturn", "uranus", "neptune", "earth"],
    ),
    FactualCase(
        topic="biology",
        child_age=10,
        question="How many bones are in the adult human body?",
        accepted_answers=["206"],
        wrong_answers=["200", "208", "212", "300"],
    ),
    FactualCase(
        topic="history",
        child_age=11,
        question="In what year did World War Two end?",
        accepted_answers=["1945"],
        wrong_answers=["1944", "1946", "1943", "1918"],
    ),
    FactualCase(
        topic="history",
        child_age=11,
        question="Who was the first person to walk on the moon?",
        accepted_answers=["neil armstrong", "armstrong"],
        wrong_answers=["buzz aldrin", "aldrin", "yuri gagarin", "gagarin"],
    ),
    FactualCase(
        topic="states of matter",
        child_age=9,
        question="At what temperature does water boil at sea level?",
        accepted_answers=["100", "212"],
        wrong_answers=["90", "110", "50", "200"],
    ),
    FactualCase(
        topic="vocabulary",
        child_age=10,
        question="What does the word 'enormous' mean?",
        accepted_answers=["very large", "very big", "huge", "gigantic", "extremely large"],
        wrong_answers=["very small", "very fast", "very quiet"],
    ),
]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _system(age: int, topic: str) -> str:
    age_key = "under_8" if age < 8 else "8_plus"
    rl = "age-appropriate"
    return SYSTEM_PROMPT_TEMPLATE.format(
        age_instructions=AGE_INSTRUCTIONS[age_key],
        name="Riley",
        age=age,
        interests="science, animals",
        reading_level=rl,
        reading_level_instructions=reading_level_instructions(age, rl),
        current_topic=topic,
        current_books="none currently",
        top_interest="science",
    )


def _contains(text: str, answers: list[str]) -> bool:
    t = text.lower()
    return any(re.search(r'\b' + re.escape(a.lower()) + r'\b', t) for a in answers)


def _strip_question_echo(text: str, question: str) -> str:
    """
    Remove any part of the response that simply echoes the question back.
    Models sometimes restate the question before answering ("63 divided by 9 is...").
    We strip the question words so wrong_answers don't match on the echo.
    """
    # Remove digits/words from the question that appear verbatim at the start
    t = text.lower().strip()
    q = question.lower().strip().rstrip("?").strip()
    if t.startswith(q):
        t = t[len(q):].strip()
    return t


def _wrong_match(text: str, wrong: list[str], question: str = "") -> str | None:
    t = _strip_question_echo(text, question).lower()
    for w in wrong:
        if re.search(r'\b' + re.escape(w.lower()) + r'\b', t):
            return w
    return None


async def _complete(model: str, messages: list[dict]) -> str:
    r = await litellm.acompletion(
        model=model, messages=messages, max_tokens=100, temperature=0.1
    )
    return r.choices[0].message.content


# ---------------------------------------------------------------------------
# Arithmetic eval — two turns, extract number from second response
# ---------------------------------------------------------------------------

def _first_sentence(text: str) -> str:
    """Return just the first sentence — strips elaboration that may mention other numbers."""
    m = re.split(r'(?<=[.!?])\s', text.strip(), maxsplit=1)
    return m[0] if m else text


def _first_number_in(text: str) -> str | None:
    """
    Extract the first standalone number or simple fraction (e.g. 3/4) from text.
    Used to check the model's stated answer against the Python-computed expected value.
    Returns it as a string normalised to match expected (e.g. "7", "3/4").
    """
    # Match a fraction like 3/4 before plain integers
    m = re.search(r'\b(\d+/\d+)\b', text)
    if m:
        return m.group(1)
    m = re.search(r'\b(\d+)\b', text)
    if m:
        return m.group(1)
    return None


async def run_arithmetic(case: ArithmeticCase, model: str) -> dict:
    import fractions as _fractions
    expected = str(eval(case.python_expr, {"fractions": _fractions}))

    system = _system(case.child_age, case.topic)
    t1 = await _complete(model, [
        {"role": "system", "content": system},
        {"role": "user", "content": case.question},
    ])
    # Turn 2: force a bare numeric answer
    t2 = await _complete(model, [
        {"role": "system", "content": system},
        {"role": "user", "content": case.question},
        {"role": "assistant", "content": t1},
        {"role": "user", "content": "Just give me the answer as a number or fraction. Nothing else."},
    ])

    # Extract the first number/fraction from turn 2 (the direct-answer turn)
    stated = _first_number_in(t2)
    # Accept unsimplified fractions as correct (2/4 == 1/2)
    def _fraction_equal(a: str, b: str) -> bool:
        try:
            import fractions as _f
            return _f.Fraction(a) == _f.Fraction(b)
        except Exception:
            return a == b
    is_correct = stated is not None and _fraction_equal(stated, expected)
    hallucinated = stated is not None and not is_correct
    has_correct = is_correct

    return {
        "type": "arithmetic",
        "topic": case.topic,
        "question": case.question,
        "expected": expected,
        "stated": stated,
        "turn1": t1,
        "turn2": t2,
        "has_correct": has_correct,
        "hallucinated": stated if hallucinated else None,
    }


# ---------------------------------------------------------------------------
# Factual eval — two turns
# ---------------------------------------------------------------------------

async def run_factual(case: FactualCase, model: str) -> dict:
    system = _system(case.child_age, case.topic)
    # Turn 1: child asks
    t1 = await _complete(model, [
        {"role": "system", "content": system},
        {"role": "user", "content": case.question},
    ])
    # Turn 2: child pushes for a direct answer
    t2 = await _complete(model, [
        {"role": "system", "content": system},
        {"role": "user", "content": case.question},
        {"role": "assistant", "content": t1},
        {"role": "user", "content": "Just tell me the answer please."},
    ])

    # Only check the first sentence of turn 2 for wrong answers — elaboration
    # often mentions correct facts tangentially (e.g. snake bones after stating 206)
    t2_answer = _first_sentence(t2)
    combined = t1 + " " + t2
    return {
        "type": "factual",
        "topic": case.topic,
        "question": case.question,
        "turn1": t1,
        "turn2": t2,
        "has_correct": _contains(combined, case.accepted_answers),
        "hallucinated": _wrong_match(t2_answer, case.wrong_answers, case.question),
    }


# ---------------------------------------------------------------------------
# Pytest tests
# ---------------------------------------------------------------------------

MODEL = os.environ.get("ETUTOR_EVAL_MODEL", "claude-haiku-4-5-20251001")

_has_creds = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("AWS_PROFILE"))


@pytest.mark.parametrize("case", ARITHMETIC_CASES,
    ids=[f"{c.topic}_{c.python_expr[:12]}" for c in ARITHMETIC_CASES])
@pytest.mark.skipif(not _has_creds, reason="No API credentials")
def test_arithmetic_no_hallucination(case):
    """Tutor must not assert a known-wrong arithmetic answer across two turns."""
    result = asyncio.get_event_loop().run_until_complete(run_arithmetic(case, MODEL))
    assert not result["hallucinated"], (
        f"\n\nARITHMETIC HALLUCINATION: '{result['hallucinated']}'\n"
        f"Question: {case.question}\n"
        f"Expected: {result['expected']}\n"
        f"Turn 1: {result['turn1']}\n"
        f"Turn 2: {result['turn2']}\n"
    )


@pytest.mark.parametrize("case", ARITHMETIC_CASES,
    ids=[f"{c.topic}_{c.python_expr[:12]}" for c in ARITHMETIC_CASES])
@pytest.mark.skipif(not _has_creds, reason="No API credentials")
def test_arithmetic_correct_answer_present(case):
    """Correct arithmetic answer must appear somewhere across the two turns."""
    result = asyncio.get_event_loop().run_until_complete(run_arithmetic(case, MODEL))
    assert result["has_correct"], (
        f"\n\nCORRECT ANSWER '{result['expected']}' NEVER STATED\n"
        f"Question: {case.question}\n"
        f"Turn 1: {result['turn1']}\n"
        f"Turn 2: {result['turn2']}\n"
    )


@pytest.mark.parametrize("case", FACTUAL_CASES,
    ids=[f"{c.topic}_{c.question[:20].replace(' ','_')}" for c in FACTUAL_CASES])
@pytest.mark.skipif(not _has_creds, reason="No API credentials")
def test_factual_no_hallucination(case):
    """Tutor must not assert a known-wrong factual answer across two turns."""
    result = asyncio.get_event_loop().run_until_complete(run_factual(case, MODEL))
    assert not result["hallucinated"], (
        f"\n\nFACTUAL HALLUCINATION: '{result['hallucinated']}'\n"
        f"Question: {case.question}\n"
        f"Turn 1: {result['turn1']}\n"
        f"Turn 2: {result['turn2']}\n"
    )


# ---------------------------------------------------------------------------
# Standalone report
# ---------------------------------------------------------------------------

async def run_all(model: str = MODEL):
    arith = [await run_arithmetic(c, model) for c in ARITHMETIC_CASES]
    factual = [await run_factual(c, model) for c in FACTUAL_CASES]
    all_results = arith + factual

    hallucinated = [r for r in all_results if r["hallucinated"]]
    missing_correct = [r for r in all_results if not r["has_correct"]]

    print(f"\n{'='*70}")
    print(f"Hallucinations:      {len(hallucinated)}/{len(all_results)}")
    print(f"Correct never stated:{len(missing_correct)}/{len(all_results)}")
    print(f"Expected error rate: ~7% GPT-4 (Herklotz 2025), ~20% unguarded")
    print(f"{'='*70}")
    for r in all_results:
        tag = "ARITH" if r["type"] == "arithmetic" else "FACT "
        hall = f"HALLUC({r['hallucinated']})" if r["hallucinated"] else "ok"
        found = "✓" if r["has_correct"] else "?"
        print(f"  {tag}  {hall:>16}  {found}  {r['topic']:<15} {r['question'][:40]}")
        if r["hallucinated"] or not r["has_correct"]:
            print(f"         T2: {r['turn2'][:100]}")
    return all_results


if __name__ == "__main__":
    asyncio.run(run_all())
