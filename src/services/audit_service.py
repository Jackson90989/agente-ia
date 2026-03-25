"""
Audit service for sensitive domain actions.
"""

import sqlite3
from pathlib import Path
from typing import Optional

from src.config.settings import Settings


class AuditService:
    """Persist audit trail for sensitive actions."""

    def __init__(self, db_path: Optional[Path] = None):
        settings = Settings.get_instance()
        self.db_path = Path(db_path) if db_path else Path(settings.DB_PATH)
        self._ensure_table()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS auditoria_agente (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_tipo TEXT NOT NULL,
                actor_id INTEGER,
                acao TEXT NOT NULL,
                recurso TEXT,
                origem TEXT,
                sucesso BOOLEAN NOT NULL,
                detalhe TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_auditoria_actor
            ON auditoria_agente (actor_tipo, actor_id, criado_em)
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_auditoria_acao
            ON auditoria_agente (acao, criado_em)
            """
        )
        conn.commit()
        conn.close()

    def registrar_evento(
        self,
        *,
        actor_tipo: str,
        actor_id: Optional[int],
        acao: str,
        recurso: str,
        origem: str,
        sucesso: bool,
        detalhe: str = "",
    ) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO auditoria_agente (
                actor_tipo, actor_id, acao, recurso, origem, sucesso, detalhe
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                actor_tipo,
                actor_id,
                acao,
                recurso,
                origem,
                1 if sucesso else 0,
                detalhe[:1000],
            ),
        )
        conn.commit()
        conn.close()

    def listar_eventos(
        self,
        limit: int = 100,
        acao: Optional[str] = None,
        actor_tipo: Optional[str] = None,
        actor_id: Optional[int] = None,
        sucesso: Optional[bool] = None,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
    ):
        conn = self._get_connection()
        cursor = conn.cursor()

        filtros = []
        parametros = []

        if acao:
            filtros.append("acao = ?")
            parametros.append(acao)

        if actor_tipo:
            filtros.append("actor_tipo = ?")
            parametros.append(actor_tipo)

        if actor_id is not None:
            filtros.append("actor_id = ?")
            parametros.append(int(actor_id))

        if sucesso is not None:
            filtros.append("sucesso = ?")
            parametros.append(1 if sucesso else 0)

        if data_inicio:
            filtros.append("criado_em >= ?")
            parametros.append(data_inicio)

        if data_fim:
            filtros.append("criado_em <= ?")
            parametros.append(data_fim)

        where_clause = f"WHERE {' AND '.join(filtros)}" if filtros else ""
        query = f"""
            SELECT id, actor_tipo, actor_id, acao, recurso, origem, sucesso, detalhe, criado_em
            FROM auditoria_agente
            {where_clause}
            ORDER BY id DESC
            LIMIT ?
        """
        parametros.append(int(limit))

        cursor.execute(query, tuple(parametros))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
