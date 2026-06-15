from uuid import UUID

from pydantic import BaseModel, ConfigDict

from novel_translate.modules.glossary.models import TermConstraint, TermScope, TermStatus


class GlossaryTermRead(BaseModel):
    id: UUID
    project_id: UUID
    source: str
    target: str
    aliases: list[str]
    scope: TermScope
    status: TermStatus
    constraint_kind: TermConstraint
    notes: str | None

    model_config = ConfigDict(from_attributes=True)
