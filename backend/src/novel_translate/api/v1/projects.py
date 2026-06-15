from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.api.deps import get_session
from novel_translate.modules.projects.schemas import ProjectCreate, ProjectRead
from novel_translate.modules.projects.service import create_project, get_project, list_projects

router = APIRouter(tags=["projects"])


@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(
    project_input: ProjectCreate,
    session: AsyncSession = Depends(get_session),
) -> ProjectRead:
    return await create_project(session, project_input)


@router.get("/projects", response_model=list[ProjectRead])
async def list_projects_endpoint(session: AsyncSession = Depends(get_session)) -> list[ProjectRead]:
    return await list_projects(session)


@router.get("/projects/{project_id}", response_model=ProjectRead)
async def get_project_endpoint(
    project_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> ProjectRead:
    project = await get_project(session, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project
