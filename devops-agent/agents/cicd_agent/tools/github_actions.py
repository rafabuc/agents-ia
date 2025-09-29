"""
GitHub Actions Tool for CI/CD Agent
"""

from typing import Dict, Any, Optional
import yaml
import os
from pathlib import Path

from ...base.tools import BaseDevOpsTool


class GitHubActionsTool(BaseDevOpsTool):
    """Tool for managing GitHub Actions workflows"""

    name: str = "github_actions"
    description: str = "Create, modify, and manage GitHub Actions workflows"

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute GitHub Actions operations"""
        self.log_execution("github_actions", {"action": action, "kwargs": kwargs})

        try:
            if action == "create_workflow":
                return self._create_workflow(
                    kwargs.get("workflow_config"),
                    kwargs.get("repo_path", ".")
                )
            elif action == "list_workflows":
                return self._list_workflows(kwargs.get("repo_path", "."))
            elif action == "validate_workflow":
                return self._validate_workflow(kwargs.get("workflow_file"))
            elif action == "get_workflow_runs":
                return self._get_workflow_runs(kwargs.get("workflow_name"))
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_workflow(self, workflow_config: Dict[str, Any], repo_path: str) -> Dict[str, Any]:
        """Create a new GitHub Actions workflow"""
        try:
            workflow_name = workflow_config.get("name", "workflow")
            workflow_file = f"{workflow_name.lower().replace(' ', '-')}.yml"

            # Ensure .github/workflows directory exists
            workflows_dir = Path(repo_path) / ".github" / "workflows"
            workflows_dir.mkdir(parents=True, exist_ok=True)

            # Create workflow content
            workflow_content = self._generate_workflow_yaml(workflow_config)

            # Write workflow file
            workflow_path = workflows_dir / workflow_file
            with open(workflow_path, "w") as f:
                f.write(workflow_content)

            return {
                "success": True,
                "message": f"Workflow created: {workflow_file}",
                "file_path": str(workflow_path),
                "workflow_name": workflow_name
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to create workflow: {str(e)}"}

    def _generate_workflow_yaml(self, config: Dict[str, Any]) -> str:
        """Generate GitHub Actions workflow YAML"""
        workflow = {
            "name": config.get("name", "CI/CD Pipeline"),
            "on": config.get("triggers", {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main"]}
            })
        }

        # Add jobs
        jobs = {}

        # Build job
        if config.get("build", True):
            jobs["build"] = {
                "runs-on": config.get("runner", "ubuntu-latest"),
                "steps": self._generate_build_steps(config)
            }

        # Test job
        if config.get("test", True):
            jobs["test"] = {
                "runs-on": config.get("runner", "ubuntu-latest"),
                "needs": "build" if config.get("build", True) else None,
                "steps": self._generate_test_steps(config)
            }

        # Deploy job
        if config.get("deploy", False):
            jobs["deploy"] = {
                "runs-on": config.get("runner", "ubuntu-latest"),
                "needs": ["build", "test"] if config.get("test", True) else ["build"],
                "if": "github.ref == 'refs/heads/main'",
                "steps": self._generate_deploy_steps(config)
            }

        workflow["jobs"] = jobs

        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)

    def _generate_build_steps(self, config: Dict[str, Any]) -> list:
        """Generate build steps for workflow"""
        steps = [
            {"uses": "actions/checkout@v4"},
            {
                "name": "Set up Python",
                "uses": "actions/setup-python@v4",
                "with": {"python-version": config.get("python_version", "3.11")}
            }
        ]

        # Add dependency installation
        if config.get("language") == "python":
            steps.extend([
                {
                    "name": "Install dependencies",
                    "run": "pip install -r requirements.txt"
                },
                {
                    "name": "Run linting",
                    "run": "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"
                }
            ])
        elif config.get("language") == "node":
            steps.extend([
                {
                    "name": "Set up Node.js",
                    "uses": "actions/setup-node@v3",
                    "with": {"node-version": config.get("node_version", "18")}
                },
                {
                    "name": "Install dependencies",
                    "run": "npm ci"
                }
            ])

        # Add custom build steps
        custom_steps = config.get("build_steps", [])
        steps.extend(custom_steps)

        return steps

    def _generate_test_steps(self, config: Dict[str, Any]) -> list:
        """Generate test steps for workflow"""
        steps = [
            {"uses": "actions/checkout@v4"},
            {
                "name": "Set up Python",
                "uses": "actions/setup-python@v4",
                "with": {"python-version": config.get("python_version", "3.11")}
            }
        ]

        if config.get("language") == "python":
            steps.extend([
                {
                    "name": "Install dependencies",
                    "run": "pip install -r requirements.txt"
                },
                {
                    "name": "Run tests",
                    "run": "pytest --cov=. --cov-report=xml"
                },
                {
                    "name": "Upload coverage reports",
                    "uses": "codecov/codecov-action@v3",
                    "with": {"file": "./coverage.xml"}
                }
            ])

        # Add custom test steps
        custom_steps = config.get("test_steps", [])
        steps.extend(custom_steps)

        return steps

    def _generate_deploy_steps(self, config: Dict[str, Any]) -> list:
        """Generate deployment steps for workflow"""
        steps = [
            {"uses": "actions/checkout@v4"}
        ]

        deploy_type = config.get("deploy_type", "docker")

        if deploy_type == "docker":
            steps.extend([
                {
                    "name": "Set up Docker Buildx",
                    "uses": "docker/setup-buildx-action@v2"
                },
                {
                    "name": "Login to Docker Registry",
                    "uses": "docker/login-action@v2",
                    "with": {
                        "registry": "${{ secrets.DOCKER_REGISTRY }}",
                        "username": "${{ secrets.DOCKER_USERNAME }}",
                        "password": "${{ secrets.DOCKER_PASSWORD }}"
                    }
                },
                {
                    "name": "Build and push Docker image",
                    "uses": "docker/build-push-action@v4",
                    "with": {
                        "context": ".",
                        "push": True,
                        "tags": "${{ secrets.DOCKER_REGISTRY }}/${{ github.repository }}:latest"
                    }
                }
            ])

        # Add custom deploy steps
        custom_steps = config.get("deploy_steps", [])
        steps.extend(custom_steps)

        return steps

    def _list_workflows(self, repo_path: str) -> Dict[str, Any]:
        """List existing workflows in repository"""
        try:
            workflows_dir = Path(repo_path) / ".github" / "workflows"

            if not workflows_dir.exists():
                return {"success": True, "workflows": []}

            workflows = []
            for workflow_file in workflows_dir.glob("*.yml"):
                with open(workflow_file, "r") as f:
                    try:
                        workflow_data = yaml.safe_load(f)
                        workflows.append({
                            "file": workflow_file.name,
                            "name": workflow_data.get("name", workflow_file.stem),
                            "path": str(workflow_file)
                        })
                    except yaml.YAMLError as e:
                        workflows.append({
                            "file": workflow_file.name,
                            "name": workflow_file.stem,
                            "path": str(workflow_file),
                            "error": f"Invalid YAML: {str(e)}"
                        })

            return {"success": True, "workflows": workflows}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _validate_workflow(self, workflow_file: str) -> Dict[str, Any]:
        """Validate a GitHub Actions workflow file"""
        try:
            with open(workflow_file, "r") as f:
                workflow_data = yaml.safe_load(f)

            # Basic validation
            errors = []
            warnings = []

            # Check required fields
            if "name" not in workflow_data:
                warnings.append("Missing 'name' field")

            if "on" not in workflow_data:
                errors.append("Missing 'on' (triggers) field")

            if "jobs" not in workflow_data:
                errors.append("Missing 'jobs' field")

            # Validate jobs
            jobs = workflow_data.get("jobs", {})
            for job_name, job_config in jobs.items():
                if "runs-on" not in job_config:
                    errors.append(f"Job '{job_name}' missing 'runs-on' field")

                if "steps" not in job_config:
                    errors.append(f"Job '{job_name}' missing 'steps' field")

            return {
                "success": len(errors) == 0,
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }

        except yaml.YAMLError as e:
            return {
                "success": False,
                "valid": False,
                "errors": [f"Invalid YAML syntax: {str(e)}"]
            }
        except FileNotFoundError:
            return {
                "success": False,
                "valid": False,
                "errors": [f"Workflow file not found: {workflow_file}"]
            }

    def _get_workflow_runs(self, workflow_name: str) -> Dict[str, Any]:
        """Get workflow run history (placeholder - would integrate with GitHub API)"""
        # This would typically integrate with GitHub API
        # For now, return mock data
        return {
            "success": True,
            "message": "Would fetch workflow runs from GitHub API",
            "workflow_name": workflow_name,
            "note": "GitHub API integration needed for live data"
        }