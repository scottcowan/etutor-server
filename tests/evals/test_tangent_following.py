"""
Eval 6: Tangent Following
==========================
Measures whether the tutor follows a child's tangent rather than redirecting
back to the stated topic ("We were just talking about X — let's get back to that").

The new system prompt says:
  "When they follow a tangent or ask about something off the current plan,
   follow it. Curiosity is the curriculum."

The OLD instruction was:
  "When they ask about something outside the current plan, acknowledge it warmly
   and say you'll explore it together next time."

Gate: tutor MUST NOT redirect the child back to the original topic when they
follow a genuine curiosity tangent. A redirect is a FAIL.

Run:
    ANTHROPIC_API_KEY=... pytest tests/evals/test_tangent_following.py -v
"""

import asyncio
import os
import re
import pytest
import litellm
from dataclasses import dataclass
from services.tutor import AGE_INSTRUCTIONS, SYSTEM_PROMPT_TEMPLATE


@dataclass
class TangentCase:
    current_topic: str
    child_age: int
    tangent_message: str      # child goes off-topic
    tangent_subject: str      # what they're actually asking about
    redirect_phrases: list    # strings that indicate the tutor is redirecting away


CASES = [
    TangentCase(
        current_topic="fractions",
        child_age=9,
        tangent_message="Wait, why is the sky blue? I was thinking about that at lunch",
        tangent_subject="why sky is blue",
        redirect_phrases=[
            "get back to fractions",
            "next time",
            "let's explore that another day",
            "focus on fractions",
            "back to what we were doing",
            "we can talk about that later",
        ],
    ),
    TangentCase(
        current_topic="the water cycle",
        child_age=10,
        tangent_message="How do fish breathe underwater? I was just thinking",
        tangent_subject="fish breathing",
        redirect_phrases=[
            "get back to the water cycle",
            "next time",
            "explore that another day",
            "let's stay on",
            "back to",
            "we can talk about that later",
        ],
    ),
    TangentCase(
        current_topic="multiplication",
        child_age=8,
        tangent_message="Do dinosaurs have bones like us?",
        tangent_subject="dinosaur bones",
        redirect_phrases=[
            "get back to multiplication",
            "next time",
            "explore that later",
            "let's continue with",
            "back to times tables",
            "finish multiplication first",
        ],
    ),
    TangentCase(
        current_topic="the Romans",
        child_age=11,
        tangent_message="Could a Roman soldier beat a medieval knight in a fight?",
        tangent_subject="Romans vs medieval knights",
        redirect_phrases=[
            "next time",
            "let's get back to",
            "focus on the Romans for now",
            "explore that another day",
            "back to what we were covering",
        ],
    ),
    TangentCase(
        current_topic="ecosystems",
        child_age=12,
        tangent_message="Why do some stars explode and others don't?",
        tangent_subject="stellar evolution",
        redirect_phrases=[
            "next time",
            "get back to ecosystems",
            "explore that another day",
            "let's stay on topic",
            "back to ecosystems",
        ],
    ),
]


def build_system(case: TangentCase) -> str:
    age_key = "under_8" if case.child_age < 8 else "8_plus"
    return SYSTEM_PROMPT_TEMPLATE.format(
        age_instructions=AGE_INSTRUCTIONS[age_key],
        name="Sam",
        age=case.child_age,
        interests="Minecraft, animals",
        reading_level="age-appropriate",
        current_topic=case.current_topic,
        current_books="none currently",
        top_interest="Minecraft",
    )


def response_redirects(response: str, redirect_phrases: list) -> bool:
    """Returns True if the response contains a redirect phrase."""
    resp_lower = response.lower()
    return any(phrase.lower() in resp_lower for phrase in redirect_phrases)


def response_engages_tangent(response: str, tangent_subject: str) -> bool:
    """Returns True if the response engages with the tangent subject at all."""
    # Heuristic: the response should contain a question or statement
    # related to the tangent, and not be purely a redirect
    return "?" in response  # minimal: at least asks something (engages)


async def run_case(case: TangentCase, model: str) -> dict:
    system = build_system(case)
    # Simulate: tutor has been teaching current_topic, child sends tangent
    messages = [
        {"role": "system", "content": system},
        {"role": "assistant", "content": f"Let's explore {case.current_topic} together. What do you already know about it?"},
        {"role": "user", "content": case.tangent_message},
    ]
    response = await litellm.acompletion(
        model=model,
        messages=messages,
        max_tokens=200,
        temperature=0.3,
    )
    content = response.choices[0].message.content
    redirects = response_redirects(content, case.redirect_phrases)
    engages = response_engages_tangent(content, case.tangent_subject)
    return {
        "topic": case.current_topic,
        "tangent": case.tangent_subject,
        "age": case.child_age,
        "response": content,
        "redirects": redirects,
        "engages": engages,
    }


MODEL = os.environ.get("ETUTOR_EVAL_MODEL", "claude-haiku-4-5-20251001")


@pytest.mark.parametrize("case", CASES, ids=[c.current_topic + "_tangent" for c in CASES])
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping live eval"
)
def test_does_not_redirect_tangent(case):
    """Tutor must not redirect the child back to the original topic when they follow a tangent."""
    result = asyncio.get_event_loop().run_until_complete(run_case(case, MODEL))
    assert not result["redirects"], (
        f"\n\nTANGENT REDIRECT DETECTED on topic='{case.current_topic}'\n"
        f"Child said: '{case.tangent_message}'\n"
        f"Tutor responded: {result['response']}\n"
        f"(Tutor should follow the curiosity, not redirect back to {case.current_topic})\n"
    )


@pytest.mark.parametrize("case", CASES, ids=[c.current_topic + "_engage" for c in CASES])
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping live eval"
)
def test_engages_with_tangent(case):
    """Tutor must engage with the tangent subject, not just ignore it."""
    result = asyncio.get_event_loop().run_until_complete(run_case(case, MODEL))
    assert result["engages"], (
        f"\n\nTANGENT NOT ENGAGED on topic='{case.current_topic}'\n"
        f"Child asked about: '{case.tangent_subject}'\n"
        f"Tutor responded: {result['response']}\n"
    )


async def run_all(model: str = MODEL):
    results = [await run_case(c, model) for c in CASES]
    redirected = [r for r in results if r["redirects"]]
    redirect_rate = len(redirected) / len(results) * 100
    print(f"\n{'='*60}")
    print(f"Tangent-redirect rate: {redirect_rate:.0f}%  ({len(redirected)}/{len(results)} cases)")
    print(f"Target: 0%  (tutor should ALWAYS follow curiosity)")
    print(f"{'='*60}")
    for r in results:
        status = "REDIRECT" if r["redirects"] else "ok      "
        engaged = "engaged" if r["engages"] else "ignored"
        print(f"  {status}  [{engaged}]  '{r['topic']}' → '{r['tangent']}'")
        if r["redirects"]:
            print(f"    Response: {r['response'][:120]}...")
    return redirect_rate, results


if __name__ == "__main__":
    rate, _ = asyncio.run(run_all())
    exit(0 if rate == 0 else 1)
