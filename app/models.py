import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    func,
    String,
    Date,
    Boolean,
    Table,
    Text,
    ForeignKey,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_mixin, relationship
from .database import Base
import uuid


@declarative_mixin
class TimestampMixin:
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    is_deleted = Column(Boolean, default=False, nullable=False)


event_artists = Table(
    "event_artists",
    Base.metadata,
    Column("event_id", String(36), ForeignKey("events.id"), primary_key=True),
    Column("artist_id", String(36), ForeignKey("artists.id"), primary_key=True),
)


class Artist(Base, TimestampMixin):
    __tablename__ = "artists"
    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)

    events = relationship("Event", secondary=event_artists, back_populates="artists")


class Event(Base, TimestampMixin):
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
    is_published = Column(Boolean, default=True)
    artists = relationship("Artist", secondary=event_artists, back_populates="events")
    projects = relationship("Project", back_populates="event")


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    openid = Column(String(128), index=True)
    platform = Column(String(20))  # "wechat" 或 "qq"

    nickname = Column(String(64))
    avatar_url = Column(String(255))

    is_active = Column(Boolean, default=True)  # 用户是否激活
    is_admin = Column(Boolean, default=False)  # 是否管理员
    last_login = Column(DateTime, nullable=True)  # 上次登录时间

    __table_args__ = (
        UniqueConstraint("openid", "platform", name="uix_openid_platform"),
    )


class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    name = Column(String(255), nullable=False)
    project_type = Column(String(20))
    event_id = Column(
        String(36),
        ForeignKey("events.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    creator_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=True)
    form_config = Column(JSON, nullable=True)

    event = relationship("Event", back_populates="projects")
    registrations = relationship("ProjectRegistration", back_populates="project")


class ProjectRegistration(Base, TimestampMixin):
    __tablename__ = "project_registrations"

    project_id = Column(String(36), ForeignKey("projects.id"), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)

    form_data = Column(JSON)

    project = relationship("Project", back_populates="registrations")
    user = relationship("User")
