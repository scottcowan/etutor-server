"""
Eval 7: Session-End Hook
=========================
Measures whether the tutor ends a session with an open question rather than
a resolved, closed answer.

The system prompt now says:
  "End every exchange with an open question or unresolved wonder — never
   with a complete explanation and nothing left to answer."
  "At session end, leave one question unanswered that pulls {name} back tomorrow."

Gate: when the child signals session end ("I have to go now", "that's enough
for today"), the tutor's final response MUST end with a question or cliffhanger.
A response that ends with a statement (full stop, no question) is a FAIL.

This is the Primer's cliffhanger mechanic: "just as she was clasping the book
together, new words appeared."

Run:
    ANTHROPIC_API_KEY=... pytest tests/evals/test_session_end_hook.py -v
"""

import asyncio
import os
import pytest
import litellm
from dataclasses import dataclass
from services.tutor import AGE_INSTRUCTIONS, SYSTEM_PROMPT_TEMPLATE


@dataclass
class SessionEndCase:
    topic: str
    child_age: int
    session_content: str    # what the session covered
    end_signal: str         # what the child says to end


CASES = [
    SessionEndCase(
        topic="volcanoes",
        child_age=9,
        session_content="We talked about how lava forms underground and erupts.",
        end_signal="I have to go now, it's dinner time",
    ),
    SessionEndCase(
        topic="fractions",
        child_age=10,
        session_content="We worked on adding fractions with the same denominator.",
        end_signal="That's enough for today, I'm tired",
    ),
    SessionEndCase(
        topic="ancient Egypt",
        child_age=11,
        session_content="We discussed the pharaohs and the building of the pyramids.",
        end_signal="I need to stop, my mum is calling me",
    ),
    SessionEndCase(
        topic="electricity",
        child_age=8,
        session_content="We learned about circuits and switches.",
        end_signal="I have to do my homework now",
    ),
    SessionEndCase(
        topic="ecosystems",
        child_age=12,
        session_content="We explored food chains and what happens when a species disappears.",
        end_signal="OK I think that's enough learning for today",
    ),
]


def build_system(case: SessionEndCase) -> str:
    age_key = "under_8" if case.child_age < 8 else "8_plus"
    return SYSTEM_PROMPT_TEMPLATE.format(
        age_instructions=AGE_INSTRUCTIONS[age_key],
        name="Riley",
        age=case.child_age,
        interests="dinosaurs, space",
        reading_level="age-appropriate",
        current_topic=case.topic,
        current_books="none currently",
        top_interest="dinosaurs",
    )


def ends_with_question(text: str) -> bool:
    """Returns True if the response ends with a question mark."""
    return text.rstrip().endswith("?")


def has_cliffhanger_language(text: str) -> bool:
    """
    Returns True if response contains forward-pull language even without a question mark.
    e.g. "Next time we could explore...", "I wonder what would happen if..."
    """
    cliffhanger_phrases = [
        "next time",
        "next session",
        "tomorrow",
        "i wonder",
        "think about",
        "what if",
        "what do you think",
        "come back",
        "we'll find out",
        "to be continued",
    ]
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in cliffhanger_phrases)


async def run_case(case: SessionEndCase, model: str) -> dict:
    system = build_system(case)
    messages = [
        {"role": "system", "content": system},
        {"role": "assistant", "content": f"Let's talk about {case.topic}. {case.session_content} What did you find most interesting?"},
        {"role": "user", "content": "That was cool! " + case.session_content},
        {"role": "assistant", "content": f"Great exploration today! {case.topic} has so many fascinating layers."},
        {"role": "user", "content": case.end_signal},
    ]
    response = await litellm.acompletion(
        model=model,
        messages=messages,
        max_tokens=200,
        temperature=0.3,
    )
    content = response.choices[0].message.content
    has_hook = ends_with_question(content) or has_cliffhanger_language(content)
    return {
        "topic": case.topic,
        "age": case.child_age,
        "end_signal": case.end_signal,
        "response": content,
        "ends_with_question": ends_with_question(content),
        "has_cliffhanger": has_cliffhanger_language(content),
        "has_hook": has_hook,
    }


MODEL = os.environ.get("ETUTOR_EVAL_MODEL", "claude-haiku-4-5-20251001")


@pytest.mark.parametrize("case", CASES, ids=[c.topic for c in CASES])
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping live eval"
)
def test_session_end_has_hook(case):
    """When child signals session end, tutor must leave a question or cliffhanger to pull them back."""
    result = asyncio.get_event_loop().run_until_complete(run_case(case, MODEL))
    assert result["has_hook"], (
        f"\n\nNO SESSION-END HOOK on topic='{case.topic}'\n"
        f"Child said: '{case.end_signal}'\n"
        f"Tutor responded: {result['response']}\n"
        f"(Tutor should leave an unanswered question or cliffhanger — not just say goodbye)\n"
    )


async def run_all(model: str = MODEL):
    results = [await run_case(c, model) for c in CASES]
    no_hook = [r for r in results if not r["has_hook"]]
    hook_rate = (len(results) - len(no_hook)) / len(results) * 100
    print(f"\n{'='*60}")
    print(f"Session-end hook rate: {hook_rate:.0f}%  ({len(results) - len(no_hook)}/{len(results)} cases)")
    print(f"Target: 100%  (always leave a hook)")
    print(f"{'='*60}")
    for r in results:
        q_mark = "?" if r["ends_with_question"] else " "
        cliff = "C" if r["has_cliffhanger"] else " "
        status = "ok  " if r["has_hook"] else "FAIL"
        print(f"  {status}  [Q:{q_mark} Cliff:{cliff}]  '{r['topic']}'")
        if not r["has_hook"]:
            print(f"    Response: {r['response'][:120]}...")
    return hook_rate, results


if __name__ == "__main__":
    rate, _ = asyncio.run(run_all())
    exit(0 if rate == 100 else 1)
