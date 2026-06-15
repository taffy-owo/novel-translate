from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.projects.models import Project, Segment
from novel_translate.modules.translation.schemas import LocalContext, TranslateSegmentRequest


async def build_translate_request(
    session: AsyncSession, segment: Segment, project: Project
) -> TranslateSegmentRequest:
    """Assemble the per-segment translation request.

    Local context is the immediately neighbouring segments' source text within the same
    chapter (by order_index), which gives the model the surrounding prose without sending
    the whole chapter. Glossary, style guide, and memory hits are left empty here; they are
    populated by the knowledge layer in a later phase.
    """
    previous_source = await session.scalar(
        select(Segment.source_text)
        .where(
            Segment.chapter_id == segment.chapter_id,
            Segment.order_index < segment.order_index,
        )
        .order_by(Segment.order_index.desc())
        .limit(1)
    )
    following_source = await session.scalar(
        select(Segment.source_text)
        .where(
            Segment.chapter_id == segment.chapter_id,
            Segment.order_index > segment.order_index,
        )
        .order_by(Segment.order_index.asc())
        .limit(1)
    )
    return TranslateSegmentRequest(
        source_text=segment.source_text,
        source_lang=project.source_lang,
        target_lang=project.target_lang,
        local_context=LocalContext(prev=previous_source, next=following_source),
    )
