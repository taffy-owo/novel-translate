from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.projects.models import Chapter, Project, Segment, SegmentTranslationStatus
from novel_translate.modules.providers.registry import get_provider
from novel_translate.modules.translation.request import build_translate_request


async def run_segment_translation(
    session: AsyncSession, segment: Segment, rate_limiter=None
) -> Segment:
    """Translate one pending segment and persist either success or failure."""
    if segment.status != SegmentTranslationStatus.pending:
        return segment

    segment.status = SegmentTranslationStatus.translating
    await session.commit()

    chapter = await session.get(Chapter, segment.chapter_id)
    project = await session.get(Project, chapter.project_id)
    request = await build_translate_request(session, segment, project)
    provider_kind = (
        project.provider_config.get("kind") if isinstance(project.provider_config, dict) else None
    )
    try:
        adapter = get_provider(provider_kind)
        if rate_limiter is not None:
            await rate_limiter.acquire()
        result = await adapter.translate(request)
    except Exception as exc:
        segment.status = SegmentTranslationStatus.error
        segment.error = str(exc)
    else:
        segment.target_text = result.translation
        segment.status = SegmentTranslationStatus.done
        segment.error = None

    await session.commit()
    return segment
