from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from novel_translate.modules.ingest.txt import import_txt_chapter
from novel_translate.modules.projects.models import Segment, SegmentTranslationStatus
from novel_translate.modules.projects.schemas import ProjectCreate
from novel_translate.modules.projects.service import create_project
from novel_translate.modules.translation import run as translation_run
from novel_translate.modules.translation.schemas import TranslateSegmentRequest, TranslateSegmentResult
from novel_translate.worker.tasks.translate_segment import translate_segment


class _StubAdapter:
    def __init__(self, *, translation: str | None = None, error: Exception | None = None) -> None:
        self._translation = translation
        self._error = error

    async def translate(self, request: TranslateSegmentRequest) -> TranslateSegmentResult:
        if self._error is not None:
            raise self._error
        assert self._translation is not None
        return TranslateSegmentResult(translation=self._translation)


async def _seed_pending_segment(session_factory: async_sessionmaker) -> str:
    async with session_factory() as session:
        project = await create_project(session, ProjectCreate(name="任务"))
        chapter = await import_txt_chapter(
            session=session,
            project_id=project.id,
            title="第一章",
            content="原文一\n\n原文二",
        )
        await session.commit()
        first_segment = await session.scalar(
            select(Segment)
            .where(Segment.chapter_id == chapter.id)
            .order_by(Segment.order_index)
            .limit(1)
        )
        return str(first_segment.id)


async def test_translate_segment_marks_segment_done(
    session_factory: async_sessionmaker, monkeypatch: pytest.MonkeyPatch
) -> None:
    segment_id = await _seed_pending_segment(session_factory)
    monkeypatch.setattr(
        translation_run,
        "get_provider",
        lambda kind=None: _StubAdapter(translation="译文"),
    )

    await translate_segment({"session_factory": session_factory}, segment_id)

    async with session_factory() as session:
        segment = await session.get(Segment, UUID(segment_id))
        assert segment.status == SegmentTranslationStatus.done
        assert segment.target_text == "译文"
        assert segment.error is None


async def test_translate_segment_records_provider_error(
    session_factory: async_sessionmaker, monkeypatch: pytest.MonkeyPatch
) -> None:
    segment_id = await _seed_pending_segment(session_factory)
    monkeypatch.setattr(
        translation_run,
        "get_provider",
        lambda kind=None: _StubAdapter(error=RuntimeError("provider down")),
    )

    await translate_segment({"session_factory": session_factory}, segment_id)

    async with session_factory() as session:
        segment = await session.get(Segment, UUID(segment_id))
        assert segment.status == SegmentTranslationStatus.error
        assert segment.error == "provider down"
        assert segment.target_text is None


async def test_translate_segment_records_provider_resolution_error(
    session_factory: async_sessionmaker, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A misconfigured provider kind raises when the adapter is resolved (before any
    # translate call). That failure must be recorded on the segment (status=error),
    # not propagated out of the job — otherwise the segment is stranded in `translating`.
    segment_id = await _seed_pending_segment(session_factory)

    def _raise_unknown_provider(kind: str | None = None):
        raise ValueError("Unknown provider kind: bogus")

    monkeypatch.setattr(translation_run, "get_provider", _raise_unknown_provider)

    await translate_segment({"session_factory": session_factory}, segment_id)

    async with session_factory() as session:
        segment = await session.get(Segment, UUID(segment_id))
        assert segment.status == SegmentTranslationStatus.error
        assert "Unknown provider kind" in segment.error
        assert segment.target_text is None
