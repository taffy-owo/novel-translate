from anthropic import AsyncAnthropic

from novel_translate.core.config import Settings, get_settings
from novel_translate.modules.providers.base import ProviderAdapter
from novel_translate.modules.translation.prompt import build_messages
from novel_translate.modules.translation.schemas import TranslateSegmentRequest, TranslateSegmentResult


class AnthropicAdapter(ProviderAdapter):
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def translate(self, req: TranslateSegmentRequest) -> TranslateSegmentResult:
        system_prompt, user_content = build_messages(req)
        client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)
        provider_response = await client.messages.create(
            model=self.settings.anthropic_model or "claude-sonnet-4-6",
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
            # Temperature is omitted because newer Anthropic model families reject it.
        )
        translation = "".join(
            content_block.text
            for content_block in provider_response.content
            if content_block.type == "text"
        )
        return TranslateSegmentResult(translation=translation)
