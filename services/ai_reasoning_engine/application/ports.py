from typing import Protocol, List, Optional
from services.ai_reasoning_engine.domain.entities import HistoricalFailureInfo

class LLMClientPort(Protocol):
    async def complete(self, prompt_template_id: str, context: dict) -> dict:
        """
        Takes a prompt template ID (from Module 10) and context dict.
        Returns a dict representing structured JSON from the LLM.
        """
        ...
        
class EmbeddingModelPort(Protocol):
    async def embed_text(self, text: str) -> List[float]:
        """Converts text into a vector."""
        ...

class EmbeddingRepositoryPort(Protocol):
    async def search_similar_failures(self, vector: List[float], repository_id: str, threshold: float = 0.75, top_k: int = 5) -> List[HistoricalFailureInfo]:
        """Uses pgvector cosine similarity to find nearest neighbors."""
        ...
        
    async def save_embedding(self, failure_id: str, vector: List[float], model_name: str) -> None:
        """Saves a generated embedding."""
        ...
