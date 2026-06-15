from typing import Any
from uuid import UUID

from novel_translate.modules.projects.models import Chapter, Project, Segment, SegmentTranslationStatus
from novel_translate.modules.providers.registry import get_provider
from novel_translate.modules.translation.request import build_translate_request


async def translate_segment(ctx: dict[str, Any], segment_id: str) -> None:
    """Translate one segment and persist the outcome.

    Contract: the job is idempotent — only `pending` segments are processed, so a
    re-enqueued or retried job is a no-op once a segment has moved on. A provider or
    transport failure is recorded on the segment (status=error) and never propagated,
    so one bad segment cannot crash the worker or poison the queue.
    """
    session_factory = ctx["session_factory"]
    async with session_factory() as session:
        segment = await session.get(Segment, UUID(segment_id))
        if segment is None or segment.status != SegmentTranslationStatus.pending:
            return

        segment.status = SegmentTranslationStatus.translating
        await session.commit()

        chapter = await session.get(Chapter, segment.chapter_id)
        project = await session.get(Project, chapter.project_id)
        request = await build_translate_request(session, segment, project)
        provider_kind = (
            project.provider_config.get("kind")
            if isinstance(project.provider_config, dict)
            else None
        )

        try:
            adapter = get_provider(provider_kind)
            rate_limiter = ctx.get("rate_limiter")
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
