# tests/test_agents.py
import pytest
import asyncio
from unittest.mock import Mock, patch

from agents.pmp_project_agent import PMPProjectAgent
#from agents.cost_budget_agent import CostBudgetAgent
#from agents.template_agent import TemplateAgent
from agents.agent_factory import AgentFactory


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch('config.settings.settings') as mock:
        mock.openai_api_key = "test_key"
        mock.default_llm_provider = "openai"
        mock.default_model = "gpt-3.5-turbo"
        yield mock


@pytest.fixture
def agent_factory():
    """Agent factory fixture."""
    return AgentFactory()


class TestAgentFactory:
    """Test cases for AgentFactory."""
    
    def test_list_available_agents(self, agent_factory):
        """Test listing available agents."""
        agents = agent_factory.list_available_agents()
        
        assert "pmp_project" in agents
        assert "cost_budget" in agents
        assert "template" in agents
        assert len(agents) >= 3
    
    def test_create_agent_invalid_type(self, agent_factory):
        """Test creating invalid agent type."""
        with pytest.raises(ValueError):
            agent_factory.create_agent("invalid_agent")
    
    @patch('agents.pmp_project_agent.PMPProjectAgent.__init__', return_value=None)
    @patch('agents.pmp_project_agent.PMPProjectAgent.initialize')
    def test_create_pmp_agent(self, mock_init, mock_initialize, agent_factory):
        """Test creating PMP agent."""
        agent = agent_factory.create_agent("pmp_project")
        assert agent is not None
        mock_initialize.assert_called_once()


class TestPMPProjectAgent:
    """Test cases for PMPProjectAgent."""
    
    @patch('agents.base_agent.BaseAgent._get_llm')
    @patch('agents.base_agent.DatabaseManager')
    def test_agent_initialization(self, mock_db, mock_llm):
        """Test agent initialization."""
        agent = PMPProjectAgent()
        
        assert agent.name == "PMP_Project_Agent"
        assert "PMP" in agent.description
        mock_db.assert_called_once()
    
    def test_get_system_prompt(self):
        """Test system prompt generation."""
        with patch('agents.base_agent.BaseAgent._get_llm'):
            with patch('agents.base_agent.DatabaseManager'):
                agent = PMPProjectAgent()
                prompt = agent.get_system_prompt()
                
                assert "Project Management Professional" in prompt
                assert "PMP" in prompt
                assert "SAFe" in prompt


class TestCostBudgetAgent:
    """Test cases for CostBudgetAgent."""
    
    @patch('agents.base_agent.BaseAgent._get_llm')
    @patch('agents.base_agent.DatabaseManager')
    @patch('rag.retriever.RAGRetriever')
    def test_agent_initialization(self, mock_rag, mock_db, mock_llm):
        """Test cost budget agent initialization."""
        agent = None#CostBudgetAgent()
        
        assert agent.name == "Cost_Budget_Agent"
        assert "cost" in agent.description.lower()
        mock_db.assert_called_once()
        mock_rag.assert_called_once()
    
    def test_get_system_prompt(self):
        """Test system prompt for cost agent."""
        with patch('agents.base_agent.BaseAgent._get_llm'):
            with patch('agents.base_agent.DatabaseManager'):
                with patch('rag.retriever.RAGRetriever'):
                    agent = CostBudgetAgent()
                    prompt = agent.get_system_prompt()
                    
                    assert "cost management" in prompt.lower()
                    assert "budget" in prompt.lower()


class TestTemplateAgent:
    """Test cases for TemplateAgent."""
    
    @patch('agents.base_agent.BaseAgent._get_llm')
    @patch('agents.base_agent.DatabaseManager')
    @patch('jinja2.Environment')
    def test_agent_initialization(self, mock_jinja, mock_db, mock_llm):
        """Test template agent initialization."""
        agent = None#TemplateAgent()
        
        assert agent.name == "Template_Agent"
        assert "template" in agent.description.lower()
        mock_db.assert_called_once()
        mock_jinja.assert_called_once()


# tests/test_workflows.py
import pytest
from unittest.mock import Mock, patch, AsyncMock

from workflows.workflow_manager import WorkflowManager, WorkflowStatus
from workflows.project_workflow import ProjectWorkflow


class TestWorkflowManager:
    """Test cases for WorkflowManager."""
    
    @patch('workflows.project_workflow.ProjectWorkflow')
    def test_initialization(self, mock_project_workflow):
        """Test workflow manager initialization."""
        manager = WorkflowManager()
        
        assert manager.project_workflow is not None
        assert "create_project" in manager.workflow_templates
        assert "cost_analysis" in manager.workflow_templates
        assert "custom" in manager.workflow_templates
    
    @patch('workflows.project_workflow.ProjectWorkflow')
    def test_get_available_workflows(self, mock_project_workflow):
        """Test getting available workflows."""
        manager = WorkflowManager()
        workflows = manager.get_available_workflows()
        
        assert len(workflows) >= 3
        assert "create_project" in workflows
        assert "cost_analysis" in workflows
        assert "custom" in workflows

