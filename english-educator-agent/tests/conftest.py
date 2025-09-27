"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_user():
    """Mock user data."""
    return {
        "id": 1,
        "email": "test@example.com",
        "username": "testuser",
        "current_level": "B1",
        "native_language": "Spanish",
        "learning_goals": ["improve speaking", "prepare for exam"],
        "interests": ["travel", "technology"]
    }


@pytest.fixture
def mock_session_data():
    """Mock session data."""
    return {
        "user_id": 1,
        "session_type": "conversation",
        "topic": "daily_activities",
        "duration_minutes": 15,
        "accuracy": 0.85,
        "engagement_score": 0.9
    }


@pytest.fixture
def mock_exercise():
    """Mock exercise data."""
    return {
        "type": "multiple_choice",
        "question": "What ___ you do yesterday?",
        "options": {
            "A": "do",
            "B": "did",
            "C": "does",
            "D": "doing"
        },
        "correct": "B",
        "explanation": "Use 'did' for past simple questions"
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    class MockResponse:
        def __init__(self, content):
            self.content = content
    
    return MockResponse


@pytest.fixture
def sample_text_for_grammar_check():
    """Sample text for grammar checking."""
    return "I have went to the store yesterday and buy some apples."


@pytest.fixture
def mock_progress_data():
    """Mock progress data."""
    return {
        "user_id": 1,
        "level_assessed": "B1",
        "vocabulary_score": 0.75,
        "grammar_score": 0.70,
        "fluency_score": 0.65,
        "comprehension_score": 0.80,
        "total_study_time": 500,
        "exercises_completed": 100,
        "words_learned": 200
    }


# Async fixtures
@pytest.fixture
async def async_mock_llm():
    """Async mock LLM."""
    from unittest.mock import AsyncMock
    
    mock = AsyncMock()
    mock.ainvoke = AsyncMock()
    return mock
