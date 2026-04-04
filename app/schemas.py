from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
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
