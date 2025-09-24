# run_tests.py
#!/usr/bin/env python3
"""
Script para ejecutar tests del sistema
"""
import subprocess
import sys
import os


def run_tests():
    """Ejecutar todos los tests."""
    print("=== Ejecutando Tests PMP Multi-Agent System ===\n")
    
    # Verificar que pytest está instalado
    try:
        import pytest
    except ImportError:
        print("Error: pytest no está instalado")
        print("Instalar con: pip install pytest")
        sys.exit(1)
    
    # Ejecutar tests
    test_commands = [
        "python -m pytest tests/ -v",
        "python -m pytest tests/test_agents.py -v",
        "python -m pytest tests/test_workflows.py -v", 
        "python -m pytest tests/test_storage.py -v"
    ]
    
    for cmd in test_commands:
        print(f"Ejecutando: {cmd}")
        result = subprocess.run(cmd, shell=True)
        if result.returncode != 0:
            print(f"⚠️  Algunos tests fallaron en: {cmd}")
        else:
            print(f"✓ Tests exitosos: {cmd}")
        print("-" * 50)


if __name__ == "__main__":
    run_tests()