# tests/test_rag.py
import pytest
import tempfile
from unittest.mock import Mock, patch

from rag.document_processor import DocumentProcessor
from rag.vector_store import VectorStoreManager


class TestDocumentProcessor:
    """Test cases for DocumentProcessor."""
    
    @patch('storage.database_manager.DatabaseManager')
    def test_initialization(self, mock_db):
        """Test document processor initialization."""
        processor = DocumentProcessor()
        
        assert processor.supported_extensions == {'.pdf', '.docx', '.txt', '.md'}
        mock_db.assert_called_once()
    
    def test_extract_text_file(self):
        """Test text file extraction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_path = f.name
        
        try:
            with patch('storage.database_manager.DatabaseManager'):
                processor = DocumentProcessor()
                content = processor._extract_text_file(temp_path)
                assert content == "Test content"
        finally:
            os.unlink(temp_path)
