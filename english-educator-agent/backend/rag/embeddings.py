"""
Embeddings management for RAG system.
"""
from langchain_openai import OpenAIEmbeddings
from typing import List
import logging

from config import settings

logger = logging.getLogger(__name__)


class EmbeddingsManager:
    """Manage embeddings for RAG system."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text."""
        try:
            embedding = await self.embeddings.aembed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        try:
            embeddings = await self.embeddings.aembed_documents(documents)
            return embeddings
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension size."""
        model_dimensions = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        return model_dimensions.get(settings.EMBEDDING_MODEL, 1536)


# Singleton instance
_embeddings_manager = None

def get_embeddings_manager() -> EmbeddingsManager:
    """Get or create embeddings manager instance."""
    global _embeddings_manager
    if _embeddings_manager is None:
        _embeddings_manager = EmbeddingsManager()
    return _embeddings_manager
