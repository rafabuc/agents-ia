#!/usr/bin/env python3
"""
Script de inicio rápido para Project Management Agent
"""

import subprocess
import sys
from pathlib import Path

def run_command(command):
    """Ejecutar comando y mostrar resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            return True
        else:
            print(f"❌ {command}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando {command}: {e}")
        return False

def main():
    print("🚀 Project Management Agent - Quick Start")
    print("=" * 50)
    
    # Verificar Python
    print(f"Python version: {sys.version}")
    
    # Instalar dependencias
    print("\n📦 Instalando dependencias...")
    if run_command("pip install -r requirements-minimal.txt"):
        print("✅ Dependencias instaladas")
    else:
        print("❌ Error instalando dependencias")
        return
    
    # Verificar .env
    if not Path(".env").exists():
        print("\n📝 Creando archivo .env...")
        if Path(".env.example").exists():
            run_command("cp .env.example .env")
        else:
            with open(".env", "w") as f:
                f.write("ANTHROPIC_API_KEY=tu_clave_anthropic_aqui\n")
        
        print("⚠️  Edita .env con tu ANTHROPIC_API_KEY")
    
    # Configurar agente
    print("\n⚙️ Configurando agente...")
    run_command("python main.py setup")
    
    # Probar instalación
    print("\n🧪 Probando instalación...")
    run_command("python main.py test")
    
    print("\n🎉 ¡Listo para usar!")
    print("Ejecuta: python main.py start")

if __name__ == "__main__":
    main()
