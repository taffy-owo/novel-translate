from typing import Any
from uuid import UUID

from novel_translate.modules.projects.models import Segment
from novel_translate.modules.translation.run import run_segment_translation


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
        if segment is None:
            return

        await run_segment_translation(session, segment, ctx.get("rate_limiter"))
