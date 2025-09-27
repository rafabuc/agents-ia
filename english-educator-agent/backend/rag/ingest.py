"""
RAG Content Ingestion - Educational Content Processing
"""
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List
import logging
from pathlib import Path

from config import settings

logger = logging.getLogger(__name__)


class ContentIngestor:
    """Ingest and vectorize educational content."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL
        )
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION
        
    async def ingest_educational_content(self, content_dir: str = "data/english_content"):
        """Ingest and vectorize educational materials."""
        
        logger.info(f"Starting content ingestion from {content_dir}")
        
        # Create collection if doesn't exist
        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"Collection {self.collection_name} already exists")
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
            )
            logger.info(f"Created collection {self.collection_name}")
        
        # Load documents
        loader = DirectoryLoader(
            content_dir,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        try:
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} documents")
        except Exception as e:
            logger.error(f"Failed to load documents: {e}")
            return
        
        # Chunking strategy
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")
        
        # Enrich metadata
        for chunk in chunks:
            chunk.metadata.update({
                "topic": self._extract_topic(chunk.page_content),
                "level": self._determine_level_from_path(chunk.metadata.get("source", "")),
                "type": self._categorize_content(chunk.page_content)
            })
        
        # Vectorize and upload
        await self._vectorize_and_upload(chunks)
        
        logger.info(f"Successfully ingested {len(chunks)} chunks")
    
    async def _vectorize_and_upload(self, chunks: List, batch_size: int = 100):
        """Vectorize chunks and upload to Qdrant."""
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            points = []
            
            for idx, chunk in enumerate(batch):
                try:
                    # Generate embedding
                    embedding = await self.embeddings.aembed_query(chunk.page_content)
                    
                    points.append(
                        PointStruct(
                            id=i + idx,
                            vector=embedding,
                            payload={
                                "text": chunk.page_content,
                                "metadata": chunk.metadata
                            }
                        )
                    )
                except Exception as e:
                    logger.error(f"Failed to embed chunk {i + idx}: {e}")
                    continue
            
            # Upload batch
            if points:
                try:
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    logger.info(f"Uploaded batch {i // batch_size + 1}")
                except Exception as e:
                    logger.error(f"Failed to upload batch: {e}")
    
    def _extract_topic(self, text: str) -> str:
        """Extract main topic from text."""
        # Simple heuristic: first heading or first 50 chars
        lines = text.split("\n")
        for line in lines:
            if line.startswith("#"):
                return line.replace("#", "").strip()
        
        return text[:50].strip()
    
    def _determine_level_from_path(self, source_path: str) -> str:
        """Determine CEFR level from file path."""
        source_lower = source_path.lower()
        
        levels = ["a1", "a2", "b1", "b2", "c1", "c2"]
        for level in levels:
            if level in source_lower:
                return level.upper()
        
        return "B1"  # Default
    
    def _categorize_content(self, text: str) -> str:
        """Categorize content type."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["grammar", "tense", "verb", "noun"]):
            return "grammar"
        elif any(word in text_lower for word in ["vocabulary", "word", "definition"]):
            return "vocabulary"
        elif any(word in text_lower for word in ["exercise", "practice", "question"]):
            return "exercise"
        elif any(word in text_lower for word in ["lesson", "learn", "objective"]):
            return "lesson"
        else:
            return "general"


async def ingest_content():
    """Main ingestion function."""
    ingestor = ContentIngestor()
    await ingestor.ingest_educational_content()


if __name__ == "__main__":
    import asyncio
    asyncio.run(ingest_content())
