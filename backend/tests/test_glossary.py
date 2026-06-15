from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.ingest.txt import import_txt_chapter
from novel_translate.modules.projects.models import Project
from novel_translate.modules.projects.schemas import ProjectCreate
from novel_translate.modules.projects.service import create_project


async def _make_project(db_session: AsyncSession) -> Project:
    return await create_project(db_session, ProjectCreate(name="术语项目"))


async def test_create_list_approve_term(client: AsyncClient, db_session: AsyncSession) -> None:
    project = await _make_project(db_session)
    pid = str(project.id)

    created = await client.post(
        f"/api/v1/projects/{pid}/glossary",
        json={"source": "アリス", "target": "爱丽丝", "constraint_kind": "hard"},
    )
    assert created.status_code == 201
    term = created.json()
    assert term["status"] == "draft"
    assert term["constraint_kind"] == "hard"

    listed = await client.get(f"/api/v1/projects/{pid}/glossary")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    approved = await client.post(f"/api/v1/glossary/{term['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    only_approved = await client.get(
        f"/api/v1/projects/{pid}/glossary", params={"status": "approved"}
    )
    assert len(only_approved.json()) == 1


async def test_update_term_and_404(client: AsyncClient, db_session: AsyncSession) -> None:
    project = await _make_project(db_session)
    term_id = (
        await client.post(
            f"/api/v1/projects/{project.id}/glossary",
            json={"source": "魔法", "target": "魔法"},
        )
    ).json()["id"]

    updated = await client.put(
        f"/api/v1/glossary/{term_id}", json={"target": "法术", "notes": "改用法术"}
    )
    assert updated.status_code == 200
    assert updated.json()["target"] == "法术"
    assert updated.json()["notes"] == "改用法术"

    missing = await client.put(f"/api/v1/glossary/{uuid4()}", json={"target": "x"})
    assert missing.status_code == 404


async def test_extract_candidates_from_repeated_spans(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    project = await _make_project(db_session)
    await import_txt_chapter(
        session=db_session,
        project_id=project.id,
        title="第一章",
        content="アリスは笑った。\n\nアリスは泣いた。\n\nアリスは走った。",
    )
    await db_session.commit()

    resp = await client.post(f"/api/v1/projects/{project.id}/glossary/extract")
    assert resp.status_code == 201
    candidates = resp.json()
    assert candidates, "应至少抽取出一个候选术语"
    assert all(c["status"] == "draft" for c in candidates)
    assert any("アリス" in c["source"] for c in candidates)
