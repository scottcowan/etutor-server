from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid

_sessions: dict[str, list] = {}  # child_id → list of turns


@dataclass
class Turn:
    id: str
    child_id: str
    question: str
    answer: str
    timestamp: str
    topic: Optional[str] = None


async def log_turn(child_id: str, question: str, answer: str, topic: str = None):
    turn = Turn(
        id=str(uuid.uuid4()),
        child_id=child_id,
        question=question,
        answer=answer,
        timestamp=datetime.utcnow().isoformat(),
        topic=topic,
    )
    if child_id not in _sessions:
        _sessions[child_id] = []
    _sessions[child_id].append(turn)
    return turn


async def get_session_history(child_id: str, limit: int = 50) -> list[Turn]:
    turns = _sessions.get(child_id, [])
    return turns[-limit:]


async def get_all_sessions() -> dict[str, list[Turn]]:
    return _sessions
