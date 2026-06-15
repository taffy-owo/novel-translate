"""Glossary knowledge layer.

Automatic term extraction and the draft -> approved -> deprecated approval workflow
belong to the hierarchical-knowledge phase (research report milestone d1). T5 only lands
the storage schema, so these operations are intentionally unimplemented stubs that mark
the seams the later phase fills in.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.glossary.models import GlossaryTerm


async def extract_term_candidates(session: AsyncSession, project_id: UUID) -> list[GlossaryTerm]:
    raise NotImplementedError("Glossary term extraction lands in research report milestone d1.")


async def approve_term(session: AsyncSession, term_id: UUID) -> GlossaryTerm:
    raise NotImplementedError("Glossary approval workflow lands in research report milestone d1.")
