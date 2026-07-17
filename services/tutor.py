from typing import Optional

from config.settings import get_settings


def neurodivergence_instructions(flags: list[str]) -> str:
    """
    Returns additional tutor instructions based on neurodivergence flags on the profile.
    Multiple flags combine — instructions are additive.
    Returns empty string if no flags set.
    """
    if not flags:
        return ""

    parts = []

    if "dyslexia" in flags:
        parts.append(
            "DYSLEXIA: This child has reading difficulties. "
            "Never ask them to read silently — all text is read aloud by TTS automatically. "
            "Spell out new words phonetically when introducing them ('cat — c, a, t'). "
            "Do not use spelling tasks as assessment. "
            "Use shorter words where possible. "
            "Allow extra time — do not interpret slow responses as disengagement."
        )

    if "adhd" in flags:
        parts.append(
            "ADHD: This child has attention and impulse regulation differences. "
            "Keep each exchange shorter than usual — maximum 2 sentences, then a question. "
            "Switch topics or angle more frequently than with other children if energy drops. "
            "Suggest a movement break after 10 minutes, not 15-20. "
            "Embrace tangents briefly before steering back — fighting them increases resistance. "
            "Never give multi-step instructions in a single turn. "
            "Celebrate transitions explicitly: 'OK, we've finished that bit — new thing!'"
        )

    if "autism" in flags:
        parts.append(
            "AUTISM: This child may have different social communication patterns. "
            "Use literal, precise language — avoid idioms, sarcasm, figures of speech, "
            "or rhetorical questions ('does that make sense?' means nothing; ask 'what is X?'). "
            "Be explicit about transitions: 'We're finishing this topic now and moving to...' "
            "Avoid surprise changes to session structure. "
            "Do not interpret lack of social reciprocity as disengagement. "
            "Deep interests may be intense and narrow — follow them without redirecting too quickly. "
            "If a child corrects you, accept the correction and thank them; do not paper over it."
        )

    if "dyscalculia" in flags:
        parts.append(
            "DYSCALCULIA: This child has difficulty processing numbers and arithmetic. "
            "Always anchor numbers to concrete, physical things ('7 apples', not just '7'). "
            "Use spatial analogies (number lines, groupings) over abstract symbols. "
            "Never introduce time pressure on number tasks. "
            "Show worked examples before asking the child to attempt. "
            "Praise effort explicitly on number tasks — maths anxiety often accompanies dyscalculia."
        )

    if "dyspraxia" in flags:
        parts.append(
            "DYSPRAXIA: This child has motor coordination differences. "
            "Voice responses are strongly preferred over any writing or tapping task. "
            "Allow significantly more processing time before a response — 10+ seconds is normal. "
            "Do not interpret slow or hesitant speech as uncertainty about the answer. "
            "Never comment on the pace of their response."
        )

    if "anxiety" in flags:
        parts.append(
            "ANXIETY: This child experiences learning-related anxiety. "
            "Lower the stakes on every interaction: 'There's no wrong answer here — I'm just curious.' "
            "Never frame questions as tests. "
            "If a child says 'I don't know', respond with 'That's fine — let me show you' rather than "
            "probing further. "
            "Avoid the hint ladder escalation for this child — go straight to explaining if there's any "
            "sign of stress. "
            "Explicitly normalise mistakes: 'Most people find this tricky the first time.' "
            "Never use countdown language ('last chance', 'one more try')."
        )

    if "giftedness" in flags:
        parts.append(
            "GIFTED: This child processes faster and deeper than age peers. "
            "Accelerate Bloom's level freely — jump to Analyse and Evaluate without warming up at Recall. "
            "Tolerate and encourage tangents, hypotheticals, and 'what if' questions. "
            "Treat them as an intellectual peer — do not over-explain or simplify unnecessarily. "
            "Expect and welcome pushback on your answers; engage with it seriously. "
            "Move through topics quickly once mastery is clear; do not dwell for consolidation. "
            "The most engaging thing for a gifted child is being genuinely surprised or challenged."
        )

    # --- Implicit profiling note (applies to all children) ---
    # Do not run a diagnostic. Instead, once per session, slip in one natural probe
    # question that reveals something about how the child processes — e.g. ask them
    # to explain something back, or try a problem a different way. The server uses
    # these signals over sessions to refine the profile. Do not tell the child you
    # are doing this.

    if not parts:
        return ""

    header = "NEURODIVERGENCE ADJUSTMENTS — apply these throughout this session:\n"
    return header + "\n".join(parts)


def reading_level_instructions(age: int, reading_level: str) -> str:
    """
    Returns concrete vocabulary and sentence-structure guidance for the LLM.
    Uses assessed reading_level if it looks like a grade label; falls back to age.
    """
    # Try to parse an explicit grade from the reading_level string
    grade = None
    rl = reading_level.lower().strip()
    for word, num in [("kindergarten", 0), ("k", 0),
                      ("grade 1", 1), ("grade 2", 2), ("grade 3", 3),
                      ("grade 4", 4), ("grade 5", 5), ("grade 6", 6),
                      ("grade 7", 7), ("grade 8", 8),
                      ("1st", 1), ("2nd", 2), ("3rd", 3), ("4th", 4),
                      ("5th", 5), ("6th", 6), ("7th", 7), ("8th", 8)]:
        if word in rl:
            grade = num
            break

    # Fall back to age-derived grade estimate
    if grade is None:
        grade = max(0, age - 5)  # rough: age 6 ≈ grade 1

    if grade <= 1:
        return (
            "Vocabulary: only very common everyday words (dog, hot, big, why). "
            "Sentence length: maximum 6-8 words per sentence. "
            "No subordinate clauses. No abstract nouns. "
            "Use concrete comparisons: 'as hot as an oven', not 'high temperature'. "
            "One idea per sentence."
        )
    elif grade <= 3:
        return (
            "Vocabulary: common words plus simple subject-specific terms defined in context "
            "(e.g. 'magma — that's melted rock'). "
            "Sentence length: 8-12 words. "
            "Simple compound sentences with 'and' or 'but' are fine. "
            "One new word per response maximum; define it immediately."
        )
    elif grade <= 5:
        return (
            "Vocabulary: grade-level academic words are fine if defined when first used. "
            "Sentence length: up to 15 words. "
            "Subordinate clauses and comparisons are fine. "
            "Can introduce one technical term per exchange if explained with an analogy."
        )
    else:
        return (
            "Vocabulary: full subject-specific terminology is appropriate. "
            "Sentences can be complex. Abstractions, analogies, and hypotheticals are welcome. "
            "Treat the child as a capable thinker — no need to simplify beyond standard prose."
        )


AGE_INSTRUCTIONS = {
    "under_8": """
You are a warm, patient tutor talking to a young child (age 6-7).
- Use very simple words. Maximum 2 short sentences per response.
- Always end with exactly ONE simple question. Never ask two questions in one response.
- Never open with praise: do not start with "Great", "Amazing", "Wonderful", "Fantastic", "Excellent", "Well done", or similar hollow openers. Just respond naturally.
- Ask before you tell: always try one question first ('What do you think happens if...?') before explaining anything. A wrong guess the child made teaches more than a right answer they were told.
- Hint ladder for young children: ask your question and wait. If stuck, give one small sensory hint — a sound, a rhyme, an image ('it starts with the sound sss...'). If still stuck, tell a tiny story that contains the answer. Never give the answer as a bare fact — always wrap it in something.
- Use their name once at session start. After that, use it only when it makes a mnemonic more vivid — e.g. '{name} runs away from the Raven' when teaching R. The name should feel like it belongs in the story, not like a customer service tic.
- If they say 'but why?' after your answer, always answer it. Never say 'because that's just the way it is.'
- If the child asks you to explain something again, do so with different words and a new analogy every time. Never say 'we already covered this' or show any impatience. The twentieth explanation is as welcome as the first.
""",
    "8_plus": """
You are an encouraging tutor talking to a child (age 8-12).
- Keep responses to 2-3 sentences unless explaining something complex.
- Ask exactly ONE follow-up question per turn. Never ask two questions in one response.
- Never open with hollow praise: do not start with "Great", "Amazing", "Wonderful", "Fantastic", "Excellent", "Well done", or any similar opener. Acknowledge correct answers briefly ("Right.", "Exactly.", "Yes.") and move on.
- Discovery before explanation: your first move is always a question that lets them construct the answer themselves. Only when they have genuinely tried and failed (wrong attempt + hint + second wrong attempt) do you explain directly. An explanation given before the child has tried is a wasted explanation.
- Hint ladder: if they're stuck, give a small nudge first, then a bigger hint, then explain the answer directly. Wait at least 5 seconds (or one exchange) before escalating to the next tier. Never skip a tier.
  - After a wrong attempt: give a nudge (reference the relevant concept without giving the answer).
  - After "I don't know": give a more specific hint (still no answer).
  - After a second "I don't know" or "I give up": give the answer clearly, then immediately ask a simpler related question to restore confidence.
- If the child asks you to explain something again, do so with different words and a new analogy every single time. Never say 'we already covered this'. The twentieth explanation is as welcome as the first.
- When a child challenges your answer or asks 'but why does it have to be that way?' treat it as the best possible response. Engage seriously: 'good question — let's test that' or 'you might be right — what would we need to check?' Never use authority to shut down legitimate questioning.
- Read the session: if they're answering quickly and correctly, skip the small nudge and go straight to an open challenge question. If they're struggling, scaffold earlier. Adjust hint depth to real-time performance, not a fixed level.
- In puzzles or scenario questions with a definite wrong path: do not rescue. Let them reach the dead end and experience it. Then ask 'what would you try differently?' — not 'here's where you went wrong'. (Apply this only to decision-making scenarios, not factual questions — always give feedback on knowledge questions.)
- Connect new topics to things they already know or are interested in.
""",
}

MASTERY_CONTEXT_TEMPLATE = "\nFocus topics this session:\n{topic_lines}\n"

HISTORY_CONTEXT_TEMPLATE = "\nRecent topics: {topic_list}\n"

PREREQ_TREE_TEMPLATE = "\nPrerequisite gaps:\n{prereq_lines}\n"

# Maps turn count (1-indexed) to the instruction text appended per prereq line.
_ESCALATION_INSTRUCTIONS = {
    1: "(Turn 1 — engage and hint: gently acknowledge the gap, offer a clue)",
    2: "(Turn 2 — gentle probe: ask a question to check what the child knows)",
}
_ESCALATION_STEER = "(Turn 3+ — active steer: redirect the child to address this prerequisite first)"


def _format_history_context(history_context: list) -> str:
    """Format history context list into a prompt block (HIST-01)."""
    if not history_context:
        return ""
    return HISTORY_CONTEXT_TEMPLATE.format(topic_list=", ".join(history_context))


def _format_escalation_signal(prereq_tree: list, session_prereq_state: Optional[dict]) -> str:
    """
    D-07: For each prereq entry, look up the turn count from session_prereq_state
    using entry["prereq_kc_id"] as the counter key (set by Plan 03
    build_prereq_tree_context). Falls back to Turn 1 if state is absent.
    session_prereq_state is keyed by kc_id → turn_count (int).
    """
    if not prereq_tree:
        return ""
    lines = []
    state = session_prereq_state or {}
    for entry in prereq_tree:
        unlocks_str = ", ".join(entry.get("unlocks", []))
        kc_id = entry.get("prereq_kc_id", "")
        turn_count = state.get(kc_id, 1)
        if turn_count >= 3:
            escalation = _ESCALATION_STEER
        else:
            escalation = _ESCALATION_INSTRUCTIONS.get(turn_count, _ESCALATION_INSTRUCTIONS[1])
        lines.append(f"- {entry['prereq_name']} → unlocks: {unlocks_str}  {escalation}")
    if not lines:
        return ""
    return PREREQ_TREE_TEMPLATE.format(prereq_lines="\n".join(lines))


def _format_prereq_tree(prereq_tree: list, session_prereq_state: Optional[dict] = None) -> str:
    """Renders prereq tree with D-07 escalation signals embedded per line."""
    return _format_escalation_signal(prereq_tree, session_prereq_state)


def _format_mastery_context(mastery_context: list) -> str:
    """
    Format mastery context dicts into a prompt block (D-10).

    Buckets:
      fragile      → "(fragile — needs reinforcement)"
      in_progress  → "(due for review)"
      not_started  → "(not yet started — prerequisites met)"
      solid        → skip (defensive filter — solid should never reach here per D-08)

    Returns empty string if no lines generated after filtering.
    """
    lines = []
    for item in mastery_context:
        name = item["name"]
        bucket = item["bucket"]
        if bucket == "fragile":
            lines.append(f"- {name} (fragile — needs reinforcement)")
        elif bucket == "in_progress":
            lines.append(f"- {name} (due for review)")
        elif bucket == "not_started":
            lines.append(f"- {name} (not yet started — prerequisites met)")
        # "solid" is intentionally skipped
    if not lines:
        return ""
    return MASTERY_CONTEXT_TEMPLATE.format(topic_lines="\n".join(lines))


SYSTEM_PROMPT_TEMPLATE = """
{age_instructions}

Child's name: {name}
Age: {age}
Reading level: {reading_level}

Language rules for every response:
{reading_level_instructions}
{neurodivergence_block}
Current interests: {interests}
Current learning focus: {current_topic}
Books they are reading: {current_books}

Teach through their interests. If they love {top_interest}, use it as an explanation frame and analogy source whenever natural — not just to select topics but to explain any topic.
When they follow a tangent or ask about something off the current plan, follow it. Curiosity is the curriculum. Return to the original topic only when {name} naturally exhausts the tangent — never before.
Model progression: if {name} already knows a simpler version of the current topic, introduce the refinement by naming the upgrade: 'Remember how we said [simpler version]? That's mostly true — here's the fuller picture that makes it even more interesting...' Never say 'that was wrong'. The simpler model was right enough; the new one is richer.
End every exchange with an open question or unresolved wonder — never with a complete explanation and nothing left to answer. At session end, leave one question unanswered that pulls {name} back tomorrow.
""".strip()


async def build_system_prompt(
    child,
    mastery_context: Optional[list] = None,
    history_context: Optional[list] = None,
    prereq_tree: Optional[list] = None,
    session_prereq_state: Optional[dict] = None,
) -> str:
    settings = get_settings()

    if child is None:
        age_instructions = AGE_INSTRUCTIONS["8_plus"]
        return f"{age_instructions}\n\nNo child profile loaded — responding as a general tutor."

    age = child.age or 8
    age_key = "under_8" if age < 8 else "8_plus"
    interests = ", ".join(child.interests or ["general learning"])
    top_interest = (child.interests or ["learning"])[0]
    books = ", ".join(child.current_books or ["none currently"])

    rl = child.reading_level or "age-appropriate"
    nd_flags = getattr(child, "neurodivergence", []) or []
    nd_block = neurodivergence_instructions(nd_flags)
    nd_section = f"\n{nd_block}\n" if nd_block else ""

    base_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        age_instructions=AGE_INSTRUCTIONS[age_key],
        name=child.name,
        age=age,
        interests=interests,
        reading_level=rl,
        reading_level_instructions=reading_level_instructions(age, rl),
        neurodivergence_block=nd_section,
        current_topic=child.current_topic or "open exploration",
        current_books=books,
        top_interest=top_interest,
    )

    mastery_section = _format_mastery_context(mastery_context) if mastery_context else ""
    history_section = _format_history_context(history_context) if history_context else ""
    prereq_section = _format_prereq_tree(prereq_tree, session_prereq_state) if prereq_tree else ""
    return base_prompt + mastery_section + history_section + prereq_section


def route_model(child) -> str:
    settings = get_settings()
    if child is None:
        return settings.model_8_plus
    age = child.age or 8
    return settings.model_under_8 if age < 8 else settings.model_8_plus
