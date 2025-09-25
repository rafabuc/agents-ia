# core/agent.py
import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# Rich imports con fallback
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.markdown import Markdown
except ImportError:
    # Fallback si rich no está disponible
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
    
    class Panel:
        @staticmethod
        def fit(content, title=""):
            return f"\n=== {title} ===\n{content}\n" + "="*20

# Importar nuestros módulos
from database.conversation_db import ConversationDatabase, ConversationMessage
from core.claude_client import ClaudeClient

class PMAgent:
    """Agente de Project Management con persistencia avanzada"""
    
    def __init__(self, api_key: str = None):
        self.console = Console()
        self.current_project = None
        self.current_context = []
        
        # Inicializar base de datos
        try:
            self.db = ConversationDatabase()
            print("✅ Database system initialized")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            raise
        
        # Inicializar cliente Claude
        try:
            self.claude_client = ClaudeClient(api_key=api_key)
            self.claude_available = bool(self.claude_client.client)
        except Exception as e:
            print(f"⚠️ Claude client error: {e}")
            self.claude_client = None
            self.claude_available = False
        
        # Sesión actual
        self.current_session_id = None
        self.message_count = 0
        self.auto_save_threshold = 10  # Auto-guardar cada 10 mensajes
    
    def start_new_session(self, project_id: str, session_name: str = None, tags: List[str] = None):
        """Iniciar nueva sesión de conversación"""
        if not session_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = f"Sesión_{timestamp}"
        
        try:
            self.current_session_id = self.db.create_session(
                project_id=project_id,
                name=session_name,
                tags=tags or []
            )
            self.current_project = project_id
            self.message_count = 0
            
            print(f"✅ Nueva sesión iniciada: {session_name}")
            print(f"📋 Proyecto: {project_id}")
            print(f"🆔 ID: {self.current_session_id[:8]}...")
            
            return self.current_session_id
            
        except Exception as e:
            print(f"❌ Error al iniciar sesión: {str(e)}")
            return None
    
    def chat_with_context(self, message: str) -> str:
        """Chat con contexto y guardado automático"""
        if not self.current_session_id:
            # Auto-crear sesión si no existe
            project_id = self.current_project or "default"
            self.start_new_session(project_id, "Sesión Automática")
        
        try:
            # Guardar mensaje del usuario
            self.db.add_message(
                session_id=self.current_session_id,
                project_id=self.current_project or "default",
                role="user",
                content=message,
                metadata={"timestamp": datetime.now().isoformat()}
            )
            
            # Obtener contexto de mensajes anteriores
            recent_messages = self.db.get_session_messages(
                self.current_session_id, 
                limit=10  # Últimos 10 mensajes para contexto
            )
            
            # Generar respuesta
            if self.claude_available and self.claude_client:
                # Usar Claude real
                response_content, tokens_used = self._chat_with_claude(message, recent_messages)
                model_used = self.claude_client.model
            else:
                # Usar respuesta simulada mejorada
                response_content = self._generate_fallback_response(message)
                tokens_used = len(message.split()) + len(response_content.split())
                model_used = "fallback-pm-agent"
            
            # Guardar respuesta del asistente
            self.db.add_message(
                session_id=self.current_session_id,
                project_id=self.current_project or "default",
                role="assistant",
                content=response_content,
                tokens_used=tokens_used,
                model_used=model_used,
                metadata={"model": model_used, "timestamp": datetime.now().isoformat()}
            )
            
            self.message_count += 2  # Usuario + asistente
            
            # Auto-guardar si se alcanza el umbral
            if self.message_count >= self.auto_save_threshold:
                self._auto_save_checkpoint()
                self.message_count = 0
            
            return response_content
            
        except Exception as e:
            print(f"❌ Error in chat: {e}")
            return f"❌ Error procesando mensaje: {str(e)}"
    
    def _chat_with_claude(self, message: str, recent_messages) -> tuple:
        """Llamar a Claude con contexto completo"""
        # Construir historial para Claude
        conversation_history = []
        for msg in recent_messages[:-1]:  # Excluir el mensaje actual
            conversation_history.append({
                'role': msg.role,
                'content': msg.content
            })
        
        # System prompt especializado para PM
        pm_system_prompt = f"""Eres PM-Agent, un asistente experto en Project Management para el proyecto "{self.current_project or 'General'}".

Tu especialidad incluye:
- 🏗️ Metodologías: Scrum, Kanban, PMI, SAFe, Lean, Waterfall
- 📊 Herramientas: Jira, Asana, Monday.com, MS Project, Notion
- 📈 Analytics: KPIs, métricas de velocidad, burndown charts  
- 👥 Liderazgo: gestión de equipos, stakeholders, comunicación
- 🎯 Estrategia: roadmaps, OKRs, planificación estratégica

Contexto del proyecto: {self.current_project or 'Proyecto general'}
Mensajes en sesión: {len(recent_messages)}

Proporciona respuestas:
- 🎯 Prácticas y accionables
- 📋 Estructuradas con ejemplos concretos
- 🔧 Adaptadas al contexto del proyecto
- 💡 Con recomendaciones de mejores prácticas"""

        response = self.claude_client.chat(
            message=message,
            system_prompt=pm_system_prompt,
            conversation_history=conversation_history
        )
        
        return response.content, response.tokens_used
    
    def _generate_fallback_response(self, message: str) -> str:
        """Respuesta de fallback mejorada cuando Claude no está disponible"""
        message_lower = message.lower()
        
        pm_responses = {
            "scrum": "🏃‍♂️ **Scrum** es un framework ágil que se basa en sprints iterativos de 1-4 semanas.\n\n**Eventos clave:**\n- 📅 **Sprint Planning**: Definir qué se hará\n- 🗣️ **Daily Scrum**: Sincronización diaria\n- 🎯 **Sprint Review**: Demo del incremento\n- 🔄 **Retrospectiva**: Mejora continua\n\n**Roles:**\n- 👨‍💼 **Product Owner**: Define el qué\n- 🏃‍♂️ **Scrum Master**: Facilita el proceso\n- 👥 **Development Team**: Construye el producto",
            
            "sprint": "📅 **Planificación de Sprint**\n\n**Pasos clave:**\n1. 📋 **Review del Product Backlog** con PO\n2. 🎯 **Definir Sprint Goal** claro\n3. 📊 **Estimar historias** (Planning Poker)\n4. ✅ **Seleccionar items** para el Sprint\n5. 📝 **Crear Sprint Backlog** detallado\n\n**Duración típica:** 4-8 horas para sprints de 2 semanas\n**Output:** Sprint Backlog committeado por el equipo",
            
            "kanban": "📋 **Kanban** - Visualización del flujo de trabajo\n\n**Principios:**\n- 👁️ **Visualizar** el trabajo\n- 🚫 **Limitar WIP** (Work in Progress)\n- 📊 **Medir y optimizar** el flujo\n\n**Columnas típicas:**\nTo Do → In Progress → Review → Done\n\n**Métricas clave:**\n- ⏱️ **Lead Time**: Tiempo total del item\n- 🔄 **Cycle Time**: Tiempo en proceso\n- 📈 **Throughput**: Items completados por período",
            
            "riesgo": "⚠️ **Gestión de Riesgos en Proyectos**\n\n**Proceso:**\n1. 🔍 **Identificación**: Brainstorming, checklist, expertos\n2. 📊 **Análisis**: Probabilidad × Impacto\n3. 📋 **Planificación**: Evitar, mitigar, transferir, aceptar\n4. 👀 **Monitoreo**: Seguimiento continuo\n\n**Herramientas:**\n- 📈 Matriz de riesgos (Probabilidad/Impacto)\n- 📝 Registro de riesgos\n- 🚨 Indicadores de alerta temprana",
            
            "stakeholder": "👥 **Gestión de Stakeholders**\n\n**Pasos:**\n1. 🔍 **Identificación**: Quién puede influir/ser afectado\n2. 📊 **Análisis**: Matriz Poder/Interés\n3. 📋 **Estrategia**: Cómo gestionar cada grupo\n4. 🗣️ **Comunicación**: Plan de comunicaciones\n5. 📈 **Monitoreo**: Satisfacción y engagement\n\n**Matriz Poder/Interés:**\n- 👑 Alto Poder + Alto Interés: **Gestionar de cerca**\n- 🤝 Alto Poder + Bajo Interés: **Mantener satisfecho**\n- 📢 Bajo Poder + Alto Interés: **Mantener informado**\n- 📋 Bajo Poder + Bajo Interés: **Monitorear**",
        }
        
        # Buscar respuesta relevante
        for keyword, response in pm_responses.items():
            if keyword in message_lower:
                return f"{response}\n\n💡 *Para respuestas Claude reales, configura ANTHROPIC_API_KEY*"
        
        return f"🤖 **Consulta sobre:** *{message[:100]}{'...' if len(message) > 100 else ''}*\n\n Como **PM-Agent**, puedo ayudarte con:\n\n- 🏗️ **Metodologías**: Scrum, Kanban, SAFe, PMI\n- 📊 **Planificación**: Roadmaps, sprints, estimaciones\n- 👥 **Equipos**: Liderazgo, comunicación, stakeholders\n- ⚠️ **Riesgos**: Identificación, análisis, mitigación\n- 📈 **Métricas**: KPIs, velocidad, burndown\n\n💡 *Para respuestas Claude reales, configura ANTHROPIC_API_KEY*"
    
    def _auto_save_checkpoint(self):
        """Guardar checkpoint automático"""
        try:
            stats = self.db.get_session_stats(self.current_session_id)
            print(f"💾 Auto-guardado: {stats['message_count']} mensajes, {stats['total_tokens']} tokens")
        except Exception as e:
            print(f"⚠️ Error en auto-save: {e}")
    
    def load_session(self, session_id: str) -> bool:
        """Cargar sesión existente"""
        try:
            stats = self.db.get_session_stats(session_id)
            if not stats:
                print("❌ Sesión no encontrada")
                return False
            
            self.current_session_id = session_id
            self.current_project = stats['project_id']
            self.message_count = 0
            
            print(f"✅ Sesión cargada: {stats['name']}")
            print(f"📋 Proyecto: {stats['project_id']}")
            print(f"💬 Mensajes: {stats['message_count']}")
            print(f"🎯 Tokens: {stats['total_tokens']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando sesión: {str(e)}")
            return False
    
    def list_sessions(self, project_id: str = None) -> List[Dict]:
        """Listar sesiones disponibles"""
        try:
            sessions = self.db.list_sessions(project_id=project_id, limit=20)
            
            if not sessions:
                print("📋 No hay sesiones disponibles")
                return []
            
            print("\n💬 Sesiones de Conversación:")
            print("-" * 80)
            print(f"{'ID':<10} {'Nombre':<25} {'Proyecto':<15} {'Msgs':<6} {'Tokens':<8} {'Fecha'}")
            print("-" * 80)
            
            for session in sessions:
                print(f"{session['id'][:8]:<10} {session['name'][:24]:<25} {session['project_id'][:14]:<15} {session['message_count']:<6} {session['total_tokens']:<8} {session['updated_at'][:10]}")
            
            return sessions
            
        except Exception as e:
            print(f"❌ Error listando sesiones: {str(e)}")
            return []
    
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict]:
        """Buscar en conversaciones"""
        try:
            results = self.db.search_conversations(
                query=query, 
                project_id=self.current_project,
                limit=limit
            )
            
            if not results:
                print(f"🔍 No se encontraron resultados para: '{query}'")
                return []
            
            print(f"🔍 Encontrados {len(results)} resultados para: '{query}'\n")
            
            for i, result in enumerate(results, 1):
                content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                
                print(f"📋 Resultado {i}")
                print(f"{result['role'].upper()}: {content_preview}")
                print(f"Sesión: {result['session_id'][:8]}... | {result['timestamp'][:10]}")
                print("-" * 50)
            
            return results
            
        except Exception as e:
            print(f"❌ Error en búsqueda: {str(e)}")
            return []
    
    def export_current_session(self, format: str = "markdown") -> str:
        """Exportar sesión actual"""
        if not self.current_session_id:
            print("❌ No hay sesión activa para exportar")
            return ""
        
        try:
            exported_content = self.db.export_session(self.current_session_id, format)
            
            # Guardar en archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_session_{timestamp}.{format}"
            
            Path("exports").mkdir(exist_ok=True)
            with open(f"exports/{filename}", 'w', encoding='utf-8') as f:
                f.write(exported_content)
            
            print(f"✅ Sesión exportada: exports/{filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exportando: {str(e)}")
            return ""
    
    def show_session_analytics(self, days: int = 30):
        """Mostrar analytics básicos"""
        try:
            if self.current_session_id:
                stats = self.db.get_session_stats(self.current_session_id)
                
                print(f"\n📊 Analytics - Sesión Actual")
                print("=" * 40)
                print(f"📝 Nombre: {stats['name']}")
                print(f"🏷️ Proyecto: {stats['project_id']}")
                print(f"💬 Mensajes: {stats['message_count']}")
                print(f"🎯 Tokens: {stats['total_tokens']}")
                print(f"📅 Creado: {stats['created_at'][:19]}")
                print(f"🔄 Actualizado: {stats['updated_at'][:19]}")
            else:
                print("⚠️ No hay sesión activa")
                
        except Exception as e:
            print(f"❌ Error mostrando analytics: {str(e)}")
    
    def generate_session_summary(self, session_id: str = None) -> str:
        """Generar resumen automático de la sesión"""
        target_session = session_id or self.current_session_id
        
        if not target_session:
            print("❌ No hay sesión para resumir")
            return ""
        
        try:
            messages = self.db.get_session_messages(target_session)
            
            if len(messages) < 3:
                return "Sesión muy corta para generar resumen"
            
            # Construir contenido para resumir
            content_to_summarize = ""
            for msg in messages:
                role_prefix = "Usuario" if msg.role == "user" else "Asistente"
                content_to_summarize += f"{role_prefix}: {msg.content}\n---\n"
            
            # Generar resumen
            if self.claude_available and self.claude_client:
                summary = self.claude_client.generate_summary(content_to_summarize)
            else:
                summary = f"Sesión con {len(messages)} mensajes sobre temas de project management. Última actividad: {messages[-1].timestamp.strftime('%Y-%m-%d %H:%M')}"
            
            print(f"📝 Resumen generado para sesión {target_session[:8]}...")
            return summary
            
        except Exception as e:
            print(f"❌ Error generando resumen: {str(e)}")
            return ""