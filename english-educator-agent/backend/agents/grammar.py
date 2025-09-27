"""
Grammar Checker Agent - Error Detection and Correction
"""
from langchain_openai import ChatOpenAI
from langsmith import traceable
from typing import Dict, List
import json
import logging

from config import settings

logger = logging.getLogger(__name__)


class GrammarCheckerAgent:
    """Agent for grammar checking and correction."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_GPT_MODEL,
            temperature=0.1  # Low temperature for consistent corrections
        )
    
    @traceable(name="grammar_check")
    async def check_grammar(self, text: str, student_level: str) -> Dict:
        """Check text for grammar errors with detailed feedback.
        
        Args:
            text: Text to check
            student_level: Student's CEFR level
            
        Returns:
            Detailed corrections and feedback
        """
        prompt = f"""Analyze this text for grammar errors. Student level: {student_level}

Text: "{text}"

Provide detailed, encouraging feedback in JSON format:
{{
  "corrections": [
    {{
      "original": "incorrect phrase from text",
      "corrected": "correct version",
      "error_type": "subject-verb agreement|tense|article|preposition|word order|etc",
      "explanation": "Simple explanation appropriate for {student_level}",
      "rule": "Grammar rule reference"
    }}
  ],
  "overall_quality": {{
    "score": 0-100,
    "level_assessment": "A1|A2|B1|B2|C1|C2",
    "strengths": ["what they did well", "positive aspects"],
    "areas_for_improvement": ["specific, actionable suggestions"]
  }},
  "vocabulary_feedback": {{
    "used_well": ["good vocabulary choices"],
    "could_improve": [
      {{"word": "basic word they used", "suggestion": "more sophisticated alternative", "context": "when to use it"}}
    ]
  }},
  "style_suggestions": ["tip1", "tip2"]
}}

Guidelines:
- Be encouraging and constructive
- Prioritize errors by importance (critical vs. minor)
- Adapt explanations to {student_level} level
- Provide specific examples
- If text is error-free, still provide constructive feedback"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            result = json.loads(response.content)
            
            # Log the check
            logger.info(f"Grammar check completed: {len(result.get('corrections', []))} corrections found")
            
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse grammar check response: {e}")
            return {
                "corrections": [],
                "overall_quality": {
                    "score": 0,
                    "level_assessment": student_level,
                    "strengths": [],
                    "areas_for_improvement": ["Unable to process text"]
                },
                "error": str(e)
            }
    
    @traceable(name="grammar_explain_error")
    async def explain_error(self, error_type: str, example: str, level: str) -> str:
        """Provide deep dive explanation of specific error type.
        
        Args:
            error_type: Type of grammar error
            example: Example of the error
            level: Student's level
            
        Returns:
            Detailed explanation
        """
        prompt = f"""Explain this grammar error in detail for a {level} level student.

Error type: {error_type}
Student's mistake: "{example}"

Provide:
1. **Why it's wrong** - Clear explanation
2. **Correct form** - How to fix it
3. **Grammar rule** - The rule being broken
4. **More examples** - 3 additional examples (wrong → correct)
5. **Memory tip** - Easy way to remember the rule
6. **Common contexts** - When this error commonly occurs

Use simple language appropriate for {level} level.
Be encouraging - everyone makes mistakes while learning!"""
        
        response = await self.llm.ainvoke(prompt)
        return response.content
    
    @traceable(name="grammar_analyze_conversation")
    async def analyze_conversation(self, messages: List[Dict], level: str) -> Dict:
        """Analyze entire conversation for patterns and insights.
        
        Args:
            messages: List of conversation messages
            level: Student's level
            
        Returns:
            Analysis of patterns and recommendations
        """
        conversation_text = "\n".join([
            f"Student: {msg.get('content', '')}" 
            for msg in messages 
            if msg.get('role') == 'user'
        ])
        
        prompt = f"""Analyze this conversation for grammar patterns and insights.

Student level: {level}

Conversation:
{conversation_text}

Provide analysis in JSON:
{{
  "recurring_errors": [
    {{
      "pattern": "description of error pattern",
      "frequency": "how often it appears",
      "examples": ["example1", "example2"],
      "focus_area": "what to study"
    }}
  ],
  "improvement_areas": [
    {{
      "skill": "grammar area needing work",
      "current_level": "assessment",
      "target_exercises": ["exercise type1", "exercise type2"]
    }}
  ],
  "strengths": ["what student does well consistently"],
  "progress_indicators": ["signs of improvement"],
  "recommendations": [
    {{
      "priority": "high|medium|low",
      "focus": "what to practice",
      "resources": ["suggested resources"],
      "time_frame": "suggested practice duration"
    }}
  ]
}}"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse conversation analysis: {e}")
            return {"error": str(e)}
    
    @traceable(name="grammar_compare_sentences")
    async def compare_sentences(self, original: str, corrected: str, level: str) -> Dict:
        """Compare original and corrected sentences with explanation.
        
        Args:
            original: Original sentence with errors
            corrected: Corrected sentence
            level: Student's level
            
        Returns:
            Detailed comparison and learning points
        """
        prompt = f"""Compare these sentences and explain the differences for a {level} student.

Original: "{original}"
Corrected: "{corrected}"

Provide detailed comparison in JSON:
{{
  "differences": [
    {{
      "aspect": "what changed (word, tense, structure, etc.)",
      "original": "original form",
      "corrected": "corrected form",
      "reason": "why it was changed",
      "rule": "grammar rule applied"
    }}
  ],
  "key_learning_points": ["point1", "point2", "point3"],
  "practice_suggestions": [
    {{
      "exercise": "what to practice",
      "example": "practice sentence"
    }}
  ]
}}

Make explanations clear and appropriate for {level} level."""
        
        try:
            response = await self.llm.ainvoke(prompt)
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse sentence comparison: {e}")
            return {"error": str(e)}
    
    @traceable(name="grammar_suggest_improvements")
    async def suggest_improvements(self, text: str, target_level: str, current_level: str) -> Dict:
        """Suggest ways to improve text to reach target level.
        
        Args:
            text: Current text
            target_level: Desired level
            current_level: Current level
            
        Returns:
            Suggestions for improvement
        """
        prompt = f"""Suggest improvements to elevate this text from {current_level} to {target_level} level.

Current text: "{text}"

Provide suggestions in JSON:
{{
  "improved_versions": [
    {{
      "version": "improved text",
      "level": "{target_level}",
      "changes_made": ["change1", "change2"],
      "new_structures_used": ["structure1", "structure2"],
      "vocabulary_upgraded": [
        {{"from": "simple word", "to": "advanced word"}}
      ]
    }}
  ],
  "learning_path": [
    {{
      "skill": "what to learn",
      "current_gap": "what's missing",
      "how_to_practice": "specific practice method"
    }}
  ],
  "complexity_analysis": {{
    "sentence_structure": "assessment",
    "vocabulary_range": "assessment",
    "grammar_variety": "assessment"
  }}
}}"""
        
        try:
            response = await self.llm.ainvoke(prompt)
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse improvement suggestions: {e}")
            return {"error": str(e)}
