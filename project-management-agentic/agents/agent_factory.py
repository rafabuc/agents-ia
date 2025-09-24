# agents/agent_factory.py
from typing import Dict, Any, Optional, Type
from .base_agent import BaseAgent
from .pmp_project_agent import PMPProjectAgent
from .cost_budget_agent import CostBudgetAgent
from .template_agent import TemplateAgent
from utils.logger import logger


class AgentFactory:
    """Factory for creating and managing agents."""
    
    def __init__(self):
        self._agent_classes: Dict[str, Type[BaseAgent]] = {
            "pmp_project": PMPProjectAgent,
            "cost_budget": CostBudgetAgent,
            "template": TemplateAgent
        }
        self._agent_instances: Dict[str, BaseAgent] = {}
        logger.info("AgentFactory initialized")
    
    def create_agent(self, agent_type: str, **kwargs) -> BaseAgent:
        """Create or get existing agent instance."""
        if agent_type not in self._agent_classes:
            available_types = ", ".join(self._agent_classes.keys())
            raise ValueError(f"Unknown agent type: {agent_type}. Available: {available_types}")
        
        # Return existing instance if available (singleton pattern)
        if agent_type in self._agent_instances:
            return self._agent_instances[agent_type]
        
        # Create new instance
        agent_class = self._agent_classes[agent_type]
        agent = agent_class(**kwargs)
        agent.initialize()
        
        # Store instance
        self._agent_instances[agent_type] = agent
        
        logger.info(f"Created agent: {agent_type}")
        return agent
    
    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Get existing agent instance."""
        return self._agent_instances.get(agent_type)
    
    def register_agent(self, agent_type: str, agent_class: Type[BaseAgent]):
        """Register a new agent type."""
        self._agent_classes[agent_type] = agent_class
        logger.info(f"Registered new agent type: {agent_type}")
    
    def list_available_agents(self) -> Dict[str, str]:
        """List all available agent types with descriptions."""
        agents = {}
        for agent_type, agent_class in self._agent_classes.items():
            # Get description from agent instance or class
            try:
                if agent_type in self._agent_instances:
                    description = self._agent_instances[agent_type].description
                else:
                    # Create temporary instance to get description
                    temp_agent = agent_class()
                    description = temp_agent.description
                agents[agent_type] = description
            except Exception:
                agents[agent_type] = "Agent description not available"
        
        return agents
    
    def get_agent_info(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an agent."""
        if agent_type not in self._agent_classes:
            return None
        
        if agent_type in self._agent_instances:
            return self._agent_instances[agent_type].get_agent_info()
        else:
            return {
                "name": agent_type,
                "class": self._agent_classes[agent_type].__name__,
                "initialized": False
            }
    
    def cleanup_agents(self):
        """Clean up all agent instances."""
        for agent in self._agent_instances.values():
            try:
                agent.clear_memory()
            except Exception as e:
                logger.warning(f"Error cleaning up agent: {str(e)}")
        
        self._agent_instances.clear()
        logger.info("All agents cleaned up")
