from uuid import UUID

from arq.connections import ArqRedis
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from novel_translate.api.deps import get_arq_pool, get_session
from novel_translate.modules.exports.chapter import export_chapter_txt
from novel_translate.modules.ingest.txt import import_txt_chapter
from novel_translate.modules.projects.models import Chapter, SegmentTranslationStatus
from novel_translate.modules.projects.schemas import ChapterRead, TxtChapterImport
from novel_translate.modules.projects.service import get_project

router = APIRouter(tags=["chapters"])


class ChapterTranslationEnqueued(BaseModel):
    chapter_id: UUID
    enqueued: int


async def read_chapter_with_segments(session: AsyncSession, chapter_id: UUID) -> Chapter | None:
    return await session.scalar(
        select(Chapter).options(selectinload(Chapter.segments)).where(Chapter.id == chapter_id)
    )


@router.post("/projects/{project_id}/chapters/import-txt", response_model=ChapterRead)
async def import_txt_chapter_endpoint(
    project_id: UUID,
    chapter_import: TxtChapterImport,
    session: AsyncSession = Depends(get_session),
) -> ChapterRead:
    project = await get_project(session, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    chapter = await import_txt_chapter(
        session=session,
        project_id=project_id,
        title=chapter_import.title,
        content=chapter_import.content,
    )
    return chapter


@router.get("/chapters/{chapter_id}", response_model=ChapterRead)
async def get_chapter_endpoint(
    chapter_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ChapterRead:
    chapter = await read_chapter_with_segments(session, chapter_id)
    if chapter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return chapter


@router.post(
    "/chapters/{chapter_id}/translate",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=ChapterTranslationEnqueued,
)
async def translate_chapter_endpoint(
    chapter_id: UUID,
    session: AsyncSession = Depends(get_session),
    arq_pool: ArqRedis = Depends(get_arq_pool),
) -> ChapterTranslationEnqueued:
    chapter = await read_chapter_with_segments(session, chapter_id)
    if chapter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    pending_segments = [
        segment
        for segment in chapter.segments
        if segment.status == SegmentTranslationStatus.pending
    ]
    for segment in pending_segments:
        await arq_pool.enqueue_job("translate_segment", str(segment.id))

    return ChapterTranslationEnqueued(chapter_id=chapter_id, enqueued=len(pending_segments))


@router.get("/chapters/{chapter_id}/export", response_class=PlainTextResponse)
async def export_chapter_endpoint(
    chapter_id: UUID,
    export_format: str = Query("txt", alias="format"),
    session: AsyncSession = Depends(get_session),
) -> PlainTextResponse:
    if export_format != "txt":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only txt is supported")

    exported_text = await export_chapter_txt(session, chapter_id)
    if exported_text is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return PlainTextResponse(exported_text)
