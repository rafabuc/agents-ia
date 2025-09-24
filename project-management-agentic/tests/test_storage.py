# tests/test_storage.py
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from storage.file_manager import FileManager


class TestFileManager:
    """Test cases for FileManager."""
    
    def test_initialization(self):
        """Test file manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('config.settings.settings') as mock_settings:
                mock_settings.project_storage_path = temp_dir
                
                manager = FileManager()
                assert os.path.exists(temp_dir)
    
    def test_create_project_directory(self):
        """Test project directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('config.settings.settings') as mock_settings:
                mock_settings.project_storage_path = temp_dir
                
                manager = FileManager()
                project_path = manager.create_project_directory(1)
                
                assert os.path.exists(project_path)
                assert os.path.exists(os.path.join(project_path, "documents"))
                assert os.path.exists(os.path.join(project_path, "templates"))
    
    def test_save_and_read_document(self):
        """Test document save and read operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('config.settings.settings') as mock_settings:
                mock_settings.project_storage_path = temp_dir
                
                manager = FileManager()
                manager.create_project_directory(1)
                
                # Save document
                content = "Test document content"
                file_path = manager.save_project_document(
                    project_id=1,
                    document_type="test",
                    content=content,
                    filename="test.md"
                )
                
                assert os.path.exists(file_path)
                
                # Read document
                read_content = manager.read_project_document(1, "test.md")
                assert read_content == content
