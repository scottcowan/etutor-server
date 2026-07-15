"""
Eval 3: Hint Ladder
====================
Tests that the tutor escalates through the 3-level hint ladder correctly:
  Level 1 (nudge): vague reference to relevant concept, no answer
  Level 2 (hint):  more specific pointer, still no answer
  Level 3 (explain): gives the answer, then asks a simpler related question

Each case simulates a 3-turn exchange where the child is stuck.
We check:
  - Turn 1 after wrong attempt: hint level 1, no answer reveal
  - Turn 2 after "I don't know": hint level 2, still no answer reveal
  - Turn 3 after second "I don't know": gives answer AND asks follow-up question

Based on pedagogy.md §Interaction Design §3 "Hint Ladder" and research finding
that LLMs achieve only 75% hint accuracy (Dey Tithi et al., arXiv:2505.04736).

Run:
    ANTHROPIC_API_KEY=... pytest tests/evals/test_hint_ladder.py -v
"""

import asyncio
import os
import re
import pytest
import litellm
from dataclasses import dataclass, field
from services.tutor import AGE_INSTRUCTIONS, SYSTEM_PROMPT_TEMPLATE


@dataclass
class HintCase:
    topic: str
    child_age: int
    question: str
    wrong_attempt: str
    correct_answer: str


CASES = [
    HintCase(
        topic="multiplication",
        child_age=9,
        question="What is 6 times 7?",
        wrong_attempt="Is it 36?",
        correct_answer="42",
    ),
    HintCase(
        topic="photosynthesis",
        child_age=10,
        question="What gas do plants breathe in to make food?",
        wrong_attempt="Oxygen?",
        correct_answer="carbon dioxide",
    ),
    HintCase(
        topic="capitals",
        child_age=9,
        question="What is the capital of France?",
        wrong_attempt="Is it Lyon?",
        correct_answer="Paris",
    ),
    HintCase(
        topic="fractions",
        child_age=10,
        question="What is a quarter of 20?",
        wrong_attempt="Is it 8?",
        correct_answer="5",
    ),
]


def build_system(case: HintCase) -> str:
    age_key = "under_8" if case.child_age < 8 else "8_plus"
    return SYSTEM_PROMPT_TEMPLATE.format(
        age_instructions=AGE_INSTRUCTIONS[age_key],
        name="Jordan",
        age=case.child_age,
        interests="football, animals",
        reading_level="age-appropriate",
        current_topic=case.topic,
        current_books="none currently",
        top_interest="football",
    )


def contains_answer(text: str, answer: str) -> bool:
    pattern = r'\b' + re.escape(answer.lower()) + r'\b'
    return bool(re.search(pattern, text.lower()))


def ends_with_question(text: str) -> bool:
    return text.rstrip().endswith("?")


async def run_hint_sequence(case: HintCase, model: str) -> dict:
    system = build_system(case)
    history = [{"role": "system", "content": system}]

    # Turn 1: tutor asks question (simulated)
    history.append({"role": "assistant", "content": case.question})

    # Turn 2: child makes wrong attempt
    history.append({"role": "user", "content": case.wrong_attempt})
    r1 = await litellm.acompletion(model=model, messages=history, max_tokens=150, temperature=0.3)
    hint1 = r1.choices[0].message.content
    history.append({"role": "assistant", "content": hint1})

    # Turn 3: child says "I don't know"
    history.append({"role": "user", "content": "I don't know"})
    r2 = await litellm.acompletion(model=model, messages=history, max_tokens=150, temperature=0.3)
    hint2 = r2.choices[0].message.content
    history.append({"role": "assistant", "content": hint2})

    # Turn 4: child says "I still don't know" — tutor should now explain
    history.append({"role": "user", "content": "I still don't know, I give up"})
    r3 = await litellm.acompletion(model=model, messages=history, max_tokens=200, temperature=0.3)
    explain = r3.choices[0].message.content

    return {
        "topic": case.topic,
        "age": case.child_age,
        "hint1": hint1,
        "hint2": hint2,
        "explain": explain,
        "hint1_reveals": contains_answer(hint1, case.correct_answer),
        "hint2_reveals": contains_answer(hint2, case.correct_answer),
        "explain_reveals": contains_answer(explain, case.correct_answer),
        "explain_has_followup": ends_with_question(explain),
    }


from eval_helpers import requires_llm, MODEL


@pytest.mark.parametrize("case", CASES, ids=[c.topic for c in CASES])
@requires_llm
def test_hint1_does_not_reveal(case):
    """First hint after wrong attempt must not give the answer."""
    result = asyncio.get_event_loop().run_until_complete(run_hint_sequence(case, MODEL))
    assert not result["hint1_reveals"], (
        f"\n\nHINT 1 REVEALED ANSWER on topic='{case.topic}'\n"
        f"Correct answer: '{case.correct_answer}'\n"
        f"Tutor hint 1: {result['hint1']}\n"
    )


@pytest.mark.parametrize("case", CASES, ids=[c.topic for c in CASES])
@requires_llm
def test_hint2_does_not_reveal(case):
    """Second hint after 'I don't know' must still not give the answer."""
    result = asyncio.get_event_loop().run_until_complete(run_hint_sequence(case, MODEL))
    assert not result["hint2_reveals"], (
        f"\n\nHINT 2 REVEALED ANSWER on topic='{case.topic}'\n"
        f"Correct answer: '{case.correct_answer}'\n"
        f"Tutor hint 2: {result['hint2']}\n"
    )


@pytest.mark.parametrize("case", CASES, ids=[c.topic for c in CASES])
@requires_llm
def test_explain_reveals_answer(case):
    """After two failed hints, the tutor MUST give the answer (level 3 explain)."""
    result = asyncio.get_event_loop().run_until_complete(run_hint_sequence(case, MODEL))
    assert result["explain_reveals"], (
        f"\n\nEXPLAIN DID NOT GIVE ANSWER on topic='{case.topic}'\n"
        f"Correct answer: '{case.correct_answer}'\n"
        f"Tutor explain: {result['explain']}\n"
    )


@pytest.mark.parametrize("case", CASES, ids=[c.topic for c in CASES])
@requires_llm
def test_explain_has_followup_question(case):
    """After explaining the answer, tutor must ask a simpler follow-up to restore confidence."""
    result = asyncio.get_event_loop().run_until_complete(run_hint_sequence(case, MODEL))
    assert result["explain_has_followup"], (
        f"\n\nNO FOLLOW-UP QUESTION after explain on topic='{case.topic}'\n"
        f"Tutor explain: {result['explain']}\n"
    )


async def run_all(model: str = MODEL):
    results = [await run_hint_sequence(c, model) for c in CASES]
    print(f"\n{'='*70}")
    print(f"{'Topic':<20}  H1-ok  H2-ok  Exp-ok  Followup")
    print(f"{'-'*70}")
    for r in results:
        h1 = "✓" if not r["hint1_reveals"] else "REVEAL"
        h2 = "✓" if not r["hint2_reveals"] else "REVEAL"
        ex = "✓" if r["explain_reveals"] else "MISSING"
        fq = "✓" if r["explain_has_followup"] else "✗"
        print(f"  {r['topic']:<18}  {h1:>6}  {h2:>6}  {ex:>7}  {fq:>7}")
    return results


if __name__ == "__main__":
    asyncio.run(run_all())
