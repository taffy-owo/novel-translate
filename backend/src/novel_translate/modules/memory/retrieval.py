"""Layered-memory retrieval.

Nearest-neighbour recall over MemorySnapshot.embedding (pgvector) is part of the
layered-memory phase (research report milestone d2). Until then this returns no hits, so
the translation pipeline can call it unconditionally without special-casing.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


async def retrieve_memory_hits(
    session: AsyncSession, project_id: UUID, query_embedding: list[float]
) -> list[dict]:
    # TODO (milestone d2): pgvector ORDER BY embedding <=> :query LIMIT k over MemorySnapshot.
    return []
