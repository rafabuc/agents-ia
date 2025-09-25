"""
Agent Orchestrator - Central coordinator for multi-agent system
Handles routing, coordination, and communication between specialized agents
"""

from typing import Dict, Any, List, Optional, Type
from abc import ABC, abstractmethod
import asyncio
from enum import Enum

from .base_agent import BaseAgent
from utils.logger import logger


class TaskType(Enum):
    """Define different types of tasks that can be handled by agents"""
    PROJECT_CREATION = "project_creation"
    DOCUMENT_GENERATION = "document_generation"
    RISK_ANALYSIS = "risk_analysis"
    STAKEHOLDER_MANAGEMENT = "stakeholder_management"
    SCHEDULE_MANAGEMENT = "schedule_management"
    BUDGET_ANALYSIS = "budget_analysis"
    REPORTING = "reporting"
    GENERAL_QUERY = "general_query"


class AgentCapability(Enum):
    """Define capabilities that agents can have"""
    PROJECT_CHARTER = "project_charter"
    WBS_CREATION = "wbs_creation"
    RISK_REGISTER = "risk_register"
    STAKEHOLDER_MAPPING = "stakeholder_mapping"
    COST_ESTIMATION = "cost_estimation"
    BUDGET_MANAGEMENT = "budget_management"
    SCHEDULE_OPTIMIZATION = "schedule_optimization"
    REPORT_GENERATION = "report_generation"


class TaskContext:
    """Context object that gets passed between agents"""

    def __init__(self, user_input: str, project_id: Optional[int] = None):
        self.user_input = user_input
        self.project_id = project_id
        self.intent: Optional[str] = None
        self.parameters: Dict[str, Any] = {}
        self.requires_collaboration = False
        self.primary_agent: Optional[str] = None
        self.secondary_agents: List[str] = []
        self.intermediate_results: Dict[str, Any] = {}

    def add_result(self, agent_name: str, result: Dict[str, Any]):
        """Add result from an agent to the context"""
        self.intermediate_results[agent_name] = result

    def get_result(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get result from a specific agent"""
        return self.intermediate_results.get(agent_name)


class AgentOrchestrator:
    """
    Central coordinator that manages multiple specialized agents
    Routes tasks to appropriate agents and coordinates multi-agent workflows
    """

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_routing: Dict[TaskType, str] = {}
        self.agent_capabilities: Dict[str, List[AgentCapability]] = {}
        self._setup_routing()

        logger.info("AgentOrchestrator initialized")

    def register_agent(self, agent: BaseAgent, capabilities: List[AgentCapability]):
        """Register an agent with its capabilities"""
        agent_name = agent.name
        self.agents[agent_name] = agent
        self.agent_capabilities[agent_name] = capabilities

        logger.info(f"Registered agent: {agent_name} with capabilities: {[cap.value for cap in capabilities]}")

    def _setup_routing(self):
        """Setup default routing rules for different task types"""
        self.task_routing = {
            TaskType.PROJECT_CREATION: "project_manager_agent",
            TaskType.DOCUMENT_GENERATION: "document_agent",
            TaskType.RISK_ANALYSIS: "risk_management_agent",
            TaskType.STAKEHOLDER_MANAGEMENT: "stakeholder_agent",
            TaskType.SCHEDULE_MANAGEMENT: "schedule_agent",
            TaskType.BUDGET_ANALYSIS: "cost_budget_agent",  # Use existing CostBudgetAgent
            TaskType.REPORTING: "analytics_agent",
            TaskType.GENERAL_QUERY: "project_manager_agent"
        }

    async def process_request(self, user_input: str, project_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Main entry point for processing user requests
        Analyzes intent and routes to appropriate agent(s)
        """
        try:
            # Create task context
            context = TaskContext(user_input, project_id)

            # Try to extract project context from user input if not provided
            if not project_id:
                extracted_id = self._extract_project_id_from_input(user_input)
                if extracted_id:
                    context.project_id = extracted_id

            # Analyze intent and determine routing
            await self._analyze_intent(context)

            # Route to appropriate agent(s)
            if context.requires_collaboration:
                return await self._coordinate_multi_agent_task(context)
            else:
                return await self._route_to_single_agent(context)

        except Exception as e:
            logger.error(f"Error in process_request: {str(e)}")
            return {
                "success": False,
                "error": f"Orchestration error: {str(e)}",
                "response": "Lo siento, hubo un error procesando tu solicitud."
            }

    async def _analyze_intent(self, context: TaskContext):
        """
        Analyze user input to determine intent and routing
        This is a simplified version - in a real implementation this would use LLM
        """
        user_input_lower = context.user_input.lower()

        # Simple intent detection based on keywords
        intent_patterns = {
            TaskType.PROJECT_CREATION: ["crear proyecto", "nuevo proyecto", "iniciar proyecto"],
            TaskType.DOCUMENT_GENERATION: ["charter", "documento", "plantilla", "generar"],
            TaskType.RISK_ANALYSIS: ["riesgo", "risk", "análisis de riesgo"],
            TaskType.STAKEHOLDER_MANAGEMENT: ["stakeholder", "interesado", "comunicación"],
            TaskType.SCHEDULE_MANAGEMENT: ["cronograma", "schedule", "tiempo", "wbs"],
            TaskType.BUDGET_ANALYSIS: ["presupuesto", "costo", "budget", "precio", "estimación", "coste"],
            TaskType.REPORTING: ["reporte", "informe", "dashboard", "analítica"],
        }

        # Determine primary task type
        detected_task = TaskType.GENERAL_QUERY  # Default
        for task_type, keywords in intent_patterns.items():
            if any(keyword in user_input_lower for keyword in keywords):
                detected_task = task_type
                break

        # Set context
        context.intent = detected_task.value
        context.primary_agent = self.task_routing.get(detected_task, "project_manager_agent")

        # Determine if collaboration is needed
        context.requires_collaboration = self._needs_collaboration(detected_task, user_input_lower)

        if context.requires_collaboration:
            context.secondary_agents = self._get_secondary_agents(detected_task)

    def _needs_collaboration(self, task_type: TaskType, user_input: str) -> bool:
        """Determine if a task requires multiple agents"""
        collaboration_indicators = {
            TaskType.PROJECT_CREATION: ["completo", "todo", "full", "integral"],
            TaskType.DOCUMENT_GENERATION: ["con riesgos", "con presupuesto", "completo"],
        }

        indicators = collaboration_indicators.get(task_type, [])
        return any(indicator in user_input for indicator in indicators)

    def _get_secondary_agents(self, task_type: TaskType) -> List[str]:
        """Get secondary agents needed for collaborative tasks"""
        secondary_mapping = {
            TaskType.PROJECT_CREATION: ["document_agent", "risk_management_agent"],
            TaskType.DOCUMENT_GENERATION: ["risk_management_agent", "budget_agent"],
        }

        return secondary_mapping.get(task_type, [])

    async def _route_to_single_agent(self, context: TaskContext) -> Dict[str, Any]:
        """Route task to a single agent"""
        agent_name = context.primary_agent

        if agent_name not in self.agents:
            logger.warning(f"Agent {agent_name} not found, using fallback")
            # Fallback to first available agent or return error
            if self.agents:
                agent_name = list(self.agents.keys())[0]
            else:
                return {
                    "success": False,
                    "error": "No agents available",
                    "response": "Sistema no disponible"
                }

        agent = self.agents[agent_name]
        logger.info(f"Routing to single agent: {agent_name}")

        # Process with the agent
        result = await self._execute_agent_task(agent, context)
        return result

    async def _coordinate_multi_agent_task(self, context: TaskContext) -> Dict[str, Any]:
        """Coordinate a task that requires multiple agents"""
        logger.info(f"Coordinating multi-agent task: {context.primary_agent} + {context.secondary_agents}")

        # Execute primary agent first
        primary_agent = self.agents.get(context.primary_agent)
        if not primary_agent:
            return {
                "success": False,
                "error": f"Primary agent {context.primary_agent} not available",
                "response": "Agente principal no disponible"
            }

        # Execute primary task
        primary_result = await self._execute_agent_task(primary_agent, context)

        if not primary_result.get("success", False):
            return primary_result

        context.add_result(context.primary_agent, primary_result)

        # Execute secondary agents in parallel
        secondary_tasks = []
        for agent_name in context.secondary_agents:
            if agent_name in self.agents:
                agent = self.agents[agent_name]
                task = self._execute_agent_task(agent, context)
                secondary_tasks.append((agent_name, task))

        # Wait for all secondary tasks
        secondary_results = {}
        for agent_name, task in secondary_tasks:
            try:
                result = await task
                secondary_results[agent_name] = result
                context.add_result(agent_name, result)
            except Exception as e:
                logger.error(f"Error in secondary agent {agent_name}: {str(e)}")
                secondary_results[agent_name] = {
                    "success": False,
                    "error": str(e)
                }

        # Combine results
        return self._combine_agent_results(context, primary_result, secondary_results)

    async def _execute_agent_task(self, agent: BaseAgent, context: TaskContext) -> Dict[str, Any]:
        """Execute a task with a specific agent"""
        try:
            # For now, use the existing process method
            # In future iterations, agents should accept TaskContext
            if hasattr(agent, 'process_with_context'):
                return await agent.process_with_context(context)
            else:
                return agent.process(context.user_input)

        except Exception as e:
            logger.error(f"Error executing task with agent {agent.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": f"Error en {agent.name}"
            }

    def _combine_agent_results(self, context: TaskContext, primary_result: Dict[str, Any],
                              secondary_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Combine results from multiple agents into a cohesive response"""

        # Start with primary result
        combined_result = primary_result.copy()

        # Add information from secondary agents
        additional_info = []
        for agent_name, result in secondary_results.items():
            if result.get("success", False):
                response = result.get("response", "")
                if response:
                    additional_info.append(f"\n**{agent_name}**: {response}")

        # Enhance the response with additional information
        if additional_info:
            original_response = combined_result.get("response", "")
            combined_response = original_response + "\n\n**Información adicional:**" + "".join(additional_info)
            combined_result["response"] = combined_response

        # Add metadata about the coordination
        combined_result["coordination"] = {
            "primary_agent": context.primary_agent,
            "secondary_agents": context.secondary_agents,
            "agents_used": list(secondary_results.keys()) + [context.primary_agent]
        }

        return combined_result

    def get_available_agents(self) -> Dict[str, List[str]]:
        """Get list of available agents and their capabilities"""
        return {
            agent_name: [cap.value for cap in capabilities]
            for agent_name, capabilities in self.agent_capabilities.items()
        }

    def _extract_project_id_from_input(self, user_input: str) -> Optional[int]:
        """Extract project ID from user input"""
        import re

        # Look for patterns like "proyecto 13", "project 5", "para proyecto 13"
        patterns = [
            r'proyecto\s+(\d+)',
            r'project\s+(\d+)',
            r'para\s+proyecto\s+(\d+)',
            r'del\s+proyecto\s+(\d+)',
            r'ID\s+(\d+)',
            r'id\s+(\d+)'
        ]

        user_input_lower = user_input.lower()
        for pattern in patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue

        return None

    def get_system_status(self) -> Dict[str, Any]:
        """Get status of the orchestrator and all agents"""
        return {
            "orchestrator_status": "active",
            "registered_agents": len(self.agents),
            "agents": {
                name: {
                    "status": "active",
                    "capabilities": [cap.value for cap in self.agent_capabilities.get(name, [])]
                }
                for name in self.agents.keys()
            },
            "routing_rules": {task_type.value: agent for task_type, agent in self.task_routing.items()}
        }