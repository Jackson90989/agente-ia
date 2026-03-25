"""
Memória do agente - Gerencia histórico de conversas
"""

import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class ConversationMemory:
    """Memória de curto prazo da conversa atual"""
    
    def __init__(self, max_history: int = 50):
        self.history = []
        self.max_history = max_history
        self.context = {}
    
    def add(self, role: str, message: str, metadata: Dict = None):
        """Adiciona uma mensagem ao histórico"""
        
        entry = {
            "role": role,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.history.append(entry)
        
        # Manter apenas o histórico recente
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_recent(self, n: int = 10) -> str:
        """Retorna as últimas n mensagens formatadas"""
        
        recent = self.history[-n:] if n > 0 else self.history
        
        context = "Histórico da conversa:\n\n"
        for entry in recent:
            context += f"{entry['role'].upper()}: {entry['message']}\n"
        
        return context
    
    def clear(self):
        """Limpa a memória"""
        self.history = []
        self.context = {}


class LongTermMemory:
    """Memória de longo prazo usando SQLite"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Inicializa tabelas de memória"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela para memórias permanentes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                key TEXT,
                value TEXT,
                category TEXT,
                created_at TIMESTAMP,
                last_accessed TIMESTAMP
            )
        """)
        
        # Índices
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_key ON memories(user_id, key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON memories(category)")
        
        conn.commit()
        conn.close()
    
    def remember(self, user_id: str, key: str, value: str, category: str = "general"):
        """Armazena uma informação na memória de longo prazo"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (user_id, key, value, category, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, key, value, category, now, now))
        
        conn.commit()
        conn.close()
    
    def recall(self, user_id: str, key: str = None, category: str = None) -> List[Dict]:
        """Recupera informações da memória"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT key, value, category FROM memories WHERE user_id = ?"
        params = [user_id]
        
        if key:
            query += " AND key = ?"
            params.append(key)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        cursor.execute(query, params)
        results = [{"key": row[0], "value": row[1], "category": row[2]} 
                   for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def forget(self, user_id: str, key: str = None):
        """Remove informações da memória"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if key:
            cursor.execute("DELETE FROM memories WHERE user_id = ? AND key = ?", 
                          (user_id, key))
        else:
            cursor.execute("DELETE FROM memories WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()