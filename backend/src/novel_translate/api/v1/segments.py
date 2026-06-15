from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.api.deps import get_session
from novel_translate.modules.projects.models import Segment
from novel_translate.modules.projects.schemas import SegmentRead, SegmentTranslationEdit

router = APIRouter(tags=["segments"])


@router.put("/segments/{segment_id}", response_model=SegmentRead)
async def update_segment_translation_endpoint(
    segment_id: UUID,
    translation_edit: SegmentTranslationEdit,
    session: AsyncSession = Depends(get_session),
) -> SegmentRead:
    segment = await session.get(Segment, segment_id)
    if segment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Segment not found")

    segment.target_text = translation_edit.target_text
    await session.flush()
    await session.commit()
    return segment
