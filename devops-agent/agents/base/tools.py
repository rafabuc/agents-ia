"""
Base Tools for DevOps AI Agents
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
from langchain_core.tools import BaseTool
from pydantic import BaseModel


class BaseDevOpsTool(BaseTool, ABC):
    """
    Base class for all DevOps tools used by agents
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(f"tool.{self.name}")

    @abstractmethod
    def _run(self, *args, **kwargs) -> Any:
        """Synchronous implementation of the tool"""
        pass

    async def _arun(self, *args, **kwargs) -> Any:
        """Asynchronous implementation of the tool"""
        return self._run(*args, **kwargs)

    def log_execution(self, action: str, details: Optional[Dict] = None):
        """Log tool execution"""
        self.logger.info(f"Executing {action}: {details or {}}")


class ShellCommandTool(BaseDevOpsTool):
    """Tool for executing shell commands safely"""

    name: str = "shell_command"
    description: str = "Execute shell commands with safety checks"

    def __init__(self, allowed_commands: Optional[list] = None, **kwargs):
        super().__init__(**kwargs)
        self.allowed_commands = allowed_commands or []

    def _run(self, command: str) -> Dict[str, Any]:
        """Execute a shell command with safety checks"""
        import subprocess
        import shlex

        self.log_execution("shell_command", {"command": command})

        # Safety checks
        if self.allowed_commands and not any(
            command.startswith(allowed) for allowed in self.allowed_commands
        ):
            return {
                "success": False,
                "error": f"Command not allowed: {command}",
                "output": ""
            }

        try:
            # Parse command safely
            cmd_parts = shlex.split(command)

            # Execute command
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                check=False
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }


class GitTool(BaseDevOpsTool):
    """Tool for Git operations"""

    name: str = "git"
    description: str = "Perform Git operations like status, commit, push"

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute Git operations"""
        self.log_execution("git", {"action": action, "kwargs": kwargs})

        try:
            if action == "status":
                return self._git_status()
            elif action == "add":
                return self._git_add(kwargs.get("files", "."))
            elif action == "commit":
                return self._git_commit(kwargs.get("message", "Auto commit"))
            elif action == "push":
                return self._git_push()
            else:
                return {"success": False, "error": f"Unknown git action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _git_status(self) -> Dict[str, Any]:
        """Get git status"""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "success": True,
                "output": result.stdout,
                "has_changes": bool(result.stdout.strip())
            }
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}

    def _git_add(self, files: str) -> Dict[str, Any]:
        """Add files to git"""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "add", files],
                capture_output=True,
                text=True,
                check=True
            )
            return {"success": True, "output": "Files added successfully"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}

    def _git_commit(self, message: str) -> Dict[str, Any]:
        """Commit changes"""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                capture_output=True,
                text=True,
                check=True
            )
            return {"success": True, "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}

    def _git_push(self) -> Dict[str, Any]:
        """Push changes"""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "push"],
                capture_output=True,
                text=True,
                check=True
            )
            return {"success": True, "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}


class KubernetesTool(BaseDevOpsTool):
    """Tool for Kubernetes operations"""

    name: str = "kubectl"
    description: str = "Execute kubectl commands for Kubernetes management"

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute Kubernetes operations"""
        self.log_execution("kubectl", {"action": action, "kwargs": kwargs})

        try:
            if action == "get":
                return self._kubectl_get(
                    kwargs.get("resource"),
                    kwargs.get("namespace"),
                    kwargs.get("selector")
                )
            elif action == "apply":
                return self._kubectl_apply(kwargs.get("file"))
            elif action == "delete":
                return self._kubectl_delete(
                    kwargs.get("resource"),
                    kwargs.get("name"),
                    kwargs.get("namespace")
                )
            else:
                return {"success": False, "error": f"Unknown kubectl action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _kubectl_get(self, resource: str, namespace: str = None, selector: str = None) -> Dict[str, Any]:
        """Get Kubernetes resources"""
        import subprocess

        cmd = ["kubectl", "get", resource, "-o", "json"]
        if namespace:
            cmd.extend(["-n", namespace])
        if selector:
            cmd.extend(["-l", selector])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {"success": True, "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}

    def _kubectl_apply(self, file: str) -> Dict[str, Any]:
        """Apply Kubernetes manifest"""
        import subprocess
        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", file],
                capture_output=True,
                text=True,
                check=True
            )
            return {"success": True, "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}

    def _kubectl_delete(self, resource: str, name: str, namespace: str = None) -> Dict[str, Any]:
        """Delete Kubernetes resource"""
        import subprocess

        cmd = ["kubectl", "delete", resource, name]
        if namespace:
            cmd.extend(["-n", namespace])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return {"success": True, "output": result.stdout}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": e.stderr}