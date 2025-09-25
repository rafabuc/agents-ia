"""
Risk Management Agent - Specialized in project risk analysis and mitigation
Handles risk identification, assessment, mitigation planning, and monitoring
"""

from typing import Dict, Any, List, Optional
import json
import math
from datetime import datetime, timedelta
from enum import Enum

from .base_agent import BaseAgent
from storage.database_manager import DatabaseManager
from models.project import Project
from utils.logger import logger
from config.settings import settings


class RiskProbability(Enum):
    """Risk probability levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskImpact(Enum):
    """Risk impact levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskStatus(Enum):
    """Risk status"""
    OPEN = "open"
    MITIGATED = "mitigated"
    CLOSED = "closed"
    ACCEPTED = "accepted"


class RiskManagementAgent(BaseAgent):
    """
    Risk Management Agent - Specialized in comprehensive risk management

    This agent handles all aspects of project risk management:
    - Risk identification and cataloging
    - Probability and impact assessment
    - Risk scoring and prioritization
    - Mitigation strategy development
    - Risk monitoring and tracking
    - Monte Carlo analysis for schedule/budget risks
    """

    def __init__(self):
        super().__init__(
            name="risk_management_agent",
            description="Specialized agent for project risk management and analysis"
        )
        self.db_manager = DatabaseManager()

        # LLM is already initialized in BaseAgent as self.llm

        # Risk scoring matrix
        self.risk_matrix = {
            RiskProbability.LOW: 1,
            RiskProbability.MEDIUM: 2,
            RiskProbability.HIGH: 3
        }

        self.impact_matrix = {
            RiskImpact.LOW: 1,
            RiskImpact.MEDIUM: 2,
            RiskImpact.HIGH: 3
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for risk management"""
        return """Eres un Risk Management Agent experto especializado en la identificación, análisis y gestión de riesgos de proyectos.

Tu especialidad incluye:
1. **Identificación de Riesgos** - Detectar riesgos técnicos, de negocio, externos y de recursos
2. **Análisis Cuantitativo** - Probabilidad, impacto, scoring y priorización
3. **Estrategias de Mitigación** - Evitar, mitigar, transferir o aceptar riesgos
4. **Monitoreo Continuo** - Seguimiento y actualización de registros de riesgo
5. **Análisis Predictivo** - Monte Carlo y análisis de sensibilidad

Capacidades clave:
- Identificar riesgos específicos por tipo de proyecto e industria
- Calcular scores de riesgo usando matrices probabilidad/impacto
- Desarrollar planes de mitigación concretos y accionables
- Crear registros de riesgo profesionales siguiendo estándares PMI
- Analizar tendencias y patrones de riesgo
- Proporcionar recomendaciones proactivas

Metodologías aplicadas:
- **PMP Risk Management**: Siguiendo PMBOK Guide
- **Análisis Cuantitativo**: Monte Carlo, sensitivity analysis
- **Risk Response Strategies**: Avoid, Mitigate, Transfer, Accept

Cuando analices riesgos:
- Sé específico y concreto en la identificación
- Proporciona justificación para scoring
- Desarrolla mitigaciones realistas y específicas
- Considera riesgos secundarios y residuales
- Mantén perspectiva del contexto del proyecto

Siempre proporciona:
- Análisis fundamentado en experiencia
- Recomendaciones accionables
- Timeframes realistas para mitigación
- Asignación clara de responsabilidades
"""

    async def process_with_context(self, context) -> Dict[str, Any]:
        """Process risk management requests with full context"""
        try:
            user_input = context.user_input
            project_id = context.project_id

            # Analyze risk intent
            intent_analysis = self._analyze_risk_intent(user_input)

            if intent_analysis["intent"] == "create_risk_register":
                return await self._handle_risk_register_creation(intent_analysis, project_id)
            elif intent_analysis["intent"] == "identify_risks":
                return await self._handle_risk_identification(intent_analysis, project_id)
            elif intent_analysis["intent"] == "analyze_specific_risk":
                return await self._handle_specific_risk_analysis(intent_analysis, project_id)
            elif intent_analysis["intent"] == "risk_assessment":
                return await self._handle_risk_assessment(intent_analysis, project_id)
            elif intent_analysis["intent"] == "mitigation_planning":
                return await self._handle_mitigation_planning(intent_analysis, project_id)
            elif intent_analysis["intent"] == "monte_carlo_analysis":
                return await self._handle_monte_carlo_analysis(intent_analysis, project_id)
            else:
                return self._handle_general_risk_query(user_input, project_id)

        except Exception as e:
            logger.error(f"Error in RiskManagementAgent.process_with_context: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "🚫 Error procesando la solicitud de análisis de riesgo. Intenta de nuevo."
            }

    def process(self, user_input: str, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Process request (legacy method for backward compatibility)"""
        class SimpleContext:
            def __init__(self, user_input, project_id):
                self.user_input = user_input
                self.project_id = project_id

        context = SimpleContext(user_input, project_id)

        import asyncio
        try:
            return asyncio.run(self.process_with_context(context))
        except RuntimeError:
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.process_with_context(context))
                return future.result()

    def _analyze_risk_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze what type of risk management is being requested"""
        analysis_prompt = f"""Analiza esta solicitud relacionada con gestión de riesgos:

Solicitud: "{user_input}"

Intenciones posibles:
- create_risk_register: Crear un risk register completo
- identify_risks: Identificar riesgos específicos
- analyze_specific_risk: Analizar un riesgo particular
- risk_assessment: Evaluar probabilidad e impacto
- mitigation_planning: Desarrollar planes de mitigación
- monte_carlo_analysis: Análisis Monte Carlo
- general_risk: Consulta general sobre riesgos

Responde en JSON:
{{
    "intent": "intención_detectada",
    "confidence": 0.8,
    "parameters": {{
        "risk_type": "tipo de riesgo si se menciona",
        "analysis_scope": "alcance del análisis",
        "specific_risk": "riesgo específico mencionado"
    }}
}}"""

        try:
            response = self.llm.invoke(analysis_prompt).content

            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._fallback_risk_intent_detection(user_input)

        except Exception as e:
            logger.warning(f"LLM risk intent analysis failed: {str(e)}")
            return self._fallback_risk_intent_detection(user_input)

    def _fallback_risk_intent_detection(self, user_input: str) -> Dict[str, Any]:
        """Fallback risk intent detection"""
        user_input_lower = user_input.lower()

        if any(keyword in user_input_lower for keyword in ["risk register", "registro de riesgos", "crear riesgos"]):
            return {"intent": "create_risk_register", "confidence": 0.8, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["identificar riesgos", "identify risks", "que riesgos"]):
            return {"intent": "identify_risks", "confidence": 0.8, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["analizar riesgo", "evaluate risk", "assess"]):
            return {"intent": "analyze_specific_risk", "confidence": 0.7, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["mitigación", "mitigation", "plan de mitigación"]):
            return {"intent": "mitigation_planning", "confidence": 0.8, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["monte carlo", "simulación", "análisis predictivo"]):
            return {"intent": "monte_carlo_analysis", "confidence": 0.9, "parameters": {}}
        else:
            return {"intent": "general_risk", "confidence": 0.5, "parameters": {}}

    async def _handle_risk_register_creation(self, intent_analysis: Dict[str, Any], project_id: Optional[int]) -> Dict[str, Any]:
        """Handle complete risk register creation"""
        try:
            if not project_id:
                return {
                    "success": True,
                    "response": """⚠️ **Crear Risk Register Completo**

Para generar un Risk Register necesito:
- 🆔 **ID del proyecto** (requerido)

💡 **Ejemplo**: "Crear risk register para proyecto 5"

¿Para qué proyecto quieres crear el risk register?""",
                    "requires_follow_up": True
                }

            project = self.db_manager.get_project(project_id)
            if not project:
                return {
                    "success": False,
                    "response": f"🚫 Proyecto {project_id} no encontrado."
                }

            # Generate comprehensive risk register
            risk_register = self._generate_comprehensive_risk_register(project)

            # Save as document
            from storage.file_manager import FileManager
            file_manager = FileManager()

            file_path = file_manager.save_project_document(
                project_id=project.id,
                document_type="risk_register",
                content=risk_register,
                filename=f"risk_register_{project.name.replace(' ', '_').lower()}.md"
            )

            # Save to database
            self.db_manager.create_project_document(
                project_id=project.id,
                document_type="risk_register",
                file_path=file_path,
                content=risk_register
            )

            return {
                "success": True,
                "response": f"""✅ **Risk Register Creado Exitosamente**

📋 **Proyecto**: {project.name}
⚠️ **Archivo**: `{file_path}`
📅 **Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 **El Risk Register incluye**:
- ✅ Identificación de riesgos por categoría
- ✅ Análisis de probabilidad e impacto
- ✅ Scoring y priorización automática
- ✅ Estrategias de mitigación específicas
- ✅ Asignación de responsabilidades
- ✅ Timeline de seguimiento

📊 **Próximos pasos sugeridos**:
1. 📈 Análisis Monte Carlo: `"Hacer análisis Monte Carlo"`
2. 🔄 Seguimiento semanal: `"Monitorear riesgos"`
3. 📋 Actualización: `"Actualizar risk register"`

💡 **¿Quieres analizar algún riesgo específico en detalle?**""",
                "document_path": file_path,
                "document_type": "risk_register"
            }

        except Exception as e:
            logger.error(f"Error creating risk register: {str(e)}")
            return {
                "success": False,
                "response": f"🚫 Error creando el Risk Register: {str(e)}"
            }

    def _generate_comprehensive_risk_register(self, project: Project) -> str:
        """Generate comprehensive risk register using LLM"""
        risk_generation_prompt = f"""Genera un Risk Register completo y profesional para este proyecto:

**Proyecto**: {project.name}
**Descripción**: {project.description}
**Metodología**: {project.methodology}

Instrucciones:
1. Identifica riesgos específicos y realistas para este tipo de proyecto
2. Incluye riesgos de todas las categorías: técnicos, de negocio, externos, recursos
3. Asigna probabilidad (High/Medium/Low) e impacto (High/Medium/Low) justificados
4. Calcula risk score (Probabilidad × Impacto, donde High=3, Medium=2, Low=1)
5. Desarrolla estrategias de mitigación específicas y accionables
6. Asigna responsables realistas por rol
7. Incluye timeline de seguimiento

Categorías de riesgo a cubrir:
- **Técnico**: Tecnología, arquitectura, integración
- **Negocio**: Cambios de requisitos, aprobaciones, presupuesto
- **Externo**: Proveedores, regulación, mercado
- **Recursos**: Disponibilidad, competencias, rotación

Formato: Tabla en Markdown con todas las columnas del risk register.

Genera mínimo 8-10 riesgos diversos y específicos."""

        try:
            return self.llm.invoke(risk_generation_prompt).content
        except Exception as e:
            logger.error(f"Error generating risk register with LLM: {str(e)}")
            return self._get_fallback_risk_register(project)

    def _get_fallback_risk_register(self, project: Project) -> str:
        """Fallback risk register template"""
        return f"""# Risk Register: {project.name}

## Risk Assessment Matrix

| Risk ID | Risk Description | Category | Probability | Impact | Risk Score | Mitigation Strategy | Owner | Status | Target Date |
|---------|------------------|----------|-------------|---------|------------|-------------------|--------|--------|-------------|
| R001 | Cambios frecuentes en requisitos | Negocio | High | High | 9 | Implementar change control board, freeze de alcance en hitos | Product Owner | Open | {(datetime.now() + timedelta(weeks=2)).strftime('%Y-%m-%d')} |
| R002 | Disponibilidad limitada de recursos clave | Recursos | Medium | High | 6 | Cross-training, identificar recursos backup | Project Manager | Open | {(datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d')} |
| R003 | Integración compleja con sistemas legacy | Técnico | High | Medium | 6 | PoC temprano, arquitectura de integración detallada | Tech Lead | Open | {(datetime.now() + timedelta(weeks=3)).strftime('%Y-%m-%d')} |
| R004 | Retrasos en aprobaciones regulatorias | Externo | Medium | High | 6 | Inicio temprano del proceso, asesoría legal | Compliance | Open | {(datetime.now() + timedelta(weeks=4)).strftime('%Y-%m-%d')} |
| R005 | Rotación de personal del equipo | Recursos | Medium | Medium | 4 | Documentación completa, knowledge sharing sessions | HR / PM | Open | {(datetime.now() + timedelta(weeks=2)).strftime('%Y-%m-%d')} |
| R006 | Problemas de performance en producción | Técnico | Medium | High | 6 | Testing de carga, monitoreo proactivo | DevOps | Open | {(datetime.now() + timedelta(weeks=6)).strftime('%Y-%m-%d')} |
| R007 | Presupuesto insuficiente para alcance | Negocio | Low | High | 3 | Estimaciones detalladas, contingency fund | Sponsor | Open | {(datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d')} |
| R008 | Dependencias externas críticas | Externo | High | Medium | 6 | SLAs claros, proveedores alternativos | Procurement | Open | {(datetime.now() + timedelta(weeks=2)).strftime('%Y-%m-%d')} |

## Risk Categories Definition

### Technical Risks
- Technology-related challenges
- Integration complexities
- Performance issues
- Security vulnerabilities

### Business Risks
- Requirement changes
- Stakeholder alignment
- Budget constraints
- Timeline pressures

### External Risks
- Vendor dependencies
- Regulatory changes
- Market conditions
- Third-party integrations

### Resource Risks
- Team availability
- Skill gaps
- Knowledge transfer
- Staff turnover

## Probability Scale
- **High (3)**: >70% chance of occurrence
- **Medium (2)**: 30-70% chance of occurrence
- **Low (1)**: <30% chance of occurrence

## Impact Scale
- **High (3)**: Major impact on cost, schedule, or quality
- **Medium (2)**: Moderate impact, manageable
- **Low (1)**: Minor impact, easily recoverable

## Risk Response Strategies
- **Avoid**: Eliminate the risk by changing project plan
- **Mitigate**: Reduce probability or impact
- **Transfer**: Shift risk to third party (insurance, contracts)
- **Accept**: Acknowledge and monitor, create contingency

## Monitoring Schedule
- **Daily**: High-score risks (8-9)
- **Weekly**: Medium-score risks (4-6)
- **Monthly**: Low-score risks (1-3)
- **Quarterly**: Full register review and update

## Escalation Thresholds
- **Risk Score 8-9**: Immediate escalation to sponsor
- **Risk Score 6-7**: Weekly status in steering committee
- **Risk Score 4-5**: Monthly review in team meetings
- **New High Risk**: 48-hour notification to stakeholders

---
**Document Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Next Review Date**: {(datetime.now() + timedelta(weeks=2)).strftime('%Y-%m-%d')}
**Risk Manager**: Project Manager
"""

    async def _handle_risk_identification(self, intent_analysis: Dict[str, Any], project_id: Optional[int]) -> Dict[str, Any]:
        """Handle specific risk identification requests"""
        try:
            if not project_id:
                return {
                    "success": True,
                    "response": """🔍 **Identificación de Riesgos**

Para identificar riesgos específicos necesito:
- 🆔 **ID del proyecto** (requerido)
- 📋 **Área específica** (opcional): técnica, negocio, externa, recursos

💡 **Ejemplos**:
- "Identificar riesgos técnicos del proyecto 5"
- "Qué riesgos de negocio tiene el proyecto?"

¿Para qué proyecto y área quieres identificar riesgos?""",
                    "requires_follow_up": True
                }

            project = self.db_manager.get_project(project_id)
            if not project:
                return {
                    "success": False,
                    "response": f"🚫 Proyecto {project_id} no encontrado."
                }

            risk_type = intent_analysis.get("parameters", {}).get("risk_type", "all")
            risks = self._identify_project_risks(project, risk_type)

            response = f"""🔍 **Riesgos Identificados: {project.name}**

{risks}

💡 **Próximos pasos**:
- 📊 Evaluar probabilidad e impacto: `"Evaluar estos riesgos"`
- ⚠️ Crear risk register completo: `"Crear risk register"`
- 🛡️ Desarrollar mitigación: `"Crear plan de mitigación"`

¿Qué riesgo te preocupa más?"""

            return {
                "success": True,
                "response": response,
                "risks_identified": True
            }

        except Exception as e:
            logger.error(f"Error in risk identification: {str(e)}")
            return {
                "success": False,
                "response": f"🚫 Error identificando riesgos: {str(e)}"
            }

    def _identify_project_risks(self, project: Project, risk_type: str = "all") -> str:
        """Identify specific risks for a project"""
        identification_prompt = f"""Como experto en gestión de riesgos, identifica riesgos específicos para este proyecto:

**Proyecto**: {project.name}
**Descripción**: {project.description}
**Metodología**: {project.methodology}
**Tipo de riesgo solicitado**: {risk_type}

Identifica 5-7 riesgos específicos y realistas, incluyendo:
1. Descripción clara del riesgo
2. Por qué es relevante para este proyecto
3. Categoría (técnico/negocio/externo/recursos)
4. Impacto potencial específico

Formato: Lista con bullets, explicando cada riesgo en 1-2 líneas."""

        try:
            return self.llm.invoke(identification_prompt).content
        except Exception as e:
            return """**Riesgos Identificados** (análisis genérico):

🔧 **Técnicos**:
- Complejidad de integración con sistemas existentes
- Problemas de rendimiento bajo carga

💼 **Negocio**:
- Cambios en requisitos durante desarrollo
- Aprobaciones tardías de stakeholders clave

🌐 **Externos**:
- Dependencias de proveedores externos
- Cambios regulatorios durante proyecto

👥 **Recursos**:
- Disponibilidad limitada de especialistas
- Rotación de personal clave del equipo"""

    async def _handle_monte_carlo_analysis(self, intent_analysis: Dict[str, Any], project_id: Optional[int]) -> Dict[str, Any]:
        """Handle Monte Carlo analysis requests"""
        try:
            if not project_id:
                return {
                    "success": True,
                    "response": """📈 **Análisis Monte Carlo**

Para realizar un análisis Monte Carlo necesito:
- 🆔 **ID del proyecto** (requerido)
- 📊 **Tipo de análisis** (opcional): cronograma, presupuesto, o ambos

💡 **El análisis Monte Carlo te ayudará a**:
- Estimar probabilidades de finalización en fechas
- Calcular rangos de presupuesto con confianza estadística
- Identificar riesgos críticos para el cronograma

¿Para qué proyecto quieres el análisis?""",
                    "requires_follow_up": True
                }

            project = self.db_manager.get_project(project_id)
            if not project:
                return {
                    "success": False,
                    "response": f"🚫 Proyecto {project_id} no encontrado."
                }

            # Perform Monte Carlo analysis
            analysis_result = await self._perform_monte_carlo_analysis(project)

            return {
                "success": True,
                "response": analysis_result,
                "analysis_type": "monte_carlo",
                "project_id": project_id
            }

        except Exception as e:
            logger.error(f"Error in Monte Carlo analysis: {str(e)}")
            return {
                "success": False,
                "response": f"🚫 Error en análisis Monte Carlo: {str(e)}"
            }

    async def _perform_monte_carlo_analysis(self, project: Project) -> str:
        """Perform Monte Carlo simulation analysis"""
        # Simplified Monte Carlo simulation
        import random
        import numpy as np

        # Simulate 1000 iterations
        iterations = 1000

        # Base estimates (example values)
        base_duration_weeks = 12
        base_budget_usd = 100000

        # Risk factors (triangular distribution parameters)
        duration_optimistic = base_duration_weeks * 0.8
        duration_pessimistic = base_duration_weeks * 1.5
        duration_most_likely = base_duration_weeks

        budget_optimistic = base_budget_usd * 0.9
        budget_pessimistic = base_budget_usd * 1.4
        budget_most_likely = base_budget_usd

        duration_results = []
        budget_results = []

        # Monte Carlo simulation
        for _ in range(iterations):
            # Triangular distribution simulation
            duration = np.random.triangular(duration_optimistic, duration_most_likely, duration_pessimistic)
            budget = np.random.triangular(budget_optimistic, budget_most_likely, budget_pessimistic)

            duration_results.append(duration)
            budget_results.append(budget)

        # Calculate statistics
        duration_p10 = np.percentile(duration_results, 10)
        duration_p50 = np.percentile(duration_results, 50)
        duration_p90 = np.percentile(duration_results, 90)

        budget_p10 = np.percentile(budget_results, 10)
        budget_p50 = np.percentile(budget_results, 50)
        budget_p90 = np.percentile(budget_results, 90)

        return f"""📈 **Análisis Monte Carlo: {project.name}**

🕒 **Cronograma** (1,000 simulaciones):
- 📊 **P10** (optimista): {duration_p10:.1f} semanas
- 📊 **P50** (más probable): {duration_p50:.1f} semanas
- 📊 **P90** (pesimista): {duration_p90:.1f} semanas

💰 **Presupuesto** (USD):
- 💵 **P10** (optimista): ${budget_p10:,.0f}
- 💵 **P50** (más probable): ${budget_p50:,.0f}
- 💵 **P90** (pesimista): ${budget_p90:,.0f}

📊 **Interpretación**:
- ✅ **80% confianza**: El proyecto terminará entre {duration_p10:.1f} y {duration_p90:.1f} semanas
- 💰 **80% confianza**: El presupuesto estará entre ${budget_p10:,.0f} y ${budget_p90:,.0f}
- 🎯 **Recomendación**: Planificar para P70-P80 ({(duration_p50 * 1.2):.1f} semanas, ${(budget_p50 * 1.15):,.0f})

⚠️ **Riesgos Críticos Identificados**:
- 🔄 Variabilidad alta en duración ({(duration_p90/duration_p10 - 1)*100:.0f}% rango)
- 💸 Riesgo presupuestario significativo ({(budget_p90/budget_p10 - 1)*100:.0f}% rango)

🎯 **Acciones Recomendadas**:
1. 📋 Refinar estimaciones de tareas críticas
2. 🛡️ Crear contingency plan para escenarios P80-P90
3. 🔄 Revisar análisis mensualmente con datos reales

*Basado en distribución triangular y {iterations:,} simulaciones Monte Carlo*"""

    def _handle_general_risk_query(self, user_input: str, project_id: Optional[int]) -> Dict[str, Any]:
        """Handle general risk management queries"""
        query_prompt = f"""Como Risk Management Agent experto, responde a esta consulta sobre gestión de riesgos:

Consulta: "{user_input}"
Proyecto ID: {project_id if project_id else "No especificado"}

Proporciona una respuesta útil sobre:
- Metodologías de gestión de riesgos
- Técnicas de identificación y análisis
- Estrategias de mitigación
- Mejores prácticas PMP/PMI
- Herramientas de análisis cuantitativo

Respuesta profesional pero accesible, con ejemplos específicos cuando sea útil."""

        try:
            response = self.llm.invoke(query_prompt).content
            return {
                "success": True,
                "response": response,
                "query_type": "risk_general"
            }
        except Exception as e:
            return {
                "success": True,
                "response": """⚠️ **Risk Management Agent - Ayuda General**

Puedo ayudarte con:

🔍 **Identificación de Riesgos**:
- Riesgos técnicos, de negocio, externos, y de recursos
- Técnicas: brainstorming, checklists, análisis FODA

📊 **Análisis de Riesgos**:
- Matriz probabilidad/impacto
- Scoring y priorización
- Análisis cuantitativo (Monte Carlo)

🛡️ **Gestión de Riesgos**:
- Estrategias: Evitar, Mitigar, Transferir, Aceptar
- Planes de contingencia
- Monitoreo y seguimiento

🔧 **Comandos útiles**:
- `"Crear risk register para proyecto [ID]"`
- `"Identificar riesgos del proyecto"`
- `"Hacer análisis Monte Carlo"`
- `"Evaluar riesgo específico"`

💡 **¿En qué aspecto de gestión de riesgos necesitas ayuda?**"""
            }

    def calculate_risk_score(self, probability: RiskProbability, impact: RiskImpact) -> int:
        """Calculate risk score based on probability and impact"""
        prob_score = self.risk_matrix[probability]
        impact_score = self.impact_matrix[impact]
        return prob_score * impact_score

    def get_risk_priority(self, risk_score: int) -> str:
        """Get risk priority based on score"""
        if risk_score >= 8:
            return "Critical"
        elif risk_score >= 6:
            return "High"
        elif risk_score >= 4:
            return "Medium"
        else:
            return "Low"

    def get_agent_capabilities(self) -> List[str]:
        """Get list of this agent's capabilities"""
        return [
            "risk_identification",
            "risk_assessment",
            "risk_scoring",
            "mitigation_planning",
            "monte_carlo_analysis",
            "risk_monitoring",
            "quantitative_analysis",
            "risk_register_creation",
            "pmp_risk_standards"
        ]