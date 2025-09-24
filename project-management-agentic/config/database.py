from sqlalchemy import create_engine
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
    """Context manager for database sessions."""
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
    """Dependency for FastAPI or other frameworks."""
    with get_db_session() as session:
        yield session


def init_database():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def drop_database():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)


def reset_database():
    """Reset database (drop and recreate)."""
    drop_database()
    init_database()
