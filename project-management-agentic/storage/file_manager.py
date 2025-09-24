import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

from config.settings import settings
from utils.logger import logger


class FileManager:
    """Manages file operations for projects and documents."""
    
    def __init__(self):
        self.projects_base_path = settings.project_storage_path
        self.ensure_base_directories()
    
    def ensure_base_directories(self):
        """Ensure base directories exist."""
        os.makedirs(self.projects_base_path, exist_ok=True)
    
    def create_project_directory(self, project_id: int) -> str:
        """Create directory structure for a project."""
        project_path = os.path.join(self.projects_base_path, f"project_{project_id}")
        
        # Create main project directory
        os.makedirs(project_path, exist_ok=True)
        
        # Create subdirectories
        subdirs = [
            "documents",
            "templates", 
            "exports",
            "attachments"
        ]
        
        for subdir in subdirs:
            os.makedirs(os.path.join(project_path, subdir), exist_ok=True)
        
        logger.info(f"Created project directory: {project_path}")
        return project_path
    
    def save_project_document(self, project_id: int, document_type: str, 
                            content: str, filename: Optional[str] = None) -> str:
        """Save a document for a project."""
        project_path = os.path.join(self.projects_base_path, f"project_{project_id}")
        
        # Ensure project directory exists
        if not os.path.exists(project_path):
            self.create_project_directory(project_id)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{document_type}_{timestamp}.md"
        
        # Ensure filename has appropriate extension
        if not any(filename.endswith(ext) for ext in ['.md', '.txt', '.html', '.json']):
            filename += '.md'
        
        # Save to documents subdirectory
        documents_path = os.path.join(project_path, "documents")
        file_path = os.path.join(documents_path, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved document: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving document {file_path}: {str(e)}")
            raise
