"""
CI/CD Agent for DevOps AI Platform
Handles continuous integration and deployment workflows
"""

from typing import List, Dict, Any
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool

from ..base.agent import BaseAgent
from .tools import GitHubActionsTool, PipelineTool, DockerTool
from ..base.tools import GitTool, ShellCommandTool


class CICDAgent(BaseAgent):
    """
    Specialized agent for CI/CD operations including:
    - GitHub Actions management
    - Pipeline automation
    - Docker builds and deployments
    - Code quality checks
    - Automated testing
    """

    def __init__(self, llm: BaseLanguageModel, **kwargs):
        # Initialize specialized tools for CI/CD
        tools = [
            GitHubActionsTool(),
            PipelineTool(),
            DockerTool(),
            GitTool(),
            ShellCommandTool(allowed_commands=[
                "docker", "npm", "pip", "pytest", "coverage", "flake8", "black"
            ])
        ]

        super().__init__(
            name="cicd",
            llm=llm,
            tools=tools,
            **kwargs
        )

        # CI/CD specific state
        self.state.update({
            "current_pipeline": None,
            "build_history": [],
            "deployment_status": "idle"
        })

    def get_system_prompt(self) -> str:
        """System prompt for CI/CD agent"""
        return """You are a specialized CI/CD agent responsible for automating continuous integration and deployment workflows.

Your primary responsibilities include:
1. Managing GitHub Actions workflows
2. Automating build and test pipelines
3. Docker image building and registry management
4. Code quality assurance and testing
5. Deployment orchestration
6. Pipeline monitoring and optimization

Key capabilities:
- Create and modify GitHub Actions workflows
- Execute build and test commands
- Manage Docker containers and images
- Perform code quality checks (linting, formatting, testing)
- Coordinate with other agents for deployment approvals
- Monitor pipeline performance and suggest improvements

Always prioritize:
- Security in CI/CD pipelines
- Code quality and testing coverage
- Fast feedback loops
- Proper error handling and rollback strategies
- Documentation of pipeline changes

When executing tasks:
1. Analyze the current codebase and existing pipelines
2. Plan changes with minimal disruption
3. Implement changes incrementally
4. Validate changes with appropriate tests
5. Monitor results and provide feedback
"""

    def _create_agent_executor(self) -> AgentExecutor:
        """Create the CI/CD agent executor"""
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
            max_iterations=10
        )

    async def create_github_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new GitHub Actions workflow"""
        self.logger.info(f"Creating GitHub workflow: {workflow_config.get('name')}")

        task = f"""Create a GitHub Actions workflow with the following configuration:
        {workflow_config}

        Ensure the workflow includes:
        - Proper trigger conditions
        - Security best practices
        - Appropriate test stages
        - Build optimization
        - Error handling
        """

        result = await self.execute(task, {"workflow_config": workflow_config})

        if result["success"]:
            self.update_state("last_workflow_created", workflow_config)

        return result

    async def run_pipeline(self, pipeline_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a CI/CD pipeline"""
        self.logger.info(f"Running pipeline: {pipeline_name}")

        self.update_state("current_pipeline", pipeline_name)
        self.update_state("deployment_status", "running")

        task = f"""Execute the CI/CD pipeline '{pipeline_name}' with parameters: {parameters or {}}

        Steps to follow:
        1. Validate pipeline configuration
        2. Check prerequisites and dependencies
        3. Execute pipeline stages in order
        4. Monitor progress and handle errors
        5. Provide detailed status updates
        6. Clean up resources if needed
        """

        result = await self.execute(task, {
            "pipeline_name": pipeline_name,
            "parameters": parameters
        })

        # Update state based on result
        if result["success"]:
            self.update_state("deployment_status", "completed")
            # Add to build history
            build_history = self.state.get("build_history", [])
            build_history.append({
                "pipeline": pipeline_name,
                "timestamp": result["timestamp"],
                "status": "success",
                "parameters": parameters
            })
            self.update_state("build_history", build_history[-10:])  # Keep last 10
        else:
            self.update_state("deployment_status", "failed")

        self.update_state("current_pipeline", None)
        return result

    async def build_and_test(self, project_path: str, test_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build project and run tests"""
        self.logger.info(f"Building and testing project at: {project_path}")

        task = f"""Build and test the project located at '{project_path}'.

        Execute the following steps:
        1. Install dependencies
        2. Run linting and code quality checks
        3. Execute unit tests with coverage reporting
        4. Run integration tests if available
        5. Build the application/container
        6. Generate test reports

        Test configuration: {test_config or 'Use defaults'}

        Provide detailed feedback on:
        - Build status and any issues
        - Test results and coverage metrics
        - Code quality issues found
        - Recommendations for improvements
        """

        return await self.execute(task, {
            "project_path": project_path,
            "test_config": test_config
        })

    async def deploy_application(self, deployment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy application using specified configuration"""
        self.logger.info("Deploying application")

        self.update_state("deployment_status", "deploying")

        task = f"""Deploy the application using this configuration:
        {deployment_config}

        Deployment steps:
        1. Validate deployment configuration
        2. Prepare deployment environment
        3. Execute deployment strategy (blue-green, rolling, etc.)
        4. Verify deployment health
        5. Update routing/load balancer if needed
        6. Confirm application is responding correctly

        Handle rollback automatically if deployment fails.
        """

        result = await self.execute(task, {"deployment_config": deployment_config})

        if result["success"]:
            self.update_state("deployment_status", "deployed")
        else:
            self.update_state("deployment_status", "failed")

        return result

    async def optimize_pipeline(self, pipeline_name: str) -> Dict[str, Any]:
        """Analyze and optimize CI/CD pipeline performance"""
        self.logger.info(f"Optimizing pipeline: {pipeline_name}")

        task = f"""Analyze and optimize the CI/CD pipeline '{pipeline_name}'.

        Analysis areas:
        1. Pipeline execution time and bottlenecks
        2. Resource utilization
        3. Test efficiency and parallelization
        4. Cache utilization
        5. Dependency management
        6. Build artifact optimization

        Provide:
        - Current performance metrics
        - Identified bottlenecks
        - Specific optimization recommendations
        - Estimated improvement impact
        - Implementation steps
        """

        return await self.execute(task, {"pipeline_name": pipeline_name})

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            "current_pipeline": self.state.get("current_pipeline"),
            "deployment_status": self.state.get("deployment_status"),
            "build_history": self.state.get("build_history", []),
            "last_workflow_created": self.state.get("last_workflow_created")
        }