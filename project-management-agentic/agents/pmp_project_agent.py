from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

from .base_agent import BaseAgent
from storage.file_manager import FileManager
from models.project import Project, ProjectStatus
from config.settings import settings
from utils.logger import logger


class PMPProjectAgent(BaseAgent):
    """Agent specialized in PMP project creation and management."""
    
    def __init__(self):
        super().__init__(
            name="PMP_Project_Agent",
            description="Creates and manages projects using PMP and SAFe methodologies"
        )
        self.file_manager = FileManager()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.agent_executor = None
    
    def get_system_prompt(self) -> str:
        return """You are an expert Project Management Professional (PMP) and SAFe specialist. 
        You help create comprehensive project documentation following PMI standards and SAFe practices.
        
        Your responsibilities include:
        1. Creating project charters
        2. Developing Work Breakdown Structures (WBS)
        3. Defining project scope and deliverables
        4. Creating project schedules and milestones
        5. Identifying stakeholders and their roles
        6. Developing risk registers
        7. Creating communication plans
        8. Following PMP best practices and SAFe principles
        
        Always provide structured, detailed responses that can be used as official project documentation.
        Save all generated documents to the file system for future reference.
        """
    
    def _create_agent(self) -> AgentExecutor:
        """Create the PMP project agent."""
        tools = [
            self._create_project_tool(),
            self._save_project_document_tool(),
            self._get_project_template_tool(),
            self._update_project_status_tool()
        ]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _create_project_tool(self) -> Tool:
        """Tool to create a new project in the database."""
        def create_project(project_data: str) -> str:
            try:
                data = json.loads(project_data)

                # Create project in database
                project = self.db_manager.create_project(
                    name=data.get("name"),
                    description=data.get("description"),
                    methodology=data.get("methodology", "PMP"),
                    project_data=data
                )

                # Now we should be able to access project attributes safely
                project_id = project.id
                project_name = project.name

                # Create project directory
                project_dir = self.file_manager.create_project_directory(project_id)

                logger.info(f"Created project {project_name} with ID {project_id}")

                return f"Project '{project_name}' created successfully with ID {project_id}. Project directory: {project_dir}"

            except Exception as e:
                logger.error(f"Error creating project: {str(e)}")
                return f"Error creating project: {str(e)}"

        return Tool(
            name="create_project",
            description="Create a new project with the given data. Input should be JSON string with project information.",
            func=create_project
        )
    
    def _save_project_document_tool(self) -> Tool:
        """Tool to save project documents."""
        def save_document(document_info: str) -> str:
            try:
                data = json.loads(document_info)
                project_id = data.get("project_id")
                document_type = data.get("document_type")
                content = data.get("content")
                filename = data.get("filename")
                
                if not all([project_id, document_type, content]):
                    return "Error: Missing required fields (project_id, document_type, content)"
                
                # Save to file system
                file_path = self.file_manager.save_project_document(
                    project_id=project_id,
                    document_type=document_type,
                    content=content,
                    filename=filename
                )
                
                # Save to database
                self.db_manager.create_project_document(
                    project_id=project_id,
                    document_type=document_type,
                    file_path=file_path,
                    content=content
                )
                
                return f"Document saved successfully: {file_path}"
                
            except Exception as e:
                logger.error(f"Error saving document: {str(e)}")
                return f"Error saving document: {str(e)}"
        
        return Tool(
            name="save_project_document",
            description="Save a project document to file system and database. Input should be JSON with project_id, document_type, content, and optional filename.",
            func=save_document
        )
    
    def _get_project_template_tool(self) -> Tool:
        """Tool to get project templates."""
        def get_template(template_type: str) -> str:
            try:
                templates = {
                    "project_charter": self._get_project_charter_template(),
                    "wbs": self._get_wbs_template(),
                    "risk_register": self._get_risk_register_template(),
                    "stakeholder_register": self._get_stakeholder_register_template(),
                    "communication_plan": self._get_communication_plan_template()
                }
                
                template = templates.get(template_type.lower())
                if template:
                    return template
                else:
                    available = ", ".join(templates.keys())
                    return f"Template not found. Available templates: {available}"
                    
            except Exception as e:
                return f"Error getting template: {str(e)}"
        
        return Tool(
            name="get_project_template",
            description="Get a project template by type. Available types: project_charter, wbs, risk_register, stakeholder_register, communication_plan",
            func=get_template
        )
    
    def _update_project_status_tool(self) -> Tool:
        """Tool to update project status."""
        def update_status(status_data: str) -> str:
            try:
                data = json.loads(status_data)
                project_id = data.get("project_id")
                new_status = data.get("status")
                
                if not project_id or not new_status:
                    return "Error: Missing project_id or status"
                
                # Update in database
                success = self.db_manager.update_project_status(project_id, new_status)
                
                if success:
                    return f"Project {project_id} status updated to {new_status}"
                else:
                    return f"Error updating project status"
                    
            except Exception as e:
                return f"Error updating project status: {str(e)}"
        
        return Tool(
            name="update_project_status",
            description="Update project status. Input should be JSON with project_id and status.",
            func=update_status
        )
    
    def _get_project_charter_template(self) -> str:
        return """
# PROJECT CHARTER TEMPLATE

## 1. PROJECT INFORMATION
- Project Name: 
- Project Manager: 
- Sponsor: 
- Start Date: 
- Expected End Date: 
- Budget: 

## 2. PROJECT DESCRIPTION
[Detailed description of the project]

## 3. PROJECT OBJECTIVES
- Primary Objective:
- Secondary Objectives:
- Success Criteria:

## 4. PROJECT SCOPE
### In Scope:
- [List items included in project scope]

### Out of Scope:
- [List items explicitly excluded]

## 5. HIGH-LEVEL REQUIREMENTS
- [List major requirements]

## 6. HIGH-LEVEL RISKS
- [Identify major risks]

## 7. HIGH-LEVEL ASSUMPTIONS
- [List key assumptions]

## 8. HIGH-LEVEL CONSTRAINTS
- [List major constraints]

## 9. STAKEHOLDERS
| Name | Role | Contact | Influence/Interest |
|------|------|---------|-------------------|
|      |      |         |                   |

## 10. AUTHORIZATION
Project Manager Signature: _______________ Date: ___________
Sponsor Signature: _______________ Date: ___________
"""
    
    def _get_wbs_template(self) -> str:
        return """
# WORK BREAKDOWN STRUCTURE (WBS)

## 1.0 [PROJECT NAME]
### 1.1 Project Management
    1.1.1 Project Planning
    1.1.2 Project Monitoring & Control
    1.1.3 Project Closure

### 1.2 [MAJOR DELIVERABLE 1]
    1.2.1 [Sub-deliverable 1.1]
    1.2.2 [Sub-deliverable 1.2]
    1.2.3 [Sub-deliverable 1.3]

### 1.3 [MAJOR DELIVERABLE 2]
    1.3.1 [Sub-deliverable 2.1]
    1.3.2 [Sub-deliverable 2.2]

### 1.4 Quality Assurance
    1.4.1 Quality Planning
    1.4.2 Quality Control
    1.4.3 Quality Improvement

### 1.5 Testing & Validation
    1.5.1 Test Planning
    1.5.2 Test Execution
    1.5.3 User Acceptance Testing
"""
    
    def _get_risk_register_template(self) -> str:
        return """
# RISK REGISTER

| ID | Risk Description | Category | Probability | Impact | Risk Score | Mitigation Strategy | Owner | Status |
|----|------------------|----------|-------------|---------|------------|-------------------|-------|---------|
| R001 | [Risk description] | Technical/Schedule/Budget/Resource | H/M/L | H/M/L | [P×I] | [Mitigation plan] | [Owner] | Open/Closed |
| R002 | | | | | | | | |

## Risk Categories:
- Technical: Technology, performance, quality issues
- Schedule: Timeline, dependency, resource availability
- Budget: Cost overruns, funding issues
- Resource: Staff availability, skill gaps
- External: Vendor, regulatory, market changes

## Probability/Impact Scale:
- High (H): > 70% / Major impact on project objectives
- Medium (M): 30-70% / Moderate impact on project objectives  
- Low (L): < 30% / Minor impact on project objectives
"""
    
    def _get_stakeholder_register_template(self) -> str:
        return """
# STAKEHOLDER REGISTER

| Name | Title/Role | Organization | Contact Info | Influence | Interest | Engagement Strategy |
|------|------------|--------------|--------------|-----------|----------|-------------------|
| [Name] | [Title] | [Org] | [Email/Phone] | H/M/L | H/M/L | [Strategy] |

## Influence/Interest Matrix:
- High Influence, High Interest: Manage Closely
- High Influence, Low Interest: Keep Satisfied  
- Low Influence, High Interest: Keep Informed
- Low Influence, Low Interest: Monitor

## Engagement Strategies:
- Regular meetings and updates
- Formal reporting
- Ad-hoc communications
- Consultation on key decisions
"""
    
    def _get_communication_plan_template(self) -> str:
        return """
# COMMUNICATION PLAN

## Communication Requirements

| Stakeholder | Information Needs | Frequency | Method | Responsible | Format |
|-------------|-------------------|-----------|---------|-------------|---------|
| Project Sponsor | Status updates, issues, decisions | Weekly | Email/Meeting | PM | Status Report |
| Project Team | Tasks, schedules, issues | Daily | Standup/Slack | PM | Verbal/Chat |
| End Users | Progress, training, go-live | Bi-weekly | Newsletter | PM | Email |

## Communication Methods:
- Face-to-face meetings
- Video conferences
- Email updates
- Project dashboard
- Status reports
- Team chat (Slack/Teams)

## Escalation Matrix:
| Issue Level | Escalate To | Timeline |
|-------------|-------------|----------|
| Level 1 - Team issues | Team Lead | Immediate |
| Level 2 - Project issues | Project Manager | 24 hours |
| Level 3 - Major issues | Project Sponsor | 48 hours |
"""

    def process(self, input_text: str, session_id: Optional[int] = None) -> Dict[str, Any]:
        """Process input using the PMP project agent with its specialized tools."""
        try:
            # Store session info for context
            if session_id:
                logger.info(f"Processing request for session {session_id}")

            # For now, let's use a simpler approach to avoid the function calling issue
            # We'll detect intent and call tools directly based on keywords
            response = self._process_with_simple_logic(input_text)

            # Update memory with the conversation
            self.memory.chat_memory.add_user_message(input_text)
            self.memory.chat_memory.add_ai_message(response)

            # Format response with additional context
            formatted_response = self._format_response({"output": response}, input_text)

            logger.info(f"PMP Agent processed request: {input_text[:100]}...")

            return {
                "success": True,
                "agent": self.name,
                "response": formatted_response,
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id,
                "suggestions": self._generate_next_step_suggestions(input_text, {"output": response})
            }

        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(f"PMP Agent error: {error_msg}")

            return {
                "success": False,
                "agent": self.name,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": session_id
            }

    def _process_with_simple_logic(self, input_text: str) -> str:
        """Process input using LLM-powered intent detection."""
        try:
            # Use LLM to detect intent instead of keyword matching
            intent_data = self._detect_intent_with_llm(input_text)
            intent = intent_data.get("intent")
            parameters = intent_data.get("parameters", {})
            confidence = intent_data.get("confidence", 0)

            logger.info(f"Detected intent: {intent} (confidence: {confidence})")

            # Route to appropriate handler based on LLM-detected intent
            if intent == "create_project":
                return self._handle_create_project_request_with_params(input_text, parameters)

            elif intent == "list_projects":
                return self._handle_list_projects_request(input_text)

            elif intent == "save_charter":
                return self._handle_save_charter_request_with_params(input_text, parameters)

            elif intent == "save_wbs":
                return self._handle_save_wbs_request_with_params(input_text, parameters)

            elif intent == "save_risk":
                return self._handle_save_risk_request_with_params(input_text, parameters)

            elif intent == "view_template":
                return self._handle_view_template_request(parameters)

            elif intent == "help":
                return self._get_help_message()

            elif intent == "other" or confidence < 0.5:
                return self._handle_unclear_request(input_text, intent_data)

            else:
                return f"""🤖 **He detectado la intención:** {intent}

Pero esta funcionalidad aún no está implementada completamente.

💡 **Intenciones disponibles:**
- Crear proyectos
- Listar proyectos
- Guardar documentos (charter, wbs, riesgos)
- Ver plantillas
- Ayuda

¿Puedes ser más específico sobre qué necesitas hacer?"""

        except Exception as e:
            logger.error(f"Error in _process_with_simple_logic: {str(e)}")
            return f"❌ Error procesando tu petición: {str(e)}\n\n💡 Intenta con comandos como 'crear proyecto', 'listar proyectos' o 'ayuda'."

    def _handle_create_project_request(self, input_text: str) -> str:
        """Handle project creation requests."""
        try:
            # Extract project name from input or ask for it
            if "crear proyecto" in input_text.lower():
                # Try to extract project name
                words = input_text.split()
                if len(words) > 2:
                    project_name = " ".join(words[2:])  # Everything after "crear proyecto"
                else:
                    project_name = "Mi Nuevo Proyecto PMP"
            else:
                project_name = "Nuevo Proyecto PMP"

            # Create basic project data
            project_data = {
                "name": project_name,
                "description": f"Proyecto creado usando metodología PMP - {project_name}",
                "methodology": "PMP",
                "created_by": "PMP_Project_Agent",
                "status": "PLANNING"
            }

            # Use the create_project tool directly
            tool = self._create_project_tool()
            result = tool.func(json.dumps(project_data))

            return f"""✅ {result}

🎯 **Próximos pasos recomendados:**
1. Crear un Project Charter: escribe `charter`
2. Desarrollar WBS: escribe `wbs`
3. Identificar stakeholders: escribe `stakeholder`
4. Registrar riesgos: escribe `risk`

¿Qué te gustaría hacer ahora?"""

        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            return f"❌ Error al crear el proyecto: {str(e)}\n\nIntenta nuevamente con: 'crear proyecto [nombre del proyecto]'"

    def _enhance_input_with_context(self, input_text: str) -> str:
        """Enhance user input with contextual PMP guidance."""
        # Analyze input for common PMP keywords and provide context
        pmp_keywords = {
            "project": "Consider using PMP project creation tools and templates.",
            "charter": "I can help you create a comprehensive project charter using the project_charter template.",
            "wbs": "Let me assist you with Work Breakdown Structure creation using the wbs template.",
            "risk": "I can help you create and manage a risk register using the risk_register template.",
            "stakeholder": "Let me help you identify and document stakeholders using the stakeholder_register template.",
            "communication": "I can assist with creating a communication plan using the communication_plan template.",
            "plan": "I can help you create various project plans and documentation using PMP best practices."
        }

        input_lower = input_text.lower()
        context_hints = []

        for keyword, hint in pmp_keywords.items():
            if keyword in input_lower:
                context_hints.append(hint)

        if context_hints:
            enhanced = f"{input_text}\n\nContext: {' '.join(context_hints[:2])}"  # Limit to 2 hints
            return enhanced

        return input_text

    def _format_response(self, agent_result: Dict[str, Any], original_input: str) -> str:
        """Format the agent response with additional helpful information."""
        base_response = agent_result.get("output", "No response generated")

        # Add helpful formatting and structure
        if "created successfully" in base_response.lower():
            base_response += "\n\n💡 **Next Steps:**\n- Review the generated documents\n- Share with stakeholders for feedback\n- Consider creating additional project artifacts"

        elif "template" in base_response.lower():
            base_response += "\n\n📋 **Available Templates:**\n- project_charter\n- wbs (Work Breakdown Structure)\n- risk_register\n- stakeholder_register\n- communication_plan"

        return base_response

    def _extract_tools_used(self, agent_result: Dict[str, Any]) -> List[str]:
        """Extract which tools were used during the agent execution."""
        tools_used = []

        # This is a simplified extraction - in practice, you'd track this during execution
        output = agent_result.get("output", "").lower()

        if "project" in output and "created" in output:
            tools_used.append("create_project")
        if "document" in output and "saved" in output:
            tools_used.append("save_project_document")
        if "template" in output:
            tools_used.append("get_project_template")
        if "status" in output and "updated" in output:
            tools_used.append("update_project_status")

        return tools_used

    def _generate_next_step_suggestions(self, input_text: str, agent_result: Dict[str, Any]) -> List[str]:
        """Generate helpful next step suggestions based on the interaction."""
        suggestions = []
        output = agent_result.get("output", "").lower()
        input_lower = input_text.lower()

        if "project" in input_lower and "create" in input_lower:
            suggestions.extend([
                "Create a project charter for formal approval",
                "Develop a detailed Work Breakdown Structure (WBS)",
                "Identify and document key stakeholders"
            ])

        elif "charter" in output:
            suggestions.extend([
                "Create a Work Breakdown Structure next",
                "Develop a stakeholder register",
                "Create a risk register"
            ])

        elif "wbs" in output:
            suggestions.extend([
                "Create project schedules based on WBS",
                "Estimate resources for each work package",
                "Develop risk assessment for work packages"
            ])

        # Limit to 3 suggestions
        return suggestions[:3]

    def _detect_intent_with_llm(self, input_text: str) -> Dict[str, Any]:
        """Use LLM to detect user intent and extract parameters."""
        try:
            prompt = f"""Analiza la siguiente petición del usuario para un sistema de gestión de proyectos PMP.

PETICIÓN DEL USUARIO: "{input_text}"

Debes identificar la intención y extraer parámetros relevantes.

INTENCIONES DISPONIBLES:
1. create_project - Crear un nuevo proyecto
2. list_projects - Listar proyectos existentes
3. save_charter - Guardar/crear project charter
4. save_wbs - Guardar/crear Work Breakdown Structure
5. save_risk - Guardar/crear registro de riesgos
6. save_stakeholder - Guardar/crear registro de stakeholders
7. save_communication - Guardar/crear plan de comunicación
8. view_template - Ver una plantilla (charter, wbs, risk, etc.)
9. help - Pedir ayuda o información general
10. other - Cualquier otra cosa

RESPONDE EN FORMATO JSON:
{{
    "intent": "nombre_de_la_intencion",
    "confidence": 0.95,
    "parameters": {{
        "project_id": null,
        "project_name": "nombre extraído si aplica",
        "template_type": "tipo de plantilla si aplica",
        "action_details": "detalles adicionales"
    }},
    "reasoning": "breve explicación de por qué elegiste esta intención"
}}

EJEMPLOS:
- "crear proyecto app móvil" → intent: "create_project", project_name: "app móvil"
- "lista mis proyectos" → intent: "list_projects"
- "necesito el charter para proyecto 5" → intent: "save_charter", project_id: 5
- "documenta los riesgos del proyecto web" → intent: "save_risk", project_name: "web"
- "muéstrame la plantilla de WBS" → intent: "view_template", template_type: "wbs"

Responde solo con el JSON, sin texto adicional."""

            # Call LLM to analyze intent
            response = self.llm.invoke(prompt)

            # Parse JSON response
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)

            # Try to parse JSON, with fallback
            try:
                intent_data = json.loads(response_text)

                # Validate required fields
                if not intent_data.get("intent"):
                    intent_data = {"intent": "other", "confidence": 0.5, "parameters": {}}

                logger.info(f"LLM detected intent: {intent_data.get('intent')} (confidence: {intent_data.get('confidence', 0)})")

                return intent_data

            except json.JSONDecodeError:
                logger.warning(f"Could not parse LLM response as JSON: {response_text}")
                return {"intent": "other", "confidence": 0.3, "parameters": {}}

        except Exception as e:
            logger.error(f"Error detecting intent with LLM: {str(e)}")
            return {"intent": "other", "confidence": 0.1, "parameters": {}}

    def _handle_create_project_request_with_params(self, input_text: str, parameters: Dict) -> str:
        """Handle project creation with LLM-extracted parameters."""
        # Use parameters if available, otherwise fallback to original logic
        project_name = parameters.get("project_name") or self._extract_project_name_from_text(input_text)

        # Delegate to existing method but with extracted name
        if project_name and project_name != "Mi Nuevo Proyecto PMP":
            return self._handle_create_project_request(f"crear proyecto {project_name}")
        else:
            return self._handle_create_project_request(input_text)

    def _extract_project_name_from_text(self, input_text: str) -> str:
        """Extract project name from user input text."""
        # Simple extraction logic - can be improved later
        words = input_text.split()
        # Look for pattern after "proyecto", "project", etc.
        trigger_words = ["proyecto", "project", "app", "aplicación", "sistema", "web", "móvil", "api"]

        for i, word in enumerate(words):
            if word.lower() in trigger_words and i + 1 < len(words):
                # Take next few words as project name
                return " ".join(words[i+1:i+4])  # Max 3 words

        return "Mi Nuevo Proyecto PMP"

    def _handle_save_charter_request_with_params(self, input_text: str, parameters: Dict) -> str:
        """Handle charter saving with LLM-extracted parameters."""
        project_id = parameters.get("project_id")
        project_name = parameters.get("project_name")

        # If we have both parameters, construct the command
        if project_id and project_name:
            return self._handle_save_charter_request(f"guardar charter {project_id} {project_name}")
        elif project_id:
            return self._handle_save_charter_request(f"guardar charter {project_id} Proyecto")
        else:
            return """🤖 **Quieres crear un Project Charter**

Para guardar el charter necesito:
- 🆔 **ID del proyecto**
- 📝 **Nombre del proyecto** (opcional)

**Formato:** `guardar charter <project_id> <nombre>`

💡 **¿No conoces los IDs?** Usa `listar proyectos` para verlos."""

    def _handle_save_wbs_request_with_params(self, input_text: str, parameters: Dict) -> str:
        """Handle WBS saving with LLM-extracted parameters."""
        project_id = parameters.get("project_id")
        project_name = parameters.get("project_name")

        if project_id and project_name:
            return self._handle_save_wbs_request(f"guardar wbs {project_id} {project_name}")
        elif project_id:
            return self._handle_save_wbs_request(f"guardar wbs {project_id} Proyecto")
        else:
            return """🤖 **Quieres crear una Work Breakdown Structure (WBS)**

Para guardar el WBS necesito:
- 🆔 **ID del proyecto**
- 📝 **Nombre del proyecto** (opcional)

**Formato:** `guardar wbs <project_id> <nombre>`

💡 **¿No conoces los IDs?** Usa `listar proyectos` para verlos."""

    def _handle_save_risk_request_with_params(self, input_text: str, parameters: Dict) -> str:
        """Handle risk register saving with LLM-extracted parameters."""
        project_id = parameters.get("project_id")
        project_name = parameters.get("project_name")

        if project_id and project_name:
            return self._handle_save_risk_request(f"guardar risk {project_id} {project_name}")
        elif project_id:
            return self._handle_save_risk_request(f"guardar risk {project_id} Proyecto")
        else:
            return """🤖 **Quieres crear un Registro de Riesgos**

Para guardar el registro de riesgos necesito:
- 🆔 **ID del proyecto**
- 📝 **Nombre del proyecto** (opcional)

**Formato:** `guardar risk <project_id> <nombre>`

💡 **¿No conoces los IDs?** Usa `listar proyectos` para verlos."""

    def _handle_view_template_request(self, parameters: Dict) -> str:
        """Handle template viewing requests."""
        template_type = parameters.get("template_type", "").lower()

        if template_type in ["charter", "acta"]:
            template = self._get_project_charter_template()
            return f"""Aquí tienes la plantilla de Project Charter:\n\n{template}

💾 **Para guardar personalizado:** `guardar charter <project_id> <nombre>`"""

        elif template_type in ["wbs", "breakdown"]:
            template = self._get_wbs_template()
            return f"""Aquí tienes la plantilla de Work Breakdown Structure (WBS):\n\n{template}

💾 **Para guardar personalizado:** `guardar wbs <project_id> <nombre>`"""

        elif template_type in ["risk", "riesgo"]:
            template = self._get_risk_register_template()
            return f"""Aquí tienes la plantilla de Registro de Riesgos:\n\n{template}

💾 **Para guardar personalizado:** `guardar risk <project_id> <nombre>`"""

        else:
            return """📋 **Plantillas disponibles:**

🎯 **Project Charter:** `charter`
📊 **Work Breakdown Structure:** `wbs`
⚠️ **Registro de Riesgos:** `risk`
👥 **Registro de Stakeholders:** `stakeholder`
📢 **Plan de Comunicación:** `communication`

¿Cuál plantilla te interesa ver?"""

    def _get_help_message(self) -> str:
        """Return comprehensive help message."""
        return """🤖 **PMP Project Agent - Asistente Inteligente**

Puedo entender peticiones en lenguaje natural. Algunos ejemplos:

🚀 **Gestión de Proyectos:**
- "Crea un proyecto para mi app móvil"
- "Lista mis proyectos"
- "¿Qué proyectos tengo?"

📋 **Documentación PMP:**
- "Necesito el charter para mi proyecto web"
- "Documenta los riesgos del proyecto 5"
- "Crea el WBS para la aplicación móvil"

📊 **Plantillas:**
- "Muéstrame la plantilla de charter"
- "¿Cómo es un registro de riesgos?"
- "Ver plantilla WBS"

💡 **¡Solo háblame naturalmente!** Entiendo contexto y extraigo la información necesaria."""

    def _handle_unclear_request(self, input_text: str, intent_data: Dict) -> str:
        """Handle requests with unclear or low-confidence intent."""
        reasoning = intent_data.get("reasoning", "No se pudo determinar la intención")

        return f"""🤖 **No estoy seguro de qué necesitas**

Tu petición: "{input_text}"
Mi análisis: {reasoning}

💡 **Intenta con frases como:**
- "Crea un proyecto llamado..."
- "Lista mis proyectos"
- "Necesito el charter para..."
- "Muéstrame la plantilla de..."
- "Ayuda"

¿Puedes ser más específico?"""

    def _handle_save_charter_request(self, input_text: str) -> str:
        """Handle requests to save project charter."""
        try:
            # Parse: guardar charter <project_id> <project_name>
            parts = input_text.split()
            #if len(parts) < 4:
            #    return "❌ Formato incorrecto. Usa: `guardar charter <project_id> <nombre_proyecto>`\nEjemplo: `guardar charter 3 Mi Proyecto Web`"

            project_id = int(parts[2])
            #project_name = " ".join(parts[3:])

            # Verify that the project exists
            existing_project = self.db_manager.get_project(project_id)
            if not existing_project:
                return f"❌ Error: No existe un proyecto con ID {project_id}\n\n💡 **Ver proyectos disponibles:**\n`listar proyectos`"

            project_name=existing_project.name
            # Get the charter template and customize it
            template = self._get_project_charter_template()
            customized_charter = template.replace("[PROJECT NAME]", project_name.upper())
            customized_charter = customized_charter.replace("Project Name: ", f"Project Name: {project_name}")

            # Save to file system first
            file_path = self.file_manager.save_project_document(
                project_id=project_id,
                document_type="project_charter",
                content=customized_charter,
                filename=f"project_charter_{project_name.replace(' ', '_')}.md"
            )

            # Save to database
            self.db_manager.create_project_document(
                project_id=project_id,
                document_type="project_charter",
                file_path=file_path,
                content=customized_charter
            )

            return f"""✅ **Charter guardado exitosamente!**

🎯 **Proyecto:** {existing_project.name} (ID: {project_id})
📁 **Archivo:** {file_path}
📋 **Tipo:** Project Charter personalizado

💡 **Próximos pasos sugeridos:**
- `guardar wbs {project_id} {project_name}` - Crear WBS
- `guardar risk {project_id} {project_name}` - Crear Registro de Riesgos"""

        except ValueError:
            return "❌ Error: El project_id debe ser un número\nEjemplo: `guardar charter 3 Mi Proyecto Web`"
        except Exception as e:
            logger.error(f"Error guardando charter: {str(e)}")
            return f"❌ Error guardando charter: {str(e)}"

    def _handle_save_wbs_request(self, input_text: str) -> str:
        """Handle requests to save WBS."""
        try:
            parts = input_text.split()
            if len(parts) < 4:
                return "❌ Formato incorrecto. Usa: `guardar wbs <project_id> <nombre_proyecto>`"

            project_id = int(parts[2])
            project_name = " ".join(parts[3:])

            # Verify that the project exists
            existing_project = self.db_manager.get_project(project_id)
            if not existing_project:
                return f"❌ Error: No existe un proyecto con ID {project_id}\n\n💡 **Ver proyectos disponibles:**\n`listar proyectos`"

            template = self._get_wbs_template()
            customized_wbs = template.replace("[PROJECT NAME]", project_name.upper())

            # Save to file system first
            file_path = self.file_manager.save_project_document(
                project_id=project_id,
                document_type="wbs",
                content=customized_wbs,
                filename=f"wbs_{project_name.replace(' ', '_')}.md"
            )

            # Save to database
            self.db_manager.create_project_document(
                project_id=project_id,
                document_type="wbs",
                file_path=file_path,
                content=customized_wbs
            )

            return f"""✅ **WBS guardado exitosamente!**

🎯 **Proyecto:** {existing_project.name} (ID: {project_id})
📁 **Archivo:** {file_path}
📊 **WBS personalizado para:** {project_name}"""

        except ValueError:
            return "❌ Error: El project_id debe ser un número"
        except Exception as e:
            logger.error(f"Error guardando WBS: {str(e)}")
            return f"❌ Error guardando WBS: {str(e)}"

    def _handle_save_risk_request(self, input_text: str) -> str:
        """Handle requests to save risk register."""
        try:
            parts = input_text.split()
            if len(parts) < 4:
                return "❌ Formato incorrecto. Usa: `guardar risk <project_id> <nombre_proyecto>`"

            project_id = int(parts[2])
            project_name = " ".join(parts[3:])

            # Verify that the project exists
            existing_project = self.db_manager.get_project(project_id)
            if not existing_project:
                return f"❌ Error: No existe un proyecto con ID {project_id}\n\n💡 **Ver proyectos disponibles:**\n`listar proyectos`"

            template = self._get_risk_register_template()

            # Save to file system first
            file_path = self.file_manager.save_project_document(
                project_id=project_id,
                document_type="risk_register",
                content=template,
                filename=f"risk_register_{project_name.replace(' ', '_')}.md"
            )

            # Save to database
            self.db_manager.create_project_document(
                project_id=project_id,
                document_type="risk_register",
                file_path=file_path,
                content=template
            )

            return f"""✅ **Registro de Riesgos guardado exitosamente!**

🎯 **Proyecto:** {existing_project.name} (ID: {project_id})
📁 **Archivo:** {file_path}
⚠️ **Registro de Riesgos para:** {project_name}"""

        except ValueError:
            return "❌ Error: El project_id debe ser un número"
        except Exception as e:
            logger.error(f"Error guardando registro de riesgos: {str(e)}")
            return f"❌ Error guardando registro de riesgos: {str(e)}"

    def _handle_list_projects_request(self, input_text: str) -> str:
        """Handle requests to list projects."""
        try:
            # Get projects from database
            projects = self.db_manager.list_projects(limit=20)

            if not projects:
                return "📝 No hay proyectos creados aún.\n\n💡 **Crea tu primer proyecto:**\n`crear proyecto Mi Primer Proyecto`"

            # Format projects in a nice table-like structure
            response = "📋 **LISTA DE PROYECTOS:**\n\n"

            for i, project in enumerate(projects, 1):
                # Now we should be able to access project attributes safely
                project_id = project.id
                project_name = project.name
                project_status = project.status.value if hasattr(project.status, 'value') else str(project.status)
                project_methodology = project.methodology
                created_at = project.created_at

                # Format creation date
                if hasattr(created_at, 'strftime'):
                    date_str = created_at.strftime("%Y-%m-%d")
                else:
                    date_str = str(created_at)

                response += f"**{i}. {project_name}**\n"
                response += f"   🆔 ID: {project_id}\n"
                response += f"   📊 Estado: {project_status}\n"
                response += f"   🔧 Metodología: {project_methodology}\n"
                response += f"   📅 Creado: {date_str}\n\n"

            response += "💡 **Comandos útiles:**\n"
            response += "- `guardar charter <id> <nombre>` - Crear charter para un proyecto\n"
            response += "- `guardar wbs <id> <nombre>` - Crear WBS para un proyecto\n"
            response += "- `crear proyecto <nombre>` - Crear nuevo proyecto"

            return response

        except Exception as e:
            logger.error(f"Error listing projects: {str(e)}")
            return f"❌ Error al listar proyectos: {str(e)}\n\nIntenta nuevamente con: `listar proyectos`"