from sqlalchemy.orm import Session
from app.daos import project_dao
from app.daos import event_dao
from app.services import project_service
from app.schemas import EventDetailResponse, ParticipantItem, SubEventItem


def get_event_by_id(db: Session, event_id: int):
    return event_dao.find_event_by_id(db, event_id)


def get_events_with_page_params(db: Session, skip: int = 0, limit: int = 20):
    return event_dao.find_events_with_page_params(db, skip, limit)


def get_event_dots_by_date_range(db: Session, start_date: str, end_date: str):
    event_dots = []

    events = event_dao.find_event_dots_by_date_range(db, start_date, end_date)

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
    events = event_dao.find_events_by_date(db, date)
    if not events:
        return []

    event_ids = [event.id for event in events]
    reg_counts_map = event_dao.get_reg_user_count_by_event_ids(db, event_ids)
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


def get_events_details_by_id(
    db: Session, user_id: str, event_id: str
) -> EventDetailResponse:
    event = event_dao.find_event_by_id(db, event_id)
    if not event:
        return None

    reg_count = event_dao.get_reg_user_count_by_event_ids(db, [event_id]).get(
        event_id, 0
    )
    reg_users = event_dao.get_reg_users_by_event_id(db, event_id, limit=5)

    participants = [
        ParticipantItem(id=user.id, nickname=user.nickname, avatar_url=user.avatar_url)
        for user in reg_users
    ]

    projects = project_service.get_projects_by_event_id(db, event_id)
    projects_reg_counts = project_service.get_reg_user_counts_by_project_ids(
        db, [project.id for project in projects]
    )

    sub_events = [
        SubEventItem(
            id=project.id,
            title=project.name,
            time=project.created_at.isoformat(),
            place=project.place or "",
            image="",
            participants_count=projects_reg_counts.get(project.id, 0),
        )
        for project in projects
    ]

    is_current_user_joined = (
        get_user_is_joined_event(db, user_id, event_id) if user_id else False
    )

    return EventDetailResponse(
        id=event.id,
        title=event.title,
        date=event.event_start_date,
        place=event.place,
        category=event.category,
        event_url=event.event_url,
        header_image=event.thumbnail_url,
        participants_count=reg_count,
        participants=participants,
        sub_events=sub_events,
        is_current_user_joined=is_current_user_joined,
    )


def get_user_is_joined_event(db: Session, user_id: str, event_id: str) -> bool:
    registrations = event_dao.get_reg_users_id_by_event_id(db, event_id)
    return user_id in [reg.user_id for reg in registrations]
