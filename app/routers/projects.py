from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Project, User
from app.routers.base import ResponseModel
from app.services.project_service import get_projects_by_event_id, create_new_project
from app.schemas import ProjectCreate, ProjectOut
from typing import List

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


# --- 创建新项目 ---
@router.post("/", response_model=ResponseModel[ProjectOut], status_code=201)
async def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    # TODO:从 Token 中获取当前登录用户
    # current_user: User = Depends(get_current_user)
):
    # TODO:暂时硬编码
    test_creator = db.query(User).first()

    new_project = create_new_project(db, project_in.dict(), test_creator.id)

    return ResponseModel.success_response(data=new_project)


# --- 获取某个 Event 下的所有项目 ---
@router.get("/by-event/{event_id}", response_model=ResponseModel[List[ProjectOut]])
async def get_projects_by_event(event_id: str, db: Session = Depends(get_db)):
    projects = get_projects_by_event_id(db, int(event_id))
    return ResponseModel.success_response(data=projects)
