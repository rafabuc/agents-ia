"""
Project Manager Agent - Main coordinator and decision maker
Handles high-level project management tasks and coordinates with specialist agents
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from .base_agent import BaseAgent
from storage.database_manager import DatabaseManager
from models.project import Project, ProjectStatus
from utils.logger import logger
from config.settings import settings


class ProjectManagerAgent(BaseAgent):
    """
    Project Manager Agent - Central coordinator for project management tasks

    This agent acts as the main interface for users and coordinates with
    specialized agents when needed. It handles:
    - Project creation and lifecycle management
    - High-level decision making
    - User interaction and natural language understanding
    - Delegation to specialist agents
    """

    def __init__(self):
        super().__init__(
            name="project_manager_agent",
            description="Main project management coordinator and user interface agent"
        )
        self.db_manager = DatabaseManager()
        self.conversation_context = {}  # Store conversation state

        # LLM is already initialized in BaseAgent as self.llm

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        return """Eres un Project Manager Agent experto, el coordinador principal del sistema de gestión de proyectos.

Tu rol es:
1. **Interfaz principal** - Ser el punto de contacto principal con el usuario
2. **Coordinador inteligente** - Decidir cuándo delegar tareas a agentes especialistas
3. **Gestor de contexto** - Mantener el contexto de conversaciones y proyectos
4. **Facilitador** - Ayudar al usuario a navegar el sistema de forma natural

Capacidades principales:
- Crear y gestionar proyectos completos
- Entender peticiones en lenguaje natural
- Coordinar con agentes especialistas (Documentos, Riesgos, Stakeholders, etc.)
- Mantener contexto conversacional
- Proporcionar respuestas inteligentes y proactivas

Cuando un usuario hace una petición:
1. Analiza la intención y contexto
2. Decide si puedes manejarla directamente o necesitas delegar
3. Si delegas, coordina con los agentes apropiados
4. Combina resultados y proporciona una respuesta cohesiva
5. Mantén el contexto para la próxima interacción

Siempre sé conversacional, útil y proactivo en tus sugerencias.
Usa emojis apropiados para hacer la interacción más amigable.
"""

    async def process_with_context(self, context) -> Dict[str, Any]:
        """Process request with full task context"""
        try:
            user_input = context.user_input
            project_id = context.project_id

            # Update conversation context
            self._update_conversation_context(user_input, project_id)

            # Analyze intent with LLM
            intent_analysis = self._analyze_intent_with_llm(user_input)

            # Process based on intent
            if intent_analysis["intent"] == "create_project":
                return await self._handle_project_creation(intent_analysis, context)
            elif intent_analysis["intent"] == "list_projects":
                return self._handle_list_projects()
            elif intent_analysis["intent"] == "project_status":
                return await self._handle_project_status(intent_analysis, project_id)
            elif intent_analysis["intent"] == "general_help":
                return self._handle_general_help()
            else:
                return self._handle_general_query(user_input, project_id)

        except Exception as e:
            logger.error(f"Error in ProjectManagerAgent.process_with_context: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "🚫 Disculpa, hubo un error procesando tu solicitud. ¿Podrías intentar de nuevo?"
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

    def _analyze_intent_with_llm(self, user_input: str) -> Dict[str, Any]:
        """Analyze user intent using LLM"""
        analysis_prompt = f"""Analiza la siguiente petición del usuario y extrae:
1. Intención principal
2. Parámetros relevantes
3. Nivel de confianza

Petición del usuario: "{user_input}"

Intenciones posibles:
- create_project: Crear un nuevo proyecto
- list_projects: Listar proyectos existentes
- project_status: Ver estado de un proyecto
- document_request: Solicitar documentos (charter, WBS, etc.)
- risk_analysis: Análisis de riesgos
- general_help: Ayuda general
- general_query: Consulta general

Responde en formato JSON:
{{
    "intent": "intención_detectada",
    "confidence": 0.8,
    "parameters": {{
        "project_name": "nombre si se menciona",
        "project_id": "ID si se menciona",
        "document_type": "tipo de documento si aplica"
    }},
    "reasoning": "explicación breve"
}}"""

        try:
            # Use LangChain LLM invoke method
            response = self.llm.invoke(analysis_prompt).content

            # Try to parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                # Fallback to simple keyword detection
                return self._fallback_intent_detection(user_input)

        except Exception as e:
            logger.warning(f"LLM intent analysis failed: {str(e)}, using fallback")
            return self._fallback_intent_detection(user_input)

    def _fallback_intent_detection(self, user_input: str) -> Dict[str, Any]:
        """Fallback intent detection using simple keywords"""
        user_input_lower = user_input.lower()

        # Simple keyword-based detection
        if any(keyword in user_input_lower for keyword in ["crear proyecto", "nuevo proyecto", "iniciar proyecto"]):
            return {
                "intent": "create_project",
                "confidence": 0.7,
                "parameters": {"project_name": self._extract_project_name(user_input)},
                "reasoning": "Keywords match project creation"
            }
        elif any(keyword in user_input_lower for keyword in ["listar", "mostrar proyectos", "ver proyectos"]):
            return {
                "intent": "list_projects",
                "confidence": 0.8,
                "parameters": {},
                "reasoning": "Keywords match project listing"
            }
        elif any(keyword in user_input_lower for keyword in ["ayuda", "help", "cómo"]):
            return {
                "intent": "general_help",
                "confidence": 0.9,
                "parameters": {},
                "reasoning": "Help keywords detected"
            }
        else:
            return {
                "intent": "general_query",
                "confidence": 0.5,
                "parameters": {},
                "reasoning": "No specific intent detected"
            }

    def _extract_project_name(self, user_input: str) -> Optional[str]:
        """Extract project name from user input"""
        import re

        # Look for single quoted strings
        quoted = re.search(r"'([^']+)'", user_input)
        if quoted:
            return quoted.group(1)

        # Look for double quoted strings
        quoted = re.search(r'"([^"]+)"', user_input)
        if quoted:
            return quoted.group(1)

        # Look after keywords
        keywords = ["proyecto", "llamado", "named", "para"]
        for keyword in keywords:
            if keyword in user_input.lower():
                parts = user_input.lower().split(keyword)
                if len(parts) > 1:
                    # Clean up the potential name part
                    name_part = parts[1].strip()
                    # Remove common words that might follow
                    for stop_word in ["con", "using", "metodologia", "methodology"]:
                        if stop_word in name_part:
                            name_part = name_part.split(stop_word)[0].strip()

                    if name_part:
                        potential_name = name_part.split()[0:3]  # Take first few words
                        return " ".join(potential_name)

        return None

    async def _handle_project_creation(self, intent_analysis: Dict[str, Any], context) -> Dict[str, Any]:
        """Handle project creation requests"""
        try:
            parameters = intent_analysis.get("parameters", {})
            project_name = parameters.get("project_name")

            if not project_name:
                return {
                    "success": True,
                    "response": """🚀 **¡Perfecto! Vamos a crear un nuevo proyecto.**

Para crear tu proyecto necesito:
- 📝 **Nombre del proyecto** (requerido)
- 📋 **Descripción** (opcional)
- 🛠️ **Metodología** (PMP, SAFe, Hybrid - por defecto PMP)

💡 **Ejemplo**: "Crear proyecto 'App Móvil E-commerce' con metodología PMP"

¿Cómo te gustaría llamar a tu proyecto?""",
                    "requires_follow_up": True,
                    "next_expected": "project_name"
                }

            # Create the project
            project = self.db_manager.create_project(
                name=project_name,
                description=parameters.get("description", f"Proyecto {project_name}"),
                methodology=parameters.get("methodology", "PMP"),
                project_data={}  # Additional metadata if needed
            )

            if project:
                # Update conversation context with new project
                self.conversation_context["last_project_id"] = project.id
                self.conversation_context["last_project_name"] = project.name

                response = f"""✅ **¡Proyecto creado exitosamente!**

📋 **Proyecto**: {project.name}
🆔 **ID**: {project.id}
🛠️ **Metodología**: {project.methodology}
📅 **Creado**: {datetime.now().strftime('%Y-%m-%d')}

🎯 **Próximos pasos sugeridos**:
1. 📄 Generar Project Charter: `"Crear charter para {project.name}"`
2. ⚠️ Identificar riesgos: `"Analizar riesgos del proyecto"`
3. 👥 Mapear stakeholders: `"Identificar stakeholders"`
4. 📊 Crear WBS: `"Generar WBS para el proyecto"`

💬 **¿Qué te gustaría hacer ahora?**"""

                return {
                    "success": True,
                    "response": response,
                    "project_id": project.id,
                    "project_name": project.name,
                    "suggested_actions": [
                        "create_charter",
                        "analyze_risks",
                        "identify_stakeholders",
                        "create_wbs"
                    ]
                }
            else:
                return {
                    "success": False,
                    "response": "🚫 No pude crear el proyecto. Verifica que el nombre no esté duplicado.",
                    "error": "Project creation failed"
                }

        except Exception as e:
            logger.error(f"Error in project creation: {str(e)}")
            return {
                "success": False,
                "response": "🚫 Error creando el proyecto. Por favor intenta de nuevo.",
                "error": str(e)
            }

    def _handle_list_projects(self) -> Dict[str, Any]:
        """Handle project listing requests"""
        try:
            projects = self.db_manager.list_projects(limit=10)

            if not projects:
                return {
                    "success": True,
                    "response": """📂 **No hay proyectos creados aún**

🚀 **¿Quieres crear tu primer proyecto?**
Simplemente dime: "Crear proyecto [nombre]"

💡 **Ejemplo**: "Crear proyecto App Móvil E-commerce\""""
                }

            # Format project list
            project_list = ["📋 **Tus Proyectos**:\n"]

            for i, project in enumerate(projects, 1):
                status_emoji = {
                    "planning": "📋",
                    "executing": "⚡",
                    "completed": "✅",
                    "on_hold": "⏸️"
                }.get(project.status.value, "📋")

                project_list.append(
                    f"{i}. {status_emoji} **{project.name}** (ID: {project.id})\n"
                    f"   📅 {project.created_at.strftime('%Y-%m-%d')} | "
                    f"🛠️ {project.methodology} | "
                    f"📊 {project.status.value.title()}\n"
                )

            project_list.append("\n💬 **Para trabajar con un proyecto**:")
            project_list.append("- `\"Ver proyecto [ID]\"` - Ver detalles")
            project_list.append("- `\"Crear charter para proyecto [ID]\"` - Generar documentos")
            project_list.append("- `\"Estado del proyecto [ID]\"` - Ver estado actual")

            return {
                "success": True,
                "response": "".join(project_list),
                "projects": [{"id": p.id, "name": p.name, "status": p.status.value} for p in projects]
            }

        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            return {
                "success": False,
                "response": "🚫 Error obteniendo la lista de proyectos.",
                "error": str(e)
            }

    async def _handle_project_status(self, intent_analysis: Dict[str, Any], project_id: Optional[int]) -> Dict[str, Any]:
        """Handle project status requests"""
        try:
            # Determine project ID
            target_project_id = project_id or intent_analysis.get("parameters", {}).get("project_id")

            if not target_project_id and "last_project_id" in self.conversation_context:
                target_project_id = self.conversation_context["last_project_id"]

            if not target_project_id:
                return {
                    "success": True,
                    "response": """🤔 **¿De qué proyecto quieres ver el estado?**

💡 **Opciones**:
- `\"Estado del proyecto 5\"` - Por ID
- `\"Estado de mi último proyecto\"` - Último trabajado
- `\"Listar proyectos\"` - Ver todos primero

¿Cuál proyecto te interesa?""",
                    "requires_follow_up": True
                }

            # Get project details
            project = self.db_manager.get_project(target_project_id)

            if not project:
                return {
                    "success": False,
                    "response": f"🚫 No encontré el proyecto con ID {target_project_id}.\n\n💡 Usa `\"Listar proyectos\"` para ver los disponibles."
                }

            # Get project documents and progress
            documents = self.db_manager.get_project_documents(project.id)

            # Calculate completion percentage
            expected_docs = ["project_charter", "wbs", "risk_register", "schedule"]
            completed_docs = len([doc for doc in documents if doc.document_type in expected_docs])
            completion = (completed_docs / len(expected_docs)) * 100

            status_emoji = {
                "planning": "📋",
                "executing": "⚡",
                "completed": "✅",
                "on_hold": "⏸️"
            }.get(project.status.value, "📋")

            response = f"""📊 **Estado del Proyecto: {project.name}**

🆔 **ID**: {project.id}
{status_emoji} **Estado**: {project.status.value.title()}
🛠️ **Metodología**: {project.methodology}
📅 **Creado**: {project.created_at.strftime('%Y-%m-%d %H:%M')}
📈 **Progreso**: {completion:.0f}% completado

📄 **Documentos**:"""

            # Add document status
            doc_status = {
                "project_charter": "❌",
                "wbs": "❌",
                "risk_register": "❌",
                "schedule": "❌"
            }

            for doc in documents:
                if doc.document_type in doc_status:
                    doc_status[doc.document_type] = "✅"

            response += f"""
- {doc_status["project_charter"]} Project Charter
- {doc_status["wbs"]} Work Breakdown Structure (WBS)
- {doc_status["risk_register"]} Risk Register
- {doc_status["schedule"]} Schedule/Cronograma

💡 **Próximas acciones sugeridas**:"""

            # Suggest next actions based on missing documents
            suggestions = []
            if doc_status["project_charter"] == "❌":
                suggestions.append("📄 Crear Project Charter")
            if doc_status["risk_register"] == "❌":
                suggestions.append("⚠️ Desarrollar Risk Register")
            if doc_status["wbs"] == "❌":
                suggestions.append("📊 Generar WBS")

            if suggestions:
                for suggestion in suggestions[:3]:  # Top 3 suggestions
                    response += f"\n- {suggestion}"
            else:
                response += "\n- ✅ ¡Proyecto bien documentado!"

            return {
                "success": True,
                "response": response,
                "project_data": {
                    "id": project.id,
                    "name": project.name,
                    "status": project.status.value,
                    "completion": completion,
                    "document_count": len(documents)
                }
            }

        except Exception as e:
            logger.error(f"Error getting project status: {str(e)}")
            return {
                "success": False,
                "response": "🚫 Error obteniendo el estado del proyecto.",
                "error": str(e)
            }

    def _handle_general_help(self) -> Dict[str, Any]:
        """Handle general help requests"""
        return {
            "success": True,
            "response": """🤖 **¡Hola! Soy tu Project Manager Agent**

🎯 **¿En qué puedo ayudarte hoy?**

📋 **Gestión de Proyectos**:
- `"Crear proyecto [nombre]"` - Crear nuevo proyecto
- `"Listar proyectos"` - Ver todos tus proyectos
- `"Estado del proyecto [ID]"` - Ver estado y progreso

📄 **Documentación PMP**:
- `"Crear charter para proyecto X"` - Project Charter
- `"Generar WBS"` - Work Breakdown Structure
- `"Analizar riesgos"` - Risk Register
- `"Identificar stakeholders"` - Stakeholder mapping

⚡ **Comandos Naturales**:
Puedes hablarme de forma natural, como:
- "Necesito crear un proyecto para mi app móvil"
- "¿Qué documentos le faltan a mi último proyecto?"
- "Ayúdame con la gestión de riesgos"

🧠 **Soy inteligente**: Entiendo contexto y puedo ayudarte paso a paso.

💬 **¿Por dónde empezamos?**""",
            "available_commands": [
                "crear proyecto",
                "listar proyectos",
                "estado del proyecto",
                "crear charter",
                "analizar riesgos",
                "ayuda"
            ]
        }

    def _handle_general_query(self, user_input: str, project_id: Optional[int]) -> Dict[str, Any]:
        """Handle general queries using LLM"""
        try:
            # Get conversation context
            context_info = self._get_conversation_context_for_llm()

            query_prompt = f"""Como Project Manager Agent experto, responde a esta consulta del usuario.

Contexto de conversación:
{context_info}

Consulta del usuario: "{user_input}"

Proporciona una respuesta útil, conversacional y específica. Si la consulta requiere:
- Crear algo: Explica los pasos y ofrece hacerlo
- Ver información: Indica qué necesitas o sugiere comandos específicos
- Ayuda: Proporciona orientación clara y ejemplos

Mantén un tono amigable y profesional, usa emojis apropiados, y ofrece próximos pasos concretos."""

            response = self.llm.invoke(query_prompt).content

            return {
                "success": True,
                "response": response,
                "query_type": "general",
                "context_used": bool(context_info)
            }

        except Exception as e:
            logger.error(f"Error in general query handling: {str(e)}")
            return {
                "success": True,
                "response": """🤔 Entiendo que necesitas ayuda, pero no estoy seguro de los detalles.

💡 **¿Podrías ser más específico?** Por ejemplo:
- "Crear proyecto para [descripción]"
- "Ver estado de proyecto [ID]"
- "Necesito ayuda con [tema específico]"
- "Listar proyectos"

🚀 También puedes decir "ayuda" para ver todas las opciones disponibles.""",
                "suggested_rephrase": True
            }

    def _update_conversation_context(self, user_input: str, project_id: Optional[int]):
        """Update conversation context with current interaction"""
        self.conversation_context.update({
            "last_input": user_input,
            "timestamp": datetime.now().isoformat(),
            "current_project_id": project_id
        })

    def _get_conversation_context_for_llm(self) -> str:
        """Get formatted conversation context for LLM prompts"""
        if not self.conversation_context:
            return "No hay contexto previo de conversación."

        context_parts = []

        if "last_project_id" in self.conversation_context:
            context_parts.append(f"- Último proyecto trabajado: ID {self.conversation_context['last_project_id']}")

        if "last_project_name" in self.conversation_context:
            context_parts.append(f"- Nombre del proyecto: {self.conversation_context['last_project_name']}")

        if "last_input" in self.conversation_context:
            context_parts.append(f"- Última consulta: {self.conversation_context['last_input']}")

        return "\n".join(context_parts) if context_parts else "Conversación recién iniciada."

    def get_agent_capabilities(self) -> List[str]:
        """Get list of this agent's capabilities"""
        return [
            "project_creation",
            "project_management",
            "natural_language_processing",
            "conversation_coordination",
            "task_delegation",
            "context_management",
            "user_interaction"
        ]