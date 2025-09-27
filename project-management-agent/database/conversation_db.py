# database/conversation_db.py
import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import os

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """Estructura de mensaje de conversación"""
    id: str
    session_id: str
    project_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    message_order: int
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    metadata: Optional[Dict] = None

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
                    cost_estimate REAL DEFAULT 0.0,
                    UNIQUE(project_id, session_id, date)
                );

                -- Crear índices por separado
                CREATE INDEX IF NOT EXISTS idx_session_order ON conversation_messages (session_id, message_order);
                CREATE INDEX IF NOT EXISTS idx_project_timestamp ON conversation_messages (project_id, timestamp);
                CREATE INDEX IF NOT EXISTS idx_role_timestamp ON conversation_messages (role, timestamp);
                CREATE INDEX IF NOT EXISTS idx_project_date ON usage_stats (project_id, date);
                CREATE INDEX IF NOT EXISTS idx_session_date ON usage_stats (session_id, date);
                CREATE INDEX IF NOT EXISTS idx_session_status ON conversation_sessions (status);
            """)
            
        print(f"✅ Database initialized: {self.db_path}")
    
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
            """, (message_id, session_id, project_id, role, content, now, message_order, tokens_used, model_used, json.dumps(metadata)))
            
            # Actualizar conteo en sesión
            conn.execute("""
                UPDATE conversation_sessions 
                SET message_count = message_count + 1, 
                    updated_at = ?,
                    total_tokens = total_tokens + ?
                WHERE id = ?
            """, (now, tokens_used or 0, session_id))
            
            # Actualizar estadísticas diarias
            self._update_daily_stats(conn, project_id, session_id, tokens_used or 0)
        
        return message_id
    
    def _update_daily_stats(self, conn, project_id: str, session_id: str, tokens_used: int):
        """Actualizar estadísticas diarias"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Primero intentar insertar
        try:
            conn.execute("""
                INSERT INTO usage_stats (project_id, session_id, date, messages_count, tokens_used, api_calls)
                VALUES (?, ?, ?, 1, ?, 1)
            """, (project_id, session_id, today, tokens_used))
        except sqlite3.IntegrityError:
            # Si ya existe, actualizar
            conn.execute("""
                UPDATE usage_stats 
                SET messages_count = messages_count + 1,
                    tokens_used = tokens_used + ?,
                    api_calls = api_calls + 1
                WHERE project_id = ? AND session_id = ? AND date = ?
            """, (tokens_used, project_id, session_id, today))
    
    def get_session_messages(self, session_id: str, limit: int = None) -> List[ConversationMessage]:
        """Obtener mensajes de una sesión"""
        query = """
            SELECT id, session_id, project_id, role, content, timestamp, message_order, 
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
                messages.append(ConversationMessage(
                    id=row[0],
                    session_id=row[1],
                    project_id=row[2],
                    role=row[3],
                    content=row[4],
                    timestamp=datetime.fromisoformat(row[5]),
                    message_order=row[6],
                    tokens_used=row[7],
                    model_used=row[8],
                    metadata=json.loads(row[9]) if row[9] else {}
                ))
            
            return messages
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Obtener estadísticas de una sesión"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT s.*, 
                       COUNT(m.id) as actual_message_count,
                       SUM(m.tokens_used) as actual_tokens_used,
                       MIN(m.timestamp) as first_message,
                       MAX(m.timestamp) as last_message
                FROM conversation_sessions s
                LEFT JOIN conversation_messages m ON s.id = m.session_id
                WHERE s.id = ?
                GROUP BY s.id
            """, (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return {}
            
            return {
                'session_id': row[0],
                'project_id': row[1],
                'name': row[2],
                'created_at': row[3],
                'updated_at': row[4],
                'message_count': row[5],
                'total_tokens': row[6],
                'status': row[7],
                'tags': json.loads(row[8]) if row[8] else [],
                'summary': row[9],
                'metadata': json.loads(row[10]) if row[10] else {},
                'actual_message_count': row[11] or 0,
                'actual_tokens_used': row[12] or 0,
                'first_message': row[13],
                'last_message': row[14]
            }
    
    def list_sessions(self, project_id: str = None, status: str = 'active', 
                     limit: int = 20) -> List[Dict]:
        """Listar sesiones de conversación"""
        query = "SELECT * FROM conversation_sessions WHERE status = ?"
        params = [status]
        
        if project_id:
            query += " AND project_id = ?"
            params.append(project_id)
            
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            sessions = []
            
            for row in cursor.fetchall():
                sessions.append({
                    'id': row[0],
                    'project_id': row[1],
                    'name': row[2],
                    'created_at': row[3],
                    'updated_at': row[4],
                    'message_count': row[5],
                    'total_tokens': row[6],
                    'status': row[7],
                    'tags': json.loads(row[8]) if row[8] else [],
                    'summary': row[9]
                })
            
            return sessions
    
    def search_conversations(self, query: str, project_id: str = None, limit: int = 10) -> List[Dict]:
        """Buscar en conversaciones usando LIKE (fallback si no hay FTS)"""
        sql_query = "SELECT * FROM conversation_messages WHERE content LIKE ?"
        params = [f"%{query}%"]
        
        if project_id:
            sql_query += " AND project_id = ?"
            params.append(project_id)
            
        sql_query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(sql_query, params)
            return [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
    
    def export_session(self, session_id: str, format: str = 'json') -> str:
        """Exportar sesión en diferentes formatos"""
        session_stats = self.get_session_stats(session_id)
        messages = self.get_session_messages(session_id)
        
        if format == 'json':
            return json.dumps({
                'session': session_stats,
                'messages': [asdict(msg) for msg in messages]
            }, indent=2, default=str)
        
        elif format == 'markdown':
            md_content = f"# {session_stats['name']}\n\n"
            md_content += f"**Proyecto:** {session_stats['project_id']}\n"
            md_content += f"**Creado:** {session_stats['created_at']}\n"
            md_content += f"**Mensajes:** {session_stats['message_count']}\n"
            md_content += f"**Tokens:** {session_stats['total_tokens']}\n\n"
            
            for msg in messages:
                role_emoji = "👤" if msg.role == "user" else "🤖"
                md_content += f"## {role_emoji} {msg.role.upper()}\n"
                md_content += f"*{msg.timestamp}*\n\n"
                md_content += f"{msg.content}\n\n"
                if msg.tokens_used:
                    md_content += f"*Tokens: {msg.tokens_used}*\n\n"
                md_content += "---\n\n"
            
            return md_content
        
        else:
            raise ValueError(f"Format '{format}' not supported")