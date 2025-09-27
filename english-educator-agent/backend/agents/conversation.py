"""
Conversation Partner Agent - Natural English Practice
"""
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langsmith import traceable
from typing import List, Dict
import logging

from config import settings

logger = logging.getLogger(__name__)


class ConversationPartnerAgent:
    """Agent for natural conversation practice."""
    
    def __init__(self):
        self.llm = ChatAnthropic(
            model=settings.DEFAULT_CLAUDE_MODEL,
            temperature=0.9  # Higher temperature for more natural variation
        )
        self.conversation_memory: Dict[int, List] = {}
    
    @traceable(name="conversation_chat")
    async def chat(self, user_message: str, context: dict) -> dict:
        """Natural conversation with pedagogical intent.
        
        Args:
            user_message: User's message
            context: Context including level, topic, user_id
            
        Returns:
            Response with reply, corrections, new vocabulary
        """
        user_id = context.get("user_id", 0)
        level = context.get("level", "B1")
        topic = context.get("topic", "general")
        goals = context.get("goals", [])
        
        # Get or initialize conversation history
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = []
        
        system_context = f"""You are a friendly, encouraging English conversation partner.

Student Profile:
- Level: {level} (CEFR)
- Current topic: {topic}
- Learning goals: {', '.join(goals) if goals else 'general improvement'}

Your Role:
- Maintain natural, engaging conversation
- Match language complexity to {level} level
- Gently model correct forms without explicitly correcting (natural recasting)
- Ask follow-up questions to encourage more speaking
- Introduce new vocabulary occasionally (1-2 words per exchange)
- Be supportive and build confidence
- Make the conversation feel authentic and enjoyable

Conversation Guidelines:
- Use contractions and natural speech patterns
- Show interest in what the student says
- Vary your sentence structures
- Include some idioms/phrasal verbs appropriate for {level}
- Keep responses conversational (not too long)"""

        # Build message history
        messages = [
            {"role": "system", "content": system_context}
        ] + self.conversation_memory[user_id] + [
            {"role": "user", "content": user_message}
        ]
        
        # Get response
        response = await self.llm.ainvoke(messages)
        
        # Analyze user's message in background
        analysis = await self._analyze_message(user_message, level)
        
        # Update conversation memory (keep last 10 exchanges)
        self.conversation_memory[user_id].append(
            {"role": "user", "content": user_message}
        )
        self.conversation_memory[user_id].append(
            {"role": "assistant", "content": response.content}
        )
        
        if len(self.conversation_memory[user_id]) > 20:  # 10 exchanges
            self.conversation_memory[user_id] = self.conversation_memory[user_id][-20:]
        
        return {
            "reply": response.content,
            "corrections": analysis.get("corrections", []),
            "new_vocabulary": analysis.get("vocabulary_introduced", []),
            "engagement_score": analysis.get("engagement_score", 0.5),
            "suggestions": analysis.get("suggestions", [])
        }
    
    @traceable(name="conversation_analyze_message")
    async def _analyze_message(self, message: str, level: str) -> dict:
        """Analyze user's message for errors and learning opportunities.
        
        This runs in background without interrupting conversation flow.
        """
        analysis_prompt = f"""Analyze this student message ({level} level):

"{message}"

Provide brief analysis:
1. Major errors (only critical ones worth noting)
2. Good language use (positive reinforcement)
3. Engagement level (0.0-1.0)
4. Suggested improvements (1-2 specific tips)

Format as JSON:
{{
    "corrections": [
        {{"error": "...", "correction": "...", "note": "brief explanation"}}
    ],
    "strengths": ["point1", "point2"],
    "engagement_score": 0.0-1.0,
    "suggestions": ["tip1", "tip2"],
    "vocabulary_introduced": ["word1", "word2"]
}}

Be encouraging - only note significant errors."""
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=analysis_prompt)
            ])
            
            import json
            return json.loads(response.content)
        except Exception as e:
            logger.error(f"Message analysis failed: {e}")
            return {
                "corrections": [],
                "strengths": [],
                "engagement_score": 0.5,
                "suggestions": [],
                "vocabulary_introduced": []
            }
    
    def clear_conversation(self, user_id: int):
        """Clear conversation history for a user."""
        if user_id in self.conversation_memory:
            del self.conversation_memory[user_id]
            logger.info(f"Cleared conversation history for user {user_id}")
    
    def get_conversation_summary(self, user_id: int) -> dict:
        """Get summary of conversation."""
        if user_id not in self.conversation_memory:
            return {"message": "No conversation history"}
        
        history = self.conversation_memory[user_id]
        return {
            "user_id": user_id,
            "message_count": len(history),
            "last_messages": history[-6:] if len(history) >= 6 else history
        }
