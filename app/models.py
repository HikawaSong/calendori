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
from .database import Base


event_artists = Table(
    "event_artists",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id"), primary_key=True),
    Column("band_id", Integer, ForeignKey("bands.id"), primary_key=True),
)


class Band(Base):
    __tablename__ = "bands"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)

    events = relationship("Event", secondary=event_artists, back_populates="artists")


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    dates = Column(JSON, nullable=True)
    place = Column(String(255), nullable=True)
    category = Column(String(255), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    event_url = Column(String(500), nullable=True)

    artists = relationship("Band", secondary=event_artists, back_populates="events")
