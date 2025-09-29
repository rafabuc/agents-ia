"""
LangGraph Orchestrator for DevOps Multi-Agent Workflows
"""

from typing import Dict, Any, List, Optional, Callable
import logging
from langgraph import StateGraph, END
from langchain_core.language_models import BaseLanguageModel

from .state import DevOpsState, StateManager
from ..agents import BaseAgent, CICDAgent, InfrastructureAgent, SecurityAgent, TestingAgent


class DevOpsWorkflowGraph:
    """
    Main orchestrator for DevOps workflows using LangGraph.
    Coordinates multiple specialized agents to execute complex DevOps tasks.
    """

    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.logger = logging.getLogger("devops_orchestrator")
        self.agents: Dict[str, BaseAgent] = {}
        self.graph: Optional[StateGraph] = None

        # Initialize agents
        self._initialize_agents()

        # Build workflow graph
        self._build_graph()

    def _initialize_agents(self):
        """Initialize all DevOps agents"""
        try:
            self.agents = {
                "cicd": CICDAgent(self.llm, verbose=False),
                "infrastructure": InfrastructureAgent(self.llm, verbose=False),
                "security": SecurityAgent(self.llm, verbose=False),
                "testing": TestingAgent(self.llm, verbose=False),
            }
            self.logger.info(f"Initialized {len(self.agents)} agents")
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {str(e)}")
            raise

    def _build_graph(self):
        """Build the LangGraph workflow"""
        try:
            # Create workflow graph
            workflow = StateGraph(DevOpsState)

            # Add workflow entry point
            workflow.add_node("start", self._start_workflow)

            # Add agent nodes
            workflow.add_node("cicd_agent", self._execute_cicd_agent)
            workflow.add_node("infrastructure_agent", self._execute_infrastructure_agent)
            workflow.add_node("security_agent", self._execute_security_agent)
            workflow.add_node("testing_agent", self._execute_testing_agent)

            # Add decision and coordination nodes
            workflow.add_node("route_request", self._route_request)
            workflow.add_node("validate_results", self._validate_results)
            workflow.add_node("handle_errors", self._handle_errors)
            workflow.add_node("finalize", self._finalize_workflow)

            # Define workflow edges
            self._add_workflow_edges(workflow)

            # Set entry point
            workflow.set_entry_point("start")

            # Compile graph
            self.graph = workflow.compile()
            self.logger.info("DevOps workflow graph compiled successfully")

        except Exception as e:
            self.logger.error(f"Failed to build workflow graph: {str(e)}")
            raise

    def _add_workflow_edges(self, workflow: StateGraph):
        """Add edges to define workflow routing"""
        # Start workflow routing
        workflow.add_edge("start", "route_request")

        # Route to appropriate agents
        workflow.add_conditional_edges(
            "route_request",
            self._determine_agent_routing,
            {
                "cicd": "cicd_agent",
                "infrastructure": "infrastructure_agent",
                "security": "security_agent",
                "testing": "testing_agent",
                "multi_agent": "cicd_agent",  # Start with CI/CD if multiple needed
                "error": "handle_errors"
            }
        )

        # CI/CD agent routing
        workflow.add_conditional_edges(
            "cicd_agent",
            self._check_cicd_completion,
            {
                "continue_infrastructure": "infrastructure_agent",
                "validate": "validate_results",
                "error": "handle_errors"
            }
        )

        # Infrastructure agent routing
        workflow.add_conditional_edges(
            "infrastructure_agent",
            self._check_infrastructure_completion,
            {
                "validate": "validate_results",
                "error": "handle_errors"
            }
        )

        # Validation routing
        workflow.add_conditional_edges(
            "validate_results",
            self._check_validation,
            {
                "success": "finalize",
                "retry_cicd": "cicd_agent",
                "retry_infrastructure": "infrastructure_agent",
                "error": "handle_errors"
            }
        )

        # Error handling
        workflow.add_conditional_edges(
            "handle_errors",
            self._check_error_recovery,
            {
                "retry": "route_request",
                "finalize": "finalize"
            }
        )

        # Final state
        workflow.add_edge("finalize", END)

    async def execute_workflow(
        self,
        workflow_type: str,
        user_request: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a DevOps workflow"""
        try:
            # Create initial state
            initial_state = StateManager.create_initial_state(
                workflow_type=workflow_type,
                user_request=user_request,
                context=context or {}
            )

            self.logger.info(f"Starting workflow: {initial_state['workflow_id']}")

            # Execute workflow
            if not self.graph:
                raise Exception("Workflow graph not initialized")

            final_state = await self.graph.ainvoke(initial_state)

            # Return results
            return {
                "success": final_state["status"] == "completed",
                "workflow_id": final_state["workflow_id"],
                "results": final_state["workflow_results"],
                "summary": StateManager.get_summary(final_state),
                "state": final_state
            }

        except Exception as e:
            self.logger.error(f"Workflow execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": initial_state.get("workflow_id", "unknown")
            }

    # Node implementations

    async def _start_workflow(self, state: DevOpsState) -> DevOpsState:
        """Initialize workflow execution"""
        self.logger.info(f"Starting workflow: {state['workflow_type']}")

        state = StateManager.update_agent_status(state, "orchestrator", "started")
        state["status"] = "running"

        return state

    async def _execute_cicd_agent(self, state: DevOpsState) -> DevOpsState:
        """Execute CI/CD agent"""
        try:
            self.logger.info("Executing CI/CD agent")

            state = StateManager.update_agent_status(state, "cicd", "started")

            # Determine CI/CD task based on workflow type and context
            cicd_task = self._determine_cicd_task(state)

            # Execute CI/CD agent
            cicd_agent = self.agents["cicd"]
            result = await cicd_agent.execute(cicd_task, state["context"])

            if result["success"]:
                state = StateManager.update_agent_status(
                    state, "cicd", "completed", result
                )
                # Update pipeline status based on task
                if "build" in cicd_task.lower():
                    state = StateManager.update_pipeline_status(
                        state, "built", result.get("build_info")
                    )
                elif "deploy" in cicd_task.lower():
                    state = StateManager.update_pipeline_status(
                        state, "deployed", None, result.get("deployment_info")
                    )
            else:
                state = StateManager.update_agent_status(
                    state, "cicd", "failed", result
                )
                state = StateManager.add_error(
                    state, "cicd", result.get("error", "CI/CD execution failed")
                )

        except Exception as e:
            self.logger.error(f"CI/CD agent execution failed: {str(e)}")
            state = StateManager.add_error(state, "cicd", str(e))
            state = StateManager.update_agent_status(state, "cicd", "failed")

        return state

    async def _execute_infrastructure_agent(self, state: DevOpsState) -> DevOpsState:
        """Execute Infrastructure agent"""
        try:
            self.logger.info("Executing Infrastructure agent")

            state = StateManager.update_agent_status(state, "infrastructure", "started")

            # Determine infrastructure task
            infra_task = self._determine_infrastructure_task(state)

            # Execute Infrastructure agent
            infra_agent = self.agents["infrastructure"]
            result = await infra_agent.execute(infra_task, state["context"])

            if result["success"]:
                state = StateManager.update_agent_status(
                    state, "infrastructure", "completed", result
                )
                # Add infrastructure changes to state
                if result.get("infrastructure_changes"):
                    for change in result["infrastructure_changes"]:
                        state = StateManager.add_infrastructure_change(
                            state,
                            change.get("type", "unknown"),
                            change.get("resource", "unknown"),
                            change.get("action", "unknown"),
                            change.get("details", {})
                        )
            else:
                state = StateManager.update_agent_status(
                    state, "infrastructure", "failed", result
                )
                state = StateManager.add_error(
                    state, "infrastructure", result.get("error", "Infrastructure execution failed")
                )

        except Exception as e:
            self.logger.error(f"Infrastructure agent execution failed: {str(e)}")
            state = StateManager.add_error(state, "infrastructure", str(e))
            state = StateManager.update_agent_status(state, "infrastructure", "failed")

        return state

    async def _route_request(self, state: DevOpsState) -> DevOpsState:
        """Route request to appropriate agents"""
        workflow_type = state["workflow_type"]
        user_request = state["user_request"].lower()

        # Analyze request to determine routing
        needs_cicd = any(keyword in user_request for keyword in [
            "build", "deploy", "pipeline", "ci/cd", "release"
        ])

        needs_infrastructure = any(keyword in user_request for keyword in [
            "infrastructure", "terraform", "kubernetes", "cluster", "provision", "scale"
        ])

        needs_security = any(keyword in user_request for keyword in [
            "security", "vulnerability", "compliance", "audit", "scan", "secret"
        ])

        needs_testing = any(keyword in user_request for keyword in [
            "test", "coverage", "quality", "performance", "load"
        ])

        # Count needs
        needs_count = sum([needs_cicd, needs_infrastructure, needs_security, needs_testing])

        # Set routing strategy
        if needs_count > 1:
            state["context"]["routing"] = "multi_agent"
            state["context"]["required_agents"] = []
            if needs_cicd:
                state["context"]["required_agents"].append("cicd")
            if needs_infrastructure:
                state["context"]["required_agents"].append("infrastructure")
            if needs_security:
                state["context"]["required_agents"].append("security")
            if needs_testing:
                state["context"]["required_agents"].append("testing")
        elif needs_security:
            state["context"]["routing"] = "security"
        elif needs_testing:
            state["context"]["routing"] = "testing"
        elif needs_cicd:
            state["context"]["routing"] = "cicd"
        elif needs_infrastructure:
            state["context"]["routing"] = "infrastructure"
        else:
            # Default routing based on workflow type
            if workflow_type == "deployment":
                state["context"]["routing"] = "multi_agent"
                state["context"]["required_agents"] = ["cicd", "infrastructure", "security"]
            elif workflow_type == "security":
                state["context"]["routing"] = "security"
            elif workflow_type == "testing":
                state["context"]["routing"] = "testing"
            elif workflow_type == "infrastructure":
                state["context"]["routing"] = "infrastructure"
            else:
                state["context"]["routing"] = "cicd"

        self.logger.info(f"Request routed to: {state['context']['routing']}")
        return state

    async def _validate_results(self, state: DevOpsState) -> DevOpsState:
        """Validate workflow results"""
        try:
            self.logger.info("Validating workflow results")

            # Check if all required agents completed successfully
            required_agents = self._get_required_agents(state)
            completed_agents = set(state["completed_agents"])
            failed_agents = set(state["failed_agents"])

            validation_success = True
            validation_errors = []

            # Check agent completion
            for agent in required_agents:
                if agent in failed_agents:
                    validation_success = False
                    validation_errors.append(f"Agent {agent} failed")
                elif agent not in completed_agents:
                    validation_success = False
                    validation_errors.append(f"Agent {agent} not completed")

            # Additional validations based on workflow type
            if state["workflow_type"] == "deployment":
                if not state.get("pipeline_status") or state["pipeline_status"] not in ["deployed", "completed"]:
                    validation_success = False
                    validation_errors.append("Deployment not completed")

            # Update state with validation results
            state["context"]["validation"] = {
                "success": validation_success,
                "errors": validation_errors,
                "completed_agents": list(completed_agents),
                "failed_agents": list(failed_agents)
            }

            if validation_success:
                self.logger.info("Workflow validation successful")
            else:
                self.logger.warning(f"Workflow validation failed: {validation_errors}")

        except Exception as e:
            self.logger.error(f"Validation failed: {str(e)}")
            state["context"]["validation"] = {
                "success": False,
                "errors": [str(e)]
            }

        return state

    async def _handle_errors(self, state: DevOpsState) -> DevOpsState:
        """Handle workflow errors"""
        self.logger.info("Handling workflow errors")

        errors = state["errors"]
        failed_agents = state["failed_agents"]

        # Determine error recovery strategy
        if len(errors) > 3:  # Too many errors
            state["context"]["error_action"] = "finalize"
            state["status"] = "failed"
        elif "infrastructure" in failed_agents and len(errors) < 2:
            # Retry infrastructure if it's the only failure
            state["context"]["error_action"] = "retry"
        else:
            # Finalize with partial results
            state["context"]["error_action"] = "finalize"
            state["status"] = "partial_success"

        return state

    async def _finalize_workflow(self, state: DevOpsState) -> DevOpsState:
        """Finalize workflow execution"""
        self.logger.info("Finalizing workflow")

        # Compile final results
        results = {
            "agents_executed": state["completed_agents"],
            "agents_failed": state["failed_agents"],
            "infrastructure_changes": state["infrastructure_changes"],
            "pipeline_status": state.get("pipeline_status"),
            "alerts": state["alerts"],
            "recommendations": state["recommendations"],
            "errors": state["errors"]
        }

        # Set final status if not already set
        if state["status"] == "running":
            if state["errors"]:
                state["status"] = "completed_with_errors"
            else:
                state["status"] = "completed"

        state = StateManager.finalize_workflow(state, state["status"], results)

        self.logger.info(f"Workflow finalized with status: {state['status']}")
        return state

    async def _execute_security_agent(self, state: DevOpsState) -> DevOpsState:
        """Execute Security agent"""
        try:
            self.logger.info("Executing Security agent")

            state = StateManager.update_agent_status(state, "security", "started")

            # Determine security task
            security_task = self._determine_security_task(state)

            # Execute Security agent
            security_agent = self.agents["security"]
            result = await security_agent.execute(security_task, state["context"])

            if result["success"]:
                state = StateManager.update_agent_status(
                    state, "security", "completed", result
                )
                # Add security findings to state
                if result.get("security_findings"):
                    for finding in result["security_findings"]:
                        state = StateManager.add_alert(
                            state, "security", finding.get("severity", "medium"),
                            finding.get("message", "Security finding"),
                            "security_agent", finding
                        )
            else:
                state = StateManager.update_agent_status(
                    state, "security", "failed", result
                )
                state = StateManager.add_error(
                    state, "security", result.get("error", "Security execution failed")
                )

        except Exception as e:
            self.logger.error(f"Security agent execution failed: {str(e)}")
            state = StateManager.add_error(state, "security", str(e))
            state = StateManager.update_agent_status(state, "security", "failed")

        return state

    async def _execute_testing_agent(self, state: DevOpsState) -> DevOpsState:
        """Execute Testing agent"""
        try:
            self.logger.info("Executing Testing agent")

            state = StateManager.update_agent_status(state, "testing", "started")

            # Determine testing task
            testing_task = self._determine_testing_task(state)

            # Execute Testing agent
            testing_agent = self.agents["testing"]
            result = await testing_agent.execute(testing_task, state["context"])

            if result["success"]:
                state = StateManager.update_agent_status(
                    state, "testing", "completed", result
                )
                # Update metrics with test results
                if result.get("test_metrics"):
                    state["metrics"].update(result["test_metrics"])
            else:
                state = StateManager.update_agent_status(
                    state, "testing", "failed", result
                )
                state = StateManager.add_error(
                    state, "testing", result.get("error", "Testing execution failed")
                )

        except Exception as e:
            self.logger.error(f"Testing agent execution failed: {str(e)}")
            state = StateManager.add_error(state, "testing", str(e))
            state = StateManager.update_agent_status(state, "testing", "failed")

        return state

    # Decision functions for conditional edges

    def _determine_agent_routing(self, state: DevOpsState) -> str:
        """Determine which agent(s) to route to"""
        routing = state["context"].get("routing", "cicd")

        if routing == "error":
            return "error"
        return routing

    def _check_cicd_completion(self, state: DevOpsState) -> str:
        """Check CI/CD agent completion and determine next step"""
        if "cicd" in state["failed_agents"]:
            return "error"

        routing = state["context"].get("routing", "cicd")
        if routing == "both" and "infrastructure" not in state["completed_agents"]:
            return "continue_infrastructure"

        return "validate"

    def _check_infrastructure_completion(self, state: DevOpsState) -> str:
        """Check Infrastructure agent completion"""
        if "infrastructure" in state["failed_agents"]:
            return "error"

        return "validate"

    def _check_validation(self, state: DevOpsState) -> str:
        """Check validation results"""
        validation = state["context"].get("validation", {})

        if validation.get("success", False):
            return "success"

        # Determine retry strategy based on errors
        errors = validation.get("errors", [])
        if any("cicd" in error.lower() for error in errors):
            return "retry_cicd"
        elif any("infrastructure" in error.lower() for error in errors):
            return "retry_infrastructure"

        return "error"

    def _check_error_recovery(self, state: DevOpsState) -> str:
        """Check error recovery strategy"""
        return state["context"].get("error_action", "finalize")

    # Helper methods

    def _determine_cicd_task(self, state: DevOpsState) -> str:
        """Determine CI/CD task based on workflow context"""
        workflow_type = state["workflow_type"]
        user_request = state["user_request"]

        if workflow_type == "deployment":
            return f"Execute deployment pipeline: {user_request}"
        elif "build" in user_request.lower():
            return f"Build and test application: {user_request}"
        elif "test" in user_request.lower():
            return f"Run test suite: {user_request}"
        else:
            return f"Execute CI/CD workflow: {user_request}"

    def _determine_infrastructure_task(self, state: DevOpsState) -> str:
        """Determine Infrastructure task based on workflow context"""
        workflow_type = state["workflow_type"]
        user_request = state["user_request"]

        if workflow_type == "infrastructure":
            return f"Manage infrastructure: {user_request}"
        elif "provision" in user_request.lower():
            return f"Provision infrastructure resources: {user_request}"
        elif "scale" in user_request.lower():
            return f"Scale infrastructure: {user_request}"
        else:
            return f"Execute infrastructure workflow: {user_request}"

    def _determine_security_task(self, state: DevOpsState) -> str:
        """Determine Security task based on workflow context"""
        workflow_type = state["workflow_type"]
        user_request = state["user_request"]

        if workflow_type == "security":
            return f"Execute security assessment: {user_request}"
        elif "vulnerability" in user_request.lower():
            return f"Perform vulnerability scan: {user_request}"
        elif "compliance" in user_request.lower():
            return f"Check compliance: {user_request}"
        elif "audit" in user_request.lower():
            return f"Conduct security audit: {user_request}"
        else:
            return f"Execute security workflow: {user_request}"

    def _determine_testing_task(self, state: DevOpsState) -> str:
        """Determine Testing task based on workflow context"""
        workflow_type = state["workflow_type"]
        user_request = state["user_request"]

        if workflow_type == "testing":
            return f"Execute test suite: {user_request}"
        elif "coverage" in user_request.lower():
            return f"Analyze test coverage: {user_request}"
        elif "performance" in user_request.lower():
            return f"Execute performance tests: {user_request}"
        elif "quality" in user_request.lower():
            return f"Analyze code quality: {user_request}"
        else:
            return f"Execute testing workflow: {user_request}"

    def _get_required_agents(self, state: DevOpsState) -> List[str]:
        """Get list of required agents for the workflow"""
        routing = state["context"].get("routing", "cicd")

        if routing == "multi_agent":
            return state["context"].get("required_agents", ["cicd"])
        elif routing == "security":
            return ["security"]
        elif routing == "testing":
            return ["testing"]
        elif routing == "infrastructure":
            return ["infrastructure"]
        else:
            return ["cicd"]