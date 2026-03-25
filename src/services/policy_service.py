"""
Policy service for authorization decisions in the domain agent.
"""

from dataclasses import dataclass
from typing import Optional
from src.config.policy_matrix import POLICY_MATRIX


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str = ""


class PolicyService:
    """Centralized authorization rules for domain actions."""

    # Actions handled by deterministic services.
    ACAO_CONSULTAR_DADOS = "CONSULTAR_DADOS"
    ACAO_CONSULTAR_NOTAS = "CONSULTAR_NOTAS"
    ACAO_CONSULTAR_GRADE = "CONSULTAR_GRADE"
    ACAO_CONSULTAR_HISTORICO = "CONSULTAR_HISTORICO"
    ACAO_GERAR_DECLARACAO = "GERAR_DECLARACAO"
    ACAO_CONSULTAR_FINANCEIRO = "CONSULTAR_FINANCEIRO"
    ACAO_SOLICITAR_TRANCAMENTO = "SOLICITAR_TRANCAMENTO"
    ACAO_SOLICITAR_CANCELAMENTO = "SOLICITAR_CANCELAMENTO"
    ACAO_SOLICITAR_SEGUNDA_VIA_BOLETO = "SOLICITAR_SEGUNDA_VIA_BOLETO"
    ACAO_AJUSTAR_GRADE_INCLUSAO = "AJUSTAR_GRADE_INCLUSAO"
    ACAO_AJUSTAR_GRADE_REMOCAO = "AJUSTAR_GRADE_REMOCAO"
    ACAO_CONSULTAR_TOTAL_ALUNOS = "CONSULTAR_TOTAL_ALUNOS"
    ACAO_LISTAR_ALUNOS = "LISTAR_ALUNOS"
    ACAO_LISTAR_NOVOS_CADASTROS = "LISTAR_NOVOS_CADASTROS"

    def autorizar(
        self,
        *,
        actor_tipo: str,
        acao: str,
        actor_id: Optional[int] = None,
        resource_owner_id: Optional[int] = None,
    ) -> PolicyDecision:
        """Returns authorization decision for a given action."""
        actor = (actor_tipo or "").lower().strip()
        allowed_actions = POLICY_MATRIX.get(actor, set())

        if not allowed_actions:
            return PolicyDecision(False, "perfil sem permissao para acao solicitada")

        if acao not in allowed_actions:
            return PolicyDecision(False, f"acao nao permitida para perfil {actor}")

        if actor == "secretaria":
            return PolicyDecision(True, "secretaria com acesso institucional")

        if actor == "aluno":
            if resource_owner_id is not None and actor_id is not None and resource_owner_id != actor_id:
                return PolicyDecision(False, "aluno so pode acessar os proprios dados")

            return PolicyDecision(True, "aluno autorizado no proprio contexto")

        return PolicyDecision(True, f"perfil {actor} autorizado")
