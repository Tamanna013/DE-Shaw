from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from services.ai_reasoning_engine.domain.entities import HistoricalFailureInfo
from services.ai_reasoning_engine.application.ports import EmbeddingRepositoryPort
from shared.db.models.embeddings import FailureEmbeddingModel
from shared.db.models.failures import FailureModel

class PgVectorRepository(EmbeddingRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_similar_failures(self, vector: List[float], repository_id: str, threshold: float = 0.75, top_k: int = 5) -> List[HistoricalFailureInfo]:
        # Perform cosine similarity search utilizing the pgvector extension
        # 1 - cosine_distance = cosine_similarity
        similarity_expr = 1 - FailureEmbeddingModel.vector.cosine_distance(vector)
        
        # In a real system, we'd join with TestRunModel and RepositoryModel to filter by repository_id
        # For simplicity in this mock, we just filter embeddings directly.
        stmt = (
            select(FailureEmbeddingModel, FailureModel, similarity_expr.label("similarity"))
            .join(FailureModel, FailureModel.embedding_id == FailureEmbeddingModel.id)
            .where(similarity_expr >= threshold)
            .order_by(FailureEmbeddingModel.vector.cosine_distance(vector))
            .limit(top_k)
        )
        
        result = await self.session.execute(stmt)
        
        historical_failures = []
        for emb, fail, sim in result:
            historical_failures.append(HistoricalFailureInfo(
                id=fail.id,
                test_case_id=fail.test_case_execution_id, # Simplified for mock
                normalized_signature=fail.normalized_signature or "unknown",
                similarity_score=float(sim),
                resolution_notes=None # E.g., we would join a resolution table here
            ))
            
        return historical_failures

    async def save_embedding(self, failure_id: str, vector: List[float], model_name: str) -> None:
        model = FailureEmbeddingModel(
            vector=vector,
            model_name=model_name
        )
        self.session.add(model)
        await self.session.flush() # Get ID
        
        # Update the failure record to point to this embedding
        stmt = select(FailureModel).where(FailureModel.id == failure_id)
        result = await self.session.execute(stmt)
        fail = result.scalar_one_or_none()
        if fail:
            fail.embedding_id = model.id
            
        await self.session.commit()
