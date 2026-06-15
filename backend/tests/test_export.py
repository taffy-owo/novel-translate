from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.exports.chapter import export_chapter_txt
from novel_translate.modules.ingest.txt import import_txt_chapter
from novel_translate.modules.projects.schemas import ProjectCreate
from novel_translate.modules.projects.service import create_project


async def test_export_chapter_txt_prefers_target_text(db_session: AsyncSession) -> None:
    project = await create_project(db_session, ProjectCreate(name="导出"))
    chapter = await import_txt_chapter(
        db_session,
        project_id=project.id,
        title="第一章",
        content="原文一\n\n原文二",
    )
    chapter.segments[0].target_text = "译文一"
    chapter.segments[1].target_text = "译文二"
    await db_session.commit()

    exported_text = await export_chapter_txt(db_session, chapter.id)

    assert exported_text == "译文一\n\n译文二"


async def test_export_chapter_txt_falls_back_to_source_text(db_session: AsyncSession) -> None:
    project = await create_project(db_session, ProjectCreate(name="回退"))
    chapter = await import_txt_chapter(
        db_session,
        project_id=project.id,
        title="第一章",
        content="原文一\n\n原文二",
    )
    chapter.segments[0].target_text = "译文一"
    await db_session.commit()

    exported_text = await export_chapter_txt(db_session, chapter.id)

    assert exported_text == "译文一\n\n原文二"
