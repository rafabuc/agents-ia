

# workflows/project_workflow.py
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from langgraph.graph import Graph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain.schema import BaseMessage, HumanMessage, AIMessage

from agents.pmp_project_agent import PMPProjectAgent
#from agents.cost_budget_agent import CostBudgetAgent
#from agents.template_agent import TemplateAgent
from storage.database_manager import DatabaseManager
from utils.logger import logger


class ProjectWorkflow:
    """Orchestrates multi-agent workflows for project management."""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.agents = {
            "pmp_project": PMPProjectAgent(),
            #"cost_budget": CostBudgetAgent(),
            #"template": TemplateAgent()
        }
        
        # Initialize agents
        for agent in self.agents.values():
            agent.initialize()
        
        self.workflow_graph = self._create_workflow_graph()
        logger.info("ProjectWorkflow initialized")
    
    def _create_workflow_graph(self) -> Graph:
        """Create the LangGraph workflow."""
        
        def route_to_agent(state: Dict) -> str:
            """Route to appropriate agent based on request."""
            request_type = state.get("request_type", "general")
            
            if request_type in ["create_project", "project_charter", "wbs", "schedule"]:
                return "pmp_project_node"
            elif request_type in ["cost_estimate", "budget", "cost_analysis"]:
                return "cost_budget_node"
            elif request_type in ["fill_template", "generate_document"]:
                return "template_node"
            else:
                return "pmp_project_node"  # Default
        
        def pmp_project_node(state: Dict) -> Dict:
            """Handle PMP project requests."""
            try:
                input_text = state.get("input", "")
                session_id = state.get("session_id")
                
                result = self.agents["pmp_project"].process(input_text, session_id)
                
                state["messages"].append(AIMessage(content=result["response"]))
                state["last_agent"] = "pmp_project"
                state["results"] = state.get("results", []) + [result]
                
                return state
                
            except Exception as e:
                logger.error(f"Error in PMP project node: {str(e)}")
                state["messages"].append(AIMessage(content=f"Error: {str(e)}"))
                return state
        
        def cost_budget_node(state: Dict) -> Dict:
            """Handle cost/budget requests."""
            try:
                input_text = state.get("input", "")
                session_id = state.get("session_id")
                
                result = self.agents["cost_budget"].process(input_text, session_id)
                
                state["messages"].append(AIMessage(content=result["response"]))
                state["last_agent"] = "cost_budget"
                state["results"] = state.get("results", []) + [result]
                
                return state
                
            except Exception as e:
                logger.error(f"Error in cost budget node: {str(e)}")
                state["messages"].append(AIMessage(content=f"Error: {str(e)}"))
                return state
        
        def template_node(state: Dict) -> Dict:
            """Handle template requests."""
            try:
                input_text = state.get("input", "")
                session_id = state.get("session_id")
                
                result = self.agents["template"].process(input_text, session_id)
                
                state["messages"].append(AIMessage(content=result["response"]))
                state["last_agent"] = "template"
                state["results"] = state.get("results", []) + [result]
                
                return state
                
            except Exception as e:
                logger.error(f"Error in template node: {str(e)}")
                state["messages"].append(AIMessage(content=f"Error: {str(e)}"))
                return state
        
        def should_continue(state: Dict) -> str:
            """Determine if workflow should continue."""
            # Check if there are follow-up requests
            if state.get("continue_workflow", False):
                return "router"
            else:
                return END
        
        # Build the graph
        workflow = Graph()
        
        # Add nodes
        workflow.add_node("router", route_to_agent)
        workflow.add_node("pmp_project_node", pmp_project_node)
        workflow.add_node("cost_budget_node", cost_budget_node)
        workflow.add_node("template_node", template_node)
        
        # Add edges
        workflow.add_edge(START, "router")
        workflow.add_conditional_edges(
            "router",
            route_to_agent,
            {
                "pmp_project_node": "pmp_project_node",
                "cost_budget_node": "cost_budget_node",
                "template_node": "template_node"
            }
        )
        
        # Add continuation logic
        workflow.add_conditional_edges(
            "pmp_project_node",
            should_continue,
            {
                "router": "router",
                END: END
            }
        )
        workflow.add_conditional_edges(
            "cost_budget_node", 
            should_continue,
            {
                "router": "router",
                END: END
            }
        )
        workflow.add_conditional_edges(
            "template_node",
            should_continue,
            {
                "router": "router", 
                END: END
            }
        )
        
        return workflow.compile()
    
    async def execute_workflow(self, input_text: str, request_type: str = "general",
                              project_id: Optional[int] = None, 
                              session_id: Optional[int] = None) -> Dict[str, Any]:
        """Execute a workflow with the given input."""
        
        try:
            # Create session if needed
            if not session_id and project_id:
                chat_session = self.db_manager.create_chat_session(
                    project_id=project_id,
                    agent_type="workflow"
                )
                session_id = chat_session.id
            
            # Initial state
            initial_state = {
                "input": input_text,
                "request_type": request_type,
                "project_id": project_id,
                "session_id": session_id,
                "messages": [HumanMessage(content=input_text)],
                "results": [],
                "continue_workflow": False
            }
            
            # Execute workflow
            final_state = await self.workflow_graph.ainvoke(initial_state)
            
            # Extract results
            results = final_state.get("results", [])
            last_agent = final_state.get("last_agent", "unknown")
            
            # Get final response
            final_response = ""
            if results:
                final_response = results[-1].get("response", "No response generated")
            
            logger.info(f"Workflow executed successfully with {len(results)} agent interactions")
            
            return {
                "success": True,
                "response": final_response,
                "agent_results": results,
                "last_agent": last_agent,
                "session_id": session_id,
                "project_id": project_id,
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "executed_at": datetime.utcnow().isoformat()
            }
    
    def create_project_workflow(self, project_data: Dict[str, Any], 
                               session_id: Optional[int] = None) -> Dict[str, Any]:
        """Complete workflow for creating a new project."""
        
        try:
            results = []
            
            # Step 1: Create project structure
            pmp_result = self.agents["pmp_project"].process(
                f"Create a new project with this data: {json.dumps(project_data)}",
                session_id
            )
            results.append(pmp_result)
            
            project_id = self._extract_project_id(pmp_result)
            
            if project_id:
                # Step 2: Create initial cost estimate
                cost_result = self.agents["cost_budget"].process(
                    f"Create a preliminary cost estimate for project {project_id} based on the project scope",
                    session_id
                )
                results.append(cost_result)
                
                # Step 3: Generate project charter template
                template_result = self.agents["template"].process(
                    f"Fill the project charter template for project {project_id} with available data",
                    session_id
                )
                results.append(template_result)
            
            return {
                "success": True,
                "project_id": project_id,
                "results": results,
                "message": "Project creation workflow completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error in project creation workflow: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": results
            }
    
    def cost_analysis_workflow(self, project_id: int, analysis_type: str = "comprehensive",
                              session_id: Optional[int] = None) -> Dict[str, Any]:
        """Workflow for comprehensive cost analysis."""
        
        try:
            results = []
            
            # Step 1: Get project information
            project_info_result = self.agents["pmp_project"].process(
                f"Get detailed information for project {project_id}",
                session_id
            )
            results.append(project_info_result)
            
            # Step 2: Create detailed cost estimate
            estimate_result = self.agents["cost_budget"].process(
                f"Create a detailed {analysis_type} cost estimate for project {project_id}",
                session_id
            )
            results.append(estimate_result)
            
            # Step 3: Create budget document
            budget_result = self.agents["cost_budget"].process(
                f"Create a comprehensive budget document for project {project_id}",
                session_id
            )
            results.append(budget_result)
            
            # Step 4: Generate cost baseline
            baseline_result = self.agents["cost_budget"].process(
                f"Create cost performance baseline for project {project_id}",
                session_id
            )
            results.append(baseline_result)
            
            return {
                "success": True,
                "project_id": project_id,
                "results": results,
                "message": f"Cost analysis workflow ({analysis_type}) completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error in cost analysis workflow: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "results": results
            }
    
    def _extract_project_id(self, agent_result: Dict[str, Any]) -> Optional[int]:
        """Extract project ID from agent result."""
        try:
            response = agent_result.get("response", "")
            # Simple regex to find project ID
            import re
            match = re.search(r'ID (\d+)', response)
            if match:
                return int(match.group(1))
            return None
        except Exception:
            return None

