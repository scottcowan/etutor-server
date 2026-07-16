"""
SQLAlchemy 2.0 ORM models for etutor-server.

Models:
  - ChildProfileModel: child profile (mirrors ChildProfile dataclass in services/profiles.py)
  - SessionModel: tutoring session record (DB-03)
  - InteractionEventModel: per-turn interaction events (DB-04)
  - MasteryStateModel: BKT + FSRS mastery scaffold (DB-05)
  - ChildFSRSParamsModel: per-child FSRS-5 fitted weight vector (D-06)

Importing this module does NOT trigger any DB I/O.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ChildProfileModel(Base):
    """Child profile — mirrors ChildProfile dataclass field names exactly."""
    __tablename__ = "child_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    device_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True, unique=True)
    reading_level: Mapped[str] = mapped_column(String, default="age-appropriate")
    interests: Mapped[list] = mapped_column(JSON, default=list)
    neurodivergence: Mapped[list] = mapped_column(JSON, default=list)
    current_topic: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    current_books: Mapped[list] = mapped_column(JSON, default=list)
    session_count: Mapped[int] = mapped_column(Integer, default=0)


class SessionModel(Base):
    """Tutoring session record (DB-03). turn_count is derived — not stored."""
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID4
    child_id: Mapped[str] = mapped_column(
        String, ForeignKey("child_profiles.id"), nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class InteractionEventModel(Base):
    """Per-turn interaction event (DB-04). Maps to Turn dataclass."""
    __tablename__ = "interaction_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID4
    child_id: Mapped[str] = mapped_column(
        String, ForeignKey("child_profiles.id"), nullable=False, index=True
    )
    session_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("sessions.id"), nullable=True
    )
    question: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
    topic: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    # DB-04 scaffold columns — nullable in Phase 1; populated in Phase 2 (BKT) and Phase 1 chat timing
    kc_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)   # set by Phase 2 BKT
    correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)  # set by Phase 2 BKT
    response_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # chat turn latency
    hint_used: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)   # set by Phase 2


class MasteryStateModel(Base):
    """BKT + FSRS mastery state scaffold (DB-05). Composite PK: (child_id, kc_id)."""
    __tablename__ = "mastery_state"

    child_id: Mapped[str] = mapped_column(
        String, ForeignKey("child_profiles.id"), primary_key=True
    )
    kc_id: Mapped[str] = mapped_column(String, primary_key=True)
    # BKT fields
    p_mastery: Mapped[float] = mapped_column(Float, default=0.1)
    p_learn: Mapped[float] = mapped_column(Float, default=0.2)
    p_slip: Mapped[float] = mapped_column(Float, default=0.1)
    p_guess: Mapped[float] = mapped_column(Float, default=0.2)
    # FSRS fields (scaffold — populated in Phase 2)
    stability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    difficulty_d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    card_state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    next_review: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ChildFSRSParamsModel(Base):
    """Per-child FSRS-5 fitted weight vector (D-06)."""
    __tablename__ = "child_fsrs_params"

    child_id: Mapped[str] = mapped_column(
        String, ForeignKey("child_profiles.id"), primary_key=True
    )
    # JSON list of 21 floats — FSRS-5 weight vector
    weights: Mapped[list] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
