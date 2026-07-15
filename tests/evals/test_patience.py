"""
Eval 8: Patience and Re-explanation
=====================================
Measures whether the tutor handles repeated re-explanation requests with
genuine patience — different words and a new analogy each time — rather than
showing frustration, repeating itself verbatim, or saying "we already covered this".

The system prompt now says:
  "If the child asks you to explain something again, do so with different words
   and a new analogy every single time. Never say 'we already covered this'.
   The twentieth explanation is as welcome as the first."

Two gates:
1. PATIENCE gate: tutor must not say "we already covered", "I just said",
   "as I explained", "like I mentioned", or similar impatient phrases.
2. VARIATION gate: across two re-explanation requests, the responses must not
   be near-verbatim repetitions of each other (checked via word overlap).

Run:
    ANTHROPIC_API_KEY=... pytest tests/evals/test_patience.py -v
"""

import asyncio
import os
import re
import pytest
import litellm
from dataclasses import dataclass
from services.tutor import AGE_INSTRUCTIONS, SYSTEM_PROMPT_TEMPLATE


@dataclass
class PatienceCase:
    topic: str
    child_age: int
    concept: str              # what the tutor explained
    first_explanation: str    # the tutor's first explanation (simulated)
    re_request: str           # how the child asks again


CASES = [
    PatienceCase(
        topic="multiplication",
        child_age=9,
        concept="what multiplication means",
        first_explanation="Multiplication is a quick way of adding the same number lots of times. So 3 times 4 means adding 3 four times: 3 + 3 + 3 + 3 = 12.",
        re_request="I still don't understand, can you explain it again?",
    ),
    PatienceCase(
        topic="fractions",
        child_age=10,
        concept="what a denominator is",
        first_explanation="The denominator is the bottom number in a fraction. It tells you how many equal parts the whole is divided into.",
        re_request="Sorry, I'm confused. Can you explain denominator again differently?",
    ),
    PatienceCase(
        topic="photosynthesis",
        child_age=11,
        concept="why plants need sunlight",
        first_explanation="Plants use sunlight as an energy source to power a chemical reaction that turns water and carbon dioxide into sugar — their food.",
        re_request="I don't get it. Can you tell me again why they need light?",
    ),
    PatienceCase(
        topic="electricity",
        child_age=8,
        concept="what a circuit is",
        first_explanation="A circuit is a complete loop that electricity can travel around. If there's a gap anywhere, the electricity stops and the light goes off.",
        re_request="Can you explain circuit again? I forgot",
    ),
    PatienceCase(
        topic="gravity",
        child_age=12,
        concept="why the moon doesn't fall into Earth",
        first_explanation="The moon is moving sideways so fast that as it falls toward Earth, Earth curves away underneath it — so it keeps falling but never hits.",
        re_request="Wait, I still don't understand. Say it again but differently?",
    ),
]

# Phrases that indicate impatience or unhelpful repetition
IMPATIENCE_PHRASES = [
    "we already covered",
    "i just explained",
    "as i explained",
    "like i said",
    "like i mentioned",
    "i already told you",
    "we went over",
    "as we discussed",
    "i just told you",
    "remember, i said",
]


def build_system(case: PatienceCase) -> str:
    age_key = "under_8" if case.child_age < 8 else "8_plus"
    return SYSTEM_PROMPT_TEMPLATE.format(
        age_instructions=AGE_INSTRUCTIONS[age_key],
        name="Casey",
        age=case.child_age,
        interests="football, video games",
        reading_level="age-appropriate",
        current_topic=case.topic,
        current_books="none currently",
        top_interest="football",
    )


def shows_impatience(text: str) -> bool:
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in IMPATIENCE_PHRASES)


def word_overlap_ratio(text1: str, text2: str) -> float:
    """Jaccard similarity of word sets — 1.0 = identical, 0.0 = no shared words."""
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)


async def run_case(case: PatienceCase, model: str) -> dict:
    system = build_system(case)

    # Turn 1: tutor gives first explanation (simulated)
    # Turn 2: child says they still don't understand
    # Turn 3: tutor re-explains (this is what we test)
    messages_first = [
        {"role": "system", "content": system},
        {"role": "assistant", "content": case.first_explanation},
        {"role": "user", "content": case.re_request},
    ]
    r1 = await litellm.acompletion(
        model=model, messages=messages_first, max_tokens=200, temperature=0.4,
    )
    re_explain_1 = r1.choices[0].message.content

    # Turn 4: child asks a THIRD time (testing patience on second re-request)
    messages_second = messages_first + [
        {"role": "assistant", "content": re_explain_1},
        {"role": "user", "content": "I'm sorry, I still don't get it. One more time please?"},
    ]
    r2 = await litellm.acompletion(
        model=model, messages=messages_second, max_tokens=200, temperature=0.4,
    )
    re_explain_2 = r2.choices[0].message.content

    overlap = word_overlap_ratio(re_explain_1, re_explain_2)
    impatient_1 = shows_impatience(re_explain_1)
    impatient_2 = shows_impatience(re_explain_2)

    return {
        "topic": case.topic,
        "age": case.child_age,
        "re_explain_1": re_explain_1,
        "re_explain_2": re_explain_2,
        "impatient_1": impatient_1,
        "impatient_2": impatient_2,
        "word_overlap": overlap,
        # >0.7 overlap = essentially the same explanation = FAIL variation gate
        "too_similar": overlap > 0.7,
    }


MODEL = os.environ.get("ETUTOR_EVAL_MODEL", "claude-haiku-4-5-20251001")


@pytest.mark.parametrize("case", CASES, ids=[c.topic for c in CASES])
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping live eval"
)
def test_no_impatience_on_first_reexplain(case):
    """Tutor must not show impatience when child asks for a re-explanation."""
    result = asyncio.get_event_loop().run_until_complete(run_case(case, MODEL))
    assert not result["impatient_1"], (
        f"\n\nIMPATIENCE on first re-explain, topic='{case.topic}'\n"
        f"Tutor said: {result['re_explain_1']}\n"
    )


@pytest.mark.parametrize("case", CASES, ids=[c.topic for c in CASES])
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping live eval"
)
def test_no_impatience_on_second_reexplain(case):
    """Tutor must not show impatience on the second re-explanation request either."""
    result = asyncio.get_event_loop().run_until_complete(run_case(case, MODEL))
    assert not result["impatient_2"], (
        f"\n\nIMPATIENCE on second re-explain, topic='{case.topic}'\n"
        f"Tutor said: {result['re_explain_2']}\n"
    )


@pytest.mark.parametrize("case", CASES, ids=[c.topic for c in CASES])
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping live eval"
)
def test_varied_reexplanation(case):
    """Two re-explanations of the same concept should not be near-verbatim copies."""
    result = asyncio.get_event_loop().run_until_complete(run_case(case, MODEL))
    assert not result["too_similar"], (
        f"\n\nREPETITIVE RE-EXPLANATION on topic='{case.topic}'\n"
        f"Word overlap: {result['word_overlap']:.2f} (threshold: 0.70)\n"
        f"First re-explain: {result['re_explain_1']}\n"
        f"Second re-explain: {result['re_explain_2']}\n"
    )


async def run_all(model: str = MODEL):
    results = [await run_case(c, model) for c in CASES]
    print(f"\n{'='*70}")
    print(f"{'Topic':<20}  Impatient-1  Impatient-2  Overlap  Varied")
    print(f"{'-'*70}")
    for r in results:
        i1 = "IMP" if r["impatient_1"] else "ok "
        i2 = "IMP" if r["impatient_2"] else "ok "
        sim = "SAME" if r["too_similar"] else "ok  "
        overlap = f"{r['word_overlap']:.2f}"
        print(f"  {r['topic']:<18}  {i1:>11}  {i2:>11}  {overlap:>7}  {sim:>6}")
    return results


if __name__ == "__main__":
    asyncio.run(run_all())
