#!/usr/bin/env python3
"""
Script para verificar y arreglar el modelo de Claude
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_and_fix_model():
    """Verificar y corregir modelo de Claude"""
    
    print("🔍 Verificando configuración del modelo Claude...")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Modelos disponibles actuales
    available_models = [
        "claude-3-5-sonnet-20241022",  # Recomendado
        "claude-3-5-sonnet-20240620", 
        "claude-3-haiku-20240307",
        "claude-3-opus-20240229"
    ]
    
    recommended_model = "claude-3-5-sonnet-20241022"
    
    # Verificar archivo .env
    env_file = Path(".env")
    claude_model = os.getenv("CLAUDE_MODEL")
    
    if claude_model:
        print(f"📋 Modelo en .env: {claude_model}")
        if claude_model in available_models:
            print("✅ Modelo válido en .env")
            return True
        else:
            print(f"❌ Modelo en .env no válido: {claude_model}")
    else:
        print("📋 No hay CLAUDE_MODEL en .env")
    
    # Verificar archivo config/settings.py
    settings_file = Path("config/settings.py")
    if settings_file.exists():
        content = settings_file.read_text()
        
        # Buscar modelo hardcoded obsoleto
        if "claude-3-sonnet-20240229" in content:
            print("❌ Modelo obsoleto encontrado en config/settings.py")
            
            # Ofrecer arreglo automático
            fix = input("¿Arreglar automáticamente? (y/N): ").lower()
            if fix == 'y':
                # Reemplazar modelo obsoleto
                new_content = content.replace(
                    '"claude-3-sonnet-20240229"',
                    f'"{recommended_model}"'
                )
                new_content = new_content.replace(
                    "'claude-3-sonnet-20240229'",
                    f"'{recommended_model}'"
                )
                
                settings_file.write_text(new_content)
                print(f"✅ Modelo actualizado a {recommended_model} en config/settings.py")
                return True
            else:
                print("⚠️  Actualiza manualmente el modelo en config/settings.py")
                return False
        else:
            print("✅ No se encontró modelo obsoleto en config/settings.py")
    
    # Agregar modelo a .env si no existe
    if not claude_model:
        print(f"➕ Agregando CLAUDE_MODEL={recommended_model} a .env")
        
        with open(env_file, "a") as f:
            f.write(f"\n# Modelo Claude actualizado\n")
            f.write(f"CLAUDE_MODEL={recommended_model}\n")
        
        print("✅ Modelo agregado a .env")
    
    return True

def test_model():
    """Probar conexión con modelo"""
    try:
        print("\n🧪 Probando conexión con Claude...")
        
        from anthropic import Anthropic
        load_dotenv()
        
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")
        
        if not api_key or api_key == "tu_clave_anthropic_aqui":
            print("❌ API key no configurada")
            return False
        
        client = Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": "Di solo: Conexión exitosa"}]
        )
        
        result = response.content[0].text
        print(f"✅ Respuesta de Claude: {result}")
        print(f"✅ Modelo funcionando: {model}")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        if "404" in str(e) or "not_found" in str(e):
            print("💡 El modelo especificado no existe. Verifica el nombre.")
        return False

def show_model_info():
    """Mostrar información de modelos disponibles"""
    
    models_info = {
        "claude-3-5-sonnet-20241022": {
            "name": "Claude 3.5 Sonnet (Latest)",
            "description": "Más reciente, balance perfecto",
            "cost": "Medio (~$3/$15 per 1M tokens)",
            "speed": "Rápido",
            "recommended": "⭐ RECOMENDADO"
        },
        "claude-3-haiku-20240307": {
            "name": "Claude 3 Haiku", 
            "description": "Rápido y económico",
            "cost": "Bajo (~$0.25/$1.25 per 1M tokens)",
            "speed": "Muy rápido",
            "recommended": "💰 Para pruebas"
        },
        "claude-3-opus-20240229": {
            "name": "Claude 3 Opus",
            "description": "Más potente",
            "cost": "Alto (~$15/$75 per 1M tokens)", 
            "speed": "Lento",
            "recommended": "🧠 Para tareas complejas"
        }
    }
    
    print("\n📊 Modelos Claude Disponibles:")
    print("=" * 60)
    
    for model_id, info in models_info.items():
        print(f"\n🤖 {info['name']}")
        print(f"   ID: {model_id}")
        print(f"   Descripción: {info['description']}")
        print(f"   Costo: {info['cost']}")
        print(f"   Velocidad: {info['speed']}")
        print(f"   Recomendación: {info['recommended']}")

def main():
    """Función principal"""
    print("🚀 Project Management Agent - Model Checker")
    print("=" * 50)
    
    # Verificar y arreglar modelo
    if check_and_fix_model():
        print("\n✅ Configuración de modelo corregida")
        
        # Probar conexión
        if test_model():
            print("\n🎉 ¡Todo funcionando correctamente!")
        else:
            print("\n❌ Hay problemas de conexión")
            print("\n🔑 Verifica tu ANTHROPIC_API_KEY en .env")
    else:
        print("\n❌ No se pudo corregir la configuración")
        print("Arregla manualmente config/settings.py")
    
    # Mostrar información de modelos
    show_info = input("\n¿Ver información de modelos disponibles? (y/N): ").lower()
    if show_info == 'y':
        show_model_info()

if __name__ == "__main__":
    main()
