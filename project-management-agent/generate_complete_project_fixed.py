#!/usr/bin/env python3
"""
Generador Completo del Project Management Agent
Crea toda la estructura de archivos y código necesario
"""

import os
import json
from pathlib import Path
from typing import Dict, List

def create_file(filepath: str, content: str):
    """Crear archivo con contenido"""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    print(f"✅ {filepath}")

def generate_init_files():
    """Generar archivos __init__.py"""
    packages = [
        'config', 'core', 'rag_system', 'methodology', 'templates',
        'document_management', 'knowledge_base', 'integrations', 
        'ui', 'utils', 'tests', 'scripts'
    ]
    
    for package in packages:
        create_file(f"{package}/__init__.py", '"""Package initialization."""\n')

def generate_config_files():
    """Generar archivos de configuración"""
    
    # config/settings.py
    settings_content = '''import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig(BaseModel):
    """Configuración de base de datos"""
    type: str = "sqlite"
    url: str = "sqlite:///project_agent.db"
    vector_store_path: str = "./data/vector_store"

class ClaudeConfig(BaseModel):
    """Configuración de Claude API"""
    api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 4000
    temperature: float = 0.1

class RAGConfig(BaseModel):
    """Configuración del sistema RAG"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "all-MiniLM-L6-v2"
    similarity_threshold: float = 0.7
    max_results: int = 5

class Settings(BaseModel):
    """Configuración principal del sistema"""
    app_name: str = "Project Management Agent"
    version: str = "1.0.0"
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "False").lower() == "true")
    
    database: DatabaseConfig = DatabaseConfig()
    claude: ClaudeConfig = ClaudeConfig()
    rag: RAGConfig = RAGConfig()
    
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = Field(default_factory=lambda: Path("./data"))
    logs_dir: Path = Field(default_factory=lambda: Path("./logs"))
    
    def __init__(self, **data):
        super().__init__(**data)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Crear directorios necesarios si no existen"""
        directories = [
            self.data_dir,
            self.logs_dir,
            Path(self.database.vector_store_path).parent,
            Path("./projects"),
            Path("./knowledge_base")
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

settings = Settings()
'''
    create_file("config/settings.py", settings_content)

def generate_utils_files():
    """Generar archivos de utilidades"""
    
    # utils/logging_config.py
    logging_content = '''import sys
from pathlib import Path
from loguru import logger
from config.settings import settings

def setup_logging():
    """Configurar sistema de logging con loguru"""
    logger.remove()
    
    log_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} | {message}"
    
    # Console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level="INFO",
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # File handler
    log_file = settings.logs_dir / "agent.log"
    logger.add(
        str(log_file),
        format=log_format,
        level="DEBUG",
        rotation="10 MB",
        retention="1 month",
        compression="zip",
        backtrace=True,
        diagnose=True
    )
    
    logger.info("Logging system initialized")
'''
    create_file("utils/logging_config.py", logging_content)
    
    # utils/validators.py
    validators_content = '''from typing import Dict, List, Any, Optional
import re
from datetime import datetime

class ProjectValidator:
    """Validador para datos de proyecto"""
    
    @staticmethod
    def validate_project_name(name: str) -> bool:
        """Validar nombre de proyecto"""
        if not name or len(name.strip()) < 3:
            return False
        
        pattern = r'^[a-zA-Z0-9\\s\\-_\\.]+$'
        return bool(re.match(pattern, name.strip()))
    
    @staticmethod
    def validate_methodology(methodology: str) -> bool:
        """Validar metodología"""
        valid_methodologies = ['PMI', 'SAFe', 'Hybrid', 'Agile', 'Waterfall']
        return methodology in valid_methodologies
    
    @staticmethod
    def validate_project_data(project_data: Dict) -> Dict[str, List[str]]:
        """Validar datos completos de proyecto"""
        errors = {}
        
        required_fields = ['name', 'methodology', 'type', 'description']
        for field in required_fields:
            if field not in project_data or not project_data[field]:
                if 'required' not in errors:
                    errors['required'] = []
                errors['required'].append(f"Campo requerido: {field}")
        
        return errors
'''
    create_file("utils/validators.py", validators_content)

def generate_core_files():
    """Generar archivos core del sistema"""
    
    # core/claude_client.py
    claude_content = '''import asyncio
import json
from typing import List, Dict, Optional, AsyncGenerator
from anthropic import Anthropic, AsyncAnthropic
from loguru import logger
from config.settings import settings

class ClaudeClient:
    """Cliente para interactuar con la API de Claude"""
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.claude.api_key)
        self.async_client = AsyncAnthropic(api_key=settings.claude.api_key)
        self.conversation_history: List[Dict] = []
        
    def add_to_history(self, role: str, content: str):
        """Agregar mensaje al historial de conversación"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def chat(self, message: str, system_prompt: str = "", context: Optional[Dict] = None) -> str:
        """Enviar mensaje a Claude y recibir respuesta"""
        try:
            messages = self.conversation_history.copy()
            messages.append({"role": "user", "content": message})
            
            response = self.client.messages.create(
                model=settings.claude.model,
                max_tokens=settings.claude.max_tokens,
                temperature=settings.claude.temperature,
                system=system_prompt,
                messages=messages
            )
            
            response_text = response.content[0].text
            
            self.add_to_history("user", message)
            self.add_to_history("assistant", response_text)
            
            logger.info("Claude response generated")
            return response_text
            
        except Exception as e:
            logger.error(f"Error communicating with Claude: {e}")
            raise
    
    def clear_history(self):
        """Limpiar historial de conversación"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
'''
    create_file("core/claude_client.py", claude_content)
    
    # core/agent.py
    agent_content = '''import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger

from core.claude_client import ClaudeClient
from config.settings import settings

class ProjectManagementAgent:
    """Agente principal para gestión de proyectos con PMI y SAFe"""
    
    def __init__(self):
        self.claude_client = ClaudeClient()
        self.current_project: Optional[Dict] = None
        self.pending_approvals: List[Dict] = []
        
        logger.info("Project Management Agent initialized successfully")
    
    def create_new_project(self, project_info: Dict) -> Dict:
        """Crear nuevo proyecto"""
        try:
            required_fields = ['name', 'methodology', 'type', 'description']
            for field in required_fields:
                if field not in project_info:
                    raise ValueError(f"Missing required field: {field}")
            
            project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            project = {
                'id': project_id,
                'name': project_info['name'],
                'methodology': project_info['methodology'],
                'type': project_info['type'],
                'description': project_info['description'],
                'created_at': datetime.now().isoformat(),
                'status': 'initiated',
                'phase': 'initiation',
                'documents': {},
                'approvals': {},
                'version_history': []
            }
            
            project_path = Path("./projects") / project_id
            project_path.mkdir(parents=True, exist_ok=True)
            
            project_file = project_path / "project.json"
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project, f, indent=2, ensure_ascii=False)
            
            self.current_project = project
            
            logger.info(f"New project created: {project_id}")
            
            return {
                'success': True,
                'project_id': project_id,
                'project': project
            }
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_work_plan(self) -> str:
        """Generar plan de trabajo básico"""
        if not self.current_project:
            return "No hay proyecto activo. Primero crea o carga un proyecto."
        
        project = self.current_project
        methodology = project['methodology']
        
        prompt = f"""
        Genera un plan de trabajo detallado para el siguiente proyecto:
        
        Nombre: {project['name']}
        Metodología: {methodology}
        Tipo: {project['type']}
        Descripción: {project['description']}
        
        El plan debe incluir:
        1. Resumen ejecutivo
        2. Fases del proyecto según {methodology}
        3. Actividades principales por fase
        4. Cronograma estimado
        5. Recursos necesarios
        6. Entregables clave
        7. Próximos pasos
        
        Formatea en Markdown.
        """
        
        return self.claude_client.chat(prompt, "Eres un experto en gestión de proyectos especializado en PMI y SAFe.")
    
    def chat_with_context(self, message: str) -> str:
        """Chat con contexto del proyecto actual"""
        context_prompt = ""
        if self.current_project:
            context_prompt = f"Contexto del proyecto actual: {json.dumps(self.current_project, indent=2)}"
        
        system_prompt = f"""
        Eres un asistente experto en gestión de proyectos con conocimiento profundo en PMI y SAFe.
        {context_prompt}
        
        Responde de manera útil y práctica.
        """
        
        return self.claude_client.chat(message, system_prompt)
    
    def list_projects(self) -> List[Dict]:
        """Listar todos los proyectos"""
        try:
            projects_path = Path("./projects")
            projects = []
            
            if projects_path.exists():
                for project_dir in projects_path.iterdir():
                    if project_dir.is_dir():
                        project_file = project_dir / "project.json"
                        if project_file.exists():
                            with open(project_file, 'r', encoding='utf-8') as f:
                                project = json.load(f)
                                projects.append({
                                    'id': project['id'],
                                    'name': project['name'],
                                    'methodology': project['methodology'],
                                    'status': project['status'],
                                    'created_at': project['created_at']
                                })
            
            return projects
            
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return []
    
    def load_project(self, project_id: str) -> Dict:
        """Cargar proyecto existente"""
        try:
            project_path = Path("./projects") / project_id / "project.json"
            
            if not project_path.exists():
                return {'success': False, 'error': 'Proyecto no encontrado'}
            
            with open(project_path, 'r', encoding='utf-8') as f:
                project = json.load(f)
            
            self.current_project = project
            logger.info(f"Project loaded: {project_id}")
            
            return {'success': True, 'project': project}
            
        except Exception as e:
            logger.error(f"Error loading project: {e}")
            return {'success': False, 'error': str(e)}
'''
    create_file("core/agent.py", agent_content)

def generate_methodology_files():
    """Generar archivos de metodologías"""
    
    # methodology/pmi_framework.py
    pmi_content = '''from typing import Dict, List
from datetime import datetime

class PMIFramework:
    """Framework PMI para gestión de proyectos"""
    
    def __init__(self):
        self.process_groups = [
            "Initiating", "Planning", "Executing", 
            "Monitoring & Controlling", "Closing"
        ]
        
        self.knowledge_areas = [
            "Integration", "Scope", "Schedule", "Cost", "Quality",
            "Resource", "Communications", "Risk", "Procurement", "Stakeholder"
        ]
    
    def get_next_steps(self, current_phase: str) -> List[str]:
        """Obtener próximos pasos según la fase actual"""
        phase_steps = {
            "initiation": [
                "Desarrollar Project Charter",
                "Identificar stakeholders clave",
                "Realizar análisis inicial de riesgos",
                "Definir criterios de éxito"
            ],
            "planning": [
                "Desarrollar Project Management Plan",
                "Crear Work Breakdown Structure (WBS)",
                "Estimar duración y costos",
                "Identificar y analizar riesgos"
            ]
        }
        
        return phase_steps.get(current_phase.lower(), [])
    
    def get_guidance(self) -> Dict:
        """Obtener guía del framework PMI"""
        return {
            "principles": [
                "Stewardship", "Team", "Stakeholders", "Value",
                "Systems Thinking", "Leadership", "Tailoring", "Quality"
            ],
            "performance_domains": [
                "Stakeholders", "Team", "Development Approach",
                "Planning", "Project Work", "Delivery", "Measurement", "Uncertainty"
            ]
        }
'''
    create_file("methodology/pmi_framework.py", pmi_content)
    
    # methodology/safe_framework.py
    safe_content = '''from typing import Dict, List
from datetime import datetime

class SAFeFramework:
    """Framework SAFe para desarrollo ágil escalado"""
    
    def __init__(self):
        self.configurations = [
            "Essential SAFe", "Large Solution SAFe", 
            "Portfolio SAFe", "Full SAFe"
        ]
        
        self.core_values = [
            "Alignment", "Built-in Quality", 
            "Transparency", "Program Execution"
        ]
        
        self.lean_agile_principles = [
            "Take an economic view",
            "Apply systems thinking", 
            "Assume variability; preserve options",
            "Build incrementally with fast, integrated learning cycles"
        ]
    
    def get_next_steps(self, current_phase: str) -> List[str]:
        """Obtener próximos pasos según la fase actual SAFe"""
        phase_steps = {
            "assessment": [
                "Realizar SAFe assessment organizacional",
                "Identificar value streams",
                "Definir ARTs (Agile Release Trains)",
                "Seleccionar configuración SAFe apropiada"
            ],
            "preparation": [
                "Entrenar líderes en SAFe",
                "Establecer Lean-Agile Center of Excellence",
                "Identificar Product Owners y Scrum Masters",
                "Definir Definition of Done común"
            ]
        }
        
        return phase_steps.get(current_phase.lower(), [])
    
    def get_guidance(self) -> Dict:
        """Obtener guía del framework SAFe"""
        return {
            "implementation_roadmap": [
                "Reaching the Tipping Point",
                "Train Lean-Agile Change Agents", 
                "Train Executives, Managers, and Leaders",
                "Create a Lean-Agile Center of Excellence"
            ],
            "success_patterns": [
                "Executive leadership and sponsorship",
                "Training and education first",
                "Start with Essential SAFe",
                "Focus on value streams"
            ]
        }
'''
    create_file("methodology/safe_framework.py", safe_content)

def generate_knowledge_base():
    """Generar archivos de knowledge base"""
    
    # knowledge_base/safe_documentation/core_values.json
    safe_values = {
        "alignment": {
            "definition": "Everyone understands how their work supports business objectives",
            "description": "Alignment keeps teams working toward common goals and priorities",
            "practices": [
                "Clear vision and strategy communication",
                "Regular PI Planning events",
                "Transparent decision-making processes"
            ]
        },
        "built_in_quality": {
            "definition": "Quality is built into every increment of work",
            "description": "Quality practices are embedded throughout development",
            "practices": [
                "Test-driven development",
                "Continuous integration",
                "Definition of Done",
                "Automated testing"
            ]
        }
    }
    create_file("knowledge_base/safe_documentation/core_values.json", json.dumps(safe_values, indent=2))
    
    # knowledge_base/pmi_documentation/process_groups.json
    pmi_processes = {
        "initiating": {
            "definition": "Processes to define a new project or phase",
            "key_processes": [
                "Develop Project Charter",
                "Identify Stakeholders"
            ],
            "outputs": [
                "Project Charter",
                "Stakeholder Register"
            ]
        },
        "planning": {
            "definition": "Processes to establish scope and define actions",
            "key_processes": [
                "Develop Project Management Plan",
                "Plan Scope Management",
                "Create WBS",
                "Plan Schedule Management"
            ],
            "outputs": [
                "Project Management Plan",
                "Work Breakdown Structure",
                "Schedule Baseline"
            ]
        }
    }
    create_file("knowledge_base/pmi_documentation/process_groups.json", json.dumps(pmi_processes, indent=2))

def generate_templates():
    """Generar plantillas de documentos"""
    
    # templates/template_engine.py
    template_engine_content = '''import os
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, Template
from loguru import logger

class TemplateEngine:
    """Motor de plantillas para documentos de proyecto"""
    
    def __init__(self):
        self.templates_path = Path("./templates")
        self.templates_path.mkdir(parents=True, exist_ok=True)
        
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        self.env.globals.update({
            'now': datetime.now,
            'format_date': self._format_date,
        })
        
        logger.info("Template engine initialized")
    
    def _format_date(self, date_obj, format_str: str = "%Y-%m-%d") -> str:
        """Formatear fecha"""
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            except ValueError:
                return date_obj
        return date_obj.strftime(format_str)
    
    def generate_document(self, document_type: str, context: dict) -> str:
        """Generar documento usando plantilla"""
        try:
            methodology = context.get('methodology', 'PMI')
            template_name = f"{methodology.lower()}_templates/{document_type}.md"
            
            try:
                template = self.env.get_template(template_name)
            except Exception:
                template = self.env.get_template(f"common_templates/{document_type}.md")
            
            content = template.render(**context)
            logger.info(f"Document generated: {document_type}")
            return content
            
        except Exception as e:
            logger.error(f"Error generating document {document_type}: {e}")
            return self._generate_fallback_document(document_type, context)
    
    def _generate_fallback_document(self, document_type: str, context: dict) -> str:
        """Generar documento básico si no hay plantilla"""
        project = context.get('project', {})
        
        return f"""# {document_type.replace('_', ' ').title()}
**Proyecto:** {project.get('name', 'TBD')}
**Fecha:** {datetime.now().strftime('%Y-%m-%d')}
**Metodología:** {project.get('methodology', 'TBD')}

## Descripción
Este documento será completado según los requerimientos específicos del proyecto.

## Secciones Principales
- Objetivos
- Alcance
- Entregables
- Cronograma
- Recursos
- Riesgos

---
*Documento generado automáticamente.*
"""
'''
    create_file("templates/template_engine.py", template_engine_content)
    
    # templates/pmi_templates/project_charter.md
    charter_template = '''# Project Charter
**Proyecto:** {{ project.name }}
**Fecha:** {{ format_date(now()) }}
**Project Manager:** {{ project.manager | default('TBD') }}

## 1. Propósito del Proyecto
{{ project.description }}

## 2. Objetivos del Proyecto
{% for objective in project.objectives | default(['TBD']) %}
- {{ objective }}
{% endfor %}

## 3. Alcance del Proyecto
### Incluye:
{% for item in project.scope.includes | default(['TBD']) %}
- {{ item }}
{% endfor %}

### No Incluye:
{% for item in project.scope.excludes | default(['TBD']) %}
- {{ item }}
{% endfor %}

## 4. Entregables Principales
{% for deliverable in project.deliverables | default(['TBD']) %}
- {{ deliverable }}
{% endfor %}

## 5. Cronograma de Alto Nivel
- **Inicio:** {{ format_date(project.start_date | default(now())) }}
- **Fin:** {{ format_date(project.end_date | default('TBD')) }}

## 6. Presupuesto Estimado
{{ project.budget | default('TBD') }}

## 7. Riesgos de Alto Nivel
{% for risk in project.high_level_risks | default(['TBD']) %}
- {{ risk }}
{% endfor %}

## 8. Stakeholders Principales
{% for stakeholder in project.stakeholders | default([]) %}
- **{{ stakeholder.name }}:** {{ stakeholder.role }}
{% endfor %}

## 9. Criterios de Éxito
{% for criteria in project.success_criteria | default(['TBD']) %}
- {{ criteria }}
{% endfor %}

## 10. Autorización
**Sponsor:** {{ project.sponsor | default('TBD') }}
**Fecha de Aprobación:** _______________
**Firma:** _______________
'''
    create_file("templates/pmi_templates/project_charter.md", charter_template)
    
    # templates/safe_templates/pi_planning.md
    pi_template = '''# PI Planning
**ART:** {{ project.art_name | default('ART Name') }}
**PI:** {{ pi_number | default('X') }}
**Fechas:** {{ format_date(pi_start_date) }} - {{ format_date(pi_end_date) }}

## Objetivos del PI
{% for objective in pi_objectives | default([]) %}
### {{ loop.index }}. {{ objective.title }}
- **Descripción:** {{ objective.description }}
- **Valor de Negocio:** {{ objective.business_value }}
- **Equipos Involucrados:** {{ objective.teams | join(', ') }}
{% endfor %}

## Features Planificadas
| Feature | Epic | Equipo | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 | Sprint 5 |
|---------|------|--------|----------|----------|----------|----------|----------|
{% for feature in features | default([]) %}
| {{ feature.name }} | {{ feature.epic }} | {{ feature.team }} | {{ feature.sprint1 }} | {{ feature.sprint2 }} | {{ feature.sprint3 }} | {{ feature.sprint4 }} | {{ feature.sprint5 }} |
{% endfor %}

## Dependencies
{% for dependency in dependencies | default([]) %}
- **{{ dependency.from_team }}** → **{{ dependency.to_team }}**: {{ dependency.description }}
{% endfor %}

## Risks and Issues
{% for risk in risks | default([]) %}
### {{ risk.title }}
- **Probabilidad:** {{ risk.probability }}
- **Impacto:** {{ risk.impact }}
- **Mitigación:** {{ risk.mitigation }}
- **Owner:** {{ risk.owner }}
{% endfor %}
'''
    create_file("templates/safe_templates/pi_planning.md", pi_template)

def generate_main_file():
    """Generar archivo main.py principal"""
    
    main_content = '''#!/usr/bin/env python3
"""
Project Management Agent - Main Application
Agente avanzado para gestión de proyectos con PMI y SAFe
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
from utils.logging_config import setup_logging
setup_logging()

# Importar componentes principales
from core.agent import ProjectManagementAgent
from config.settings import settings

# Configurar CLI
app = typer.Typer(
    name="pm-agent",
    help="🚀 Agente Avanzado de Gestión de Proyectos con PMI y SAFe",
    rich_markup_mode="rich"
)

console = Console()
agent = ProjectManagementAgent()

def display_header():
    """Mostrar header de la aplicación"""
    header = """
    ╔══════════════════════════════════════════════════════════════╗
    ║            🚀 PROJECT MANAGEMENT AGENT 🚀                    ║
    ║                                                              ║
    ║    Agente Avanzado para Gestión de Proyectos                 ║
    ║    • PMI Framework Support                                   ║
    ║    • SAFe Framework Support                                  ║
    ║    • AI-Powered Documentation                                ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(header, style="bold blue")

@app.command()
def start():
    """🎯 Iniciar sesión interactiva del agente"""
    display_header()
    
    # Verificar configuración
    if not settings.claude.api_key or settings.claude.api_key == "tu_clave_anthropic_aqui":
        console.print("❌ [red]ANTHROPIC_API_KEY no configurada[/red]")
        console.print("Edita el archivo .env con tu clave API")
        return
    
    console.print("¡Bienvenido al Agente de Gestión de Proyectos!", style="bold green")
    console.print("Escribe 'help' para ver comandos disponibles o 'quit' para salir.\\n")
    
    while True:
        try:
            user_input = Prompt.ask("[bold cyan]PM-Agent[/bold cyan]")
            
            if user_input.lower() in ['quit', 'exit', 'salir']:
                console.print("¡Hasta luego! 👋", style="bold yellow")
                break
            elif user_input.lower() == 'help':
                show_help()
            elif user_input.lower().startswith('crear proyecto'):
                interactive_create_project()
            elif user_input.lower() == 'proyectos':
                list_projects()
            elif user_input.lower().startswith('generar plan'):
                interactive_generate_plan()
            else:
                # Chat contextual
                response = agent.chat_with_context(user_input)
                console.print("\\n[bold green]Respuesta:[/bold green]")
                console.print(Markdown(response))
                console.print()
                
        except KeyboardInterrupt:
            console.print("\\n¡Hasta luego! 👋", style="bold yellow")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

def show_help():
    """Mostrar ayuda"""
    help_text = """
## 📖 Comandos Disponibles

### Gestión de Proyectos
- `crear proyecto` - Crear nuevo proyecto
- `proyectos` - Listar todos los proyectos
- `generar plan` - Generar plan de trabajo

### Conversación
- `help` - Mostrar esta ayuda
- `quit/exit/salir` - Salir del agente

### Chat Contextual
Puedes hacer cualquier pregunta sobre metodologías o procesos.

**Ejemplos:**
- "¿Qué es un Project Charter en PMI?"
- "Explícame PI Planning en SAFe"
- "¿Cómo gestiono riesgos?"
    """
    console.print(Markdown(help_text))

def interactive_create_project():
    """Crear proyecto interactivamente"""
    console.print("\\n[bold blue]🚀 Crear Nuevo Proyecto[/bold blue]")
    
    project_name = Prompt.ask("Nombre del proyecto")
    project_description = Prompt.ask("Descripción del proyecto")
    
    methodologies = ["PMI", "SAFe", "Hybrid"]
    console.print("\\nSelecciona la metodología:")
    for i, method in enumerate(methodologies, 1):
        console.print(f"  {i}. {method}")
    
    method_choice = Prompt.ask("Opción", choices=["1", "2", "3"], default="1")
    methodology = methodologies[int(method_choice) - 1]
    
    project_types = ["Software Development", "Infrastructure", "Business Process", "Other"]
    console.print("\\nTipo de proyecto:")
    for i, ptype in enumerate(project_types, 1):
        console.print(f"  {i}. {ptype}")
    
    type_choice = Prompt.ask("Opción", choices=["1", "2", "3", "4"], default="1")
    project_type = project_types[int(type_choice) - 1]
    
    project_info = {
        'name': project_name,
        'description': project_description,
        'methodology': methodology,
        'type': project_type
    }
    
    result = agent.create_new_project(project_info)
    
    if result['success']:
        console.print(f"\\n✅ [green]Proyecto creado exitosamente: {result['project_id']}[/green]")
    else:
        console.print(f"[red]❌ Error creando proyecto: {result.get('error')}[/red]")

def interactive_generate_plan():
    """Generar plan de trabajo"""
    if not agent.current_project:
        console.print("[yellow]⚠️  No hay proyecto activo. Crea un proyecto primero.[/yellow]")
        return
    
    console.print(f"\\n[bold blue]📋 Generando Plan para: {agent.current_project['name']}[/bold blue]")
    
    plan = agent.generate_work_plan()
    console.print("\\n[bold green]📋 Plan de Trabajo:[/bold green]")
    console.print(Markdown(plan))

def list_projects():
    """Listar proyectos"""
    projects = agent.list_projects()
    
    if not projects:
        console.print("[yellow]No hay proyectos disponibles[/yellow]")
        return
    
    table = Table(title="📂 Proyectos")
    table.add_column("ID", style="cyan")
    table.add_column("Nombre", style="green")
    table.add_column("Metodología", style="blue")
    table.add_column("Estado", style="yellow")
    table.add_column("Creado", style="dim")
    
    for project in projects:
        table.add_row(
            project['id'],
            project['name'],
            project['methodology'],
            project['status'],
            project['created_at'][:10]
        )
    
    console.print(table)

@app.command()
def setup():
    """⚙️ Configuración inicial"""
    display_header()
    console.print("🔧 Configuración inicial del agente", style="bold blue")
    
    # Crear directorios
    directories = ["./projects", "./data", "./logs", "./backups"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        console.print(f"✅ Directorio: {directory}")
    
    # Verificar .env
    if not Path(".env").exists():
        env_content = """# Configuración del Agente
ANTHROPIC_API_KEY=tu_clave_anthropic_aqui
DEBUG=False
LOG_LEVEL=INFO
"""
        Path(".env").write_text(env_content)
        console.print("✅ Archivo .env creado")
        console.print("⚠️  [yellow]Edita .env con tu ANTHROPIC_API_KEY[/yellow]")
    
    console.print("\\n🎉 [green]Configuración completada![/green]")

@app.command()
def test():
    """🧪 Probar instalación"""
    console.print("Probando componentes...", style="bold yellow")
    
    tests = [
        ("anthropic", "anthropic"),
        ("rich", "rich"), 
        ("typer", "typer"),
        ("jinja2", "jinja2"),
        ("pydantic", "pydantic")
    ]
    
    for name, module in tests:
        try:
            __import__(module)
            console.print(f"✅ {name}", style="green")
        except ImportError:
            console.print(f"❌ {name}", style="red")
    
    # Verificar API key
    if settings.claude.api_key and settings.claude.api_key != "tu_clave_anthropic_aqui":
        console.print("✅ API Key configurada", style="green")
    else:
        console.print("❌ API Key no configurada", style="red")

@app.command()
def version():
    """ℹ️ Ver versión"""
    console.print(f"[bold blue]{settings.app_name}[/bold blue]")
    console.print(f"Versión: {settings.version}")

if __name__ == "__main__":
    app()
'''
    create_file("main.py", main_content)

def generate_requirements():
    """Generar archivos requirements"""
    
    requirements_content = '''# Project Management Agent - Dependencies

# Core AI
anthropic>=0.18.0,<1.0

# CLI and UI
rich>=13.7.0,<14.0
typer>=0.9.0,<1.0

# Templates and Configuration
jinja2>=3.1.0,<4.0
pydantic>=2.5.0,<3.0
python-dotenv>=1.0.0,<2.0
pyyaml>=6.0,<7.0

# Logging
loguru>=0.7.0,<1.0

# Utilities
requests>=2.31.0,<3.0
tqdm>=4.65.0,<5.0

# Database
sqlalchemy>=2.0.0,<3.0

# Optional: RAG System (install if needed)
# chromadb>=0.4.20,<0.5
# sentence-transformers>=2.2.0,<3.0

# Optional: Web Interface (install if needed)  
# streamlit>=1.30.0,<2.0
# fastapi>=0.100.0,<1.0

# Optional: Document Processing (install if needed)
# python-docx>=1.1.0,<2.0
# openpyxl>=3.1.0,<4.0
# pymupdf>=1.23.0,<2.0
'''
    create_file("requirements.txt", requirements_content)
    
    minimal_requirements = '''# Minimal dependencies for basic functionality
anthropic>=0.18.0,<1.0
rich>=13.7.0,<14.0
typer>=0.9.0,<1.0
jinja2>=3.1.0,<4.0
pydantic>=2.5.0,<3.0
python-dotenv>=1.0.0,<2.0
loguru>=0.7.0,<1.0
'''
    create_file("requirements-minimal.txt", minimal_requirements)

def generate_env_and_config():
    """Generar archivos de configuración"""
    
    env_content = '''# Configuración del Agente de Gestión de Proyectos

# API Keys (REQUERIDO)
ANTHROPIC_API_KEY=tu_clave_anthropic_aqui

# Configuración General
DEBUG=False
LOG_LEVEL=INFO

# Rutas
PROJECTS_PATH=./projects
VECTOR_STORE_PATH=./data/vector_store
LOG_FILE=./logs/agent.log

# Configuración Claude
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4000
CLAUDE_TEMPERATURE=0.1

# Configuración RAG (Opcional)
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=1000
SIMILARITY_THRESHOLD=0.7

# Integraciones (Opcional)
JIRA_URL=
JIRA_USERNAME=
JIRA_API_TOKEN=
CONFLUENCE_URL=
GITHUB_TOKEN=
'''
    create_file(".env.example", env_content)
    
    gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Project specific
.env
data/
logs/
projects/
backups/
*.log

# OS
.DS_Store
Thumbs.db

# Conda
environment_backup.yml
'''
    create_file(".gitignore", gitignore_content)

def generate_readme():
    """Generar README.md"""
    
    readme_content = '''# 🚀 Project Management Agent

Agente avanzado de gestión de proyectos con soporte completo para metodologías PMI y SAFe, potenciado por Claude AI.

## ✨ Características

- ✅ **Planes de trabajo** basados en PMI y SAFe
- ✅ **Documentación automática** con plantillas
- ✅ **Chat contextual** con Claude AI
- ✅ **Interfaz CLI elegante** con Rich
- ✅ **Sistema de proyectos** persistente

## 🚀 Instalación Rápida

### Requisitos
- Python 3.9+
- Clave API de Anthropic (Claude)

### Pasos
```bash
# 1. Clonar/descargar código
# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\\Scripts\\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API key
cp .env.example .env
# Editar .env con tu ANTHROPIC_API_KEY

# 5. Configuración inicial
python main.py setup

# 6. ¡Usar el agente!
python main.py start
```

## 🎮 Uso

### Modo Interactivo
```bash
python main.py start
```

### Comandos CLI
```bash
python main.py setup     # Configuración inicial
python main.py test      # Probar instalación
python main.py --help    # Ver ayuda
```

## 📖 Comandos Disponibles

- `crear proyecto` - Crear nuevo proyecto
- `proyectos` - Listar proyectos
- `generar plan` - Crear plan de trabajo
- `help` - Mostrar ayuda
- `quit` - Salir

## 🔑 Obtener API Key

1. Ve a https://console.anthropic.com/
2. Crea cuenta y agrega tarjeta
3. Crear API Key
4. Copiar clave completa
5. Agregar a .env: `ANTHROPIC_API_KEY=tu_clave_aqui`

## 💰 Costos

- **Créditos iniciales**: $5 USD gratuitos
- **Uso típico**: $0.01-0.05 por consulta
- **Uso diario**: $0.25-1.00 USD

## 🎯 Ejemplos de Uso

```
PM-Agent> crear proyecto
# Guía interactiva para crear proyecto

PM-Agent> ¿Qué es un Project Charter en PMI?
# Explicación detallada con contexto

PM-Agent> generar plan
# Plan de trabajo completo basado en metodología
```

## 🛠️ Estructura del Proyecto

- `core/` - Motor del agente y Claude client
- `methodology/` - Frameworks PMI y SAFe  
- `templates/` - Plantillas de documentos
- `knowledge_base/` - Base de conocimiento
- `utils/` - Utilidades y helpers

## 🐛 Troubleshooting

### Error: API key not found
```bash
# Verificar .env
cat .env | grep ANTHROPIC_API_KEY
```

### Error: Import modules
```bash
# Instalar dependencias faltantes
pip install -r requirements.txt
```

## 📝 Licencia

MIT License - ver LICENSE para detalles.

## 🤝 Contribuir

1. Fork del repositorio
2. Crear branch: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -am 'Agregar funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

---

**⭐ Si te ayuda, considera darle una estrella!**
'''
    create_file("README.md", readme_content)

def generate_additional_files():
    """Generar archivos adicionales"""
    
    # scripts/quick_start.py
    quick_start_content = '''#!/usr/bin/env python3
"""
Script de inicio rápido para Project Management Agent
"""

import subprocess
import sys
from pathlib import Path

def run_command(command):
    """Ejecutar comando y mostrar resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            return True
        else:
            print(f"❌ {command}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando {command}: {e}")
        return False

def main():
    print("🚀 Project Management Agent - Quick Start")
    print("=" * 50)
    
    # Verificar Python
    print(f"Python version: {sys.version}")
    
    # Instalar dependencias
    print("\\n📦 Instalando dependencias...")
    if run_command("pip install -r requirements-minimal.txt"):
        print("✅ Dependencias instaladas")
    else:
        print("❌ Error instalando dependencias")
        return
    
    # Verificar .env
    if not Path(".env").exists():
        print("\\n📝 Creando archivo .env...")
        if Path(".env.example").exists():
            run_command("cp .env.example .env")
        else:
            with open(".env", "w") as f:
                f.write("ANTHROPIC_API_KEY=tu_clave_anthropic_aqui\\n")
        
        print("⚠️  Edita .env con tu ANTHROPIC_API_KEY")
    
    # Configurar agente
    print("\\n⚙️ Configurando agente...")
    run_command("python main.py setup")
    
    # Probar instalación
    print("\\n🧪 Probando instalación...")
    run_command("python main.py test")
    
    print("\\n🎉 ¡Listo para usar!")
    print("Ejecuta: python main.py start")

if __name__ == "__main__":
    main()
'''
    create_file("scripts/quick_start.py", quick_start_content)
    
    # LICENSE
    license_content = '''MIT License

Copyright (c) 2024 Project Management Agent

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
    create_file("LICENSE", license_content)

def main():
    """Función principal para generar todo el proyecto"""
    print("🚀 Generando Project Management Agent Completo")
    print("=" * 60)
    
    print("📁 Creando estructura de directorios...")
    generate_init_files()
    print()
    
    print("⚙️ Generando archivos de configuración...")
    generate_config_files()
    generate_env_and_config()
    print()
    
    print("🔧 Generando utilidades...")
    generate_utils_files()
    print()
    
    print("🧠 Generando motor principal...")
    generate_core_files()
    print()
    
    print("📋 Generando frameworks metodológicos...")
    generate_methodology_files()
    print()
    
    print("📚 Generando knowledge base...")
    generate_knowledge_base()
    print()
    
    print("📝 Generando sistema de plantillas...")
    generate_templates()
    print()
    
    print("🎯 Generando aplicación principal...")
    generate_main_file()
    print()
    
    print("📦 Generando archivos de dependencias...")
    generate_requirements()
    print()
    
    print("📖 Generando documentación...")
    generate_readme()
    print()
    
    print("🔧 Generando archivos adicionales...")
    generate_additional_files()
    print()
    
    print("🎉 ¡PROYECTO COMPLETO GENERADO!")
    print("=" * 60)
    print()
    print("📋 Próximos pasos:")
    print("1. Instalar dependencias: pip install -r requirements.txt")
    print("2. Configurar .env con tu ANTHROPIC_API_KEY")
    print("3. Ejecutar: python main.py setup")
    print("4. Probar: python main.py test")
    print("5. Iniciar: python main.py start")
    print()
    print("🚀 Inicio rápido: python scripts/quick_start.py")
    print()
    print("🔑 Obtén tu API key en: https://console.anthropic.com/")
    print("💰 Créditos gratuitos: $5 USD para empezar")
    print()
    print("¡Listo para usar! 🚀")

if __name__ == "__main__":
    main()
