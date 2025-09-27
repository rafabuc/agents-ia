"""
Supervisor Agent - Multi-Agent Orchestration with LangGraph
"""
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Literal, Optional
from langsmith import traceable
import json
import logging

from config import settings
from agents.evaluator import EvaluatorAgent
from agents.tutor import TutorAgent
from agents.grammar import GrammarCheckerAgent
from agents.conversation import ConversationPartnerAgent
from agents.exercise import ExerciseGeneratorAgent
from agents.progress import ProgressTrackerAgent

logger = logging.getLogger(__name__)


class SupervisorState(TypedDict):
    """State for supervisor workflow."""
    user_message: str
    user_context: dict
    current_agent: str
    agent_responses: dict
    final_response: str
    next_action: str


class SupervisorAgent:
    """Supervisor for multi-agent orchestration."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model=settings.DEFAULT_GPT_MODEL, temperature=0)
        
        # Initialize agents
        self.agents = {
            "evaluator": EvaluatorAgent(),
            "tutor": TutorAgent(),
            "grammar": GrammarCheckerAgent(),
            "conversation": ConversationPartnerAgent(),
            "exercise": ExerciseGeneratorAgent(),
            "progress": ProgressTrackerAgent()
        }
        
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create supervisor workflow graph."""
        
        workflow = StateGraph(SupervisorState)
        
        # Add nodes
        workflow.add_node("analyze_request", self.analyze_request)
        workflow.add_node("route_to_agent", self.route_to_agent)
        workflow.add_node("execute_agent", self.execute_agent)
        workflow.add_node("synthesize_response", self.synthesize_response)
        
        # Set entry point
        workflow.set_entry_point("analyze_request")
        
        # Add edges
        workflow.add_edge("analyze_request", "route_to_agent")
        workflow.add_edge("route_to_agent", "execute_agent")
        
        # Conditional: check if need more agents
        workflow.add_conditional_edges(
            "execute_agent",
            self.should_continue,
            {
                "continue": "route_to_agent",
                "synthesize": "synthesize_response"
            }
        )
        
        workflow.add_edge("synthesize_response", END)
        
        return workflow.compile()
    
    @traceable(name="supervisor_analyze_request")
    async def analyze_request(self, state: SupervisorState) -> dict:
        """Analyze user request to understand intent."""
        
        analysis_prompt = f"""Analyze this user request and determine the intent.

User message: "{state['user_message']}"
User context: {json.dumps(state['user_context'], indent=2)}

Classify the intent:
- evaluation: User wants level assessment
- lesson: User wants to learn something
- grammar_check: User wants grammar correction
- conversation: User wants to practice speaking/chatting
- exercise: User wants practice exercises
- progress: User wants to see their progress

Return JSON:
{{
    "intent": "primary intent",
    "sub_intents": ["additional intents"],
    "confidence": 0.0-1.0,
    "reasoning": "why this classification"
}}"""
        
        try:
            response = await self.llm.ainvoke(analysis_prompt)
            analysis = json.loads(response.content)
            
            logger.info(f"Request analysis: {analysis['intent']} (confidence: {analysis['confidence']})")
            
            return {
                "agent_responses": {
                    "analysis": analysis
                }
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis: {e}")
            return {
                "agent_responses": {
                    "analysis": {"intent": "conversation", "confidence": 0.5}
                }
            }
    
    @traceable(name="supervisor_route")
    async def route_to_agent(self, state: SupervisorState) -> dict:
        """Route to appropriate agent based on analysis."""
        
        analysis = state["agent_responses"].get("analysis", {})
        intent = analysis.get("intent", "conversation")
        
        # Map intent to agent
        agent_mapping = {
            "evaluation": "evaluator",
            "lesson": "tutor",
            "grammar_check": "grammar",
            "conversation": "conversation",
            "exercise": "exercise",
            "progress": "progress"
        }
        
        current_agent = agent_mapping.get(intent, "conversation")
        
        logger.info(f"Routing to agent: {current_agent}")
        
        return {
            "current_agent": current_agent,
            "next_action": "execute"
        }
    
    @traceable(name="supervisor_execute")
    async def execute_agent(self, state: SupervisorState) -> dict:
        """Execute current agent."""
        
        agent_name = state["current_agent"]
        user_message = state["user_message"]
        user_context = state["user_context"]
        
        logger.info(f"Executing agent: {agent_name}")
        
        try:
            agent = self.agents[agent_name]
            
            # Execute agent based on type
            if agent_name == "evaluator":
                result = await agent.run(
                    user_id=user_context.get("user_id", 1),
                    initial_message=user_message
                )
            
            elif agent_name == "tutor":
                # Determine what to teach
                if "explain" in user_message.lower():
                    concept = self._extract_concept(user_message)
                    result = agent.explain_grammar(
                        concept=concept,
                        level=user_context.get("level", "B1")
                    )
                else:
                    topic = self._extract_topic(user_message)
                    result = agent.create_lesson(
                        topic=topic,
                        level=user_context.get("level", "B1")
                    )
            
            elif agent_name == "grammar":
                result = await agent.check_grammar(
                    text=user_message,
                    student_level=user_context.get("level", "B1")
                )
            
            elif agent_name == "conversation":
                result = await agent.chat(
                    user_message=user_message,
                    context=user_context
                )
            
            elif agent_name == "exercise":
                topic = self._extract_topic(user_message)
                result = await agent.generate_exercise_set(
                    topic=topic,
                    level=user_context.get("level", "B1"),
                    exercise_types=["multiple_choice", "fill_in_blank"],
                    quantity=5
                )
            
            elif agent_name == "progress":
                result = await agent.generate_progress_report(
                    user_id=user_context.get("user_id", 1),
                    period_days=30
                )
            
            else:
                result = {"error": f"Unknown agent: {agent_name}"}
            
            # Update responses
            agent_responses = state.get("agent_responses", {})
            agent_responses[agent_name] = result
            
            return {
                "agent_responses": agent_responses,
                "next_action": "synthesize"
            }
            
        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            return {
                "agent_responses": {
                    **state.get("agent_responses", {}),
                    agent_name: {"error": str(e)}
                },
                "next_action": "synthesize"
            }
    
    def should_continue(self, state: SupervisorState) -> str:
        """Determine if should continue routing or synthesize."""
        
        # For now, go straight to synthesis
        # Future: check if multiple agents needed
        return "synthesize"
    
    @traceable(name="supervisor_synthesize")
    async def synthesize_response(self, state: SupervisorState) -> dict:
        """Synthesize final response from agent outputs."""
        
        agent_responses = state.get("agent_responses", {})
        user_context = state.get("user_context", {})
        
        # Remove analysis from synthesis
        synthesis_responses = {
            k: v for k, v in agent_responses.items() 
            if k != "analysis"
        }
        
        synthesis_prompt = f"""Synthesize agent responses into a natural, helpful user reply.

Agent responses:
{json.dumps(synthesis_responses, indent=2)}

User context:
{json.dumps(user_context, indent=2)}

Create a response that:
1. Directly addresses the user's question
2. Integrates information from agent(s)
3. Is encouraging and supportive
4. Suggests relevant next steps
5. Is written in natural, conversational language

Return only the final response text, no JSON."""
        
        try:
            response = await self.llm.ainvoke(synthesis_prompt)
            final_response = response.content.strip()
            
            logger.info("Response synthesized successfully")
            
            return {
                "final_response": final_response
            }
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            
            # Fallback: use first agent response
            first_response = next(iter(synthesis_responses.values()), {})
            return {
                "final_response": str(first_response)
            }
    
    def _extract_topic(self, message: str) -> str:
        """Extract topic from message."""
        # Simple extraction - can be improved with NER
        words = message.lower().split()
        
        # Common topic keywords
        topics = [
            "grammar", "vocabulary", "speaking", "writing",
            "present", "past", "future", "tense",
            "verb", "noun", "adjective", "adverb"
        ]
        
        for word in words:
            if word in topics:
                return word
        
        return "general English"
    
    def _extract_concept(self, message: str) -> str:
        """Extract concept to explain."""
        # Simple extraction
        if "present perfect" in message.lower():
            return "Present Perfect"
        elif "past simple" in message.lower():
            return "Past Simple"
        elif "conditional" in message.lower():
            return "Conditionals"
        else:
            return self._extract_topic(message)
    
    async def run(self, user_message: str, user_context: dict) -> dict:
        """Run supervisor workflow."""
        
        initial_state = {
            "user_message": user_message,
            "user_context": user_context,
            "current_agent": "",
            "agent_responses": {},
            "final_response": "",
            "next_action": ""
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        return {
            "response": result.get("final_response"),
            "agent_used": result.get("current_agent"),
            "raw_outputs": result.get("agent_responses")
        }


# Singleton instance
_supervisor = None

def get_supervisor() -> SupervisorAgent:
    """Get or create supervisor instance."""
    global _supervisor
    if _supervisor is None:
        _supervisor = SupervisorAgent()
    return _supervisor
