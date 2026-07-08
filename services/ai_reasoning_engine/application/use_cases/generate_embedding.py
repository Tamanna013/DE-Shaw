from typing import List
from services.ai_reasoning_engine.application.ports import EmbeddingModelPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class GenerateEmbeddingUseCase:
    def __init__(self, model_adapter: EmbeddingModelPort):
        self.model_adapter = model_adapter

    async def execute(self, text: str) -> List[float]:
        try:
            return await self.model_adapter.embed_text(text)
        except Exception as e:
            logger.error("Failed to generate embedding", exc_info=e)
            raise
