"""
Document Agent - Specialized in project documentation creation and management
Handles Project Charters, WBS, templates, and document generation
"""

from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

from .base_agent import BaseAgent
from storage.file_manager import FileManager
from storage.database_manager import DatabaseManager
from models.project import Project
from utils.logger import logger
from config.settings import settings


class DocumentAgent(BaseAgent):
    """
    Document Agent - Specialized in PMP/SAFe document creation and management

    This agent handles all document-related tasks including:
    - Project Charter creation
    - Work Breakdown Structure (WBS) generation
    - Risk Register templates
    - Stakeholder documentation
    - Template management and customization
    """

    def __init__(self):
        super().__init__(
            name="document_agent",
            description="Specialized agent for PMP/SAFe document creation and management"
        )
        self.file_manager = FileManager()
        self.db_manager = DatabaseManager()

        # LLM is already initialized in BaseAgent as self.llm

    def get_system_prompt(self) -> str:
        """Get the system prompt for document generation"""
        return """Eres un Document Agent experto especializado en la creación de documentación de proyectos bajo estándares PMP y SAFe.

Tu especialidad incluye:
1. **Project Charters** - Documentos de inicio de proyecto completos
2. **Work Breakdown Structure (WBS)** - Estructuras de desglose detalladas
3. **Risk Registers** - Registros de riesgos con análisis probabilístico
4. **Stakeholder Registers** - Mapeo y análisis de interesados
5. **Communication Plans** - Planes de comunicación estructurados
6. **Templates** - Plantillas personalizables por industria

Capacidades clave:
- Generar documentos profesionales siguiendo estándares PMI
- Personalizar contenido según el contexto del proyecto
- Crear documentos en formato Markdown profesional
- Integrar metodologías PMP y SAFe según corresponda
- Mantener consistencia entre documentos relacionados

Siempre genera documentos:
- Estructurados y profesionales
- Completos pero concisos
- Adaptados al contexto específico del proyecto
- Listos para uso empresarial
- Con formato Markdown claro y legible

Cuando generes un documento, incluye:
- Encabezados jerárquicos apropiados
- Secciones claramente definidas
- Contenido específico y útil (no solo placeholders)
- Fechas y metadatos relevantes
- Referencias a estándares cuando aplique
"""

    async def process_with_context(self, context) -> Dict[str, Any]:
        """Process document requests with full context"""
        try:
            user_input = context.user_input
            project_id = context.project_id

            # Analyze document intent
            intent_analysis = self._analyze_document_intent(user_input)

            if intent_analysis["intent"] == "create_charter":
                return await self._handle_charter_creation(intent_analysis, project_id)
            elif intent_analysis["intent"] == "create_wbs":
                return await self._handle_wbs_creation(intent_analysis, project_id)
            elif intent_analysis["intent"] == "create_risk_register":
                return await self._handle_risk_register_creation(intent_analysis, project_id)
            elif intent_analysis["intent"] == "get_template":
                return await self._handle_template_request(intent_analysis)
            elif intent_analysis["intent"] == "list_documents":
                return await self._handle_list_documents(project_id)
            else:
                return self._handle_general_document_query(user_input, project_id)

        except Exception as e:
            logger.error(f"Error in DocumentAgent.process_with_context: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "🚫 Error procesando la solicitud de documento. Intenta de nuevo."
            }

    def process(self, user_input: str, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Process request (legacy method for backward compatibility)"""
        # Create a simple context for backward compatibility
        class SimpleContext:
            def __init__(self, user_input, project_id):
                self.user_input = user_input
                self.project_id = project_id

        context = SimpleContext(user_input, project_id)

        # Use asyncio to run the async method
        import asyncio
        try:
            return asyncio.run(self.process_with_context(context))
        except RuntimeError:
            # If we're already in an async context, create a new loop
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, self.process_with_context(context))
                return future.result()

    def _analyze_document_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze what type of document is being requested"""
        analysis_prompt = f"""Analiza esta solicitud de documento y extrae la intención:

Solicitud: "{user_input}"

Intenciones posibles:
- create_charter: Crear project charter
- create_wbs: Crear Work Breakdown Structure
- create_risk_register: Crear risk register
- create_stakeholder_register: Crear stakeholder register
- get_template: Obtener plantilla
- list_documents: Listar documentos de proyecto
- general_document: Consulta general sobre documentos

Responde en JSON:
{{
    "intent": "intención_detectada",
    "confidence": 0.8,
    "parameters": {{
        "document_type": "tipo de documento",
        "project_name": "nombre si se menciona",
        "custom_requirements": "requisitos especiales"
    }}
}}"""

        try:
            response = self.llm.invoke(analysis_prompt).content

            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return self._fallback_document_intent_detection(user_input)

        except Exception as e:
            logger.warning(f"LLM document intent analysis failed: {str(e)}")
            return self._fallback_document_intent_detection(user_input)

    def _fallback_document_intent_detection(self, user_input: str) -> Dict[str, Any]:
        """Fallback document intent detection"""
        user_input_lower = user_input.lower()

        if any(keyword in user_input_lower for keyword in ["charter", "proyecto charter"]):
            return {"intent": "create_charter", "confidence": 0.8, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["wbs", "breakdown", "estructura"]):
            return {"intent": "create_wbs", "confidence": 0.8, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["riesgo", "risk", "riesgos"]):
            return {"intent": "create_risk_register", "confidence": 0.8, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["plantilla", "template"]):
            return {"intent": "get_template", "confidence": 0.8, "parameters": {}}
        elif any(keyword in user_input_lower for keyword in ["listar", "documentos", "ver documentos"]):
            return {"intent": "list_documents", "confidence": 0.8, "parameters": {}}
        else:
            return {"intent": "general_document", "confidence": 0.5, "parameters": {}}

    async def _handle_charter_creation(self, intent_analysis: Dict[str, Any], project_id: Optional[int]) -> Dict[str, Any]:
        """Handle project charter creation"""
        try:
            if not project_id:
                return {
                    "success": True,
                    "response": """📄 **Crear Project Charter**

Para generar un Project Charter necesito:
- 🆔 **ID del proyecto** (requerido)

💡 **Ejemplo**: "Crear charter para proyecto 5"

¿De qué proyecto quieres crear el charter?""",
                    "requires_follow_up": True
                }

            # Get project information
            project = self.db_manager.get_project(project_id)
            if not project:
                return {
                    "success": False,
                    "response": f"🚫 Proyecto {project_id} no encontrado."
                }

            # Generate project charter using LLM
            charter_content = self._generate_project_charter(project)

            # Save the document
            file_path = self.file_manager.save_project_document(
                project_id=project.id,
                document_type="project_charter",
                content=charter_content,
                filename=f"project_charter_{project.name.replace(' ', '_').lower()}.md"
            )

            # Save to database
            self.db_manager.create_project_document(
                project_id=project.id,
                document_type="project_charter",
                file_path=file_path,
                content=charter_content
            )

            response = f"""✅ **Project Charter Creado Exitosamente**

📋 **Proyecto**: {project.name}
📄 **Archivo**: `{file_path}`
📅 **Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 **El charter incluye**:
- ✅ Objetivos del proyecto
- ✅ Alcance y deliverables
- ✅ Stakeholders identificados
- ✅ Cronograma de alto nivel
- ✅ Presupuesto estimado
- ✅ Riesgos preliminares

💡 **Próximos pasos sugeridos**:
1. 📊 Crear WBS: `"Generar WBS para proyecto {project.id}"`
2. ⚠️ Análisis de riesgos: `"Crear risk register"`
3. 👥 Mapear stakeholders: `"Documentar stakeholders"`"""

            return {
                "success": True,
                "response": response,
                "document_path": file_path,
                "document_type": "project_charter"
            }

        except Exception as e:
            logger.error(f"Error creating project charter: {str(e)}")
            return {
                "success": False,
                "response": f"🚫 Error creando el Project Charter: {str(e)}"
            }

    def _generate_project_charter(self, project: Project) -> str:
        """Generate project charter content using LLM"""
        generation_prompt = f"""Genera un Project Charter completo y profesional para el siguiente proyecto:

**Información del Proyecto:**
- Nombre: {project.name}
- Descripción: {project.description}
- Metodología: {project.methodology}
- Estado: {project.status.value}

**Instrucciones:**
1. Crea un Project Charter siguiendo estándares PMI/PMP
2. Incluye TODAS las secciones estándar de un charter
3. Usa formato Markdown profesional
4. El contenido debe ser específico y útil (no genérico)
5. Incluye fechas, presupuestos estimados realistas
6. Agrega stakeholders típicos para este tipo de proyecto

**Secciones requeridas:**
1. Executive Summary
2. Objetivos del Proyecto
3. Alcance del Proyecto (In/Out of Scope)
4. Deliverables Principales
5. Stakeholders y Roles
6. Cronograma de Alto Nivel
7. Presupuesto Estimado
8. Riesgos de Alto Nivel
9. Criterios de Éxito
10. Aprobaciones

Genera el documento completo en formato Markdown."""

        try:
            return self.llm.invoke(generation_prompt).content
        except Exception as e:
            logger.error(f"Error generating charter with LLM: {str(e)}")
            return self._get_fallback_project_charter(project)

    def _get_fallback_project_charter(self, project: Project) -> str:
        """Fallback project charter template"""
        return f"""# Project Charter: {project.name}

## Executive Summary
El proyecto {project.name} tiene como objetivo {project.description or "cumplir con los objetivos definidos por el negocio"}.

## Información del Proyecto
- **Nombre del Proyecto**: {project.name}
- **Fecha de Inicio**: {datetime.now().strftime('%Y-%m-%d')}
- **Metodología**: {project.methodology}
- **Estado**: {project.status.value.title()}
- **Project Manager**: Por asignar

## Objetivos del Proyecto
1. Objetivo principal del proyecto
2. Objetivos secundarios
3. Beneficios esperados

## Alcance del Proyecto

### In Scope
- Entregables principales
- Funcionalidades incluidas
- Procesos cubiertos

### Out of Scope
- Elementos excluidos
- Funcionalidades no incluidas
- Restricciones definidas

## Stakeholders Principales
| Rol | Nombre | Responsabilidad |
|-----|--------|-----------------|
| Sponsor | Por definir | Patrocinio ejecutivo |
| Project Manager | Por asignar | Gestión del proyecto |
| Product Owner | Por definir | Definición de requisitos |

## Cronograma de Alto Nivel
- **Inicio**: {datetime.now().strftime('%Y-%m-%d')}
- **Planning**: 2-3 semanas
- **Ejecución**: 8-12 semanas
- **Cierre**: 1 semana

## Presupuesto Estimado
- Recursos humanos: Por estimar
- Infraestructura: Por estimar
- Otros costos: Por estimar

## Riesgos de Alto Nivel
1. Disponibilidad de recursos
2. Cambios en alcance
3. Dependencias externas

## Criterios de Éxito
- [ ] Entregables completados según especificaciones
- [ ] Proyecto dentro del presupuesto
- [ ] Cumplimiento de fechas clave

---
**Documento generado**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

    async def _handle_wbs_creation(self, intent_analysis: Dict[str, Any], project_id: Optional[int]) -> Dict[str, Any]:
        """Handle WBS creation"""
        try:
            if not project_id:
                return {
                    "success": True,
                    "response": """📊 **Crear Work Breakdown Structure (WBS)**

Para generar un WBS necesito:
- 🆔 **ID del proyecto** (requerido)

💡 **Ejemplo**: "Crear WBS para proyecto 5"

¿Para qué proyecto quieres crear el WBS?""",
                    "requires_follow_up": True
                }

            project = self.db_manager.get_project(project_id)
            if not project:
                return {
                    "success": False,
                    "response": f"🚫 Proyecto {project_id} no encontrado."
                }

            # Generate WBS content
            wbs_content = self._generate_wbs(project)

            # Save the document
            file_path = self.file_manager.save_project_document(
                project_id=project.id,
                document_type="wbs",
                content=wbs_content,
                filename=f"wbs_{project.name.replace(' ', '_').lower()}.md"
            )

            # Save to database
            self.db_manager.create_project_document(
                project_id=project.id,
                document_type="wbs",
                file_path=file_path,
                content=wbs_content
            )

            return {
                "success": True,
                "response": f"""✅ **Work Breakdown Structure Creado**

📋 **Proyecto**: {project.name}
📊 **Archivo**: `{file_path}`
📅 **Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

🎯 **El WBS incluye**:
- ✅ Estructura jerárquica de trabajo
- ✅ Paquetes de trabajo definidos
- ✅ Estimaciones de esfuerzo
- ✅ Dependencias identificadas

💡 **Siguiente paso**: Crear cronograma detallado basado en este WBS""",
                "document_path": file_path,
                "document_type": "wbs"
            }

        except Exception as e:
            logger.error(f"Error creating WBS: {str(e)}")
            return {
                "success": False,
                "response": f"🚫 Error creando el WBS: {str(e)}"
            }

    def _generate_wbs(self, project: Project) -> str:
        """Generate WBS content using LLM"""
        wbs_prompt = f"""Genera un Work Breakdown Structure (WBS) completo para:

**Proyecto**: {project.name}
**Descripción**: {project.description}
**Metodología**: {project.methodology}

Crea un WBS que incluya:
1. Estructura jerárquica (mínimo 3 niveles)
2. Paquetes de trabajo específicos
3. Estimaciones de esfuerzo realistas
4. Identificación de dependencias
5. Entregables por cada paquete

Formato en Markdown con numeración jerárquica."""

        try:
            return self.llm.invoke(wbs_prompt).content
        except Exception as e:
            return self._get_fallback_wbs(project)

    def _get_fallback_wbs(self, project: Project) -> str:
        """Fallback WBS template"""
        return f"""# Work Breakdown Structure: {project.name}

## 1. Iniciación del Proyecto
### 1.1 Project Charter
- 1.1.1 Definir objetivos
- 1.1.2 Identificar stakeholders
- 1.1.3 Aprobación del charter

### 1.2 Análisis Inicial
- 1.2.1 Análisis de requerimientos
- 1.2.2 Evaluación de riesgos
- 1.2.3 Estimación preliminar

## 2. Planificación
### 2.1 Planificación Detallada
- 2.1.1 Plan de proyecto
- 2.1.2 Cronograma detallado
- 2.1.3 Plan de recursos

### 2.2 Documentación
- 2.2.1 Especificaciones técnicas
- 2.2.2 Plan de calidad
- 2.2.3 Plan de comunicación

## 3. Ejecución
### 3.1 Desarrollo
- 3.1.1 Análisis y diseño
- 3.1.2 Implementación
- 3.1.3 Integración

### 3.2 Control de Calidad
- 3.2.1 Testing unitario
- 3.2.2 Testing de integración
- 3.2.3 Testing de usuario

## 4. Monitoreo y Control
### 4.1 Seguimiento
- 4.1.1 Reportes de progreso
- 4.1.2 Control de cambios
- 4.1.3 Gestión de riesgos

## 5. Cierre
### 5.1 Entrega
- 5.1.1 Documentación final
- 5.1.2 Transferencia de conocimiento
- 5.1.3 Lecciones aprendidas

---
**Generado**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

    async def _handle_template_request(self, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle template requests"""
        template_type = intent_analysis.get("parameters", {}).get("document_type", "").lower()

        templates = {
            "project_charter": self._get_project_charter_template(),
            "charter": self._get_project_charter_template(),
            "wbs": self._get_wbs_template(),
            "risk_register": self._get_risk_register_template(),
            "stakeholder_register": self._get_stakeholder_register_template(),
            "communication_plan": self._get_communication_plan_template()
        }

        if not template_type:
            available = ", ".join(templates.keys())
            return {
                "success": True,
                "response": f"""📄 **Plantillas Disponibles**

Puedo proporcionarte plantillas para:
- `project_charter` - Project Charter
- `wbs` - Work Breakdown Structure
- `risk_register` - Risk Register
- `stakeholder_register` - Stakeholder Register
- `communication_plan` - Communication Plan

💡 **Uso**: "Dame la plantilla de [tipo]"
**Ejemplo**: "Dame la plantilla de project_charter\"""",
                "available_templates": list(templates.keys())
            }

        template_content = templates.get(template_type)
        if template_content:
            return {
                "success": True,
                "response": f"""📄 **Plantilla: {template_type.replace('_', ' ').title()}**

```markdown
{template_content}
```

💡 **Tip**: Copia este contenido y personalízalo para tu proyecto específico.""",
                "template_type": template_type,
                "template_content": template_content
            }
        else:
            available = ", ".join(templates.keys())
            return {
                "success": False,
                "response": f"🚫 Plantilla '{template_type}' no encontrada.\n\n📄 **Disponibles**: {available}"
            }

    async def _handle_list_documents(self, project_id: Optional[int]) -> Dict[str, Any]:
        """List documents for a project"""
        if not project_id:
            return {
                "success": True,
                "response": """📂 **Listar Documentos del Proyecto**

Para ver los documentos necesito:
- 🆔 **ID del proyecto** (requerido)

💡 **Ejemplo**: "Ver documentos del proyecto 5\""""
            }

        try:
            documents = self.db_manager.get_project_documents(project_id)
            project = self.db_manager.get_project(project_id)

            if not project:
                return {
                    "success": False,
                    "response": f"🚫 Proyecto {project_id} no encontrado."
                }

            if not documents:
                return {
                    "success": True,
                    "response": f"""📂 **Documentos del Proyecto: {project.name}**

❌ No hay documentos creados aún.

🎯 **Documentos sugeridos para crear**:
- 📄 Project Charter
- 📊 Work Breakdown Structure (WBS)
- ⚠️ Risk Register
- 👥 Stakeholder Register

💡 **Para crear**: "Crear [tipo de documento] para proyecto {project_id}\""""
                }

            # Format document list
            doc_list = [f"📂 **Documentos del Proyecto: {project.name}**\n"]

            doc_types = {
                "project_charter": "📄 Project Charter",
                "wbs": "📊 Work Breakdown Structure",
                "risk_register": "⚠️ Risk Register",
                "stakeholder_register": "👥 Stakeholder Register",
                "communication_plan": "📢 Communication Plan"
            }

            for doc in documents:
                doc_icon = doc_types.get(doc.document_type, "📄")
                doc_list.append(f"- {doc_icon}: `{doc.file_path}`")
                doc_list.append(f"  📅 Creado: {doc.created_at.strftime('%Y-%m-%d %H:%M')}")

            return {
                "success": True,
                "response": "\n".join(doc_list),
                "document_count": len(documents),
                "documents": [{"type": doc.document_type, "path": doc.file_path} for doc in documents]
            }

        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return {
                "success": False,
                "response": "🚫 Error obteniendo lista de documentos."
            }

    def _get_project_charter_template(self) -> str:
        """Get project charter template"""
        return """# Project Charter: [PROJECT NAME]

## Executive Summary
[Brief description of the project and its business value]

## Project Information
- **Project Name**: [Name]
- **Project Manager**: [Name]
- **Sponsor**: [Name]
- **Start Date**: [Date]
- **Target End Date**: [Date]
- **Methodology**: [PMP/SAFe/Hybrid]

## Objectives
1. [Primary objective]
2. [Secondary objective]
3. [Additional objectives]

## Scope

### In Scope
- [Deliverable 1]
- [Deliverable 2]
- [Process/Function 1]

### Out of Scope
- [Excluded item 1]
- [Excluded item 2]
- [Limitation 1]

## Stakeholders
| Role | Name | Responsibility |
|------|------|----------------|
| Sponsor | [Name] | Executive support |
| Project Manager | [Name] | Project execution |
| Product Owner | [Name] | Requirements definition |

## High-Level Timeline
- **Initiation**: [Timeframe]
- **Planning**: [Timeframe]
- **Execution**: [Timeframe]
- **Closure**: [Timeframe]

## Budget Estimate
- **Total Budget**: [Amount]
- **Human Resources**: [Amount]
- **Technology**: [Amount]
- **Other**: [Amount]

## High-Level Risks
1. [Risk 1] - [Mitigation]
2. [Risk 2] - [Mitigation]
3. [Risk 3] - [Mitigation]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Approvals
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Sponsor | | | |
| Project Manager | | | |

---
*Document Created: [Date]*
"""

    def _get_wbs_template(self) -> str:
        """Get WBS template"""
        return """# Work Breakdown Structure: [PROJECT NAME]

## 1. Project Initiation
### 1.1 Project Charter
- 1.1.1 Define objectives
- 1.1.2 Identify stakeholders
- 1.1.3 Charter approval

### 1.2 Initial Analysis
- 1.2.1 Requirements analysis
- 1.2.2 Risk assessment
- 1.2.3 Initial estimation

## 2. Planning
### 2.1 Project Planning
- 2.1.1 Detailed project plan
- 2.1.2 Schedule development
- 2.1.3 Resource planning

### 2.2 Documentation
- 2.2.1 Technical specifications
- 2.2.2 Quality plan
- 2.2.3 Communication plan

## 3. Execution
### 3.1 Development
- 3.1.1 Analysis & design
- 3.1.2 Implementation
- 3.1.3 Integration

### 3.2 Quality Assurance
- 3.2.1 Unit testing
- 3.2.2 Integration testing
- 3.2.3 User acceptance testing

## 4. Monitoring & Control
### 4.1 Progress Tracking
- 4.1.1 Status reporting
- 4.1.2 Change control
- 4.1.3 Risk management

## 5. Project Closure
### 5.1 Delivery
- 5.1.1 Final documentation
- 5.1.2 Knowledge transfer
- 5.1.3 Lessons learned

---
*Effort Estimates and Dependencies to be added*
"""

    def _get_risk_register_template(self) -> str:
        """Get risk register template"""
        return """# Risk Register: [PROJECT NAME]

## Risk Assessment Matrix

| Risk ID | Risk Description | Category | Probability | Impact | Risk Score | Mitigation Strategy | Owner | Status |
|---------|------------------|----------|-------------|---------|------------|-------------------|--------|--------|
| R001 | [Risk description] | [Technical/Business/External] | [High/Medium/Low] | [High/Medium/Low] | [Score] | [Mitigation plan] | [Name] | [Open/Mitigated/Closed] |
| R002 | | | | | | | | |
| R003 | | | | | | | | |

## Risk Categories
- **Technical**: Technology-related risks
- **Business**: Business process and requirement risks
- **External**: External dependency and environmental risks
- **Resource**: People and resource availability risks

## Probability Scale
- **High (3)**: >70% chance of occurrence
- **Medium (2)**: 30-70% chance of occurrence
- **Low (1)**: <30% chance of occurrence

## Impact Scale
- **High (3)**: Significant impact on cost, schedule, or quality
- **Medium (2)**: Moderate impact, manageable
- **Low (1)**: Minor impact, easily recoverable

## Risk Response Strategies
- **Avoid**: Eliminate the risk
- **Mitigate**: Reduce probability or impact
- **Transfer**: Shift risk to third party
- **Accept**: Acknowledge and monitor

---
*Last Updated: [Date]*
"""

    def _get_stakeholder_register_template(self) -> str:
        """Get stakeholder register template"""
        return """# Stakeholder Register: [PROJECT NAME]

## Stakeholder Analysis Matrix

| Stakeholder | Role/Position | Interest | Influence | Power | Engagement Strategy | Communication Method | Frequency |
|-------------|---------------|----------|-----------|-------|-------------------|-------------------|-----------|
| [Name] | [Role] | [High/Medium/Low] | [High/Medium/Low] | [High/Medium/Low] | [Strategy] | [Email/Meeting/Report] | [Weekly/Monthly] |

## Stakeholder Categories

### Internal Stakeholders
- **Sponsor**: [Name and role]
- **Project Team**: [Team members]
- **End Users**: [User groups]

### External Stakeholders
- **Customers**: [Customer groups]
- **Vendors**: [Vendor information]
- **Regulatory**: [Regulatory bodies]

## Power/Interest Grid

### High Power, High Interest (Manage Closely)
- [Stakeholder names]

### High Power, Low Interest (Keep Satisfied)
- [Stakeholder names]

### Low Power, High Interest (Keep Informed)
- [Stakeholder names]

### Low Power, Low Interest (Monitor)
- [Stakeholder names]

## Communication Requirements
| Stakeholder | Information Needed | Preferred Format | Timing |
|-------------|-------------------|------------------|--------|
| [Name] | [Information type] | [Format] | [When] |

---
*Last Updated: [Date]*
"""

    def _get_communication_plan_template(self) -> str:
        """Get communication plan template"""
        return """# Communication Plan: [PROJECT NAME]

## Communication Matrix

| Information | Audience | Purpose | Frequency | Method | Responsible | Distribution Date |
|-------------|----------|---------|-----------|---------|-------------|-------------------|
| Status Report | Sponsor, PMO | Progress update | Weekly | Email | PM | Fridays |
| Team Meeting | Project Team | Coordination | Weekly | Meeting | PM | Mondays |
| Steering Committee | Executives | Decision making | Monthly | Presentation | PM | Month-end |

## Stakeholder Communication Preferences

| Stakeholder | Preferred Method | Language | Time Zone | Special Requirements |
|-------------|-----------------|----------|-----------|-------------------|
| [Name] | [Email/Meeting/Phone] | [Language] | [Zone] | [Requirements] |

## Communication Guidelines

### Meeting Guidelines
- All meetings will have agendas distributed 24 hours in advance
- Meeting minutes will be distributed within 24 hours
- Action items will be tracked and followed up

### Reporting Structure
- **Daily**: Stand-up meetings (team level)
- **Weekly**: Status reports to sponsor
- **Monthly**: Steering committee updates
- **Ad-hoc**: Issue escalation as needed

### Escalation Process
1. **Level 1**: Project Manager
2. **Level 2**: Project Sponsor
3. **Level 3**: Steering Committee

### Communication Channels
- **Urgent**: Phone/Instant messaging
- **Formal**: Email with read receipts
- **Documentation**: Project repository
- **Collaboration**: Team workspace

## Document Management
- All project documents stored in [Location]
- Version control managed by [System]
- Access permissions managed by [Person]

---
*Last Updated: [Date]*
"""

    def _handle_general_document_query(self, user_input: str, project_id: Optional[int]) -> Dict[str, Any]:
        """Handle general document-related queries"""
        query_prompt = f"""Como Document Agent especializado en documentación PMP/SAFe, responde a esta consulta:

Consulta: "{user_input}"
Proyecto ID: {project_id if project_id else "No especificado"}

Proporciona una respuesta útil sobre:
- Tipos de documentos disponibles
- Cómo crear documentos específicos
- Mejores prácticas de documentación
- Templates y plantillas
- Estándares PMP/SAFe aplicables

Respuesta en tono profesional pero amigable, con ejemplos específicos."""

        try:
            response = self.llm.invoke(query_prompt).content
            return {
                "success": True,
                "response": response,
                "query_type": "document_general"
            }
        except Exception as e:
            return {
                "success": True,
                "response": """📄 **Document Agent - Ayuda General**

Puedo ayudarte con:

🎯 **Crear Documentos**:
- Project Charter
- Work Breakdown Structure (WBS)
- Risk Register
- Stakeholder Register
- Communication Plan

🔧 **Comandos útiles**:
- `"Crear charter para proyecto [ID]"`
- `"Generar WBS"`
- `"Dame la plantilla de risk_register"`
- `"Ver documentos del proyecto [ID]"`

💡 **¿Qué necesitas crear?**"""
            }

    def get_agent_capabilities(self) -> List[str]:
        """Get list of this agent's capabilities"""
        return [
            "project_charter",
            "wbs_creation",
            "risk_register",
            "stakeholder_register",
            "communication_plan",
            "template_management",
            "document_generation",
            "pmp_standards",
            "safe_standards"
        ]