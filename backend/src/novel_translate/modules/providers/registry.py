from novel_translate.core.config import get_settings
from novel_translate.modules.providers.anthropic import AnthropicAdapter
from novel_translate.modules.providers.base import ProviderAdapter
from novel_translate.modules.providers.openai_compatible import OpenAICompatibleAdapter

provider_adapter_classes: dict[str, type[ProviderAdapter]] = {
    "openai_compatible": OpenAICompatibleAdapter,
    "anthropic": AnthropicAdapter,
}


def get_provider(kind: str | None = None) -> ProviderAdapter:
    settings = get_settings()
    provider_kind = kind or settings.nt_provider_kind
    try:
        adapter_class = provider_adapter_classes[provider_kind]
    except KeyError as exc:
        raise ValueError(f"Unknown provider kind: {provider_kind}") from exc
    return adapter_class(settings)
