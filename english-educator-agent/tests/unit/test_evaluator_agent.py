"""
Tests for Evaluator Agent.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.agents.evaluator import EvaluatorAgent


@pytest.mark.asyncio
async def test_evaluator_initialization():
    """Test evaluator agent initialization."""
    evaluator = EvaluatorAgent()
    assert evaluator is not None
    assert evaluator.llm is not None
    assert evaluator.graph is not None


@pytest.mark.asyncio
async def test_ask_question():
    """Test question generation."""
    evaluator = EvaluatorAgent()
    
    state = {
        "messages": [],
        "student_level": None,
        "strengths": [],
        "weaknesses": [],
        "conversation_history": [],
        "question_count": 0
    }
    
    with patch.object(evaluator.llm, 'ainvoke', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = '{"question": "What is your name?", "skill_tested": "basic"}'
        
        result = await evaluator.ask_question(state)
        
        assert "messages" in result
        assert result["question_count"] == 1


@pytest.mark.asyncio
async def test_should_continue_logic():
    """Test continuation logic."""
    evaluator = EvaluatorAgent()
    
    # Should continue with few questions
    state = {
        "question_count": 3,
        "conversation_history": []
    }
    assert evaluator.should_continue(state) == "continue"
    
    # Should finish with many questions
    state = {
        "question_count": 8,
        "conversation_history": []
    }
    assert evaluator.should_continue(state) == "finish"


@pytest.mark.asyncio
async def test_determine_level():
    """Test level determination."""
    evaluator = EvaluatorAgent()
    
    state = {
        "conversation_history": [
            {
                "question_num": 1,
                "student_response": "I am learning English",
                "analysis": {
                    "estimated_level": "B1",
                    "confidence": 0.8
                }
            }
        ]
    }
    
    with patch.object(evaluator.llm, 'ainvoke', new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value.content = '''{
            "cefr_level": "B1",
            "confidence": 0.85,
            "strengths": ["Good vocabulary"],
            "weaknesses": ["Grammar needs work"]
        }'''
        
        result = await evaluator.determine_level(state)
        
        assert result["student_level"] == "B1"
        assert "strengths" in result
        assert "weaknesses" in result


@pytest.mark.asyncio
async def test_full_evaluation_flow():
    """Test complete evaluation flow."""
    evaluator = EvaluatorAgent()
    
    with patch.object(evaluator, 'graph') as mock_graph:
        mock_graph.ainvoke = AsyncMock(return_value={
            "student_level": "B1",
            "strengths": ["Vocabulary"],
            "weaknesses": ["Grammar"],
            "final_assessment": {"score": 75}
        })
        
        result = await evaluator.run(user_id=1, initial_message="Hello")
        
        assert result["student_level"] == "B1"
        assert len(result["strengths"]) > 0
