import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # Database
    database_url: str = Field("sqlite:///./pmp_system.db", env="DATABASE_URL")
    
    # Paths
    vector_store_path: str = Field("./data/vector_store", env="VECTOR_STORE_PATH")
    project_storage_path: str = Field("./data/projects", env="PROJECT_STORAGE_PATH")
    knowledge_base_path: str = Field("./data/knowledge_base", env="KNOWLEDGE_BASE_PATH")
    templates_path: str = Field("./templates", env="TEMPLATES_PATH")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("./logs/pmp_system.log", env="LOG_FILE")
    
    # Model Configuration
    default_llm_provider: str = Field("anthropic", env="DEFAULT_LLM_PROVIDER")#openai
    default_model: str = Field("claude-3-haiku-20240307", env="DEFAULT_MODEL")#gpt-4
    embedding_model: str = Field("text-embedding-ada-002", env="EMBEDDING_MODEL")
    
    # System Settings
    max_concurrent_agents: int = Field(5, env="MAX_CONCURRENT_AGENTS")
    chunk_size: int = Field(1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(200, env="CHUNK_OVERLAP")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.vector_store_path,
            self.project_storage_path,
            self.knowledge_base_path,
            self.templates_path,
            os.path.dirname(self.log_file) if self.log_file else "./logs"
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)


# Global settings instance
settings = Settings()
