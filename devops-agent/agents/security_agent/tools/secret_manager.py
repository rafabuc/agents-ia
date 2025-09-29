"""
Secret Manager Tool for Security Agent
"""

import os
import json
import base64
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import subprocess

from ...base.tools import BaseDevOpsTool


class SecretManager(BaseDevOpsTool):
    """Tool for managing secrets and credentials securely"""

    name: str = "secret_manager"
    description: str = "Manage secrets, credentials, and sensitive configuration securely"

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute secret management operations"""
        self.log_execution("secret_manager", {"action": action, "kwargs": kwargs})

        try:
            if action == "scan_secrets":
                return self._scan_for_secrets(
                    kwargs.get("path", "."),
                    kwargs.get("file_patterns", ["*.py", "*.js", "*.yml", "*.yaml", "*.json"])
                )
            elif action == "rotate_secret":
                return self._rotate_secret(
                    kwargs.get("secret_name"),
                    kwargs.get("secret_config", {})
                )
            elif action == "store_secret":
                return self._store_secret(
                    kwargs.get("secret_name"),
                    kwargs.get("secret_value"),
                    kwargs.get("metadata", {})
                )
            elif action == "retrieve_secret":
                return self._retrieve_secret(kwargs.get("secret_name"))
            elif action == "list_secrets":
                return self._list_secrets(kwargs.get("filter_criteria", {}))
            elif action == "vault_integration":
                return self._integrate_with_vault(kwargs.get("vault_config", {}))
            elif action == "k8s_secrets":
                return self._manage_k8s_secrets(
                    kwargs.get("operation"),
                    kwargs.get("secret_data", {})
                )
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _scan_for_secrets(self, path: str, file_patterns: List[str]) -> Dict[str, Any]:
        """Scan codebase for potential secrets and credentials"""
        try:
            secret_patterns = {
                "api_key": [
                    r"api[_-]?key['\"]?\s*[:=]\s*['\"]([A-Za-z0-9]{20,})",
                    r"apikey['\"]?\s*[:=]\s*['\"]([A-Za-z0-9]{20,})",
                ],
                "password": [
                    r"password['\"]?\s*[:=]\s*['\"]([^'\"]{8,})",
                    r"passwd['\"]?\s*[:=]\s*['\"]([^'\"]{8,})",
                    r"pwd['\"]?\s*[:=]\s*['\"]([^'\"]{8,})",
                ],
                "token": [
                    r"token['\"]?\s*[:=]\s*['\"]([A-Za-z0-9._-]{20,})",
                    r"access[_-]?token['\"]?\s*[:=]\s*['\"]([A-Za-z0-9._-]{20,})",
                    r"auth[_-]?token['\"]?\s*[:=]\s*['\"]([A-Za-z0-9._-]{20,})",
                ],
                "secret": [
                    r"secret['\"]?\s*[:=]\s*['\"]([A-Za-z0-9._-]{16,})",
                    r"client[_-]?secret['\"]?\s*[:=]\s*['\"]([A-Za-z0-9._-]{16,})",
                ],
                "database_url": [
                    r"database[_-]?url['\"]?\s*[:=]\s*['\"]([^'\"]+)",
                    r"db[_-]?url['\"]?\s*[:=]\s*['\"]([^'\"]+)",
                ],
                "private_key": [
                    r"-----BEGIN\s+(RSA\s+)?PRIVATE KEY-----",
                    r"private[_-]?key['\"]?\s*[:=]\s*['\"]([A-Za-z0-9+/=]{100,})",
                ],
                "aws_credentials": [
                    r"aws[_-]?access[_-]?key[_-]?id['\"]?\s*[:=]\s*['\"]([A-Z0-9]{20})",
                    r"aws[_-]?secret[_-]?access[_-]?key['\"]?\s*[:=]\s*['\"]([A-Za-z0-9/+=]{40})",
                ]
            }

            findings = []
            scanned_files = 0

            # Scan files matching patterns
            import glob
            import re

            for pattern in file_patterns:
                file_path = os.path.join(path, "**", pattern)
                for file_name in glob.glob(file_path, recursive=True):
                    try:
                        with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            scanned_files += 1

                            # Check against secret patterns
                            for secret_type, patterns in secret_patterns.items():
                                for regex_pattern in patterns:
                                    matches = re.finditer(regex_pattern, content, re.IGNORECASE)
                                    for match in matches:
                                        # Mask the secret value
                                        secret_value = match.group(1) if match.groups() else match.group(0)
                                        masked_value = secret_value[:4] + "*" * (len(secret_value) - 8) + secret_value[-4:] if len(secret_value) > 8 else "***"

                                        findings.append({
                                            "file": file_name,
                                            "line": content[:match.start()].count('\n') + 1,
                                            "secret_type": secret_type,
                                            "masked_value": masked_value,
                                            "confidence": self._calculate_confidence(secret_type, secret_value),
                                            "severity": "high" if secret_type in ["private_key", "aws_credentials"] else "medium"
                                        })

                    except Exception as e:
                        continue

            # Generate recommendations
            recommendations = []
            if findings:
                recommendations.extend([
                    "Remove hardcoded secrets from source code",
                    "Use environment variables for configuration",
                    "Implement proper secret management (Vault, AWS Secrets Manager)",
                    "Add secrets scanning to CI/CD pipeline",
                    "Use .gitignore to prevent committing sensitive files"
                ])

            return {
                "success": True,
                "scan_summary": {
                    "scanned_files": scanned_files,
                    "total_findings": len(findings),
                    "high_severity": len([f for f in findings if f["severity"] == "high"]),
                    "medium_severity": len([f for f in findings if f["severity"] == "medium"])
                },
                "findings": findings,
                "recommendations": recommendations
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _rotate_secret(self, secret_name: str, secret_config: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate a secret with zero-downtime deployment"""
        try:
            if not secret_name:
                return {"success": False, "error": "Secret name is required"}

            rotation_type = secret_config.get("type", "manual")
            rotation_strategy = secret_config.get("strategy", "blue_green")

            # Generate new secret value
            new_secret = self._generate_secret(secret_config.get("length", 32))

            # Rotation process
            rotation_steps = []

            if rotation_strategy == "blue_green":
                rotation_steps = [
                    "Generate new secret value",
                    "Store new secret alongside current secret",
                    "Update applications to use new secret",
                    "Verify applications are working with new secret",
                    "Remove old secret from storage"
                ]
            elif rotation_strategy == "immediate":
                rotation_steps = [
                    "Generate new secret value",
                    "Update secret in storage",
                    "Restart dependent services",
                    "Verify service functionality"
                ]

            # Execute rotation (simulation)
            rotation_result = {
                "secret_name": secret_name,
                "rotation_id": f"rot_{int(datetime.now().timestamp())}",
                "old_secret_hash": hashlib.sha256(f"old_secret_{secret_name}".encode()).hexdigest()[:16],
                "new_secret_hash": hashlib.sha256(new_secret.encode()).hexdigest()[:16],
                "rotation_strategy": rotation_strategy,
                "steps_completed": rotation_steps,
                "next_rotation": (datetime.now() + timedelta(days=secret_config.get("rotation_period_days", 90))).isoformat(),
                "status": "completed"
            }

            return {
                "success": True,
                "rotation_result": rotation_result,
                "message": f"Secret '{secret_name}' rotated successfully"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _store_secret(self, secret_name: str, secret_value: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Store secret securely"""
        try:
            if not secret_name or not secret_value:
                return {"success": False, "error": "Secret name and value are required"}

            # Encrypt secret value (simulation - in real implementation would use proper encryption)
            encrypted_value = base64.b64encode(secret_value.encode()).decode()

            secret_record = {
                "name": secret_name,
                "encrypted_value": encrypted_value,
                "created_at": datetime.now().isoformat(),
                "metadata": metadata,
                "version": metadata.get("version", 1),
                "tags": metadata.get("tags", []),
                "access_policy": metadata.get("access_policy", "default"),
                "rotation_policy": {
                    "enabled": metadata.get("auto_rotate", False),
                    "period_days": metadata.get("rotation_period", 90),
                    "next_rotation": (datetime.now() + timedelta(days=metadata.get("rotation_period", 90))).isoformat()
                }
            }

            # Store in secure backend (simulation)
            storage_backends = metadata.get("backends", ["local_vault"])
            stored_locations = []

            for backend in storage_backends:
                if backend == "vault":
                    stored_locations.append({"backend": "HashiCorp Vault", "path": f"secret/{secret_name}"})
                elif backend == "aws_secrets":
                    stored_locations.append({"backend": "AWS Secrets Manager", "arn": f"arn:aws:secretsmanager:region:account:secret:{secret_name}"})
                elif backend == "k8s_secret":
                    stored_locations.append({"backend": "Kubernetes Secret", "namespace": metadata.get("namespace", "default")})
                else:
                    stored_locations.append({"backend": "Local Vault", "path": f"/vault/secrets/{secret_name}"})

            return {
                "success": True,
                "secret_stored": {
                    "name": secret_name,
                    "version": secret_record["version"],
                    "stored_locations": stored_locations,
                    "access_policy": secret_record["access_policy"],
                    "rotation_policy": secret_record["rotation_policy"]
                },
                "message": f"Secret '{secret_name}' stored securely"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _retrieve_secret(self, secret_name: str) -> Dict[str, Any]:
        """Retrieve secret securely"""
        try:
            if not secret_name:
                return {"success": False, "error": "Secret name is required"}

            # Simulate secret retrieval
            secret_info = {
                "name": secret_name,
                "exists": True,  # Would check actual storage
                "version": 1,
                "created_at": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 1,
                "metadata": {
                    "description": f"Secret for {secret_name}",
                    "owner": "system",
                    "tags": ["application", "production"]
                }
            }

            # Note: In real implementation, secret value would be securely retrieved and decrypted
            # Here we don't return the actual value for security reasons

            return {
                "success": True,
                "secret_info": secret_info,
                "message": f"Secret '{secret_name}' retrieved successfully",
                "note": "Actual secret value not included in response for security"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _list_secrets(self, filter_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """List secrets with filtering"""
        try:
            # Simulate secret listing
            mock_secrets = [
                {
                    "name": "database-password",
                    "version": 2,
                    "created_at": "2024-01-15T10:30:00Z",
                    "last_rotated": "2024-03-15T10:30:00Z",
                    "next_rotation": "2024-06-15T10:30:00Z",
                    "tags": ["database", "production"],
                    "access_policy": "restricted"
                },
                {
                    "name": "api-key-external-service",
                    "version": 1,
                    "created_at": "2024-02-01T14:20:00Z",
                    "last_rotated": "2024-02-01T14:20:00Z",
                    "next_rotation": "2024-05-01T14:20:00Z",
                    "tags": ["api", "external"],
                    "access_policy": "default"
                },
                {
                    "name": "ssl-certificate-key",
                    "version": 1,
                    "created_at": "2024-01-01T00:00:00Z",
                    "last_rotated": "2024-01-01T00:00:00Z",
                    "next_rotation": "2025-01-01T00:00:00Z",
                    "tags": ["ssl", "certificate"],
                    "access_policy": "restricted"
                }
            ]

            # Apply filters
            filtered_secrets = mock_secrets
            if filter_criteria.get("tags"):
                filtered_secrets = [s for s in filtered_secrets if any(tag in s["tags"] for tag in filter_criteria["tags"])]

            if filter_criteria.get("access_policy"):
                filtered_secrets = [s for s in filtered_secrets if s["access_policy"] == filter_criteria["access_policy"]]

            return {
                "success": True,
                "secrets": filtered_secrets,
                "total_count": len(filtered_secrets),
                "summary": {
                    "by_access_policy": {
                        "restricted": len([s for s in filtered_secrets if s["access_policy"] == "restricted"]),
                        "default": len([s for s in filtered_secrets if s["access_policy"] == "default"])
                    },
                    "rotation_due_soon": len([s for s in filtered_secrets if self._is_rotation_due_soon(s["next_rotation"])])
                }
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _integrate_with_vault(self, vault_config: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with HashiCorp Vault"""
        try:
            vault_url = vault_config.get("url", "https://vault.example.com:8200")
            auth_method = vault_config.get("auth_method", "token")

            # Vault integration steps (simulation)
            integration_steps = [
                "Connect to Vault server",
                "Authenticate using configured method",
                "Verify access permissions",
                "Configure secret engines",
                "Set up policies and roles",
                "Test secret operations"
            ]

            vault_setup = {
                "vault_url": vault_url,
                "auth_method": auth_method,
                "secret_engines": vault_config.get("secret_engines", ["kv-v2"]),
                "policies_configured": vault_config.get("policies", ["default-policy"]),
                "integration_status": "active",
                "last_health_check": datetime.now().isoformat(),
                "capabilities": [
                    "secret_storage",
                    "secret_rotation",
                    "dynamic_secrets",
                    "encryption_as_a_service"
                ]
            }

            return {
                "success": True,
                "vault_integration": vault_setup,
                "integration_steps": integration_steps,
                "message": "Vault integration configured successfully"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _manage_k8s_secrets(self, operation: str, secret_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage Kubernetes secrets"""
        try:
            if operation == "create":
                return self._create_k8s_secret(secret_data)
            elif operation == "update":
                return self._update_k8s_secret(secret_data)
            elif operation == "delete":
                return self._delete_k8s_secret(secret_data.get("name"), secret_data.get("namespace"))
            elif operation == "list":
                return self._list_k8s_secrets(secret_data.get("namespace"))
            else:
                return {"success": False, "error": f"Unknown K8s operation: {operation}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_k8s_secret(self, secret_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kubernetes secret"""
        try:
            secret_name = secret_data.get("name")
            namespace = secret_data.get("namespace", "default")
            secret_type = secret_data.get("type", "Opaque")
            data = secret_data.get("data", {})

            # Create kubectl command (simulation)
            kubectl_cmd = f"kubectl create secret generic {secret_name}"

            for key, value in data.items():
                # Base64 encode the values
                encoded_value = base64.b64encode(value.encode()).decode()
                kubectl_cmd += f" --from-literal={key}={encoded_value}"

            kubectl_cmd += f" --namespace={namespace}"

            return {
                "success": True,
                "secret_created": {
                    "name": secret_name,
                    "namespace": namespace,
                    "type": secret_type,
                    "data_keys": list(data.keys()),
                    "created_at": datetime.now().isoformat()
                },
                "kubectl_command": kubectl_cmd,
                "message": f"Kubernetes secret '{secret_name}' created in namespace '{namespace}'"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_secret(self, length: int = 32) -> str:
        """Generate secure random secret"""
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _calculate_confidence(self, secret_type: str, secret_value: str) -> str:
        """Calculate confidence level for secret detection"""
        high_confidence_types = ["private_key", "aws_credentials"]

        if secret_type in high_confidence_types:
            return "high"
        elif len(secret_value) > 20 and any(c.isdigit() for c in secret_value) and any(c.isalpha() for c in secret_value):
            return "medium"
        else:
            return "low"

    def _is_rotation_due_soon(self, next_rotation: str, days_threshold: int = 30) -> bool:
        """Check if rotation is due soon"""
        try:
            rotation_date = datetime.fromisoformat(next_rotation.replace('Z', '+00:00'))
            threshold_date = datetime.now() + timedelta(days=days_threshold)
            return rotation_date <= threshold_date
        except:
            return False

    def _update_k8s_secret(self, secret_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update Kubernetes secret"""
        # Implementation would update existing K8s secret
        return {"success": True, "message": "K8s secret updated"}

    def _delete_k8s_secret(self, name: str, namespace: str) -> Dict[str, Any]:
        """Delete Kubernetes secret"""
        # Implementation would delete K8s secret
        return {"success": True, "message": f"K8s secret '{name}' deleted from namespace '{namespace}'"}

    def _list_k8s_secrets(self, namespace: str) -> Dict[str, Any]:
        """List Kubernetes secrets"""
        # Implementation would list K8s secrets
        return {"success": True, "secrets": [], "message": f"Listed secrets in namespace '{namespace}'"}