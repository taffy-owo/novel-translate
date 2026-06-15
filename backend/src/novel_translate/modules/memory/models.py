import enum
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from novel_translate.db.base import Base

# Dimension of the snapshot embedding vector. 1536 matches common text-embedding models;
# changing it is a schema migration, not a runtime toggle.
EMBEDDING_DIMENSIONS = 1536


class SnapshotLevel(str, enum.Enum):
    book = "book"
    volume = "volume"
    chapter = "chapter"


class MemorySnapshot(Base):
    __tablename__ = "memory_snapshots"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
    )
    level: Mapped[SnapshotLevel] = mapped_column(Enum(SnapshotLevel, name="memory_snapshot_level"))
    version: Mapped[str] = mapped_column(String(64))
    content: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'::jsonb")
    )
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIMENSIONS), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
