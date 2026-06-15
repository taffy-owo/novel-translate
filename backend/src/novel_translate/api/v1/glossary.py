from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.api.deps import get_session
from novel_translate.modules.glossary import service
from novel_translate.modules.glossary.models import TermStatus
from novel_translate.modules.glossary.schemas import (
    GlossaryTermCreate,
    GlossaryTermRead,
    GlossaryTermUpdate,
)
from novel_translate.modules.projects.service import get_project

router = APIRouter(tags=["glossary"])


@router.post(
    "/projects/{project_id}/glossary",
    response_model=GlossaryTermRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_glossary_term(
    project_id: UUID,
    term_input: GlossaryTermCreate,
    session: AsyncSession = Depends(get_session),
) -> GlossaryTermRead:
    if await get_project(session, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return await service.create_term(session, project_id, term_input)


@router.get("/projects/{project_id}/glossary", response_model=list[GlossaryTermRead])
async def list_glossary_terms(
    project_id: UUID,
    term_status: TermStatus | None = Query(default=None, alias="status"),
    session: AsyncSession = Depends(get_session),
) -> list[GlossaryTermRead]:
    return await service.list_terms(session, project_id, term_status)


@router.post(
    "/projects/{project_id}/glossary/extract",
    response_model=list[GlossaryTermRead],
    status_code=status.HTTP_201_CREATED,
)
async def extract_glossary_candidates(
    project_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> list[GlossaryTermRead]:
    if await get_project(session, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return await service.extract_term_candidates(session, project_id)


@router.put("/glossary/{term_id}", response_model=GlossaryTermRead)
async def update_glossary_term(
    term_id: UUID,
    term_update: GlossaryTermUpdate,
    session: AsyncSession = Depends(get_session),
) -> GlossaryTermRead:
    term = await service.update_term(session, term_id, term_update)
    if term is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
    return term


@router.post("/glossary/{term_id}/approve", response_model=GlossaryTermRead)
async def approve_glossary_term(
    term_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> GlossaryTermRead:
    term = await service.approve_term(session, term_id)
    if term is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
    return term
