from sqlalchemy.orm import Session
from app.daos.event_dao import find_event_by_id, find_events_with_page_params


def get_event_by_id(db: Session, event_id: int):
    return find_event_by_id(db, event_id)


def get_events_with_page_params(db: Session, skip: int = 0, limit: int = 20):
    return find_events_with_page_params(db, skip, limit)
