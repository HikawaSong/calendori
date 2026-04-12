from app.daos.project_dao import find_projects_by_event_id, create_project
from sqlalchemy.orm import Session


def get_projects_by_event_id(db: Session, event_id: int):
    return find_projects_by_event_id(db, event_id)


def create_new_project(db: Session, project_data: dict, creator_id: int):
    project = create_project(db, project_data, creator_id)
    db.commit()
    db.refresh(project)
    return project
