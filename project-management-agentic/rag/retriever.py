from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback Document class
    class Document:
        def __init__(self, page_content, metadata=None):
            self.page_content = page_content
            self.metadata = metadata or {}
    LANGCHAIN_AVAILABLE = False

from .vector_store import VectorStoreManager
from .document_processor import DocumentProcessor
from config.settings import settings
from utils.logger import logger


class RAGRetriever:
    """Main RAG retrieval system."""
    
    def __init__(self):
        self.vector_store_manager = VectorStoreManager()
        self.document_processor = DocumentProcessor()
        self.query_history = []
        
        logger.info("RAGRetriever initialized successfully")
    
    def ingest_knowledge_base(self, knowledge_base_path: str = None):
        """Ingest documents from knowledge base directory."""
        if not knowledge_base_path:
            knowledge_base_path = settings.knowledge_base_path
        
        try:
            logger.info(f"Starting knowledge base ingestion from: {knowledge_base_path}")
            
            # Process documents
            documents = self.document_processor.process_directory(
                directory_path=knowledge_base_path,
                source_type="knowledge_base"
            )
            
            if documents:
                # Add to vector store
                self.vector_store_manager.add_documents(
                    documents=documents,
                    source_type="knowledge_base"
                )
                
                logger.info(f"Successfully ingested {len(documents)} documents")
                return {
                    "success": True,
                    "documents_processed": len(documents),
                    "message": f"Ingested {len(documents)} documents successfully"
                }
            else:
                logger.warning("No documents found to ingest")
                return {
                    "success": False,
                    "documents_processed": 0,
                    "message": "No documents found in knowledge base directory"
                }
                
        except Exception as e:
            error_msg = f"Error ingesting knowledge base: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "documents_processed": 0
            }
    
    def add_document(self, file_path: str, source_type: str = "user_upload") -> bool:
        """Add a single document to the knowledge base."""
        try:
            logger.info(f"Adding document: {file_path}")
            
            # Validate file first
            validation = self.document_processor.validate_file(file_path)
            if not validation["valid"]:
                logger.error(f"File validation failed: {validation['error']}")
                return False
            
            # Process document
            document = self.document_processor.process_file(file_path, source_type)
            
            # Add to vector store
            self.vector_store_manager.add_documents([document], source_type)
            
            logger.info(f"Successfully added document: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document {file_path}: {str(e)}")
            return False
    
    def add_text_content(self, content: str, title: str = "text_content", 
                        source_type: str = "manual") -> bool:
        """Add text content directly to the knowledge base."""
        try:
            logger.info(f"Adding text content: {title}")
            
            # Process text content
            document = self.document_processor.process_text_content(
                content=content,
                filename=title,
                source_type=source_type
            )
            
            # Add to vector store
            self.vector_store_manager.add_documents([document], source_type)
            
            logger.info(f"Successfully added text content: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding text content: {str(e)}")
            return False
    
    def query(self, query: str, max_results: int = 5, 
             min_score: float = 0.0, source_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query the knowledge base and return relevant documents."""
        try:
            logger.info(f"Querying knowledge base: '{query}' (max_results: {max_results})")
            
            # Store query in history
            self.query_history.append({
                "query": query,
                "timestamp": datetime.utcnow().isoformat(),
                "max_results": max_results
            })
            
            # Keep only last 100 queries
            if len(self.query_history) > 100:
                self.query_history = self.query_history[-100:]
            
            # Prepare filter
            filter_dict = None
            if source_filter:
                filter_dict = {"source_type": source_filter}
            
            # Perform similarity search with scores
            results = self.vector_store_manager.similarity_search_with_score(
                query=query,
                k=max_results
            )
            
            # Format results
            formatted_results = []
            for document, score in results:
                if score >= min_score:  # Filter by minimum score
                    formatted_results.append({
                        "content": document.page_content,
                        "metadata": document.metadata,
                        "relevance_score": float(score),
                        "source": document.metadata.get("source", "unknown"),
                        "filename": document.metadata.get("filename", "unknown"),
                        "file_type": document.metadata.get("file_type", "unknown")
                    })
            
            # Sort by relevance score (higher is better)
            formatted_results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            logger.info(f"Retrieved {len(formatted_results)} relevant documents for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error querying knowledge base: {str(e)}")
            return []
    
    def get_context(self, query: str, max_context_length: int = 4000) -> str:
        """Get concatenated context from relevant documents."""
        try:
            results = self.query(query, max_results=5)
            
            if not results:
                return "No relevant context found in knowledge base."
            
            context_parts = []
            current_length = 0
            
            for result in results:
                content = result["content"]
                source = result["metadata"].get("filename", "unknown")
                
                # Add source header
                header = f"\n--- Source: {source} ---\n"
                part = header + content
                
                if current_length + len(part) > max_context_length:
                    # Truncate if needed
                    remaining_length = max_context_length - current_length
                    if remaining_length > len(header) + 100:  # Minimum useful content
                        truncated_content = content[:remaining_length - len(header) - 20] + "..."
                        part = header + truncated_content
                        context_parts.append(part)
                    break
                
                context_parts.append(part)
                current_length += len(part)
            
            context = "\n".join(context_parts)
            
            logger.info(f"Generated context of {len(context)} characters")
            return context
            
        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            return f"Error retrieving context: {str(e)}"
    
    def search_by_metadata(self, metadata_filters: Dict[str, str], 
                          max_results: int = 10) -> List[Dict[str, Any]]:
        """Search documents by metadata filters."""
        try:
            # This is a simplified implementation
            # In a full implementation, you'd use the vector store's metadata filtering
            all_docs = self.vector_store_manager.similarity_search("", k=100)  # Get many docs
            
            filtered_docs = []
            for doc in all_docs:
                match = True
                for key, value in metadata_filters.items():
                    if key not in doc.metadata or str(doc.metadata[key]).lower() != str(value).lower():
                        match = False
                        break
                
                if match:
                    filtered_docs.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "source": doc.metadata.get("source", "unknown")
                    })
                
                if len(filtered_docs) >= max_results:
                    break
            
            logger.info(f"Found {len(filtered_docs)} documents matching metadata filters")
            return filtered_docs
            
        except Exception as e:
            logger.error(f"Error searching by metadata: {str(e)}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system."""
        try:
            vector_stats = self.vector_store_manager.get_collection_stats()
            processor_stats = self.document_processor.get_supported_formats()
            
            return {
                "vector_store": vector_stats,
                "document_processor": {
                    "supported_formats": processor_stats,
                    "available_formats": [fmt for fmt, available in processor_stats.items() if available]
                },
                "retriever": {
                    "query_history_length": len(self.query_history),
                    "last_query": self.query_history[-1] if self.query_history else None
                },
                "settings": {
                    "chunk_size": settings.chunk_size,
                    "chunk_overlap": settings.chunk_overlap,
                    "embedding_model": settings.embedding_model
                },
                "system_info": {
                    "langchain_available": LANGCHAIN_AVAILABLE,
                    "knowledge_base_path": settings.knowledge_base_path,
                    "vector_store_path": settings.vector_store_path
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting RAG stats: {str(e)}")
            return {"error": str(e)}
    
    def clear_knowledge_base(self, source_type: Optional[str] = None):
        """Clear all or specific documents from the knowledge base."""
        try:
            if source_type:
                self.vector_store_manager.delete_documents(source_type)
                logger.info(f"Cleared documents of type: {source_type}")
            else:
                # This would need implementation in vector store manager
                logger.warning("Full knowledge base clearing not implemented")
                
        except Exception as e:
            logger.error(f"Error clearing knowledge base: {str(e)}")
    
    def get_query_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent query history."""
        try:
            return self.query_history[-limit:] if self.query_history else []
        except Exception as e:
            logger.error(f"Error getting query history: {str(e)}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the RAG system."""
        try:
            health_status = {
                "status": "healthy",
                "components": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check vector store
            try:
                stats = self.vector_store_manager.get_collection_stats()
                health_status["components"]["vector_store"] = {
                    "status": "healthy",
                    "document_count": stats.get("document_count", 0)
                }
            except Exception as e:
                health_status["components"]["vector_store"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            # Check document processor
            try:
                formats = self.document_processor.get_supported_formats()
                available_count = sum(1 for available in formats.values() if available)
                health_status["components"]["document_processor"] = {
                    "status": "healthy",
                    "supported_formats": available_count
                }
            except Exception as e:
                health_status["components"]["document_processor"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }