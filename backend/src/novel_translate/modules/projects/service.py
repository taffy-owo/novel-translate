from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.projects.models import Project
from novel_translate.modules.projects.schemas import ProjectCreate


async def create_project(session: AsyncSession, project_input: ProjectCreate) -> Project:
    project = Project(
        name=project_input.name,
        source_lang=project_input.source_lang,
        target_lang=project_input.target_lang,
        provider_config=project_input.provider_config,
    )
    session.add(project)
    await session.flush()
    await session.commit()
    await session.refresh(project)
    return project


async def get_project(session: AsyncSession, project_id: UUID) -> Project | None:
    return await session.get(Project, project_id)


async def list_projects(session: AsyncSession) -> list[Project]:
    projects = await session.scalars(select(Project).order_by(Project.created_at, Project.id))
    return list(projects)
