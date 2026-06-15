from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.glossary.models import GlossaryTerm, TermStatus
from novel_translate.modules.projects.models import Project, Segment
from novel_translate.modules.translation.schemas import (
    GlossaryTermRef,
    LocalContext,
    TranslateSegmentRequest,
)


async def build_translate_request(
    session: AsyncSession, segment: Segment, project: Project
) -> TranslateSegmentRequest:
    """Assemble the per-segment translation request.

    Local context is the immediately neighbouring segments' source text within the same
    chapter (by order_index), giving the model the surrounding prose without the whole
    chapter. Glossary terms are the project's approved terms (with a filled target) whose
    source actually occurs in this segment — keeping the constraint set focused and the
    prompt small. Style guide and memory hits remain for a later phase.
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

    approved_terms = await session.scalars(
        select(GlossaryTerm).where(
            GlossaryTerm.project_id == project.id,
            GlossaryTerm.status == TermStatus.approved,
        )
    )
    glossary_terms = [
        GlossaryTermRef(source=term.source, target=term.target, constraint=term.constraint_kind.value)
        for term in approved_terms
        if term.target and term.source in segment.source_text
    ]

    return TranslateSegmentRequest(
        source_text=segment.source_text,
        source_lang=project.source_lang,
        target_lang=project.target_lang,
        local_context=LocalContext(prev=previous_source, next=following_source),
        glossary_terms=glossary_terms,
    )
