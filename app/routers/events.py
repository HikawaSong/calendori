from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from ..database import get_db  # 假设你把 get_db 抽离到了 database.py
from ..models import Event
from ..schemas import EventRead

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.get("/", response_model=List[EventRead])
def find_events(
    skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
) -> List[EventRead]:
    events = (
        db.query(Event)
        .options(joinedload(Event.artists))
        .order_by(Event.event_start_date.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )

    return events


@router.get("/{event_id}", response_model=EventRead)
def find_event(event_id: int, db: Session = Depends(get_db)):
    event = (
        db.query(Event)
        .options(joinedload(Event.artists))
        .filter(Event.id == event_id)
        .first()
    )

    if not event:
        raise HTTPException(status_code=404, detail="活动不存在")
    return event
