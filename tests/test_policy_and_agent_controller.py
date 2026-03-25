import tempfile
import unittest
from pathlib import Path

from src.services.audit_service import AuditService
from src.services.agent_controller_service import AgentControllerService
from src.services.policy_service import PolicyService


class TestPolicyAndAgentController(unittest.TestCase):
    def test_policy_denies_unknown_profile(self):
        policy = PolicyService()
        decision = policy.autorizar(actor_tipo="publico", actor_id=None, acao=PolicyService.ACAO_CONSULTAR_DADOS)
        self.assertFalse(decision.allowed)

    def test_policy_allows_aluno_own_action(self):
        policy = PolicyService()
        decision = policy.autorizar(
            actor_tipo="aluno",
            actor_id=10,
            resource_owner_id=10,
            acao=PolicyService.ACAO_CONSULTAR_DADOS,
        )
        self.assertTrue(decision.allowed)

    def test_agent_controller_executes_and_audits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "audit.db"
            controller = AgentControllerService(
                policy_service=PolicyService(),
                audit_service=AuditService(db_path=db_path),
            )

            resposta = controller.executar_acao(
                actor_tipo="aluno",
                actor_id=99,
                resource_owner_id=99,
                acao=PolicyService.ACAO_CONSULTAR_DADOS,
                recurso="aluno:99",
                origem="teste",
                handler=lambda: "ok",
            )

            self.assertEqual(resposta, "ok")

    def test_agent_controller_denies_and_returns_message(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "audit.db"
            controller = AgentControllerService(
                policy_service=PolicyService(),
                audit_service=AuditService(db_path=db_path),
            )

            resposta = controller.executar_acao(
                actor_tipo="publico",
                actor_id=None,
                resource_owner_id=1,
                acao=PolicyService.ACAO_CONSULTAR_DADOS,
                recurso="aluno:1",
                origem="teste",
                handler=lambda: "nao deveria executar",
            )

            self.assertIn("nao autorizado", resposta.lower())


if __name__ == "__main__":
    unittest.main()
