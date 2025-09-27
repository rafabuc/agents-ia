"""
Exercise Generator Agent - Personalized Exercise Creation
"""
from langchain_openai import ChatOpenAI
from langsmith import traceable
from typing import List, Dict
from enum import Enum
import json
import logging

from config import settings

logger = logging.getLogger(__name__)


class ExerciseType(str, Enum):
    """Types of exercises that can be generated."""
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    SENTENCE_REORDER = "sentence_reorder"
    TRANSLATION = "translation"
    WRITING_PROMPT = "writing_prompt"
    MATCHING = "matching"
    TRUE_FALSE = "true_false"
    ERROR_CORRECTION = "error_correction"


class ExerciseGeneratorAgent:
    """Agent for generating personalized exercises."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_GPT_MODEL,
            temperature=0.7
        )
    
    @traceable(name="exercise_generate_set")
    async def generate_exercise_set(
        self,
        topic: str,
        level: str,
        exercise_types: List[ExerciseType],
        quantity: int = 10
    ) -> List[Dict]:
        """Generate a diverse set of exercises.
        
        Args:
            topic: Topic to practice
            level: CEFR level
            exercise_types: Types of exercises to include
            quantity: Total number of exercises
            
        Returns:
            List of exercises with questions and answers
        """
        exercises = []
        
        # Distribute quantity across exercise types
        exercises_per_type = max(1, quantity // len(exercise_types))
        
        for exercise_type in exercise_types:
            type_exercises = await self._generate_by_type(
                exercise_type=exercise_type,
                topic=topic,
                level=level,
                quantity=exercises_per_type
            )
            exercises.extend(type_exercises)
        
        # Trim to exact quantity if over
        exercises = exercises[:quantity]
        
        logger.info(f"Generated {len(exercises)} exercises for {topic} at {level} level")
        return exercises
    
    async def _generate_by_type(
        self,
        exercise_type: ExerciseType,
        topic: str,
        level: str,
        quantity: int
    ) -> List[Dict]:
        """Generate exercises of specific type."""
        
        prompt = self._get_prompt_for_type(exercise_type, topic, level, quantity)
        
        try:
            response = await self.llm.ainvoke(prompt)
            exercises = json.loads(response.content)
            
            # Ensure it's a list
            if isinstance(exercises, dict):
                exercises = exercises.get("exercises", [exercises])
            
            # Add metadata
            for ex in exercises:
                ex["type"] = exercise_type.value
                ex["topic"] = topic
                ex["level"] = level
            
            return exercises
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse exercises: {e}")
            return []
    
    def _get_prompt_for_type(self, exercise_type: ExerciseType, topic: str, level: str, qty: int) -> str:
        """Get appropriate prompt for exercise type."""
        
        if exercise_type == ExerciseType.MULTIPLE_CHOICE:
            return f"""Create {qty} multiple choice questions about {topic} for {level} level.

Format each as JSON:
{{
  "question": "Question text",
  "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
  "correct_answer": "A",
  "explanation": "Why this is correct"
}}

Return as JSON array. Make questions engaging and educational."""

        elif exercise_type == ExerciseType.FILL_IN_BLANK:
            return f"""Create {qty} fill-in-the-blank exercises for {topic} ({level} level).

Format each as JSON:
{{
  "sentence": "The cat ___ on the mat.",
  "answer": "sat",
  "alternatives": ["sits", "sitting", "to sit"],
  "hint": "past tense of 'sit'",
  "difficulty": "easy|medium|hard"
}}

Return as JSON array."""

        elif exercise_type == ExerciseType.SENTENCE_REORDER:
            return f"""Create {qty} sentence reordering exercises for {topic} ({level} level).

Format each as JSON:
{{
  "scrambled_words": ["always", "I", "coffee", "morning", "drink", "the", "in"],
  "correct_sentence": "I always drink coffee in the morning.",
  "hint": "Think about word order in English",
  "grammar_focus": "adverb placement"
}}

Return as JSON array."""

        elif exercise_type == ExerciseType.TRANSLATION:
            return f"""Create {qty} translation exercises for {topic} ({level} level).

Format each as JSON:
{{
  "source_language": "Spanish",
  "source_text": "Me gusta leer libros.",
  "target_language": "English",
  "correct_translation": "I like to read books.",
  "alternative_translations": ["I like reading books.", "I enjoy reading books."],
  "notes": "Multiple correct translations possible"
}}

Return as JSON array. Use common source languages for English learners."""

        elif exercise_type == ExerciseType.ERROR_CORRECTION:
            return f"""Create {qty} error correction exercises for {topic} ({level} level).

Format each as JSON:
{{
  "incorrect_sentence": "She don't like pizza.",
  "correct_sentence": "She doesn't like pizza.",
  "error_type": "subject-verb agreement",
  "explanation": "Use 'doesn't' with third person singular (he/she/it)",
  "similar_examples": ["He don't go → He doesn't go"]
}}

Return as JSON array."""

        elif exercise_type == ExerciseType.MATCHING:
            return f"""Create {qty} matching exercises for {topic} ({level} level).

Format each as JSON:
{{
  "instruction": "Match the words with their definitions",
  "left_column": ["word1", "word2", "word3", "word4"],
  "right_column": ["definition1", "definition2", "definition3", "definition4"],
  "correct_matches": {{
    "word1": "definition1",
    "word2": "definition2",
    "word3": "definition3",
    "word4": "definition4"
  }}
}}

Return as JSON array."""

        elif exercise_type == ExerciseType.TRUE_FALSE:
            return f"""Create {qty} true/false questions for {topic} ({level} level).

Format each as JSON:
{{
  "statement": "The present perfect is used for completed actions in the past.",
  "correct_answer": false,
  "explanation": "The present perfect connects past to present, not just completed actions.",
  "correction": "Use simple past for completed actions at a specific time."
}}

Return as JSON array."""

        else:  # WRITING_PROMPT
            return f"""Create {qty} writing prompts for {topic} ({level} level).

Format each as JSON:
{{
  "prompt": "Write about your favorite hobby",
  "word_count": "100-150 words",
  "key_vocabulary": ["enjoyable", "practice", "skill", "passion", "regularly"],
  "grammar_focus": "Present simple for habits and routines",
  "evaluation_criteria": ["Vocabulary use", "Grammar accuracy", "Organization", "Content"],
  "example_opening": "My favorite hobby is..."
}}

Return as JSON array."""
    
    @traceable(name="exercise_generate_writing_prompt")
    async def generate_writing_prompt(self, level: str, interests: List[str] = None) -> Dict:
        """Generate creative writing prompt based on interests.
        
        Args:
            level: Student's level
            interests: Student's interests
            
        Returns:
            Detailed writing prompt
        """
        interests_str = ", ".join(interests) if interests else "general topics"
        
        prompt = f"""Create an engaging writing prompt for {level} level student.

Student interests: {interests_str}

Provide complete prompt in JSON:
{{
  "title": "Catchy title",
  "prompt": "2-3 sentences describing what to write",
  "suggested_word_count": 150,
  "key_vocabulary": ["word1", "word2", "word3", "word4", "word5"],
  "grammar_focus": ["structure1", "structure2"],
  "evaluation_criteria": [
    {{"criterion": "Vocabulary", "weight": 25, "description": "..."}}
  ],
  "brainstorming_questions": ["question1", "question2", "question3"],
  "example_outline": {{
    "introduction": "brief note",
    "body": "brief note",
    "conclusion": "brief note"
  }},
  "tips": ["tip1", "tip2", "tip3"]
}}

Make it interesting and relevant to their interests!"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse writing prompt: {e}")
            return {"error": str(e)}
    
    @traceable(name="exercise_generate_adaptive")
    async def generate_adaptive_exercise(
        self,
        topic: str,
        level: str,
        previous_performance: Dict
    ) -> Dict:
        """Generate exercise adapted to student's performance.
        
        Args:
            topic: Topic to practice
            level: Current level
            previous_performance: Data about past performance
            
        Returns:
            Adaptive exercise
        """
        avg_score = previous_performance.get("average_score", 70)
        weak_areas = previous_performance.get("weak_areas", [])
        
        # Adjust difficulty
        if avg_score > 85:
            difficulty = "challenging"
        elif avg_score > 70:
            difficulty = "standard"
        else:
            difficulty = "reinforcement"
        
        prompt = f"""Create an adaptive exercise for {topic} at {level} level.

Performance context:
- Average score: {avg_score}%
- Weak areas: {', '.join(weak_areas)}
- Difficulty needed: {difficulty}

Create exercise in JSON that:
1. Addresses weak areas if they exist
2. Matches appropriate difficulty
3. Builds on previous learning
4. Provides scaffolding if needed

Format:
{{
  "exercise_type": "type",
  "difficulty": "{difficulty}",
  "question": "...",
  "answer": "...",
  "hints": ["progressive hints from general to specific"],
  "scaffolding": ["steps to solve if struggling"],
  "explanation": "why this exercise was chosen"
}}"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse adaptive exercise: {e}")
            return {"error": str(e)}
    
    @traceable(name="exercise_evaluate_answer")
    async def evaluate_answer(
        self,
        exercise: Dict,
        student_answer: str,
        level: str
    ) -> Dict:
        """Evaluate student's answer to an exercise.
        
        Args:
            exercise: The exercise data
            student_answer: Student's response
            level: Student's level
            
        Returns:
            Evaluation with feedback
        """
        exercise_json = json.dumps(exercise, indent=2)
        
        prompt = f"""Evaluate this student's answer ({level} level).

Exercise:
{exercise_json}

Student's answer: "{student_answer}"

Provide evaluation in JSON:
{{
  "is_correct": true/false,
  "score": 0-100,
  "feedback": "Encouraging, specific feedback",
  "explanation": "Why correct/incorrect",
  "correct_answer": "if applicable",
  "partial_credit": {{
    "earned": "what was correct",
    "missed": "what was incorrect"
  }},
  "next_steps": ["suggestion1", "suggestion2"]
}}

Be encouraging and constructive, especially if incorrect."""
        
        try:
            response = await self.llm.ainvoke(prompt)
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse evaluation: {e}")
            return {"error": str(e)}
