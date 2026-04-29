from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models import Event, EventRegistration


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


def find_event_dots_by_date_range(db: Session, start_date: str, end_date: str):

    events = (
        db.query(Event)
        .filter(
            Event.event_start_date >= start_date, Event.event_start_date <= end_date
        )
        .options(joinedload(Event.artists))
        .all()
    )

    return events


def find_events_by_date(db: Session, date: str):

    return (
        db.query(Event)
        .filter(Event.event_start_date == date, Event.is_published == True)
        .all()
    )


def get_reg_user_count_by_event_ids(db: Session, event_ids: list[str]) -> dict:
    """根据活动 ID 列表，批量查询报名人数，返回 {event_id: count} 的字典"""

    rows = (
        db.query(EventRegistration.event_id, func.count(EventRegistration.user_id))
        .filter(EventRegistration.event_id.in_(event_ids))
        .group_by(EventRegistration.event_id)
        .all()
    )

    return {row[0]: row[1] for row in rows}
