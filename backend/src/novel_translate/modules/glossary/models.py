import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from novel_translate.db.base import Base


class TermScope(str, enum.Enum):
    segment = "segment"
    chapter = "chapter"
    volume = "volume"
    book = "book"
    project = "project"


class TermStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"
    deprecated = "deprecated"


class TermConstraint(str, enum.Enum):
    hard = "hard"
    soft = "soft"


class GlossaryTerm(Base):
    __tablename__ = "glossary_terms"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
    )
    source: Mapped[str] = mapped_column(String(255))
    target: Mapped[str] = mapped_column(String(255))
    aliases: Mapped[list[str]] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb")
    )
    scope: Mapped[TermScope] = mapped_column(
        Enum(TermScope, name="glossary_term_scope"),
        default=TermScope.project,
        server_default=TermScope.project.value,
    )
    status: Mapped[TermStatus] = mapped_column(
        Enum(TermStatus, name="glossary_term_status"),
        default=TermStatus.draft,
        server_default=TermStatus.draft.value,
    )
    constraint_kind: Mapped[TermConstraint] = mapped_column(
        Enum(TermConstraint, name="glossary_term_constraint"),
        default=TermConstraint.soft,
        server_default=TermConstraint.soft.value,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
