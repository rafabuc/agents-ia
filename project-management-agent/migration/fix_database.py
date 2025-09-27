# migration/fix_database.py
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from loguru import logger

def migrate_database(db_path: str):
    """Migrar base de datos existente para corregir problemas de schema"""
    
    db_file = Path(db_path)
    if not db_file.exists():
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    # Crear backup
    backup_path = db_file.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    shutil.copy2(db_file, backup_path)
    print(f"💾 Backup creado: {backup_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Verificar si la tabla usage_stats ya tiene la restricción UNIQUE
            cursor = conn.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='usage_stats'
            """)
            table_sql = cursor.fetchone()
            
            if table_sql and "UNIQUE(project_id, session_id, date)" not in table_sql[0]:
                print("🔧 Aplicando migración a usage_stats...")
                
                # 1. Crear nueva tabla con la restricción correcta
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS usage_stats_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        project_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        messages_count INTEGER DEFAULT 0,
                        tokens_used INTEGER DEFAULT 0,
                        api_calls INTEGER DEFAULT 0,
                        cost_estimate REAL DEFAULT 0.0,
                        UNIQUE(project_id, session_id, date)
                    )
                """)
                
                # 2. Migrar datos eliminando duplicados
                conn.execute("""
                    INSERT OR IGNORE INTO usage_stats_new 
                    SELECT * FROM usage_stats
                """)
                
                # 3. Eliminar tabla antigua
                conn.execute("DROP TABLE usage_stats")
                
                # 4. Renombrar nueva tabla
                conn.execute("ALTER TABLE usage_stats_new RENAME TO usage_stats")
                
                # 5. Recrear índices
                conn.execute("CREATE INDEX IF NOT EXISTS idx_project_date ON usage_stats (project_id, date)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_session_date ON usage_stats (session_id, date)")
                
                print("✅ Migración de usage_stats completada")
            else:
                print("ℹ️ usage_stats ya tiene la estructura correcta")
            
            # Verificar otras tablas y crear índices faltantes
            print("🔍 Verificando índices...")
            
            required_indexes = [
                ("idx_session_order", "conversation_messages", "(session_id, message_order)"),
                ("idx_project_timestamp", "conversation_messages", "(project_id, timestamp)"),
                ("idx_role_timestamp", "conversation_messages", "(role, timestamp)"),
                ("idx_session_status", "conversation_sessions", "(status)"),
                ("idx_project_date", "usage_stats", "(project_id, date)"),
                ("idx_session_date", "usage_stats", "(session_id, date)")
            ]
            
            for idx_name, table_name, columns in required_indexes:
                try:
                    conn.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} {columns}")
                    print(f"✅ Índice {idx_name} verificado/creado")
                except Exception as e:
                    print(f"⚠️ Error creando índice {idx_name}: {e}")
            
            # Verificar integridad de datos
            print("🔍 Verificando integridad de datos...")
            
            # Contar registros
            tables_info = {}
            for table in ['conversation_sessions', 'conversation_messages', 'usage_stats']:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                tables_info[table] = count
                print(f"📊 {table}: {count} registros")
            
            # Verificar consistencia
            cursor = conn.execute("""
                SELECT COUNT(*) FROM conversation_messages cm
                LEFT JOIN conversation_sessions cs ON cm.session_id = cs.id
                WHERE cs.id IS NULL
            """)
            orphan_messages = cursor.fetchone()[0]
            
            if orphan_messages > 0:
                print(f"⚠️ Encontrados {orphan_messages} mensajes huérfanos")
            else:
                print("✅ Integridad referencial verificada")
            
            conn.commit()
            
        print("🎉 Migración completada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        
        # Restaurar backup en caso de error
        if backup_path.exists():
            shutil.copy2(backup_path, db_file)
            print(f"🔄 Base de datos restaurada desde backup")
        
        return False

def main():
    """Script principal de migración"""
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python fix_database.py <ruta_a_base_de_datos>")
        print("Ejemplo: python fix_database.py ./data/conversations.db")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    print("🔧 SCRIPT DE MIGRACIÓN DE BASE DE DATOS")
    print("=" * 50)
    print(f"📁 Base de datos: {db_path}")
    
    if migrate_database(db_path):
        print("\n✅ Migración exitosa. La base de datos está lista para usar.")
        sys.exit(0)
    else:
        print("\n❌ Migración fallida. Revisar errores.")
        sys.exit(1)

if __name__ == "__main__":
    main()