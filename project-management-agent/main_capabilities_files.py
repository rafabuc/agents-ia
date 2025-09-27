#!/usr/bin/env python3
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
    if not settings.claude.api_key :#or settings.claude.api_key == "tu_clave_anthropic_aqui":
        console.print("❌ [red]ANTHROPIC_API_KEY no configurada[/red]")
        console.print("Edita el archivo .env con tu clave API")
        return
    
    console.print("¡Bienvenido al Agente de Gestión de Proyectos!", style="bold green")
    console.print("Escribe 'help' para ver comandos disponibles o 'quit' para salir.\n")
    
    while True:
        try:
            user_input = Prompt.ask("[bold cyan]PM-Agent[/bold cyan]")
            
            if user_input.lower() in ['quit', 'exit', 'salir']:
                console.print("¡Hasta luego! 👋", style="bold yellow")
                break
            elif user_input.lower() == 'help':
                show_help()
            elif user_input.lower()=='proyecto crear':#.startswith('crear proyecto'):
                interactive_create_project()
            elif user_input.lower() == 'proyectos':
                list_projects()
            elif user_input.lower()=='plan generar':#.startswith('generar plan'):
                interactive_generate_plan()
            # Y agregar esta línea en el bucle principal de start(), después de elif user_input.lower() == 'proyectos':
            elif user_input.lower()=='proyecto cargar':#.startswith('cargar proyecto'):
                interactive_load_project()
            #elif user_input.lower().startswith('cargar'):
            #    interactive_load_project()
            elif user_input.lower() == 'proyecto estado':
                show_project_status()    
            # Agregar estos comandos al bucle while True en main.py
            # después de elif user_input.lower().startswith('generar plan'):

            elif user_input.lower()=='guardar conversacion':#.startswith('guardar conversacion') or user_input.lower().startswith('save conversation'):
                save_conversation_command()
            elif user_input.lower()=='listar archivos':#.startswith('listar archivos') or user_input.lower().startswith('list files'):
                list_files_command()
            elif user_input.lower()=='proyecto exportar':#.startswith('exportar proyecto') or user_input.lower().startswith('export project'):
                export_project_command()
            elif user_input.lower()=='plan guardar':#.startswith('guardar plan') or user_input.lower().startswith('save plan'):
                save_plan_command()            
                                        
            # Agregar estos comandos al bucle while True en main.py
            # Comandos guardar conversaciones 
            
            elif user_input.lower()=='chat guardar':#.startswith('guardar conversacion'):
                save_conversation_interactive()
            elif user_input.lower()=='chat cargar':#.startswith('cargar conversacion'):
                load_conversation_interactive()
            elif user_input.lower()=='chat listar':#.startswith('listar conversaciones'):
                list_conversations_command()
            elif user_input.lower()=='chat limpiar':#.startswith('limpiar conversacion'):
                clear_conversation_command()
            elif user_input.lower()=='chat resumir':#.startswith('resumen conversacion'):
                conversation_summary_command()
            elif user_input.lower()=='auto guardar':#.startswith('auto guardar'):
                auto_save_command()
                    
            else:
                # Chat contextual
                response = agent.chat_with_context(user_input)
                
                console.print("\n[bold green]Respuesta:[/bold green]")
                console.print(Markdown(response))
                console.print()
                
        except KeyboardInterrupt:
            console.print("\n¡Hasta luego! 👋", style="bold yellow")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


# Actualizar la función show_help() para incluir nuevos comandos:

def show_help():
    """Mostrar ayuda completa actualizada"""
    help_text = """
## 📖 Comandos Disponibles

### 🚀 Gestión de Proyectos
- `crear proyecto` - Crear nuevo proyecto
- `cargar proyecto` - Cargar proyecto existente
- `proyectos` - Listar todos los proyectos
- `generar plan` - Generar plan de trabajo
- `guardar plan` - Generar y guardar plan de trabajo

### 💬 Gestión de Conversaciones (Base de Datos)
- `nueva sesion` - Iniciar nueva sesión de conversación
- `cargar sesion` - Cargar sesión anterior desde BD
- `sesiones` - Listar todas las sesiones guardadas
- `resumen automatico` - Generar resumen IA de la conversación
- `buscar [término]` - Buscar en todas las conversaciones

### 📊 Analytics y Estadísticas
- `estadisticas` - Ver estadísticas de uso del proyecto
- `exportar [json|markdown|csv]` - Exportar conversación
- `limpiar antiguos` - Archivar sesiones antiguas

### 📁 Gestión de Archivos (Legacy)
- `guardar conversacion` - Guardar como archivo markdown
- `listar archivos` - Ver archivos del proyecto
- `exportar proyecto` - Exportar todo a markdown

### 🛠️ Sistema
- `help` - Mostrar esta ayuda
- `quit/exit/salir` - Salir del agente

### 🤖 Chat Contextual Inteligente
Cada mensaje se guarda automáticamente en la base de datos.
El historial se mantiene entre sesiones.

**Ejemplos de Búsqueda:**
- `buscar project charter` - Buscar discusiones sobre charter
- `buscar riesgo` - Encontrar conversaciones sobre riesgos
- `buscar "pi planning"` - Búsqueda exacta

**Ejemplos de Chat:**
- "¿Qué es un Project Charter en PMI?"
- "Explícame PI Planning en SAFe"
- "¿Cómo gestiono riesgos en este proyecto?"

### 🎯 Workflow Recomendado
1. **Cargar proyecto** existente o crear nuevo
2. **Nueva sesion** para tema específico (opcional)
3. **Conversar** normalmente - todo se guarda automáticamente
4. **Buscar** en conversaciones anteriores cuando necesites
5. **Resumen automatico** al final de sesiones largas
6. **Exportar** documentación importante
    """
    console.print(Markdown(help_text))
    
def show_help__():
    """Mostrar ayuda actualizada"""
    help_text = """
## 📖 Comandos Disponibles

### Gestión de Proyectos
- `crear proyecto` - Crear nuevo proyecto
- `cargar proyecto` - Cargar proyecto existente
- `proyectos` - Listar todos los proyectos
- `generar plan` - Generar plan de trabajo
- `guardar plan` - Generar y guardar plan de trabajo

### Gestión de Conversaciones 💬
- `guardar conversacion` - Guardar chat actual
- `cargar conversacion` - Restaurar chat anterior
- `listar conversaciones` - Ver todas las conversaciones
- `limpiar conversacion` - Limpiar chat (guardando antes)
- `resumen conversacion` - Resumen de la conversación actual
- `auto guardar` - Forzar auto-guardado

### Gestión de Archivos
- `listar archivos` - Ver archivos del proyecto
- `exportar proyecto` - Exportar todo a markdown

### Conversación
- `help` - Mostrar esta ayuda
- `quit/exit/salir` - Salir del agente

### Chat Contextual
Puedes hacer cualquier pregunta sobre metodologías o procesos.
El historial se guarda automáticamente cada 10 mensajes.

**Ejemplos:**
- "¿Qué es un Project Charter en PMI?"
- "Explícame PI Planning en SAFe"
- "¿Cómo gestiono riesgos?"
    """
    console.print(Markdown(help_text))
    
def show_help___():
    """Mostrar ayuda"""
    help_text = """
## 📖 Comandos Disponibles

### Gestión de Proyectos
- `crear proyecto` - Crear nuevo proyecto
- `cargar proyecto` - Cargar proyecto existente
- `proyectos` - Listar todos los proyectos
- `generar plan` - Generar plan de trabajo
- `estado` - Ver estado del proyecto actual

### Conversación
- `help` - Mostrar esta ayuda
- `quit/exit/salir` - Salir del agente

### Chat Contextual
Puedes hacer cualquier pregunta sobre metodologías o procesos.

**Ejemplos:**
- "¿Qué es un Project Charter en PMI?"
- "Explícame PI Planning en SAFe"
- "¿Cómo gestiono riesgos?"

### Comandos de Proyecto
- "Carga el proyecto [ID]" - Cargar proyecto específico
- "¿Qué proyecto tengo activo?" - Ver proyecto actual
    """
    console.print(Markdown(help_text))


# También actualizar la función show_help():

def show_help_v2():
    """Mostrar ayuda"""
    help_text = """
## 📖 Comandos Disponibles

### Gestión de Proyectos
- `crear proyecto` - Crear nuevo proyecto
- `cargar proyecto` - Cargar proyecto existente
- `proyectos` - Listar todos los proyectos
- `generar plan` - Generar plan de trabajo
- `guardar plan` - Generar y guardar plan de trabajo

### Gestión de Archivos
- `guardar conversacion` - Guardar chat actual
- `listar archivos` - Ver archivos del proyecto
- `exportar proyecto` - Exportar todo a markdown

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
    console.print("\n[bold blue]🚀 Crear Nuevo Proyecto[/bold blue]")
    
    project_name = Prompt.ask("Nombre del proyecto")
    project_description = Prompt.ask("Descripción del proyecto")
    
    methodologies = ["PMI", "SAFe", "Hybrid"]
    console.print("\nSelecciona la metodología:")
    for i, method in enumerate(methodologies, 1):
        console.print(f"  {i}. {method}")
    
    method_choice = Prompt.ask("Opción", choices=["1", "2", "3"], default="1")
    methodology = methodologies[int(method_choice) - 1]
    
    project_types = ["Software Development", "Infrastructure", "Business Process", "Other"]
    console.print("\nTipo de proyecto:")
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
        console.print(f"\n✅ [green]Proyecto creado exitosamente: {result['project_id']}[/green]")
    else:
        console.print(f"[red]❌ Error creando proyecto: {result.get('error')}[/red]")

def interactive_generate_plan():
    """Generar plan de trabajo"""
    if not agent.current_project:
        console.print("[yellow]⚠️  No hay proyecto activo. Crea un proyecto primero.[/yellow]")
        return
    
    console.print(f"\n[bold blue]📋 Generando Plan para: {agent.current_project['name']}[/bold blue]")
    
    plan = agent.generate_work_plan()
    console.print("\n[bold green]📋 Plan de Trabajo:[/bold green]")
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
    
    console.print("\n🎉 [green]Configuración completada![/green]")

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

def show_project_status():
    """Mostrar estado del proyecto actual"""
    if not agent.current_project:
        console.print("[yellow]⚠️  No hay proyecto activo[/yellow]")
        console.print("Usa 'proyectos' para ver disponibles y 'cargar proyecto' para activar uno.")
        return
    
    project = agent.current_project
    project_info = f"""
**ID:** {project['id']}
**Nombre:** {project['name']}
**Metodología:** {project['methodology']}
**Tipo:** {project['type']}
**Estado:** {project['status']}
**Fase:** {project.get('phase', 'N/A')}
**Creado:** {project['created_at'][:10]}
    """
    
    console.print(Panel(
        project_info.strip(),
        title=f"📊 Proyecto Activo",
        style="blue"
    ))
    
# Agregar esta función al main.py, después de interactive_create_project()
def interactive_load_project():
    """Cargar proyecto interactivamente"""
    projects = agent.list_projects()
    
    if not projects:
        console.print("[yellow]No hay proyectos disponibles. Crea uno nuevo primero.[/yellow]")
        return
    
    console.print("\n[bold blue]📂 Proyectos Disponibles:[/bold blue]")
    
    table = Table(title="Seleccionar Proyecto")
    table.add_column("Opción", style="cyan", no_wrap=True)
    table.add_column("ID", style="dim")
    table.add_column("Nombre", style="green")
    table.add_column("Metodología", style="blue")
    table.add_column("Estado", style="yellow")
    table.add_column("Creado", style="dim")
    
    for i, project in enumerate(projects, 1):
        table.add_row(
            str(i),
            project['id'],
            project['name'],
            project['methodology'],
            project['status'],
            project['created_at'][:10]
        )
    
    console.print(table)
    
    try:
        choice = Prompt.ask(f"Selecciona proyecto (1-{len(projects)})")
        project_index = int(choice) - 1
        
        if 0 <= project_index < len(projects):
            selected_project = projects[project_index]
            
            console.print(f"\n[bold yellow]Cargando proyecto: {selected_project['name']}[/bold yellow]")
            
            result = agent.load_project(selected_project['id'])
            
            if result['success']:
                console.print(f"✅ [green]Proyecto cargado: {selected_project['name']}[/green]")
                
                # Mostrar información del proyecto
                project_info = f"""
**ID:** {selected_project['id']}
**Nombre:** {selected_project['name']}
**Metodología:** {selected_project['methodology']}
**Estado:** {selected_project['status']}
**Creado:** {selected_project['created_at'][:10]}
                """
                
                console.print(Panel(
                    project_info.strip(),
                    title="📊 Proyecto Activo",
                    style="blue"
                ))
                
                console.print("\n[bold green]¡Ahora puedes usar comandos como 'generar plan'![/bold green]")
            else:
                console.print(f"[red]❌ Error cargando proyecto: {result.get('error')}[/red]")
        else:
            console.print("[red]Selección inválida[/red]")
            
    except (ValueError, IndexError):
        console.print("[red]Selección inválida[/red]")


# Y agregar estas funciones DESPUÉS de las funciones existentes:

def save_conversation_command():
    """Guardar conversación del chat"""
    if not agent.current_project:
        console.print("[yellow]⚠️  No hay proyecto activo. Carga un proyecto primero.[/yellow]")
        return
    
    console.print("[bold blue]💾 Guardando conversación...[/bold blue]")
    
    try:
        result = agent.save_conversation()
        
        if result['success']:
            console.print(f"✅ [green]{result['message']}[/green]")
            console.print(f"📁 Archivo: {result['filename']}")
        else:
            console.print(f"❌ [red]Error: {result['error']}[/red]")
            
    except Exception as e:
        console.print(f"❌ [red]Error guardando conversación: {e}[/red]")

def list_files_command():
    """Listar archivos del proyecto"""
    if not agent.current_project:
        console.print("[yellow]⚠️  No hay proyecto activo. Carga un proyecto primero.[/yellow]")
        return
    
    console.print(f"[bold blue]📁 Archivos del Proyecto: {agent.current_project['name']}[/bold blue]")
    
    try:
        result = agent.list_project_files()
        
        if result['success']:
            files = result['files']
            
            # Documentos
            if files['documents']:
                console.print("\n[bold green]📄 Documentos:[/bold green]")
                for doc in files['documents']:
                    size_kb = doc['size'] / 1024
                    console.print(f"  • {doc['name']} ({size_kb:.1f} KB)")
            
            # Conversaciones
            if files['conversations']:
                console.print("\n[bold yellow]💬 Conversaciones:[/bold yellow]")
                for conv in files['conversations']:
                    size_kb = conv['size'] / 1024
                    console.print(f"  • {conv['name']} ({size_kb:.1f} KB)")
            
            # Exports
            if files['exports']:
                console.print("\n[bold cyan]📦 Exports:[/bold cyan]")
                for exp in files['exports']:
                    size_kb = exp['size'] / 1024
                    console.print(f"  • {exp['name']} ({size_kb:.1f} KB)")
            
            console.print(f"\n[dim]Total de archivos: {result['total_files']}[/dim]")
            
            if result['total_files'] == 0:
                console.print("[yellow]No hay archivos guardados aún.[/yellow]")
        else:
            console.print(f"❌ [red]Error: {result['error']}[/red]")
            
    except Exception as e:
        console.print(f"❌ [red]Error listando archivos: {e}[/red]")

def export_project_command():
    """Exportar proyecto completo"""
    if not agent.current_project:
        console.print("[yellow]⚠️  No hay proyecto activo. Carga un proyecto primero.[/yellow]")
        return
    
    console.print("[bold blue]📦 Exportando proyecto completo...[/bold blue]")
    
    try:
        result = agent.export_project_data()
        
        if result['success']:
            console.print(f"✅ [green]{result['message']}[/green]")
            console.print(f"📁 Archivo: {result['filename']}")
        else:
            console.print(f"❌ [red]Error: {result['error']}[/red]")
            
    except Exception as e:
        console.print(f"❌ [red]Error exportando: {e}[/red]")

def save_plan_command():
    """Generar y guardar plan de trabajo"""
    if not agent.current_project:
        console.print("[yellow]⚠️  No hay proyecto activo. Carga un proyecto primero.[/yellow]")
        return
    
    console.print("[bold blue]📋 Generando y guardando plan de trabajo...[/bold blue]")
    
    try:
        # Generar plan
        plan = agent.generate_work_plan()
        
        # Guardar plan
        result = agent.save_document("plan_trabajo", plan, "work_plan")
        
        if result['success']:
            console.print(f"✅ [green]Plan generado y guardado: {result['filename']}[/green]")
            console.print("\n[bold green]📋 Plan de Trabajo:[/bold green]")
            console.print(Markdown(plan))
        else:
            console.print(f"❌ [red]Error guardando: {result['error']}[/red]")
            console.print("\n[bold green]📋 Plan Generado (no guardado):[/bold green]")
            console.print(Markdown(plan))
            
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")



#################################################################
##################################################################
## Funciones guardado de conversaciones en  archivos

# Y agregar estas funciones después de las existentes:

def save_conversation_interactive():
    """Guardar conversación interactivamente"""
    if not agent.current_project:
        console.print("[yellow]⚠️  No hay proyecto activo. Carga un proyecto primero.[/yellow]")
        return
    
    # Verificar si hay conversación
    if not hasattr(agent.claude_client, 'conversation_history') or not agent.claude_client.conversation_history:
        console.print("[yellow]No hay conversación que guardar.[/yellow]")
        return
    
    message_count = len(agent.claude_client.conversation_history)
    console.print(f"[bold blue]💾 Guardando conversación ({message_count} mensajes)[/bold blue]")
    
    # Pedir nombre de sesión opcional
    session_name = Prompt.ask("Nombre de la sesión (opcional)", default="")
    session_name = session_name.strip() if session_name.strip() else None
    
    try:
        result = agent.save_conversation_history(session_name)
        
        if result['success']:
            console.print(f"✅ [green]{result['message']}[/green]")
            console.print(f"📁 Archivo: {result['filename']}")
            console.print(f"📊 Mensajes guardados: {result['message_count']}")
        else:
            console.print(f"❌ [red]Error: {result['error']}[/red]")
            
    except Exception as e:
        console.print(f"❌ [red]Error guardando conversación: {e}[/red]")

def load_conversation_interactive():
    """Cargar conversación interactivamente"""
    if not agent.current_project:
        console.print("[yellow]⚠️  No hay proyecto activo. Carga un proyecto primero.[/yellow]")
        return
    
    # Listar conversaciones disponibles
    result = agent.list_conversation_sessions()
    
    if not result['success']:
        console.print(f"❌ [red]Error: {result['error']}[/red]")
        return
    
    sessions = result['sessions']
    
    if not sessions:
        console.print("[yellow]No hay conversaciones guardadas.[/yellow]")
        return
    
    console.print("\n[bold blue]💬 Conversaciones Disponibles:[/bold blue]")
    
    table = Table(title="Seleccionar Conversación")
    table.add_column("Opción", style="cyan", no_wrap=True)
    table.add_column("Archivo", style="green")
    table.add_column("Creado", style="blue")
    table.add_column("Tamaño", style="yellow")
    table.add_column("Mensajes", style="magenta")
    
    for i, session in enumerate(sessions, 1):
        table.add_row(
            str(i),
            session['filename'],
            session['created'],
            f"{session['size_kb']} KB",
            str(session['estimated_messages'])
        )
    
    console.print(table)
    
    # Opción para cargar la más reciente
    console.print(f"\n[dim]Presiona Enter para cargar la más reciente[/dim]")
    
    try:
        choice = Prompt.ask(f"Selecciona conversación (1-{len(sessions)} o Enter)", default="1")
        
        if choice.strip() == "":
            choice = "1"
        
        session_index = int(choice) - 1
        
        if 0 <= session_index < len(sessions):
            selected_session = sessions[session_index]
            
            # Advertir sobre pérdida de conversación actual
            current_count = len(agent.claude_client.conversation_history) if hasattr(agent.claude_client, 'conversation_history') else 0
            
            if current_count > 0:
                save_current = Confirm.ask(f"¿Guardar conversación actual ({current_count} mensajes) antes de cargar?", default=True)
                if save_current:
                    agent.save_conversation_history("before_load")
                    console.print("✅ Conversación actual guardada")
            
            console.print(f"\n[bold yellow]📂 Cargando: {selected_session['filename']}[/bold yellow]")
            
            load_result = agent.load_conversation_history(selected_session['filename'])
            
            if load_result['success']:
                console.print(f"✅ [green]{load_result['message']}[/green]")
                console.print(f"📊 Mensajes cargados: {load_result['message_count']}")
                console.print("\n[bold green]¡Conversación restaurada! Puedes continuar donde la dejaste.[/bold green]")
            else:
                console.print(f"❌ [red]Error cargando: {load_result['error']}[/red]")
        else:
            console.print("[red]Selección inválida[/red]")
            
    except (ValueError, IndexError):
        console.print("[red]Selección inválida[/red]")

def list_conversations_command():
    """Listar todas las conversaciones"""
    if not agent.current_project:
        console.print("[yellow]⚠️  No hay proyecto activo. Carga un proyecto primero.[/yellow]")
        return
    
    console.print(f"[bold blue]💬 Conversaciones de: {agent.current_project['name']}[/bold blue]")
    
    try:
        result = agent.list_conversation_sessions()
        
        if result['success']:
            sessions = result['sessions']
            
            if not sessions:
                console.print("[yellow]No hay conversaciones guardadas aún.[/yellow]")
                return
            
            table = Table(title=f"Conversaciones Guardadas ({result['total_sessions']})")
            table.add_column("Archivo", style="green")
            table.add_column("Creado", style="blue")
            table.add_column("Modificado", style="cyan")
            table.add_column("Tamaño", style="yellow")
            table.add_column("Mensajes", style="magenta")
            
            for session in sessions:
                table.add_row(
                    session['filename'],
                    session['created'],
                    session['modified'],
                    f"{session['size_kb']} KB",
                    str(session['estimated_messages'])
                )
            
            console.print(table)
            
            # Mostrar estadísticas
            total_size = sum(s['size_kb'] for s in sessions)
            total_messages = sum(s['estimated_messages'] for s in sessions)
            
            console.print(f"\n[dim]📊 Total: {result['total_sessions']} conversaciones, {total_size:.1f} KB, ~{total_messages} mensajes[/dim]")
            
        else:
            console.print(f"❌ [red]Error: {result['error']}[/red]")
            
    except Exception as e:
        console.print(f"❌ [red]Error listando conversaciones: {e}[/red]")

def clear_conversation_command():
    """Limpiar conversación actual"""
    if not agent.current_project:
        console.print("[yellow]⚠️  No hay proyecto activo. Carga un proyecto primero.[/yellow]")
        return
    
    current_count = len(agent.claude_client.conversation_history) if hasattr(agent.claude_client, 'conversation_history') else 0
    
    if current_count == 0:
        console.print("[yellow]No hay conversación que limpiar.[/yellow]")
        return
    
    console.print(f"[bold yellow]⚠️  Conversación actual: {current_count} mensajes[/bold yellow]")
    
    if Confirm.ask("¿Limpiar conversación? (se guardará automáticamente)", default=False):
        try:
            result = agent.clear_current_conversation()
            
            if result['success']:
                console.print(f"✅ [green]{result['message']}[/green]")
                if result.get('saved_file'):
                    console.print(f"💾 Guardado como: {result['saved_file']}")
            else:
                console.print(f"❌ [red]Error: {result['error']}[/red]")
                
        except Exception as e:
            console.print(f"❌ [red]Error limpiando conversación: {e}[/red]")

def conversation_summary_command():
    """Mostrar resumen de conversación"""
    console.print("[bold blue]📄 Generando resumen de conversación...[/bold blue]")
    
    try:
        summary = agent.get_conversation_summary()
        console.print("\n[bold green]📋 Resumen de la Conversación:[/bold green]")
        console.print(Markdown(summary))
        
    except Exception as e:
        console.print(f"❌ [red]Error generando resumen: {e}[/red]")

def auto_save_command():
    """Ejecutar auto-guardado manual"""
    try:
        result = agent.auto_save_conversation()
        
        if result['success']:
            if 'filename' in result:
                console.print(f"✅ [green]Auto-guardado realizado: {result.get('filename', '')}[/green]")
            else:
                console.print(f"ℹ️ [blue]{result['message']}[/blue]")
        else:
            console.print(f"❌ [red]Error en auto-guardado: {result['error']}[/red]")
            
    except Exception as e:
        console.print(f"❌ [red]Error: {e}[/red]")




if __name__ == "__main__":
    app()
