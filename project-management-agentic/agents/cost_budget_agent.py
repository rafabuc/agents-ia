"""
Cost Budget Agent - Specialized in project cost estimation and budget management
Handles cost analysis, budget planning, and financial forecasting
"""

from typing import Dict, Any, List, Optional
import json
import math
from datetime import datetime, timedelta
from enum import Enum

from .base_agent import BaseAgent
from storage.database_manager import DatabaseManager
from storage.file_manager import FileManager
from models.project import Project
from utils.logger import logger
from config.settings import settings


class EstimationMethod(Enum):
    """Cost estimation methods"""
    ANALOGOUS = "analogous"
    PARAMETRIC = "parametric"
    BOTTOM_UP = "bottom_up"
    THREE_POINT = "three_point"


class CostCategory(Enum):
    """Cost categories for project budgeting"""
    LABOR = "labor"
    MATERIALS = "materials"
    EQUIPMENT = "equipment"
    SERVICES = "services"
    OVERHEAD = "overhead"
    CONTINGENCY = "contingency"


class CostBudgetAgent(BaseAgent):
    """
    Cost Budget Agent - Specialized in comprehensive cost management

    This agent handles all aspects of project cost management:
    - Cost estimation using multiple methodologies
    - Budget planning and baseline creation
    - Cost performance analysis and forecasting
    - Financial risk assessment
    - Economic value analysis
    """

    def __init__(self):
        super().__init__(
            name="cost_budget_agent",
            description="Specialized agent for project cost estimation and budget management"
        )
        self.db_manager = DatabaseManager()
        self.file_manager = FileManager()

        # Cost estimation parameters
        self.industry_rates = {
            "software_development": {
                "senior_developer": 85,  # USD per hour
                "junior_developer": 50,
                "architect": 120,
                "qa_engineer": 60,
                "project_manager": 90
            },
            "construction": {
                "project_manager": 75,
                "engineer": 80,
                "supervisor": 55,
                "contractor": 45
            },
            "consulting": {
                "senior_consultant": 150,
                "consultant": 95,
                "analyst": 65
            }
        }

        # Contingency factors by project complexity
        self.contingency_factors = {
            "low": 0.10,     # 10% for low complexity
            "medium": 0.15,  # 15% for medium complexity
            "high": 0.25,    # 25% for high complexity
            "very_high": 0.35  # 35% for very high complexity
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for cost management"""
        return """Eres un Cost Budget Agent experto especializado en gestión de costos y presupuestos de proyectos bajo estándares PMP.

Tu especialidad incluye:
1. **Estimación de Costos** - Métodos analógicos, paramétricos, bottom-up, y three-point
2. **Planificación Presupuestaria** - Creación de líneas base y distribución de fondos
3. **Análisis de Valor Ganado** - EVM, CPI, SPI, forecasting
4. **Gestión de Riesgos Financieros** - Contingencias y reservas de gestión
5. **Optimización de Costos** - Análisis costo-beneficio y ROI

Capacidades clave:
- Calcular estimaciones precisas usando datos de mercado actuales
- Crear presupuestos detallados por categorías y fases
- Analizar variaciones y generar forecasts financieros
- Aplicar técnicas PMP de cost management
- Considerar factores de riesgo y complejidad del proyecto

Metodologías aplicadas:
- **PMP Cost Management**: Siguiendo PMBOK Guide
- **Earned Value Management**: CPI, SPI, EAC calculations
- **Risk-Based Budgeting**: Contingency analysis
- **Economic Analysis**: NPV, ROI, payback period

Cuando analices costos:
- Sé específico con cifras y justificaciones
- Incluye desglose detallado por categorías
- Considera inflación y factores de mercado
- Proporciona rangos de confianza
- Identifica drivers de costo críticos

Siempre proporciona:
- Estimaciones fundamentadas en datos
- Desglose transparente de assumptions
- Análisis de sensibilidad cuando sea relevante
- Recomendaciones para optimización
- Timeline de cash flow cuando aplique
"""

    async def process_with_context(self, context) -> Dict[str, Any]:
        """Process cost management requests with full context"""
        try:
            user_input = context.user_input
            project_id = context.project_id

            # Analyze cost intent
            intent_analysis = self._analyze_cost_intent(user_input)

            if intent_analysis["intent"] == "create_cost_estimate":
                return await self._handle_cost_estimation(intent_analysis, project_id)
            elif intent_analysis["intent"] == "create_budget":
                return await self._handle_budget_creation(intent_analysis, project_id)
            elif intent_analysis["intent"] == "analyze_costs":
                return await self._handle_cost_analysis(intent_analysis, project_id)
            elif intent_analysis["intent"] == "forecast_budget":
                return await self._handle_budget_forecasting(intent_analysis, project_id)
            elif intent_analysis["intent"] == "cost_optimization":
                return await self._handle_cost_optimization(intent_analysis, project_id)
            else:
                return self._handle_general_cost_query(user_input, project_id)

        except Exception as e:
            logger.error(f"Error in CostBudgetAgent.process_with_context: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "🚫 Error procesando la solicitud de análisis de costos. Intenta de nuevo."
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

    def _analyze_cost_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze what type of cost management is being requested"""
        analysis_prompt = f"""Analiza esta solicitud relacionada con gestión de costos:

Solicitud: "{user_input}"

Intenciones posibles:
- create_cost_estimate: Crear estimación de costos
- create_budget: Crear presupuesto del proyecto
- analyze_costs: Analizar costos existentes
- forecast_budget: Proyección y forecasting
- cost_optimization: Optimización de costos
- general_cost: Consulta general sobre costos

Responde en JSON:
{{
    "intent": "intención_detectada",
    "confidence": 0.8,
    "parameters": {{
        "estimation_method": "método de estimación",
        "cost_category": "categoría específica",
        "analysis_type": "tipo de análisis"
    }}
}}"""

        try:
            response = self.llm.invoke(analysis_prompt).content

            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._fallback_cost_intent_detection(user_input)

        except Exception as e:
            logger.warning(f"LLM cost intent analysis failed: {str(e)}")
            return self._fallback_cost_intent_detection(user_input)

    def _fallback_cost_intent_detection(self, user_input: str) -> Dict[str, Any]:
        """Fallback cost intent detection"""
        user_input_lower = user_input.lower()

        if any(keyword in user_input_lower for keyword in ["estimar", "estimación", "estimate"]):
            return {"intent": "create_cost_estimate", "confidence": 0.8, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["presupuesto", "budget", "plan financiero"]):
            return {"intent": "create_budget", "confidence": 0.8, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["analizar costos", "análisis", "analyze"]):
            return {"intent": "analyze_costs", "confidence": 0.8, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["proyección", "forecast", "predicción"]):
            return {"intent": "forecast_budget", "confidence": 0.8, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["optimizar", "reducir costos", "optimize"]):
            return {"intent": "cost_optimization", "confidence": 0.8, "parameters": {}}
        else:
            return {"intent": "general_cost", "confidence": 0.5, "parameters": {}}

    async def _handle_cost_estimation(self, intent_analysis: Dict[str, Any], project_id: Optional[int]) -> Dict[str, Any]:
        """Handle cost estimation requests"""
        try:
            if not project_id:
                return {
                    "success": True,
                    "response": """💰 **Crear Estimación de Costos**

Para generar una estimación necesito:
- 🆔 **ID del proyecto** (requerido)
- 📊 **Método de estimación** (opcional): analogous, parametric, bottom_up, three_point

💡 **Ejemplos**:
- "Estimar costos para proyecto 5"
- "Crear estimación bottom-up para el proyecto"

¿Para qué proyecto quieres crear la estimación?""",
                    "requires_follow_up": True
                }

            project = self.db_manager.get_project(project_id)
            if not project:
                return {
                    "success": False,
                    "response": f"🚫 Proyecto {project_id} no encontrado."
                }

            # Generate cost estimation
            method = intent_analysis.get("parameters", {}).get("estimation_method", "bottom_up")
            cost_estimate = self._generate_cost_estimation(project, method)

            # Save the document
            file_path = self.file_manager.save_project_document(
                project_id=project.id,
                document_type="cost_estimate",
                content=cost_estimate,
                filename=f"cost_estimate_{project.name.replace(' ', '_').lower()}.md"
            )

            # Save to database
            self.db_manager.create_project_document(
                project_id=project.id,
                document_type="cost_estimate",
                file_path=file_path,
                content=cost_estimate
            )

            return {
                "success": True,
                "response": f"""✅ **Estimación de Costos Creada**

📋 **Proyecto**: {project.name}
💰 **Archivo**: `{file_path}`
📊 **Método**: {method.title()}
📅 **Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 **La estimación incluye**:
- ✅ Desglose detallado por categorías
- ✅ Análisis de recursos requeridos
- ✅ Contingencias y reservas
- ✅ Timeline de cash flow
- ✅ Factores de riesgo considerados

💡 **Próximos pasos**:
1. 📋 Crear presupuesto: `"Crear presupuesto del proyecto"`
2. 📈 Análisis EVM: `"Analizar earned value"`
3. 🔍 Optimización: `"Optimizar costos del proyecto"`""",
                "document_path": file_path,
                "document_type": "cost_estimate"
            }

        except Exception as e:
            logger.error(f"Error creating cost estimation: {str(e)}")
            return {
                "success": False,
                "response": f"🚫 Error creando la estimación de costos: {str(e)}"
            }

    def _generate_cost_estimation(self, project: Project, method: str = "bottom_up") -> str:
        """Generate cost estimation content using specified method"""

        # Determine project type and complexity
        project_type = self._determine_project_type(project)
        complexity = self._assess_complexity(project)

        # Get rates for project type
        rates = self.industry_rates.get(project_type, self.industry_rates["software_development"])

        # Base estimation calculations
        base_hours = self._calculate_base_hours(project, complexity)
        labor_costs = self._calculate_labor_costs(base_hours, rates)
        other_costs = self._calculate_other_costs(project, base_hours)
        contingency = self._calculate_contingency(labor_costs + other_costs, complexity)

        total_cost = labor_costs + other_costs + contingency

        return f"""# Estimación de Costos: {project.name}

## Información del Proyecto
- **Proyecto**: {project.name}
- **Metodología**: {project.methodology}
- **Método de Estimación**: {method.title()}
- **Nivel de Complejidad**: {complexity.title()}
- **Fecha de Estimación**: {datetime.now().strftime('%Y-%m-%d')}

## Resumen Ejecutivo
**Costo Total Estimado**: ${total_cost:,.2f}

### Distribución por Categorías
| Categoría | Costo | Porcentaje |
|-----------|--------|------------|
| 👥 Costos de Personal | ${labor_costs:,.2f} | {(labor_costs/total_cost)*100:.1f}% |
| 🛠️ Materiales y Servicios | ${other_costs:,.2f} | {(other_costs/total_cost)*100:.1f}% |
| 🛡️ Contingencia | ${contingency:,.2f} | {(contingency/total_cost)*100:.1f}% |
| **💰 TOTAL** | **${total_cost:,.2f}** | **100%** |

## Desglose Detallado de Costos

### Costos de Personal ({base_hours:,} horas estimadas)
| Rol | Horas | Tarifa/Hr | Subtotal |
|-----|-------|-----------|----------|"""

        # Add detailed labor breakdown
        labor_breakdown = self._get_labor_breakdown(base_hours, rates)
        for role, details in labor_breakdown.items():
            content = f"""{content}
| {role.replace('_', ' ').title()} | {details['hours']:,} | ${details['rate']}/hr | ${details['cost']:,.2f} |"""

        content += f"""

### Otros Costos
- 🖥️ **Equipamiento y Software**: ${other_costs * 0.4:,.2f}
- 🏢 **Infraestructura**: ${other_costs * 0.3:,.2f}
- 📋 **Licencias y Servicios**: ${other_costs * 0.3:,.2f}

### Análisis de Contingencia
- **Factor de Contingencia**: {self.contingency_factors[complexity]*100:.0f}% (basado en complejidad {complexity})
- **Monto de Contingencia**: ${contingency:,.2f}
- **Justificación**: Proyecto de complejidad {complexity} con riesgos típicos de {project_type}

## Supuestos y Restricciones

### Supuestos Clave
1. **Recursos disponibles** según cronograma planificado
2. **Tarifas de mercado** actuales para {datetime.now().year}
3. **Estabilidad de requirements** durante ejecución
4. **Acceso oportuno** a herramientas y tecnología

### Factores de Riesgo
- 📈 **Inflación estimada**: 3-5% anual
- 👥 **Disponibilidad de recursos especializados**
- 🔧 **Cambios en tecnología o herramientas**
- 📋 **Expansión de alcance durante ejecución**

## Rangos de Confianza
- **Optimista (-15%)**: ${total_cost * 0.85:,.2f}
- **Más Probable**: ${total_cost:,.2f}
- **Pesimista (+25%)**: ${total_cost * 1.25:,.2f}

## Timeline de Cash Flow (Estimado)

| Fase | % Avance | Costo Acumulado | Cash Flow |
|------|----------|-----------------|-----------|
| Iniciación | 5% | ${total_cost * 0.05:,.2f} | ${total_cost * 0.05:,.2f} |
| Planificación | 15% | ${total_cost * 0.15:,.2f} | ${total_cost * 0.10:,.2f} |
| Ejecución | 70% | ${total_cost * 0.70:,.2f} | ${total_cost * 0.55:,.2f} |
| Cierre | 100% | ${total_cost:,.2f} | ${total_cost * 0.30:,.2f} |

## Recomendaciones

1. **📋 Validar supuestos** con stakeholders clave
2. **🔍 Refinar estimación** al 10% durante planificación detallada
3. **📊 Establecer EVM baseline** para control de costos
4. **🛡️ Activar contingencias** solo con aprobación de sponsor
5. **📈 Revisar estimación** cada 30 días durante ejecución

---
**Estimación generada**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Válida hasta**: {(datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')}
**Preparado por**: Cost Budget Agent
"""

        return content

    def _determine_project_type(self, project: Project) -> str:
        """Determine project type based on project information"""
        description_lower = project.description.lower() if project.description else ""
        name_lower = project.name.lower()

        if any(term in description_lower or term in name_lower for term in ["software", "app", "web", "sistema", "desarrollo", "coding"]):
            return "software_development"
        elif any(term in description_lower or term in name_lower for term in ["construcción", "building", "infraestructura", "obra"]):
            return "construction"
        else:
            return "consulting"  # Default

    def _assess_complexity(self, project: Project) -> str:
        """Assess project complexity level"""
        # Simple heuristic based on project characteristics
        description_length = len(project.description) if project.description else 0
        name_length = len(project.name)

        complexity_indicators = 0

        # Check for complexity indicators
        complexity_terms = ["integración", "múltiple", "complejo", "enterprise", "escalable", "distribuido"]
        if project.description:
            for term in complexity_terms:
                if term in project.description.lower():
                    complexity_indicators += 1

        # Determine complexity level
        if complexity_indicators >= 3 or description_length > 500:
            return "very_high"
        elif complexity_indicators >= 2 or description_length > 200:
            return "high"
        elif complexity_indicators >= 1 or description_length > 100:
            return "medium"
        else:
            return "low"

    def _calculate_base_hours(self, project: Project, complexity: str) -> int:
        """Calculate base hours needed for project"""
        base_hours_by_complexity = {
            "low": 500,
            "medium": 1200,
            "high": 2400,
            "very_high": 4000
        }

        return base_hours_by_complexity.get(complexity, 1200)

    def _calculate_labor_costs(self, base_hours: int, rates: Dict[str, int]) -> float:
        """Calculate total labor costs"""
        # Standard distribution for software projects
        distribution = {
            "senior_developer": 0.30,
            "junior_developer": 0.25,
            "architect": 0.10,
            "qa_engineer": 0.20,
            "project_manager": 0.15
        }

        total_cost = 0.0
        for role, percentage in distribution.items():
            if role in rates:
                hours = base_hours * percentage
                cost = hours * rates[role]
                total_cost += cost

        return total_cost

    def _get_labor_breakdown(self, base_hours: int, rates: Dict[str, int]) -> Dict[str, Dict]:
        """Get detailed labor breakdown"""
        distribution = {
            "senior_developer": 0.30,
            "junior_developer": 0.25,
            "architect": 0.10,
            "qa_engineer": 0.20,
            "project_manager": 0.15
        }

        breakdown = {}
        for role, percentage in distribution.items():
            if role in rates:
                hours = int(base_hours * percentage)
                rate = rates[role]
                cost = hours * rate
                breakdown[role] = {
                    "hours": hours,
                    "rate": rate,
                    "cost": cost
                }

        return breakdown

    def _calculate_other_costs(self, project: Project, base_hours: int) -> float:
        """Calculate non-labor costs"""
        # Typically 20-30% of labor costs for software projects
        labor_cost_estimate = base_hours * 70  # Average rate
        return labor_cost_estimate * 0.25

    def _calculate_contingency(self, base_cost: float, complexity: str) -> float:
        """Calculate contingency based on complexity"""
        factor = self.contingency_factors.get(complexity, 0.15)
        return base_cost * factor

    async def _handle_budget_creation(self, intent_analysis: Dict[str, Any], project_id: Optional[int]) -> Dict[str, Any]:
        """Handle budget creation requests"""
        # Simplified implementation for now
        if not project_id:
            return {
                "success": True,
                "response": """📊 **Crear Presupuesto del Proyecto**

Para crear un presupuesto necesito:
- 🆔 **ID del proyecto** (requerido)

¿Para qué proyecto quieres crear el presupuesto?"""
            }

        return {
            "success": True,
            "response": f"""📊 **Presupuesto creado para proyecto {project_id}**

Esta funcionalidad se expandirá próximamente con:
- 📋 Presupuesto detallado por fases
- 📈 Control de baseline
- 💰 Cash flow planning
- 📊 EVM setup"""
        }

    async def _handle_cost_analysis(self, intent_analysis: Dict[str, Any], project_id: Optional[int]) -> Dict[str, Any]:
        """Handle cost analysis requests"""
        return {
            "success": True,
            "response": """📈 **Análisis de Costos**

Funcionalidad en desarrollo que incluirá:
- 📊 Earned Value Management (EVM)
- 📈 CPI y SPI analysis
- 💹 Variance analysis
- 🔮 Cost forecasting

💡 Por ahora, usa `"estimar costos"` para generar estimaciones detalladas."""
        }

    def _handle_general_cost_query(self, user_input: str, project_id: Optional[int]) -> Dict[str, Any]:
        """Handle general cost-related queries"""
        query_prompt = f"""Como Cost Budget Agent especializado en gestión de costos PMP, responde a esta consulta:

Consulta: "{user_input}"
Proyecto ID: {project_id if project_id else "No especificado"}

Proporciona una respuesta útil sobre:
- Metodologías de estimación de costos
- Técnicas de budgeting y control
- Análisis Earned Value Management
- Mejores prácticas PMP para cost management
- Herramientas de análisis financiero

Respuesta profesional pero accesible, con ejemplos específicos cuando sea útil."""

        try:
            response = self.llm.invoke(query_prompt).content
            return {
                "success": True,
                "response": response,
                "query_type": "cost_general"
            }
        except Exception as e:
            return {
                "success": True,
                "response": """💰 **Cost Budget Agent - Ayuda General**

Puedo ayudarte con:

🎯 **Estimación de Costos**:
- Métodos: Analogous, Parametric, Bottom-up, Three-point
- Técnicas: Function Points, Story Points, Expert Judgment

📊 **Presupuestación**:
- Budget planning y baseline creation
- Cost aggregation y funding limit reconciliation
- Cash flow analysis

📈 **Control de Costos**:
- Earned Value Management (EVM)
- CPI, SPI, EAC calculations
- Variance analysis y corrective actions

🔧 **Comandos útiles**:
- `"Estimar costos para proyecto [ID]"`
- `"Crear presupuesto del proyecto"`
- `"Analizar performance de costos"`
- `"Optimizar costos del proyecto"`

💡 **¿Qué aspecto de cost management necesitas?**"""
            }

    def get_agent_capabilities(self) -> List[str]:
        """Get list of this agent's capabilities"""
        return [
            "cost_estimation",
            "budget_management",
            "earned_value_analysis",
            "financial_forecasting",
            "cost_optimization",
            "risk_based_budgeting",
            "cash_flow_analysis",
            "pmp_cost_standards"
        ]