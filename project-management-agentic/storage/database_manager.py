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
            session.commit()  # Commit the transaction to persist the project
            session.refresh(project)  # Refresh to ensure all attributes are loaded

            # Extract essential data before session closes
            project_id = project.id
            project_name = project.name

            logger.info(f"Created project: {project_name} (ID: {project_id})")

            # Return a new project object with the essential data
            # This avoids the detached instance problem
            result_project = Project(
                name=project_name,
                description=description,
                methodology=methodology,
                project_data=project_data or {}
            )
            result_project.id = project_id
            return result_project
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID."""
        with get_db_session() as session:
            project = session.query(Project).filter(Project.id == project_id).first()

            if not project:
                return None

            # Extract data while session is active
            project_data = {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'methodology': project.methodology,
                'status': project.status,
                'created_at': project.created_at,
                'updated_at': project.updated_at,
                'project_data': project.project_data
            }

            # Create new Project object with extracted data
            result_project = Project(
                name=project_data['name'],
                description=project_data['description'],
                methodology=project_data['methodology'],
                project_data=project_data['project_data']
            )
            result_project.id = project_data['id']
            result_project.status = project_data['status']
            result_project.created_at = project_data['created_at']
            result_project.updated_at = project_data['updated_at']
            result_project.name = project_data['name']

            return result_project
    
    def list_projects(self, limit: int = 50) -> List[Project]:
        """List all projects."""
        with get_db_session() as session:
            projects = session.query(Project).order_by(Project.updated_at.desc()).limit(limit).all()

            # Create detached copies to avoid session binding issues
            result_projects = []
            for project in projects:
                # Extract data while session is active
                project_data = {
                    'id': project.id,
                    'name': project.name,
                    'description': project.description,
                    'methodology': project.methodology,
                    'status': project.status,
                    'created_at': project.created_at,
                    'updated_at': project.updated_at,
                    'project_data': project.project_data
                }

                # Create new Project object with extracted data
                result_project = Project(
                    name=project_data['name'],
                    description=project_data['description'],
                    methodology=project_data['methodology'],
                    project_data=project_data['project_data']
                )
                result_project.id = project_data['id']
                result_project.status = project_data['status']
                result_project.created_at = project_data['created_at']
                result_project.updated_at = project_data['updated_at']

                result_projects.append(result_project)

            return result_projects
    
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

    def get_project_documents(self, project_id: int) -> List[ProjectDocument]:
        """Get all documents for a project."""
        with get_db_session() as session:
            documents = session.query(ProjectDocument).filter(
                ProjectDocument.project_id == project_id
            ).all()

            # Extract data while session is active to avoid detached instance issues
            result_documents = []
            for doc in documents:
                doc_data = {
                    'id': doc.id,
                    'project_id': doc.project_id,
                    'document_type': doc.document_type,
                    'file_path': doc.file_path,
                    'content': doc.content,
                    'created_at': doc.created_at,
                    'updated_at': doc.updated_at
                }

                # Create new ProjectDocument object with extracted data
                result_doc = ProjectDocument(
                    project_id=doc_data['project_id'],
                    document_type=doc_data['document_type'],
                    file_path=doc_data['file_path'],
                    content=doc_data['content']
                )
                result_doc.id = doc_data['id']
                result_doc.created_at = doc_data['created_at']
                result_doc.updated_at = doc_data['updated_at']

                result_documents.append(result_doc)

            logger.info(f"Retrieved {len(result_documents)} documents for project {project_id}")
            return result_documents
