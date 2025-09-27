"""
Main Graph - Complete Agent Orchestration Workflow
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from langsmith import traceable
import logging

from agents.evaluator import EvaluatorAgent
from agents.tutor import TutorAgent
from agents.grammar import GrammarCheckerAgent
from agents.conversation import ConversationPartnerAgent
from agents.exercise import ExerciseGeneratorAgent
from agents.progress import ProgressTrackerAgent
from graphs.supervisor import SupervisorAgent

logger = logging.getLogger(__name__)


class MainWorkflowState(TypedDict):
    """Main workflow state."""
    user_id: int
    session_id: Optional[str]
    user_message: str
    user_level: Optional[str]
    conversation_history: List[dict]
    current_phase: str
    responses: dict
    final_output: str


class MainWorkflow:
    """Main orchestration workflow for complete learning journey."""
    
    def __init__(self):
        self.evaluator = EvaluatorAgent()
        self.tutor = TutorAgent()
        self.grammar = GrammarCheckerAgent()
        self.conversation = ConversationPartnerAgent()
        self.exercise = ExerciseGeneratorAgent()
        self.progress = ProgressTrackerAgent()
        self.supervisor = SupervisorAgent()
        
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create main workflow graph."""
        
        workflow = StateGraph(MainWorkflowState)
        
        # Add nodes
        workflow.add_node("check_user_level", self.check_user_level)
        workflow.add_node("evaluate_user", self.evaluate_user)
        workflow.add_node("process_request", self.process_request)
        workflow.add_node("track_session", self.track_session)
        
        # Set entry point
        workflow.set_entry_point("check_user_level")
        
        # Conditional edges
        workflow.add_conditional_edges(
            "check_user_level",
            self.needs_evaluation,
            {
                "evaluate": "evaluate_user",
                "process": "process_request"
            }
        )
        
        workflow.add_edge("evaluate_user", "process_request")
        workflow.add_edge("process_request", "track_session")
        workflow.add_edge("track_session", END)
        
        return workflow.compile()
    
    @traceable(name="main_check_level")
    async def check_user_level(self, state: MainWorkflowState) -> dict:
        """Check if user has a level assigned."""
        
        user_level = state.get("user_level")
        
        logger.info(f"Checking level for user {state['user_id']}: {user_level}")
        
        return {
            "current_phase": "evaluation" if not user_level else "processing"
        }
    
    def needs_evaluation(self, state: MainWorkflowState) -> str:
        """Determine if user needs evaluation."""
        return "evaluate" if state["current_phase"] == "evaluation" else "process"
    
    @traceable(name="main_evaluate")
    async def evaluate_user(self, state: MainWorkflowState) -> dict:
        """Evaluate user level if needed."""
        
        logger.info(f"Evaluating user {state['user_id']}")
        
        result = await self.evaluator.run(
            user_id=state["user_id"],
            initial_message=state["user_message"]
        )
        
        user_level = result.get("student_level", "B1")
        
        # TODO: Update user level in database
        
        return {
            "user_level": user_level,
            "responses": {
                "evaluation": result
            },
            "current_phase": "processing"
        }
    
    @traceable(name="main_process")
    async def process_request(self, state: MainWorkflowState) -> dict:
        """Process user request with supervisor."""
        
        logger.info(f"Processing request for user {state['user_id']}")
        
        user_context = {
            "user_id": state["user_id"],
            "level": state.get("user_level", "B1"),
            "conversation_history": state.get("conversation_history", [])
        }
        
        result = await self.supervisor.run(
            user_message=state["user_message"],
            user_context=user_context
        )
        
        responses = state.get("responses", {})
        responses["supervisor"] = result
        
        return {
            "responses": responses,
            "final_output": result.get("response", ""),
            "current_phase": "tracking"
        }
    
    @traceable(name="main_track")
    async def track_session(self, state: MainWorkflowState) -> dict:
        """Track session for progress monitoring."""
        
        logger.info(f"Tracking session for user {state['user_id']}")
        
        session_data = {
            "user_id": state["user_id"],
            "session_id": state.get("session_id"),
            "activity": "conversation",
            "timestamp": None,  # Will be set by tracker
            "responses": state.get("responses", {})
        }
        
        await self.progress.track_session(session_data)
        
        return {
            "current_phase": "complete"
        }
    
    async def run(
        self,
        user_id: int,
        user_message: str,
        user_level: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> dict:
        """Run complete workflow."""
        
        initial_state = {
            "user_id": user_id,
            "session_id": session_id,
            "user_message": user_message,
            "user_level": user_level,
            "conversation_history": [],
            "current_phase": "init",
            "responses": {},
            "final_output": ""
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        return {
            "user_id": user_id,
            "level": result.get("user_level"),
            "response": result.get("final_output"),
            "phase": result.get("current_phase"),
            "details": result.get("responses", {})
        }


# Singleton instance
_main_workflow = None

def get_main_workflow() -> MainWorkflow:
    """Get or create main workflow instance."""
    global _main_workflow
    if _main_workflow is None:
        _main_workflow = MainWorkflow()
    return _main_workflow
