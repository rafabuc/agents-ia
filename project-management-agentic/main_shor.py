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
from storage.database_manager import DatabaseManager
from utils.logger import logger

console = Console()


class PMPSystem:
    """Main PMP Multi-Agent System class."""
    
    def __init__(self):
        self.agent_factory = AgentFactory()
        self.db_manager = DatabaseManager()
        
        console.print("[green]PMP Multi-Agent System initialized successfully![/green]")
    
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
            agents = self.agent_factory.list_available_agents()
            
            # Create status panels
            db_panel = Panel(
                f"Projects: {stats['projects']['total']}\n"
                f"Chat Sessions: {stats['chat']['sessions']}\n"
                f"Messages: {stats['chat']['messages']}",
                title="Database Status",
                border_style="green"
            )
            
            agent_list = "\n".join([f"- {name}: {desc}" for name, desc in agents.items()])
            agent_panel = Panel(
                agent_list,
                title="Available Agents", 
                border_style="blue"
            )
            
            console.print(db_panel)
            console.print(agent_panel)
            
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
@click.argument('name')
@click.option('--description', default='', help='Project description')
@click.option('--methodology', default='PMP', help='Project methodology')
def create_project(name, description, methodology):
    """Create a new project."""
    try:
        system = PMPSystem()
        project = system.db_manager.create_project(
            name=name,
            description=description,
            methodology=methodology
        )
        
        console.print(f"[green]✓[/green] Project '{name}' created successfully!")
        console.print(f"Project ID: {project.id}")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error creating project: {str(e)}")


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
def demo():
    """Run system demo."""
    try:
        system = PMPSystem()
        
        console.print("[blue]Running PMP System Demo...[/blue]")
        
        # Create a demo project
        project = system.db_manager.create_project(
            name="Demo Project",
            description="A demonstration project",
            methodology="PMP"
        )
        
        console.print(f"[green]✓[/green] Created demo project: {project.name}")
        
        # Show system status
        system.system_status()
        
        console.print("[green]Demo completed successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Demo failed: {str(e)}")


if __name__ == "__main__":
    cli()
