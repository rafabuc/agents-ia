# Guía para Agregar Nuevos Agentes

Esta guía detalla el proceso completo para crear y agregar nuevos agentes especializados al sistema DevOps AI Platform.

## 📋 Tabla de Contenidos

1. [Conceptos Básicos](#conceptos-básicos)
2. [Estructura de un Agente](#estructura-de-un-agente)
3. [Paso a Paso: Crear un Nuevo Agente](#paso-a-paso-crear-un-nuevo-agente)
4. [Ejemplo Completo: Monitoring Agent](#ejemplo-completo-monitoring-agent)
5. [Integración con el Orchestrator](#integración-con-el-orchestrator)
6. [Testing del Nuevo Agente](#testing-del-nuevo-agente)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## 🎯 Conceptos Básicos

### ¿Qué es un Agente?

Un agente en nuestro sistema es una entidad especializada que:
- **Tiene un dominio específico** (monitoring, security, testing, etc.)
- **Utiliza herramientas especializadas** para su dominio
- **Hereda de `BaseAgent`** para funcionalidad común
- **Se integra con LangGraph** para coordinación
- **Mantiene estado** durante la ejecución

### Arquitectura de Agentes

```
Nuevo Agente
├── agent.py           # Lógica principal del agente
├── tools/            # Herramientas especializadas
│   ├── __init__.py
│   ├── tool1.py
│   └── tool2.py
├── workflows/        # Workflows específicos (opcional)
└── __init__.py       # Exportaciones del módulo
```

## 🏗️ Estructura de un Agente

### Componentes Requeridos:

1. **Clase Principal** (`agent.py`):
   - Hereda de `BaseAgent`
   - Define system prompt
   - Configura herramientas
   - Implementa métodos específicos

2. **Herramientas** (`tools/`):
   - Heredan de `BaseDevOpsTool`
   - Encapsulan operaciones específicas
   - Manejan errores y logging

3. **Configuración** (`__init__.py`):
   - Exporta clases públicas
   - Define interface del módulo

## 📝 Paso a Paso: Crear un Nuevo Agente

### Paso 1: Crear Estructura de Directorios

```bash
# Crear directorios del nuevo agente
mkdir -p agents/monitoring_agent/tools
mkdir -p agents/monitoring_agent/workflows

# Crear archivos básicos
touch agents/monitoring_agent/__init__.py
touch agents/monitoring_agent/agent.py
touch agents/monitoring_agent/tools/__init__.py
```

### Paso 2: Implementar la Clase Base del Agente

Crear `agents/monitoring_agent/agent.py`:

```python
"""
Monitoring Agent for DevOps AI Platform
Handles monitoring, alerting, and observability workflows
"""

from typing import List, Dict, Any
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseLanguageModel

from ..base.agent import BaseAgent
from .tools import PrometheusToolset, GrafanaTool, AlertManagerTool
from ..base.tools import ShellCommandTool


class MonitoringAgent(BaseAgent):
    """
    Specialized agent for monitoring and observability operations including:
    - Prometheus metrics configuration
    - Grafana dashboard management
    - AlertManager alert configuration
    - Log aggregation and analysis
    - Performance monitoring and optimization
    """

    def __init__(self, llm: BaseLanguageModel, **kwargs):
        # Initialize specialized tools for monitoring
        tools = [
            PrometheusToolset(),
            GrafanaTool(),
            AlertManagerTool(),
            ShellCommandTool(allowed_commands=[
                "kubectl", "helm", "curl", "prometheus", "grafana-cli"
            ])
        ]

        super().__init__(
            name="monitoring",
            llm=llm,
            tools=tools,
            **kwargs
        )

        # Monitoring specific state
        self.state.update({
            "active_dashboards": [],
            "configured_alerts": [],
            "metric_sources": [],
            "monitoring_status": "idle",
            "last_health_check": None
        })

    def get_system_prompt(self) -> str:
        """System prompt for Monitoring agent"""
        return """You are a specialized Monitoring agent responsible for observability, alerting, and performance monitoring.

Your primary responsibilities include:
1. Configure and manage Prometheus metrics collection
2. Create and maintain Grafana dashboards
3. Set up intelligent alerting with AlertManager
4. Monitor application and infrastructure health
5. Analyze performance metrics and trends
6. Generate monitoring reports and recommendations

Key capabilities:
- Design monitoring strategies for applications and infrastructure
- Create custom Grafana dashboards and panels
- Configure alert rules based on SLIs and SLOs
- Integrate with various data sources (Prometheus, Loki, etc.)
- Perform root cause analysis using metrics and logs
- Optimize monitoring stack performance

Always prioritize:
- Comprehensive coverage without alert fatigue
- Clear and actionable alerts
- Performance impact of monitoring overhead
- Security of monitoring data and access
- Documentation of monitoring configurations

When executing monitoring tasks:
1. Assess current monitoring coverage
2. Identify gaps and improvement opportunities
3. Implement changes with minimal service impact
4. Validate monitoring functionality
5. Document configurations and procedures
"""

    def _create_agent_executor(self) -> AgentExecutor:
        """Create the Monitoring agent executor"""
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

    # Métodos específicos del agente
    async def setup_monitoring_stack(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup complete monitoring stack"""
        self.logger.info("Setting up monitoring stack")

        task = f"""Setup monitoring stack with configuration:
        {config}

        Steps to execute:
        1. Deploy Prometheus for metrics collection
        2. Configure Grafana for visualization
        3. Setup AlertManager for notifications
        4. Configure data sources and service discovery
        5. Create basic dashboards for infrastructure monitoring
        6. Validate monitoring stack functionality
        """

        result = await self.execute(task, {"config": config, "operation": "setup"})

        if result["success"]:
            self.update_state("monitoring_status", "configured")

        return result

    async def create_dashboard(self, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Grafana dashboard"""
        dashboard_name = dashboard_config.get("name", "Custom Dashboard")
        self.logger.info(f"Creating dashboard: {dashboard_name}")

        task = f"""Create Grafana dashboard with configuration:
        {dashboard_config}

        Requirements:
        1. Design dashboard layout and panels
        2. Configure data sources and queries
        3. Set up appropriate visualizations
        4. Configure dashboard variables and templating
        5. Set permissions and sharing options
        6. Validate dashboard functionality
        """

        result = await self.execute(task, {"dashboard_config": dashboard_config})

        if result["success"]:
            active_dashboards = self.state.get("active_dashboards", [])
            active_dashboards.append(dashboard_name)
            self.update_state("active_dashboards", active_dashboards)

        return result

    async def configure_alerts(self, alert_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure monitoring alerts"""
        self.logger.info("Configuring monitoring alerts")

        task = f"""Configure monitoring alerts:
        {alert_config}

        Alert configuration steps:
        1. Analyze SLIs and define appropriate SLOs
        2. Create alert rules in Prometheus
        3. Configure AlertManager routing and notifications
        4. Set up escalation policies
        5. Test alert functionality
        6. Document alert procedures
        """

        result = await self.execute(task, {"alert_config": alert_config})

        if result["success"]:
            configured_alerts = self.state.get("configured_alerts", [])
            configured_alerts.extend(alert_config.get("alerts", []))
            self.update_state("configured_alerts", configured_alerts)

        return result

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "monitoring_status": self.state.get("monitoring_status"),
            "active_dashboards": self.state.get("active_dashboards", []),
            "configured_alerts": len(self.state.get("configured_alerts", [])),
            "metric_sources": self.state.get("metric_sources", []),
            "last_health_check": self.state.get("last_health_check")
        }
```

### Paso 3: Crear Herramientas Especializadas

Crear `agents/monitoring_agent/tools/prometheus.py`:

```python
"""
Prometheus Tool for Monitoring Agent
"""

import yaml
import requests
from typing import Dict, Any, List
from pathlib import Path

from ...base.tools import BaseDevOpsTool


class PrometheusToolset(BaseDevOpsTool):
    """Tool for managing Prometheus configuration and queries"""

    name: str = "prometheus"
    description: str = "Manage Prometheus metrics collection and querying"

    def _run(self, action: str, **kwargs) -> Dict[str, Any]:
        """Execute Prometheus operations"""
        self.log_execution("prometheus", {"action": action, "kwargs": kwargs})

        try:
            if action == "configure":
                return self._configure_prometheus(kwargs.get("config"))
            elif action == "query":
                return self._execute_query(
                    kwargs.get("query"),
                    kwargs.get("prometheus_url", "http://localhost:9090")
                )
            elif action == "add_target":
                return self._add_scrape_target(kwargs.get("target_config"))
            elif action == "create_rule":
                return self._create_alert_rule(kwargs.get("rule_config"))
            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _configure_prometheus(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure Prometheus"""
        try:
            # Generate Prometheus configuration
            prometheus_config = self._generate_prometheus_config(config)

            # Write configuration file
            config_path = Path("infrastructure/monitoring/prometheus/prometheus.yml")
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, "w") as f:
                yaml.dump(prometheus_config, f, default_flow_style=False)

            return {
                "success": True,
                "message": "Prometheus configuration created",
                "config_path": str(config_path)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_prometheus_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Prometheus YAML configuration"""
        return {
            "global": {
                "scrape_interval": config.get("scrape_interval", "15s"),
                "evaluation_interval": config.get("evaluation_interval", "15s")
            },
            "scrape_configs": config.get("scrape_configs", [
                {
                    "job_name": "prometheus",
                    "static_configs": [{"targets": ["localhost:9090"]}]
                }
            ]),
            "rule_files": config.get("rule_files", [
                "rules/*.yml"
            ]),
            "alerting": {
                "alertmanagers": config.get("alertmanagers", [
                    {"static_configs": [{"targets": ["localhost:9093"]}]}
                ])
            }
        }

    def _execute_query(self, query: str, prometheus_url: str) -> Dict[str, Any]:
        """Execute Prometheus query"""
        try:
            response = requests.get(
                f"{prometheus_url}/api/v1/query",
                params={"query": query},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "query": query,
                    "result": data["data"]["result"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Query failed: {response.text}"
                }

        except Exception as e:
            return {"success": False, "error": str(e)}
```

### Paso 4: Crear Archivo de Inicialización

Crear `agents/monitoring_agent/__init__.py`:

```python
"""
Monitoring Agent Module
"""

from .agent import MonitoringAgent
from .tools import PrometheusToolset, GrafanaTool, AlertManagerTool

__all__ = ["MonitoringAgent", "PrometheusToolset", "GrafanaTool", "AlertManagerTool"]
```

### Paso 5: Registrar el Agente en el Sistema

Actualizar `agents/__init__.py`:

```python
"""
DevOps AI Agents Package
"""

from .base.agent import BaseAgent
from .cicd_agent.agent import CICDAgent
from .infrastructure_agent.agent import InfrastructureAgent
from .monitoring_agent.agent import MonitoringAgent  # ← Agregar nuevo agente

__all__ = [
    "BaseAgent",
    "CICDAgent",
    "InfrastructureAgent",
    "MonitoringAgent"  # ← Agregar a la lista
]
```

## 🔄 Integración con el Orchestrator

### Paso 6: Agregar al LangGraph Orchestrator

Actualizar `orchestrator/graph.py`:

```python
# En el método _initialize_agents()
def _initialize_agents(self):
    """Initialize all DevOps agents"""
    try:
        self.agents = {
            "cicd": CICDAgent(self.llm, verbose=False),
            "infrastructure": InfrastructureAgent(self.llm, verbose=False),
            "monitoring": MonitoringAgent(self.llm, verbose=False),  # ← Agregar aquí
        }
        self.logger.info(f"Initialized {len(self.agents)} agents")
    except Exception as e:
        self.logger.error(f"Failed to initialize agents: {str(e)}")
        raise

# En el método _build_graph()
def _build_graph(self):
    """Build the LangGraph workflow"""
    try:
        workflow = StateGraph(DevOpsState)

        # Agregar nodos existentes
        workflow.add_node("start", self._start_workflow)
        workflow.add_node("cicd_agent", self._execute_cicd_agent)
        workflow.add_node("infrastructure_agent", self._execute_infrastructure_agent)
        workflow.add_node("monitoring_agent", self._execute_monitoring_agent)  # ← Nuevo nodo

        # ... resto de nodos

# Agregar método de ejecución del nuevo agente
async def _execute_monitoring_agent(self, state: DevOpsState) -> DevOpsState:
    """Execute Monitoring agent"""
    try:
        self.logger.info("Executing Monitoring agent")

        state = StateManager.update_agent_status(state, "monitoring", "started")

        # Determinar tarea de monitoring
        monitoring_task = self._determine_monitoring_task(state)

        # Ejecutar Monitoring agent
        monitoring_agent = self.agents["monitoring"]
        result = await monitoring_agent.execute(monitoring_task, state["context"])

        if result["success"]:
            state = StateManager.update_agent_status(
                state, "monitoring", "completed", result
            )
        else:
            state = StateManager.update_agent_status(
                state, "monitoring", "failed", result
            )
            state = StateManager.add_error(
                state, "monitoring", result.get("error", "Monitoring execution failed")
            )

    except Exception as e:
        self.logger.error(f"Monitoring agent execution failed: {str(e)}")
        state = StateManager.add_error(state, "monitoring", str(e))
        state = StateManager.update_agent_status(state, "monitoring", "failed")

    return state

def _determine_monitoring_task(self, state: DevOpsState) -> str:
    """Determine Monitoring task based on workflow context"""
    user_request = state["user_request"]

    if "dashboard" in user_request.lower():
        return f"Create monitoring dashboard: {user_request}"
    elif "alert" in user_request.lower():
        return f"Configure monitoring alerts: {user_request}"
    else:
        return f"Setup monitoring: {user_request}"
```

### Paso 7: Actualizar Routing Logic

Actualizar los métodos de routing en el orchestrator:

```python
def _determine_agent_routing(self, state: DevOpsState) -> str:
    """Determine which agent(s) to route to"""
    user_request = state["user_request"].lower()

    # Detectar necesidad de monitoring
    needs_monitoring = any(keyword in user_request for keyword in [
        "monitor", "dashboard", "alert", "metrics", "observability"
    ])

    # Detectar otras necesidades
    needs_cicd = any(keyword in user_request for keyword in [
        "build", "test", "deploy", "pipeline", "ci/cd"
    ])

    needs_infrastructure = any(keyword in user_request for keyword in [
        "infrastructure", "terraform", "kubernetes", "cluster"
    ])

    # Determinar routing
    if needs_monitoring and (needs_cicd or needs_infrastructure):
        state["context"]["routing"] = "multi_agent"
    elif needs_monitoring:
        state["context"]["routing"] = "monitoring"
    elif needs_cicd and needs_infrastructure:
        state["context"]["routing"] = "both"
    # ... resto de la lógica

    return state["context"]["routing"]
```

## 🧪 Testing del Nuevo Agente

### Paso 8: Crear Tests

Crear `tests/unit/test_monitoring_agent.py`:

```python
"""
Tests for Monitoring Agent
"""

import pytest
from unittest.mock import Mock, AsyncMock
from agents.monitoring_agent import MonitoringAgent


class TestMonitoringAgent:
    """Test suite for MonitoringAgent"""

    @pytest.fixture
    def mock_llm(self):
        """Mock LLM for testing"""
        llm = Mock()
        llm.ainvoke = AsyncMock()
        return llm

    @pytest.fixture
    def monitoring_agent(self, mock_llm):
        """Create MonitoringAgent instance for testing"""
        return MonitoringAgent(mock_llm)

    def test_agent_initialization(self, monitoring_agent):
        """Test agent initializes correctly"""
        assert monitoring_agent.name == "monitoring"
        assert len(monitoring_agent.tools) > 0
        assert "active_dashboards" in monitoring_agent.state
        assert "configured_alerts" in monitoring_agent.state

    def test_get_system_prompt(self, monitoring_agent):
        """Test system prompt is defined"""
        prompt = monitoring_agent.get_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "monitoring" in prompt.lower()

    @pytest.mark.asyncio
    async def test_setup_monitoring_stack(self, monitoring_agent):
        """Test monitoring stack setup"""
        # Mock the execute method
        monitoring_agent.execute = AsyncMock(return_value={
            "success": True,
            "result": "Monitoring stack configured"
        })

        config = {
            "prometheus": {"enabled": True},
            "grafana": {"enabled": True}
        }

        result = await monitoring_agent.setup_monitoring_stack(config)

        assert result["success"] is True
        assert monitoring_agent.state["monitoring_status"] == "configured"

    def test_get_monitoring_status(self, monitoring_agent):
        """Test getting monitoring status"""
        # Set some state
        monitoring_agent.state.update({
            "monitoring_status": "active",
            "active_dashboards": ["Dashboard 1", "Dashboard 2"]
        })

        status = monitoring_agent.get_monitoring_status()

        assert status["monitoring_status"] == "active"
        assert len(status["active_dashboards"]) == 2
```

### Paso 9: Crear Tests de Integración

Crear `tests/integration/test_monitoring_integration.py`:

```python
"""
Integration tests for Monitoring Agent
"""

import pytest
from orchestrator import DevOpsWorkflowGraph
from langchain_openai import ChatOpenAI


class TestMonitoringIntegration:
    """Integration tests for monitoring workflows"""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator for testing"""
        # Use a mock LLM for testing
        mock_llm = ChatOpenAI(model="gpt-3.5-turbo", api_key="test-key")
        return DevOpsWorkflowGraph(mock_llm)

    @pytest.mark.asyncio
    async def test_monitoring_workflow(self, orchestrator):
        """Test complete monitoring workflow"""
        # Mock the agent execution
        orchestrator.agents["monitoring"].execute = AsyncMock(
            return_value={"success": True, "result": "Dashboard created"}
        )

        result = await orchestrator.execute_workflow(
            workflow_type="monitoring",
            user_request="Create monitoring dashboard for application",
            context={"application": "test-app"}
        )

        assert result["success"] is True
        assert "monitoring" in result["summary"]["agents_completed"]
```

## 🔧 Best Practices

### 1. **Naming Conventions**
```python
# Agente
class MonitoringAgent  # PascalCase con "Agent" suffix

# Herramientas
class PrometheusToolset  # PascalCase con descriptive suffix

# Métodos
async def setup_monitoring_stack()  # snake_case, descriptivo
```

### 2. **Error Handling**
```python
try:
    # Operación del agente
    result = await operation()
    if not result["success"]:
        state = StateManager.add_error(state, agent_name, result["error"])
except Exception as e:
    self.logger.error(f"Operation failed: {str(e)}")
    return {"success": False, "error": str(e)}
```

### 3. **Logging**
```python
# En el agente
self.logger.info(f"Starting operation: {operation_name}")
self.log_execution("tool_name", {"param": value})

# En las herramientas
self.log_execution("action_name", {"details": details})
```

### 4. **State Management**
```python
# Actualizar estado consistentemente
self.update_state("key", value)
state = StateManager.update_agent_status(state, "agent_name", "status")
state = StateManager.add_error(state, "agent_name", "error_message")
```

### 5. **Documentation**
```python
"""
Agent/Tool description

Key responsibilities:
1. Responsibility 1
2. Responsibility 2

Capabilities:
- Capability 1
- Capability 2
"""
```

## ❗ Troubleshooting

### Problemas Comunes:

1. **Import Errors**
```bash
# Verificar que el agente esté en __init__.py
python -c "from agents import MonitoringAgent"
```

2. **Tool Registration**
```python
# Verificar que las herramientas estén en la lista de tools del agente
assert "prometheus" in [tool.name for tool in agent.tools]
```

3. **Orchestrator Integration**
```bash
# Verificar que el agente esté registrado
python -c "from orchestrator.graph import DevOpsWorkflowGraph; print(list(DevOpsWorkflowGraph(None).agents.keys()))"
```

4. **Testing Issues**
```bash
# Ejecutar tests específicos del agente
pytest tests/unit/test_monitoring_agent.py -v
```

## ✅ Checklist de Verificación

Antes de considerar completo tu nuevo agente:

- [ ] ✅ Estructura de directorios creada
- [ ] ✅ Clase principal hereda de `BaseAgent`
- [ ] ✅ System prompt definido y específico
- [ ] ✅ Herramientas implementadas y funcionando
- [ ] ✅ Métodos específicos del dominio creados
- [ ] ✅ Estado del agente inicializado correctamente
- [ ] ✅ Agregado a `agents/__init__.py`
- [ ] ✅ Integrado en el orchestrator
- [ ] ✅ Routing logic actualizada
- [ ] ✅ Tests unitarios creados
- [ ] ✅ Tests de integración funcionando
- [ ] ✅ Documentación actualizada
- [ ] ✅ Error handling implementado
- [ ] ✅ Logging configurado

## 🚀 Próximos Pasos

Después de crear tu agente:

1. **Testear exhaustivamente** en diferentes escenarios
2. **Optimizar performance** de herramientas y queries
3. **Documentar casos de uso** específicos
4. **Crear ejemplos** de implementación
5. **Integrar con otros agentes** si es necesario
6. **Monitorear performance** en producción

---

**¡Felicidades! Has agregado exitosamente un nuevo agente al sistema DevOps AI Platform.**

Esta guía te proporciona todo lo necesario para extender el sistema con nuevas capacidades especializadas manteniendo la consistencia y calidad del código.