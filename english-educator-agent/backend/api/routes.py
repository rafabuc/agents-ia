"""
API Routes for English Tutor AI.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional, List
import logging

from agents.evaluator import EvaluatorAgent
from agents.tutor import TutorAgent
from utils.metrics import track_api_request

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class EvaluationRequest(BaseModel):
    user_id: int
    initial_message: Optional[str] = None


class LessonRequest(BaseModel):
    topic: str
    level: str
    user_id: Optional[int] = None


class QuestionRequest(BaseModel):
    question: str
    level: str
    topic: Optional[str] = "general"


class ExerciseRequest(BaseModel):
    topic: str
    level: str
    exercise_types: List[str] = ["multiple_choice", "fill_in_blank"]
    quantity: int = 10


# Dependency for agents (can be improved with DI container)
def get_evaluator_agent():
    return EvaluatorAgent()


def get_tutor_agent():
    return TutorAgent()


@router.post("/evaluate")
@track_api_request("POST", "/evaluate")
async def start_evaluation(
    request: EvaluationRequest,
    evaluator: EvaluatorAgent = Depends(get_evaluator_agent)
):
    """Start level evaluation for a user."""
    try:
        result = await evaluator.run(
            user_id=request.user_id,
            initial_message=request.initial_message
        )
        return {
            "user_id": request.user_id,
            "level": result.get("student_level"),
            "assessment": result.get("final_assessment"),
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", [])
        }
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lesson/create")
@track_api_request("POST", "/lesson/create")
async def create_lesson(
    request: LessonRequest,
    tutor: TutorAgent = Depends(get_tutor_agent)
):
    """Create a personalized lesson."""
    try:
        lesson = tutor.create_lesson(
            topic=request.topic,
            level=request.level
        )
        return {
            "topic": request.topic,
            "level": request.level,
            "lesson": lesson
        }
    except Exception as e:
        logger.error(f"Lesson creation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lesson/explain")
@track_api_request("POST", "/lesson/explain")
async def explain_grammar(
    concept: str,
    level: str,
    tutor: TutorAgent = Depends(get_tutor_agent)
):
    """Explain a grammar concept."""
    try:
        explanation = tutor.explain_grammar(concept=concept, level=level)
        return {
            "concept": concept,
            "level": level,
            "explanation": explanation
        }
    except Exception as e:
        logger.error(f"Grammar explanation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lesson/examples")
@track_api_request("POST", "/lesson/examples")
async def get_examples(
    word_or_phrase: str,
    context: str = "general",
    tutor: TutorAgent = Depends(get_tutor_agent)
):
    """Get usage examples for a word or phrase."""
    try:
        examples = tutor.provide_examples(
            word_or_phrase=word_or_phrase,
            context=context
        )
        return {
            "word_or_phrase": word_or_phrase,
            "context": context,
            "examples": examples
        }
    except Exception as e:
        logger.error(f"Example generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/question/answer")
@track_api_request("POST", "/question/answer")
async def answer_question(
    request: QuestionRequest,
    tutor: TutorAgent = Depends(get_tutor_agent)
):
    """Answer a student's question."""
    try:
        answer = await tutor.answer_question(
            question=request.question,
            context={
                "level": request.level,
                "topic": request.topic
            }
        )
        return {
            "question": request.question,
            "answer": answer,
            "level": request.level
        }
    except Exception as e:
        logger.error(f"Question answering failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/{user_id}")
@track_api_request("GET", "/progress")
async def get_progress(
    user_id: int,
    period_days: int = 30
):
    """Get progress report for a user."""
    try:
        # TODO: Implement progress tracking
        return {
            "user_id": user_id,
            "period_days": period_days,
            "message": "Progress tracking coming soon"
        }
    except Exception as e:
        logger.error(f"Progress retrieval failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api"}
