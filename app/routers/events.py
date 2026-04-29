from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import calendar
from app.routers.base import ResponseModel
from app.services.event_service import (
    get_daily_event_cards,
    get_event_by_id,
    get_event_dots_by_date_range,
    get_events_with_page_params,
)
from ..database import get_db
from datetime import date
from ..schemas import EventRead, EventCalendarDot, EventDailyCard

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.get("/", response_model=ResponseModel[List[EventRead]])
def get_events(
    skip: int = 0, limit: int = 20, db: Session = Depends(get_db)
) -> List[EventRead]:
    events = get_events_with_page_params(db, skip, limit)
    return ResponseModel.success_response(data=events)


@router.get("/calendar", response_model=ResponseModel[List[EventCalendarDot]])
def get_events_for_calendar(
    year: int = Query(..., description="查询年份"),
    month: int = Query(..., ge=1, le=12, description="查询月份"),
    db: Session = Depends(get_db),
):
    """
    获取指定月份的日历轻量数据
    """

    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    event_dots = get_event_dots_by_date_range(db, start_date, end_date)

    return ResponseModel.success_response(data=event_dots)


@router.get("/daily", response_model=ResponseModel[List[EventDailyCard]])
def get_daily_events(
    date: date = Query(..., description="查询日期"),
    db: Session = Depends(get_db),
):
    """
    获取指定日期的活动列表
    """

    daily_cards = get_daily_event_cards(db, date.isoformat())
    return ResponseModel.success_response(data=daily_cards)


@router.get("/{event_id}", response_model=ResponseModel[EventRead])
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = get_event_by_id(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="活动不存在")
    return ResponseModel.success_response(data=event)
