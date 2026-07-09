from dataclasses import dataclass, field
from typing import Optional
import json

# In-memory store for dev — replace with SQLAlchemy in prod
_profiles: dict[str, "ChildProfile"] = {}
_device_map: dict[str, str] = {}  # device_id → child_id


@dataclass
class ChildProfile:
    id: str
    name: str
    age: int
    device_id: Optional[str] = None
    interests: list[str] = field(default_factory=list)
    reading_level: str = "age-appropriate"
    current_topic: Optional[str] = None
    current_books: list[str] = field(default_factory=list)
    session_count: int = 0
    # Neurodivergence flags — set by parent, used to adjust tutor behaviour.
    # These are not diagnostic labels; they are practical adjustments.
    # A child can have multiple flags set.
    neurodivergence: list[str] = field(default_factory=list)
    # Supported values:
    #   "dyslexia"      — reading difficulty; phonics support, wider letter spacing,
    #                     never rely on silent reading, always TTS, more time on phonics
    #   "adhd"          — attention and impulse; shorter exchanges, more frequent topic
    #                     shifts, physical break prompts, avoid long explanations
    #   "autism"        — social communication; literal language, avoid idioms/sarcasm,
    #                     predictable structure, explicit transitions, no surprise changes
    #   "dyscalculia"   — number processing difficulty; concrete manipulatives framing,
    #                     avoid timed pressure, more worked examples, spatial analogies
    #   "dyspraxia"     — motor/coordination; voice-only encouraged, no writing tasks,
    #                     more processing time before expecting a response
    #   "anxiety"       — school/learning anxiety; lower stakes framing, no wrong-answer
    #                     pressure, explicit "there's no trick here", extra reassurance
    #   "giftedness"    — advanced processing; accelerate level freely, higher Bloom targets,
    #                     tolerate tangents and deep-dives, treat as intellectual peer


def seed_dev_profiles():
    profiles = [
        ChildProfile(
            id="child-001",
            name="Alex",
            age=7,
            device_id="device-001",
            interests=["dinosaurs", "space", "Minecraft"],
            reading_level="grade 2",
            current_topic="prehistoric life",
            current_books=["My Big Dinosaur Book"],
        ),
        ChildProfile(
            id="child-002",
            name="Sam",
            age=10,
            device_id="device-002",
            interests=["volcanoes", "ocean animals", "coding"],
            reading_level="grade 5",
            current_topic="earth science",
            current_books=["How the Earth Works"],
        ),
    ]
    for p in profiles:
        _profiles[p.id] = p
        if p.device_id:
            _device_map[p.device_id] = p.id


seed_dev_profiles()


async def get_child_by_device_id(device_id: str) -> Optional[ChildProfile]:
    child_id = _device_map.get(device_id)
    if child_id:
        return _profiles.get(child_id)
    return None


async def get_child_by_id(child_id: str) -> Optional[ChildProfile]:
    return _profiles.get(child_id)


async def list_children() -> list[ChildProfile]:
    return list(_profiles.values())


async def update_interests(child_id: str, new_interests: list[str]):
    if child_id in _profiles:
        existing = set(_profiles[child_id].interests)
        _profiles[child_id].interests = list(existing | set(new_interests))
