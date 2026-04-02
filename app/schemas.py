from pydantic import BaseModel, ConfigDict
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
