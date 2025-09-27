"""
Quick test script to verify system functionality.
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from agents.evaluator import EvaluatorAgent
from agents.tutor import TutorAgent
from agents.conversation import ConversationPartnerAgent
from agents.exercise import ExerciseGeneratorAgent, ExerciseType
from config import settings


async def test_evaluator():
    """Test evaluator agent."""
    print("\n" + "="*60)
    print("TESTING EVALUATOR AGENT")
    print("="*60)
    
    evaluator = EvaluatorAgent()
    
    print("\n🤖 Starting evaluation...")
    result = await evaluator.run(
        user_id=1,
        initial_message="I want to improve my English skills"
    )
    
    print(f"\n✅ Evaluation complete!")
    print(f"   Level: {result.get('student_level', 'Unknown')}")
    print(f"   Strengths: {', '.join(result.get('strengths', []))}")
    print(f"   Weaknesses: {', '.join(result.get('weaknesses', []))}")


async def test_tutor():
    """Test tutor agent."""
    print("\n" + "="*60)
    print("TESTING TUTOR AGENT")
    print("="*60)
    
    tutor = TutorAgent()
    
    print("\n🤖 Creating lesson...")
    lesson = tutor.create_lesson(
        topic="Present Perfect Tense",
        level="B1"
    )
    
    print(f"\n✅ Lesson created!")
    print(f"   Topic: {lesson.get('topic', 'N/A')}")
    if isinstance(lesson, dict) and 'objectives' in lesson:
        print(f"   Objectives: {len(lesson.get('objectives', []))} items")


async def test_conversation():
    """Test conversation agent."""
    print("\n" + "="*60)
    print("TESTING CONVERSATION AGENT")
    print("="*60)
    
    conv_agent = ConversationPartnerAgent()
    
    print("\n🤖 Starting conversation...")
    response = await conv_agent.chat(
        user_message="Hi! I love reading books. What about you?",
        context={
            "level": "B1",
            "topic": "hobbies",
            "user_id": 1
        }
    )
    
    print(f"\n✅ Conversation response:")
    print(f"   AI: {response.get('reply', 'No reply')[:100]}...")
    print(f"   Corrections: {len(response.get('corrections', []))}")
    print(f"   New vocabulary: {len(response.get('new_vocabulary', []))}")


async def test_exercises():
    """Test exercise generator."""
    print("\n" + "="*60)
    print("TESTING EXERCISE GENERATOR")
    print("="*60)
    
    exercise_agent = ExerciseGeneratorAgent()
    
    print("\n🤖 Generating exercises...")
    exercises = await exercise_agent.generate_exercise_set(
        topic="Present Simple",
        level="A2",
        exercise_types=[
            ExerciseType.MULTIPLE_CHOICE,
            ExerciseType.FILL_IN_BLANK
        ],
        quantity=5
    )
    
    print(f"\n✅ Generated {len(exercises)} exercises")
    if exercises:
        print(f"   First exercise: {exercises[0].get('type', 'unknown')}")


async def test_config():
    """Test configuration."""
    print("\n" + "="*60)
    print("TESTING CONFIGURATION")
    print("="*60)
    
    print(f"\n✅ Configuration loaded:")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   OpenAI Key: {'*' * 20}{settings.OPENAI_API_KEY[-4:]}")
    print(f"   Anthropic Key: {'*' * 20}{settings.ANTHROPIC_API_KEY[-4:]}")
    print(f"   Database: {settings.DATABASE_URL[:30]}...")
    print(f"   Redis: {settings.REDIS_URL}")


async def main():
    """Run all tests."""
    print("\n" + "🚀" + "="*58)
    print("  ENGLISH EDUCATOR AGENT - SYSTEM TEST")
    print("="*60)
    
    try:
        # Test configuration first
        test_config()
        
        # Test agents
        await test_tutor()
        await test_conversation()
        await test_exercises()
        await test_evaluator()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")
        
        print("🎉 System is ready to use!")
        print("\nNext steps:")
        print("  1. Start the API server: uvicorn main:app --reload")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Start Celery workers: celery -A tasks worker")
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ TEST FAILED: {e}")
        print("="*60 + "\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
