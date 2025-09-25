# main.py
"""
PMP Multi-Agent System
Main application entry point
"""

import os
import sys
import asyncio
from typing import Dict, Any, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.database import init_database
from config.settings import settings
from agents.agent_factory import AgentFactory
from workflows.workflow_manager import WorkflowManager
from rag.retriever import RAGRetriever
from storage.database_manager import DatabaseManager
from utils.logger import logger

console = Console()


class PMPSystem:
    """Main PMP Multi-Agent System class."""
    
    def __init__(self):
        self.workflow_manager = WorkflowManager()
        self.agent_factory = AgentFactory()
        self.rag_retriever = RAGRetriever()
        self.db_manager = DatabaseManager()
        
        console.print("[green]PMP Multi-Agent System initialized successfully![/green]")
    
    async def create_project(self, name: str, description: str = "", 
                           methodology: str = "PMP") -> Dict[str, Any]:
        """Create a new project using the complete workflow."""
        try:
            result = self.workflow_manager.create_project_complete(
                project_name=name,
                description=description,
                methodology=methodology
            )
            
            if result.get("success"):
                console.print(f"[green]✓[/green] Project '{name}' created successfully!")
                console.print(f"Project ID: {result.get('project_id')}")
            else:
                console.print(f"[red]✗[/red] Error creating project: {result.get('error')}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error creating project: {str(e)}"
            console.print(f"[red]✗[/red] {error_msg}")
            return {"success": False, "error": error_msg}
    
    async def analyze_costs(self, project_id: int, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze project costs using cost analysis workflow."""
        try:
            result = self.workflow_manager.analyze_project_costs(
                project_id=project_id,
                analysis_type=analysis_type
            )
            
            if result.get("success"):
                console.print(f"[green]✓[/green] Cost analysis completed for project {project_id}")
            else:
                console.print(f"[red]✗[/red] Error in cost analysis: {result.get('error')}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error analyzing costs: {str(e)}"
            console.print(f"[red]✗[/red] {error_msg}")
            return {"success": False, "error": error_msg}
    
    async def chat(self, message: str, agent_type: str = "auto", 
                  project_id: Optional[int] = None) -> Dict[str, Any]:
        """Interactive chat with agents."""
        try:
            if agent_type == "auto":
                # Use workflow manager for intelligent routing
                result = self.workflow_manager.custom_workflow(
                    input_text=message,
                    project_id=project_id
                )
            else:
                # Use specific agent
                agent = self.agent_factory.create_agent(agent_type)
                result = agent.process(message)
            
            if result.get("success", True):
                response = result.get("response", "No response generated")
                console.print(f"[blue]Assistant:[/blue] {response}")
            else:
                console.print(f"[red]Error:[/red] {result.get('error')}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error in chat: {str(e)}"
            console.print(f"[red]✗[/red] {error_msg}")
            return {"success": False, "error": error_msg}
    
    def list_projects(self, limit: int = 10) -> None:
        """List recent projects."""
        try:
            projects = self.db_manager.list_projects(limit=limit)
            
            if not projects:
                console.print("[yellow]No projects found.[/yellow]")
                return
            
            table = Table(title="Recent Projects")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("Methodology")
            table.add_column("Created", style="blue")
            
            for project in projects:
                table.add_row(
                    str(project.id),
                    project.name,
                    project.status.value,
                    project.methodology,
                    project.created_at.strftime("%Y-%m-%d")
                )
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error listing projects: {str(e)}[/red]")
    
    def system_status(self) -> None:
        """Display system status."""
        try:
            stats = self.db_manager.get_system_stats()
            rag_stats = self.rag_retriever.get_stats()
            
            # Create status panels
            db_panel = Panel(
                f"Projects: {stats['projects']['total']}\n"
                f"Documents: {stats['documents']['total']}\n"
                f"Chat Sessions: {stats['chat']['sessions']}\n"
                f"Messages: {stats['chat']['messages']}",
                title="Database Status",
                border_style="green"
            )
            
            rag_panel = Panel(
                f"Documents: {rag_stats.get('vector_store', {}).get('document_count', 'N/A')}\n"
                f"Chunk Size: {rag_stats.get('chunk_size', 'N/A')}\n"
                f"Model: {rag_stats.get('embedding_model', 'N/A')}",
                title="RAG System Status", 
                border_style="blue"
            )
            
            console.print(db_panel)
            console.print(rag_panel)
            
        except Exception as e:
            console.print(f"[red]Error getting system status: {str(e)}[/red]")


# CLI Commands
@click.group()
def cli():
    """PMP Multi-Agent System CLI"""
    pass


@cli.command()
def init():
    """Initialize the system (create database tables)."""
    try:
        init_database()
        console.print("[green]✓[/green] Database initialized successfully!")
    except Exception as e:
        console.print(f"[red]✗[/red] Error initializing database: {str(e)}")


@cli.command()
@click.option('--path', default=None, help='Path to knowledge base directory')
def ingest_kb(path):
    """Ingest knowledge base documents."""
    try:
        system = PMPSystem()
        kb_path = path or settings.knowledge_base_path
        
        console.print(f"[blue]Ingesting knowledge base from: {kb_path}[/blue]")
        system.rag_retriever.ingest_knowledge_base(kb_path)
        console.print("[green]✓[/green] Knowledge base ingested successfully!")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error ingesting knowledge base: {str(e)}")


@cli.command()
@click.argument('name')
@click.option('--description', default='', help='Project description')
@click.option('--methodology', default='PMP', help='Project methodology')
def create_project(name, description, methodology):
    """Create a new project."""
    async def _create():
        system = PMPSystem()
        await system.create_project(name, description, methodology)
    
    asyncio.run(_create())


@cli.command()
@click.argument('project_id', type=int)
@click.option('--type', 'analysis_type', default='comprehensive', help='Analysis type')
def analyze_costs(project_id, analysis_type):
    """Analyze project costs."""
    async def _analyze():
        system = PMPSystem()
        await system.analyze_costs(project_id, analysis_type)
    
    asyncio.run(_analyze())


@cli.command()
@click.option('--limit', default=10, help='Number of projects to show')
def list_projects(limit):
    """List recent projects."""
    system = PMPSystem()
    system.list_projects(limit)


@cli.command()
def status():
    """Show system status."""
    system = PMPSystem()
    system.system_status()


@cli.command()
@click.option('--agent', default='auto', help='Agent type (auto, pmp_project, cost_budget, template)')
@click.option('--project-id', type=int, help='Project ID for context')
def chat(agent, project_id):
    """Start interactive chat session."""
    async def _chat():
        system = PMPSystem()
        
        console.print("[green]PMP Assistant Chat - Type 'quit' to exit[/green]")
        console.print(f"Agent: {agent}")
        if project_id:
            console.print(f"Project Context: {project_id}")
        
        while True:
            try:
                message = console.input("\n[bold blue]You:[/bold blue] ")
                
                if message.lower() in ['quit', 'exit', 'bye']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if message.strip():
                    await system.chat(message, agent, project_id)
                    
            except KeyboardInterrupt:
                console.print("\n[yellow]Chat session ended.[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
    
    asyncio.run(_chat())


if __name__ == "__main__":
    cli()