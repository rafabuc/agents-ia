import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig(BaseModel):
    """Configuración de base de datos"""
    type: str = "sqlite"
    url: str = "sqlite:///project_agent.db"
    vector_store_path: str = "./data/vector_store"

class ClaudeConfig(BaseModel):
    """Configuración de Claude API"""
    api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    model: str = "claude-3-haiku-20240307"
    #claude-3-5-sonnet-20241022"claude-3-sonnet-20240229"
    max_tokens: int = 2000#4000
    temperature: float = 0.1

class RAGConfig(BaseModel):
    """Configuración del sistema RAG"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "all-MiniLM-L6-v2"
    similarity_threshold: float = 0.7
    max_results: int = 5

class Settings(BaseModel):
    """Configuración principal del sistema"""
    app_name: str = "Project Management Agent"
    version: str = "1.0.0"
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true")
    
    database: DatabaseConfig = DatabaseConfig()
    claude: ClaudeConfig = ClaudeConfig()
    rag: RAGConfig = RAGConfig()
    
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path("./data"))
    logs_dir: Path = Field(default_factory=lambda: Path("./logs"))
    
    def __init__(self, **data):
        super().__init__(**data)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Crear directorios necesarios si no existen"""
        directories = [
            self.data_dir,
            self.logs_dir,
            Path(self.database.vector_store_path).parent,
            Path("./projects"),
            Path("./knowledge_base")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

settings = Settings()
