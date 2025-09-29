# DevOps AI Platform

Una plataforma avanzada de DevOps basada en agentes de IA que automatiza el ciclo de vida completo de aplicaciones, desde desarrollo local hasta producción en AWS EKS.

## 🚀 Características Principales

- **Arquitectura Multi-Agente**: Sistema de agentes especializados coordinados por LangGraph
- **Automatización Inteligente**: Automatización de CI/CD, infraestructura y monitoreo
- **Integración Cloud-Native**: Soporte completo para Kubernetes y AWS EKS
- **IA Generativa**: Powered by LangChain y LangGraph para decisiones inteligentes
- **Infraestructura como Código**: Gestión completa con Terraform
- **Observabilidad Avanzada**: Monitoreo, alertas y análisis predictivo

## 📋 Requisitos Previos

- Python 3.10+
- Docker y Docker Compose
- Kubernetes CLI (kubectl)
- Terraform
- AWS CLI (para deployment en EKS)
- Git

## 🛠️ Instalación Rápida

```bash
# Clonar el repositorio
git clone <repository-url>
cd devops-agent

# Configurar entorno de desarrollo
make dev-setup

# Instalar dependencias
make install-dev

# Crear archivo de configuración
cp .env.example .env
# Editar .env con tus claves de API
```

## 🏗️ Arquitectura

### Agentes Especializados

1. **CI/CD Agent** (`agents/cicd_agent/`)
   - Automatización de pipelines de GitHub Actions
   - Builds y deployments automatizados
   - Testing y quality assurance

2. **Infrastructure Agent** (`agents/infrastructure_agent/`)
   - Provisioning con Terraform
   - Gestión de clusters EKS
   - Optimización de costos y compliance

3. **Monitoring Agent** (próximamente)
   - Configuración de Prometheus/Grafana
   - Alertas inteligentes
   - Análisis predictivo

### Orquestador LangGraph

El sistema utiliza LangGraph para coordinar la ejecución de múltiples agentes:

```python
from orchestrator import DevOpsWorkflowGraph
from langchain_openai import ChatOpenAI

# Inicializar orquestador
llm = ChatOpenAI(model="gpt-4")
orchestrator = DevOpsWorkflowGraph(llm)

# Ejecutar workflow
result = await orchestrator.execute_workflow(
    workflow_type="deployment",
    user_request="Deploy application to production",
    context={"environment": "production", "version": "v1.2.0"}
)
```

## 📁 Estructura del Proyecto

```
devops-agent/
├── agents/                     # Agentes especializados
│   ├── base/                  # Clases base y herramientas comunes
│   ├── cicd_agent/            # Agente CI/CD
│   └── infrastructure_agent/   # Agente de infraestructura
├── orchestrator/              # LangGraph orchestrator
│   ├── graph.py              # Definición del workflow
│   ├── state.py              # Gestión de estado
│   └── workflows/            # Workflows específicos
├── tools/                     # Herramientas especializadas
├── rag/                      # Sistema RAG para knowledge base
├── infrastructure/           # Infrastructure as Code
│   ├── terraform/           # Módulos Terraform
│   └── kubernetes/          # Manifiestos K8s
├── apps/                    # Aplicaciones
│   ├── ai_services/        # API FastAPI
│   └── django_app/         # Aplicación Django
└── tests/                  # Tests unitarios e integración
```

## 🚀 Uso Básico

### 1. Ejemplo: CI/CD Pipeline

```python
from agents import CICDAgent
from langchain_openai import ChatOpenAI

# Crear agente CI/CD
llm = ChatOpenAI(model="gpt-4")
cicd_agent = CICDAgent(llm)

# Ejecutar pipeline
result = await cicd_agent.run_pipeline(
    pipeline_name="build",
    parameters={"branch": "main", "environment": "staging"}
)
```

### 2. Ejemplo: Provisioning de Infraestructura

```python
from agents import InfrastructureAgent

# Crear agente de infraestructura
infra_agent = InfrastructureAgent(llm)

# Provisionar cluster EKS
result = await infra_agent.manage_eks_cluster(
    action="create",
    cluster_config={
        "name": "production-cluster",
        "version": "1.28",
        "node_groups": [
            {
                "name": "workers",
                "instance_type": "t3.medium",
                "desired_size": 3
            }
        ]
    }
)
```

### 3. Ejemplo: Workflow Completo

```python
from orchestrator import DevOpsWorkflowGraph

orchestrator = DevOpsWorkflowGraph(llm)

# Ejecutar deployment completo
result = await orchestrator.execute_workflow(
    workflow_type="deployment",
    user_request="Deploy new version with infrastructure scaling",
    context={
        "application": "my-app",
        "version": "v2.0.0",
        "environment": "production",
        "auto_scale": True
    }
)

print(f"Deployment Status: {result['success']}")
print(f"Summary: {result['summary']}")
```

## 🧪 Testing

```bash
# Ejecutar todos los tests
make test

# Tests con coverage
make test-cov

# Tests unitarios solamente
make test-unit

# Tests de integración
make test-integration
```

## 🔧 Desarrollo

### Configuración del Entorno

```bash
# Setup completo de desarrollo
make dev-setup

# Formatear código
make format

# Linting
make lint

# Type checking
make type-check

# CI completo
make ci
```

### Estructura de Agentes

Para crear un nuevo agente:

1. Heredar de `BaseAgent`
2. Implementar `get_system_prompt()`
3. Implementar `_create_agent_executor()`
4. Definir herramientas especializadas

```python
from agents.base import BaseAgent

class MyCustomAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return "You are a specialized agent for..."

    def _create_agent_executor(self):
        # Implementar executor específico
        pass
```

## 🐳 Docker

```bash
# Build imagen
make docker-build

# Ejecutar contenedor
make docker-run

# Docker Compose (desarrollo)
make docker-compose-up
```

## ☸️ Kubernetes

```bash
# Deploy en cluster local
make k8s-deploy

# Configurar Terraform
make terraform-init
make terraform-plan
make terraform-apply
```

## 📊 Monitoreo

```bash
# Iniciar stack de monitoreo
make start-monitoring

# Ver logs
make logs

# Health check
make health-check
```

## 🔒 Seguridad

- Gestión de secretos con HashiCorp Vault
- Escaneo de vulnerabilidades integrado
- Policies de seguridad automatizadas
- Compliance con estándares (CIS, SOC2)

```bash
# Ejecutar escaneo de seguridad
make security-scan
```

## 📝 Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```bash
# APIs de IA
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Base de datos
DATABASE_URL=postgresql://user:pass@localhost/devops_ai
REDIS_URL=redis://localhost:6379

# AWS
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_DEFAULT_REGION=us-west-2

# Configuración
LOG_LEVEL=INFO
DEBUG=False
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push a la branch (`git push origin feature/amazing-feature`)
5. Abrir Pull Request

## 📚 Documentación

- [Documentación de Arquitectura](docs/architecture/)
- [Guía de Deployment](docs/deployment/)
- [Troubleshooting](docs/troubleshooting/)

## 🗺️ Roadmap

### Ciclo 1 - MVP Base ✅
- [x] Aplicación Django básica
- [x] CI/CD Agent
- [x] Infrastructure Agent
- [x] LangGraph Orchestrator

### Ciclo 2 - Kubernetes Local (En Progreso)
- [ ] Helm charts
- [ ] Monitoring Agent
- [ ] Testing Agent
- [ ] Local Kubernetes setup

### Ciclo 3 - Infrastructure as Code
- [ ] Terraform modules completos
- [ ] Security Agent
- [ ] Configuration Agent
- [ ] GitOps con ArgoCD

### Ciclo 4 - AWS EKS + Producción
- [ ] EKS deployment automation
- [ ] Advanced monitoring
- [ ] Auto-scaling
- [ ] Cost optimization

### Ciclo 5 - IA Avanzada
- [ ] Predictive analytics
- [ ] Auto-remediation
- [ ] ML-powered optimization
- [ ] Advanced compliance

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🆘 Soporte

- Crear issue en GitHub para bugs
- Discussiones para preguntas generales
- Email: devops-ai@company.com

## 🙏 Agradecimientos

- [LangChain](https://langchain.com/) por el framework de IA
- [LangGraph](https://langgraph.com/) por la orquestación multi-agente
- Comunidad open source por las herramientas y librerías