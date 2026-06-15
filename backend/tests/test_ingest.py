from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.ingest.txt import import_txt_chapter
from novel_translate.modules.projects.models import SegmentTranslationStatus
from novel_translate.modules.projects.schemas import ProjectCreate
from novel_translate.modules.projects.service import create_project


async def test_import_txt_chapter_creates_pending_segments(db_session: AsyncSession) -> None:
    project = await create_project(db_session, ProjectCreate(name="短篇"))

    chapter = await import_txt_chapter(
        db_session,
        project_id=project.id,
        title="开端",
        content="一段。\n\n二段。\n\n三段。",
    )

    assert chapter.title == "开端"
    assert chapter.source_format == "txt"
    assert [segment.order_index for segment in chapter.segments] == [0, 1, 2]
    assert [segment.source_text for segment in chapter.segments] == ["一段。", "二段。", "三段。"]
    assert {segment.status for segment in chapter.segments} == {SegmentTranslationStatus.pending}
