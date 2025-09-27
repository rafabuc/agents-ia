#!/usr/bin/env python
"""
Database initialization and seeding script.
Run this to set up the database with initial data.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from datetime import datetime
from sqlalchemy.orm import Session

from models import Base, User, Lesson, VocabularyItem
from utils.database import engine, SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create all database tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Tables created successfully")


def seed_users(db: Session):
    """Seed initial test users."""
    logger.info("Seeding test users...")
    
    test_users = [
        User(
            email="student1@example.com",
            username="student1",
            full_name="Test Student 1",
            current_level="A2",
            target_level="B1",
            native_language="Spanish",
            learning_goals=["Improve speaking", "Pass B1 exam"],
            interests=["technology", "travel", "movies"]
        ),
        User(
            email="student2@example.com",
            username="student2",
            full_name="Test Student 2",
            current_level="B1",
            target_level="B2",
            native_language="Portuguese",
            learning_goals=["Business English", "TOEFL preparation"],
            interests=["business", "finance", "sports"]
        ),
        User(
            email="teacher@example.com",
            username="teacher",
            full_name="Test Teacher",
            current_level="C2",
            target_level="C2",
            native_language="English"
        )
    ]
    
    for user in test_users:
        existing = db.query(User).filter(User.email == user.email).first()
        if not existing:
            db.add(user)
    
    db.commit()
    logger.info(f"✓ Seeded {len(test_users)} test users")


def seed_lessons(db: Session):
    """Seed sample lessons."""
    logger.info("Seeding sample lessons...")
    
    sample_lessons = [
        Lesson(
            title="Present Perfect Introduction",
            topic="Present Perfect",
            level="B1",
            description="Introduction to Present Perfect tense",
            content={
                "objectives": ["Understand Present Perfect", "Use it correctly"],
                "vocabulary": ["already", "yet", "just", "ever", "never"],
                "examples": [
                    "I have visited Paris.",
                    "She hasn't finished yet."
                ]
            },
            created_by="system",
            is_active=True
        ),
        Lesson(
            title="Conditionals Type 1",
            topic="First Conditional",
            level="B1",
            description="Learn about first conditional sentences",
            content={
                "objectives": ["Form first conditional", "Use in real situations"],
                "vocabulary": ["if", "will", "unless"],
                "examples": [
                    "If it rains, I'll stay home.",
                    "She'll be happy if you come."
                ]
            },
            created_by="system",
            is_active=True
        ),
        Lesson(
            title="Common Phrasal Verbs",
            topic="Phrasal Verbs",
            level="B2",
            description="Essential phrasal verbs for everyday English",
            content={
                "objectives": ["Learn 20 common phrasal verbs", "Use them naturally"],
                "vocabulary": ["get up", "look after", "give up", "turn down"],
                "examples": [
                    "I get up at 7 AM.",
                    "She looks after her siblings."
                ]
            },
            created_by="system",
            is_active=True
        )
    ]
    
    for lesson in sample_lessons:
        existing = db.query(Lesson).filter(
            Lesson.title == lesson.title
        ).first()
        if not existing:
            db.add(lesson)
    
    db.commit()
    logger.info(f"✓ Seeded {len(sample_lessons)} sample lessons")


def seed_vocabulary(db: Session):
    """Seed common vocabulary items."""
    logger.info("Seeding vocabulary items...")
    
    vocab_items = [
        VocabularyItem(
            word="amazing",
            definition="Very impressive or surprising",
            level="A2",
            part_of_speech="adjective",
            example_sentences=[
                "The view was amazing!",
                "She has amazing talent."
            ],
            tags=["emotions", "description"]
        ),
        VocabularyItem(
            word="although",
            definition="Despite the fact that; however",
            level="B1",
            part_of_speech="conjunction",
            example_sentences=[
                "Although it was raining, we went out.",
                "He passed the exam, although he didn't study much."
            ],
            tags=["connectors", "grammar"]
        ),
        VocabularyItem(
            word="entrepreneur",
            definition="A person who starts their own business",
            level="B2",
            part_of_speech="noun",
            example_sentences=[
                "She became a successful entrepreneur.",
                "Many entrepreneurs fail before they succeed."
            ],
            tags=["business", "careers"]
        )
    ]
    
    for vocab in vocab_items:
        existing = db.query(VocabularyItem).filter(
            VocabularyItem.word == vocab.word
        ).first()
        if not existing:
            db.add(vocab)
    
    db.commit()
    logger.info(f"✓ Seeded {len(vocab_items)} vocabulary items")


def verify_setup(db: Session):
    """Verify database setup."""
    logger.info("\nVerifying database setup...")
    
    user_count = db.query(User).count()
    lesson_count = db.query(Lesson).count()
    vocab_count = db.query(VocabularyItem).count()
    
    logger.info(f"✓ Users: {user_count}")
    logger.info(f"✓ Lessons: {lesson_count}")
    logger.info(f"✓ Vocabulary items: {vocab_count}")
    
    if user_count > 0 and lesson_count > 0:
        logger.info("\n✅ Database setup complete!")
        return True
    else:
        logger.error("\n❌ Database setup incomplete")
        return False


def main():
    """Main initialization function."""
    print("="*60)
    print("DATABASE INITIALIZATION")
    print("="*60)
    
    try:
        # Create tables
        create_tables()
        
        # Create session
        db = SessionLocal()
        
        try:
            # Seed data
            seed_users(db)
            seed_lessons(db)
            seed_vocabulary(db)
            
            # Verify
            success = verify_setup(db)
            
            if success:
                print("\n" + "="*60)
                print("Database is ready to use!")
                print("="*60)
                print("\nTest users created:")
                print("  - student1@example.com")
                print("  - student2@example.com")
                print("  - teacher@example.com")
                print("\nYou can now start the API server.")
                return 0
            else:
                return 1
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
