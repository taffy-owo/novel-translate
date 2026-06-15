from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LocalContext(BaseModel):
    prev: str | None = None
    next: str | None = None


class GlossaryTermRef(BaseModel):
    source: str
    target: str
    constraint: str


class StyleGuide(BaseModel):
    register_: str = Field(alias="register")
    pov: str | None = None
    dialogue_policy: str
    line_break_policy: str

    model_config = ConfigDict(populate_by_name=True)


class TranslateSegmentRequest(BaseModel):
    source_text: str
    source_lang: str
    target_lang: str
    local_context: LocalContext
    glossary_terms: list[GlossaryTermRef] = Field(default_factory=list)
    style_guide: StyleGuide | None = None
    memory_hits: list[dict[str, Any]] = Field(default_factory=list)


class TranslateSegmentResult(BaseModel):
    translation: str
    new_term_candidates: list[dict[str, Any]] = Field(default_factory=list)
    consistency_warnings: list[str] = Field(default_factory=list)
    summary_delta: str | None = None
