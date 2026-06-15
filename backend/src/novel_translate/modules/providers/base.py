from abc import ABC, abstractmethod

from novel_translate.modules.translation.schemas import TranslateSegmentRequest, TranslateSegmentResult


class ProviderAdapter(ABC):
    @abstractmethod
    async def translate(self, req: TranslateSegmentRequest) -> TranslateSegmentResult:
        """Translate one segment according to the shared request contract."""
