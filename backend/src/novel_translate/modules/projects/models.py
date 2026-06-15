import enum
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from novel_translate.db.base import Base


class SegmentTranslationStatus(str, enum.Enum):
    pending = "pending"
    translating = "translating"
    done = "done"
    error = "error"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255))
    source_lang: Mapped[str] = mapped_column(String(32), default="ja", server_default="ja")
    target_lang: Mapped[str] = mapped_column(String(32), default="zh-CN", server_default="zh-CN")
    provider_config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    chapters: Mapped[list["Chapter"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Chapter.order_index",
    )


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
    )
    title: Mapped[str] = mapped_column(String(255))
    order_index: Mapped[int] = mapped_column(Integer)
    source_format: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    project: Mapped[Project] = relationship(back_populates="chapters")
    segments: Mapped[list["Segment"]] = relationship(
        back_populates="chapter",
        cascade="all, delete-orphan",
        order_by="Segment.order_index",
    )


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    chapter_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
    )
    order_index: Mapped[int] = mapped_column(Integer)
    source_text: Mapped[str] = mapped_column(Text)
    target_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[SegmentTranslationStatus] = mapped_column(
        Enum(SegmentTranslationStatus, name="segment_translation_status"),
        default=SegmentTranslationStatus.pending,
        server_default=SegmentTranslationStatus.pending.value,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    chapter: Mapped[Chapter] = relationship(back_populates="segments")
