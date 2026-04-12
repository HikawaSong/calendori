from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.routers.base import ResponseModel
from app.services.event_service import get_event_by_id, get_events_with_page_params
from ..database import get_db
from ..models import Event
from ..schemas import EventRead

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.get("/", response_model=ResponseModel[List[EventRead]])
def get_events(
    skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
) -> List[EventRead]:
    events = get_events_with_page_params(db, skip, limit)
    return ResponseModel.success_response(data=events)


@router.get("/{event_id}", response_model=ResponseModel[EventRead])
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="活动不存在")
    return ResponseModel.success_response(data=event)
