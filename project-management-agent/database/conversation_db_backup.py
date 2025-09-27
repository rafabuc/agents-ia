# database/conversation_db.py
import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger

@dataclass
class ConversationMessage:
    """Estructura de mensaje de conversación"""
    id: str
    session_id: str
    project_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    metadata: Optional[Dict] = None

@dataclass
class ConversationSession:
    """Estructura de sesión de conversación"""
    id: str
    project_id: str
    name: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    total_tokens: int
    status: str  # 'active', 'archived', 'deleted'
    tags: List[str]
    summary: Optional[str] = None

class ConversationDatabase:
    """Base de datos para gestión de conversaciones"""
    
    def __init__(self, db_path: str = "./data/conversations.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Inicializar esquema de base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Tabla de sesiones de conversación
                CREATE TABLE IF NOT EXISTS conversation_sessions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    tags TEXT DEFAULT '[]',  -- JSON array
                    summary TEXT,
                    metadata TEXT DEFAULT '{}'  -- JSON object
                );

                -- Tabla de mensajes
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    message_order INTEGER NOT NULL,
                    tokens_used INTEGER,
                    model_used TEXT,
                    metadata TEXT DEFAULT '{}',  -- JSON object
                    FOREIGN KEY (session_id) REFERENCES conversation_sessions (id)
                );

                -- Tabla de estadísticas de uso
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    date TEXT NOT NULL,  -- YYYY-MM-DD
                    messages_count INTEGER DEFAULT 0,
                    tokens_used INTEGER DEFAULT 0,
                    api_calls INTEGER DEFAULT 0,
                    cost_estimate REAL DEFAULT 0.0
                );

                -- Tabla de búsqueda full-text (opcional)
                CREATE VIRTUAL TABLE IF NOT EXISTS message_search USING fts5(
                    content,
                    session_id,
                    project_id,
                    role,
                    timestamp
                );

                -- Crear índices por separado
                CREATE INDEX IF NOT EXISTS idx_session_order ON conversation_messages (session_id, message_order);
                CREATE INDEX IF NOT EXISTS idx_project_timestamp ON conversation_messages (project_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_role_timestamp ON conversation_messages (role, timestamp);
                CREATE INDEX IF NOT EXISTS idx_project_date ON usage_stats (project_id, date);
                CREATE INDEX IF NOT EXISTS idx_session_date ON usage_stats (session_id, date);
            """)
            
            logger.info(f"Database initialized: {self.db_path}")
            
    def create_session(self, project_id: str, name: str, tags: List[str] = None) -> str:
        """Crear nueva sesión de conversación"""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        tags = tags or []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversation_sessions 
                (id, project_id, name, created_at, updated_at, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, project_id, name, now, now, json.dumps(tags)))
        
        logger.info(f"Created conversation session: {session_id}")
        return session_id
    
    def add_message(self, session_id: str, project_id: str, role: str, 
                   content: str, tokens_used: int = None, model_used: str = None,
                   metadata: Dict = None) -> str:
        """Agregar mensaje a la conversación"""
        message_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        metadata = metadata or {}
        
        with sqlite3.connect(self.db_path) as conn:
            # Obtener orden del mensaje
            cursor = conn.execute(
                "SELECT COALESCE(MAX(message_order), 0) + 1 FROM conversation_messages WHERE session_id = ?",
                (session_id,)
            )
            message_order = cursor.fetchone()[0]
            
            # Insertar mensaje
            conn.execute("""
                INSERT INTO conversation_messages 
                (id, session_id, project_id, role, content, timestamp, message_order, tokens_used, model_used, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (message_id, session_id, project_id, role, content, now, message_order, 
                  tokens_used, model_used, json.dumps(metadata)))
            
            # Actualizar contador de mensajes en la sesión
            conn.execute("""
                UPDATE conversation_sessions 
                SET message_count = message_count + 1,
                    updated_at = ?,
                    total_tokens = total_tokens + COALESCE(?, 0)
                WHERE id = ?
            """, (now, tokens_used or 0, session_id))
            
            # Agregar a búsqueda full-text
            conn.execute("""
                INSERT INTO message_search (content, session_id, project_id, role, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (content, session_id, project_id, role, now))
        
        logger.info(f"Added message to session {session_id}")
        return message_id
    
    def get_session_messages(self, session_id: str, limit: int = None) -> List[ConversationMessage]:
        """Obtener mensajes de una sesión"""
        query = """
            SELECT id, session_id, project_id, role, content, timestamp, 
                   tokens_used, model_used, metadata
            FROM conversation_messages 
            WHERE session_id = ?
            ORDER BY message_order
        """
        
        params = [session_id]
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            messages = []
            
            for row in cursor.fetchall():
                metadata = json.loads(row[8]) if row[8] else {}
                messages.append(ConversationMessage(
                    id=row[0],
                    session_id=row[1],
                    project_id=row[2],
                    role=row[3],
                    content=row[4],
                    timestamp=datetime.fromisoformat(row[5]),
                    tokens_used=row[6],
                    model_used=row[7],
                    metadata=metadata
                ))
        
        return messages
    
    def get_project_sessions(self, project_id: str, status: str = 'active') -> List[ConversationSession]:
        """Obtener sesiones de un proyecto"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, project_id, name, created_at, updated_at, 
                       message_count, total_tokens, status, tags, summary
                FROM conversation_sessions 
                WHERE project_id = ? AND status = ?
                ORDER BY updated_at DESC
            """, (project_id, status))
            
            sessions = []
            for row in cursor.fetchall():
                tags = json.loads(row[8]) if row[8] else []
                sessions.append(ConversationSession(
                    id=row[0],
                    project_id=row[1],
                    name=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                    updated_at=datetime.fromisoformat(row[4]),
                    message_count=row[5],
                    total_tokens=row[6],
                    status=row[7],
                    tags=tags,
                    summary=row[9]
                ))
        
        return sessions
    
    def search_messages(self, query: str, project_id: str = None, 
                       limit: int = 50) -> List[Dict]:
        """Búsqueda full-text en mensajes"""
        sql_query = """
            SELECT m.id, m.session_id, m.project_id, m.role, m.content, 
                   m.timestamp, s.name as session_name
            FROM message_search ms
            JOIN conversation_messages m ON ms.rowid = m.rowid
            JOIN conversation_sessions s ON m.session_id = s.id
            WHERE message_search MATCH ?
        """
        
        params = [query]
        
        if project_id:
            sql_query += " AND m.project_id = ?"
            params.append(project_id)
        
        sql_query += " ORDER BY rank LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(sql_query, params)
            results = []
            
            for row in cursor.fetchall():
                results.append({
                    'message_id': row[0],
                    'session_id': row[1],
                    'project_id': row[2],
                    'role': row[3],
                    'content': row[4],
                    'timestamp': row[5],
                    'session_name': row[6]
                })
        
        return results
    
    def update_session_summary(self, session_id: str, summary: str):
        """Actualizar resumen de sesión"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE conversation_sessions 
                SET summary = ?, updated_at = ?
                WHERE id = ?
            """, (summary, datetime.now().isoformat(), session_id))
    
    def archive_session(self, session_id: str):
        """Archivar sesión"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE conversation_sessions 
                SET status = 'archived', updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), session_id))
    
    def get_usage_stats(self, project_id: str, days: int = 30) -> Dict:
        """Obtener estadísticas de uso"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    COUNT(DISTINCT session_id) as total_sessions,
                    COUNT(*) as total_messages,
                    SUM(COALESCE(tokens_used, 0)) as total_tokens,
                    AVG(COALESCE(tokens_used, 0)) as avg_tokens_per_message
                FROM conversation_messages 
                WHERE project_id = ? 
                AND timestamp >= datetime('now', '-{} days')
            """.format(days), (project_id,))
            
            row = cursor.fetchone()
            
            return {
                'total_sessions': row[0] or 0,
                'total_messages': row[1] or 0,
                'total_tokens': row[2] or 0,
                'avg_tokens_per_message': round(row[3] or 0, 2),
                'period_days': days
            }
    
    def export_session_to_formats(self, session_id: str) -> Dict[str, str]:
        """Exportar sesión a múltiples formatos"""
        messages = self.get_session_messages(session_id)
        
        if not messages:
            return {}
        
        # Obtener info de la sesión
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name, created_at, project_id, summary
                FROM conversation_sessions WHERE id = ?
            """, (session_id,))
            session_info = cursor.fetchone()
        
        session_name = session_info[0] if session_info else "Unknown"
        
        # Formato JSON estructurado
        json_export = {
            'session_id': session_id,
            'session_name': session_name,
            'created_at': session_info[1] if session_info else None,
            'project_id': session_info[2] if session_info else None,
            'summary': session_info[3] if session_info else None,
            'message_count': len(messages),
            'messages': [
                {
                    'id': msg.id,
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat(),
                    'tokens_used': msg.tokens_used,
                    'model_used': msg.model_used,
                    'metadata': msg.metadata
                }
                for msg in messages
            ]
        }
        
        # Formato Markdown
        markdown_export = f"# Conversación: {session_name}\n\n"
        markdown_export += f"**Sesión ID:** {session_id}\n"
        markdown_export += f"**Creada:** {session_info[1] if session_info else 'N/A'}\n"
        markdown_export += f"**Mensajes:** {len(messages)}\n\n"
        
        if session_info and session_info[3]:
            markdown_export += f"## Resumen\n{session_info[3]}\n\n"
        
        markdown_export += "## Conversación\n\n"
        
        for i, msg in enumerate(messages, 1):
            role_emoji = "👤" if msg.role == "user" else "🤖"
            role_name = "Usuario" if msg.role == "user" else "Agente"
            
            markdown_export += f"### {role_emoji} {role_name} (Mensaje {i})\n"
            markdown_export += f"*{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            markdown_export += f"{msg.content}\n\n"
            
            if msg.tokens_used:
                markdown_export += f"*Tokens: {msg.tokens_used}*\n\n"
            
            markdown_export += "---\n\n"
        
        # Formato CSV simple
        csv_export = "timestamp,role,content,tokens\n"
        for msg in messages:
            # Escapar comillas en CSV
            content_escaped = msg.content.replace('"', '""')
            csv_export += f'"{msg.timestamp.isoformat()}","{msg.role}","{content_escaped}","{msg.tokens_used or 0}"\n'
        
        return {
            'json': json.dumps(json_export, indent=2, ensure_ascii=False),
            'markdown': markdown_export,
            'csv': csv_export
        }
    
    def cleanup_old_sessions(self, days: int = 90):
        """Limpiar sesiones antiguas (mover a archived)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE conversation_sessions 
                SET status = 'archived'
                WHERE updated_at < datetime('now', '-{} days')
                AND status = 'active'
            """.format(days))
            
            affected = cursor.rowcount
            
        logger.info(f"Archived {affected} old sessions (older than {days} days)")
        return affected
