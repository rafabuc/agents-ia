#!/usr/bin/env python3
"""
Script de instalación completa del PMP Multi-Agent System
Genera todos los archivos y carpetas automáticamente
"""
import os
import sys
from pathlib import Path
import subprocess


def create_file(file_path, content):
    """Crear archivo con contenido."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Creado: {file_path}")


def create_directory_structure():
    """Crear estructura de directorios."""
    directories = [
        "config",
        "agents", 
        "workflows",
        "rag",
        "templates",
        "models",
        "storage", 
        "utils",
        "data/knowledge_base",
        "data/projects", 
        "data/vector_store",
        "logs",
        "tests",
        "scripts"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Directorio: {directory}")


def generate_requirements_txt():
    """Generar requirements.txt."""
    content = """# Core dependencies
langchain==0.1.0
langchain-community==0.0.10
langchain-openai==0.0.5
langchain-anthropic==0.1.1
langgraph==0.0.20

# Vector stores and embeddings
chromadb==0.4.18
sentence-transformers==2.2.2
faiss-cpu==1.7.4

# Database
sqlalchemy==2.0.23
alembic==1.13.1

# Document processing
pypdf2==3.0.1
python-docx==1.1.0
openpyxl==3.1.2
jinja2==3.1.2

# Web framework (optional for API)
fastapi==0.104.1
uvicorn==0.24.0

# Utilities
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
click==8.1.7
rich==13.7.0
loguru==0.7.2

# Development
pytest==7.4.3
black==23.11.0
flake8==6.1.0
"""
    create_file("requirements.txt", content)


def generate_env_example():
    """Generar .env.example."""
    content = """# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database
DATABASE_URL=sqlite:///./pmp_system.db

# Vector Store
VECTOR_STORE_PATH=./data/vector_store

# File Storage
PROJECT_STORAGE_PATH=./data/projects
KNOWLEDGE_BASE_PATH=./data/knowledge_base
TEMPLATES_PATH=./templates

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/pmp_system.log

# Model Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-ada-002
"""
    create_file(".env.example", content)


def generate_config_files():
    """Generar archivos de configuración."""
    
    # config/__init__.py
    init_content = """from .settings import settings
from .database import Base, engine, SessionLocal, get_db_session, init_database

__all__ = [
    "settings", 
    "Base", 
    "engine", 
    "SessionLocal", 
    "get_db_session", 
    "init_database"
]
"""
    create_file("config/__init__.py", init_content)
    
    # config/settings.py
    settings_content = """import os
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
    default_llm_provider: str = Field("openai", env="DEFAULT_LLM_PROVIDER")
    default_model: str = Field("gpt-4", env="DEFAULT_MODEL")
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
        \"\"\"Create necessary directories if they don't exist.\"\"\"
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
"""
    create_file("config/settings.py", settings_content)
    
    # config/database.py
    database_content = """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from .settings import settings

# Database engine
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    \"\"\"Context manager for database sessions.\"\"\"
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    \"\"\"Dependency for FastAPI or other frameworks.\"\"\"
    with get_db_session() as session:
        yield session


def init_database():
    \"\"\"Initialize database tables.\"\"\"
    Base.metadata.create_all(bind=engine)


def drop_database():
    \"\"\"Drop all database tables.\"\"\"
    Base.metadata.drop_all(bind=engine)


def reset_database():
    \"\"\"Reset database (drop and recreate).\"\"\"
    drop_database()
    init_database()
"""
    create_file("config/database.py", database_content)


def generate_models():
    """Generar modelos de base de datos."""
    
    # models/__init__.py
    init_content = """from .project import Project, ProjectDocument
from .chat import ChatSession, ChatMessage
from .document import Document, DocumentChunk

__all__ = [
    "Project", "ProjectDocument", 
    "ChatSession", "ChatMessage",
    "Document", "DocumentChunk"
]
"""
    create_file("models/__init__.py", init_content)
    
    # models/project.py
    project_content = """from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from config.database import Base


class ProjectStatus(enum.Enum):
    INITIATED = "initiated"
    PLANNING = "planning"
    EXECUTING = "executing"
    MONITORING = "monitoring"
    CLOSING = "closing"
    CLOSED = "closed"


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.INITIATED)
    methodology = Column(String)  # PMP, SAFe, etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Project data as JSON
    project_data = Column(JSON)
    
    # Relationships
    documents = relationship("ProjectDocument", back_populates="project")
    chat_sessions = relationship("ChatSession", back_populates="project")


class ProjectDocument(Base):
    __tablename__ = "project_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    document_type = Column(String)  # charter, wbs, cost_estimate, etc.
    file_path = Column(String)
    content = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="documents")
"""
    create_file("models/project.py", project_content)
    
    # models/chat.py
    chat_content = """from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from config.database import Base


class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    session_name = Column(String)
    agent_type = Column(String)  # pmp_project, cost_budget, template
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(Enum(MessageRole))
    content = Column(Text)
    agent_name = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
"""
    create_file("models/chat.py", chat_content)
    
    # models/document.py
    document_content = """from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from config.database import Base


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    document_type = Column(String)  # pdf, docx, txt, etc.
    source = Column(String)  # knowledge_base, project, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_index = Column(Integer)
    content = Column(Text)
    embedding_id = Column(String)  # ID in vector store
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
"""
    create_file("models/document.py", document_content)


def generate_utils():
    """Generar archivos de utilidades."""
    
    # utils/__init__.py
    init_content = """from .logger import logger, setup_logging
from .helpers import *

__all__ = ["logger", "setup_logging"]
"""
    create_file("utils/__init__.py", init_content)
    
    # utils/logger.py
    logger_content = """import logging
import sys
from pathlib import Path
from datetime import datetime
from loguru import logger as loguru_logger

from config.settings import settings


def setup_logging():
    \"\"\"Setup logging configuration.\"\"\"
    # Remove default handler
    loguru_logger.remove()
    
    # Add console handler
    loguru_logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # Add file handler
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    loguru_logger.add(
        str(log_file),
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="zip"
    )
    
    return loguru_logger


# Initialize logger
logger = setup_logging()
"""
    create_file("utils/logger.py", logger_content)
    
    # utils/helpers.py
    helpers_content = """import re
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import json


def sanitize_filename(filename: str) -> str:
    \"\"\"Sanitize filename for safe file system operations.\"\"\"
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\\\|?*]', '_', filename)
    # Remove extra spaces and dots
    sanitized = re.sub(r'\\s+', '_', sanitized.strip())
    sanitized = re.sub(r'\\.+', '.', sanitized)
    # Ensure not empty
    if not sanitized or sanitized == '.':
        sanitized = 'unnamed_file'
    return sanitized


def format_currency(amount: float, currency: str = "USD") -> str:
    \"\"\"Format currency amount.\"\"\"
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    \"\"\"Safely load JSON string with default fallback.\"\"\"
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default
"""
    create_file("utils/helpers.py", helpers_content)


def generate_storage():
    """Generar archivos de storage."""
    
    # storage/__init__.py
    init_content = """from .file_manager import FileManager
from .database_manager import DatabaseManager

__all__ = ["FileManager", "DatabaseManager"]
"""
    create_file("storage/__init__.py", init_content)
    
    # storage/file_manager.py
    file_manager_content = """import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime

from config.settings import settings
from utils.logger import logger


class FileManager:
    \"\"\"Manages file operations for projects and documents.\"\"\"
    
    def __init__(self):
        self.projects_base_path = settings.project_storage_path
        self.ensure_base_directories()
    
    def ensure_base_directories(self):
        \"\"\"Ensure base directories exist.\"\"\"
        os.makedirs(self.projects_base_path, exist_ok=True)
    
    def create_project_directory(self, project_id: int) -> str:
        \"\"\"Create directory structure for a project.\"\"\"
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
        \"\"\"Save a document for a project.\"\"\"
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
"""
    create_file("storage/file_manager.py", file_manager_content)
    
    # storage/database_manager.py
    db_manager_content = """from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from config.database import get_db_session
from models.project import Project, ProjectDocument, ProjectStatus
from models.chat import ChatSession, ChatMessage, MessageRole
from models.document import Document, DocumentChunk
from utils.logger import logger


class DatabaseManager:
    \"\"\"Manages database operations for the PMP system.\"\"\"
    
    def __init__(self):
        pass
    
    # Project Operations
    def create_project(self, name: str, description: str = None, 
                      methodology: str = "PMP", project_data: Dict = None) -> Project:
        \"\"\"Create a new project.\"\"\"
        with get_db_session() as session:
            project = Project(
                name=name,
                description=description,
                methodology=methodology,
                project_data=project_data or {}
            )
            
            session.add(project)
            session.flush()  # Get the ID without committing
            
            logger.info(f"Created project: {project.name} (ID: {project.id})")
            return project
    
    def get_project(self, project_id: int) -> Optional[Project]:
        \"\"\"Get a project by ID.\"\"\"
        with get_db_session() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            return project
    
    def list_projects(self, limit: int = 50) -> List[Project]:
        \"\"\"List all projects.\"\"\"
        with get_db_session() as session:
            projects = session.query(Project).order_by(Project.updated_at.desc()).limit(limit).all()
            return projects
    
    # Chat Operations
    def create_chat_session(self, project_id: Optional[int] = None, 
                           session_name: str = None, agent_type: str = None) -> ChatSession:
        \"\"\"Create a new chat session.\"\"\"
        with get_db_session() as session:
            chat_session = ChatSession(
                project_id=project_id,
                session_name=session_name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                agent_type=agent_type
            )
            
            session.add(chat_session)
            session.flush()
            
            logger.info(f"Created chat session: {chat_session.id}")
            return chat_session
    
    def store_chat_message(self, session_id: int, role: str, 
                          content: str, agent_name: str = None) -> ChatMessage:
        \"\"\"Store a chat message.\"\"\"
        with get_db_session() as session:
            message = ChatMessage(
                session_id=session_id,
                role=MessageRole(role),
                content=content,
                agent_name=agent_name
            )
            
            session.add(message)
            session.flush()
            
            return message
    
    def get_system_stats(self) -> Dict[str, Any]:
        \"\"\"Get system statistics.\"\"\"
        with get_db_session() as session:
            project_count = session.query(Project).count()
            chat_session_count = session.query(ChatSession).count()
            message_count = session.query(ChatMessage).count()
            
            return {
                "projects": {
                    "total": project_count
                },
                "chat": {
                    "sessions": chat_session_count,
                    "messages": message_count
                },
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def create_project_document(self, project_id: int, document_type: str, 
                               file_path: str, content: str = None) -> ProjectDocument:
        \"\"\"Create a project document record.\"\"\"
        with get_db_session() as session:
            document = ProjectDocument(
                project_id=project_id,
                document_type=document_type,
                file_path=file_path,
                content=content
            )
            
            session.add(document)
            session.flush()
            
            logger.info(f"Created project document: {document.id}")
            return document
"""
    create_file("storage/database_manager.py", db_manager_content)


def generate_agents():
    """Generar archivos de agentes."""
    
    # agents/__init__.py
    init_content = """from .base_agent import BaseAgent
from .agent_factory import AgentFactory

__all__ = [
    "BaseAgent",
    "AgentFactory"
]
"""
    create_file("agents/__init__.py", init_content)
    
    # agents/base_agent.py
    base_agent_content = """from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from config.settings import settings
from storage.database_manager import DatabaseManager
from utils.logger import logger


class BaseAgent(ABC):
    \"\"\"Base class for all PMP agents.\"\"\"
    
    def __init__(
        self,
        name: str,
        description: str,
        llm_provider: str = None,
        model: str = None,
    ):
        self.name = name
        self.description = description
        self.llm_provider = llm_provider or settings.default_llm_provider
        self.model = model or settings.default_model
        
        # Initialize LLM
        self.llm = self._get_llm()
        
        # Database manager
        self.db_manager = DatabaseManager()
        
        logger.info(f"Initialized agent: {self.name}")
    
    def _get_llm(self):
        \"\"\"Get the appropriate LLM based on provider.\"\"\"
        if self.llm_provider.lower() == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return ChatOpenAI(
                api_key=settings.openai_api_key,
                model=self.model,
                temperature=0.1
            )
        elif self.llm_provider.lower() == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            return ChatAnthropic(
                api_key=settings.anthropic_api_key,
                model=self.model,
                temperature=0.1
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def initialize(self):
        \"\"\"Initialize the agent.\"\"\"
        logger.info(f"Agent {self.name} initialized successfully")
    
    def process(self, input_text: str, session_id: Optional[int] = None) -> Dict[str, Any]:
        \"\"\"Process input and return response.\"\"\"
        # Simple implementation - override in subclasses
        return {
            "agent": self.name,
            "response": f"Processed: {input_text}",
            "timestamp": datetime.utcnow().isoformat()
        }
"""
    create_file("agents/base_agent.py", base_agent_content)
    
    # agents/agent_factory.py
    factory_content = """from typing import Dict, Any, Optional, Type
from .base_agent import BaseAgent
from utils.logger import logger


class DemoAgent(BaseAgent):
    \"\"\"Demo agent for testing.\"\"\"
    
    def __init__(self):
        super().__init__(
            name="demo_agent",
            description="Demo agent for testing the system"
        )


class AgentFactory:
    \"\"\"Factory for creating and managing agents.\"\"\"
    
    def __init__(self):
        self._agent_classes: Dict[str, Type[BaseAgent]] = {
            "demo": DemoAgent,
        }
        self._agent_instances: Dict[str, BaseAgent] = {}
        logger.info("AgentFactory initialized")
    
    def create_agent(self, agent_type: str, **kwargs) -> BaseAgent:
        \"\"\"Create or get existing agent instance.\"\"\"
        if agent_type not in self._agent_classes:
            available_types = ", ".join(self._agent_classes.keys())
            raise ValueError(f"Unknown agent type: {agent_type}. Available: {available_types}")
        
        # Return existing instance if available (singleton pattern)
        if agent_type in self._agent_instances:
            return self._agent_instances[agent_type]
        
        # Create new instance
        agent_class = self._agent_classes[agent_type]
        agent = agent_class(**kwargs)
        agent.initialize()
        
        # Store instance
        self._agent_instances[agent_type] = agent
        
        logger.info(f"Created agent: {agent_type}")
        return agent
    
    def list_available_agents(self) -> Dict[str, str]:
        \"\"\"List all available agent types with descriptions.\"\"\"
        agents = {}
        for agent_type, agent_class in self._agent_classes.items():
            try:
                temp_agent = agent_class()
                description = temp_agent.description
                agents[agent_type] = description
            except Exception:
                agents[agent_type] = "Agent description not available"
        
        return agents
"""
    create_file("agents/agent_factory.py", factory_content)


def generate_main():
    """Generar archivo principal."""
    main_content = """\"\"\"
PMP Multi-Agent System
Main application entry point
\"\"\"

import os
import sys
import asyncio
from typing import Dict, Any, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import init_database
from config.settings import settings
from agents.agent_factory import AgentFactory
from storage.database_manager import DatabaseManager
from utils.logger import logger

console = Console()


class PMPSystem:
    \"\"\"Main PMP Multi-Agent System class.\"\"\"
    
    def __init__(self):
        self.agent_factory = AgentFactory()
        self.db_manager = DatabaseManager()
        
        console.print("[green]PMP Multi-Agent System initialized successfully![/green]")
    
    def list_projects(self, limit: int = 10) -> None:
        \"\"\"List recent projects.\"\"\"
        try:
            projects = self.db_manager.list_projects(limit=limit)
            
            if not projects:
                console.print("[yellow]No projects found.[/yellow]")
                return
            
            table = Table(title="Recent Projects")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("Methodology")
            table.add_column("Created", style="blue")
            
            for project in projects:
                table.add_row(
                    str(project.id),
                    project.name,
                    project.status.value,
                    project.methodology,
                    project.created_at.strftime("%Y-%m-%d")
                )
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error listing projects: {str(e)}[/red]")
    
    def system_status(self) -> None:
        \"\"\"Display system status.\"\"\"
        try:
            stats = self.db_manager.get_system_stats()
            agents = self.agent_factory.list_available_agents()
            
            # Create status panels
            db_panel = Panel(
                f"Projects: {stats['projects']['total']}\\n"
                f"Chat Sessions: {stats['chat']['sessions']}\\n"
                f"Messages: {stats['chat']['messages']}",
                title="Database Status",
                border_style="green"
            )
            
            agent_list = "\\n".join([f"- {name}: {desc}" for name, desc in agents.items()])
            agent_panel = Panel(
                agent_list,
                title="Available Agents", 
                border_style="blue"
            )
            
            console.print(db_panel)
            console.print(agent_panel)
            
        except Exception as e:
            console.print(f"[red]Error getting system status: {str(e)}[/red]")


# CLI Commands
@click.group()
def cli():
    \"\"\"PMP Multi-Agent System CLI\"\"\"
    pass


@cli.command()
def init():
    \"\"\"Initialize the system (create database tables).\"\"\"
    try:
        init_database()
        console.print("[green]✓[/green] Database initialized successfully!")
    except Exception as e:
        console.print(f"[red]✗[/red] Error initializing database: {str(e)}")


@cli.command()
@click.argument('name')
@click.option('--description', default='', help='Project description')
@click.option('--methodology', default='PMP', help='Project methodology')
def create_project(name, description, methodology):
    \"\"\"Create a new project.\"\"\"
    try:
        system = PMPSystem()
        project = system.db_manager.create_project(
            name=name,
            description=description,
            methodology=methodology
        )
        
        console.print(f"[green]✓[/green] Project '{name}' created successfully!")
        console.print(f"Project ID: {project.id}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error creating project: {str(e)}")


@cli.command()
@click.option('--limit', default=10, help='Number of projects to show')
def list_projects(limit):
    \"\"\"List recent projects.\"\"\"
    system = PMPSystem()
    system.list_projects(limit)


@cli.command()
def status():
    \"\"\"Show system status.\"\"\"
    system = PMPSystem()
    system.system_status()


@cli.command()
def demo():
    \"\"\"Run system demo.\"\"\"
    try:
        system = PMPSystem()
        
        console.print("[blue]Running PMP System Demo...[/blue]")
        
        # Create a demo project
        project = system.db_manager.create_project(
            name="Demo Project",
            description="A demonstration project",
            methodology="PMP"
        )
        
        console.print(f"[green]✓[/green] Created demo project: {project.name}")
        
        # Show system status
        system.system_status()
        
        console.print("[green]Demo completed successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Demo failed: {str(e)}")


if __name__ == "__main__":
    cli()
"""
    create_file("main.py", main_content)


def generate_readme():
    """Generar README.md."""
    readme_content = """# PMP Multi-Agent System

Sistema completo de gestión de proyectos que utiliza agentes de IA especializados en metodologías PMP y SAFe.

## 🚀 Instalación Rápida

1. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tu API key de OpenAI o Anthropic
```

3. **Inicializar sistema**:
```bash
python main.py init
```

4. **Probar el sistema**:
```bash
python main.py demo
```

## 🔧 Comandos Disponibles

```bash
# Ver estado del sistema
python main.py status

# Crear proyecto
python main.py create-project "Mi Proyecto" --description "Descripción" --methodology PMP

# Listar proyectos
python main.py list-projects

# Ejecutar demo
python main.py demo
```

## 📁 Estructura

```
pmp_multiagent_system/
├── main.py              # Punto de entrada
├── config/              # Configuración
├── agents/              # Agentes de IA
├── models/              # Modelos de BD
├── storage/             # Gestión de archivos/BD
├── utils/               # Utilidades
├── data/                # Datos y proyectos
└── templates/           # Plantillas
```

## 🛠️ Configuración

Edita `.env` con tu clave API:

```bash
OPENAI_API_KEY=tu_clave_aqui
# O
ANTHROPIC_API_KEY=tu_clave_aqui
```

## 🤝 Soporte

Para problemas o preguntas, revisa los logs en `./logs/` o ejecuta `python main.py status`.
"""
    create_file("README.md", readme_content)


def generate_templates():
    """Generar plantillas básicas."""
    
    # templates/project_charter.jinja2
    charter_content = """# PROJECT CHARTER

## PROJECT INFORMATION
- **Project Name:** {{ project_name }}
- **Project Manager:** {{ project_manager | default('TBD') }}
- **Start Date:** {{ start_date | default('TBD') }}
- **Budget:** {{ budget | default('TBD') }}

## PROJECT DESCRIPTION
{{ description | default('Project description to be defined') }}

## PROJECT OBJECTIVES
{% if objectives %}
{% for objective in objectives %}
- {{ objective }}
{% endfor %}
{% else %}
- Objectives to be defined
{% endif %}

## PROJECT SCOPE
### In Scope:
{% if scope_inclusions %}
{% for item in scope_inclusions %}
- {{ item }}
{% endfor %}
{% else %}
- Scope to be defined
{% endif %}

## STAKEHOLDERS
{% if stakeholders %}
{% for stakeholder in stakeholders %}
- **{{ stakeholder.name }}:** {{ stakeholder.role }}
{% endfor %}
{% else %}
- Stakeholders to be identified
{% endif %}

---
*Document Version:* {{ version | default('1.0') }}
*Created On:* {{ created_date | default('TBD') }}
"""
    create_file("templates/project_charter.jinja2", charter_content)


def run_installation():
    """Ejecutar instalación de dependencias."""
    print("\n=== Instalando dependencias ===")
    
    # Crear entorno virtual
    if not os.path.exists("venv"):
        print("Creando entorno virtual...")
        result = subprocess.run([sys.executable, "-m", "venv", "venv"])
        if result.returncode == 0:
            print("✓ Entorno virtual creado")
        else:
            print("⚠️  No se pudo crear entorno virtual, continuando...")
    
    # Determinar comando pip
    if sys.platform == "win32":
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Instalar dependencias
    print("Instalando dependencias...")
    result = subprocess.run([pip_cmd, "install", "-r", "requirements.txt"])
    if result.returncode == 0:
        print("✓ Dependencias instaladas")
        
        # Copiar .env
        if not os.path.exists(".env"):
            if os.path.exists(".env.example"):
                import shutil
                shutil.copy(".env.example", ".env")
                print("✓ Archivo .env creado")
        
        # Inicializar base de datos
        print("Inicializando base de datos...")
        result = subprocess.run([python_cmd, "main.py", "init"])
        if result.returncode == 0:
            print("✓ Base de datos inicializada")
            
            # Ejecutar demo
            print("Ejecutando demo...")
            subprocess.run([python_cmd, "main.py", "demo"])
        
    else:
        print("⚠️  Error instalando dependencias. Instala manualmente con:")
        print("pip install -r requirements.txt")


def main():
    """Función principal."""
    print("=" * 60)
    print("   GENERADOR COMPLETO PMP MULTI-AGENT SYSTEM")
    print("=" * 60)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    
    print("\n🏗️  Generando estructura del proyecto...")
    
    # Crear estructura
    create_directory_structure()
    
    print("\n📝 Generando archivos de configuración...")
    generate_requirements_txt()
    generate_env_example()
    generate_config_files()
    
    print("\n🗄️  Generando modelos de base de datos...")
    generate_models()
    
    print("\n🛠️  Generando utilidades...")
    generate_utils()
    
    print("\n💾 Generando gestores de almacenamiento...")
    generate_storage()
    
    print("\n🤖 Generando agentes...")
    generate_agents()
    
    print("\n📋 Generando plantillas...")
    generate_templates()
    
    print("\n🚀 Generando archivo principal...")
    generate_main()
    
    print("\n📖 Generando documentación...")
    generate_readme()
    
    print("\n" + "=" * 60)
    print("✅ SISTEMA PMP MULTI-AGENT GENERADO EXITOSAMENTE!")
    print("=" * 60)
    
    print("\n📁 Archivos creados en:")
    print(f"   {os.path.abspath('.')}")
    
    print("\n🔧 Próximos pasos:")
    print("1. Editar .env con tu API key")
    print("2. python -m venv venv")
    print("3. venv\\Scripts\\activate (Windows) o source venv/bin/activate (Linux/Mac)")
    print("4. pip install -r requirements.txt")
    print("5. python main.py init")
    print("6. python main.py demo")
    
    # Preguntar si instalar automáticamente
    response = input("\n¿Quieres instalar las dependencias automáticamente? (y/N): ")
    if response.lower() == 'y':
        run_installation()
    
    print("\n🎉 ¡Sistema listo para usar!")


if __name__ == "__main__":
    main()