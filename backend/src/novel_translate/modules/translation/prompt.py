import json

from novel_translate.modules.translation.schemas import TranslateSegmentRequest


def build_messages(req: TranslateSegmentRequest) -> tuple[str, str]:
    system_prompt = (
        f"You are a literary translator working from {req.source_lang} to {req.target_lang}. "
        "Translate the supplied segment with natural literary prose, preserve meaningful line "
        "breaks, respect local context, and obey glossary terms marked as hard constraints. "
        "Return only the translated segment text."
    )
    user_content = json.dumps(req.model_dump(mode="json", by_alias=True), ensure_ascii=False)
    return system_prompt, user_content
