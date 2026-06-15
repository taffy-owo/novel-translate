from collections.abc import AsyncIterator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.api.deps import get_arq_pool
from novel_translate.api.main import app
from novel_translate.modules.ingest.txt import import_txt_chapter
from novel_translate.modules.projects.schemas import ProjectCreate
from novel_translate.modules.projects.service import create_project


class _RecordingArqPool:
    def __init__(self) -> None:
        self.enqueued_jobs: list[tuple[str, tuple[object, ...]]] = []

    async def enqueue_job(self, function: str, *args: object, **_: object) -> None:
        self.enqueued_jobs.append((function, args))
        return None


async def test_translate_endpoint_enqueues_one_job_per_pending_segment(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    project = await create_project(db_session, ProjectCreate(name="入队"))
    chapter = await import_txt_chapter(
        session=db_session,
        project_id=project.id,
        title="第一章",
        content="原文一\n\n原文二\n\n原文三",
    )
    await db_session.commit()

    recording_pool = _RecordingArqPool()

    async def _override_get_arq_pool() -> AsyncIterator[_RecordingArqPool]:
        yield recording_pool

    app.dependency_overrides[get_arq_pool] = _override_get_arq_pool
    try:
        response = await client.post(f"/api/v1/chapters/{chapter.id}/translate")
    finally:
        app.dependency_overrides.pop(get_arq_pool, None)

    assert response.status_code == 202
    body = response.json()
    assert body["enqueued"] == 3
    assert len(recording_pool.enqueued_jobs) == 3
    assert all(function == "translate_segment" for function, _ in recording_pool.enqueued_jobs)
    assert {args[0] for _, args in recording_pool.enqueued_jobs} == {
        str(segment.id) for segment in chapter.segments
    }


async def test_translate_endpoint_returns_404_for_missing_chapter(client: AsyncClient) -> None:
    from uuid import uuid4

    # get_arq_pool is resolved for every request to this route, so override it even on the
    # 404 path to keep the test free of a live Redis dependency.
    async def _override_get_arq_pool() -> AsyncIterator[_RecordingArqPool]:
        yield _RecordingArqPool()

    app.dependency_overrides[get_arq_pool] = _override_get_arq_pool
    try:
        response = await client.post(f"/api/v1/chapters/{uuid4()}/translate")
    finally:
        app.dependency_overrides.pop(get_arq_pool, None)

    assert response.status_code == 404
