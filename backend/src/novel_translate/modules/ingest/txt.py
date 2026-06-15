from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from novel_translate.modules.ingest.segment import split_into_segments
from novel_translate.modules.projects.models import Chapter, Segment, SegmentTranslationStatus


async def import_txt_chapter(
    session: AsyncSession,
    project_id: UUID,
    title: str,
    content: str,
    order_index: int = 0,
) -> Chapter:
    chapter = Chapter(
        project_id=project_id,
        title=title,
        order_index=order_index,
        source_format="txt",
    )
    chapter.segments = [
        Segment(
            order_index=segment_index,
            source_text=source_text,
            status=SegmentTranslationStatus.pending,
        )
        for segment_index, source_text in enumerate(split_into_segments(content))
    ]

    session.add(chapter)
    await session.flush()
    await session.commit()

    imported_chapter = await session.scalar(
        select(Chapter).options(selectinload(Chapter.segments)).where(Chapter.id == chapter.id)
    )
    if imported_chapter is None:
        raise RuntimeError("Imported chapter could not be loaded after commit.")
    return imported_chapter
