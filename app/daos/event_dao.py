from sqlalchemy.orm import Session, joinedload
from app.models import Event


def find_event_by_id(db: Session, event_id: int):
    return (
        db.query(Event)
        .options(joinedload(Event.artists))
        .filter(Event.id == event_id)
        .first()
    )


def find_events_with_page_params(db: Session, skip: int = 0, limit: int = 20):
    return (
        db.query(Event)
        .options(joinedload(Event.artists))
        .order_by(Event.event_start_date.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )
