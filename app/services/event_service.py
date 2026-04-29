from sqlalchemy.orm import Session
from app.daos import project_dao
from app.daos.event_dao import (
    find_event_by_id,
    find_event_dots_by_date_range,
    find_events_by_date,
    find_events_with_page_params,
    get_reg_user_count_by_event_ids,
)


def get_event_by_id(db: Session, event_id: int):
    return find_event_by_id(db, event_id)


def get_events_with_page_params(db: Session, skip: int = 0, limit: int = 20):
    return find_events_with_page_params(db, skip, limit)


def get_event_dots_by_date_range(db: Session, start_date: str, end_date: str):
    event_dots = []

    events = find_event_dots_by_date_range(db, start_date, end_date)

    if not events:
        return event_dots

    for event in events:
        event_dots.append(
            {
                "date": event.event_start_date.isoformat(),
                "type": event.category,
                "bands": [artist.name for artist in event.artists],
            }
        )

    return event_dots


def get_daily_event_cards(db: Session, date: str):
    # 1. 查询当天的活动列表
    events = find_events_by_date(db, date)
    if not events:
        return []

    event_ids = [event.id for event in events]
    reg_counts_map = get_reg_user_count_by_event_ids(db, event_ids)
    project_counts_map = project_dao.get_project_counts_by_event_ids(db, event_ids)

    # 2. 构造返回的活动卡片数据
    daily_cards = []
    for event in events:
        card = {
            "id": event.id,
            "type": event.category,
            "title": event.title,
            "place": event.place,
            "participants": reg_counts_map.get(event.id, 0),
            "sub_events": project_counts_map.get(event.id, 0),
        }
        daily_cards.append(card)

    return daily_cards
