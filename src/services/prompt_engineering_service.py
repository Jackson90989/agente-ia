"""
Prompt engineering utilities for role-specific and context-aware prompts.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional


class PromptEngineeringService:
    """Builds stable, concise prompts for OLLAMA with memory-aware context."""

    @staticmethod
    def construir_system_prompt(
        tipo_usuario: str,
        contexto: Dict[str, Any],
        dados_usuario: Optional[Dict[str, Any]] = None,
    ) -> str:
        dados_usuario = dados_usuario or {}

        if tipo_usuario == "secretaria":
            return (
                "Voce e a assistente da secretaria academica. "
                "Responda com objetividade, tom profissional, e foco em operacao. "
                f"Nome de referencia: {dados_usuario.get('secretaria_nome', 'Secretaria')}. "
                f"Total de alunos visivel: {contexto.get('total_alunos', 0)}."
            )

        if tipo_usuario == "aluno":
            nome_aluno = dados_usuario.get("aluno_nome", "Aluno")
            contexto_resumido = json.dumps(contexto, ensure_ascii=True)[:500]
            return (
                f"Voce e a SECRETARIA ACADEMICA atendendo o aluno {nome_aluno}. "
                "Responda com postura institucional, objetiva e orientada a procedimento. "
                "Quando houver solicitacao administrativa (trancamento, cancelamento, requerimento), "
                "forneca passos, prazo e protocolo sugerido, sem aconselhamento terapeutico. "
                f"Contexto do aluno: {contexto_resumido}"
            )

        return (
            "Voce e a assistente de atendimento ao publico de uma faculdade. "
            "Seja acolhedora, clara e pragmatica. "
            "Quando cabivel, ofereca opcoes concretas: cursos, valores, documentos e cadastro."
        )

    @staticmethod
    def construir_prompt_usuario(
        pergunta: str,
        memoria_recente: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        memoria_recente = memoria_recente or []

        if not memoria_recente:
            return pergunta

        linhas = []
        for item in memoria_recente[-6:]:
            role = item.get("role", "user")
            msg = (item.get("mensagem", "") or "").strip()
            if not msg:
                continue
            prefix = "usuario" if role == "user" else "assistente"
            linhas.append(f"{prefix}: {msg}")

        historico = "\n".join(linhas)
        return (
            "Historico recente da conversa:\n"
            f"{historico}\n\n"
            "Mensagem atual do usuario:\n"
            f"{pergunta}"
        )
