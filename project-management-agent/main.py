#!/usr/bin/env python3
# main.py - PM-Agent v2.0 Final

import sys
import os
import signal
from pathlib import Path
from datetime import datetime

# Agregar path actual para imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


# Importar módulos principales
try:
    from core.agent import PMAgent
except ImportError as e:
    print(f"❌ Error importing agent: {e}")
    print("💡 Asegúrate de que los archivos estén en:")
    print("   - database/conversation_db.py")
    print("   - core/agent.py")
    print("   - core/claude_client.py")
    sys.exit(1)

class PMAgentCLI:
    """Interfaz de línea de comandos para PM Agent"""
    
    def __init__(self):
        self.agent = PMAgent()
        self.running = True
        
        # Configurar manejo de señales para Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Manejar Ctrl+C gracefully"""
        print("\n🔄 Guardando sesión antes de salir...")
        if self.agent.current_session_id:
            self.agent._auto_save_checkpoint()
        print("👋 ¡Hasta luego!")
        sys.exit(0)
    
    def start(self):
        """Iniciar la interfaz CLI"""
        print("="*60)
        print("🚀 PM-Agent v2.0 - Sistema de Gestión de Conversaciones")
        print("="*60)
        print("Comandos disponibles:")
        print("• nueva sesion - Crear nueva conversación")
        print("• cargar sesion - Cargar sesión existente")
        print("• buscar [término] - Buscar en historial")
        print("• exportar - Exportar sesión actual")
        print("• analytics - Ver estadísticas")
        print("• ayuda - Mostrar ayuda completa")
        print("• salir - Guardar y salir")
        print("="*60)
        
        # Auto-inicializar sesión
        self._initialize_session()
        
        while self.running:
            try:
                user_input = input(f"\nPM-Agent ({self.agent.current_project or 'general'}): ").strip()
                
                if not user_input:
                    continue
                
                self._process_command(user_input)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def _initialize_session(self):
        """Inicializar sesión al arrancar"""
        try:
            # Intentar cargar la última sesión activa
            recent_sessions = self.agent.list_sessions()
            
            if recent_sessions:
                latest_session = recent_sessions[0]
                
                response = input(f"\n¿Continuar con '{latest_session['name']}'? (s/N): ").lower()
                if response in ['s', 'si', 'yes', 'y']:
                    self.agent.load_session(latest_session['id'])
                    return
            
            # Si no hay sesiones o usuario no quiere continuar, crear nueva
            project_id = input("Proyecto (default): ").strip() or "default"
            session_name = input("Nombre de sesión (Nueva Sesión): ").strip() or "Nueva Sesión"
            
            self.agent.start_new_session(project_id, session_name)
            
        except Exception as e:
            print(f"⚠️ Error inicializando sesión: {e}")
            print("Iniciando sin sesión previa...")
    
    def _process_command(self, user_input: str):
        """Procesar comandos del usuario"""
        
        # Comandos del sistema
        if user_input.lower() == 'nueva sesion':
            self._cmd_new_session()
            
        elif user_input.lower() == 'cargar sesion':
            self._cmd_load_session()
            
        elif user_input.lower() == 'listar sesiones':
            self.agent.list_sessions(self.agent.current_project)
            
        elif user_input.lower().startswith('buscar '):
            query = user_input[7:].strip()
            if query:
                self.agent.search_conversations(query)
            else:
                print("❌ Especifica qué buscar: buscar [término]")
            
        elif user_input.lower() == 'exportar':
            self._cmd_export_session()
            
        elif user_input.lower() == 'analytics':
            self.agent.show_session_analytics()
            
        elif user_input.lower() == 'resumen':
            summary = self.agent.generate_session_summary()
            if summary:
                print(f"\n📝 Resumen:\n{summary}")
            
        elif user_input.lower() == 'ayuda':
            self._show_help()
            
        elif user_input.lower() == 'salir':
            self._cmd_exit()
            
        elif user_input.lower() == 'estado':
            self._show_status()
            
        else:
            # Procesar como mensaje de chat normal
            response = self.agent.chat_with_context(user_input)
            print(f"\n🤖 PM-Agent: {response}")
    
    def _cmd_new_session(self):
        """Comando: Nueva sesión"""
        try:
            # Guardar sesión actual si existe
            if self.agent.current_session_id:
                self.agent._auto_save_checkpoint()
            
            project_id = input("🏷️ Proyecto: ").strip() or self.agent.current_project or "default"
            session_name = input("📝 Nombre de sesión: ").strip() or "Nueva Sesión"
            
            # Opcional: tags
            tags_input = input("🏷️ Tags (separados por comas): ").strip()
            tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()] if tags_input else []
            
            self.agent.start_new_session(project_id, session_name, tags)
            
        except Exception as e:
            print(f"❌ Error creando sesión: {str(e)}")
    
    def _cmd_load_session(self):
        """Comando: Cargar sesión"""
        try:
            sessions = self.agent.list_sessions(limit=10)
            
            if not sessions:
                return
            
            # Mostrar opciones numeradas
            print("\n📋 Selecciona una sesión:")
            for i, session in enumerate(sessions, 1):
                print(f"{i}. {session['name']} ({session['project_id']}) - {session['message_count']} mensajes")
            
            choice = input("\nNúmero de sesión: ").strip()
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(sessions):
                    selected_session = sessions[choice_num - 1]
                    self.agent.load_session(selected_session['id'])
                else:
                    print("❌ Número inválido")
            except ValueError:
                print("❌ Ingresa un número válido")
                
        except Exception as e:
            print(f"❌ Error cargando sesión: {str(e)}")
    
    def _cmd_export_session(self):
        """Comando: Exportar sesión"""
        try:
            format_choice = input("Formato (markdown/json) [markdown]: ").strip().lower() or "markdown"
            
            if format_choice not in ["markdown", "json"]:
                print("❌ Formato inválido. Usa: markdown o json")
                return
                
            filename = self.agent.export_current_session(format_choice)
            
            if filename:
                print(f"✅ Archivo exportado: {filename}")
                
        except Exception as e:
            print(f"❌ Error exportando: {str(e)}")
    
    def _show_status(self):
        """Mostrar estado actual del agente"""
        try:
            if self.agent.current_session_id:
                stats = self.agent.db.get_session_stats(self.agent.current_session_id)
                
                print("\n🟢 Sesión Activa")
                print("=" * 30)
                print(f"📝 Nombre: {stats['name']}")
                print(f"🏷️ Proyecto: {stats['project_id']}")
                print(f"💬 Mensajes: {stats['message_count']}")
                print(f"🎯 Tokens: {stats['total_tokens']}")
                print(f"📅 Creado: {stats['created_at'][:19]}")
                print(f"🔄 Actualizado: {stats['updated_at'][:19]}")
                print(f"🆔 ID: {self.agent.current_session_id[:8]}...")
                
                # Estado de Claude
                if self.agent.claude_available:
                    print(f"🤖 Claude: ✅ Activo ({self.agent.claude_client.model})")
                else:
                    print("🤖 Claude: ⚠️ Modo fallback (configura ANTHROPIC_API_KEY)")
            else:
                print("⚠️ No hay sesión activa")
                
        except Exception as e:
            print(f"❌ Error obteniendo estado: {str(e)}")
    
    def _show_help(self):
        """Mostrar ayuda completa"""
        help_text = """
🚀 PM-Agent v2.0 - Comandos Disponibles

📋 Gestión de Sesiones:
• nueva sesion       - Crear nueva sesión de conversación
• cargar sesion      - Cargar sesión existente
• listar sesiones    - Ver todas las sesiones disponibles
• exportar          - Exportar sesión actual (Markdown/JSON)
• resumen           - Generar resumen automático de la sesión

🔍 Búsqueda y Analytics:
• buscar [término]   - Buscar en todas las conversaciones
• analytics         - Ver estadísticas de uso (mensajes, tokens)
• estado           - Ver estado de la sesión actual

🤖 Funciones del Agente:
• ayuda            - Mostrar esta ayuda
• salir            - Guardar y salir del programa

💬 Chat Normal:
• Cualquier otro texto será procesado como una consulta de PM
• El contexto se mantiene automáticamente entre mensajes
• Auto-guardado cada 10 mensajes

🎯 Especialidades de PM-Agent:
• Metodologías: Scrum, Kanban, PMI, SAFe
• Herramientas: Jira, Asana, Monday.com, MS Project
• Liderazgo: Equipos, stakeholders, comunicación
• Métricas: KPIs, velocity, burndown charts

💡 Configuración de Claude:
Para respuestas reales de Claude, configura:
export ANTHROPIC_API_KEY=tu_api_key

Ejemplos de uso:
PM-Agent> ¿Cómo planificar un Sprint en Scrum?
PM-Agent> buscar sprint planning
PM-Agent> exportar
PM-Agent> analytics
        """
        print(help_text)
    
    def _cmd_exit(self):
        """Comando: Salir del programa"""
        try:
            if self.agent.current_session_id:
                self.agent._auto_save_checkpoint()
                print("💾 Sesión guardada automáticamente")
            
            print("👋 ¡Hasta luego!")
            self.running = False
            
        except Exception as e:
            print(f"⚠️ Error guardando al salir: {str(e)}")
            self.running = False


def check_dependencies():
    """Verificar dependencias básicas"""
    missing = []
    
    # Verificar estructura de archivos
    required_files = [
        "database/conversation_db.py",
        "core/agent.py", 
        "core/claude_client.py"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print("❌ Archivos faltantes:")
        for file in missing:
            print(f"   - {file}")
        print("\n💡 Asegúrate de tener todos los archivos en su lugar")
        return False
    
    # Crear directorios necesarios
    Path("data").mkdir(exist_ok=True)
    Path("exports").mkdir(exist_ok=True)
    
    return True


def main():
    """Función principal"""
    print("🔄 Iniciando PM-Agent...")
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar variables de entorno
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("💡 Tip: Para usar Claude real, configura ANTHROPIC_API_KEY")
        print("   export ANTHROPIC_API_KEY=tu_api_key")
    
    try:
        # Inicializar y ejecutar CLI
        cli = PMAgentCLI()
        cli.start()
        
    except KeyboardInterrupt:
        print("\n👋 Interrumpido por usuario")
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()