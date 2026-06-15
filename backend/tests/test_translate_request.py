from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.glossary import service as glossary_service
from novel_translate.modules.glossary.schemas import GlossaryTermCreate
from novel_translate.modules.ingest.txt import import_txt_chapter
from novel_translate.modules.projects.models import Segment
from novel_translate.modules.projects.schemas import ProjectCreate
from novel_translate.modules.projects.service import create_project
from novel_translate.modules.translation.request import build_translate_request


async def test_build_request_injects_only_approved_terms_present_in_segment(
    db_session: AsyncSession,
) -> None:
    project = await create_project(db_session, ProjectCreate(name="注入"))
    chapter = await import_txt_chapter(
        session=db_session,
        project_id=project.id,
        title="第一章",
        content="魔法使いのアリスが現れた。",
    )

    # 已审批且出现在本段 -> 应注入
    hit = await glossary_service.create_term(
        db_session,
        project.id,
        GlossaryTermCreate(source="アリス", target="爱丽丝", constraint_kind="hard"),
    )
    await glossary_service.approve_term(db_session, hit.id)
    # 已审批但不在本段 -> 排除
    absent = await glossary_service.create_term(
        db_session, project.id, GlossaryTermCreate(source="ドラゴン", target="龙")
    )
    await glossary_service.approve_term(db_session, absent.id)
    # 在本段但仍是草稿（未审批）-> 排除
    await glossary_service.create_term(
        db_session, project.id, GlossaryTermCreate(source="魔法", target="魔法")
    )

    segment = await db_session.scalar(select(Segment).where(Segment.chapter_id == chapter.id))
    request = await build_translate_request(db_session, segment, project)

    refs = {(r.source, r.target, r.constraint) for r in request.glossary_terms}
    assert ("アリス", "爱丽丝", "hard") in refs
    assert all(r.source != "ドラゴン" for r in request.glossary_terms)
    assert all(r.source != "魔法" for r in request.glossary_terms)
