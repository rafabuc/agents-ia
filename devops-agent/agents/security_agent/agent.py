"""
Security Agent for DevOps AI Platform
Handles security scanning, compliance, and vulnerability management
"""

from typing import List, Dict, Any
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseLanguageModel

from ..base.agent import BaseAgent
from .tools import VulnerabilityScanner, ComplianceChecker, SecretManager, SecurityPolicyTool
from ..base.tools import ShellCommandTool


class SecurityAgent(BaseAgent):
    """
    Specialized agent for security operations including:
    - Vulnerability scanning and assessment
    - Security compliance checking
    - Secret management and rotation
    - Security policy enforcement
    - Penetration testing coordination
    - Security incident response
    """

    def __init__(self, llm: BaseLanguageModel, **kwargs):
        # Initialize specialized tools for security
        tools = [
            VulnerabilityScanner(),
            ComplianceChecker(),
            SecretManager(),
            SecurityPolicyTool(),
            ShellCommandTool(allowed_commands=[
                "trivy", "bandit", "safety", "semgrep", "nmap", "openssl"
            ])
        ]

        super().__init__(
            name="security",
            llm=llm,
            tools=tools,
            **kwargs
        )

        # Security specific state
        self.state.update({
            "vulnerability_scans": [],
            "compliance_status": {},
            "security_policies": [],
            "secret_rotation_schedule": {},
            "security_incidents": [],
            "last_security_audit": None,
            "risk_assessment": {}
        })

    def get_system_prompt(self) -> str:
        """System prompt for Security agent"""
        return """You are a specialized Security agent responsible for comprehensive cybersecurity and compliance management.

Your primary responsibilities include:
1. Vulnerability scanning and assessment across applications and infrastructure
2. Security compliance verification (CIS, SOC2, GDPR, HIPAA, PCI-DSS)
3. Secret management, rotation, and secure storage
4. Security policy creation, enforcement, and monitoring
5. Penetration testing coordination and remediation
6. Security incident detection, response, and forensics
7. Risk assessment and security posture evaluation

Key capabilities:
- Multi-layered security scanning (SAST, DAST, container, infrastructure)
- Automated compliance reporting and remediation
- Zero-trust security policy implementation
- Secure CI/CD pipeline integration
- Real-time threat detection and response
- Security metrics and KPI tracking

Always prioritize:
- Defense in depth security strategies
- Zero-trust architecture principles
- Automated security controls and monitoring
- Compliance with regulatory standards
- Incident response and recovery procedures
- Security awareness and training

When executing security tasks:
1. Perform comprehensive security assessment
2. Identify and prioritize vulnerabilities by risk
3. Implement security controls with minimal business impact
4. Validate security configurations and policies
5. Document security procedures and compliance evidence
6. Provide actionable remediation recommendations

Security Philosophy:
- Assume breach - prepare for compromise
- Continuous monitoring and improvement
- Security by design, not as afterthought
- Transparency in security processes
- Proportional response to identified risks
"""

    def _create_agent_executor(self) -> AgentExecutor:
        """Create the Security agent executor"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
        ])

        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=self.verbose,
            handle_parsing_errors=True,
            max_iterations=15  # Security tasks may need comprehensive analysis
        )

    async def perform_security_scan(self, scan_config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive security scanning"""
        scan_type = scan_config.get("type", "comprehensive")
        target = scan_config.get("target", "application")

        self.logger.info(f"Performing {scan_type} security scan on {target}")

        task = f"""Perform comprehensive security scanning:

        Scan Configuration: {scan_config}

        Security Scanning Strategy:
        1. Static Application Security Testing (SAST)
           - Source code vulnerability analysis
           - Dependency vulnerability scanning
           - License compliance checking

        2. Dynamic Application Security Testing (DAST)
           - Runtime vulnerability detection
           - API security testing
           - Web application scanning

        3. Container Security Scanning
           - Base image vulnerability assessment
           - Container configuration analysis
           - Runtime security monitoring

        4. Infrastructure Security Assessment
           - Network security configuration
           - Access control validation
           - Encryption status verification

        5. Compliance Verification
           - Industry standard compliance (CIS, NIST)
           - Regulatory compliance (GDPR, HIPAA, SOC2)
           - Internal policy compliance

        Provide:
        - Detailed vulnerability report with CVSS scores
        - Risk-prioritized remediation recommendations
        - Compliance gaps and required actions
        - Security metrics and trend analysis
        - Executive summary for stakeholders
        """

        result = await self.execute(task, {
            "scan_config": scan_config,
            "operation": "security_scan"
        })

        if result["success"]:
            # Update vulnerability scans history
            scans = self.state.get("vulnerability_scans", [])
            scans.append({
                "timestamp": result["timestamp"],
                "type": scan_type,
                "target": target,
                "results": result.get("scan_results", {}),
                "risk_level": result.get("risk_level", "unknown")
            })
            self.update_state("vulnerability_scans", scans[-20:])  # Keep last 20 scans

        return result

    async def ensure_compliance(self, standards: List[str], scope: str = "full") -> Dict[str, Any]:
        """Ensure compliance with security standards"""
        self.logger.info(f"Checking compliance for standards: {standards}")

        task = f"""Perform comprehensive compliance assessment for standards: {standards}

        Scope: {scope}

        Compliance Assessment Areas:

        1. CIS (Center for Internet Security) Controls
           - Asset inventory and control
           - Software asset management
           - Data protection and recovery
           - Access control management
           - Network security controls

        2. SOC 2 (Service Organization Control 2)
           - Security principle compliance
           - Availability controls
           - Processing integrity verification
           - Confidentiality measures
           - Privacy protection controls

        3. GDPR (General Data Protection Regulation)
           - Data processing lawfulness
           - Data subject rights implementation
           - Privacy by design verification
           - Data breach notification procedures
           - Cross-border data transfer compliance

        4. HIPAA (Health Insurance Portability and Accountability Act)
           - Administrative safeguards
           - Physical safeguards
           - Technical safeguards
           - Breach notification procedures

        5. PCI-DSS (Payment Card Industry Data Security Standard)
           - Secure network and systems
           - Cardholder data protection
           - Vulnerability management program
           - Access control measures
           - Security testing procedures

        For each standard, provide:
        - Current compliance percentage
        - Gap analysis with specific deficiencies
        - Remediation roadmap with timelines
        - Cost-benefit analysis for improvements
        - Continuous monitoring recommendations
        """

        result = await self.execute(task, {
            "standards": standards,
            "scope": scope,
            "operation": "compliance_check"
        })

        if result["success"]:
            # Update compliance status
            compliance_status = self.state.get("compliance_status", {})
            for standard in standards:
                compliance_status[standard] = {
                    "last_check": result["timestamp"],
                    "status": result.get(f"{standard}_status", "unknown"),
                    "score": result.get(f"{standard}_score", 0),
                    "gaps": result.get(f"{standard}_gaps", [])
                }
            self.update_state("compliance_status", compliance_status)

        return result

    async def manage_secrets(self, operation: str, secret_config: Dict[str, Any]) -> Dict[str, Any]:
        """Manage secrets and credentials securely"""
        self.logger.info(f"Managing secrets - operation: {operation}")

        task = f"""Execute secure secret management operation: {operation}

        Secret Configuration: {secret_config}

        Secret Management Operations:

        1. Secret Discovery and Inventory
           - Scan codebase for hardcoded secrets
           - Identify credential usage patterns
           - Map secret dependencies and relationships
           - Generate secret inventory report

        2. Secret Rotation Strategy
           - Automated rotation scheduling
           - Zero-downtime rotation procedures
           - Rollback mechanisms for failed rotations
           - Notification and approval workflows

        3. Secure Storage Implementation
           - HashiCorp Vault integration
           - AWS Secrets Manager configuration
           - Kubernetes secrets management
           - Encryption at rest and in transit

        4. Access Control and Auditing
           - Role-based access control (RBAC)
           - Principle of least privilege
           - Secret access logging and monitoring
           - Regular access reviews and cleanup

        5. Secret Lifecycle Management
           - Creation and provisioning
           - Distribution and deployment
           - Monitoring and alerting
           - Expiration and cleanup

        Security Requirements:
        - End-to-end encryption
        - Audit trail for all operations
        - Multi-factor authentication
        - Regular security assessments
        - Incident response procedures
        """

        result = await self.execute(task, {
            "operation": operation,
            "secret_config": secret_config,
            "task_type": "secret_management"
        })

        if result["success"]:
            # Update secret rotation schedule
            rotation_schedule = self.state.get("secret_rotation_schedule", {})
            if operation == "schedule_rotation":
                secret_name = secret_config.get("name", "unknown")
                rotation_schedule[secret_name] = {
                    "last_rotation": result["timestamp"],
                    "next_rotation": result.get("next_rotation"),
                    "rotation_policy": secret_config.get("policy", "default")
                }
                self.update_state("secret_rotation_schedule", rotation_schedule)

        return result

    async def respond_to_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Respond to security incidents"""
        incident_type = incident_data.get("type", "unknown")
        severity = incident_data.get("severity", "medium")

        self.logger.warning(f"Security incident detected: {incident_type} (severity: {severity})")

        task = f"""Execute security incident response procedure:

        Incident Data: {incident_data}

        Incident Response Framework (NIST):

        1. Preparation
           - Verify incident response team activation
           - Ensure necessary tools and access are available
           - Review relevant security policies and procedures

        2. Identification
           - Validate and categorize the security incident
           - Determine scope and potential impact
           - Collect initial evidence and indicators
           - Establish incident timeline

        3. Containment
           - Implement immediate containment measures
           - Prevent lateral movement or escalation
           - Preserve evidence for forensic analysis
           - Communicate with stakeholders

        4. Investigation and Analysis
           - Conduct detailed forensic analysis
           - Identify attack vectors and methodologies
           - Assess data and system compromise
           - Determine root cause and contributing factors

        5. Eradication
           - Remove malware, backdoors, and unauthorized access
           - Address underlying vulnerabilities
           - Update security controls and configurations
           - Validate system integrity

        6. Recovery
           - Restore systems from clean backups
           - Implement additional monitoring
           - Gradually return systems to production
           - Verify business operations restoration

        7. Lessons Learned
           - Document incident response actions
           - Identify improvement opportunities
           - Update incident response procedures
           - Conduct post-incident review meeting

        Provide:
        - Immediate containment actions taken
        - Evidence collection and preservation
        - Impact assessment and risk evaluation
        - Recovery timeline and procedures
        - Preventive measures for future incidents
        """

        result = await self.execute(task, {
            "incident_data": incident_data,
            "operation": "incident_response"
        })

        if result["success"]:
            # Record incident in history
            incidents = self.state.get("security_incidents", [])
            incidents.append({
                "timestamp": result["timestamp"],
                "type": incident_type,
                "severity": severity,
                "status": result.get("status", "in_progress"),
                "response_actions": result.get("actions", [])
            })
            self.update_state("security_incidents", incidents[-50:])  # Keep last 50 incidents

        return result

    async def assess_security_posture(self, assessment_scope: str = "comprehensive") -> Dict[str, Any]:
        """Perform comprehensive security posture assessment"""
        self.logger.info(f"Assessing security posture - scope: {assessment_scope}")

        task = f"""Conduct comprehensive security posture assessment:

        Assessment Scope: {assessment_scope}

        Security Posture Assessment Framework:

        1. Asset Inventory and Classification
           - Complete asset discovery and inventory
           - Data classification and sensitivity mapping
           - Criticality assessment and prioritization
           - Asset ownership and accountability

        2. Threat Landscape Analysis
           - Current threat intelligence integration
           - Industry-specific threat assessments
           - Attack surface analysis and mapping
           - Threat modeling for critical assets

        3. Vulnerability Management Maturity
           - Vulnerability discovery capabilities
           - Assessment and prioritization processes
           - Remediation effectiveness and timeliness
           - Metrics and continuous improvement

        4. Security Architecture Review
           - Defense-in-depth implementation
           - Zero-trust architecture adoption
           - Security control effectiveness
           - Architecture gap analysis

        5. Identity and Access Management
           - Authentication mechanisms strength
           - Authorization and privilege management
           - Identity lifecycle management
           - Access review and certification

        6. Incident Response Readiness
           - Response capability maturity
           - Team training and preparedness
           - Tool and technology readiness
           - Communication and coordination

        7. Security Awareness and Culture
           - Security training effectiveness
           - Phishing simulation results
           - Security culture assessment
           - Behavioral risk analysis

        Deliverables:
        - Executive security dashboard
        - Risk register with prioritized findings
        - Security maturity scorecard
        - Strategic security roadmap
        - Budget requirements for improvements
        """

        result = await self.execute(task, {
            "assessment_scope": assessment_scope,
            "operation": "posture_assessment"
        })

        if result["success"]:
            # Update risk assessment
            risk_assessment = {
                "timestamp": result["timestamp"],
                "scope": assessment_scope,
                "overall_score": result.get("security_score", 0),
                "risk_level": result.get("risk_level", "unknown"),
                "key_findings": result.get("findings", []),
                "recommendations": result.get("recommendations", [])
            }
            self.update_state("risk_assessment", risk_assessment)

        return result

    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        return {
            "vulnerability_scans_count": len(self.state.get("vulnerability_scans", [])),
            "compliance_status": self.state.get("compliance_status", {}),
            "active_security_policies": len(self.state.get("security_policies", [])),
            "managed_secrets_count": len(self.state.get("secret_rotation_schedule", {})),
            "security_incidents_count": len(self.state.get("security_incidents", [])),
            "last_security_audit": self.state.get("last_security_audit"),
            "current_risk_level": self.state.get("risk_assessment", {}).get("risk_level", "unknown"),
            "security_score": self.state.get("risk_assessment", {}).get("overall_score", 0)
        }