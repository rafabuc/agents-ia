"""
Pipeline Tool for CI/CD Agent
"""

from typing import Dict, Any, List, Optional
import json
import subprocess
from pathlib import Path

from ...base.tools import BaseDevOpsTool


class PipelineTool(BaseDevOpsTool):
    """Tool for managing CI/CD pipelines"""

    name: str = "pipeline"
    description: str = "Execute and manage CI/CD pipelines and stages"

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute pipeline operations"""
        self.log_execution("pipeline", {"action": action, "kwargs": kwargs})

        try:
            if action == "run":
                return self._run_pipeline(
                    kwargs.get("pipeline_name"),
                    kwargs.get("parameters", {})
                )
            elif action == "status":
                return self._get_pipeline_status(kwargs.get("pipeline_name"))
            elif action == "create":
                return self._create_pipeline(kwargs.get("pipeline_config"))
            elif action == "validate":
                return self._validate_pipeline(kwargs.get("pipeline_config"))
            elif action == "list":
                return self._list_pipelines()
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_pipeline(self, pipeline_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a CI/CD pipeline"""
        try:
            self.logger.info(f"Running pipeline: {pipeline_name}")

            # Load pipeline configuration
            pipeline_config = self._load_pipeline_config(pipeline_name)
            if not pipeline_config:
                return {"success": False, "error": f"Pipeline '{pipeline_name}' not found"}

            # Execute pipeline stages
            results = []
            for stage in pipeline_config.get("stages", []):
                stage_result = self._execute_stage(stage, parameters)
                results.append(stage_result)

                # Stop on failure if not configured to continue
                if not stage_result["success"] and not stage.get("continue_on_failure", False):
                    return {
                        "success": False,
                        "pipeline": pipeline_name,
                        "failed_stage": stage["name"],
                        "error": stage_result["error"],
                        "results": results
                    }

            return {
                "success": True,
                "pipeline": pipeline_name,
                "results": results,
                "message": f"Pipeline '{pipeline_name}' completed successfully"
            }

        except Exception as e:
            return {"success": False, "error": f"Pipeline execution failed: {str(e)}"}

    def _execute_stage(self, stage: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single pipeline stage"""
        stage_name = stage.get("name", "unnamed_stage")
        self.logger.info(f"Executing stage: {stage_name}")

        try:
            # Replace parameters in commands
            commands = stage.get("commands", [])
            processed_commands = []

            for cmd in commands:
                # Simple parameter substitution
                for key, value in parameters.items():
                    cmd = cmd.replace(f"${{{key}}}", str(value))
                processed_commands.append(cmd)

            # Execute commands
            outputs = []
            for cmd in processed_commands:
                result = self._execute_command(cmd, stage.get("environment", {}))
                outputs.append(result)

                if not result["success"] and not stage.get("continue_on_failure", False):
                    return {
                        "success": False,
                        "stage": stage_name,
                        "command": cmd,
                        "error": result["error"],
                        "outputs": outputs
                    }

            return {
                "success": True,
                "stage": stage_name,
                "outputs": outputs
            }

        except Exception as e:
            return {
                "success": False,
                "stage": stage_name,
                "error": str(e)
            }

    def _execute_command(self, command: str, environment: Dict[str, str]) -> Dict[str, Any]:
        """Execute a single command"""
        try:
            # Prepare environment
            env = os.environ.copy()
            env.update(environment)

            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                env=env,
                timeout=3600  # 1 hour timeout
            )

            return {
                "success": result.returncode == 0,
                "command": command,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "command": command,
                "error": "Command timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "command": command,
                "error": str(e)
            }

    def _load_pipeline_config(self, pipeline_name: str) -> Optional[Dict[str, Any]]:
        """Load pipeline configuration from file"""
        try:
            # Look for pipeline config in various locations
            config_paths = [
                f".pipelines/{pipeline_name}.json",
                f"pipelines/{pipeline_name}.json",
                f".github/pipelines/{pipeline_name}.json"
            ]

            for config_path in config_paths:
                if Path(config_path).exists():
                    with open(config_path, "r") as f:
                        return json.load(f)

            # Return default pipeline if no config found
            return self._get_default_pipeline_config(pipeline_name)

        except Exception as e:
            self.logger.error(f"Failed to load pipeline config: {str(e)}")
            return None

    def _get_default_pipeline_config(self, pipeline_name: str) -> Dict[str, Any]:
        """Get default pipeline configuration based on name"""
        if pipeline_name == "build":
            return {
                "name": "build",
                "description": "Build pipeline",
                "stages": [
                    {
                        "name": "install_dependencies",
                        "commands": ["pip install -r requirements.txt"]
                    },
                    {
                        "name": "lint",
                        "commands": ["flake8 .", "black --check ."]
                    },
                    {
                        "name": "build",
                        "commands": ["python setup.py build"]
                    }
                ]
            }
        elif pipeline_name == "test":
            return {
                "name": "test",
                "description": "Test pipeline",
                "stages": [
                    {
                        "name": "unit_tests",
                        "commands": ["pytest tests/unit/"]
                    },
                    {
                        "name": "integration_tests",
                        "commands": ["pytest tests/integration/"]
                    },
                    {
                        "name": "coverage",
                        "commands": ["coverage run -m pytest", "coverage report"]
                    }
                ]
            }
        elif pipeline_name == "deploy":
            return {
                "name": "deploy",
                "description": "Deployment pipeline",
                "stages": [
                    {
                        "name": "build_image",
                        "commands": ["docker build -t ${image_name}:${version} ."]
                    },
                    {
                        "name": "push_image",
                        "commands": ["docker push ${image_name}:${version}"]
                    },
                    {
                        "name": "deploy_k8s",
                        "commands": ["kubectl apply -f k8s/"]
                    }
                ]
            }
        else:
            return None

    def _create_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new pipeline configuration"""
        try:
            pipeline_name = pipeline_config.get("name")
            if not pipeline_name:
                return {"success": False, "error": "Pipeline name is required"}

            # Ensure pipelines directory exists
            pipelines_dir = Path(".pipelines")
            pipelines_dir.mkdir(exist_ok=True)

            # Write pipeline config
            config_file = pipelines_dir / f"{pipeline_name}.json"
            with open(config_file, "w") as f:
                json.dump(pipeline_config, f, indent=2)

            return {
                "success": True,
                "message": f"Pipeline '{pipeline_name}' created successfully",
                "config_file": str(config_file)
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to create pipeline: {str(e)}"}

    def _validate_pipeline(self, pipeline_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pipeline configuration"""
        errors = []
        warnings = []

        # Check required fields
        if not pipeline_config.get("name"):
            errors.append("Pipeline name is required")

        if not pipeline_config.get("stages"):
            errors.append("Pipeline must have at least one stage")

        # Validate stages
        stages = pipeline_config.get("stages", [])
        for i, stage in enumerate(stages):
            if not stage.get("name"):
                errors.append(f"Stage {i + 1} missing name")

            if not stage.get("commands"):
                warnings.append(f"Stage '{stage.get('name', i + 1)}' has no commands")

        return {
            "success": len(errors) == 0,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def _list_pipelines(self) -> Dict[str, Any]:
        """List available pipelines"""
        try:
            pipelines = []

            # Check for pipeline config files
            config_dirs = [".pipelines", "pipelines", ".github/pipelines"]
            for config_dir in config_dirs:
                if Path(config_dir).exists():
                    for config_file in Path(config_dir).glob("*.json"):
                        try:
                            with open(config_file, "r") as f:
                                config = json.load(f)
                                pipelines.append({
                                    "name": config.get("name", config_file.stem),
                                    "description": config.get("description", ""),
                                    "file": str(config_file),
                                    "stages": len(config.get("stages", []))
                                })
                        except Exception as e:
                            pipelines.append({
                                "name": config_file.stem,
                                "file": str(config_file),
                                "error": f"Invalid config: {str(e)}"
                            })

            # Add default pipelines if no custom ones found
            if not pipelines:
                pipelines = [
                    {"name": "build", "description": "Default build pipeline", "type": "default"},
                    {"name": "test", "description": "Default test pipeline", "type": "default"},
                    {"name": "deploy", "description": "Default deploy pipeline", "type": "default"}
                ]

            return {"success": True, "pipelines": pipelines}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_pipeline_status(self, pipeline_name: str) -> Dict[str, Any]:
        """Get pipeline execution status"""
        # This would typically track running pipelines
        # For now, return mock status
        return {
            "success": True,
            "pipeline": pipeline_name,
            "status": "idle",
            "message": "Pipeline status tracking not implemented yet"
        }