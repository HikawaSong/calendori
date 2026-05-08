from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Project


def find_projects_by_event_id(db: Session, event_id: int):
    return (
        db.query(Project)
        .filter(
            Project.event_id == event_id,
            Project.is_deleted == False,
        )
        .all()
    )


def create_project(db: Session, project_data: dict, creator_id: int):
    new_project = Project(**project_data, creator_id=creator_id)
    db.add(new_project)
    db.flush()
    return new_project


def get_project_counts_by_event_ids(db: Session, event_ids: list[str]) -> dict:
    """根据活动 ID 列表，批量查询子项目数，返回 {event_id: count} 的字典"""
    if not event_ids:
        return {}

    rows = (
        db.query(Project.event_id, func.count(Project.id))
        .filter(Project.event_id.in_(event_ids))
        .group_by(Project.event_id)
        .all()
    )

    return {row[0]: row[1] for row in rows}


def get_reg_user_counts_by_project_ids(db: Session, project_ids: list[str]) -> dict:
    """根据项目 ID 列表，批量查询报名人数，返回 {project_id: count} 的字典"""
    if not project_ids:
        return {}

    rows = (
        db.query(Project.id, func.count(Project.reg_users))
        .filter(Project.id.in_(project_ids))
        .group_by(Project.id)
        .all()
    )

    return {row[0]: row[1] for row in rows}
