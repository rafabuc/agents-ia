"""
DevOps Workflow State Management for LangGraph
"""

from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import json


class DevOpsState(TypedDict):
    """
    State schema for DevOps workflows in LangGraph.
    Contains all necessary information for multi-agent coordination.
    """

    # Workflow metadata
    workflow_id: str
    workflow_type: str  # deployment, incident_response, optimization, etc.
    status: str  # pending, running, completed, failed
    created_at: str
    updated_at: str

    # Request information
    user_request: str
    context: Dict[str, Any]

    # Agent coordination
    current_agent: Optional[str]
    completed_agents: List[str]
    failed_agents: List[str]
    agent_outputs: Dict[str, Any]

    # Infrastructure state
    environments: List[str]
    target_environment: Optional[str]
    infrastructure_changes: List[Dict[str, Any]]

    # CI/CD state
    pipeline_status: Optional[str]
    build_info: Optional[Dict[str, Any]]
    deployment_info: Optional[Dict[str, Any]]

    # Monitoring and alerts
    alerts: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    health_checks: Dict[str, Any]

    # Security and compliance
    security_scans: List[Dict[str, Any]]
    compliance_checks: Dict[str, Any]

    # Results and feedback
    workflow_results: Dict[str, Any]
    recommendations: List[str]
    next_actions: List[str]

    # Error handling
    errors: List[Dict[str, Any]]
    rollback_plan: Optional[Dict[str, Any]]


class StateManager:
    """Utility class for managing DevOps workflow state"""

    @staticmethod
    def create_initial_state(
        workflow_type: str,
        user_request: str,
        context: Dict[str, Any] = None
    ) -> DevOpsState:
        """Create initial state for a new workflow"""
        timestamp = datetime.now().isoformat()

        return DevOpsState(
            workflow_id=f"workflow_{int(datetime.now().timestamp())}",
            workflow_type=workflow_type,
            status="pending",
            created_at=timestamp,
            updated_at=timestamp,
            user_request=user_request,
            context=context or {},
            current_agent=None,
            completed_agents=[],
            failed_agents=[],
            agent_outputs={},
            environments=[],
            target_environment=None,
            infrastructure_changes=[],
            pipeline_status=None,
            build_info=None,
            deployment_info=None,
            alerts=[],
            metrics={},
            health_checks={},
            security_scans=[],
            compliance_checks={},
            workflow_results={},
            recommendations=[],
            next_actions=[],
            errors=[],
            rollback_plan=None
        )

    @staticmethod
    def update_agent_status(
        state: DevOpsState,
        agent_name: str,
        status: str,
        output: Dict[str, Any] = None
    ) -> DevOpsState:
        """Update agent execution status in state"""
        state = state.copy()
        state["updated_at"] = datetime.now().isoformat()

        if status == "started":
            state["current_agent"] = agent_name
        elif status == "completed":
            if agent_name not in state["completed_agents"]:
                state["completed_agents"].append(agent_name)
            if agent_name == state.get("current_agent"):
                state["current_agent"] = None
            if output:
                state["agent_outputs"][agent_name] = output
        elif status == "failed":
            if agent_name not in state["failed_agents"]:
                state["failed_agents"].append(agent_name)
            if agent_name == state.get("current_agent"):
                state["current_agent"] = None
            if output:
                state["agent_outputs"][agent_name] = output

        return state

    @staticmethod
    def add_error(
        state: DevOpsState,
        agent_name: str,
        error_message: str,
        error_details: Dict[str, Any] = None
    ) -> DevOpsState:
        """Add error information to state"""
        state = state.copy()
        state["errors"].append({
            "agent": agent_name,
            "message": error_message,
            "details": error_details or {},
            "timestamp": datetime.now().isoformat()
        })
        state["updated_at"] = datetime.now().isoformat()
        return state

    @staticmethod
    def add_infrastructure_change(
        state: DevOpsState,
        change_type: str,
        resource: str,
        action: str,
        details: Dict[str, Any] = None
    ) -> DevOpsState:
        """Add infrastructure change to state"""
        state = state.copy()
        state["infrastructure_changes"].append({
            "type": change_type,
            "resource": resource,
            "action": action,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })
        state["updated_at"] = datetime.now().isoformat()
        return state

    @staticmethod
    def add_alert(
        state: DevOpsState,
        alert_type: str,
        severity: str,
        message: str,
        source: str,
        metadata: Dict[str, Any] = None
    ) -> DevOpsState:
        """Add alert to state"""
        state = state.copy()
        state["alerts"].append({
            "type": alert_type,
            "severity": severity,
            "message": message,
            "source": source,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
        state["updated_at"] = datetime.now().isoformat()
        return state

    @staticmethod
    def update_pipeline_status(
        state: DevOpsState,
        status: str,
        build_info: Dict[str, Any] = None,
        deployment_info: Dict[str, Any] = None
    ) -> DevOpsState:
        """Update CI/CD pipeline status"""
        state = state.copy()
        state["pipeline_status"] = status
        if build_info:
            state["build_info"] = build_info
        if deployment_info:
            state["deployment_info"] = deployment_info
        state["updated_at"] = datetime.now().isoformat()
        return state

    @staticmethod
    def add_recommendation(
        state: DevOpsState,
        recommendation: str,
        priority: str = "medium",
        category: str = "general"
    ) -> DevOpsState:
        """Add recommendation to state"""
        state = state.copy()
        state["recommendations"].append({
            "text": recommendation,
            "priority": priority,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        state["updated_at"] = datetime.now().isoformat()
        return state

    @staticmethod
    def set_rollback_plan(
        state: DevOpsState,
        rollback_plan: Dict[str, Any]
    ) -> DevOpsState:
        """Set rollback plan in state"""
        state = state.copy()
        state["rollback_plan"] = rollback_plan
        state["updated_at"] = datetime.now().isoformat()
        return state

    @staticmethod
    def finalize_workflow(
        state: DevOpsState,
        status: str,
        results: Dict[str, Any]
    ) -> DevOpsState:
        """Finalize workflow with results"""
        state = state.copy()
        state["status"] = status
        state["workflow_results"] = results
        state["current_agent"] = None
        state["updated_at"] = datetime.now().isoformat()
        return state

    @staticmethod
    def get_summary(state: DevOpsState) -> Dict[str, Any]:
        """Get workflow summary"""
        return {
            "workflow_id": state["workflow_id"],
            "workflow_type": state["workflow_type"],
            "status": state["status"],
            "duration": state["updated_at"],  # Could calculate actual duration
            "agents_completed": len(state["completed_agents"]),
            "agents_failed": len(state["failed_agents"]),
            "infrastructure_changes": len(state["infrastructure_changes"]),
            "alerts_count": len(state["alerts"]),
            "errors_count": len(state["errors"]),
            "recommendations_count": len(state["recommendations"]),
            "current_agent": state.get("current_agent"),
            "target_environment": state.get("target_environment")
        }

    @staticmethod
    def to_dict(state: DevOpsState) -> Dict[str, Any]:
        """Convert state to dictionary for serialization"""
        return dict(state)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> DevOpsState:
        """Create state from dictionary"""
        return DevOpsState(**data)

    @staticmethod
    def to_json(state: DevOpsState) -> str:
        """Convert state to JSON string"""
        return json.dumps(StateManager.to_dict(state), indent=2)

    @staticmethod
    def from_json(json_str: str) -> DevOpsState:
        """Create state from JSON string"""
        data = json.loads(json_str)
        return StateManager.from_dict(data)