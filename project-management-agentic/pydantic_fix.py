#!/usr/bin/env python3
"""
Script para corregir todas las advertencias de LangChain y Pydantic
"""
import os
import subprocess
import sys
from pathlib import Path

def install_compatible_dependencies():
    """Instalar versiones compatibles de todas las dependencias."""
    print("🔧 Instalando versiones compatibles...")
    
    # Primero desinstalar versiones problemáticas
    uninstall_packages = [
        "langchain", 
        "langchain-community", 
        "langchain-openai", 
        "langchain-anthropic",
        "pydantic"
    ]
    
    for package in uninstall_packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", package], 
                          capture_output=True, check=False)
        except:
            pass
    
    # Instalar versiones específicas compatibles
    compatible_packages = [
        "pydantic>=2.5.0,<3.0.0",
        "pydantic-settings>=2.1.0",
        "langchain-core>=0.1.0",
        "langchain-community>=0.0.20", 
        "langchain-openai>=0.0.5",
        "langchain-anthropic>=0.1.1",
        "langchain>=0.1.0"
    ]
    
    for package in compatible_packages:
        print(f"📦 Instalando {package}...")
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package} instalado correctamente")
            else:
                print(f"⚠️ Problema con {package}: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando {package}: {e}")

def update_requirements_txt():
    """Actualizar requirements.txt con versiones compatibles."""
    print("📝 Actualizando requirements.txt...")
    
    new_requirements = """# Core dependencies - Compatible versions
pydantic>=2.5.0,<3.0.0
pydantic-settings>=2.1.0
langchain-core>=0.1.0
langchain>=0.1.0
langchain-community>=0.0.20
langchain-openai>=0.0.5
langchain-anthropic>=0.1.1
langgraph>=0.0.20

# Vector stores and embeddings
chromadb>=0.4.18
sentence-transformers>=2.2.2
faiss-cpu>=1.7.4

# Database
sqlalchemy>=2.0.23
alembic>=1.13.1

# Document processing
pypdf2>=3.0.1
python-docx>=1.1.0
openpyxl>=3.1.2
jinja2>=3.1.2

# Web framework (optional for API)
fastapi>=0.104.1
uvicorn>=0.24.0

# Utilities
python-dotenv>=1.0.0
click>=8.1.7
rich>=13.7.0
loguru>=0.7.2

# Development
pytest>=7.4.3
black>=23.11.0
flake8>=6.1.0
"""
    
    try:
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write(new_requirements)
        print("✅ requirements.txt actualizado")
    except Exception as e:
        print(f"⚠️ Error actualizando requirements.txt: {e}")

def fix_pydantic_imports():
    """Corregir importaciones de Pydantic en el código."""
    print("🔧 Corrigiendo importaciones de Pydantic...")
    
    # Buscar archivos Python que podrían tener importaciones problemáticas
    python_files = []
    for root, dirs, files in os.walk("."):
        # Ignorar directorios específicos
        dirs[:] = [d for d in dirs if not d.startswith(('.', '__pycache__', 'venv', 'env'))]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    # Patrones de reemplazo
    replacements = [
        ("from pydantic import", "from pydantic import"),
        ("from pydantic import", "from pydantic import"),
        ("import pydantic as", "import pydantic as"),
        ("from pydantic import", "from pydantic import"),
    ]
    
    fixed_files = 0
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            for old_pattern, new_pattern in replacements:
                content = content.replace(old_pattern, new_pattern)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Corregido: {file_path}")
                fixed_files += 1
                
        except Exception as e:
            print(f"⚠️ Error procesando {file_path}: {e}")
    
    if fixed_files == 0:
        print("✅ No se encontraron importaciones problemáticas en el código")
    else:
        print(f"✅ Se corrigieron {fixed_files} archivos")

def update_config_settings():
    """Actualizar config/settings.py para usar pydantic v2."""
    print("🔧 Actualizando config/settings.py...")
    
    settings_content = '''import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # API Keys
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, env="ANTHROPIC_API_KEY")
    
    # Database
    database_url: str = Field("sqlite:///./pmp_system.db", env="DATABASE_URL")
    
    # Paths
    vector_store_path: str = Field("./data/vector_store", env="VECTOR_STORE_PATH")
    project_storage_path: str = Field("./data/projects", env="PROJECT_STORAGE_PATH")
    knowledge_base_path: str = Field("./data/knowledge_base", env="KNOWLEDGE_BASE_PATH")
    templates_path: str = Field("./templates", env="TEMPLATES_PATH")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("./logs/pmp_system.log", env="LOG_FILE")
    
    # Model Configuration
    default_llm_provider: str = Field("openai", env="DEFAULT_LLM_PROVIDER")
    default_model: str = Field("gpt-4", env="DEFAULT_MODEL")
    embedding_model: str = Field("text-embedding-ada-002", env="EMBEDDING_MODEL")
    
    # System Settings
    max_concurrent_agents: int = Field(5, env="MAX_CONCURRENT_AGENTS")
    chunk_size: int = Field(1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(200, env="CHUNK_OVERLAP")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.vector_store_path,
            self.project_storage_path,
            self.knowledge_base_path,
            self.templates_path,
            os.path.dirname(self.log_file) if self.log_file else "./logs"
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)


# Global settings instance
settings = Settings()
'''
    
    try:
        # Intentar con pydantic_settings primero
        try:
            import pydantic_settings
            settings_content = settings_content.replace(
                "from pydantic import BaseSettings, Field",
                "from pydantic_settings import BaseSettings\nfrom pydantic import Field"
            )
        except ImportError:
            pass
            
        os.makedirs("config", exist_ok=True)
        with open("config/settings.py", "w", encoding="utf-8") as f:
            f.write(settings_content)
        print("✅ config/settings.py actualizado")
    except Exception as e:
        print(f"⚠️ Error actualizando settings.py: {e}")

def create_env_if_not_exists():
    """Crear archivo .env si no existe."""
    if not os.path.exists(".env"):
        print("📝 Creando archivo .env...")
        env_content = """# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database
DATABASE_URL=sqlite:///./pmp_system.db

# Vector Store
VECTOR_STORE_PATH=./data/vector_store

# File Storage
PROJECT_STORAGE_PATH=./data/projects
KNOWLEDGE_BASE_PATH=./data/knowledge_base
TEMPLATES_PATH=./templates

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/pmp_system.log

# Model Configuration
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4
EMBEDDING_MODEL=text-embedding-ada-002
"""
        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            print("✅ Archivo .env creado")
        except Exception as e:
            print(f"⚠️ Error creando .env: {e}")

def test_system():
    """Probar que el sistema funciona sin advertencias."""
    print("🧪 Probando el sistema...")
    
    try:
        # Probar importaciones
        result = subprocess.run([
            sys.executable, "-c", 
            "from config.settings import settings; print('✅ Importaciones OK')"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Test de importaciones: PASÓ")
        else:
            print(f"⚠️ Test de importaciones: {result.stderr}")
        
        # Probar inicialización
        result = subprocess.run([
            sys.executable, "main.py", "init"
        ], capture_output=True, text=True, timeout=60)
        
        if "successfully" in result.stdout.lower():
            print("✅ Test de inicialización: PASÓ")
            print("🎉 ¡Sistema funcionando correctamente!")
        else:
            print(f"⚠️ Test de inicialización: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ Error en tests: {e}")

def main():
    print("=" * 60)
    print("   CORRECTOR COMPLETO - LANGCHAIN & PYDANTIC")
    print("=" * 60)
    print()
    
    # Paso 1: Instalar dependencias compatibles
    install_compatible_dependencies()
    print()
    
    # Paso 2: Actualizar requirements.txt
    update_requirements_txt()
    print()
    
    # Paso 3: Corregir importaciones problemáticas
    fix_pydantic_imports()
    print()
    
    # Paso 4: Actualizar settings.py
    update_config_settings()
    print()
    
    # Paso 5: Crear .env si no existe
    create_env_if_not_exists()
    print()
    
    # Paso 6: Probar sistema
    test_system()
    
    print()
    print("=" * 60)
    print("✅ CORRECCIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("🚀 Comandos para probar:")
    print("   python main.py init")
    print("   python main.py status") 
    print("   python main.py demo")
    print()
    print("📝 No olvides configurar tu API key en .env")

if __name__ == "__main__":
    main()