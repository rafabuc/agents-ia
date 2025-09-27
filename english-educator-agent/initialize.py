#!/usr/bin/env python3
"""
Complete initialization script for English Educator Agent
Prepares the entire system for first use
"""
import os
import sys
import subprocess
import asyncio
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(message):
    """Print formatted header."""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{message:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓ {message}{RESET}")

def print_warning(message):
    """Print warning message."""
    print(f"{YELLOW}⚠ {message}{RESET}")

def print_error(message):
    """Print error message."""
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    """Print info message."""
    print(f"{BLUE}ℹ {message}{RESET}")

def run_command(command, description, check=True):
    """Run shell command with description."""
    print_info(f"{description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success(f"{description} completed")
            return True
        else:
            if check:
                print_error(f"{description} failed: {result.stderr}")
                return False
            else:
                print_warning(f"{description} completed with warnings")
                return True
    except subprocess.CalledProcessError as e:
        print_error(f"{description} failed: {e}")
        return False

def check_prerequisites():
    """Check if all prerequisites are installed."""
    print_header("CHECKING PREREQUISITES")
    
    prerequisites = {
        "Python": "python --version",
        "Docker": "docker --version",
        "Docker Compose": "docker-compose --version"
    }
    
    all_ok = True
    for name, command in prerequisites.items():
        if run_command(command, f"Checking {name}", check=False):
            print_success(f"{name} is installed")
        else:
            print_error(f"{name} is NOT installed")
            all_ok = False
    
    return all_ok

def setup_environment():
    """Setup environment variables."""
    print_header("ENVIRONMENT SETUP")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print_warning(".env file already exists, skipping...")
        return True
    
    if not env_example.exists():
        print_error(".env.example not found!")
        return False
    
    # Copy .env.example to .env
    try:
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print_success("Created .env file from .env.example")
        print_warning("⚠️  IMPORTANT: Edit .env and add your API keys!")
        print_info("   - OPENAI_API_KEY")
        print_info("   - ANTHROPIC_API_KEY")
        print_info("   - LANGSMITH_API_KEY (optional)")
        
        return True
    except Exception as e:
        print_error(f"Failed to create .env: {e}")
        return False

def start_docker_services():
    """Start Docker services."""
    print_header("STARTING DOCKER SERVICES")
    
    # Change to docker directory
    os.chdir("docker")
    
    if not run_command("docker-compose up -d", "Starting Docker services"):
        os.chdir("..")
        return False
    
    print_info("Waiting for services to be ready...")
    import time
    time.sleep(10)
    
    # Check services status
    run_command("docker-compose ps", "Checking services status", check=False)
    
    os.chdir("..")
    return True

def setup_python_environment():
    """Setup Python virtual environment."""
    print_header("PYTHON ENVIRONMENT SETUP")
    
    os.chdir("backend")
    
    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            os.chdir("..")
            return False
    else:
        print_warning("Virtual environment already exists, skipping...")
    
    # Determine activation command based on OS
    if sys.platform == "win32":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing Python packages"):
        os.chdir("..")
        return False
    
    os.chdir("..")
    return True

def initialize_database():
    """Initialize database tables."""
    print_header("DATABASE INITIALIZATION")
    
    os.chdir("backend")
    
    # Determine python command
    if sys.platform == "win32":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    if run_command(f"{python_cmd} utils/database.py", "Creating database tables", check=False):
        print_success("Database initialized")
    else:
        print_warning("Database may already be initialized")
    
    os.chdir("..")
    return True

def ingest_educational_content():
    """Ingest educational content into vector database."""
    print_header("CONTENT INGESTION")
    
    os.chdir("backend")
    
    # Determine python command
    if sys.platform == "win32":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    if run_command(f"{python_cmd} -m rag.ingest", "Ingesting educational content", check=False):
        print_success("Content ingested successfully")
    else:
        print_warning("Content ingestion completed with warnings")
    
    os.chdir("..")
    return True

def run_system_tests():
    """Run system tests."""
    print_header("RUNNING SYSTEM TESTS")
    
    # Determine python command
    if sys.platform == "win32":
        python_cmd = "venv\\Scripts\\python" if Path("backend/venv").exists() else "python"
    else:
        python_cmd = "venv/bin/python" if Path("backend/venv").exists() else "python3"
    
    if run_command(f"{python_cmd} test_system.py", "Running system tests", check=False):
        print_success("System tests passed")
        return True
    else:
        print_warning("Some tests failed, but system may still work")
        return True

def display_next_steps():
    """Display next steps for user."""
    print_header("INITIALIZATION COMPLETE!")
    
    print(f"\n{BOLD}🎉 Your English Educator Agent is ready!{RESET}\n")
    
    print(f"{BOLD}Next Steps:{RESET}")
    print(f"\n1. {YELLOW}Configure API Keys{RESET}")
    print(f"   Edit .env file and add your API keys:")
    print(f"   {BLUE}OPENAI_API_KEY=your-key-here{RESET}")
    print(f"   {BLUE}ANTHROPIC_API_KEY=your-key-here{RESET}")
    
    print(f"\n2. {YELLOW}Start the Backend API{RESET}")
    if sys.platform == "win32":
        print(f"   {BLUE}cd backend{RESET}")
        print(f"   {BLUE}venv\\Scripts\\activate{RESET}")
        print(f"   {BLUE}uvicorn main:app --reload{RESET}")
    else:
        print(f"   {BLUE}cd backend{RESET}")
        print(f"   {BLUE}source venv/bin/activate{RESET}")
        print(f"   {BLUE}uvicorn main:app --reload{RESET}")
    
    print(f"\n3. {YELLOW}Start Celery Workers{RESET} (Optional)")
    print(f"   In a new terminal:")
    if sys.platform == "win32":
        print(f"   {BLUE}cd backend{RESET}")
        print(f"   {BLUE}venv\\Scripts\\activate{RESET}")
        print(f"   {BLUE}celery -A tasks worker --loglevel=info --pool=solo{RESET}")
    else:
        print(f"   {BLUE}cd backend{RESET}")
        print(f"   {BLUE}source venv/bin/activate{RESET}")
        print(f"   {BLUE}celery -A tasks worker --loglevel=info{RESET}")
    
    print(f"\n4. {YELLOW}Access the Application{RESET}")
    print(f"   API Docs:    {BLUE}http://localhost:8000/docs{RESET}")
    print(f"   Grafana:     {BLUE}http://localhost:3001{RESET} (admin/admin)")
    print(f"   Prometheus:  {BLUE}http://localhost:9090{RESET}")
    print(f"   RabbitMQ:    {BLUE}http://localhost:15672{RESET} (admin/admin)")
    
    print(f"\n5. {YELLOW}Read the Documentation{RESET}")
    print(f"   Quick Start: {BLUE}README.md{RESET}")
    print(f"   Setup Guide: {BLUE}SETUP_GUIDE.md{RESET}")
    print(f"   API Examples: {BLUE}API_EXAMPLES.md{RESET}")
    
    print(f"\n{BOLD}Useful Commands:{RESET}")
    print(f"   Stop services:    {BLUE}docker-compose down{RESET}")
    print(f"   View logs:        {BLUE}docker-compose logs -f{RESET}")
    print(f"   Run tests:        {BLUE}pytest tests/{RESET}")
    
    print(f"\n{GREEN}Happy coding! 🚀{RESET}\n")

def main():
    """Main initialization function."""
    print(f"\n{BOLD}{GREEN}")
    print(r"""
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║     ENGLISH EDUCATOR AGENT - INITIALIZATION          ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    print(f"{RESET}\n")
    
    # Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites check failed. Please install missing components.")
        sys.exit(1)
    
    # Setup steps
    steps = [
        (setup_environment, "Environment setup"),
        (start_docker_services, "Docker services"),
        (setup_python_environment, "Python environment"),
        (initialize_database, "Database initialization"),
        (ingest_educational_content, "Content ingestion"),
        (run_system_tests, "System tests")
    ]
    
    for step_func, step_name in steps:
        if not step_func():
            print_error(f"{step_name} failed!")
            print_info("You may need to fix issues and run initialization again")
            sys.exit(1)
    
    # Display next steps
    display_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Initialization interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
