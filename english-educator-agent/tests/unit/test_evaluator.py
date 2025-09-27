"""
Unit tests for Evaluator Agent
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.agents.evaluator import EvaluatorAgent


@pytest.mark.asyncio
async def test_evaluator_agent_initialization():
    """Test that evaluator agent initializes correctly."""
    agent = EvaluatorAgent()
    
    assert agent.llm is not None
    assert agent.graph is not None


@pytest.mark.asyncio
async def test_ask_question():
    """Test question generation."""
    agent = EvaluatorAgent()
    
    state = {
        "messages": [],
        "conversation_history": [],
        "question_count": 0
    }
    
    # Mock LLM response
    mock_response = Mock()
    mock_response.content = '{"question": "What is your name?", "skill_tested": "vocabulary", "expected_level": "A1"}'
    
    with patch.object(agent.llm, 'ainvoke', return_value=mock_response):
        result = await agent.ask_question(state)
        
        assert "messages" in result
        assert len(result["messages"]) == 1
        assert result["question_count"] == 1


@pytest.mark.asyncio
async def test_should_continue():
    """Test continuation logic."""
    agent = EvaluatorAgent()
    
    # Test with less than 7 questions
    state = {"question_count": 3, "conversation_history": []}
    assert agent.should_continue(state) == "continue"
    
    # Test with 7 questions
    state = {"question_count": 7, "conversation_history": []}
    assert agent.should_continue(state) == "finish"


@pytest.mark.asyncio
async def test_analyze_response():
    """Test response analysis."""
    agent = EvaluatorAgent()
    
    state = {
        "messages": [{"role": "user", "content": "I am student"}],
        "question_count": 1,
        "conversation_history": [],
        "strengths": [],
        "weaknesses": []
    }
    
    mock_response = Mock()
    mock_response.content = '''{
        "level_indicators": ["basic vocabulary"],
        "vocabulary_quality": {"range": "basic", "accuracy": 0.8},
        "grammar_quality": {"complexity": "simple", "accuracy": 0.7},
        "estimated_level": "A2",
        "confidence": 0.7,
        "strengths": ["clear communication"],
        "weaknesses": ["article usage"]
    }'''
    
    with patch.object(agent.llm, 'ainvoke', return_value=mock_response):
        result = await agent.analyze_response(state)
        
        assert "conversation_history" in result
        assert len(result["conversation_history"]) == 1
        assert len(result["strengths"]) > 0


@pytest.mark.asyncio
async def test_determine_level():
    """Test final level determination."""
    agent = EvaluatorAgent()
    
    state = {
        "conversation_history": [
            {
                "question_num": 1,
                "student_response": "I like English",
                "analysis": {"estimated_level": "A2"}
            }
        ]
    }
    
    mock_response = Mock()
    mock_response.content = '''{
        "cefr_level": "A2",
        "confidence": 0.8,
        "detailed_breakdown": {
            "vocabulary": "A2",
            "grammar": "A2",
            "fluency": "A1",
            "comprehension": "A2"
        },
        "strengths": ["vocabulary", "willingness to learn"],
        "weaknesses": ["grammar accuracy"],
        "recommendations": ["practice present simple", "learn articles"]
    }'''
    
    with patch.object(agent.llm, 'ainvoke', return_value=mock_response):
        result = await agent.determine_level(state)
        
        assert result["student_level"] == "A2"
        assert "strengths" in result
        assert "weaknesses" in result


@pytest.mark.asyncio
async def test_run_complete_evaluation():
    """Test complete evaluation run."""
    agent = EvaluatorAgent()
    
    # Mock the graph's ainvoke method
    expected_result = {
        "student_level": "B1",
        "strengths": ["vocabulary", "comprehension"],
        "weaknesses": ["grammar"],
        "final_assessment": {"cefr_level": "B1", "confidence": 0.85}
    }
    
    with patch.object(agent.graph, 'ainvoke', return_value=expected_result):
        result = await agent.run(user_id=1, initial_message="Hello")
        
        assert result["student_level"] == "B1"
        assert len(result["strengths"]) > 0
        assert "final_assessment" in result


def test_evaluator_state_structure():
    """Test that state structure is correct."""
    from backend.agents.evaluator import EvaluatorState
    
    # This will raise TypeError if structure is wrong
    state: EvaluatorState = {
        "messages": [],
        "student_level": None,
        "strengths": [],
        "weaknesses": [],
        "conversation_history": [],
        "question_count": 0
    }
    
    assert state["question_count"] == 0
    assert state["student_level"] is None
