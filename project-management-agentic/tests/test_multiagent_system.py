"""
Test suite for the multi-agent architecture
Tests orchestrator, individual agents, and inter-agent communication
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import AgentOrchestrator, TaskContext, TaskType, AgentCapability
from agents.project_manager_agent import ProjectManagerAgent
from agents.document_agent import DocumentAgent
from agents.risk_management_agent import RiskManagementAgent
from agents.agent_factory import AgentFactory
from models.project import Project, ProjectStatus


class TestAgentOrchestrator:
    """Test the orchestrator coordination logic"""

    @pytest.fixture
    def orchestrator(self):
        return AgentOrchestrator()

    @pytest.fixture
    def mock_project_manager_agent(self):
        agent = Mock(spec=ProjectManagerAgent)
        agent.name = "project_manager_agent"
        agent.process.return_value = {"success": True, "response": "Test response"}
        return agent

    @pytest.fixture
    def mock_document_agent(self):
        agent = Mock(spec=DocumentAgent)
        agent.name = "document_agent"
        agent.process.return_value = {"success": True, "response": "Document created"}
        return agent

    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly"""
        assert orchestrator.agents == {}
        assert orchestrator.task_routing is not None
        assert TaskType.PROJECT_CREATION in orchestrator.task_routing

    def test_agent_registration(self, orchestrator, mock_project_manager_agent):
        """Test agent registration with capabilities"""
        capabilities = [AgentCapability.PROJECT_CHARTER]
        orchestrator.register_agent(mock_project_manager_agent, capabilities)

        assert "project_manager_agent" in orchestrator.agents
        assert "project_manager_agent" in orchestrator.agent_capabilities
        assert AgentCapability.PROJECT_CHARTER in orchestrator.agent_capabilities["project_manager_agent"]

    @pytest.mark.asyncio
    async def test_single_agent_routing(self, orchestrator, mock_project_manager_agent):
        """Test routing to a single agent"""
        orchestrator.register_agent(mock_project_manager_agent, [AgentCapability.PROJECT_CHARTER])

        result = await orchestrator.process_request("crear proyecto test")

        assert result["success"] is True
        assert "response" in result

    @pytest.mark.asyncio
    async def test_intent_analysis(self, orchestrator):
        """Test intent detection for different inputs"""
        # Test project creation intent
        context = TaskContext("crear proyecto app móvil")
        await orchestrator._analyze_intent(context)

        assert context.intent == "project_creation"
        assert context.primary_agent == "project_manager_agent"

    def test_task_context_creation(self):
        """Test TaskContext object creation and management"""
        context = TaskContext("test input", project_id=123)

        assert context.user_input == "test input"
        assert context.project_id == 123
        assert context.intent is None
        assert context.intermediate_results == {}

        # Test adding results
        context.add_result("agent1", {"data": "test"})
        assert context.get_result("agent1") == {"data": "test"}

    def test_get_system_status(self, orchestrator, mock_project_manager_agent):
        """Test system status reporting"""
        orchestrator.register_agent(mock_project_manager_agent, [AgentCapability.PROJECT_CHARTER])

        status = orchestrator.get_system_status()

        assert status["orchestrator_status"] == "active"
        assert status["registered_agents"] == 1
        assert "project_manager_agent" in status["agents"]


class TestProjectManagerAgent:
    """Test the Project Manager Agent functionality"""

    @pytest.fixture
    def agent(self):
        with patch('agents.project_manager_agent.ClaudeClient'):
            return ProjectManagerAgent()

    @pytest.fixture
    def mock_db_manager(self):
        mock_db = Mock()
        mock_project = Mock(spec=Project)
        mock_project.id = 1
        mock_project.name = "Test Project"
        mock_project.description = "Test Description"
        mock_project.methodology = "PMP"
        mock_project.status = ProjectStatus.PLANNING
        mock_project.created_at = datetime.now()

        mock_db.create_project.return_value = mock_project
        mock_db.get_project.return_value = mock_project
        mock_db.list_projects.return_value = [mock_project]
        return mock_db

    @pytest.mark.asyncio
    async def test_project_creation_intent(self, agent, mock_db_manager):
        """Test project creation with intent analysis"""
        with patch.object(agent, 'db_manager', mock_db_manager):
            with patch.object(agent, '_analyze_intent_with_llm') as mock_llm:
                mock_llm.return_value = {
                    "intent": "create_project",
                    "confidence": 0.9,
                    "parameters": {"project_name": "Test App"},
                    "reasoning": "User wants to create project"
                }

                result = agent.process("crear proyecto Test App")

                assert result["success"] is True
                assert "Test App" in result["response"]
                mock_db_manager.create_project.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_projects_intent(self, agent, mock_db_manager):
        """Test listing projects"""
        with patch.object(agent, 'db_manager', mock_db_manager):
            with patch.object(agent, '_analyze_intent_with_llm') as mock_llm:
                mock_llm.return_value = {
                    "intent": "list_projects",
                    "confidence": 0.9,
                    "parameters": {},
                    "reasoning": "User wants to see projects"
                }

                result = agent.process("listar proyectos")

                assert result["success"] is True
                assert "Test Project" in result["response"]
                mock_db_manager.list_projects.assert_called_once()

    def test_conversation_context_update(self, agent):
        """Test conversation context management"""
        agent._update_conversation_context("test input", 123)

        assert agent.conversation_context["last_input"] == "test input"
        assert agent.conversation_context["current_project_id"] == 123
        assert "timestamp" in agent.conversation_context

    def test_fallback_intent_detection(self, agent):
        """Test fallback intent detection when LLM fails"""
        result = agent._fallback_intent_detection("crear proyecto nuevo")

        assert result["intent"] == "create_project"
        assert result["confidence"] > 0.5

    def test_project_name_extraction(self, agent):
        """Test project name extraction from user input"""
        # Test quoted string
        name = agent._extract_project_name('crear proyecto "Mi App Móvil"')
        assert name == "Mi App Móvil"

        # Test keyword-based extraction
        name = agent._extract_project_name('crear proyecto para mi aplicación web')
        assert name is not None


class TestDocumentAgent:
    """Test the Document Agent functionality"""

    @pytest.fixture
    def agent(self):
        with patch('agents.document_agent.ClaudeClient'):
            return DocumentAgent()

    @pytest.fixture
    def mock_project(self):
        project = Mock(spec=Project)
        project.id = 1
        project.name = "Test Project"
        project.description = "Test Description"
        project.methodology = "PMP"
        project.status = ProjectStatus.PLANNING
        return project

    @pytest.mark.asyncio
    async def test_charter_creation_intent(self, agent, mock_project):
        """Test project charter creation"""
        with patch.object(agent, 'db_manager') as mock_db:
            with patch.object(agent, 'file_manager') as mock_file:
                with patch.object(agent, '_analyze_document_intent') as mock_intent:
                    mock_db.get_project.return_value = mock_project
                    mock_file.save_project_document.return_value = "/test/path/charter.md"
                    mock_intent.return_value = {
                        "intent": "create_charter",
                        "confidence": 0.9,
                        "parameters": {}
                    }

                    result = agent.process("crear charter", project_id=1)

                    assert result["success"] is True
                    assert "charter" in result["response"].lower()
                    mock_db.create_project_document.assert_called_once()

    def test_fallback_document_intent_detection(self, agent):
        """Test document intent detection fallback"""
        result = agent._fallback_document_intent_detection("crear charter del proyecto")

        assert result["intent"] == "create_charter"
        assert result["confidence"] > 0.7

    def test_template_availability(self, agent):
        """Test template methods exist and return content"""
        charter_template = agent._get_project_charter_template()
        wbs_template = agent._get_wbs_template()
        risk_template = agent._get_risk_register_template()

        assert "Project Charter" in charter_template
        assert "Work Breakdown Structure" in wbs_template
        assert "Risk Register" in risk_template
        assert len(charter_template) > 100  # Templates should be substantial

    @pytest.mark.asyncio
    async def test_template_request_handling(self, agent):
        """Test template request processing"""
        with patch.object(agent, '_analyze_document_intent') as mock_intent:
            mock_intent.return_value = {
                "intent": "get_template",
                "confidence": 0.9,
                "parameters": {"document_type": "project_charter"}
            }

            result = agent.process("dame la plantilla de project_charter")

            assert result["success"] is True
            assert "template_content" in result
            assert "Project Charter" in result["template_content"]


class TestRiskManagementAgent:
    """Test the Risk Management Agent functionality"""

    @pytest.fixture
    def agent(self):
        with patch('agents.risk_management_agent.ClaudeClient'):
            return RiskManagementAgent()

    @pytest.fixture
    def mock_project(self):
        project = Mock(spec=Project)
        project.id = 1
        project.name = "Software Project"
        project.description = "Web application development"
        project.methodology = "PMP"
        return project

    @pytest.mark.asyncio
    async def test_risk_register_creation(self, agent, mock_project):
        """Test risk register creation"""
        with patch.object(agent, 'db_manager') as mock_db:
            with patch('agents.risk_management_agent.FileManager') as mock_file_class:
                mock_file_manager = Mock()
                mock_file_class.return_value = mock_file_manager
                mock_file_manager.save_project_document.return_value = "/test/risk_register.md"

                mock_db.get_project.return_value = mock_project

                with patch.object(agent, '_analyze_risk_intent') as mock_intent:
                    mock_intent.return_value = {
                        "intent": "create_risk_register",
                        "confidence": 0.9,
                        "parameters": {}
                    }

                    result = agent.process("crear risk register", project_id=1)

                    assert result["success"] is True
                    assert "Risk Register" in result["response"]
                    mock_db.create_project_document.assert_called_once()

    def test_risk_scoring_calculation(self, agent):
        """Test risk score calculation"""
        from agents.risk_management_agent import RiskProbability, RiskImpact

        # Test high probability, high impact
        score = agent.calculate_risk_score(RiskProbability.HIGH, RiskImpact.HIGH)
        assert score == 9

        # Test medium probability, low impact
        score = agent.calculate_risk_score(RiskProbability.MEDIUM, RiskImpact.LOW)
        assert score == 2

        # Test priority calculation
        priority = agent.get_risk_priority(9)
        assert priority == "Critical"

        priority = agent.get_risk_priority(4)
        assert priority == "Medium"

    @pytest.mark.asyncio
    async def test_monte_carlo_analysis(self, agent, mock_project):
        """Test Monte Carlo analysis functionality"""
        with patch.object(agent, 'db_manager') as mock_db:
            mock_db.get_project.return_value = mock_project

            with patch.object(agent, '_analyze_risk_intent') as mock_intent:
                mock_intent.return_value = {
                    "intent": "monte_carlo_analysis",
                    "confidence": 0.9,
                    "parameters": {}
                }

                result = agent.process("hacer análisis monte carlo", project_id=1)

                assert result["success"] is True
                assert "Monte Carlo" in result["response"]
                assert "P10" in result["response"]  # Should contain percentile analysis
                assert "P50" in result["response"]
                assert "P90" in result["response"]

    def test_fallback_risk_intent_detection(self, agent):
        """Test risk intent detection fallback"""
        result = agent._fallback_risk_intent_detection("identificar riesgos del proyecto")

        assert result["intent"] == "identify_risks"
        assert result["confidence"] > 0.7


class TestAgentFactory:
    """Test the Agent Factory functionality"""

    @pytest.fixture
    def factory(self):
        return AgentFactory()

    def test_factory_initialization(self, factory):
        """Test factory initialization with both legacy and new agents"""
        available_agents = factory.list_available_agents()

        # Should have legacy agents
        assert "pmp_project" in available_agents
        assert "cost_budget" in available_agents
        assert "template" in available_agents

        # Should have new agents
        assert "project_manager_agent" in available_agents
        assert "document_agent" in available_agents
        assert "risk_management_agent" in available_agents

    def test_agent_creation(self, factory):
        """Test agent creation for different types"""
        # Test new agent creation
        pm_agent = factory.create_agent("project_manager_agent")
        assert isinstance(pm_agent, ProjectManagerAgent)
        assert pm_agent.name == "project_manager_agent"

        # Test legacy agent creation
        legacy_agent = factory.create_agent("pmp_project")
        assert legacy_agent is not None

    def test_orchestrator_setup(self, factory):
        """Test orchestrator initialization"""
        orchestrator = factory.get_orchestrator()

        assert orchestrator is not None
        status = orchestrator.get_system_status()
        assert status["orchestrator_status"] == "active"
        assert status["registered_agents"] > 0

    @pytest.mark.asyncio
    async def test_multiagent_processing(self, factory):
        """Test processing with orchestrator"""
        # This is an integration test that requires mocking LLM calls
        with patch('core.claude_client.ClaudeClient') as mock_claude:
            mock_claude_instance = Mock()
            mock_claude_instance.chat = AsyncMock(return_value='{"intent": "general_query", "confidence": 0.5, "parameters": {}}')
            mock_claude.return_value = mock_claude_instance

            result = await factory.process_with_orchestrator("ayuda general")

            assert isinstance(result, dict)
            # Result should have basic structure even if mocked

    def test_migration_suggestions(self, factory):
        """Test migration suggestions for legacy agents"""
        suggestion = factory.migrate_from_legacy("pmp_project")
        assert "project_manager_agent" in suggestion
        assert "Consider migrating" in suggestion

        suggestion = factory.migrate_from_legacy("unknown_agent")
        assert "No direct migration path" in suggestion

    def test_multiagent_system_creation(self, factory):
        """Test complete multi-agent system initialization"""
        status = factory.create_multiagent_system()

        assert "orchestrator" in status
        assert "factory" in status
        assert status["orchestrator"]["orchestrator_status"] == "active"
        assert status["factory"]["registered_agents"] > 0


class TestIntegration:
    """Integration tests for the complete multi-agent system"""

    @pytest.fixture
    def system_components(self):
        """Setup complete system for integration testing"""
        factory = AgentFactory()
        orchestrator = factory.get_orchestrator()
        return factory, orchestrator

    @pytest.mark.asyncio
    async def test_end_to_end_project_creation(self, system_components):
        """Test complete project creation workflow"""
        factory, orchestrator = system_components

        # Mock database and LLM interactions
        with patch('storage.database_manager.DatabaseManager') as mock_db_class:
            with patch('core.claude_client.ClaudeClient') as mock_claude_class:
                mock_db = Mock()
                mock_project = Mock()
                mock_project.id = 1
                mock_project.name = "Test Project"
                mock_project.description = "Integration test project"
                mock_project.methodology = "PMP"
                mock_project.status = ProjectStatus.PLANNING
                mock_project.created_at = datetime.now()

                mock_db.create_project.return_value = mock_project
                mock_db_class.return_value = mock_db

                mock_claude = Mock()
                mock_claude.chat = AsyncMock(return_value='{"intent": "create_project", "confidence": 0.9, "parameters": {"project_name": "Test Project"}}')
                mock_claude_class.return_value = mock_claude

                result = await orchestrator.process_request("crear proyecto Test Project")

                assert result["success"] is True
                assert "proyecto" in result["response"].lower() or "project" in result["response"].lower()

    def test_agent_capability_mapping(self, system_components):
        """Test that agents are correctly mapped to capabilities"""
        factory, orchestrator = system_components

        available_agents = orchestrator.get_available_agents()

        assert "document_agent" in available_agents
        assert "project_charter" in available_agents["document_agent"]
        assert "wbs_creation" in available_agents["document_agent"]

        assert "risk_management_agent" in available_agents
        assert "risk_register" in available_agents["risk_management_agent"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])