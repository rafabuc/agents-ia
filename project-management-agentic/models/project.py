from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
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
