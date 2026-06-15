from openai import AsyncOpenAI

from novel_translate.core.config import Settings, get_settings
from novel_translate.modules.providers.base import ProviderAdapter
from novel_translate.modules.translation.prompt import build_messages
from novel_translate.modules.translation.schemas import TranslateSegmentRequest, TranslateSegmentResult


class OpenAICompatibleAdapter(ProviderAdapter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def translate(self, req: TranslateSegmentRequest) -> TranslateSegmentResult:
        system_prompt, user_content = build_messages(req)
        client = AsyncOpenAI(
            base_url=self.settings.openai_base_url,
            api_key=self.settings.openai_api_key or "noauth",
        )
        provider_response = await client.chat.completions.create(
            model=self.settings.openai_model,
            temperature=0.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )
        translation = provider_response.choices[0].message.content or ""
        return TranslateSegmentResult(translation=translation)
