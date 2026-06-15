from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from novel_translate.modules.projects.models import SegmentTranslationStatus


class ProjectCreate(BaseModel):
    name: str
    source_lang: str = "ja"
    target_lang: str = "zh-CN"
    provider_config: dict[str, Any] | None = None


class ProjectRead(BaseModel):
    id: UUID
    name: str
    source_lang: str
    target_lang: str
    provider_config: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TxtChapterImport(BaseModel):
    title: str
    content: str


class SegmentRead(BaseModel):
    id: UUID
    order_index: int
    source_text: str
    target_text: str | None
    status: SegmentTranslationStatus
    error: str | None

    model_config = ConfigDict(from_attributes=True)


class ChapterRead(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    order_index: int
    source_format: str
    created_at: datetime
    segments: list[SegmentRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class SegmentTranslationEdit(BaseModel):
    target_text: str | None
