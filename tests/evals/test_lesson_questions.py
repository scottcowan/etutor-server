"""
Eval 5: Lesson Question Quality by Age Group
=============================================
Tests that questions asked by the tutor during a lesson are:
  1. Appropriate Bloom's cognitive level for the age group
  2. Vocabulary-calibrated (concrete for 6-7, can introduce one new word for 8-9,
     abstractions/analogies fine for 10-12)
  3. Actually answerable by the child (open-ended, not rhetorical)
  4. Single question per turn (already tested in socratic eval but verified here
     in lesson context)

Age group targets from pedagogy.md:
  Ages 6-7:  Bloom levels 1-2 (Remember, Understand). Concrete language.
  Ages 8-9:  Bloom levels 2-3 (Understand, Apply). Can introduce one new word.
  Ages 10-12: Bloom levels 3-4 (Apply, Analyse). Analogies and hypotheticals welcome.

Run:
    AWS_PROFILE=... pytest tests/evals/test_lesson_questions.py -v
    AWS_PROFILE=... python tests/evals/test_lesson_questions.py
"""

import asyncio
import os
import re
import pytest
import litellm
from dataclasses import dataclass
from services.tutor import AGE_INSTRUCTIONS, SYSTEM_PROMPT_TEMPLATE, reading_level_instructions


# ---------------------------------------------------------------------------
# Lesson scenarios: simulate a mid-lesson exchange and extract the tutor's
# question from the response.
# ---------------------------------------------------------------------------

@dataclass
class LessonScenario:
    age: int
    reading_level: str
    topic: str
    # The last thing the child said — a correct-ish answer that should prompt
    # the tutor to ask a follow-up question at the right Bloom level
    child_answer: str
    # What Bloom levels are acceptable for this age group
    min_bloom: int   # 1=Remember 2=Understand 3=Apply 4=Analyse 5=Evaluate 6=Create
    max_bloom: int
    description: str


SCENARIOS = [
    # --- Ages 6-7 ---
    LessonScenario(
        age=6, reading_level="grade 1",
        topic="animals",
        child_answer="Dogs have four legs",
        min_bloom=1, max_bloom=2,
        description="Age 6 animals — should ask a simple recall or recognition question",
    ),
    LessonScenario(
        age=7, reading_level="grade 2",
        topic="weather",
        child_answer="Rain comes from clouds",
        min_bloom=1, max_bloom=2,
        description="Age 7 weather — should stay at remember/understand",
    ),
    LessonScenario(
        age=6, reading_level="grade 1",
        topic="counting",
        child_answer="Five plus three is eight",
        min_bloom=1, max_bloom=3,
        description="Age 6 maths — concrete question, can reach Apply (show/count)",
    ),

    # --- Ages 8-9 ---
    LessonScenario(
        age=8, reading_level="grade 3",
        topic="volcanoes",
        child_answer="Magma is melted rock underground",
        min_bloom=2, max_bloom=3,
        description="Age 8 science — should ask what or why, can introduce one term",
    ),
    LessonScenario(
        age=9, reading_level="grade 4",
        topic="fractions",
        child_answer="A half is bigger than a quarter",
        min_bloom=2, max_bloom=3,
        description="Age 9 maths — should apply understanding to a new situation",
    ),
    LessonScenario(
        age=8, reading_level="grade 3",
        topic="history",
        child_answer="Ancient Egyptians built pyramids",
        min_bloom=2, max_bloom=3,
        description="Age 8 history — should ask why or what happened, not how to evaluate",
    ),

    # --- Ages 10-12 ---
    LessonScenario(
        age=10, reading_level="grade 5",
        topic="ecosystems",
        child_answer="Plants make food using sunlight",
        min_bloom=3, max_bloom=4,
        description="Age 10 science — should push to apply or analyse",
    ),
    LessonScenario(
        age=11, reading_level="grade 6",
        topic="electricity",
        child_answer="Electrons flow through a circuit",
        min_bloom=3, max_bloom=5,
        description="Age 11 physics — can use analogies and hypotheticals",
    ),
    LessonScenario(
        age=12, reading_level="grade 7",
        topic="democracy",
        child_answer="People vote to choose their leaders",
        min_bloom=4, max_bloom=6,
        description="Age 12 civics — should push to analyse or evaluate",
    ),
    LessonScenario(
        age=10, reading_level="grade 5",
        topic="water cycle",
        child_answer="Water evaporates from the ocean and forms clouds",
        min_bloom=3, max_bloom=5,
        description="Age 10 geography — apply/analyse, can use hypotheticals",
    ),
]


# ---------------------------------------------------------------------------
# Bloom's level classifier — asks Claude to judge the question's cognitive level
# Uses a separate system prompt so it's a distinct judge, not the tutor judging itself
# ---------------------------------------------------------------------------

BLOOM_JUDGE_SYSTEM = """
You are an educational psychologist classifying questions by Bloom's Taxonomy level.

Bloom's levels:
1 - Remember: recall facts ("What is...", "Name...", "When did...")
2 - Understand: explain in own words, summarise ("Why does...", "What does ... mean", "Can you explain...")
3 - Apply: use knowledge in a new situation ("What would happen if...", "How would you use...", "Can you show me...")
4 - Analyse: break down, find patterns, compare ("Why do you think...", "What is the difference between...", "How does ... affect...")
5 - Evaluate: judge, justify, argue ("Do you agree...", "Which is better...", "Is it fair that...")
6 - Create: produce something new ("Can you make up...", "Design a...", "What if you could...")

Reply with ONLY a JSON object: {"level": <1-6>, "reason": "<one sentence>"}
""".strip()


async def classify_bloom(question: str, model: str) -> dict:
    r = await litellm.acompletion(
        model=model,
        messages=[
            {"role": "system", "content": BLOOM_JUDGE_SYSTEM},
            {"role": "user", "content": f'Classify this question: "{question}"'},
        ],
        max_tokens=80,
        temperature=0.0,
    )
    text = r.choices[0].message.content.strip()
    m = re.search(r'\{[^}]+\}', text, re.DOTALL)
    if m:
        import json
        try:
            return json.loads(m.group())
        except Exception:
            pass
    # Fallback: extract just the number
    num = re.search(r'"level"\s*:\s*(\d)', text)
    return {"level": int(num.group(1)) if num else 0, "reason": text}


# ---------------------------------------------------------------------------
# Concrete language checker — detects abstractions inappropriate for ages 6-7
# ---------------------------------------------------------------------------

ABSTRACT_TERMS = [
    r'\btemperature\b', r'\bcentigrade\b', r'\bcelsius\b', r'\bdegrees?\b',
    r'\bhypothes\w+\b', r'\bphilosoph\w+\b', r'\babstract\b', r'\bconceptual\b',
    r'\bimplication\b', r'\bconsequence\b', r'\bsignificance\b',
    r'\bcharacteristic\b', r'\battribute\b', r'\bproportion\b',
    r'\btheoretical\b', r'\bsystematic\b', r'\banalysis\b',
]

CONCRETE_VIOLATION_MAX_AGE = 7


def has_abstract_language(text: str) -> list[str]:
    """Returns list of abstract terms found. Empty = ok."""
    found = []
    t = text.lower()
    for pattern in ABSTRACT_TERMS:
        if re.search(pattern, t):
            found.append(pattern.strip(r'\b'))
    return found


def count_unfamiliar_words(text: str, age: int, topic: str = "") -> int:
    """
    Counts genuinely technical/academic words not appropriate for the age group.
    Only flags words over 10 characters that aren't in a broad common-words list.
    Ages 6-7: limit 0. Ages 8-9: limit 1.
    """
    if age >= 10:
        return 0  # no restriction for 10-12 — full vocabulary is expected

    words = re.findall(r'\b[a-z]{11,}\b', text.lower())  # 11+ chars = genuinely unusual

    # Broad list of long-but-common English words
    common_long = {
        "something", "everything", "sometimes", "different", "questions",
        "remember", "important", "happening", "beautiful", "wonderful",
        "interesting", "understand", "favourite", "everybody", "afternoon",
        "yesterday", "alongside", "carefully", "correctly", "describes",
        "comparing", "connected", "materials", "perfectly", "themselves",
        "themselves", "comfortable", "information", "communicate",
        "underground", "temperature", "immediately", "underground",
        "together", "completely", "underneath", "impossible", "themselves",
        "electricity", "imagination",
    }

    topic_root = re.sub(r'\s+', '', topic.lower())[:8]
    return sum(1 for w in words
               if w not in common_long and not w.startswith(topic_root))


# ---------------------------------------------------------------------------
# Whether the question is open (has a real answer) vs rhetorical
# Simple heuristic: question mark present + not a yes/no trap
# ---------------------------------------------------------------------------

def is_answerable_question(text: str) -> bool:
    """
    Returns True if the response contains a genuine question the child can answer.
    Checks the last question in the response (not just the last sentence, which
    may be a statement after the question).
    """
    questions = [s.strip() for s in re.split(r'(?<=[.!?])\s', text) if s.strip().endswith('?')]
    if not questions:
        return False
    last_q = questions[-1].lower()
    # Wh-questions, modal questions, and think/guess invitations are all answerable
    answerable_patterns = [
        r'^what\b', r'^why\b', r'^how\b', r'^which\b', r'^who\b',
        r'^where\b', r'^when\b', r'^can you\b', r'^do you\b',
        r'^have you\b', r'^would you\b', r'^could you\b',
        r'^do you think\b', r'^what do you\b', r'^what do you think\b',
        r'^if you\b', r'^if a\b', r'^if the\b',
        r"^here'?s a question", r'^here is a question',
        r"^here'?s something", r'^here is something',
        r'think .{0,40}\?$',
        r'\bfast or slow\b', r'\byes or no\b', r'\bor\b.{0,30}\?$',
        r'\bbigger\b.{0,10}\?$', r'\bsmaller\b.{0,10}\?$',
    ]
    return any(re.search(p, last_q) for p in answerable_patterns)


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------

def _build_system(scenario: LessonScenario) -> str:
    age_key = "under_8" if scenario.age < 8 else "8_plus"
    rl = scenario.reading_level
    return SYSTEM_PROMPT_TEMPLATE.format(
        age_instructions=AGE_INSTRUCTIONS[age_key],
        name="Jamie",
        age=scenario.age,
        interests="nature, stories, Lego",
        reading_level=rl,
        reading_level_instructions=reading_level_instructions(scenario.age, rl),
        current_topic=scenario.topic,
        current_books="none currently",
        top_interest="nature",
    )


async def run_scenario(scenario: LessonScenario, model: str) -> dict:
    system = _build_system(scenario)
    # Simulate mid-lesson: tutor asked something, child gave a correct answer,
    # tutor should now ask the next question
    setup = f"Good. {scenario.child_answer}."
    r = await litellm.acompletion(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": setup},
        ],
        max_tokens=120,
        temperature=0.3,
    )
    response = r.choices[0].message.content

    # Extract just the question portion for Bloom classification
    questions = [s.strip() for s in re.split(r'(?<=[.!?])\s', response) if s.strip().endswith('?')]
    question_text = questions[-1] if questions else response

    bloom = await classify_bloom(question_text, model)
    abstract_violations = has_abstract_language(response) if scenario.age <= 7 else []
    unfamiliar_count = count_unfamiliar_words(response, scenario.age, scenario.topic)
    unfamiliar_limit = 0 if scenario.age <= 7 else 1

    return {
        "description": scenario.description,
        "age": scenario.age,
        "topic": scenario.topic,
        "response": response,
        "question": question_text,
        "bloom_level": bloom.get("level", 0),
        "bloom_reason": bloom.get("reason", ""),
        "bloom_in_range": scenario.min_bloom <= bloom.get("level", 0) <= scenario.max_bloom,
        "min_bloom": scenario.min_bloom,
        "max_bloom": scenario.max_bloom,
        "abstract_violations": abstract_violations,
        "unfamiliar_count": unfamiliar_count,
        "unfamiliar_ok": unfamiliar_count <= unfamiliar_limit,
        "is_answerable": is_answerable_question(response),
    }


# ---------------------------------------------------------------------------
# Pytest tests
# ---------------------------------------------------------------------------

from eval_helpers import requires_llm, MODEL


@pytest.mark.parametrize("scenario", SCENARIOS,
    ids=[f"age{s.age}_{s.topic}" for s in SCENARIOS])
@requires_llm
def test_bloom_level_appropriate(scenario):
    """Tutor question must be at the right Bloom level for the age group."""
    result = asyncio.get_event_loop().run_until_complete(run_scenario(scenario, MODEL))
    assert result["bloom_in_range"], (
        f"\n\nBLOOM LEVEL WRONG for age {scenario.age} — got {result['bloom_level']}, "
        f"expected {scenario.min_bloom}–{scenario.max_bloom}\n"
        f"Scenario: {scenario.description}\n"
        f"Question asked: {result['question']}\n"
        f"Reason: {result['bloom_reason']}\n"
    )


@pytest.mark.parametrize("scenario", [s for s in SCENARIOS if s.age <= 7],
    ids=[f"age{s.age}_{s.topic}" for s in SCENARIOS if s.age <= 7])
@requires_llm
def test_no_abstract_language_ages_6_7(scenario):
    """Ages 6-7: no abstract/technical vocabulary."""
    result = asyncio.get_event_loop().run_until_complete(run_scenario(scenario, MODEL))
    assert not result["abstract_violations"], (
        f"\n\nABSTRACT LANGUAGE for age {scenario.age}: {result['abstract_violations']}\n"
        f"Response: {result['response']}\n"
    )


@pytest.mark.parametrize("scenario", [s for s in SCENARIOS if s.age <= 9],
    ids=[f"age{s.age}_{s.topic}" for s in SCENARIOS if s.age <= 9])
@requires_llm
def test_vocabulary_not_overwhelming(scenario):
    """Ages 6-7 allow 0 unfamiliar long words; ages 8-9 allow 1."""
    result = asyncio.get_event_loop().run_until_complete(run_scenario(scenario, MODEL))
    limit = 0 if scenario.age <= 7 else 1
    assert result["unfamiliar_count"] <= limit, (
        f"\n\nTOO MANY UNFAMILIAR WORDS for age {scenario.age}: "
        f"{result['unfamiliar_count']} (limit {limit})\n"
        f"Response: {result['response']}\n"
    )


@pytest.mark.parametrize("scenario", SCENARIOS,
    ids=[f"age{s.age}_{s.topic}" for s in SCENARIOS])
@requires_llm
def test_question_is_answerable(scenario):
    """Tutor must end with a genuine open question the child can answer."""
    result = asyncio.get_event_loop().run_until_complete(run_scenario(scenario, MODEL))
    assert result["is_answerable"], (
        f"\n\nNO ANSWERABLE QUESTION for age {scenario.age}, topic '{scenario.topic}'\n"
        f"Response: {result['response']}\n"
    )


# ---------------------------------------------------------------------------
# Standalone report
# ---------------------------------------------------------------------------

async def run_all(model: str = MODEL):
    results = [await run_scenario(s, model) for s in SCENARIOS]

    print(f"\n{'='*80}")
    print(f"{'Scenario':<35} {'Age':>3}  {'Bloom':>5}  {'Range':>9}  {'Vocab':>5}  {'Open?':>5}")
    print(f"{'-'*80}")

    bloom_fails = 0
    vocab_fails = 0
    open_fails = 0

    for r in results:
        bloom_ok = "✓" if r["bloom_in_range"] else f"✗({r['bloom_level']})"
        vocab_ok = "✓" if r["unfamiliar_ok"] else f"✗({r['unfamiliar_count']})"
        open_ok = "✓" if r["is_answerable"] else "✗"
        bloom_range = f"{r['min_bloom']}–{r['max_bloom']}"

        if not r["bloom_in_range"]: bloom_fails += 1
        if not r["unfamiliar_ok"]: vocab_fails += 1
        if not r["is_answerable"]: open_fails += 1

        print(f"  {r['description'][:33]:<35} {r['age']:>3}  "
              f"{bloom_ok:>5}  {bloom_range:>9}  {vocab_ok:>5}  {open_ok:>5}")

        if not r["bloom_in_range"]:
            print(f"    Question: {r['question']}")
            print(f"    Reason:   {r['bloom_reason']}")

    total = len(results)
    print(f"\nPASS RATES:  bloom {total-bloom_fails}/{total}  "
          f"vocab {total-vocab_fails}/{total}  answerable {total-open_fails}/{total}")
    return results


if __name__ == "__main__":
    asyncio.run(run_all())
