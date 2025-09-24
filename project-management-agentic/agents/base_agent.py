from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from config.settings import settings
from storage.database_manager import DatabaseManager
from utils.logger import logger


class BaseAgent(ABC):
    """Base class for all PMP agents."""
    
    def __init__(
        self,
        name: str,
        description: str,
        llm_provider: str = None,
        model: str = None,
    ):
        self.name = name
        self.description = description
        self.llm_provider = llm_provider or settings.default_llm_provider
        self.model = model or settings.default_model
        
        # Initialize LLM
        self.llm = self._get_llm()
        
        # Database manager
        self.db_manager = DatabaseManager()
        
        logger.info(f"Initialized agent: {self.name}")
    
    def _get_llm(self):
        """Get the appropriate LLM based on provider."""
        if self.llm_provider.lower() == "openai":
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            return ChatOpenAI(
                api_key=settings.openai_api_key,
                model=self.model,
                temperature=0.1
            )
        elif self.llm_provider.lower() == "anthropic":
            if not settings.anthropic_api_key:
                raise ValueError("Anthropic API key not configured")
            return ChatAnthropic(
                api_key=settings.anthropic_api_key,
                model=self.model,
                temperature=0.1
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
    
    def initialize(self):
        """Initialize the agent."""
        logger.info(f"Agent {self.name} initialized successfully")
    
    def process(self, input_text: str, session_id: Optional[int] = None) -> Dict[str, Any]:
        """Process input and return response."""
        # Simple implementation - override in subclasses
        return {
            "agent": self.name,
            "response": f"Processed: {input_text}",
            "timestamp": datetime.utcnow().isoformat()
        }
