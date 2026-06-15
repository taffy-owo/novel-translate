from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from novel_translate.modules.glossary.models import TermConstraint, TermScope, TermStatus


class GlossaryTermCreate(BaseModel):
    source: str
    target: str
    aliases: list[str] = Field(default_factory=list)
    scope: TermScope = TermScope.project
    constraint_kind: TermConstraint = TermConstraint.soft
    notes: str | None = None


class GlossaryTermUpdate(BaseModel):
    # Only provided fields are applied (partial update); status transitions have dedicated
    # endpoints (approve/deprecate) but may also be set here when editing in bulk.
    target: str | None = None
    aliases: list[str] | None = None
    scope: TermScope | None = None
    constraint_kind: TermConstraint | None = None
    status: TermStatus | None = None
    notes: str | None = None


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
