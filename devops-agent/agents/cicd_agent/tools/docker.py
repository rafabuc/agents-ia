"""
Docker Tool for CI/CD Agent
"""

import os
from typing import Dict, Any, List, Optional
import subprocess
import json

from ...base.tools import BaseDevOpsTool


class DockerTool(BaseDevOpsTool):
    """Tool for Docker operations in CI/CD pipelines"""

    name: str = "docker"
    description: str = "Build, manage, and deploy Docker containers"

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute Docker operations"""
        self.log_execution("docker", {"action": action, "kwargs": kwargs})

        try:
            if action == "build":
                return self._build_image(
                    kwargs.get("image_name"),
                    kwargs.get("dockerfile", "Dockerfile"),
                    kwargs.get("context", "."),
                    kwargs.get("build_args", {})
                )
            elif action == "push":
                return self._push_image(kwargs.get("image_name"))
            elif action == "pull":
                return self._pull_image(kwargs.get("image_name"))
            elif action == "run":
                return self._run_container(
                    kwargs.get("image_name"),
                    kwargs.get("container_name"),
                    kwargs.get("ports", {}),
                    kwargs.get("environment", {}),
                    kwargs.get("volumes", {})
                )
            elif action == "stop":
                return self._stop_container(kwargs.get("container_name"))
            elif action == "remove":
                return self._remove_container(kwargs.get("container_name"))
            elif action == "images":
                return self._list_images()
            elif action == "containers":
                return self._list_containers()
            elif action == "prune":
                return self._prune_system()
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _build_image(self, image_name: str, dockerfile: str, context: str, build_args: Dict[str, str]) -> Dict[str, Any]:
        """Build Docker image"""
        try:
            if not image_name:
                return {"success": False, "error": "Image name is required"}

            # Prepare build command
            cmd = ["docker", "build", "-t", image_name, "-f", dockerfile]

            # Add build arguments
            for key, value in build_args.items():
                cmd.extend(["--build-arg", f"{key}={value}"])

            # Add context
            cmd.append(context)

            # Execute build
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout for builds
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "image_name": image_name,
                    "message": "Image built successfully",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Build failed: {result.stderr}",
                    "output": result.stdout
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Build timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _push_image(self, image_name: str) -> Dict[str, Any]:
        """Push Docker image to registry"""
        try:
            if not image_name:
                return {"success": False, "error": "Image name is required"}

            result = subprocess.run(
                ["docker", "push", image_name],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "image_name": image_name,
                    "message": "Image pushed successfully",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Push failed: {result.stderr}",
                    "output": result.stdout
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Push timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _pull_image(self, image_name: str) -> Dict[str, Any]:
        """Pull Docker image from registry"""
        try:
            if not image_name:
                return {"success": False, "error": "Image name is required"}

            result = subprocess.run(
                ["docker", "pull", image_name],
                capture_output=True,
                text=True,
                timeout=1800
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "image_name": image_name,
                    "message": "Image pulled successfully",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Pull failed: {result.stderr}",
                    "output": result.stdout
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_container(self, image_name: str, container_name: str = None,
                      ports: Dict[str, str] = None, environment: Dict[str, str] = None,
                      volumes: Dict[str, str] = None) -> Dict[str, Any]:
        """Run Docker container"""
        try:
            if not image_name:
                return {"success": False, "error": "Image name is required"}

            cmd = ["docker", "run", "-d"]

            # Add container name
            if container_name:
                cmd.extend(["--name", container_name])

            # Add port mappings
            if ports:
                for host_port, container_port in ports.items():
                    cmd.extend(["-p", f"{host_port}:{container_port}"])

            # Add environment variables
            if environment:
                for key, value in environment.items():
                    cmd.extend(["-e", f"{key}={value}"])

            # Add volume mounts
            if volumes:
                for host_path, container_path in volumes.items():
                    cmd.extend(["-v", f"{host_path}:{container_path}"])

            # Add image name
            cmd.append(image_name)

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                container_id = result.stdout.strip()
                return {
                    "success": True,
                    "container_id": container_id,
                    "container_name": container_name or container_id[:12],
                    "message": "Container started successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to run container: {result.stderr}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _stop_container(self, container_name: str) -> Dict[str, Any]:
        """Stop Docker container"""
        try:
            if not container_name:
                return {"success": False, "error": "Container name is required"}

            result = subprocess.run(
                ["docker", "stop", container_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "container_name": container_name,
                    "message": "Container stopped successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to stop container: {result.stderr}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _remove_container(self, container_name: str) -> Dict[str, Any]:
        """Remove Docker container"""
        try:
            if not container_name:
                return {"success": False, "error": "Container name is required"}

            result = subprocess.run(
                ["docker", "rm", "-f", container_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "container_name": container_name,
                    "message": "Container removed successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to remove container: {result.stderr}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _list_images(self) -> Dict[str, Any]:
        """List Docker images"""
        try:
            result = subprocess.run(
                ["docker", "images", "--format", "json"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                images = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            image_data = json.loads(line)
                            images.append(image_data)
                        except json.JSONDecodeError:
                            pass

                return {
                    "success": True,
                    "images": images,
                    "count": len(images)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to list images: {result.stderr}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _list_containers(self) -> Dict[str, Any]:
        """List Docker containers"""
        try:
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "json"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            container_data = json.loads(line)
                            containers.append(container_data)
                        except json.JSONDecodeError:
                            pass

                return {
                    "success": True,
                    "containers": containers,
                    "count": len(containers)
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to list containers: {result.stderr}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _prune_system(self) -> Dict[str, Any]:
        """Prune Docker system (remove unused containers, images, networks)"""
        try:
            result = subprocess.run(
                ["docker", "system", "prune", "-f"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Docker system pruned successfully",
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to prune system: {result.stderr}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}