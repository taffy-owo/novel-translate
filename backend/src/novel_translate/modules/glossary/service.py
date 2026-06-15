"""Glossary knowledge layer (research report milestone d1).

Implements term CRUD, the draft -> approved -> deprecated workflow, and a baseline
candidate extractor. Extraction is an explainable frequency heuristic over repeated
CJK/kana spans in the project's source text (incremental: known sources are skipped);
a fuller NER-based extractor is future work. Approved terms with a filled target are
injected into the translation request — see modules/translation/request.py.
"""

import re
from collections import Counter
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from novel_translate.modules.glossary.models import (
    GlossaryTerm,
    TermConstraint,
    TermScope,
    TermStatus,
)
from novel_translate.modules.glossary.schemas import GlossaryTermCreate, GlossaryTermUpdate
from novel_translate.modules.projects.models import Chapter, Segment

# Contiguous runs of kanji/hiragana/katakana, 2–8 chars — the units candidate terms come from.
_CJK_RUN = re.compile(r"[一-鿿぀-ヿ]{2,8}")


async def create_term(
    session: AsyncSession, project_id: UUID, term_input: GlossaryTermCreate
) -> GlossaryTerm:
    term = GlossaryTerm(
        project_id=project_id,
        source=term_input.source,
        target=term_input.target,
        aliases=term_input.aliases,
        scope=term_input.scope,
        constraint_kind=term_input.constraint_kind,
        notes=term_input.notes,
        status=TermStatus.draft,
    )
    session.add(term)
    await session.flush()
    await session.commit()
    await session.refresh(term)
    return term


async def list_terms(
    session: AsyncSession, project_id: UUID, status: TermStatus | None = None
) -> list[GlossaryTerm]:
    stmt = select(GlossaryTerm).where(GlossaryTerm.project_id == project_id)
    if status is not None:
        stmt = stmt.where(GlossaryTerm.status == status)
    stmt = stmt.order_by(GlossaryTerm.created_at, GlossaryTerm.id)
    return list(await session.scalars(stmt))


async def get_term(session: AsyncSession, term_id: UUID) -> GlossaryTerm | None:
    return await session.get(GlossaryTerm, term_id)


async def update_term(
    session: AsyncSession, term_id: UUID, term_update: GlossaryTermUpdate
) -> GlossaryTerm | None:
    term = await session.get(GlossaryTerm, term_id)
    if term is None:
        return None
    for field, value in term_update.model_dump(exclude_unset=True).items():
        setattr(term, field, value)
    await session.commit()
    await session.refresh(term)
    return term


async def _set_status(
    session: AsyncSession, term_id: UUID, status: TermStatus
) -> GlossaryTerm | None:
    term = await session.get(GlossaryTerm, term_id)
    if term is None:
        return None
    term.status = status
    await session.commit()
    await session.refresh(term)
    return term


async def approve_term(session: AsyncSession, term_id: UUID) -> GlossaryTerm | None:
    return await _set_status(session, term_id, TermStatus.approved)


async def deprecate_term(session: AsyncSession, term_id: UUID) -> GlossaryTerm | None:
    return await _set_status(session, term_id, TermStatus.deprecated)


def _candidate_sources(texts: list[str], min_count: int = 3, max_candidates: int = 30) -> list[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        for run in _CJK_RUN.findall(text):
            for n in (2, 3, 4):
                for i in range(len(run) - n + 1):
                    counter[run[i : i + n]] += 1
    frequent = {gram: count for gram, count in counter.items() if count >= min_count}
    # Prefer longer spans: drop a gram that is contained in an already-kept longer one.
    ordered = sorted(frequent, key=lambda g: (-len(g), -frequent[g]))
    kept: list[str] = []
    for gram in ordered:
        if any(gram != k and gram in k for k in kept):
            continue
        kept.append(gram)
    kept.sort(key=lambda g: (-frequent[g], -len(g)))
    return kept[:max_candidates]


async def extract_term_candidates(
    session: AsyncSession, project_id: UUID
) -> list[GlossaryTerm]:
    """Create draft term candidates from repeated source spans in the project.

    Targets are left blank for the translator to fill before approval. Sources already
    present in the project's glossary are skipped, so extraction is incremental.
    """
    sources = list(
        await session.scalars(
            select(Segment.source_text)
            .join(Chapter, Segment.chapter_id == Chapter.id)
            .where(Chapter.project_id == project_id)
        )
    )
    existing = set(
        await session.scalars(
            select(GlossaryTerm.source).where(GlossaryTerm.project_id == project_id)
        )
    )
    created: list[GlossaryTerm] = []
    for source in _candidate_sources(sources):
        if source in existing:
            continue
        term = GlossaryTerm(
            project_id=project_id,
            source=source,
            target="",
            aliases=[],
            scope=TermScope.project,
            constraint_kind=TermConstraint.soft,
            status=TermStatus.draft,
        )
        session.add(term)
        created.append(term)
    if created:
        await session.commit()
        for term in created:
            await session.refresh(term)
    return created
