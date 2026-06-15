"""Layered memory snapshots.

Generating book/volume/chapter snapshots (people, places, world rules, prior-chapter
summaries) is part of the layered-memory phase (research report milestone d2). T5 lands
the storage schema only; snapshot generation is an unimplemented stub here.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.memory.models import MemorySnapshot, SnapshotLevel


async def build_snapshot(
    session: AsyncSession, project_id: UUID, level: SnapshotLevel
) -> MemorySnapshot:
    raise NotImplementedError("Snapshot generation lands in research report milestone d2.")
