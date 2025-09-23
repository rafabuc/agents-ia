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
        'ui', 'utils', 'tests'
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
    
    # core/agent.py (versión simplificada)
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
                "Plan"
            ]
        }
    }