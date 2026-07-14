"""
Thin wrapper over db/crud.py for child profile operations.

All functions accept an explicit AsyncSession parameter — callers inject via
Depends(get_db) in API route handlers (Plans 06-07).

Importing this module causes zero DB I/O and no side effects.

Neurodivergence flag values (used by services/tutor.py to adjust responses):
  "dyslexia"    — reading difficulty; phonics support, wider letter spacing,
                  never rely on silent reading, always TTS, more time on phonics
  "adhd"        — attention and impulse; shorter exchanges, more frequent topic
                  shifts, physical break prompts, avoid long explanations
  "autism"      — social communication; literal language, avoid idioms/sarcasm,
                  predictable structure, explicit transitions, no surprise changes
  "dyscalculia" — number processing difficulty; concrete manipulatives framing,
                  avoid timed pressure, more worked examples, spatial analogies
  "dyspraxia"   — motor/coordination; voice-only encouraged, no writing tasks,
                  more processing time before expecting a response
  "anxiety"     — school/learning anxiety; lower stakes framing, no wrong-answer
                  pressure, explicit "there's no trick here", extra reassurance
  "giftedness"  — advanced processing; accelerate level freely, higher Bloom targets,
                  tolerate tangents and deep-dives, treat as intellectual peer
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import (
    get_child_by_id as db_get_child_by_id,
    get_child_by_device_id as db_get_child_by_device_id,
    list_children as db_list_children,
    update_interests as db_update_interests,
)


async def get_child_by_device_id(device_id: str, session: AsyncSession):
    return await db_get_child_by_device_id(device_id, session)


async def get_child_by_id(child_id: str, session: AsyncSession):
    return await db_get_child_by_id(child_id, session)


async def list_children(session: AsyncSession):
    return await db_list_children(session)


async def update_interests(child_id: str, new_interests: list[str], session: AsyncSession):
    return await db_update_interests(child_id, new_interests, session)
