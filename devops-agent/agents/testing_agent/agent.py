"""
Testing Agent for DevOps AI Platform
Handles automated testing, quality assurance, and test orchestration
"""

from typing import List, Dict, Any
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseLanguageModel

from ..base.agent import BaseAgent
from .tools import TestFrameworkTool, CoverageAnalyzer, TestReportGenerator, PerformanceTestTool
from ..base.tools import ShellCommandTool


class TestingAgent(BaseAgent):
    """
    Specialized agent for testing and quality assurance operations including:
    - Unit, integration, and end-to-end testing
    - Test coverage analysis and reporting
    - Performance and load testing
    - Test automation and CI/CD integration
    - Quality metrics and test optimization
    - Test data management and mocking
    """

    def __init__(self, llm: BaseLanguageModel, **kwargs):
        # Initialize specialized tools for testing
        tools = [
            TestFrameworkTool(),
            CoverageAnalyzer(),
            TestReportGenerator(),
            PerformanceTestTool(),
            ShellCommandTool(allowed_commands=[
                "pytest", "coverage", "npm", "jest", "selenium", "locust", "k6"
            ])
        ]

        super().__init__(
            name="testing",
            llm=llm,
            tools=tools,
            **kwargs
        )

        # Testing specific state
        self.state.update({
            "test_suites": {},
            "coverage_reports": [],
            "performance_baselines": {},
            "test_execution_history": [],
            "quality_metrics": {},
            "flaky_tests": [],
            "test_environments": [],
            "automation_status": "idle"
        })

    def get_system_prompt(self) -> str:
        """System prompt for Testing agent"""
        return """You are a specialized Testing agent responsible for comprehensive quality assurance and test automation.

Your primary responsibilities include:
1. Design and implement comprehensive test strategies (unit, integration, e2e)
2. Automate test execution across multiple environments and platforms
3. Analyze test coverage and identify gaps in testing
4. Perform performance testing and establish baselines
5. Generate detailed test reports and quality metrics
6. Integrate testing with CI/CD pipelines
7. Manage test data, fixtures, and mocking strategies
8. Optimize test execution time and reliability

Key capabilities:
- Multi-framework test execution (pytest, Jest, Selenium, etc.)
- Advanced test coverage analysis and reporting
- Performance and load testing with detailed metrics
- Automated test generation and maintenance
- Flaky test detection and remediation
- Cross-browser and cross-platform testing
- API testing and contract validation
- Test environment management and provisioning

Testing Philosophy:
- Shift-left testing approach - early and continuous testing
- Test pyramid strategy - appropriate balance of test types
- Risk-based testing - focus on high-impact areas
- Automated regression testing
- Continuous feedback and improvement

Quality Standards:
- Minimum 80% code coverage for critical paths
- All tests must be deterministic and reliable
- Performance tests must validate against baselines
- Integration tests must validate end-to-end workflows
- Security testing integrated in test pipeline

When executing testing tasks:
1. Analyze codebase and identify testing requirements
2. Design appropriate test strategy and structure
3. Implement automated tests with proper assertions
4. Execute tests and capture detailed results
5. Analyze failures and provide actionable insights
6. Generate comprehensive test reports
7. Recommend improvements and optimizations

Always prioritize:
- Test reliability and maintainability
- Fast feedback cycles
- Clear and actionable test results
- Comprehensive coverage of critical functionality
- Integration with development workflows
"""

    def _create_agent_executor(self) -> AgentExecutor:
        """Create the Testing agent executor"""
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
            max_iterations=12
        )

    async def execute_test_suite(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive test suite"""
        suite_name = test_config.get("name", "default_suite")
        test_types = test_config.get("types", ["unit", "integration"])

        self.logger.info(f"Executing test suite: {suite_name}")

        self.update_state("automation_status", "running")

        task = f"""Execute comprehensive test suite: {suite_name}

        Test Configuration: {test_config}

        Test Execution Strategy:

        1. Pre-Test Setup
           - Validate test environment configuration
           - Setup test databases and fixtures
           - Configure test data and mocks
           - Verify dependencies and services

        2. Unit Testing
           - Execute unit tests with maximum parallelization
           - Capture code coverage metrics
           - Identify and report test failures
           - Generate detailed assertion reports

        3. Integration Testing
           - Execute integration tests in controlled environment
           - Validate service-to-service communication
           - Test database interactions and transactions
           - Verify external API integrations

        4. End-to-End Testing
           - Execute user journey tests
           - Validate complete application workflows
           - Test cross-browser compatibility
           - Verify mobile responsiveness

        5. Performance Testing
           - Execute load tests against performance baselines
           - Measure response times and throughput
           - Identify performance bottlenecks
           - Generate performance comparison reports

        6. Security Testing
           - Execute security-focused test scenarios
           - Validate input sanitization and validation
           - Test authentication and authorization
           - Scan for common security vulnerabilities

        Provide comprehensive results including:
        - Test execution summary with pass/fail counts
        - Coverage analysis with gap identification
        - Performance metrics and baseline comparisons
        - Detailed failure analysis and recommendations
        - Quality metrics and trend analysis
        """

        result = await self.execute(task, {
            "test_config": test_config,
            "operation": "test_execution"
        })

        if result["success"]:
            # Update test execution history
            execution_history = self.state.get("test_execution_history", [])
            execution_history.append({
                "timestamp": result["timestamp"],
                "suite_name": suite_name,
                "test_types": test_types,
                "result_summary": result.get("test_summary", {}),
                "status": "completed"
            })
            self.update_state("test_execution_history", execution_history[-20:])

            # Update test suites
            test_suites = self.state.get("test_suites", {})
            test_suites[suite_name] = {
                "last_execution": result["timestamp"],
                "status": "passed" if result.get("all_tests_passed", False) else "failed",
                "coverage": result.get("coverage_percentage", 0),
                "test_count": result.get("total_tests", 0)
            }
            self.update_state("test_suites", test_suites)

        self.update_state("automation_status", "idle")
        return result

    async def analyze_test_coverage(self, coverage_config: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive test coverage analysis"""
        self.logger.info("Analyzing test coverage")

        task = f"""Perform comprehensive test coverage analysis:

        Coverage Configuration: {coverage_config}

        Coverage Analysis Framework:

        1. Code Coverage Metrics
           - Line coverage: percentage of code lines executed
           - Branch coverage: percentage of decision branches taken
           - Function coverage: percentage of functions called
           - Statement coverage: percentage of statements executed

        2. Coverage Gap Analysis
           - Identify uncovered critical paths
           - Analyze complex business logic coverage
           - Review error handling and edge cases
           - Assess integration points coverage

        3. Coverage Quality Assessment
           - Evaluate meaningfulness of covered lines
           - Identify superficial vs. thorough testing
           - Assess test assertion quality
           - Review test data diversity

        4. Trend Analysis
           - Compare coverage with previous executions
           - Identify coverage improvements or degradations
           - Track coverage goals and targets
           - Generate coverage trend reports

        5. Recommendations
           - Prioritize areas needing additional tests
           - Suggest specific test scenarios
           - Recommend refactoring for testability
           - Propose coverage improvement strategies

        Deliverables:
        - Detailed coverage report with visual metrics
        - Gap analysis with prioritized recommendations
        - Coverage trend analysis and projections
        - Actionable improvement plan
        """

        result = await self.execute(task, {
            "coverage_config": coverage_config,
            "operation": "coverage_analysis"
        })

        if result["success"]:
            # Update coverage reports
            coverage_reports = self.state.get("coverage_reports", [])
            coverage_reports.append({
                "timestamp": result["timestamp"],
                "overall_coverage": result.get("coverage_percentage", 0),
                "coverage_by_type": result.get("coverage_breakdown", {}),
                "gaps_identified": result.get("coverage_gaps", [])
            })
            self.update_state("coverage_reports", coverage_reports[-10:])

        return result

    async def execute_performance_tests(self, performance_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute performance and load testing"""
        test_name = performance_config.get("name", "performance_test")
        self.logger.info(f"Executing performance tests: {test_name}")

        task = f"""Execute comprehensive performance testing:

        Performance Test Configuration: {performance_config}

        Performance Testing Strategy:

        1. Load Testing
           - Simulate normal expected load
           - Measure response times under typical usage
           - Validate system stability over time
           - Assess resource utilization patterns

        2. Stress Testing
           - Push system beyond normal operating capacity
           - Identify breaking points and failure modes
           - Test system recovery and graceful degradation
           - Validate error handling under extreme load

        3. Spike Testing
           - Simulate sudden load increases
           - Test auto-scaling responsiveness
           - Validate system behavior during traffic spikes
           - Assess performance recovery times

        4. Volume Testing
           - Test with large amounts of data
           - Validate database performance with scale
           - Assess memory and storage utilization
           - Test data processing efficiency

        5. Endurance Testing
           - Run tests for extended periods
           - Identify memory leaks and resource degradation
           - Validate system stability over time
           - Test long-running process reliability

        Performance Metrics to Capture:
        - Response time percentiles (50th, 90th, 95th, 99th)
        - Throughput (requests/transactions per second)
        - Error rates and failure patterns
        - Resource utilization (CPU, memory, disk, network)
        - Database performance and query efficiency
        - Cache hit rates and effectiveness

        Baseline Comparison:
        - Compare results against established baselines
        - Identify performance regressions
        - Highlight improvements and optimizations
        - Generate performance trend analysis
        """

        result = await self.execute(task, {
            "performance_config": performance_config,
            "operation": "performance_testing"
        })

        if result["success"]:
            # Update performance baselines
            baselines = self.state.get("performance_baselines", {})
            baselines[test_name] = {
                "timestamp": result["timestamp"],
                "response_time_p95": result.get("response_time_p95", 0),
                "throughput": result.get("throughput", 0),
                "error_rate": result.get("error_rate", 0),
                "baseline_status": result.get("baseline_comparison", "unknown")
            }
            self.update_state("performance_baselines", baselines)

        return result

    async def generate_test_report(self, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive testing report"""
        report_type = report_config.get("type", "comprehensive")
        self.logger.info(f"Generating test report: {report_type}")

        task = f"""Generate comprehensive testing report:

        Report Configuration: {report_config}

        Report Generation Framework:

        1. Executive Summary
           - Overall testing health and status
           - Key quality metrics and KPIs
           - Risk assessment and recommendations
           - Testing ROI and value delivered

        2. Test Execution Summary
           - Test suite execution results
           - Pass/fail rates and trends
           - Test execution time analysis
           - Environment-specific results

        3. Coverage Analysis
           - Code coverage metrics and trends
           - Coverage gap analysis
           - Critical path coverage assessment
           - Coverage improvement recommendations

        4. Performance Analysis
           - Performance test results summary
           - Baseline comparisons and trends
           - Performance regression identification
           - Optimization opportunities

        5. Quality Metrics
           - Defect density and escape rates
           - Test effectiveness metrics
           - Flaky test identification and trends
           - Testing velocity and efficiency

        6. Risk Analysis
           - High-risk areas with insufficient testing
           - Technical debt impacting testability
           - Quality gate compliance status
           - Release readiness assessment

        7. Recommendations and Action Items
           - Prioritized improvement opportunities
           - Resource allocation suggestions
           - Process optimization recommendations
           - Tool and technology recommendations

        Report Formats:
        - Executive dashboard with key visualizations
        - Detailed technical report with metrics
        - Trend analysis and historical comparisons
        - Actionable recommendations with timelines
        """

        result = await self.execute(task, {
            "report_config": report_config,
            "operation": "report_generation"
        })

        return result

    async def optimize_test_suite(self, optimization_config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize test suite performance and reliability"""
        self.logger.info("Optimizing test suite")

        task = f"""Optimize test suite for performance and reliability:

        Optimization Configuration: {optimization_config}

        Test Suite Optimization Strategy:

        1. Execution Time Optimization
           - Analyze test execution times and bottlenecks
           - Identify opportunities for parallelization
           - Optimize test data setup and teardown
           - Implement intelligent test ordering

        2. Flaky Test Remediation
           - Identify tests with inconsistent results
           - Analyze root causes of flakiness
           - Implement stabilization strategies
           - Add proper wait conditions and retries

        3. Test Maintenance
           - Remove obsolete and duplicate tests
           - Refactor complex test cases for clarity
           - Improve test assertions and error messages
           - Update test documentation and comments

        4. Resource Optimization
           - Optimize test environment provisioning
           - Implement efficient test data management
           - Reduce external dependencies where possible
           - Optimize CI/CD pipeline integration

        5. Test Architecture Improvements
           - Implement proper test categorization
           - Establish test pyramid compliance
           - Improve test isolation and independence
           - Enhance test reporting and debugging

        Optimization Deliverables:
        - Test execution time reduction plan
        - Flaky test remediation roadmap
        - Test maintenance recommendations
        - Performance improvement metrics
        - Reliability enhancement strategies
        """

        result = await self.execute(task, {
            "optimization_config": optimization_config,
            "operation": "test_optimization"
        })

        if result["success"]:
            # Update flaky tests tracking
            if result.get("flaky_tests"):
                self.update_state("flaky_tests", result["flaky_tests"])

            # Update quality metrics
            quality_metrics = {
                "execution_time_improvement": result.get("time_improvement_percentage", 0),
                "flaky_tests_resolved": result.get("flaky_tests_resolved", 0),
                "test_reliability_score": result.get("reliability_score", 0),
                "optimization_timestamp": result["timestamp"]
            }
            self.update_state("quality_metrics", quality_metrics)

        return result

    async def setup_test_automation(self, automation_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup comprehensive test automation pipeline"""
        self.logger.info("Setting up test automation")

        task = f"""Setup comprehensive test automation pipeline:

        Automation Configuration: {automation_config}

        Test Automation Framework:

        1. CI/CD Integration
           - Configure automated test triggers
           - Setup test execution in multiple environments
           - Implement test result reporting
           - Configure quality gates and failure handling

        2. Test Environment Management
           - Automate test environment provisioning
           - Configure environment-specific test data
           - Implement environment cleanup procedures
           - Setup monitoring and health checks

        3. Test Data Management
           - Implement test data generation strategies
           - Setup test data refresh and cleanup
           - Configure data privacy and masking
           - Implement data versioning and rollback

        4. Test Execution Orchestration
           - Configure parallel test execution
           - Implement test suite prioritization
           - Setup dynamic test selection
           - Configure retry and recovery mechanisms

        5. Reporting and Notifications
           - Setup automated test result reporting
           - Configure failure notifications and escalation
           - Implement trend analysis and alerting
           - Setup quality metrics dashboards

        Automation Deliverables:
        - Fully configured CI/CD test pipeline
        - Automated test environment provisioning
        - Test data management automation
        - Comprehensive test reporting system
        - Quality metrics and alerting setup
        """

        result = await self.execute(task, {
            "automation_config": automation_config,
            "operation": "automation_setup"
        })

        if result["success"]:
            # Update test environments
            test_environments = automation_config.get("environments", [])
            self.update_state("test_environments", test_environments)

            self.update_state("automation_status", "configured")

        return result

    def get_testing_status(self) -> Dict[str, Any]:
        """Get current testing status and metrics"""
        return {
            "automation_status": self.state.get("automation_status"),
            "test_suites_count": len(self.state.get("test_suites", {})),
            "latest_coverage": self.state.get("coverage_reports", [])[-1] if self.state.get("coverage_reports") else None,
            "performance_baselines_count": len(self.state.get("performance_baselines", {})),
            "flaky_tests_count": len(self.state.get("flaky_tests", [])),
            "test_environments": self.state.get("test_environments", []),
            "last_execution": self.state.get("test_execution_history", [])[-1] if self.state.get("test_execution_history") else None,
            "quality_metrics": self.state.get("quality_metrics", {})
        }