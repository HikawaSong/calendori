from sqlalchemy.orm import Session
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
