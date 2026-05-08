from app.daos import project_dao
from sqlalchemy.orm import Session


def get_projects_by_event_id(db: Session, event_id: int):
    return project_dao.find_projects_by_event_id(db, event_id)


def create_new_project(db: Session, project_data: dict, creator_id: int):
    project = project_dao.create_project(db, project_data, creator_id)
    db.commit()
    db.refresh(project)
    return project


def get_reg_user_counts_by_project_ids(db: Session, event_ids: list[str]) -> dict:
    return project_dao.get_reg_user_counts_by_project_ids(db, event_ids)
