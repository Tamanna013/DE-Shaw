from typing import List
from services.ai_reasoning_engine.domain.entities import HistoricalFailureInfo
from services.ai_reasoning_engine.application.ports import EmbeddingRepositoryPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

class RetrieveSimilarFailuresUseCase:
    def __init__(self, repo: EmbeddingRepositoryPort):
        self.repo = repo

    async def execute(self, vector: List[float], repository_id: str, threshold: float = 0.75, top_k: int = 5) -> List[HistoricalFailureInfo]:
        try:
            results = await self.repo.search_similar_failures(vector, repository_id, threshold, top_k)
            logger.info("Retrieved similar failures", count=len(results), threshold=threshold)
            return results
        except Exception as e:
            logger.error("Failed to retrieve similar failures", exc_info=e)
            return []
