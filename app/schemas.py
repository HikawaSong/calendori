from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import List, Optional
from datetime import date


class ArtistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    dates: List[str]
    event_start_date: date
    place: str
    category: str
    event_url: str
    thumbnail_url: Optional[str] = None
    artists: List[ArtistRead]


class ProjectBase(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Roselia 演唱会花篮登记"})
    project_type: str = Field(..., json_schema_extra={"example": "花篮"})
    description: Optional[str] = None
    event_id: Optional[str] = None
    # 定义这个项目需要登记人填什么
    # 例如：{"fields": [{"label": "寄语", "type": "text"}, {"label": "金额", "type": "number"}]}
    form_config: Optional[dict] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectOut(ProjectBase):
    id: str
    creator_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EventCalendarDot(BaseModel):
    date: str
    type: str
    bands: List[str]


class EventDailyCard(BaseModel):
    id: str
    type: str  # 例如 "Live" 或 "Event"
    title: str  # 活动标题
    place: str  # 地点
    participants: int  # 参与人数
    sub_events: int  # 子活动数量

    class Config:
        from_attributes = True


# --- 1. 参与者简要信息 ---
class ParticipantItem(BaseModel):
    id: str
    nickname: str
    avatar_url: str
    is_admin: bool = False


# --- 2. 子活动简要信息 ---
class SubEventItem(BaseModel):
    id: str
    title: str
    time: str
    place: str
    image: str  # 子活动的封面图
    participants_count: int  # 报名这个子活动的人数


class EventDetailResponse(BaseModel):
    # 基础信息
    id: str
    header_image: str
    title: str
    place: str
    date: date
    time_display: Optional[str] = None
    event_url: str
    category: str
    # 参与者相关
    participants_count: int  # 总报名人数
    participants: List[
        ParticipantItem
    ]  # 注意：只返回前 10 个参与者的简要信息，用于展示头像和昵称等

    # 子活动相关
    sub_events: List[SubEventItem]  # 关联的子活动列表

    # 当前用户相关
    is_current_user_joined: bool  # 当前请求这个接口的用户，是否已经报名
