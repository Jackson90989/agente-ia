"""
Agent controller service.
Orchestrates policy checks + deterministic execution + audit logging.
"""

from typing import Callable, Optional

from src.services.audit_service import AuditService
from src.services.policy_service import PolicyService


class AgentControllerService:
    """Core orchestrator for high-risk domain actions."""

    def __init__(
        self,
        policy_service: Optional[PolicyService] = None,
        audit_service: Optional[AuditService] = None,
    ):
        self.policy_service = policy_service or PolicyService()
        self.audit_service = audit_service or AuditService()

    def executar_acao(
        self,
        *,
        actor_tipo: str,
        actor_id: Optional[int],
        resource_owner_id: Optional[int],
        acao: str,
        recurso: str,
        origem: str,
        handler: Callable[[], str],
    ) -> str:
        """
        Authorize and execute a deterministic action with full audit trail.
        """
        decision = self.policy_service.autorizar(
            actor_tipo=actor_tipo,
            actor_id=actor_id,
            acao=acao,
            resource_owner_id=resource_owner_id,
        )

        if not decision.allowed:
            self.audit_service.registrar_evento(
                actor_tipo=actor_tipo,
                actor_id=actor_id,
                acao=acao,
                recurso=recurso,
                origem=origem,
                sucesso=False,
                detalhe=decision.reason,
            )
            return "❌ Acesso nao autorizado para esta operacao."

        try:
            resultado = handler()
            self.audit_service.registrar_evento(
                actor_tipo=actor_tipo,
                actor_id=actor_id,
                acao=acao,
                recurso=recurso,
                origem=origem,
                sucesso=True,
                detalhe="acao executada com sucesso",
            )
            return resultado
        except Exception as exc:
            self.audit_service.registrar_evento(
                actor_tipo=actor_tipo,
                actor_id=actor_id,
                acao=acao,
                recurso=recurso,
                origem=origem,
                sucesso=False,
                detalhe=f"erro na execucao: {exc}",
            )
            return "❌ Ocorreu um erro na operacao. Tente novamente."