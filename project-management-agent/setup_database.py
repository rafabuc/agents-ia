#!/usr/bin/env python3
"""
Script de configuración para Project Management Agent con Base de Datos
"""

import os
import sqlite3
from pathlib import Path
from database.conversation_db import ConversationDatabase

def setup_database():
    """Configurar base de datos y verificar funcionamiento"""
    
    print("🗄️ Configurando Base de Datos...")
    
    # Crear directorio de datos
    data_dir = Path("./data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Inicializar base de datos
        db = ConversationDatabase()
        
        print("✅ Base de datos inicializada")
        print(f"📁 Ubicación: {db.db_path}")
        
        # Verificar que las tablas se crearon
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'conversation_sessions',
            'conversation_messages', 
            'usage_stats',
            'message_search'
        ]
        
        print(f"\n📋 Tablas creadas:")
        for table in tables:
            status = "✅" if table in expected_tables else "ℹ️"
            print(f"  {status} {table}")
        
        # Verificar funcionalidad básica
        print(f"\n🧪 Probando funcionalidad...")
        
        # Crear sesión de prueba
        test_session_id = db.create_session(
            project_id="test_project",
            name="Test Session",
            tags=["test", "setup"]
        )
        
        # Agregar mensaje de prueba
        db.add_message(
            session_id=test_session_id,
            project_id="test_project",
            role="user",
            content="¿Funciona la base de datos?",
            tokens_used=10
        )
        
        db.add_message(
            session_id=test_session_id,
            project_id="test_project",
            role="assistant",
            content="¡Sí! La base de datos funciona perfectamente.",
            tokens_used=15
        )
        
        # Verificar que se guardó
        sessions = db.get_project_sessions("test_project")
        messages = db.get_session_messages(test_session_id)
        
        if len(sessions) == 1 and len(messages) == 2:
            print("✅ Funcionalidad básica verificada")
            
            # Probar búsqueda
            search_results = db.search_messages("base de datos", "test_project")
            
            if search_results:
                print("✅ Búsqueda full-text funcionando")
            else:
                print("⚠️ Búsqueda full-text no retornó resultados")
            
            # Limpiar datos de prueba
            with sqlite3.connect(db.db_path) as conn:
                conn.execute("DELETE FROM conversation_messages WHERE project_id = 'test_project'")
                conn.execute("DELETE FROM conversation_sessions WHERE project_id = 'test_project'")
                conn.execute("DELETE FROM message_search WHERE project_id = 'test_project'")
                conn.commit()
            
            print("🧹 Datos de prueba limpiados")
            
        else:
            print("❌ Error en funcionalidad básica")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")
        return False

def check_dependencies():
    """Verificar dependencias requeridas"""
    print("📦 Verificando dependencias...")
    
    required_modules = [
        'sqlite3',  # Built-in
        'anthropic',
        'rich',
        'typer',
        'jinja2',
        'pydantic',
        'loguru'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'sqlite3':
                import sqlite3
            else:
                __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️ Módulos faltantes: {', '.join(missing_modules)}")
        print("Instala con: pip install -r requirements.txt")
        return False
    
    return True

def setup_directories():
    """Crear estructura de directorios necesaria"""
    print("📁 Configurando directorios...")
    
    directories = [
        "./data",
        "./data/backups",
        "./logs",
        "./projects",
        "./exports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}")
    
    return True

def create_sample_project():
    """Crear proyecto de ejemplo si no existe ninguno"""
    print("📋 Configurando proyecto de ejemplo...")
    
    projects_dir = Path("./projects")
    
    if not any(projects_dir.iterdir()):
        from datetime import datetime
        import json
        
        project_id = "sample_project_001"
        project_data = {
            'id': project_id,
            'name': 'Proyecto de Ejemplo - Sistema CRM',
            'methodology': 'PMI',
            'type': 'Software Development',
            'description': 'Implementación de sistema CRM para gestión de clientes',
            'created_at': datetime.now().isoformat(),
            'status': 'initiated',
            'phase': 'initiation',
            'documents': {},
            'approvals': {},
            'version_history': []
        }
        
        # Crear directorio del proyecto
        project_path = projects_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Guardar datos del proyecto
        project_file = project_path / "project.json"
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Proyecto de ejemplo creado: {project_id}")
        return True
    
    else:
        print("  ℹ️ Ya existen proyectos, omitiendo ejemplo")
        return True

def main():
    """Configuración completa del sistema"""
    print("🚀 Project Management Agent - Setup con Base de Datos")
    print("=" * 60)
    
    success_steps = []
    
    # Paso 1: Verificar dependencias
    if check_dependencies():
        success_steps.append("✅ Dependencias")
    else:
        print("❌ Faltan dependencias críticas")
        return
    
    # Paso 2: Crear directorios
    if setup_directories():
        success_steps.append("✅ Directorios")
    
    # Paso 3: Configurar base de datos
    if setup_database():
        success_steps.append("✅ Base de Datos")
    else:
        print("❌ Error crítico en base de datos")
        return
    
    # Paso 4: Proyecto de ejemplo
    if create_sample_project():
        success_steps.append("✅ Proyecto Ejemplo")
    
    # Resumen final
    print(f"\n🎉 Setup Completado!")
    print("=" * 40)
    
    for step in success_steps:
        print(f"  {step}")
    
    print(f"\n📋 Próximos pasos:")
    print("1. Configura tu ANTHROPIC_API_KEY en .env")
    print("2. Ejecuta: python main.py start")
    print("3. Usa 'proyectos' para ver el proyecto de ejemplo")
    print("4. Usa 'nueva sesion' para empezar a conversar")
    print("5. Todas las conversaciones se guardan automáticamente")
    
    # Información sobre migración
    conversations_dir = Path("./projects").glob("*/conversations")
    md_files = []
    
    for conv_dir in conversations_dir:
        if conv_dir.exists():
            md_files.extend(conv_dir.glob("*.md"))
    
    if md_files:
        print(f"\n💡 Se encontraron {len(md_files)} archivos de conversación existentes")
        print("   Ejecuta 'python migrate_to_database.py' para migrarlos a la BD")

if __name__ == "__main__":
    main()
