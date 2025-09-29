"""
Infrastructure Agent for DevOps AI Platform
Handles infrastructure provisioning, management, and optimization
"""

from typing import List, Dict, Any
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool

from ..base.agent import BaseAgent
from .tools import TerraformTool, AWSToolset, KubernetesTool
from ..base.tools import ShellCommandTool


class InfrastructureAgent(BaseAgent):
    """
    Specialized agent for infrastructure operations including:
    - Terraform infrastructure provisioning
    - AWS/Cloud resource management
    - Kubernetes cluster management
    - Infrastructure monitoring and optimization
    - Cost optimization and compliance
    """

    def __init__(self, llm: BaseLanguageModel, **kwargs):
        # Initialize specialized tools for infrastructure
        tools = [
            TerraformTool(),
            AWSToolset(),
            KubernetesTool(),
            ShellCommandTool(allowed_commands=[
                "terraform", "kubectl", "aws", "helm", "eksctl", "docker"
            ])
        ]

        super().__init__(
            name="infrastructure",
            llm=llm,
            tools=tools,
            **kwargs
        )

        # Infrastructure specific state
        self.state.update({
            "active_environments": [],
            "terraform_states": {},
            "cluster_status": {},
            "resource_inventory": {},
            "cost_tracking": {},
            "compliance_status": {}
        })

    def get_system_prompt(self) -> str:
        """System prompt for Infrastructure agent"""
        return """You are a specialized Infrastructure agent responsible for provisioning, managing, and optimizing cloud infrastructure and Kubernetes resources.

Your primary responsibilities include:
1. Infrastructure as Code (IaC) with Terraform
2. AWS/Cloud resource provisioning and management
3. Kubernetes cluster lifecycle management
4. EKS cluster operations and optimization
5. Infrastructure cost optimization
6. Security and compliance monitoring
7. Resource scaling and performance tuning

Key capabilities:
- Design and implement Terraform modules
- Provision and manage AWS resources (EKS, VPC, IAM, etc.)
- Deploy and manage Kubernetes clusters
- Implement infrastructure security best practices
- Monitor resource utilization and costs
- Automate infrastructure scaling decisions
- Ensure compliance with organizational policies

Always prioritize:
- Infrastructure security and least privilege access
- Cost optimization and resource efficiency
- High availability and disaster recovery
- Infrastructure documentation and versioning
- Automated provisioning and configuration management

When executing infrastructure tasks:
1. Analyze current infrastructure state
2. Plan changes with impact assessment
3. Validate configurations and security policies
4. Apply changes with proper state management
5. Monitor deployment and verify functionality
6. Update documentation and compliance records
"""

    def _create_agent_executor(self) -> AgentExecutor:
        """Create the Infrastructure agent executor"""
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
            max_iterations=15  # Infrastructure tasks may need more iterations
        )

    async def provision_infrastructure(self, environment: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Provision infrastructure using Terraform"""
        self.logger.info(f"Provisioning infrastructure for environment: {environment}")

        task = f"""Provision infrastructure for environment '{environment}' with the following configuration:
        {config}

        Steps to execute:
        1. Validate Terraform configuration files
        2. Initialize Terraform state for the environment
        3. Plan infrastructure changes and review resource requirements
        4. Apply infrastructure provisioning with proper state management
        5. Verify resource creation and connectivity
        6. Update infrastructure inventory and documentation

        Ensure:
        - Proper resource tagging and naming conventions
        - Security group and IAM configurations follow best practices
        - Cost optimization through appropriate resource sizing
        - High availability and fault tolerance
        """

        result = await self.execute(task, {
            "environment": environment,
            "config": config,
            "operation": "provision"
        })

        if result["success"]:
            # Update state tracking
            active_envs = self.state.get("active_environments", [])
            if environment not in active_envs:
                active_envs.append(environment)
            self.update_state("active_environments", active_envs)

            # Update terraform state tracking
            terraform_states = self.state.get("terraform_states", {})
            terraform_states[environment] = {
                "status": "provisioned",
                "timestamp": result["timestamp"],
                "config": config
            }
            self.update_state("terraform_states", terraform_states)

        return result

    async def manage_eks_cluster(self, action: str, cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """Manage AWS EKS cluster operations"""
        cluster_name = cluster_config.get("name", "default-cluster")
        self.logger.info(f"Managing EKS cluster '{cluster_name}' - action: {action}")

        task = f"""Perform EKS cluster operation: {action}

        Cluster configuration:
        {cluster_config}

        Operations to handle based on action:

        CREATE:
        - Provision VPC and networking components
        - Create EKS cluster with worker node groups
        - Configure RBAC and security policies
        - Install essential add-ons (CNI, CoreDNS, etc.)
        - Set up cluster autoscaler and monitoring

        UPDATE:
        - Update cluster version or configuration
        - Modify worker node groups
        - Update add-ons and configurations

        SCALE:
        - Adjust worker node group capacity
        - Configure horizontal and vertical pod autoscaling
        - Optimize resource allocation

        DELETE:
        - Safely drain and terminate worker nodes
        - Remove cluster resources
        - Clean up associated AWS resources

        Monitor the operation and provide detailed status updates.
        """

        result = await self.execute(task, {
            "action": action,
            "cluster_config": cluster_config,
            "cluster_name": cluster_name
        })

        if result["success"]:
            # Update cluster status
            cluster_status = self.state.get("cluster_status", {})
            cluster_status[cluster_name] = {
                "action": action,
                "status": "completed",
                "timestamp": result["timestamp"],
                "config": cluster_config
            }
            self.update_state("cluster_status", cluster_status)

        return result

    async def optimize_costs(self, scope: str = "all") -> Dict[str, Any]:
        """Analyze and optimize infrastructure costs"""
        self.logger.info(f"Optimizing costs for scope: {scope}")

        task = f"""Analyze and optimize infrastructure costs for scope: {scope}

        Cost optimization analysis:
        1. Resource utilization analysis
        2. Right-sizing recommendations for compute resources
        3. Storage optimization opportunities
        4. Reserved instance and savings plan recommendations
        5. Unused or idle resource identification
        6. Network traffic optimization
        7. Auto-scaling configuration review

        Provide:
        - Current cost breakdown by service/resource
        - Identified cost savings opportunities
        - Prioritized recommendations with impact estimates
        - Implementation plan for cost optimizations
        - ROI analysis for recommended changes

        Focus on maintaining performance while reducing costs.
        """

        result = await self.execute(task, {"scope": scope, "operation": "cost_optimization"})

        if result["success"]:
            # Update cost tracking
            cost_tracking = self.state.get("cost_tracking", {})
            cost_tracking["last_optimization"] = {
                "timestamp": result["timestamp"],
                "scope": scope,
                "recommendations": result.get("recommendations", [])
            }
            self.update_state("cost_tracking", cost_tracking)

        return result

    async def ensure_compliance(self, standards: List[str] = None) -> Dict[str, Any]:
        """Ensure infrastructure compliance with security and organizational standards"""
        standards = standards or ["CIS", "SOC2", "GDPR", "HIPAA"]
        self.logger.info(f"Checking compliance for standards: {standards}")

        task = f"""Perform comprehensive compliance check for standards: {standards}

        Compliance assessment areas:
        1. Security group and network ACL configurations
        2. IAM policies and role permissions
        3. Encryption at rest and in transit
        4. Logging and monitoring configurations
        5. Backup and disaster recovery setup
        6. Resource tagging and governance
        7. Access control and authentication mechanisms

        For each standard, provide:
        - Compliance status (compliant/non-compliant/partial)
        - Specific violations or gaps identified
        - Remediation steps and timeline
        - Risk assessment for non-compliance items
        - Automated remediation recommendations

        Generate compliance report with actionable recommendations.
        """

        result = await self.execute(task, {
            "standards": standards,
            "operation": "compliance_check"
        })

        if result["success"]:
            # Update compliance status
            compliance_status = self.state.get("compliance_status", {})
            compliance_status["last_check"] = {
                "timestamp": result["timestamp"],
                "standards": standards,
                "status": result.get("overall_compliance", "unknown")
            }
            self.update_state("compliance_status", compliance_status)

        return result

    async def scale_infrastructure(self, scaling_config: Dict[str, Any]) -> Dict[str, Any]:
        """Scale infrastructure resources based on demand"""
        self.logger.info("Scaling infrastructure resources")

        task = f"""Scale infrastructure resources based on configuration:
        {scaling_config}

        Scaling operations:
        1. Analyze current resource utilization and demand patterns
        2. Determine optimal scaling strategy (horizontal/vertical)
        3. Update auto-scaling policies and thresholds
        4. Scale Kubernetes deployments and services
        5. Adjust infrastructure capacity (EC2, RDS, etc.)
        6. Update load balancer configurations if needed
        7. Monitor scaling operations and performance impact

        Ensure:
        - Zero-downtime scaling where possible
        - Cost-effective scaling decisions
        - Proper health checks and monitoring
        - Rollback capability if issues arise
        """

        return await self.execute(task, {
            "scaling_config": scaling_config,
            "operation": "scale"
        })

    async def backup_and_disaster_recovery(self, operation: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Manage backup and disaster recovery operations"""
        self.logger.info(f"Managing backup/DR operation: {operation}")

        task = f"""Execute backup and disaster recovery operation: {operation}

        Configuration: {config}

        Operations to handle:

        SETUP_BACKUP:
        - Configure automated backup schedules
        - Set up cross-region replication
        - Implement backup retention policies
        - Test backup integrity

        DISASTER_RECOVERY_PLAN:
        - Create DR environment configuration
        - Set up failover procedures
        - Configure RTO/RPO requirements
        - Document recovery procedures

        TEST_RECOVERY:
        - Perform DR testing scenarios
        - Validate data integrity after recovery
        - Test failover and failback procedures
        - Update recovery documentation

        EXECUTE_RECOVERY:
        - Execute actual disaster recovery
        - Monitor recovery progress
        - Validate system functionality
        - Switch traffic to recovery environment

        Provide detailed status updates and validation results.
        """

        return await self.execute(task, {
            "operation": operation,
            "config": config,
            "task_type": "backup_dr"
        })

    def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get current infrastructure status"""
        return {
            "active_environments": self.state.get("active_environments", []),
            "terraform_states": self.state.get("terraform_states", {}),
            "cluster_status": self.state.get("cluster_status", {}),
            "resource_inventory": self.state.get("resource_inventory", {}),
            "cost_tracking": self.state.get("cost_tracking", {}),
            "compliance_status": self.state.get("compliance_status", {}),
            "agent_ready": True
        }