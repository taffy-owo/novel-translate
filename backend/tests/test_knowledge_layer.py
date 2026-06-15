from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.glossary.models import (
    GlossaryTerm,
    TermConstraint,
    TermScope,
    TermStatus,
)
from novel_translate.modules.memory.models import MemorySnapshot, SnapshotLevel
from novel_translate.modules.projects.schemas import ProjectCreate
from novel_translate.modules.projects.service import create_project


async def test_glossary_term_persists_with_scope_and_constraint(db_session: AsyncSession) -> None:
    project = await create_project(db_session, ProjectCreate(name="术语"))
    term = GlossaryTerm(
        project_id=project.id,
        source="Aether Gate",
        target="以太之门",
        aliases=["以太门"],
        scope=TermScope.book,
        status=TermStatus.approved,
        constraint_kind=TermConstraint.hard,
        notes="正式设定词",
    )
    db_session.add(term)
    await db_session.commit()
    await db_session.refresh(term)

    assert term.id is not None
    assert term.aliases == ["以太门"]
    assert term.scope == TermScope.book
    assert term.constraint_kind == TermConstraint.hard


async def test_memory_snapshot_embedding_round_trips(db_session: AsyncSession) -> None:
    project = await create_project(db_session, ProjectCreate(name="记忆"))
    snapshot = MemorySnapshot(
        project_id=project.id,
        level=SnapshotLevel.book,
        version="book_v1",
        content={"characters": ["伊芙琳"]},
        embedding=[0.1] * 1536,
    )
    db_session.add(snapshot)
    await db_session.commit()
    # refresh forces a real SELECT, proving the pgvector column survived the DB round-trip.
    await db_session.refresh(snapshot)

    assert len(snapshot.embedding) == 1536
    assert abs(float(snapshot.embedding[0]) - 0.1) < 1e-3
    assert snapshot.content == {"characters": ["伊芙琳"]}
