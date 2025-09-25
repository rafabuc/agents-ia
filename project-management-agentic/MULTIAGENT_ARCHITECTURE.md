# 🚀 Multi-Agent Architecture - PMP Project Management System

## 🎯 Overview

El sistema ha sido completamente refactorizado de una arquitectura monolítica a un sistema multi-agente modular y especializado. Esta nueva arquitectura proporciona:

- **🧠 Inteligencia Distribuida**: Cada agente es experto en su dominio
- **🤝 Coordinación Automática**: Orchestrator inteligente que ruta peticiones
- **💬 Lenguaje Natural**: Comprensión avanzada con contexto conversacional
- **🔧 Modularidad**: Fácil mantenimiento y escalabilidad
- **⚡ Performance**: Procesamiento paralelo cuando es posible

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Interface                        │
│                     main.py                            │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                Agent Factory                            │
│              agent_factory.py                          │
│  • Legacy compatibility                                │
│  • New agent registration                              │
│  • Orchestrator management                             │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Agent Orchestrator                         │
│               orchestrator.py                           │
│  • Intent analysis                                     │
│  • Agent routing                                       │
│  • Multi-agent coordination                            │
└─────────────┬───────────────────────────┬───────────────┘
              │                           │
              ▼                           ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│   ProjectManagerAgent   │    │    Specialist Agents    │
│ project_manager_agent.py│    │                         │
│                         │    │  • DocumentAgent        │
│ • Main coordinator      │    │  • RiskManagementAgent  │
│ • User interaction      │    │  • (Future agents...)   │
│ • Conversation context  │    │                         │
│ • High-level decisions  │    │                         │
└─────────────────────────┘    └─────────────────────────┘
```

## 🤖 Agentes Especializados

### 1. **ProjectManagerAgent** (Coordinador Principal)
**Archivo**: `agents/project_manager_agent.py`
o
**Responsabilidades**:
- 🎯 Interfaz principal con el usuario
- 📝 Gestión de proyectos de alto nivel
- 🧠 Mantenimiento de contexto conversacional
- 🚦 Decisiones de delegación a especialistas
- 📊 Coordinación de workflows complejos

**Capacidades**:
- Crear y gestionar proyectos
- Entender peticiones en lenguaje natural
- Mantener contexto entre conversaciones
- Proporcionar sugerencias proactivas

### 2. **DocumentAgent** (Especialista en Documentación)
**Archivo**: `agents/document_agent.py`

**Responsabilidades**:
- 📄 Creación de Project Charters
- 📊 Generación de Work Breakdown Structures (WBS)
- 📋 Gestión de plantillas PMP/SAFe
- 📂 Control de versiones de documentos

**Capacidades**:
- Generar documentos profesionales siguiendo estándares PMI
- Personalizar contenido según contexto del proyecto
- Crear plantillas por industria
- Mantener consistencia entre documentos relacionados

### 3. **RiskManagementAgent** (Especialista en Riesgos)
**Archivo**: `agents/risk_management_agent.py`

**Responsabilidades**:
- ⚠️ Identificación y catalogación de riesgos
- 📈 Análisis cuantitativo (probabilidad/impacto)
- 🛡️ Desarrollo de estrategias de mitigación
- 📊 Análisis Monte Carlo para predicción

**Capacidades**:
- Identificar riesgos específicos por proyecto e industria
- Calcular scores usando matrices de riesgo
- Generar registros de riesgo profesionales
- Análisis predictivo avanzado

## 🎛️ Agent Orchestrator

**Archivo**: `agents/orchestrator.py`

El orchestrator es el cerebro del sistema que:

1. **Analiza Intenciones**: Usa LLM para entender qué quiere el usuario
2. **Ruta Inteligentemente**: Decide qué agente(s) deben manejar la petición
3. **Coordina Colaboración**: Maneja workflows que requieren múltiples agentes
4. **Combina Resultados**: Integra respuestas de varios agentes de forma coherente

### Tipos de Routing

```python
# Routing simple (un agente)
"crear charter" → DocumentAgent

# Routing complejo (múltiples agentes)
"crear proyecto completo" → ProjectManagerAgent + DocumentAgent + RiskManagementAgent

# Routing contextual (basado en historial)
Usuario: "Crear proyecto App"
Sistema: (crea proyecto)
Usuario: "Ahora genera el charter"
Sistema: → DocumentAgent (con contexto del proyecto recién creado)
```

## 💻 Comandos CLI Actualizados

### Nuevos Comandos

```bash
# Chat con sistema multi-agente (modo por defecto)
python main.py chat --agent auto

# Chat con agente específico
python main.py chat --agent project_manager_agent
python main.py chat --agent document_agent
python main.py chat --agent risk_management_agent

# Estado del sistema multi-agente
python main.py multiagent-status

# Sugerencias de migración
python main.py migrate pmp_project
```

### Modos de Operación

1. **Auto Mode** (`--agent auto`): Orchestrator decide automáticamente
2. **Multiagent Mode** (`--agent multiagent`): Colaboración explícita entre agentes
3. **Direct Mode** (`--agent document_agent`): Comunicación directa con agente específico
4. **Legacy Mode** (`--agent pmp_project`): Compatibilidad hacia atrás

## 🧪 Testing Framework

**Archivo**: `tests/test_multiagent_system.py`

### Cobertura de Testing

```python
# Test de orchestrator
TestAgentOrchestrator
├── test_orchestrator_initialization()
├── test_agent_registration()
├── test_single_agent_routing()
├── test_intent_analysis()
└── test_get_system_status()

# Test de agentes individuales
TestProjectManagerAgent
TestDocumentAgent
TestRiskManagementAgent

# Test de integración
TestIntegration
├── test_end_to_end_project_creation()
├── test_agent_capability_mapping()
└── test_multiagent_coordination()
```

### Ejecutar Tests

```bash
# Todos los tests
python -m pytest tests/test_multiagent_system.py -v

# Test específico
python -m pytest tests/test_multiagent_system.py::TestAgentOrchestrator -v

# Con coverage
python -m pytest tests/test_multiagent_system.py --cov=agents
```

## 🔄 Flujos de Trabajo Típicos

### 1. Creación de Proyecto Completo

```
Usuario: "Crear proyecto completo para app móvil e-commerce"
    ↓
Orchestrator analiza → "Requiere múltiples agentes"
    ↓
ProjectManagerAgent: Crea proyecto en DB
    ↓ (coordina con)
DocumentAgent: Genera Project Charter
    ↓ (coordina con)
RiskManagementAgent: Crea Risk Register inicial
    ↓
Orchestrator combina respuestas → Usuario recibe resultado integrado
```

### 2. Chat Contextual

```
Usuario: "Crear proyecto MiApp"
Sistema: ✅ "Proyecto MiApp creado (ID: 123)"

Usuario: "Generar charter"
Sistema: (usa contexto: proyecto 123) → DocumentAgent
Sistema: ✅ "Charter generado para MiApp"

Usuario: "¿Qué riesgos tiene?"
Sistema: (usa contexto: proyecto 123) → RiskManagementAgent
Sistema: ⚠️ "Riesgos identificados: [lista detallada]"
```

## 🚀 Beneficios de la Nueva Arquitectura

### Para Desarrolladores

- **🔧 Mantenibilidad**: Código modular, cada agente tiene responsabilidad única
- **🧪 Testabilidad**: Tests unitarios por agente, integración separada
- **📈 Escalabilidad**: Agregar nuevos agentes es simple y no invasivo
- **🔄 Reutilización**: Agentes usables en otros contextos
- **🐛 Debugging**: Logs detallados por agente facilitan troubleshooting

### Para Usuarios

- **💬 Naturalidad**: Conversaciones fluidas en lenguaje natural
- **🧠 Inteligencia**: Respuestas especializadas y contextuales
- **⚡ Eficiencia**: Procesamiento paralelo y sugerencias proactivas
- **🎯 Precisión**: Cada agente es experto en su dominio
- **🔄 Continuidad**: Contexto mantenido entre interacciones

### Para el Negocio

- **📊 Especialización**: Calidad profesional en cada área (documentos, riesgos, etc.)
- **🚀 Productividad**: Workflows automatizados y sugerencias inteligentes
- **🛡️ Robustez**: Falla de un agente no afecta el sistema completo
- **📈 Escalabilidad**: Fácil adición de nuevas capacidades
- **🔍 Trazabilidad**: Auditoría completa de decisiones y acciones

## 🔮 Roadmap de Expansión

### Agentes Futuros (Siguientes Sprints)

1. **ScheduleAgent** - Gestión de cronogramas y critical path
2. **BudgetAgent** - Análisis financiero y cost management
3. **StakeholderAgent** - Gestión de interesados y comunicación
4. **QualityAgent** - Control de calidad y testing
5. **ComplianceAgent** - Cumplimiento regulatorio y auditoría

### Funcionalidades Avanzadas

- **🔄 Workflow Orchestration**: Workflows complejos predefinidos
- **📊 Analytics Dashboard**: Métricas y KPIs en tiempo real
- **🔗 External Integrations**: Jira, Trello, MS Project
- **🌐 Multi-tenant**: Soporte empresarial multi-organización
- **🔒 Advanced Security**: Role-based access, encryption

## 📝 Migración desde Sistema Legacy

### Compatibilidad Hacia Atrás

El sistema mantiene **compatibilidad completa** con comandos legacy:

```bash
# Estos comandos siguen funcionando
python main.py chat --agent pmp_project
python main.py chat --agent cost_budget
python main.py chat --agent template
```

### Migración Gradual Recomendada

1. **Familiarización** (Semana 1-2)
   ```bash
   python main.py multiagent-status
   python main.py chat --agent auto
   ```

2. **Adopción Parcial** (Semana 3-4)
   - Usar nuevos agentes para tareas específicas
   - Comparar resultados con sistema legacy

3. **Migración Completa** (Semana 5+)
   - Configurar `--agent auto` como default
   - Entrenar usuarios en nuevo sistema
   - Deprecar comandos legacy gradualmente

### Sugerencias de Migración

```bash
# Obtener sugerencias específicas
python main.py migrate pmp_project
# → "Consider migrating from 'pmp_project' to 'project_manager_agent' for enhanced capabilities"

python main.py migrate template
# → "Consider migrating from 'template' to 'document_agent' for enhanced capabilities"
```

## 🤝 Contribución y Desarrollo

### Agregar Nuevo Agente

1. **Crear clase** heredando de `BaseAgent`
2. **Implementar métodos** requeridos (`process`, `get_system_prompt`)
3. **Registrar en Factory** con sus capacidades
4. **Agregar tests** correspondientes
5. **Actualizar documentación**

### Ejemplo - Nuevo StakeholderAgent

```python
# 1. Crear agents/stakeholder_agent.py
class StakeholderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="stakeholder_agent",
            description="Specialized in stakeholder management"
        )

# 2. Registrar en AgentFactory
self._agent_classes["stakeholder_agent"] = StakeholderAgent

# 3. Configurar capacidades en orchestrator
"stakeholder_agent": [AgentCapability.STAKEHOLDER_MAPPING]

# 4. Tests en test_multiagent_system.py
class TestStakeholderAgent:
    def test_stakeholder_mapping(self):
        # Test implementation
```

---

**✅ La refactorización está completa y el sistema multi-agente está listo para producción.**

**🚀 Next Steps**: Probar el sistema, ajustar basado en feedback, y comenzar desarrollo de agentes adicionales según roadmap.

**📞 Support**: Para preguntas sobre la nueva arquitectura, revisar logs en `./logs/` o usar `python main.py multiagent-status`.