"""
Base Agent Class for DevOps AI Platform
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool


class BaseAgent(ABC):
    """
    Base class for all DevOps AI agents.
    Provides common functionality and interface for specialized agents.
    """

    def __init__(
        self,
        name: str,
        llm: BaseLanguageModel,
        tools: List[BaseTool],
        memory: Optional[ConversationBufferMemory] = None,
        verbose: bool = False
    ):
        self.name = name
        self.llm = llm
        self.tools = tools
        self.memory = memory or ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.verbose = verbose
        self.state = {}
        self.logger = logging.getLogger(f"agent.{name}")
        self._setup_logging()

        # Initialize agent executor
        self.agent_executor = self._create_agent_executor()

    def _setup_logging(self):
        """Setup logging for the agent"""
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f'%(asctime)s - {self.name} - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    @abstractmethod
    def _create_agent_executor(self) -> AgentExecutor:
        """Create and return the agent executor for this specific agent"""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass

    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task using the agent

        Args:
            task: The task description
            context: Optional context information

        Returns:
            Dictionary with execution results
        """
        self.logger.info(f"Executing task: {task}")

        try:
            # Update state with context
            if context:
                self.state.update(context)

            # Prepare input for agent
            agent_input = {
                "input": task,
                "context": context or {},
                "agent_state": self.state
            }

            # Execute the task
            result = await self.agent_executor.ainvoke(agent_input)

            # Update state with results
            self.update_state("last_execution", {
                "timestamp": datetime.now().isoformat(),
                "task": task,
                "result": result,
                "success": True
            })

            self.logger.info(f"Task completed successfully")
            return {
                "success": True,
                "result": result,
                "agent": self.name,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            self.update_state("last_execution", {
                "timestamp": datetime.now().isoformat(),
                "task": task,
                "error": str(e),
                "success": False
            })

            return {
                "success": False,
                "error": str(e),
                "agent": self.name,
                "timestamp": datetime.now().isoformat()
            }

    def update_state(self, key: str, value: Any):
        """Update agent state"""
        self.state[key] = value
        self.logger.debug(f"State updated: {key} = {value}")

    def get_state(self, key: str = None) -> Any:
        """Get agent state"""
        if key:
            return self.state.get(key)
        return self.state

    def reset_state(self):
        """Reset agent state"""
        self.state = {}
        self.memory.clear()
        self.logger.info("Agent state reset")

    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        return [tool.name for tool in self.tools]

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "tools": self.get_capabilities(),
            "state_keys": list(self.state.keys()),
            "memory_size": len(self.memory.chat_memory.messages),
            "last_execution": self.state.get("last_execution"),
            "is_ready": True
        }

    def __str__(self) -> str:
        return f"{self.name}Agent(tools={len(self.tools)}, state_keys={len(self.state)})"

    def __repr__(self) -> str:
        return self.__str__()