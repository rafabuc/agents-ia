"""
Evaluator Agent - CEFR Level Assessment
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
from langsmith import traceable
import json
import logging

from config import settings

logger = logging.getLogger(__name__)


class EvaluatorState(TypedDict):
    """State for evaluator agent."""
    messages: List[dict]
    student_level: Optional[str]
    strengths: List[str]
    weaknesses: List[str]
    conversation_history: List[dict]
    question_count: int


EVALUATOR_SYSTEM_PROMPT = """You are an expert English language evaluator following the CEFR framework (A1, A2, B1, B2, C1, C2).

Your task is to assess the student's English level through a natural conversation. Evaluate:
- Vocabulary range and accuracy
- Grammar complexity and correctness
- Fluency and coherence
- Comprehension abilities

Ask 5-7 progressively challenging questions. Start simple, then adapt based on responses.

For each response, analyze and provide:
1. Assessment of current answer quality
2. Detected level indicators
3. Next question (or null if evaluation complete)

Be encouraging and supportive while being accurate in your assessment."""


class EvaluatorAgent:
    """Agent for evaluating student's English level."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.DEFAULT_GPT_MODEL,
            temperature=0.3
        )
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Create LangGraph workflow."""
        workflow = StateGraph(EvaluatorState)
        
        # Add nodes
        workflow.add_node("ask_question", self.ask_question)
        workflow.add_node("analyze_response", self.analyze_response)
        workflow.add_node("determine_level", self.determine_level)
        
        # Set entry point
        workflow.set_entry_point("ask_question")
        
        # Add edges
        workflow.add_edge("ask_question", "analyze_response")
        workflow.add_conditional_edges(
            "analyze_response",
            self.should_continue,
            {
                "continue": "ask_question",
                "finish": "determine_level"
            }
        )
        workflow.add_edge("determine_level", END)
        
        return workflow.compile()
    
    @traceable(name="evaluator_ask_question")
    async def ask_question(self, state: EvaluatorState) -> dict:
        """Generate next evaluation question."""
        question_num = state.get("question_count", 0) + 1
        
        prompt = f"""Generate evaluation question #{question_num}.

Previous conversation:
{json.dumps(state.get('conversation_history', []), indent=2)}

Create a question that:
1. Assesses the student's level appropriately
2. Is engaging and natural
3. Tests specific language skills

Return JSON:
{{
    "question": "Your question here",
    "skill_tested": "vocabulary|grammar|comprehension",
    "expected_level": "A1|A2|B1|B2|C1|C2"
}}"""
        
        response = await self.llm.ainvoke([
            SystemMessage(content=EVALUATOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        try:
            question_data = json.loads(response.content)
            return {
                "messages": state["messages"] + [{"role": "assistant", "content": question_data["question"]}],
                "question_count": question_num
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "messages": state["messages"] + [{"role": "assistant", "content": response.content}],
                "question_count": question_num
            }
    
    @traceable(name="evaluator_analyze_response")
    async def analyze_response(self, state: EvaluatorState) -> dict:
        """Analyze student's response."""
        last_message = state["messages"][-1] if state["messages"] else {}
        
        prompt = f"""Analyze this student response:

Student answer: "{last_message.get('content', '')}"
Question number: {state['question_count']}

Provide detailed analysis in JSON:
{{
    "level_indicators": ["indicator1", "indicator2"],
    "vocabulary_quality": {{
        "range": "basic|intermediate|advanced",
        "accuracy": 0.0-1.0
    }},
    "grammar_quality": {{
        "complexity": "simple|compound|complex",
        "accuracy": 0.0-1.0
    }},
    "estimated_level": "A1|A2|B1|B2|C1|C2",
    "confidence": 0.0-1.0,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"]
}}"""
        
        response = await self.llm.ainvoke([
            SystemMessage(content=EVALUATOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        try:
            analysis = json.loads(response.content)
            
            conversation_entry = {
                "question_num": state["question_count"],
                "student_response": last_message.get('content', ''),
                "analysis": analysis
            }
            
            return {
                "conversation_history": state.get("conversation_history", []) + [conversation_entry],
                "strengths": list(set(state.get("strengths", []) + analysis.get("strengths", []))),
                "weaknesses": list(set(state.get("weaknesses", []) + analysis.get("weaknesses", [])))
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse analysis: {e}")
            return state
    
    def should_continue(self, state: EvaluatorState) -> str:
        """Determine if evaluation should continue."""
        question_count = state.get("question_count", 0)
        
        # Continue if less than 7 questions
        if question_count < 7:
            # Check if we have enough confidence
            if len(state.get("conversation_history", [])) >= 5:
                # Check consistency in last 3 assessments
                recent = state["conversation_history"][-3:]
                levels = [h["analysis"].get("estimated_level") for h in recent]
                
                # If consistent level detected, finish early
                if len(set(levels)) == 1:
                    return "finish"
            
            return "continue"
        
        return "finish"
    
    @traceable(name="evaluator_determine_level")
    async def determine_level(self, state: EvaluatorState) -> dict:
        """Determine final CEFR level."""
        
        prompt = f"""Based on this complete evaluation, determine the final CEFR level.

Conversation history:
{json.dumps(state.get('conversation_history', []), indent=2)}

Provide final assessment in JSON:
{{
    "cefr_level": "A1|A2|B1|B2|C1|C2",
    "confidence": 0.0-1.0,
    "detailed_breakdown": {{
        "vocabulary": "A1|A2|B1|B2|C1|C2",
        "grammar": "A1|A2|B1|B2|C1|C2",
        "fluency": "A1|A2|B1|B2|C1|C2",
        "comprehension": "A1|A2|B1|B2|C1|C2"
    }},
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2"],
    "recommendations": ["recommendation1", "recommendation2", "recommendation3"]
}}"""
        
        response = await self.llm.ainvoke([
            SystemMessage(content=EVALUATOR_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ])
        
        try:
            final_assessment = json.loads(response.content)
            
            return {
                "student_level": final_assessment["cefr_level"],
                "strengths": final_assessment.get("strengths", []),
                "weaknesses": final_assessment.get("weaknesses", []),
                "final_assessment": final_assessment
            }
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse final assessment: {e}")
            return {
                "student_level": "B1",  # Default fallback
                "final_assessment": {"error": str(e)}
            }
    
    async def run(self, user_id: int, initial_message: str = None) -> dict:
        """Run evaluation for a user."""
        initial_state = {
            "messages": [],
            "student_level": None,
            "strengths": [],
            "weaknesses": [],
            "conversation_history": [],
            "question_count": 0
        }
        
        if initial_message:
            initial_state["messages"] = [{"role": "user", "content": initial_message}]
        
        result = await self.graph.ainvoke(initial_state)
        
        logger.info(f"Evaluation completed for user {user_id}: {result.get('student_level')}")
        
        return result
