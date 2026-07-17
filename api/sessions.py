from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import get_session, get_turns_by_session_id
from db.session import get_db
from services.knowledge_tracing import fit_fsrs_params, update_bkt_for_session
from services.session_intelligence import extract_and_update_interests
from services.sessions import get_session_history

router = APIRouter()


@router.get("/sessions/{child_id}")
async def get_sessions(
    child_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
):
    turns = await get_session_history(child_id, session, limit)
    return {
        "child_id": child_id,
        "turns": [
            {
                "id": t.id,
                "child_id": t.child_id,
                "session_id": t.session_id,
                "question": t.question,
                "answer": t.answer,
                "topic": t.topic,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
            }
            for t in turns
        ],
    }


@router.get("/sessions/{session_id}/turns")
async def get_session_turns(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    # HIST-03 (CR-02 note): same IDOR exposure as GET /sessions/{child_id} — fix both together in auth phase
    turns = await get_turns_by_session_id(session_id, db)
    return {
        "session_id": session_id,
        "turns": [
            {
                "id": t.id,
                "child_id": t.child_id,
                "question": t.question,
                "answer": t.answer,
                "topic": t.topic,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
            }
            for t in turns
        ],
    }


@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    KT-04: Close a tutoring session and trigger BKT + FSRS updates.

    Sets sessions.ended_at = now(), runs batch BKT update for all session events,
    then re-fits per-child FSRS parameters.

    Security note (T-2-10): session_id passed to get_session() which uses SQLAlchemy
    parameterised select() — never string-interpolated.
    Security note (T-2-12): 409 guard prevents BKT/FSRS from running on already-ended sessions.
    """
    session_row = await get_session(session_id, db)
    if session_row is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if session_row.ended_at is not None:
        raise HTTPException(status_code=409, detail="Session already ended")

    session_row.ended_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(session_row)

    bkt_updates = await update_bkt_for_session(session_id, db)
    await fit_fsrs_params(session_row.child_id, db)
    await extract_and_update_interests(session_id, session_row.child_id, db)

    return {
        "session_id": session_id,
        "ended_at": session_row.ended_at.isoformat(),
        "kcs_updated": len(bkt_updates),
    }
