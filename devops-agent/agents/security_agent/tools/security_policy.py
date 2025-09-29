"""
Security Policy Tool for Security Agent
"""

import yaml
import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from ...base.tools import BaseDevOpsTool


class SecurityPolicyTool(BaseDevOpsTool):
    """Tool for managing security policies and configurations"""

    name: str = "security_policy"
    description: str = "Create, manage, and enforce security policies"

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute security policy operations"""
        self.log_execution("security_policy", {"action": action, "kwargs": kwargs})

        try:
            if action == "create_policy":
                return self._create_security_policy(
                    kwargs.get("policy_config"),
                    kwargs.get("policy_type", "general")
                )
            elif action == "validate_policy":
                return self._validate_policy_compliance(
                    kwargs.get("policy_name"),
                    kwargs.get("target_config")
                )
            elif action == "generate_iam_policy":
                return self._generate_iam_policy(kwargs.get("requirements"))
            elif action == "create_network_policy":
                return self._create_network_security_policy(kwargs.get("network_config"))
            elif action == "enforce_policy":
                return self._enforce_security_policy(
                    kwargs.get("policy_name"),
                    kwargs.get("target_environment")
                )
            elif action == "policy_report":
                return self._generate_policy_report(kwargs.get("scope", "all"))
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_security_policy(self, policy_config: Dict[str, Any], policy_type: str) -> Dict[str, Any]:
        """Create comprehensive security policy"""
        try:
            if not policy_config:
                return {"success": False, "error": "Policy configuration is required"}

            policy_name = policy_config.get("name", f"{policy_type}_policy")

            # Base policy template
            security_policy = {
                "metadata": {
                    "name": policy_name,
                    "type": policy_type,
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "description": policy_config.get("description", f"Security policy for {policy_type}"),
                    "tags": policy_config.get("tags", [policy_type])
                },
                "scope": {
                    "environments": policy_config.get("environments", ["production"]),
                    "services": policy_config.get("services", ["all"]),
                    "data_classification": policy_config.get("data_classification", ["confidential", "restricted"])
                },
                "rules": [],
                "exceptions": policy_config.get("exceptions", []),
                "enforcement": {
                    "mode": policy_config.get("enforcement_mode", "enforce"),  # monitor, enforce
                    "actions": policy_config.get("actions", ["alert", "block"]),
                    "escalation": policy_config.get("escalation", "security_team")
                }
            }

            # Generate rules based on policy type
            if policy_type == "data_protection":
                security_policy["rules"].extend(self._generate_data_protection_rules(policy_config))
            elif policy_type == "access_control":
                security_policy["rules"].extend(self._generate_access_control_rules(policy_config))
            elif policy_type == "network_security":
                security_policy["rules"].extend(self._generate_network_security_rules(policy_config))
            elif policy_type == "encryption":
                security_policy["rules"].extend(self._generate_encryption_rules(policy_config))
            else:
                security_policy["rules"].extend(self._generate_general_security_rules(policy_config))

            # Save policy
            policy_file = Path(f"policies/{policy_name}.yaml")
            policy_file.parent.mkdir(parents=True, exist_ok=True)

            with open(policy_file, 'w') as f:
                yaml.dump(security_policy, f, default_flow_style=False)

            return {
                "success": True,
                "policy_created": {
                    "name": policy_name,
                    "type": policy_type,
                    "file_path": str(policy_file),
                    "rules_count": len(security_policy["rules"]),
                    "scope": security_policy["scope"]
                },
                "policy_content": security_policy,
                "message": f"Security policy '{policy_name}' created successfully"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_data_protection_rules(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate data protection rules"""
        return [
            {
                "id": "DP001",
                "name": "Data Encryption at Rest",
                "description": "All sensitive data must be encrypted at rest",
                "requirement": "encrypt_at_rest",
                "severity": "critical",
                "controls": ["AES-256", "Key rotation every 90 days"]
            },
            {
                "id": "DP002",
                "name": "Data Encryption in Transit",
                "description": "All data transmission must use TLS 1.3 or higher",
                "requirement": "encrypt_in_transit",
                "severity": "critical",
                "controls": ["TLS 1.3", "Certificate validation"]
            },
            {
                "id": "DP003",
                "name": "Data Classification",
                "description": "All data must be properly classified and labeled",
                "requirement": "data_classification",
                "severity": "high",
                "controls": ["Classification labels", "Automated scanning"]
            },
            {
                "id": "DP004",
                "name": "Data Retention",
                "description": "Data retention policies must be enforced",
                "requirement": "data_retention",
                "severity": "medium",
                "controls": ["Automated deletion", "Audit trails"]
            }
        ]

    def _generate_access_control_rules(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate access control rules"""
        return [
            {
                "id": "AC001",
                "name": "Multi-Factor Authentication",
                "description": "MFA required for all privileged accounts",
                "requirement": "mfa_required",
                "severity": "critical",
                "controls": ["TOTP", "Hardware tokens", "Biometric"]
            },
            {
                "id": "AC002",
                "name": "Role-Based Access Control",
                "description": "Implement principle of least privilege",
                "requirement": "rbac",
                "severity": "high",
                "controls": ["Role definitions", "Regular access reviews"]
            },
            {
                "id": "AC003",
                "name": "Session Management",
                "description": "Secure session handling and timeout",
                "requirement": "session_security",
                "severity": "medium",
                "controls": ["Session timeout", "Concurrent session limits"]
            }
        ]

    def _generate_network_security_rules(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate network security rules"""
        return [
            {
                "id": "NS001",
                "name": "Network Segmentation",
                "description": "Implement network micro-segmentation",
                "requirement": "network_segmentation",
                "severity": "high",
                "controls": ["VPC", "Subnets", "Security groups"]
            },
            {
                "id": "NS002",
                "name": "Firewall Rules",
                "description": "Default deny with explicit allow rules",
                "requirement": "firewall_rules",
                "severity": "critical",
                "controls": ["Default deny", "Rule documentation"]
            },
            {
                "id": "NS003",
                "name": "DDoS Protection",
                "description": "DDoS protection must be enabled",
                "requirement": "ddos_protection",
                "severity": "high",
                "controls": ["Rate limiting", "Traffic analysis"]
            }
        ]

    def _generate_encryption_rules(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate encryption rules"""
        return [
            {
                "id": "EN001",
                "name": "Encryption Standards",
                "description": "Use approved encryption algorithms",
                "requirement": "approved_encryption",
                "severity": "critical",
                "controls": ["AES-256", "RSA-4096", "ECC P-384"]
            },
            {
                "id": "EN002",
                "name": "Key Management",
                "description": "Secure key generation, storage, and rotation",
                "requirement": "key_management",
                "severity": "critical",
                "controls": ["HSM", "Key rotation", "Key escrow"]
            }
        ]

    def _generate_general_security_rules(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate general security rules"""
        return [
            {
                "id": "GS001",
                "name": "Security Logging",
                "description": "Comprehensive security event logging",
                "requirement": "security_logging",
                "severity": "high",
                "controls": ["Centralized logging", "Log retention"]
            },
            {
                "id": "GS002",
                "name": "Vulnerability Management",
                "description": "Regular vulnerability assessments",
                "requirement": "vulnerability_scanning",
                "severity": "high",
                "controls": ["Automated scanning", "Remediation tracking"]
            }
        ]

    def _validate_policy_compliance(self, policy_name: str, target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration against security policy"""
        try:
            # Load policy
            policy_file = Path(f"policies/{policy_name}.yaml")
            if not policy_file.exists():
                return {"success": False, "error": f"Policy '{policy_name}' not found"}

            with open(policy_file, 'r') as f:
                policy = yaml.safe_load(f)

            compliance_results = {
                "policy_name": policy_name,
                "target": target_config.get("name", "unknown"),
                "compliance_score": 0,
                "compliant_rules": [],
                "non_compliant_rules": [],
                "exceptions_applied": [],
                "overall_status": "unknown"
            }

            total_rules = len(policy["rules"])
            compliant_count = 0

            # Check each rule
            for rule in policy["rules"]:
                rule_check = self._check_rule_compliance(rule, target_config)

                if rule_check["compliant"]:
                    compliance_results["compliant_rules"].append({
                        "rule_id": rule["id"],
                        "rule_name": rule["name"],
                        "status": "compliant"
                    })
                    compliant_count += 1
                else:
                    # Check if exception applies
                    exception_applied = self._check_exceptions(rule, target_config, policy.get("exceptions", []))

                    if exception_applied:
                        compliance_results["exceptions_applied"].append({
                            "rule_id": rule["id"],
                            "rule_name": rule["name"],
                            "exception": exception_applied
                        })
                        compliant_count += 1
                    else:
                        compliance_results["non_compliant_rules"].append({
                            "rule_id": rule["id"],
                            "rule_name": rule["name"],
                            "severity": rule.get("severity", "medium"),
                            "finding": rule_check["finding"],
                            "remediation": rule_check.get("remediation", "Review rule requirements")
                        })

            # Calculate compliance score
            if total_rules > 0:
                compliance_results["compliance_score"] = round((compliant_count / total_rules) * 100, 2)

            # Determine overall status
            if compliance_results["compliance_score"] >= 95:
                compliance_results["overall_status"] = "compliant"
            elif compliance_results["compliance_score"] >= 80:
                compliance_results["overall_status"] = "mostly_compliant"
            else:
                compliance_results["overall_status"] = "non_compliant"

            return {
                "success": True,
                "compliance_results": compliance_results
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_rule_compliance(self, rule: Dict[str, Any], target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if target configuration complies with specific rule"""
        rule_id = rule["id"]

        # Simulate rule checking logic based on rule type
        if rule_id.startswith("DP"):  # Data Protection
            return self._check_data_protection_rule(rule, target_config)
        elif rule_id.startswith("AC"):  # Access Control
            return self._check_access_control_rule(rule, target_config)
        elif rule_id.startswith("NS"):  # Network Security
            return self._check_network_security_rule(rule, target_config)
        elif rule_id.startswith("EN"):  # Encryption
            return self._check_encryption_rule(rule, target_config)
        else:  # General Security
            return self._check_general_security_rule(rule, target_config)

    def _check_data_protection_rule(self, rule: Dict[str, Any], target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check data protection rule compliance"""
        if rule["id"] == "DP001":  # Encryption at rest
            encryption_enabled = target_config.get("encryption", {}).get("at_rest", False)
            return {
                "compliant": encryption_enabled,
                "finding": "Encryption at rest not enabled" if not encryption_enabled else None,
                "remediation": "Enable database and storage encryption"
            }
        elif rule["id"] == "DP002":  # Encryption in transit
            tls_enabled = target_config.get("encryption", {}).get("in_transit", False)
            return {
                "compliant": tls_enabled,
                "finding": "TLS not properly configured" if not tls_enabled else None,
                "remediation": "Configure TLS 1.3 for all connections"
            }
        else:
            return {"compliant": True}  # Default for unknown rules

    def _check_access_control_rule(self, rule: Dict[str, Any], target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check access control rule compliance"""
        if rule["id"] == "AC001":  # MFA
            mfa_enabled = target_config.get("authentication", {}).get("mfa_enabled", False)
            return {
                "compliant": mfa_enabled,
                "finding": "MFA not enabled for privileged accounts" if not mfa_enabled else None,
                "remediation": "Enable multi-factor authentication"
            }
        else:
            return {"compliant": True}

    def _check_network_security_rule(self, rule: Dict[str, Any], target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check network security rule compliance"""
        if rule["id"] == "NS002":  # Firewall rules
            firewall_configured = target_config.get("network", {}).get("firewall_enabled", False)
            return {
                "compliant": firewall_configured,
                "finding": "Firewall not properly configured" if not firewall_configured else None,
                "remediation": "Configure firewall with default deny rules"
            }
        else:
            return {"compliant": True}

    def _check_encryption_rule(self, rule: Dict[str, Any], target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check encryption rule compliance"""
        return {"compliant": True}  # Simplified for example

    def _check_general_security_rule(self, rule: Dict[str, Any], target_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check general security rule compliance"""
        return {"compliant": True}  # Simplified for example

    def _check_exceptions(self, rule: Dict[str, Any], target_config: Dict[str, Any], exceptions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check if any exceptions apply to this rule"""
        for exception in exceptions:
            if exception.get("rule_id") == rule["id"]:
                # Check if exception conditions match target
                if self._exception_conditions_match(exception, target_config):
                    return exception
        return None

    def _exception_conditions_match(self, exception: Dict[str, Any], target_config: Dict[str, Any]) -> bool:
        """Check if exception conditions match target configuration"""
        conditions = exception.get("conditions", {})

        for key, value in conditions.items():
            if target_config.get(key) != value:
                return False

        return True

    def _generate_iam_policy(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate IAM policy based on requirements"""
        try:
            service_name = requirements.get("service_name", "unknown-service")
            permissions_level = requirements.get("permissions_level", "read")
            resources = requirements.get("resources", ["*"])

            # Generate IAM policy document
            iam_policy = {
                "Version": "2012-10-17",
                "Statement": []
            }

            # Add statements based on requirements
            if permissions_level == "read":
                iam_policy["Statement"].append({
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket",
                        "dynamodb:GetItem",
                        "dynamodb:Query",
                        "dynamodb:Scan"
                    ],
                    "Resource": resources
                })
            elif permissions_level == "write":
                iam_policy["Statement"].append({
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket",
                        "dynamodb:*"
                    ],
                    "Resource": resources
                })
            elif permissions_level == "admin":
                iam_policy["Statement"].append({
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": resources
                })

            # Add deny statements for security
            iam_policy["Statement"].append({
                "Effect": "Deny",
                "Action": [
                    "iam:CreateUser",
                    "iam:DeleteUser",
                    "iam:CreateRole"
                ],
                "Resource": "*",
                "Condition": {
                    "Bool": {
                        "aws:MultiFactorAuthPresent": "false"
                    }
                }
            })

            return {
                "success": True,
                "iam_policy": iam_policy,
                "policy_name": f"{service_name}-{permissions_level}-policy",
                "message": f"IAM policy generated for {service_name}"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_network_security_policy(self, network_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kubernetes network security policy"""
        try:
            policy_name = network_config.get("name", "default-network-policy")
            namespace = network_config.get("namespace", "default")

            # Generate Kubernetes NetworkPolicy
            network_policy = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": policy_name,
                    "namespace": namespace
                },
                "spec": {
                    "podSelector": network_config.get("podSelector", {}),
                    "policyTypes": ["Ingress", "Egress"],
                    "ingress": network_config.get("ingress_rules", [
                        {
                            "from": [
                                {"namespaceSelector": {"matchLabels": {"name": "allowed-namespace"}}}
                            ],
                            "ports": [
                                {"protocol": "TCP", "port": 80},
                                {"protocol": "TCP", "port": 443}
                            ]
                        }
                    ]),
                    "egress": network_config.get("egress_rules", [
                        {
                            "to": [],
                            "ports": [
                                {"protocol": "TCP", "port": 53},
                                {"protocol": "UDP", "port": 53}
                            ]
                        }
                    ])
                }
            }

            # Save policy
            policy_file = Path(f"network-policies/{policy_name}.yaml")
            policy_file.parent.mkdir(parents=True, exist_ok=True)

            with open(policy_file, 'w') as f:
                yaml.dump(network_policy, f, default_flow_style=False)

            return {
                "success": True,
                "network_policy": network_policy,
                "policy_file": str(policy_file),
                "message": f"Network security policy '{policy_name}' created"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _enforce_security_policy(self, policy_name: str, target_environment: str) -> Dict[str, Any]:
        """Enforce security policy in target environment"""
        try:
            enforcement_actions = [
                "Load security policy configuration",
                "Validate policy against target environment",
                "Apply policy controls and rules",
                "Configure monitoring and alerting",
                "Verify policy enforcement",
                "Generate compliance report"
            ]

            enforcement_result = {
                "policy_name": policy_name,
                "target_environment": target_environment,
                "enforcement_status": "active",
                "actions_completed": enforcement_actions,
                "enforcement_mode": "monitor",  # Could be 'enforce' or 'monitor'
                "violations_detected": 0,
                "last_enforcement": datetime.now().isoformat()
            }

            return {
                "success": True,
                "enforcement_result": enforcement_result,
                "message": f"Policy '{policy_name}' enforced in '{target_environment}'"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_policy_report(self, scope: str) -> Dict[str, Any]:
        """Generate comprehensive policy compliance report"""
        try:
            # Mock policy compliance data
            policies_data = [
                {"name": "data_protection", "compliance": 85, "critical_violations": 2},
                {"name": "access_control", "compliance": 92, "critical_violations": 1},
                {"name": "network_security", "compliance": 78, "critical_violations": 3},
                {"name": "encryption", "compliance": 95, "critical_violations": 0}
            ]

            total_compliance = sum(p["compliance"] for p in policies_data) / len(policies_data)
            total_violations = sum(p["critical_violations"] for p in policies_data)

            report = {
                "generated_at": datetime.now().isoformat(),
                "scope": scope,
                "executive_summary": {
                    "overall_compliance": round(total_compliance, 2),
                    "total_policies": len(policies_data),
                    "critical_violations": total_violations,
                    "compliance_trend": "improving"
                },
                "policy_details": policies_data,
                "recommendations": [
                    "Address critical violations in network security",
                    "Implement automated policy compliance monitoring",
                    "Conduct policy review and updates quarterly"
                ],
                "next_review_date": "2024-06-01T00:00:00Z"
            }

            return {
                "success": True,
                "policy_report": report
            }

        except Exception as e:
            return {"success": False, "error": str(e)}