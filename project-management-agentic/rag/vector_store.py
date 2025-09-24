import os
import pickle
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from langchain_community.embeddings import OpenAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from config.settings import settings
from utils.logger import logger


class VectorStoreManager:
    """Manages vector store operations for RAG system."""
    
    def __init__(self):
        self.vector_store = None
        self.embeddings = None
        self.text_splitter = None
        
        if not CHROMA_AVAILABLE or not LANGCHAIN_AVAILABLE:
            logger.warning("ChromaDB or LangChain not available, using fallback storage")
            self._init_fallback()
        else:
            try:
                self._init_chroma()
            except Exception as e:
                logger.warning(f"Failed to initialize ChromaDB: {str(e)}, using fallback")
                self._init_fallback()
        
        logger.info("VectorStoreManager initialized")
    
    def _init_chroma(self):
        """Initialize ChromaDB vector store."""
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not available, using fallback storage")
            self._init_fallback()
            return
            
        try:
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key,
                model=settings.embedding_model
            )
            
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.chunk_size,
                chunk_overlap=settings.chunk_overlap,
                length_function=len,
            )
            
            # Initialize ChromaDB
            chroma_client = chromadb.PersistentClient(
                path=settings.vector_store_path
            )
            
            self.vector_store = Chroma(
                client=chroma_client,
                collection_name="pmp_knowledge_base",
                embedding_function=self.embeddings
            )
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.warning(f"ChromaDB initialization failed: {str(e)}, using fallback")
            self._init_fallback()
    
    def _init_fallback(self):
        """Initialize fallback storage (simple file-based)."""
        self.documents_store = {}
        self.embeddings_store = {}
        self.storage_path = os.path.join(settings.vector_store_path, "fallback_store.pkl")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # Load existing data
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents_store = data.get('documents', {})
                    self.embeddings_store = data.get('embeddings', {})
                logger.info("Loaded existing fallback store")
            except Exception as e:
                logger.warning(f"Could not load fallback store: {str(e)}")
        
        logger.info("Fallback storage initialized")
    
    def add_documents(self, documents: List, source_type: str = "knowledge_base") -> List[str]:
        """Add documents to the vector store."""
        try:
            if self.vector_store and self.text_splitter:
                # Use ChromaDB
                chunks = []
                for doc in documents:
                    if hasattr(doc, 'page_content'):
                        doc_chunks = self.text_splitter.split_documents([doc])
                        for chunk in doc_chunks:
                            chunk.metadata.update({
                                "source_type": source_type,
                                "added_at": datetime.utcnow().isoformat()
                            })
                        chunks.extend(doc_chunks)
                    else:
                        # Handle raw text
                        chunks.append(doc)
                
                ids = self.vector_store.add_documents(chunks)
                logger.info(f"Added {len(chunks)} document chunks to ChromaDB")
                return ids
            else:
                # Use fallback storage
                ids = []
                for i, doc in enumerate(documents):
                    doc_id = f"{source_type}_{datetime.now().timestamp()}_{i}"
                    content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
                    metadata = getattr(doc, 'metadata', {})
                    
                    self.documents_store[doc_id] = {
                        "content": content,
                        "metadata": metadata,
                        "source_type": source_type,
                        "added_at": datetime.utcnow().isoformat()
                    }
                    ids.append(doc_id)
                
                self._save_fallback_store()
                logger.info(f"Added {len(documents)} documents to fallback store")
                return ids
                
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            # Try fallback even if ChromaDB was supposed to work
            try:
                return self._fallback_add_documents(documents, source_type)
            except:
                raise e
    
    def _fallback_add_documents(self, documents: List, source_type: str) -> List[str]:
        """Fallback method to add documents."""
        if not hasattr(self, 'documents_store'):
            self._init_fallback()
            
        ids = []
        for i, doc in enumerate(documents):
            doc_id = f"{source_type}_{datetime.now().timestamp()}_{i}"
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            metadata = getattr(doc, 'metadata', {})
            
            self.documents_store[doc_id] = {
                "content": content,
                "metadata": metadata,
                "source_type": source_type,
                "added_at": datetime.utcnow().isoformat()
            }
            ids.append(doc_id)
        
        self._save_fallback_store()
        return ids
    
    def similarity_search(self, query: str, k: int = 5, filter_dict: Optional[Dict] = None) -> List:
        """Perform similarity search."""
        try:
            if self.vector_store:
                # Use ChromaDB
                results = self.vector_store.similarity_search(
                    query=query,
                    k=k,
                    filter=filter_dict
                )
                logger.info(f"Retrieved {len(results)} similar documents from ChromaDB")
                return results
            else:
                # Use fallback - simple keyword matching
                results = []
                query_lower = query.lower()
                query_words = query_lower.split()
                
                # Score documents based on keyword matches
                scored_docs = []
                for doc_id, doc_data in self.documents_store.items():
                    content = doc_data['content'].lower()
                    score = 0
                    
                    # Simple scoring: count word matches
                    for word in query_words:
                        if word in content:
                            score += content.count(word)
                    
                    if score > 0:
                        scored_docs.append((score, doc_data))
                
                # Sort by score and take top k
                scored_docs.sort(key=lambda x: x[0], reverse=True)
                
                for score, doc_data in scored_docs[:k]:
                    # Create mock Document object
                    mock_doc = type('Document', (), {
                        'page_content': doc_data['content'],
                        'metadata': doc_data['metadata']
                    })()
                    results.append(mock_doc)
                
                logger.info(f"Retrieved {len(results)} similar documents from fallback store")
                return results
                
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            return []
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """Perform similarity search with relevance scores."""
        try:
            if self.vector_store:
                # Use ChromaDB
                results = self.vector_store.similarity_search_with_score(
                    query=query,
                    k=k
                )
                logger.info(f"Retrieved {len(results)} documents with scores from ChromaDB")
                return results
            else:
                # Use fallback with real scores
                query_lower = query.lower()
                query_words = query_lower.split()
                
                scored_docs = []
                for doc_id, doc_data in self.documents_store.items():
                    content = doc_data['content'].lower()
                    score = 0
                    
                    for word in query_words:
                        if word in content:
                            score += content.count(word)
                    
                    if score > 0:
                        # Normalize score (simple approach)
                        normalized_score = min(score / len(query_words), 1.0)
                        scored_docs.append((normalized_score, doc_data))
                
                scored_docs.sort(key=lambda x: x[0], reverse=True)
                
                results = []
                for score, doc_data in scored_docs[:k]:
                    mock_doc = type('Document', (), {
                        'page_content': doc_data['content'],
                        'metadata': doc_data['metadata']
                    })()
                    results.append((mock_doc, score))
                
                logger.info(f"Retrieved {len(results)} documents with scores from fallback")
                return results
                
        except Exception as e:
            logger.error(f"Error in similarity search with scores: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection."""
        try:
            if self.vector_store:
                # ChromaDB stats
                try:
                    collection = self.vector_store._collection
                    count = collection.count()
                except:
                    count = 0
                
                return {
                    "document_count": count,
                    "collection_name": "pmp_knowledge_base",
                    "embedding_model": settings.embedding_model,
                    "storage_type": "chromadb"
                }
            else:
                # Fallback stats
                return {
                    "document_count": len(getattr(self, 'documents_store', {})),
                    "collection_name": "fallback_store",
                    "embedding_model": "none",
                    "storage_type": "fallback"
                }
                
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {
                "document_count": 0,
                "storage_type": "error",
                "error": str(e)
            }
    
    def _save_fallback_store(self):
        """Save fallback store to disk."""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents_store,
                    'embeddings': self.embeddings_store
                }, f)
        except Exception as e:
            logger.error(f"Error saving fallback store: {str(e)}")
