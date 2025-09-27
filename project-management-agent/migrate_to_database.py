#!/usr/bin/env python3
"""
Script para migrar conversaciones existentes de archivos markdown a base de datos
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from database.conversation_db import ConversationDatabase
from core.agent import ProjectManagementAgent

def migrate_markdown_conversations():
    """Migrar conversaciones de archivos markdown a base de datos"""
    
    print("🔄 Migrando conversaciones a base de datos...")
    
    # Inicializar agente y BD
    agent = ProjectManagementAgent()
    db = ConversationDatabase()
    
    projects_path = Path("./projects")
    
    if not projects_path.exists():
        print("❌ No se encontró directorio de proyectos")
        return
    
    migrated_count = 0
    
    for project_dir in projects_path.iterdir():
        if not project_dir.is_dir():
            continue
        
        print(f"\n📂 Procesando proyecto: {project_dir.name}")
        
        # Cargar información del proyecto
        project_file = project_dir / "project.json"
        if not project_file.exists():
            print(f"  ⚠️ No se encontró project.json")
            continue
        
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        project_id = project_data['id']
        
        # Buscar archivos de conversación
        conversations_dirs = [
            project_dir / "conversations",
            project_dir / "documents"  # Por si están en documents
        ]
        
        for conv_dir in conversations_dirs:
            if not conv_dir.exists():
                continue
            
            for conv_file in conv_dir.glob("*.md"):
                print(f"  📄 Migrando: {conv_file.name}")
                
                try:
                    # Leer archivo markdown
                    with open(conv_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Parsear conversación
                    messages = parse_markdown_conversation(content)
                    
                    if not messages:
                        print(f"    ⚠️ No se encontraron mensajes válidos")
                        continue
                    
                    # Crear sesión en BD
                    session_name = conv_file.stem.replace('_', ' ').title()
                    session_id = db.create_session(
                        project_id=project_id,
                        name=session_name,
                        tags=['migrated', 'markdown']
                    )
                    
                    # Migrar mensajes
                    for msg in messages:
                        db.add_message(
                            session_id=session_id,
                            project_id=project_id,
                            role=msg['role'],
                            content=msg['content'],
                            tokens_used=estimate_tokens(msg['content'])
                        )
                    
                    print(f"    ✅ {len(messages)} mensajes migrados")
                    migrated_count += 1
                    
                    # Renombrar archivo original para evitar re-migración
                    backup_file = conv_file.with_suffix('.md.migrated')
                    conv_file.rename(backup_file)
                    
                except Exception as e:
                    print(f"    ❌ Error migrando {conv_file.name}: {e}")
    
    print(f"\n🎉 Migración completada: {migrated_count} conversaciones migradas")

def parse_markdown_conversation(content: str) -> list:
    """Parsear conversación desde markdown"""
    messages = []
    
    # Patrones para identificar mensajes
    patterns = [
        r'### \*\*(Usuario|Agente)\*\* \(Mensaje \d+\)\n\n(.*?)(?=### \*\*|$)',
        r'### (👤|🤖) (Usuario|Agente) \(Mensaje \d+\)\n.*?\n\n(.*?)(?=### |$)',
        r'\*\*(Usuario|Agente):\*\*(.*?)(?=\*\*|$)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        
        if matches:
            for match in matches:
                if len(match) >= 2:
                    role_text = match[0].lower()
                    role = 'user' if 'usuario' in role_text else 'assistant'
                    content_text = match[-1].strip()
                    
                    if content_text and len(content_text) > 10:  # Filtrar contenido muy corto
                        messages.append({
                            'role': role,
                            'content': content_text
                        })
            break  # Si encontramos mensajes con un patrón, no probar otros
    
    return messages

def estimate_tokens(text: str) -> int:
    """Estimar tokens aproximadamente"""
    return len(text.split()) + len(text) // 4

def verify_migration():
    """Verificar que la migración fue exitosa"""
    print("\n🔍 Verificando migración...")
    
    db = ConversationDatabase()
    
    # Obtener estadísticas de la BD
    with db._get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM conversation_sessions")
        total_sessions = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM conversation_messages")
        total_messages = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT project_id, COUNT(*) as sessions FROM conversation_sessions GROUP BY project_id")
        by_project = cursor.fetchall()
    
    print(f"📊 Estadísticas de migración:")
    print(f"  • Total de sesiones: {total_sessions}")
    print(f"  • Total de mensajes: {total_messages}")
    print(f"  • Promedio de mensajes por sesión: {total_messages/max(total_sessions, 1):.1f}")
    
    print(f"\n📋 Por proyecto:")
    for project_id, session_count in by_project:
        print(f"  • {project_id}: {session_count} sesiones")
    
    # Verificar integridad
    cursor = conn.execute("""
        SELECT s.name, COUNT(m.id) as message_count
        FROM conversation_sessions s
        LEFT JOIN conversation_messages m ON s.id = m.session_id
        GROUP BY s.id
        ORDER BY message_count DESC
        LIMIT 5
    """)
    
    top_sessions = cursor.fetchall()
    
    print(f"\n🏆 Top 5 sesiones con más mensajes:")
    for session_name, msg_count in top_sessions:
        print(f"  • {session_name}: {msg_count} mensajes")

def create_database_backup():
    """Crear backup de la base de datos"""
    import shutil
    from datetime import datetime
    
    db_path = Path("./data/conversations.db")
    
    if db_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = db_path.parent / f"conversations_backup_{timestamp}.db"
        
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup creado: {backup_path}")
        return backup_path
    
    return None

def main():
    """Función principal de migración"""
    print("🚀 Migración de Conversaciones a Base de Datos")
    print("=" * 60)
    
    # Verificar si ya existe BD
    db_path = Path("./data/conversations.db")
    if db_path.exists():
        from datetime import datetime
        modified_time = datetime.fromtimestamp(db_path.stat().st_mtime)
        print(f"⚠️  Base de datos existente encontrada (modificada: {modified_time})")
        
        overwrite = input("¿Continuar con la migración? Los datos existentes se conservarán (y/N): ")
        if overwrite.lower() != 'y':
            print("❌ Migración cancelada")
            return
    
    # Crear backup si existe BD
    backup_path = create_database_backup()
    
    try:
        # Ejecutar migración
        migrate_markdown_conversations()
        
        # Verificar resultados
        verify_migration()
        
        print("\n✅ Migración completada exitosamente")
        print("\n📋 Próximos pasos:")
        print("1. Ejecuta: python main.py start")
        print("2. Usa comando: sesiones")
        print("3. Usa comando: buscar [término]")
        print("4. Los archivos .md originales fueron renombrados a .md.migrated")
        
        if backup_path:
            print(f"5. Backup disponible en: {backup_path}")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        
        if backup_path:
            print(f"💾 Backup disponible para restaurar: {backup_path}")

if __name__ == "__main__":
    main()
