from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from config.database import get_db_session
from models.project import Project, ProjectDocument, ProjectStatus
from models.chat import ChatSession, ChatMessage, MessageRole
from models.document import Document, DocumentChunk
from utils.logger import logger


class DatabaseManager:
    """Manages database operations for the PMP system."""
    
    def __init__(self):
        pass
    
    # Project Operations
    def create_project(self, name: str, description: str = None, 
                      methodology: str = "PMP", project_data: Dict = None) -> Project:
        """Create a new project."""
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
        """Get a project by ID."""
        with get_db_session() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            return project
    
    def list_projects(self, limit: int = 50) -> List[Project]:
        """List all projects."""
        with get_db_session() as session:
            projects = session.query(Project).order_by(Project.updated_at.desc()).limit(limit).all()
            return projects
    
    # Chat Operations
    def create_chat_session(self, project_id: Optional[int] = None, 
                           session_name: str = None, agent_type: str = None) -> ChatSession:
        """Create a new chat session."""
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
        """Store a chat message."""
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
        """Get system statistics."""
        try:
            with get_db_session() as session:
                # Contar con manejo de errores
                try:
                    project_count = session.query(Project).count()
                except:
                    project_count = 0
                
                try:
                    document_count = session.query(ProjectDocument).count()
                except:
                    document_count = 0
                
                try:
                    chat_session_count = session.query(ChatSession).count()
                except:
                    chat_session_count = 0
                
                try:
                    message_count = session.query(ChatMessage).count()
                except:
                    message_count = 0
                
                return {
                    "projects": {"total": project_count, "recent": 0},
                    "documents": {"total": document_count},
                    "chat": {"sessions": chat_session_count, "messages": message_count},
                    "generated_at": datetime.utcnow().isoformat(),
                    "status": "healthy"
                }
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            return {
                "projects": {"total": 0, "recent": 0},
                "documents": {"total": 0},
                "chat": {"sessions": 0, "messages": 0},
                "status": "error",
                "error": str(e)
            }
        
        
    
    def create_project_document(self, project_id: int, document_type: str, 
                               file_path: str, content: str = None) -> ProjectDocument:
        """Create a project document record."""
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
