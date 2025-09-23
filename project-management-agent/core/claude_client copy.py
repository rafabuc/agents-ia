import asyncio
import json
from typing import List, Dict, Optional, AsyncGenerator
from anthropic import Anthropic, AsyncAnthropic
from loguru import logger
from config.settings import settings

class ClaudeClient:
    """Cliente para interactuar con la API de Claude"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.claude.api_key)
        self.async_client = AsyncAnthropic(api_key=settings.claude.api_key)
        self.conversation_history: List[Dict] = []
        
    def add_to_history(self, role: str, content: str):
        """Agregar mensaje al historial de conversación"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def chat(self, message: str, system_prompt: str = "", context: Optional[Dict] = None) -> str:
        """Enviar mensaje a Claude y recibir respuesta"""
        try:
            messages = self.conversation_history.copy()
            messages.append({"role": "user", "content": message})
            
            response = self.client.messages.create(
                model=settings.claude.model,
                max_tokens=settings.claude.max_tokens,
                temperature=settings.claude.temperature,
                system=system_prompt,
                messages=messages
            )
            
            response_text = response.content[0].text
            
            self.add_to_history("user", message)
            self.add_to_history("assistant", response_text)
            
            logger.info("Claude response generated")
            return response_text
            
        except Exception as e:
            logger.error(f"Error communicating with Claude: {e}")
            raise
    
    def clear_history(self):
        """Limpiar historial de conversación"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
