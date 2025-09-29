"""
Terraform Tool for Infrastructure Agent
"""

import os
import json
import subprocess
from typing import Dict, Any, Optional, List
from pathlib import Path

from ...base.tools import BaseDevOpsTool


class TerraformTool(BaseDevOpsTool):
    """Tool for managing Terraform infrastructure as code"""

    name: str = "terraform"
    description: str = "Execute Terraform commands for infrastructure provisioning and management"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.terraform_dir = Path("infrastructure/terraform")

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute Terraform operations"""
        self.log_execution("terraform", {"action": action, "kwargs": kwargs})

        try:
            if action == "init":
                return self._terraform_init(kwargs.get("environment"))
            elif action == "plan":
                return self._terraform_plan(
                    kwargs.get("environment"),
                    kwargs.get("var_files", []),
                    kwargs.get("variables", {})
                )
            elif action == "apply":
                return self._terraform_apply(
                    kwargs.get("environment"),
                    kwargs.get("auto_approve", False),
                    kwargs.get("var_files", []),
                    kwargs.get("variables", {})
                )
            elif action == "destroy":
                return self._terraform_destroy(
                    kwargs.get("environment"),
                    kwargs.get("auto_approve", False)
                )
            elif action == "validate":
                return self._terraform_validate(kwargs.get("environment"))
            elif action == "state":
                return self._terraform_state(
                    kwargs.get("environment"),
                    kwargs.get("state_action"),
                    kwargs.get("resource")
                )
            elif action == "output":
                return self._terraform_output(kwargs.get("environment"))
            elif action == "workspace":
                return self._terraform_workspace(
                    kwargs.get("workspace_action"),
                    kwargs.get("workspace_name")
                )
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _terraform_init(self, environment: str) -> Dict[str, Any]:
        """Initialize Terraform configuration"""
        try:
            env_dir = self.terraform_dir / "environments" / environment
            if not env_dir.exists():
                return {"success": False, "error": f"Environment directory not found: {env_dir}"}

            result = subprocess.run(
                ["terraform", "init"],
                cwd=env_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Terraform initialized for environment: {environment}",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Terraform init failed: {result.stderr}",
                    "output": result.stdout
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _terraform_plan(self, environment: str, var_files: List[str] = None,
                       variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate Terraform execution plan"""
        try:
            env_dir = self.terraform_dir / "environments" / environment
            if not env_dir.exists():
                return {"success": False, "error": f"Environment directory not found: {env_dir}"}

            cmd = ["terraform", "plan", "-out=tfplan"]

            # Add variable files
            if var_files:
                for var_file in var_files:
                    cmd.extend(["-var-file", var_file])

            # Add individual variables
            if variables:
                for key, value in variables.items():
                    cmd.extend(["-var", f"{key}={value}"])

            result = subprocess.run(
                cmd,
                cwd=env_dir,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                # Parse plan output for changes summary
                plan_summary = self._parse_plan_output(result.stdout)

                return {
                    "success": True,
                    "message": f"Terraform plan generated for environment: {environment}",
                    "output": result.stdout,
                    "plan_summary": plan_summary,
                    "plan_file": "tfplan"
                }
            else:
                return {
                    "success": False,
                    "error": f"Terraform plan failed: {result.stderr}",
                    "output": result.stdout
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _terraform_apply(self, environment: str, auto_approve: bool = False,
                        var_files: List[str] = None, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Apply Terraform configuration"""
        try:
            env_dir = self.terraform_dir / "environments" / environment
            if not env_dir.exists():
                return {"success": False, "error": f"Environment directory not found: {env_dir}"}

            # Check if plan file exists
            plan_file = env_dir / "tfplan"
            if plan_file.exists():
                cmd = ["terraform", "apply", "tfplan"]
            else:
                cmd = ["terraform", "apply"]
                if auto_approve:
                    cmd.append("-auto-approve")

                # Add variable files
                if var_files:
                    for var_file in var_files:
                        cmd.extend(["-var-file", var_file])

                # Add individual variables
                if variables:
                    for key, value in variables.items():
                        cmd.extend(["-var", f"{key}={value}"])

            result = subprocess.run(
                cmd,
                cwd=env_dir,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes for apply operations
            )

            if result.returncode == 0:
                # Clean up plan file
                if plan_file.exists():
                    plan_file.unlink()

                return {
                    "success": True,
                    "message": f"Terraform apply completed for environment: {environment}",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Terraform apply failed: {result.stderr}",
                    "output": result.stdout
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _terraform_destroy(self, environment: str, auto_approve: bool = False) -> Dict[str, Any]:
        """Destroy Terraform-managed infrastructure"""
        try:
            env_dir = self.terraform_dir / "environments" / environment
            if not env_dir.exists():
                return {"success": False, "error": f"Environment directory not found: {env_dir}"}

            cmd = ["terraform", "destroy"]
            if auto_approve:
                cmd.append("-auto-approve")

            result = subprocess.run(
                cmd,
                cwd=env_dir,
                capture_output=True,
                text=True,
                timeout=1800
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Terraform destroy completed for environment: {environment}",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Terraform destroy failed: {result.stderr}",
                    "output": result.stdout
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _terraform_validate(self, environment: str) -> Dict[str, Any]:
        """Validate Terraform configuration"""
        try:
            env_dir = self.terraform_dir / "environments" / environment
            if not env_dir.exists():
                return {"success": False, "error": f"Environment directory not found: {env_dir}"}

            result = subprocess.run(
                ["terraform", "validate", "-json"],
                cwd=env_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                try:
                    validation_result = json.loads(result.stdout)
                    return {
                        "success": True,
                        "message": "Terraform configuration is valid",
                        "validation_result": validation_result
                    }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "message": "Terraform configuration is valid",
                        "output": result.stdout
                    }
            else:
                return {
                    "success": False,
                    "error": f"Terraform validation failed: {result.stderr}",
                    "output": result.stdout
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _terraform_state(self, environment: str, state_action: str, resource: str = None) -> Dict[str, Any]:
        """Manage Terraform state"""
        try:
            env_dir = self.terraform_dir / "environments" / environment
            if not env_dir.exists():
                return {"success": False, "error": f"Environment directory not found: {env_dir}"}

            if state_action == "list":
                cmd = ["terraform", "state", "list"]
            elif state_action == "show" and resource:
                cmd = ["terraform", "state", "show", resource]
            elif state_action == "rm" and resource:
                cmd = ["terraform", "state", "rm", resource]
            else:
                return {"success": False, "error": f"Invalid state action: {state_action}"}

            result = subprocess.run(
                cmd,
                cwd=env_dir,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Terraform state {state_action} completed",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Terraform state {state_action} failed: {result.stderr}",
                    "output": result.stdout
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _terraform_output(self, environment: str) -> Dict[str, Any]:
        """Get Terraform outputs"""
        try:
            env_dir = self.terraform_dir / "environments" / environment
            if not env_dir.exists():
                return {"success": False, "error": f"Environment directory not found: {env_dir}"}

            result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd=env_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                try:
                    outputs = json.loads(result.stdout)
                    return {
                        "success": True,
                        "outputs": outputs,
                        "message": "Terraform outputs retrieved successfully"
                    }
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "output": result.stdout,
                        "message": "Terraform outputs retrieved (non-JSON format)"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get terraform outputs: {result.stderr}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _terraform_workspace(self, workspace_action: str, workspace_name: str = None) -> Dict[str, Any]:
        """Manage Terraform workspaces"""
        try:
            if workspace_action == "list":
                cmd = ["terraform", "workspace", "list"]
            elif workspace_action == "new" and workspace_name:
                cmd = ["terraform", "workspace", "new", workspace_name]
            elif workspace_action == "select" and workspace_name:
                cmd = ["terraform", "workspace", "select", workspace_name]
            elif workspace_action == "delete" and workspace_name:
                cmd = ["terraform", "workspace", "delete", workspace_name]
            else:
                return {"success": False, "error": f"Invalid workspace action: {workspace_action}"}

            result = subprocess.run(
                cmd,
                cwd=self.terraform_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Terraform workspace {workspace_action} completed",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Terraform workspace {workspace_action} failed: {result.stderr}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_plan_output(self, output: str) -> Dict[str, Any]:
        """Parse Terraform plan output to extract changes summary"""
        summary = {
            "to_add": 0,
            "to_change": 0,
            "to_destroy": 0,
            "resources": []
        }

        try:
            lines = output.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('Plan:'):
                    # Extract numbers from plan summary line
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'add' in part and i > 0:
                            summary["to_add"] = int(parts[i-1])
                        elif 'change' in part and i > 0:
                            summary["to_change"] = int(parts[i-1])
                        elif 'destroy' in part and i > 0:
                            summary["to_destroy"] = int(parts[i-1])

                # Extract resource changes
                if line.startswith('+ ') or line.startswith('~ ') or line.startswith('- '):
                    action = 'add' if line.startswith('+ ') else ('change' if line.startswith('~ ') else 'destroy')
                    resource = line[2:].split()[0] if len(line) > 2 else 'unknown'
                    summary["resources"].append({"action": action, "resource": resource})

        except Exception as e:
            self.logger.warning(f"Failed to parse plan output: {str(e)}")

        return summary