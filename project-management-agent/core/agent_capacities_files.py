import json
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger

from core.claude_client import ClaudeClient
from config.settings import settings


# Agregar al inicio de core/agent.py
from database.conversation_db import ConversationDatabase, ConversationMessage, ConversationSession


class ProjectManagementAgent:
    """Agente principal para gestión de proyectos con PMI y SAFe"""
    
    def __init__(self):
        self.claude_client = ClaudeClient()
        self.current_project: Optional[Dict] = None
        self.pending_approvals: List[Dict] = []
        
        # Nueva base de datos de conversaciones
        self.conversation_db = ConversationDatabase()
        self.current_session_id: Optional[str] = None
        
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
        """Chat con contexto y guardado automático en BD"""
        return self.chat_with_context_db(message)

    #Chat with context cionversation saved to  files, is replaced  with context db 
    def chat_with_context___(self, message: str) -> str:
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
        
        
        response = self.claude_client.chat(message, system_prompt)
    
        # Auto-guardado cada 10 mensajes
        try:
            self.auto_save_conversation()
        except Exception as e:
            logger.warning(f"Auto-save failed: {e}")
        
        return response   
    
    
    
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



#####################################################################
#####################################################################
    #Funciones para capacidades de  DB 
    
    def start_conversation_session(self, session_name: str = None, tags: List[str] = None) -> str:
        """Iniciar nueva sesión de conversación"""
        if not self.current_project:
            raise ValueError("No hay proyecto activo")
        
        session_name = session_name or f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        tags = tags or []
        
        # Agregar tags automáticos
        auto_tags = [
            self.current_project['methodology'].lower(),
            self.current_project['type'].lower().replace(' ', '_'),
            self.current_project.get('phase', 'unknown').lower()
        ]
        tags.extend(auto_tags)
        
        self.current_session_id = self.conversation_db.create_session(
            project_id=self.current_project['id'],
            name=session_name,
            tags=list(set(tags))  # Eliminar duplicados
        )
        
        logger.info(f"Started conversation session: {self.current_session_id}")
        return self.current_session_id
    
    def save_message_to_db(self, role: str, content: str, tokens_used: int = None, 
                          model_used: str = None, metadata: Dict = None):
        """Guardar mensaje en base de datos"""
        if not self.current_project or not self.current_session_id:
            return
        
        try:
            self.conversation_db.add_message(
                session_id=self.current_session_id,
                project_id=self.current_project['id'],
                role=role,
                content=content,
                tokens_used=tokens_used,
                model_used=model_used or settings.claude.model,
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"Error saving message to database: {e}")
    
    def load_conversation_session(self, session_id: str) -> Dict:
        """Cargar sesión de conversación desde base de datos"""
        try:
            messages = self.conversation_db.get_session_messages(session_id)
            
            # Convertir a formato Claude
            claude_history = []
            for msg in messages:
                claude_history.append({
                    'role': msg.role,
                    'content': msg.content
                })
            
            # Restaurar en Claude client
            self.claude_client.conversation_history = claude_history
            self.current_session_id = session_id
            
            return {
                'success': True,
                'message_count': len(messages),
                'session_id': session_id,
                'messages_loaded': len(claude_history)
            }
            
        except Exception as e:
            logger.error(f"Error loading conversation session: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_conversation_sessions(self) -> List[ConversationSession]:
        """Obtener sesiones del proyecto actual"""
        if not self.current_project:
            return []
        
        return self.conversation_db.get_project_sessions(self.current_project['id'])
    
    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """Buscar en conversaciones"""
        if not self.current_project:
            return []
        
        return self.conversation_db.search_messages(
            query=query,
            project_id=self.current_project['id'],
            limit=limit
        )
    
    def chat_with_context_db(self, message: str) -> str:
        """Chat con contexto y guardado en BD"""
        
        # Iniciar sesión si no existe
        if not self.current_session_id and self.current_project:
            self.start_conversation_session()
        
        # Guardar mensaje del usuario
        self.save_message_to_db('user', message)
        
        # Obtener respuesta (código existente)
        context_prompt = ""
        if self.current_project:
            context_prompt = f"""
            PROYECTO ACTIVO:
            - Nombre: {self.current_project['name']}
            - ID: {self.current_project['id']}
            - Metodología: {self.current_project['methodology']}
            - Tipo: {self.current_project['type']}
            - Estado: {self.current_project['status']}
            
            """
        
        system_prompt = f"""
        Eres el Project Management Agent con capacidades completas.
        {context_prompt}
        
        Responde de manera útil y práctica.
        """
        
        response = self.claude_client.chat(message, system_prompt)
        
        # Guardar respuesta del agente
        # Estimar tokens (aproximado)
        estimated_tokens = len(message.split()) + len(response.split())
        
        self.save_message_to_db(
            'assistant', 
            response, 
            tokens_used=estimated_tokens,
            metadata={'project_phase': self.current_project.get('phase', 'unknown')}
        )
        
        return response
    
    def generate_conversation_summary(self, session_id: str = None) -> str:
        """Generar resumen inteligente de conversación"""
        target_session = session_id or self.current_session_id
        
        if not target_session:
            return "No hay sesión activa"
        
        messages = self.conversation_db.get_session_messages(target_session)
        
        if not messages:
            return "No hay mensajes en esta sesión"
        
        # Crear prompt para resumen
        conversation_text = ""
        for msg in messages[-10:]:  # Últimos 10 mensajes
            role = "Usuario" if msg.role == 'user' else "Agente"
            conversation_text += f"{role}: {msg.content[:200]}...\n"
        
        summary_prompt = f"""
        Genera un resumen ejecutivo de esta conversación de gestión de proyectos:
        
        Proyecto: {self.current_project['name'] if self.current_project else 'N/A'}
        Metodología: {self.current_project['methodology'] if self.current_project else 'N/A'}
        Total de mensajes: {len(messages)}
        
        Últimos intercambios:
        {conversation_text}
        
        Incluye:
        1. Objetivos principales discutidos
        2. Documentos o planes generados
        3. Decisiones tomadas
        4. Próximos pasos identificados
        5. Aspectos metodológicos aplicados
        
        Máximo 300 palabras.
        """
        
        summary = self.claude_client.chat(summary_prompt, "Eres un experto en resumir conversaciones de gestión de proyectos de manera concisa y estructurada.")
        
        # Guardar resumen en BD
        self.conversation_db.update_session_summary(target_session, summary)
        
        return summary
    
    def export_conversation_data(self, session_id: str = None, format: str = 'markdown') -> Dict:
        """Exportar conversación en formato específico"""
        target_session = session_id or self.current_session_id
        
        if not target_session:
            return {'success': False, 'error': 'No hay sesión para exportar'}
        
        try:
            exports = self.conversation_db.export_session_to_formats(target_session)
            
            if format not in exports:
                return {'success': False, 'error': f'Formato {format} no disponible'}
            
            # Guardar archivo
            project_path = Path("./projects") / self.current_project['id'] / "exports"
            project_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{target_session[:8]}_{timestamp}.{format}"
            file_path = project_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(exports[format])
            
            return {
                'success': True,
                'file_path': str(file_path),
                'filename': filename,
                'format': format,
                'size': len(exports[format])
            }
            
        except Exception as e:
            logger.error(f"Error exporting conversation: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_usage_statistics(self) -> Dict:
        """Obtener estadísticas de uso del proyecto"""
        if not self.current_project:
            return {'error': 'No hay proyecto activo'}
        
        stats = self.conversation_db.get_usage_stats(self.current_project['id'])
        
        # Agregar estadísticas adicionales
        sessions = self.get_conversation_sessions()
        
        stats.update({
            'active_sessions': len([s for s in sessions if s.status == 'active']),
            'total_sessions': len(sessions),
            'current_session': self.current_session_id,
            'project_name': self.current_project['name'],
            'methodology': self.current_project['methodology']
        })
        
        return stats
    
    def cleanup_old_data(self, days: int = 90) -> Dict:
        """Limpiar datos antiguos"""
        try:
            archived_count = self.conversation_db.cleanup_old_sessions(days)
            
            return {
                'success': True,
                'archived_sessions': archived_count,
                'message': f'Se archivaron {archived_count} sesiones antiguas'
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return {'success': False, 'error': str(e)}


######################################################################
######################################################################

    #Funciones guardar  historial conversaciones en  archvioscd

    # Agregar estas funciones a core/agent.py

    def save_conversation_history(self, session_name: str = None) -> Dict:
        """Guardar historial completo de la conversación actual"""
        try:
            if not self.current_project:
                return {'success': False, 'error': 'No hay proyecto activo'}
            
            project_path = Path("./projects") / self.current_project['id']
            conversations_path = project_path / "conversations"
            conversations_path.mkdir(exist_ok=True)
            
            # Crear nombre de sesión
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if session_name:
                filename = f"{session_name}_{timestamp}.md"
            else:
                filename = f"conversation_{timestamp}.md"
            
            file_path = conversations_path / filename
            
            # Crear contenido detallado
            content = self._format_conversation_content()
            
            # Guardar archivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Guardar metadatos de la conversación
            metadata = {
                'filename': filename,
                'timestamp': timestamp,
                'project_id': self.current_project['id'],
                'project_name': self.current_project['name'],
                'message_count': len(self.claude_client.conversation_history),
                'session_name': session_name or 'default'
            }
            
            # Actualizar registro en el proyecto
            if 'conversation_sessions' not in self.current_project:
                self.current_project['conversation_sessions'] = []
            
            self.current_project['conversation_sessions'].append(metadata)
            self._save_project_data()
            
            logger.info(f"Conversation history saved: {file_path}")
            
            return {
                'success': True,
                'file_path': str(file_path),
                'filename': filename,
                'message_count': metadata['message_count'],
                'message': f'Historial guardado: {filename} ({metadata["message_count"]} mensajes)'
            }
            
        except Exception as e:
            logger.error(f"Error saving conversation history: {e}")
            return {'success': False, 'error': str(e)}

    def load_conversation_history(self, filename: str = None, session_name: str = None) -> Dict:
        """Cargar historial de conversación desde archivo"""
        try:
            if not self.current_project:
                return {'success': False, 'error': 'No hay proyecto activo'}
            
            project_path = Path("./projects") / self.current_project['id']
            conversations_path = project_path / "conversations"
            
            if not conversations_path.exists():
                return {'success': False, 'error': 'No hay conversaciones guardadas'}
            
            # Encontrar archivo
            target_file = None
            
            if filename:
                target_file = conversations_path / filename
            elif session_name:
                # Buscar por nombre de sesión
                for file_path in conversations_path.glob(f"*{session_name}*.md"):
                    target_file = file_path
                    break
            else:
                # Usar la conversación más reciente
                conversation_files = list(conversations_path.glob("*.md"))
                if conversation_files:
                    target_file = max(conversation_files, key=lambda p: p.stat().st_mtime)
            
            if not target_file or not target_file.exists():
                return {'success': False, 'error': 'Archivo de conversación no encontrado'}
            
            # Leer y parsear el archivo
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extraer historial de mensajes del contenido
            history = self._parse_conversation_content(content)
            
            # Restaurar en Claude client
            self.claude_client.conversation_history = history
            
            logger.info(f"Conversation history loaded: {target_file}")
            
            return {
                'success': True,
                'filename': target_file.name,
                'message_count': len(history),
                'file_path': str(target_file),
                'message': f'Historial cargado: {target_file.name} ({len(history)} mensajes)'
            }
            
        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            return {'success': False, 'error': str(e)}

    def list_conversation_sessions(self) -> Dict:
        """Listar todas las sesiones de conversación guardadas"""
        try:
            if not self.current_project:
                return {'success': False, 'error': 'No hay proyecto activo'}
            
            project_path = Path("./projects") / self.current_project['id']
            conversations_path = project_path / "conversations"
            
            sessions = []
            
            if conversations_path.exists():
                for file_path in conversations_path.glob("*.md"):
                    try:
                        stat = file_path.stat()
                        
                        # Leer información básica del archivo
                        with open(file_path, 'r', encoding='utf-8') as f:
                            first_lines = f.read(500)  # Primeras líneas para metadata
                        
                        # Contar mensajes aproximadamente
                        message_count = first_lines.count('### **Usuario**') + first_lines.count('### **Agente**')
                        
                        sessions.append({
                            'filename': file_path.name,
                            'path': str(file_path),
                            'size_kb': round(stat.st_size / 1024, 1),
                            'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M'),
                            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                            'estimated_messages': message_count
                        })
                        
                    except Exception as e:
                        logger.warning(f"Error reading session file {file_path}: {e}")
                        continue
            
            # Ordenar por fecha de modificación (más reciente primero)
            sessions.sort(key=lambda x: x['modified'], reverse=True)
            
            return {
                'success': True,
                'sessions': sessions,
                'total_sessions': len(sessions)
            }
            
        except Exception as e:
            logger.error(f"Error listing conversation sessions: {e}")
            return {'success': False, 'error': str(e)}

    def auto_save_conversation(self) -> Dict:
        """Guardar automáticamente la conversación cada cierto número de mensajes"""
        try:
            # Auto-guardar cada 10 mensajes
            message_count = len(self.claude_client.conversation_history)
            
            if message_count > 0 and message_count % 10 == 0:
                return self.save_conversation_history(f"auto_save_{message_count}")
            
            return {'success': True, 'message': 'No se requiere auto-save aún'}
            
        except Exception as e:
            logger.error(f"Error in auto-save: {e}")
            return {'success': False, 'error': str(e)}

    def clear_current_conversation(self) -> Dict:
        """Limpiar conversación actual (con opción de guardar antes)"""
        try:
            message_count = len(self.claude_client.conversation_history)
            
            if message_count > 0:
                # Guardar automáticamente antes de limpiar
                save_result = self.save_conversation_history("before_clear")
                
                # Limpiar historial
                self.claude_client.clear_history()
                
                return {
                    'success': True,
                    'message': f'Conversación limpiada. {message_count} mensajes guardados en {save_result.get("filename", "archivo")}',
                    'saved_file': save_result.get('filename', '')
                }
            else:
                return {'success': True, 'message': 'No hay conversación que limpiar'}
                
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            return {'success': False, 'error': str(e)}

    def _format_conversation_content(self) -> str:
        """Formatear contenido de conversación para archivo"""
        content = f"# Conversación - {self.current_project['name']}\n\n"
        content += f"**Proyecto:** {self.current_project['name']}\n"
        content += f"**ID:** {self.current_project['id']}\n"
        content += f"**Metodología:** {self.current_project['methodology']}\n"
        content += f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"**Mensajes:** {len(self.claude_client.conversation_history)}\n\n"
        
        content += "---\n\n"
        content += "## Historial de Conversación\n\n"
        
        if hasattr(self.claude_client, 'conversation_history'):
            for i, msg in enumerate(self.claude_client.conversation_history, 1):
                role = "Usuario" if msg['role'] == 'user' else "Agente"
                content += f"### **{role}** (Mensaje {i})\n\n"
                content += f"{msg['content']}\n\n"
                content += "---\n\n"
        
        # Agregar resumen al final
        content += "## Resumen de la Sesión\n\n"
        content += f"- **Total de mensajes:** {len(self.claude_client.conversation_history)}\n"
        content += f"- **Proyecto activo:** {self.current_project['name']}\n"
        content += f"- **Metodología utilizada:** {self.current_project['methodology']}\n"
        content += f"- **Fase del proyecto:** {self.current_project.get('phase', 'N/A')}\n"
        
        return content

    def _parse_conversation_content(self, content: str) -> List[Dict]:
        """Parsear contenido de archivo para extraer historial"""
        history = []
        
        try:
            # Dividir por secciones de mensajes
            sections = content.split('### **')
            
            for section in sections[1:]:  # Saltar la primera sección (header)
                if section.startswith('Usuario'):
                    # Extraer contenido del mensaje del usuario
                    lines = section.split('\n')
                    message_content = '\n'.join(lines[2:]).split('---')[0].strip()
                    
                    if message_content:
                        history.append({
                            'role': 'user',
                            'content': message_content
                        })
                        
                elif section.startswith('Agente'):
                    # Extraer contenido del mensaje del agente
                    lines = section.split('\n')
                    message_content = '\n'.join(lines[2:]).split('---')[0].strip()
                    
                    if message_content:
                        history.append({
                            'role': 'assistant',
                            'content': message_content
                        })
        
        except Exception as e:
            logger.warning(f"Error parsing conversation content: {e}")
        
        return history

    def get_conversation_summary(self) -> str:
        """Obtener resumen de la conversación actual"""
        if not hasattr(self.claude_client, 'conversation_history') or not self.claude_client.conversation_history:
            return "No hay conversación activa."
        
        message_count = len(self.claude_client.conversation_history)
        user_messages = len([m for m in self.claude_client.conversation_history if m['role'] == 'user'])
        agent_messages = len([m for m in self.claude_client.conversation_history if m['role'] == 'assistant'])
        
        # Generar resumen inteligente con Claude
        summary_prompt = """
        Genera un resumen conciso de esta conversación de Project Management:
        
        Mensajes totales: {message_count}
        Mensajes de usuario: {user_messages}
        Respuestas del agente: {agent_messages}
        
        Últimos 3 intercambios:
        {recent_messages}
        
        Incluye:
        1. Temas principales discutidos
        2. Tareas o documentos generados
        3. Decisiones tomadas
        4. Próximos pasos sugeridos
        """.format(
            message_count=message_count,
            user_messages=user_messages,
            agent_messages=agent_messages,
            recent_messages=self._get_recent_messages(3)
        )
        
        return self.claude_client.chat(summary_prompt, "Eres un asistente que resume conversaciones de gestión de proyectos de manera concisa y estructurada.")

    def _get_recent_messages(self, count: int = 3) -> str:
        """Obtener mensajes recientes formateados"""
        if not hasattr(self.claude_client, 'conversation_history'):
            return "Sin mensajes"
        
        recent = self.claude_client.conversation_history[-count*2:] if len(self.claude_client.conversation_history) >= count*2 else self.claude_client.conversation_history
        
        formatted = ""
        for msg in recent:
            role = "Usuario" if msg['role'] == 'user' else "Agente"
            content = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
            formatted += f"{role}: {content}\n\n"
        
        return formatted



