"""
Service for conversation memory/context persistence using SQLite.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config.settings import Settings


class MemoryContextService:
    """Stores and retrieves short-term conversation memory for each WhatsApp number."""

    def __init__(self, db_path: Optional[Path] = None):
        settings = Settings.get_instance()
        self.db_path = Path(db_path) if db_path else Path(settings.DB_PATH)
        self._ensure_table()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memoria_contexto (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_whatsapp TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL,
                role TEXT NOT NULL,
                mensagem TEXT NOT NULL,
                metadata TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_memoria_numero_criado
            ON memoria_contexto (numero_whatsapp, criado_em)
            """
        )
        conn.commit()
        conn.close()

    def salvar_interacao(
        self,
        numero_whatsapp: str,
        tipo_usuario: str,
        role: str,
        mensagem: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Persists one interaction message (user or assistant)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO memoria_contexto (
                    numero_whatsapp, tipo_usuario, role, mensagem, metadata, criado_em
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    numero_whatsapp,
                    tipo_usuario,
                    role,
                    mensagem,
                    json.dumps(metadata or {}, ensure_ascii=True),
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def obter_contexto_recente(self, numero_whatsapp: str, limite: int = 6) -> List[Dict[str, Any]]:
        """Returns the latest messages for a user, ordered oldest -> newest."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT role, mensagem, tipo_usuario, criado_em, metadata
            FROM memoria_contexto
            WHERE numero_whatsapp = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (numero_whatsapp, limite),
        )
        rows = cursor.fetchall()
        conn.close()

        resultado: List[Dict[str, Any]] = []
        for row in reversed(rows):
            try:
                metadata = json.loads(row["metadata"] or "{}")
            except Exception:
                metadata = {}
            resultado.append(
                {
                    "role": row["role"],
                    "mensagem": row["mensagem"],
                    "tipo_usuario": row["tipo_usuario"],
                    "criado_em": row["criado_em"],
                    "metadata": metadata,
                }
            )
        return resultado

    def limpar_contexto_usuario(self, numero_whatsapp: str) -> int:
        """Deletes all context rows for one user; returns deleted row count."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM memoria_contexto WHERE numero_whatsapp = ?",
            (numero_whatsapp,),
        )
        removidos = cursor.rowcount
        conn.commit()
        conn.close()
        return removidos
