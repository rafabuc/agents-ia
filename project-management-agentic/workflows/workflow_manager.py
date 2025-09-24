
# workflows/workflow_manager.py
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

from .project_workflow import ProjectWorkflow
from storage.database_manager import DatabaseManager
from utils.logger import logger


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowManager:
    """Manages and orchestrates multiple workflows."""
    
    def __init__(self):
        self.project_workflow = ProjectWorkflow()
        self.db_manager = DatabaseManager()
        self.active_workflows: Dict[str, Dict] = {}
        self.workflow_templates: Dict[str, Callable] = {
            "create_project": self.project_workflow.create_project_workflow,
            "cost_analysis": self.project_workflow.cost_analysis_workflow,
            "custom": self.project_workflow.execute_workflow
        }
        logger.info("WorkflowManager initialized")
    
    def execute_workflow(self, workflow_type: str, **kwargs) -> Dict[str, Any]:
        """Execute a workflow by type."""
        
        if workflow_type not in self.workflow_templates:
            return {
                "success": False,
                "error": f"Unknown workflow type: {workflow_type}",
                "available_workflows": list(self.workflow_templates.keys())
            }
        
        workflow_id = f"{workflow_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        print(f' workflow_id == {workflow_id}  workflow_type {workflow_type}  self.workflow_templates== { self.workflow_templates}')
        try:
            # Mark workflow as running
            self.active_workflows[workflow_id] = {
                "type": workflow_type,
                "status": WorkflowStatus.RUNNING,
                "started_at": datetime.utcnow(),
                "kwargs": kwargs
            }
            
            # Execute workflow
            workflow_func = self.workflow_templates[workflow_type]
            result = workflow_func(**kwargs)
            
            # Update status
            self.active_workflows[workflow_id].update({
                "status": WorkflowStatus.COMPLETED if result.get("success") else WorkflowStatus.FAILED,
                "completed_at": datetime.utcnow(),
                "result": result
            })
            
            # Add workflow ID to result
            result["workflow_id"] = workflow_id
            
            logger.info(f"Workflow {workflow_id} completed with status: {self.active_workflows[workflow_id]['status']}")
            
            return result
            
        except Exception as e:
            # Mark as failed
            self.active_workflows[workflow_id] = {
                "type": workflow_type,
                "status": WorkflowStatus.FAILED,
                "started_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
                "error": str(e),
                "kwargs": kwargs
            }
            
            logger.error(f"Workflow {workflow_id} failed: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id
            }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific workflow."""
        return self.active_workflows.get(workflow_id)
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active/recent workflows."""
        return [
            {
                "workflow_id": wf_id,
                **workflow_data
            }
            for wf_id, workflow_data in self.active_workflows.items()
        ]
    
    def create_project_complete(self, project_name: str, description: str = "",
                               methodology: str = "PMP", **additional_data) -> Dict[str, Any]:
        """Complete project creation workflow."""
        
        project_data = {
            "name": project_name,
            "description": description,
            "methodology": methodology,
            **additional_data
        }
        
        return self.execute_workflow("create_project", project_data=project_data)
    
    def analyze_project_costs(self, project_id: int, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Execute cost analysis workflow."""
        
        return self.execute_workflow(
            "cost_analysis",
            project_id=project_id,
            analysis_type=analysis_type
        )
    
    def custom_workflow(self, input_text: str, request_type: str = "general",
                       project_id: Optional[int] = None) -> Dict[str, Any]:
        """Execute custom workflow."""
        
        return self.execute_workflow(
            "custom",
            input_text=input_text,
            request_type=request_type,
            project_id=project_id
        )
    
    def get_available_workflows(self) -> Dict[str, str]:
        """Get available workflow types and descriptions."""
        return {
            "create_project": "Complete project creation with charter, initial cost estimate, and templates",
            "cost_analysis": "Comprehensive cost analysis including estimates, budgets, and baselines",
            "custom": "Custom workflow based on natural language input and request type"
        }
    
    def cleanup_completed_workflows(self, max_age_hours: int = 24):
        """Clean up completed workflows older than specified hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        workflows_to_remove = []
        for workflow_id, workflow_data in self.active_workflows.items():
            if (workflow_data.get("status") in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED] and
                workflow_data.get("completed_at", datetime.utcnow()) < cutoff_time):
                workflows_to_remove.append(workflow_id)
        
        for workflow_id in workflows_to_remove:
            del self.active_workflows[workflow_id]
        
        logger.info(f"Cleaned up {len(workflows_to_remove)} old workflows")