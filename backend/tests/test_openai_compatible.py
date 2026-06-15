import httpx
import pytest
import respx

from novel_translate.core.config import Settings
from novel_translate.modules.providers.openai_compatible import OpenAICompatibleAdapter
from novel_translate.modules.translation.schemas import LocalContext, TranslateSegmentRequest


@respx.mock
async def test_openai_compatible_adapter_returns_translation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for proxy_variable in (
        "ALL_PROXY",
        "all_proxy",
        "HTTP_PROXY",
        "http_proxy",
        "HTTPS_PROXY",
        "https_proxy",
    ):
        monkeypatch.delenv(proxy_variable, raising=False)

    provider_route = respx.post("https://provider.test/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 1,
                "model": "test-model",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "译文"},
                        "finish_reason": "stop",
                    }
                ],
            },
        )
    )
    adapter = OpenAICompatibleAdapter(
        Settings(
            openai_base_url="https://provider.test/v1",
            openai_api_key="test-key",
            openai_model="test-model",
        )
    )
    request = TranslateSegmentRequest(
        source_text="原文",
        source_lang="ja",
        target_lang="zh-CN",
        local_context=LocalContext(prev=None, next=None),
    )

    translation_result = await adapter.translate(request)

    assert translation_result.translation == "译文"
    assert provider_route.called
