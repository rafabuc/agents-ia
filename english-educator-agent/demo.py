"""
Example script to demonstrate the English Tutor AI system
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from agents.evaluator import EvaluatorAgent
from agents.tutor import TutorAgent
from agents.grammar import GrammarCheckerAgent
from agents.conversation import ConversationPartnerAgent
from agents.exercise import ExerciseGeneratorAgent, ExerciseType


async def demo_evaluator():
    """Demo: Evaluate student level"""
    print("\n" + "="*60)
    print("DEMO 1: Student Level Evaluation")
    print("="*60 + "\n")
    
    evaluator = EvaluatorAgent()
    
    # Simulate evaluation
    print("Starting evaluation for student...")
    print("This would normally be interactive through WebSocket.\n")
    
    # Mock evaluation result
    result = {
        "student_level": "B1",
        "strengths": ["Good vocabulary", "Clear pronunciation"],
        "weaknesses": ["Present perfect usage", "Article usage"],
        "final_assessment": {
            "cefr_level": "B1",
            "confidence": 0.82,
            "detailed_breakdown": {
                "vocabulary": "B1",
                "grammar": "A2",
                "fluency": "B1",
                "comprehension": "B1"
            }
        }
    }
    
    print(f"✓ Evaluation Complete!")
    print(f"  Level: {result['student_level']}")
    print(f"  Strengths: {', '.join(result['strengths'])}")
    print(f"  Areas to improve: {', '.join(result['weaknesses'])}")


async def demo_tutor():
    """Demo: Create a lesson"""
    print("\n" + "="*60)
    print("DEMO 2: Lesson Creation")
    print("="*60 + "\n")
    
    tutor = TutorAgent()
    
    print("Creating lesson on 'Present Perfect' for B1 level...")
    
    lesson = tutor.create_lesson(
        topic="Present Perfect Tense",
        level="B1"
    )
    
    print("\n✓ Lesson Created!")
    print(f"  Topic: Present Perfect Tense")
    print(f"  Level: B1")
    print(f"  Content preview: {str(lesson)[:200]}...")


async def demo_grammar_checker():
    """Demo: Check grammar"""
    print("\n" + "="*60)
    print("DEMO 3: Grammar Checking")
    print("="*60 + "\n")
    
    checker = GrammarCheckerAgent()
    
    test_text = "I have went to the store yesterday and I buyed some bread."
    
    print(f"Checking text: '{test_text}'")
    print("\nAnalyzing...\n")
    
    result = await checker.check_grammar(test_text, "B1")
    
    print("✓ Analysis Complete!")
    print(f"  Errors found: {len(result.get('corrections', []))}")
    print(f"  Overall score: {result.get('overall_quality', {}).get('score', 0)}/100")
    
    if result.get('corrections'):
        print("\n  Corrections:")
        for i, correction in enumerate(result['corrections'][:2], 1):
            print(f"    {i}. '{correction.get('original')}' → '{correction.get('corrected')}'")
            print(f"       ({correction.get('error_type')})")


async def demo_conversation():
    """Demo: Conversation practice"""
    print("\n" + "="*60)
    print("DEMO 4: Conversation Practice")
    print("="*60 + "\n")
    
    partner = ConversationPartnerAgent()
    
    user_message = "Hello! I want to practice my English. Can you help me?"
    
    print(f"Student: {user_message}")
    
    response = await partner.chat(
        user_message=user_message,
        context={
            "level": "B1",
            "topic": "daily_conversation",
            "user_id": 1
        }
    )
    
    print(f"\nTutor: {response.get('reply')}")
    
    if response.get('new_vocabulary'):
        print(f"\n💡 New vocabulary introduced: {', '.join(response['new_vocabulary'])}")


async def demo_exercise_generator():
    """Demo: Generate exercises"""
    print("\n" + "="*60)
    print("DEMO 5: Exercise Generation")
    print("="*60 + "\n")
    
    generator = ExerciseGeneratorAgent()
    
    print("Generating exercises on 'Present Simple' for A2 level...")
    
    exercises = await generator.generate_exercise_set(
        topic="Present Simple",
        level="A2",
        exercise_types=[
            ExerciseType.MULTIPLE_CHOICE.value,
            ExerciseType.FILL_BLANK.value
        ],
        quantity=5
    )
    
    print(f"\n✓ Generated {len(exercises)} exercises!")
    
    if exercises:
        print("\nExample exercise:")
        ex = exercises[0]
        print(f"  Type: {ex.get('type')}")
        print(f"  Question: {ex.get('question', ex.get('sentence', 'N/A'))}")


async def demo_complete_flow():
    """Demo: Complete learning flow"""
    print("\n" + "="*60)
    print("DEMO 6: Complete Learning Flow")
    print("="*60 + "\n")
    
    print("Simulating a complete student session:\n")
    
    # Step 1: Evaluation
    print("1️⃣  Initial Evaluation")
    print("   Student completes level assessment...")
    print("   ✓ Level determined: B1\n")
    
    # Step 2: Lesson
    print("2️⃣  Personalized Lesson")
    print("   Creating lesson based on level and goals...")
    print("   ✓ Lesson ready: 'Present Perfect for Travel'\n")
    
    # Step 3: Practice
    print("3️⃣  Conversation Practice")
    print("   Student: 'I have visited Paris last year.'")
    print("   Tutor: 'Great! Just a small correction: we say...")
    print("   ✓ Conversation completed\n")
    
    # Step 4: Exercises
    print("4️⃣  Practice Exercises")
    print("   Generating targeted exercises...")
    print("   ✓ 10 exercises ready\n")
    
    # Step 5: Feedback
    print("5️⃣  Progress Tracking")
    print("   Session analyzed...")
    print("   ✓ Progress report generated")
    print("   📊 Accuracy: 85% | Time: 25 min | New words: 8\n")
    
    print("Session complete! 🎉")


async def main():
    """Main demo runner"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "ENGLISH TUTOR AI SYSTEM" + " "*20 + "║")
    print("║" + " "*20 + "Demo Script" + " "*27 + "║")
    print("╚" + "="*58 + "╝")
    
    demos = [
        ("Evaluator", demo_evaluator),
        ("Tutor", demo_tutor),
        ("Grammar Checker", demo_grammar_checker),
        ("Conversation", demo_conversation),
        ("Exercise Generator", demo_exercise_generator),
        ("Complete Flow", demo_complete_flow),
    ]
    
    print("\nAvailable demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos)+1}. Run all demos")
    print("  0. Exit")
    
    try:
        choice = input("\nSelect demo (0-7): ").strip()
        
        if choice == "0":
            print("\nGoodbye! 👋")
            return
        
        if choice == str(len(demos) + 1):
            # Run all demos
            for name, demo_func in demos:
                await demo_func()
                await asyncio.sleep(1)
        else:
            # Run selected demo
            idx = int(choice) - 1
            if 0 <= idx < len(demos):
                await demos[idx][1]()
            else:
                print("Invalid choice!")
        
        print("\n" + "="*60)
        print("Demo completed! Check the code to see how it works.")
        print("="*60 + "\n")
        
    except ValueError:
        print("Invalid input!")
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye! 👋")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if .env exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("   Create .env from .env.example and add your API keys.\n")
    
    asyncio.run(main())
