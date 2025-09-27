"""
Advanced Retrieval - Hybrid Search and Re-ranking
"""
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List, Dict, Optional
import logging

from config import settings

logger = logging.getLogger(__name__)


class AdvancedRetriever:
    """Advanced retrieval with hybrid search and re-ranking."""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    async def hybrid_search(
        self,
        query: str,
        student_level: str,
        filters: Optional[Dict] = None,
        k: int = 5
    ) -> List[Document]:
        """Hybrid dense vector search with filters."""
        
        # Generate query embedding
        query_embedding = await self.embeddings.aembed_query(query)
        
        # Build filters
        must_conditions = []
        
        # Level filter
        must_conditions.append(
            FieldCondition(
                key="metadata.level",
                match=MatchValue(value=student_level)
            )
        )
        
        # Additional filters
        if filters:
            if "topic" in filters:
                must_conditions.append(
                    FieldCondition(
                        key="metadata.topic",
                        match=MatchValue(value=filters["topic"])
                    )
                )
            if "type" in filters:
                must_conditions.append(
                    FieldCondition(
                        key="metadata.type",
                        match=MatchValue(value=filters["type"])
                    )
                )
        
        # Search
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=Filter(must=must_conditions) if must_conditions else None,
                limit=k * 2  # Get more for re-ranking
            )
            
            # Convert to documents
            documents = [
                Document(
                    page_content=result.payload["text"],
                    metadata=result.payload["metadata"]
                )
                for result in results
            ]
            
            # Re-rank
            reranked = await self._rerank(query, documents, k)
            
            logger.info(f"Retrieved and re-ranked {len(reranked)} documents")
            return reranked
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def multi_query_retrieval(
        self,
        query: str,
        student_level: str,
        k: int = 5
    ) -> List[Document]:
        """Multi-query retrieval for better coverage."""
        
        # Generate query variations
        variations = await self._generate_query_variations(query)
        
        all_results = []
        seen_texts = set()
        
        for q in variations:
            results = await self.hybrid_search(q, student_level, k=3)
            
            for doc in results:
                # Deduplicate
                if doc.page_content not in seen_texts:
                    all_results.append(doc)
                    seen_texts.add(doc.page_content)
        
        # Re-rank final results
        final_results = await self._rerank(query, all_results, k)
        
        return final_results
    
    async def _generate_query_variations(self, original_query: str) -> List[str]:
        """Generate query variations using LLM."""
        
        prompt = f"""Generate 3 alternative phrasings of this search query for better retrieval:

Original: "{original_query}"

Requirements:
- Keep the same meaning
- Use different words/phrases
- Make them search-friendly

Return only the 3 variations, one per line, no numbering."""
        
        try:
            response = await self.llm.ainvoke(prompt)
            variations = [original_query] + [
                line.strip() 
                for line in response.content.strip().split("\n") 
                if line.strip()
            ]
            return variations[:4]  # Original + 3 variations
        except Exception as e:
            logger.error(f"Failed to generate variations: {e}")
            return [original_query]
    
    async def _rerank(
        self,
        query: str,
        documents: List[Document],
        k: int
    ) -> List[Document]:
        """Re-rank documents using LLM."""
        
        if len(documents) <= k:
            return documents
        
        # Create ranking prompt
        docs_text = "\n\n".join([
            f"[{i}] {doc.page_content[:200]}..." 
            for i, doc in enumerate(documents)
        ])
        
        prompt = f"""Rank these documents by relevance to the query.

Query: "{query}"

Documents:
{docs_text}

Return the indices of the top {k} most relevant documents, separated by commas.
Only return the numbers, no explanation."""
        
        try:
            response = await self.llm.ainvoke(prompt)
            indices = [
                int(idx.strip()) 
                for idx in response.content.strip().split(",")
                if idx.strip().isdigit()
            ]
            
            # Return re-ranked documents
            reranked = [documents[i] for i in indices if i < len(documents)]
            
            # Fill up to k if needed
            if len(reranked) < k:
                remaining = [d for i, d in enumerate(documents) if i not in indices]
                reranked.extend(remaining[:k - len(reranked)])
            
            return reranked[:k]
            
        except Exception as e:
            logger.error(f"Re-ranking failed: {e}")
            return documents[:k]
    
    async def semantic_search(
        self,
        query: str,
        level: str,
        topic: Optional[str] = None,
        k: int = 5
    ) -> List[Document]:
        """Simple semantic search wrapper."""
        
        filters = {"topic": topic} if topic else None
        return await self.hybrid_search(query, level, filters, k)
    
    async def get_related_content(
        self,
        document: Document,
        k: int = 3
    ) -> List[Document]:
        """Find related content to a document."""
        
        # Use document content as query
        level = document.metadata.get("level", "B1")
        topic = document.metadata.get("topic")
        
        filters = {"topic": topic} if topic else None
        
        results = await self.hybrid_search(
            document.page_content[:500],  # Use beginning as query
            level,
            filters,
            k=k + 1
        )
        
        # Remove the original document
        related = [
            doc for doc in results 
            if doc.page_content != document.page_content
        ]
        
        return related[:k]


# Singleton instance
_retriever = None

def get_retriever() -> AdvancedRetriever:
    """Get or create retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = AdvancedRetriever()
    return _retriever
