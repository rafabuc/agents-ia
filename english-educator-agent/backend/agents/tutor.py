"""
Tutor Agent - Lesson Creation and Concept Explanation
"""
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langsmith import traceable
from typing import List, Dict
import json
import logging

from config import settings

logger = logging.getLogger(__name__)


class TutorAgent:
    """Agent for creating lessons and explaining concepts."""
    
    def __init__(self, retriever=None):
        self.llm = ChatAnthropic(
            model=settings.DEFAULT_CLAUDE_MODEL,
            temperature=0.7
        )
        self.retriever = retriever
        self.tools = [
            self.create_lesson,
            self.explain_grammar,
            self.provide_examples,
            self.suggest_resources
        ]
    
    @tool
    @traceable(name="tutor_create_lesson")
    def create_lesson(self, topic: str, level: str) -> dict:
        """Create a personalized lesson for the given topic and level.
        
        Args:
            topic: The topic to teach (e.g., "Present Perfect Tense")
            level: CEFR level (A1, A2, B1, B2, C1, C2)
        
        Returns:
            Structured lesson with objectives, content, examples, and exercises
        """
        prompt = f"""Create a comprehensive {level}-level lesson on: {topic}

The lesson should be engaging, clear, and appropriate for {level} level students.

Include:
1. Learning objectives (3-5 clear, achievable goals)
2. Key vocabulary (10-15 words with simple definitions)
3. Grammar focus (if applicable, with clear rules)
4. Examples and usage (5-7 practical examples)
5. Practice exercises (5 varied exercises)
6. Cultural notes (if relevant to the topic)
7. Common mistakes to avoid
8. Tips for mastery

Format as structured JSON with clear sections."""
        
        response = self.llm.invoke(prompt)
        
        try:
            lesson = json.loads(response.content)
            return lesson
        except json.JSONDecodeError:
            # Return as plain text if JSON parsing fails
            return {
                "topic": topic,
                "level": level,
                "content": response.content
            }
    
    @tool
    @traceable(name="tutor_explain_grammar")
    def explain_grammar(self, concept: str, level: str) -> str:
        """Explain a grammar concept with examples.
        
        Args:
            concept: Grammar concept to explain
            level: Student's CEFR level
            
        Returns:
            Clear explanation with examples
        """
        prompt = f"""Explain "{concept}" for {level} level students.
        
        Structure your explanation:
        1. Simple, clear definition (1-2 sentences)
        2. Formation/Rules (step by step)
        3. 3-5 example sentences with translation or explanation
        4. Common mistakes to avoid (2-3)
        5. Practice tip or memory aid
        
        Use simple language appropriate for {level} level.
        Be encouraging and avoid overwhelming technical terms."""
        
        response = self.llm.invoke(prompt)
        return response.content
    
    @tool
    @traceable(name="tutor_provide_examples")
    def provide_examples(self, word_or_phrase: str, context: str = "general") -> List[str]:
        """Provide contextual examples of word/phrase usage.
        
        Args:
            word_or_phrase: The word or phrase to exemplify
            context: Context for examples (e.g., "business", "casual", "academic")
            
        Returns:
            List of example sentences
        """
        prompt = f"""Give 5 example sentences using "{word_or_phrase}" in {context} context.
        
        Requirements:
        - Vary sentence complexity (simple to more complex)
        - Use different tenses where applicable
        - Show different formality levels if relevant
        - Make examples natural and practical
        - Include brief notes on usage if helpful
        
        Format as a numbered list."""
        
        response = self.llm.invoke(prompt)
        
        # Parse examples from response
        examples = [line.strip() for line in response.content.split('\n') if line.strip() and any(line.startswith(str(i)) for i in range(1, 10))]
        return examples if examples else [response.content]
    
    @tool
    @traceable(name="tutor_suggest_resources")
    def suggest_resources(self, topic: str, level: str) -> Dict[str, List[str]]:
        """Suggest learning resources for a topic.
        
        Args:
            topic: Topic to find resources for
            level: Student's level
            
        Returns:
            Categorized resources (videos, exercises, reading, etc.)
        """
        prompt = f"""Suggest learning resources for {level} level students learning about: {topic}

Categories to include:
1. Online exercises (websites/apps)
2. Video resources (YouTube channels, educational videos)
3. Reading materials (articles, blogs, books)
4. Podcasts or audio resources
5. Interactive tools or games

Provide 2-3 specific suggestions per category with brief descriptions.
Format as JSON."""
        
        response = self.llm.invoke(prompt)
        
        try:
            resources = json.loads(response.content)
            return resources
        except json.JSONDecodeError:
            return {"general": [response.content]}
    
    @traceable(name="tutor_create_lesson_with_rag")
    async def create_lesson_with_rag(self, topic: str, level: str) -> dict:
        """Create lesson augmented with retrieved educational content."""
        
        if not self.retriever:
            # Fallback to standard lesson creation
            return self.create_lesson(topic, level)
        
        # Retrieve relevant content
        relevant_docs = await self.retriever.hybrid_search(
            query=f"lesson plan {topic}",
            student_level=level,
            filters={"type": "lesson"},
            k=5
        )
        
        # Build context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        prompt = f"""Create a comprehensive lesson on "{topic}" for {level} level students.

Retrieved educational content for reference:
{context}

Create an original, engaging lesson that:
1. Uses the retrieved content as reference and inspiration
2. Is specifically adapted to {level} level
3. Includes interactive elements
4. Provides clear, practical examples
5. Includes varied practice exercises

Format as structured JSON with sections: 
- objectives
- vocabulary  
- grammar_focus
- explanations
- examples
- exercises
- tips
- resources"""
        
        response = await self.llm.ainvoke(prompt)
        
        try:
            lesson = json.loads(response.content)
            lesson["sources"] = [doc.metadata for doc in relevant_docs]
            return lesson
        except json.JSONDecodeError:
            return {
                "topic": topic,
                "level": level,
                "content": response.content,
                "sources": [doc.metadata for doc in relevant_docs]
            }
    
    @traceable(name="tutor_answer_question")
    async def answer_question(self, question: str, context: dict) -> str:
        """Answer student's question about English.
        
        Args:
            question: Student's question
            context: Additional context (level, current topic, etc.)
            
        Returns:
            Clear, helpful answer
        """
        student_level = context.get("level", "B1")
        current_topic = context.get("topic", "general English")
        
        prompt = f"""Answer this student's question clearly and helpfully.

Student level: {student_level}
Current topic: {current_topic}
Question: {question}

Guidelines:
- Use language appropriate for {student_level} level
- Be clear, concise, and encouraging
- Provide examples if helpful
- Relate to {current_topic} if relevant
- Suggest next steps or practice if appropriate"""
        
        response = await self.llm.ainvoke(prompt)
        return response.content
