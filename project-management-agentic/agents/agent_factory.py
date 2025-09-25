# agents/agent_factory.py
from typing import Dict, Any, Optional, Type
from .base_agent import BaseAgent
from .pmp_project_agent import PMPProjectAgent
from .cost_budget_agent import CostBudgetAgent
from .template_agent import TemplateAgent
from .project_manager_agent import ProjectManagerAgent
from .document_agent import DocumentAgent
from .risk_management_agent import RiskManagementAgent
from .orchestrator import AgentOrchestrator, AgentCapability
from utils.logger import logger


class AgentFactory:
    """Factory for creating and managing agents with orchestration support."""

    def __init__(self):
        # Register both legacy and new agent types
        self._agent_classes: Dict[str, Type[BaseAgent]] = {
            # Legacy agents
            "pmp_project": PMPProjectAgent,
            "cost_budget": CostBudgetAgent,
            "template": TemplateAgent,

            # New multi-agent architecture
            "project_manager_agent": ProjectManagerAgent,
            "document_agent": DocumentAgent,
            "risk_management_agent": RiskManagementAgent
        }
        self._agent_instances: Dict[str, BaseAgent] = {}
        self._orchestrator: Optional[AgentOrchestrator] = None
        logger.info("AgentFactory initialized with multi-agent support")
    
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
    
    def get_orchestrator(self) -> AgentOrchestrator:
        """Get or create the agent orchestrator."""
        if self._orchestrator is None:
            self._orchestrator = AgentOrchestrator()
            self._setup_orchestrator()
        return self._orchestrator

    def _setup_orchestrator(self):
        """Setup orchestrator with registered agents."""
        if self._orchestrator is None:
            return

        # Register new architecture agents with their capabilities
        agent_capabilities = {
            "project_manager_agent": [
                AgentCapability.PROJECT_CHARTER,
                # Project manager can coordinate all capabilities
            ],
            "document_agent": [
                AgentCapability.PROJECT_CHARTER,
                AgentCapability.WBS_CREATION,
                AgentCapability.REPORT_GENERATION
            ],
            "risk_management_agent": [
                AgentCapability.RISK_REGISTER,
            ],
            "cost_budget": [  # Add CostBudgetAgent integration
                AgentCapability.COST_ESTIMATION,
            ]
        }

        # Create and register agents with orchestrator
        for agent_type, capabilities in agent_capabilities.items():
            if agent_type in self._agent_classes:
                agent = self.create_agent(agent_type)
                self._orchestrator.register_agent(agent, capabilities)

        logger.info("Orchestrator setup completed with registered agents")

    async def process_with_orchestrator(self, user_input: str, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Process request using the orchestrator for intelligent routing."""
        orchestrator = self.get_orchestrator()
        return await orchestrator.process_request(user_input, project_id)

    def create_multiagent_system(self) -> Dict[str, Any]:
        """Initialize and return the complete multi-agent system."""
        orchestrator = self.get_orchestrator()

        # Get system status
        system_status = {
            "orchestrator": orchestrator.get_system_status(),
            "factory": {
                "registered_agents": len(self._agent_classes),
                "active_instances": len(self._agent_instances),
                "available_types": list(self._agent_classes.keys())
            }
        }

        logger.info("Multi-agent system initialized successfully")
        return system_status

    def migrate_from_legacy(self, legacy_agent_type: str) -> str:
        """Suggest migration path from legacy agents to new architecture."""
        migration_map = {
            "pmp_project": "project_manager_agent",
            "cost_budget": "budget_agent",  # Will be created later
            "template": "document_agent"
        }

        suggested_agent = migration_map.get(legacy_agent_type)
        if suggested_agent:
            return f"Consider migrating from '{legacy_agent_type}' to '{suggested_agent}' for enhanced capabilities"
        else:
            return f"No direct migration path found for '{legacy_agent_type}'"

    def cleanup_agents(self):
        """Clean up all agent instances."""
        for agent in self._agent_instances.values():
            try:
                if hasattr(agent, 'clear_memory'):
                    agent.clear_memory()
            except Exception as e:
                logger.warning(f"Error cleaning up agent: {str(e)}")

        self._agent_instances.clear()
        if self._orchestrator:
            self._orchestrator = None
        logger.info("All agents and orchestrator cleaned up")
