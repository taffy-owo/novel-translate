from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.projects.models import Chapter, Segment


async def export_chapter_txt(session: AsyncSession, chapter_id: UUID) -> str | None:
    chapter = await session.get(Chapter, chapter_id)
    if chapter is None:
        return None

    segments = await session.scalars(
        select(Segment).where(Segment.chapter_id == chapter_id).order_by(Segment.order_index)
    )
    return "\n\n".join(segment.target_text or segment.source_text for segment in segments)
