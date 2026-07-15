"""
Eval 2: Socratic Quality
=========================
Measures whether the tutor responds with a question (Socratic) rather than
a statement (direct instruction) when the child hasn't attempted yet.

This checks the "Socratic First" principle from pedagogy.md §Interaction Design.

Also checks:
- One question per turn (not two)
- No sycophantic openers ("Great!", "Amazing!", "Well done!")
- Response length is age-appropriate

Run:
    ANTHROPIC_API_KEY=... pytest tests/evals/test_socratic_quality.py -v
"""

import asyncio
import os
import re
import pytest
import litellm
from dataclasses import dataclass
from services.tutor import AGE_INSTRUCTIONS, SYSTEM_PROMPT_TEMPLATE


@dataclass
class SocraticCase:
    topic: str
    child_age: int
    child_message: str       # what the child says to open a topic
    description: str         # what we're testing


CASES = [
    SocraticCase(
        topic="volcanoes",
        child_age=8,
        child_message="I want to learn about volcanoes",
        description="Topic opening — tutor should probe, not lecture",
    ),
    SocraticCase(
        topic="photosynthesis",
        child_age=10,
        child_message="What is photosynthesis?",
        description="Direct question — tutor should ask what child already knows",
    ),
    SocraticCase(
        topic="fractions",
        child_age=9,
        child_message="I don't get fractions",
        description="Confusion statement — tutor should diagnose before explaining",
    ),
    SocraticCase(
        topic="space",
        child_age=7,
        child_message="Tell me about planets",
        description="Open request — tutor should engage curiosity not monologue",
    ),
    SocraticCase(
        topic="animals",
        child_age=6,
        child_message="What's the biggest animal?",
        description="Factual question — tutor should invite a guess first",
    ),
    SocraticCase(
        topic="history",
        child_age=11,
        child_message="Who was Julius Caesar?",
        description="Historical person question — probe prior knowledge",
    ),
    SocraticCase(
        topic="multiplication",
        child_age=9,
        child_message="Can you teach me times tables?",
        description="Skill request — should assess current level first",
    ),
    SocraticCase(
        topic="electricity",
        child_age=10,
        child_message="How does electricity work?",
        description="Mechanism question — should invite prior model",
    ),
]

SYCOPHANTIC_OPENERS = [
    r'\bgreat\b',
    r'\bamazing\b',
    r'\bwonderful\b',
    r'\bfantastic\b',
    r'\bexcellent\b',
    r'\bawesome\b',
    r'\bwell done\b',
    r'\bsuperb\b',
    r'\bperfect\b',
    r'good (job|work|answer|question)',
]


def build_prompt(case: SocraticCase) -> list[dict]:
    from services.tutor import reading_level_instructions as rli
    age_key = "under_8" if case.child_age < 8 else "8_plus"
    rl = "age-appropriate"
    system = SYSTEM_PROMPT_TEMPLATE.format(
        age_instructions=AGE_INSTRUCTIONS[age_key],
        name="Sam",
        age=case.child_age,
        interests="space, Lego",
        reading_level=rl,
        reading_level_instructions=rli(case.child_age, rl),
        current_topic=case.topic,
        current_books="none currently",
        top_interest="space",
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": case.child_message},
    ]


def count_questions(text: str) -> int:
    return text.count("?")


def ends_with_question(text: str) -> bool:
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    if not sentences:
        return False
    last = text.rstrip()
    return last.endswith("?")


def has_sycophantic_opener(text: str) -> bool:
    first_sentence = re.split(r'[.!?]', text)[0].lower()
    return any(re.search(p, first_sentence) for p in SYCOPHANTIC_OPENERS)


def word_count(text: str) -> int:
    return len(text.split())


def age_appropriate_length(text: str, age: int) -> bool:
    wc = word_count(text)
    if age <= 7:
        return wc <= 40    # 2 short sentences
    elif age <= 9:
        return wc <= 60    # 3 sentences
    else:
        return wc <= 100   # short paragraph


async def run_case(case: SocraticCase, model: str) -> dict:
    messages = build_prompt(case)
    response = await litellm.acompletion(
        model=model,
        messages=messages,
        max_tokens=200,
        temperature=0.3,
    )
    content = response.choices[0].message.content
    return {
        "topic": case.topic,
        "age": case.child_age,
        "description": case.description,
        "response": content,
        "ends_with_question": ends_with_question(content),
        "question_count": count_questions(content),
        "sycophantic": has_sycophantic_opener(content),
        "length_ok": age_appropriate_length(content, case.child_age),
        "word_count": word_count(content),
    }


READING_LEVEL_CASES = [
    # (age, reading_level, topic, question, max_words_per_sentence, description)
    (6, "grade 1", "animals", "What do elephants eat?", 8, "Grade 1 — short sentences"),
    (8, "grade 3", "volcanoes", "How does a volcano work?", 12, "Grade 3 — medium sentences"),
    (11, "grade 6", "ecosystems", "Why do food chains matter?", 20, "Grade 6 — complex sentences ok"),
]


def max_sentence_length(text: str) -> int:
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
    if not sentences:
        return 0
    return max(len(s.split()) for s in sentences)


from eval_helpers import requires_llm, MODEL


@pytest.mark.parametrize("case", CASES, ids=[c.topic + "_age" + str(c.child_age) for c in CASES])
@requires_llm
def test_ends_with_question(case):
    """Tutor should end its turn with a question — Socratic first principle."""
    result = asyncio.get_event_loop().run_until_complete(run_case(case, MODEL))
    assert result["ends_with_question"], (
        f"\n\nNO QUESTION on topic='{case.topic}'\n"
        f"Scenario: {case.description}\n"
        f"Child said: '{case.child_message}'\n"
        f"Tutor responded: {result['response']}\n"
    )


@pytest.mark.parametrize("case", CASES, ids=[c.topic + "_age" + str(c.child_age) for c in CASES])
@requires_llm
def test_one_question_per_turn(case):
    """Tutor must ask exactly one question per turn — never two."""
    result = asyncio.get_event_loop().run_until_complete(run_case(case, MODEL))
    assert result["question_count"] <= 1, (
        f"\n\nMULTIPLE QUESTIONS ({result['question_count']}) on topic='{case.topic}'\n"
        f"Tutor responded: {result['response']}\n"
    )


@pytest.mark.parametrize("case", CASES, ids=[c.topic + "_age" + str(c.child_age) for c in CASES])
@requires_llm
def test_no_sycophancy(case):
    """Tutor must not open with hollow praise."""
    result = asyncio.get_event_loop().run_until_complete(run_case(case, MODEL))
    assert not result["sycophantic"], (
        f"\n\nSYCOPHANTIC OPENER on topic='{case.topic}'\n"
        f"Tutor responded: {result['response']}\n"
    )


@pytest.mark.parametrize("case", CASES, ids=[c.topic + "_age" + str(c.child_age) for c in CASES])
@requires_llm
def test_age_appropriate_length(case):
    """Tutor response length must match the age group limits from pedagogy.md."""
    result = asyncio.get_event_loop().run_until_complete(run_case(case, MODEL))
    assert result["length_ok"], (
        f"\n\nRESPONSE TOO LONG for age {case.age}: {result['word_count']} words\n"
        f"Topic: '{case.topic}'\n"
        f"Tutor responded: {result['response']}\n"
    )


@pytest.mark.parametrize(
    "age,reading_level,topic,question,max_sent_words,desc",
    READING_LEVEL_CASES,
    ids=[c[5] for c in READING_LEVEL_CASES],
)
@requires_llm
def test_reading_level_sentence_length(age, reading_level, topic, question, max_sent_words, desc):
    """Sentences must stay within the grade-level word-count ceiling."""
    from services.tutor import reading_level_instructions, SYSTEM_PROMPT_TEMPLATE, AGE_INSTRUCTIONS
    age_key = "under_8" if age < 8 else "8_plus"
    system = SYSTEM_PROMPT_TEMPLATE.format(
        age_instructions=AGE_INSTRUCTIONS[age_key],
        name="Casey",
        age=age,
        interests="animals, drawing",
        reading_level=reading_level,
        reading_level_instructions=reading_level_instructions(age, reading_level),
        current_topic=topic,
        current_books="none currently",
        top_interest="animals",
    )
    messages = [{"role": "system", "content": system}, {"role": "user", "content": question}]

    async def _run():
        r = await litellm.acompletion(model=MODEL, messages=messages, max_tokens=150, temperature=0.3)
        return r.choices[0].message.content

    response = asyncio.get_event_loop().run_until_complete(_run())
    longest = max_sentence_length(response)
    assert longest <= max_sent_words + 2, (  # +2 word tolerance
        f"\n\nSENTENCE TOO LONG for {reading_level} (max {max_sent_words} words)\n"
        f"Longest sentence: {longest} words\n"
        f"Response: {response}\n"
    )


async def run_all(model: str = MODEL):
    results = [await run_case(c, model) for c in CASES]
    dims = ["ends_with_question", "question_count", "sycophantic", "length_ok"]
    print(f"\n{'='*70}")
    print(f"{'Topic':<20} {'Age':>3}  {'?':>3}  {'Qs':>3}  {'Syco':>5}  {'Len':>5}  Words")
    print(f"{'-'*70}")
    for r in results:
        ok_q = "✓" if r["ends_with_question"] else "✗"
        ok_n = str(r["question_count"])
        ok_s = "✗" if r["sycophantic"] else "✓"
        ok_l = "✓" if r["length_ok"] else "✗"
        print(f"  {r['topic']:<18} {r['age']:>3}  {ok_q:>3}  {ok_n:>3}  {ok_s:>5}  {ok_l:>5}  {r['word_count']}")
    total = len(results)
    pass_q = sum(1 for r in results if r["ends_with_question"])
    pass_1 = sum(1 for r in results if r["question_count"] <= 1)
    pass_s = sum(1 for r in results if not r["sycophantic"])
    pass_l = sum(1 for r in results if r["length_ok"])
    print(f"\nPASS RATES:  ends-with-? {pass_q}/{total}  one-? {pass_1}/{total}  no-syco {pass_s}/{total}  length {pass_l}/{total}")
    return results


if __name__ == "__main__":
    asyncio.run(run_all())
