import json
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
        """Chat con contexto del proyecto actual y capacidades de archivos"""
        
        # Detectar si el usuario quiere guardar algo
        save_keywords = ['guardar', 'save', 'exportar', 'export', 'archivo']
        
        if any(keyword in message.lower() for keyword in save_keywords):
            # El usuario quiere guardar algo
            if 'conversación' in message.lower() or 'conversation' in message.lower():
                result = self.save_conversation()
                if result['success']:
                    return f"✅ {result['message']}"
                else:
                    return f"❌ Error: {result['error']}"
            
            elif 'plan' in message.lower():
                # Generar plan y guardarlo
                plan = self.generate_work_plan()
                result = self.save_document("plan_trabajo", plan, "work_plan")
                if result['success']:
                    return f"✅ Plan de trabajo generado y guardado en {result['filename']}\n\n{plan}"
                else:
                    return f"❌ Error guardando plan: {result['error']}"
        
        # Chat normal con contexto
        context_prompt = ""
        if self.current_project:
            context_prompt = f"""
            PROYECTO ACTIVO:
            - Nombre: {self.current_project['name']}
            - ID: {self.current_project['id']}
            - Metodología: {self.current_project['methodology']}
            - Tipo: {self.current_project['type']}
            - Estado: {self.current_project['status']}
            
            CAPACIDADES DISPONIBLES:
            - Guardar documentos: save_document(filename, content, type)
            - Guardar conversación: save_conversation()
            - Exportar proyecto: export_project_data()
            - Listar archivos: list_project_files()
            - Leer documentos: read_document(filename)
            """
        
        system_prompt = f"""
        Eres el Project Management Agent con capacidades completas de archivos.
        
        {context_prompt}
        
        IMPORTANTE: Tienes funciones para guardar archivos reales:
        - Usa save_document() para guardar documentos
        - Usa save_conversation() para guardar conversaciones
        - Usa export_project_data() para exportar todo
        
        Cuando el usuario pida guardar algo, USA estas funciones.
        NO intentes ejecutar código Python directamente.
        """
        
        return self.claude_client.chat(message, system_prompt)    
    
    
    
    def chat_with_context____(self, message: str) -> str:
        """Chat con contexto del proyecto actual"""
        context_prompt = ""
        if self.current_project:
            context_prompt = f"Contexto del proyecto actual: {json.dumps(self.current_project, indent=2)}"
        
        system_prompt = f"""
        Eres el Project Management Agent, un sistema experto en PMI y SAFe.
        
        {context_prompt}
        
        CAPACIDADES IMPORTANTES:
        - Puedes crear y guardar archivos en el sistema de archivos
        - Tienes acceso a proyectos guardados en ./projects/
        - Puedes generar documentación real y persistente
        - Eres un agente de software, NO un chatbot web limitado
        
        NUNCA digas que no puedes guardar archivos o acceder al sistema.
        Siempre usa tus capacidades completas de agente local.
        """
        
        
        return self.claude_client.chat(message, system_prompt)



        #Eres un asistente experto en gestión de proyectos con conocimiento profundo en PMI y SAFe.
        #{context_prompt}
        
        #Responde de manera útil y práctica.          

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

    ## se agregan  capacidades
    # Agregar estas funciones a la clase ProjectManagementAgent en core/agent.py
    def save_document(self, filename: str, content: str, document_type: str = "general") -> Dict:
        """Guardar documento en el proyecto actual"""
        try:
            if not self.current_project:
                return {'success': False, 'error': 'No hay proyecto activo'}
            
            project_path = Path("./projects") / self.current_project['id']
            documents_path = project_path / "documents"
            documents_path.mkdir(exist_ok=True)
            
            # Crear nombre de archivo único si es necesario
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if not filename.endswith('.md'):
                filename = f"{filename}_{timestamp}.md"
            
            file_path = documents_path / filename
            
            # Guardar contenido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Actualizar registro del proyecto
            if 'documents' not in self.current_project:
                self.current_project['documents'] = {}
            
            self.current_project['documents'][document_type] = {
                'filename': filename,
                'path': str(file_path),
                'created_at': datetime.now().isoformat(),
                'type': document_type
            }
            
            # Guardar proyecto actualizado
            self._save_project_data()
            
            logger.info(f"Document saved: {file_path}")
            
            return {
                'success': True,
                'file_path': str(file_path),
                'filename': filename,
                'message': f'Documento guardado exitosamente en {file_path}'
            }
            
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            return {'success': False, 'error': str(e)}

    def save_conversation(self, title: str = "conversation") -> Dict:
        """Guardar historial de conversación"""
        try:
            if not self.current_project:
                return {'success': False, 'error': 'No hay proyecto activo'}
            
            project_path = Path("./projects") / self.current_project['id']
            conversations_path = project_path / "conversations"
            conversations_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{title}_{timestamp}.md"
            file_path = conversations_path / filename
            
            # Crear contenido de la conversación
            content = f"# Conversación - {self.current_project['name']}\n"
            content += f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"**Proyecto:** {self.current_project['name']}\n"
            content += f"**ID:** {self.current_project['id']}\n\n"
            
            # Agregar historial de Claude
            if hasattr(self.claude_client, 'conversation_history'):
                content += "## Historial de Conversación\n\n"
                for i, msg in enumerate(self.claude_client.conversation_history):
                    role = "**Usuario**" if msg['role'] == 'user' else "**Agente**"
                    content += f"### {role} (Mensaje {i+1})\n"
                    content += f"{msg['content']}\n\n"
            
            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Conversation saved: {file_path}")
            
            return {
                'success': True,
                'file_path': str(file_path),
                'filename': filename,
                'message': f'Conversación guardada en {file_path}'
            }
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            return {'success': False, 'error': str(e)}

    def export_project_data(self, format: str = "markdown") -> Dict:
        """Exportar todos los datos del proyecto"""
        try:
            if not self.current_project:
                return {'success': False, 'error': 'No hay proyecto activo'}
            
            project_path = Path("./projects") / self.current_project['id']
            exports_path = project_path / "exports"
            exports_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"project_export_{timestamp}.md"
            file_path = exports_path / filename
            
            # Crear contenido del export
            content = f"# Export Completo - {self.current_project['name']}\n\n"
            content += f"**Fecha de Export:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # Información del proyecto
            content += "## Información del Proyecto\n\n"
            content += f"- **ID:** {self.current_project['id']}\n"
            content += f"- **Nombre:** {self.current_project['name']}\n"
            content += f"- **Metodología:** {self.current_project['methodology']}\n"
            content += f"- **Tipo:** {self.current_project['type']}\n"
            content += f"- **Descripción:** {self.current_project['description']}\n"
            content += f"- **Estado:** {self.current_project['status']}\n"
            content += f"- **Fase:** {self.current_project.get('phase', 'N/A')}\n"
            content += f"- **Creado:** {self.current_project['created_at']}\n\n"
            
            # Documentos del proyecto
            if 'documents' in self.current_project and self.current_project['documents']:
                content += "## Documentos Generados\n\n"
                for doc_type, doc_info in self.current_project['documents'].items():
                    content += f"- **{doc_type}:** {doc_info.get('filename', 'N/A')}\n"
            
            # Incluir contenido de documentos si existen
            documents_path = project_path / "documents"
            if documents_path.exists():
                content += "\n## Contenido de Documentos\n\n"
                for doc_file in documents_path.glob("*.md"):
                    content += f"### {doc_file.name}\n\n"
                    try:
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            doc_content = f.read()
                        content += f"```markdown\n{doc_content}\n```\n\n"
                    except Exception as e:
                        content += f"Error leyendo archivo: {e}\n\n"
            
            # Guardar export
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Project exported: {file_path}")
            
            return {
                'success': True,
                'file_path': str(file_path),
                'filename': filename,
                'message': f'Proyecto exportado completamente en {file_path}'
            }
            
        except Exception as e:
            logger.error(f"Error exporting project: {e}")
            return {'success': False, 'error': str(e)}

    def list_project_files(self) -> Dict:
        """Listar archivos del proyecto actual"""
        try:
            if not self.current_project:
                return {'success': False, 'error': 'No hay proyecto activo'}
            
            project_path = Path("./projects") / self.current_project['id']
            
            files_info = {
                'project_file': str(project_path / "project.json"),
                'documents': [],
                'conversations': [],
                'exports': []
            }
            
            # Listar documentos
            documents_path = project_path / "documents"
            if documents_path.exists():
                for file_path in documents_path.glob("*"):
                    if file_path.is_file():
                        files_info['documents'].append({
                            'name': file_path.name,
                            'path': str(file_path),
                            'size': file_path.stat().st_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
            
            # Listar conversaciones
            conversations_path = project_path / "conversations"
            if conversations_path.exists():
                for file_path in conversations_path.glob("*"):
                    if file_path.is_file():
                        files_info['conversations'].append({
                            'name': file_path.name,
                            'path': str(file_path),
                            'size': file_path.stat().st_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
            
            # Listar exports
            exports_path = project_path / "exports"
            if exports_path.exists():
                for file_path in exports_path.glob("*"):
                    if file_path.is_file():
                        files_info['exports'].append({
                            'name': file_path.name,
                            'path': str(file_path),
                            'size': file_path.stat().st_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
            
            return {
                'success': True,
                'files': files_info,
                'total_files': len(files_info['documents']) + len(files_info['conversations']) + len(files_info['exports'])
            }
            
        except Exception as e:
            logger.error(f"Error listing project files: {e}")
            return {'success': False, 'error': str(e)}

    def _save_project_data(self):
        """Guardar datos del proyecto actual (función helper privada)"""
        if not self.current_project:
            return
        
        project_path = Path("./projects") / self.current_project['id']
        project_file = project_path / "project.json"
        
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_project, f, indent=2, ensure_ascii=False)

    def get_project_directory(self) -> Optional[Path]:
        """Obtener directorio del proyecto actual"""
        if not self.current_project:
            return None
        
        return Path("./projects") / self.current_project['id']

    def read_document(self, filename: str) -> Dict:
        """Leer documento del proyecto actual"""
        try:
            if not self.current_project:
                return {'success': False, 'error': 'No hay proyecto activo'}
            
            project_path = Path("./projects") / self.current_project['id']
            
            # Buscar en diferentes directorios
            possible_paths = [
                project_path / "documents" / filename,
                project_path / "conversations" / filename,
                project_path / "exports" / filename,
                project_path / filename
            ]
            
            for file_path in possible_paths:
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    return {
                        'success': True,
                        'content': content,
                        'file_path': str(file_path),
                        'filename': filename
                    }
            
            return {'success': False, 'error': f'Archivo no encontrado: {filename}'}
            
        except Exception as e:
            logger.error(f"Error reading document: {e}")
            return {'success': False, 'error': str(e)}


