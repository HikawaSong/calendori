import datetime

from sqlalchemy import (
    JSON,
    Column,
    Integer,
    String,
    Date,
    Boolean,
    Table,
    Text,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from .database import Base
import uuid


event_artists = Table(
    "event_artists",
    Base.metadata,
    Column("event_id", String(36), ForeignKey("events.id"), primary_key=True),
    Column("artist_id", String(36), ForeignKey("artist.id"), primary_key=True),
)


class Artist(Base):
    __tablename__ = "artist"
    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)

    events = relationship("Event", secondary=event_artists, back_populates="artists")


class Event(Base):
    __tablename__ = "events"
    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    title = Column(String(255), nullable=False)
    dates = Column(JSON, nullable=True)
    place = Column(String(255), nullable=True)
    category = Column(String(255), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    event_url = Column(String(500), nullable=True)
    event_start_date = Column(Date, nullable=True)
    artists = relationship("Artist", secondary=event_artists, back_populates="events")
