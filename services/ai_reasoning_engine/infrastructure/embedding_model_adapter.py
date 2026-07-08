import os
from typing import List
# Using a lightweight local model via sentence_transformers
# We load this once at module import to avoid reloading it on every request
from sentence_transformers import SentenceTransformer
from services.ai_reasoning_engine.application.ports import EmbeddingModelPort
from shared.logging_engine import get_logger

logger = get_logger(__name__)

# "all-MiniLM-L6-v2" is ~90MB and highly efficient for this use case
MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

_model = None

def get_model():
    global _model
    if _model is None:
        logger.info("Loading embedding model into memory", model=MODEL_NAME)
        _model = SentenceTransformer(MODEL_NAME)
    return _model

class SentenceTransformerAdapter(EmbeddingModelPort):
    def __init__(self):
        # Trigger load
        get_model()

    async def embed_text(self, text: str) -> List[float]:
        # Using run_in_executor to avoid blocking the async event loop during CPU-bound inference
        import asyncio
        loop = asyncio.get_event_loop()
        
        # embed text returns a numpy array, we convert to list of floats
        vector = await loop.run_in_executor(None, lambda: get_model().encode(text).tolist())
        return vector
