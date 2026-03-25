import unittest
from unittest.mock import patch

import super_agente_simples as app_module


class TestFlaskApiIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app_module.app.config["TESTING"] = True
        cls.client = app_module.app.test_client()

    def test_api_chat_publico_ok(self):
        with patch("super_agente_simples.perguntar_ollama", return_value="resposta publica"):
            resp = self.client.post(
                "/api/chat_publico",
                json={"mensagem": "quais cursos?"},
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json().get("resposta"), "resposta publica")

    def test_api_chat_aluno_requires_login(self):
        with self.client.session_transaction() as sess:
            sess.clear()
        resp = self.client.post("/api/chat_aluno", json={"mensagem": "oi"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("login", resp.get_json().get("resposta", "").lower())

    def test_api_chat_aluno_with_session(self):
        with self.client.session_transaction() as sess:
            sess["aluno_id"] = 1
            sess["aluno_nome"] = "Aluno Teste"
            sess["tipo"] = "aluno"

        with patch("super_agente_simples.processar_mensagem_aluno_whatsapp_avancado", return_value="resposta aluno"):
            resp = self.client.post(
                "/api/chat_aluno",
                json={"mensagem": "minhas notas"},
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json().get("resposta"), "resposta aluno")

    def test_api_chat_secretaria_requires_login(self):
        with self.client.session_transaction() as sess:
            sess.clear()
        resp = self.client.post("/api/chat_secretaria", json={"mensagem": "estatisticas"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("login", resp.get_json().get("resposta", "").lower())

    def test_api_chat_secretaria_with_session(self):
        with self.client.session_transaction() as sess:
            sess["secretaria_id"] = 1
            sess["secretaria_nome"] = "Secretaria Teste"
            sess["tipo"] = "secretaria"

        with patch("super_agente_simples.processar_mensagem_secretaria_whatsapp", return_value="resposta secretaria"):
            resp = self.client.post(
                "/api/chat_secretaria",
                json={"mensagem": "quais os dados?"},
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json().get("resposta"), "resposta secretaria")

    def test_api_auditoria_requires_login(self):
        with self.client.session_transaction() as sess:
            sess.clear()
        resp = self.client.get("/api/auditoria")
        self.assertEqual(resp.status_code, 403)

    def test_api_auditoria_with_session(self):
        with self.client.session_transaction() as sess:
            sess["secretaria_id"] = 1
            sess["secretaria_nome"] = "Secretaria Teste"
            sess["tipo"] = "secretaria"

        eventos_mock = [
            {
                "id": 1,
                "actor_tipo": "secretaria",
                "actor_id": 1,
                "acao": "LISTAR_ALUNOS",
                "sucesso": 1,
                "criado_em": "2026-03-22 10:00:00",
            }
        ]
        with patch("super_agente_simples.audit_service") as mock_audit:
            mock_audit.listar_eventos.return_value = eventos_mock
            resp = self.client.get("/api/auditoria?limite=10")

        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body.get("total"), 1)
        self.assertEqual(body.get("eventos"), eventos_mock)

    def test_api_auditoria_with_filters(self):
        with self.client.session_transaction() as sess:
            sess["secretaria_id"] = 1
            sess["secretaria_nome"] = "Secretaria Teste"
            sess["tipo"] = "secretaria"

        with patch("super_agente_simples.audit_service") as mock_audit:
            mock_audit.listar_eventos.return_value = []
            resp = self.client.get(
                "/api/auditoria?limite=25&acao=LISTAR_ALUNOS&actor_tipo=secretaria&actor_id=1&sucesso=1&data_inicio=2026-03-01%2000:00:00&data_fim=2026-03-31%2023:59:59"
            )

        self.assertEqual(resp.status_code, 200)
        mock_audit.listar_eventos.assert_called_once_with(
            limit=25,
            acao="LISTAR_ALUNOS",
            actor_tipo="secretaria",
            actor_id=1,
            sucesso=True,
            data_inicio="2026-03-01 00:00:00",
            data_fim="2026-03-31 23:59:59",
        )

    def test_auditoria_secretaria_page_requires_login(self):
        with self.client.session_transaction() as sess:
            sess.clear()
        resp = self.client.get("/auditoria_secretaria")
        self.assertEqual(resp.status_code, 302)

    def test_auditoria_secretaria_page_with_session(self):
        with self.client.session_transaction() as sess:
            sess["secretaria_id"] = 1
            sess["secretaria_nome"] = "Secretaria Teste"
            sess["tipo"] = "secretaria"
        resp = self.client.get("/auditoria_secretaria")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Auditoria Operacional da Secretaria", resp.get_data(as_text=True))

    def test_whatsapp_webhook_missing_data(self):
        resp = self.client.post("/api/whatsapp-webhook", json={})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("incompletos", resp.get_json().get("resposta", "").lower())

    def test_whatsapp_webhook_via_message_service(self):
        with patch(
            "super_agente_simples.identificar_usuario_por_whatsapp",
            return_value={"id": 1, "nome": "Aluno Teste", "tipo": "aluno"},
        ), patch("super_agente_simples.processar_mensagem_aluno_whatsapp_avancado", return_value="ok webhook"):
            resp = self.client.post(
                "/api/whatsapp-webhook",
                json={"numero": "5511999999999", "mensagem": "oi"},
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json().get("resposta"), "ok webhook")

    def test_whatsapp_webhook_aluno_trancamento_fluxo_secretaria(self):
        with patch(
            "super_agente_simples.identificar_usuario_por_whatsapp",
            return_value={"id": 1, "nome": "Jackson Rodrigues", "tipo": "aluno"},
        ):
            resp = self.client.post(
                "/api/whatsapp-webhook",
                json={"numero": "5511999999999", "mensagem": "quero trancar a faculdade"},
            )

        self.assertEqual(resp.status_code, 200)
        resposta = resp.get_json().get("resposta", "").lower()
        self.assertIn("trancamento", resposta)
        self.assertIn("protocolo", resposta)

    def test_whatsapp_webhook_aluno_cancelamento_fluxo_secretaria(self):
        with patch(
            "super_agente_simples.identificar_usuario_por_whatsapp",
            return_value={"id": 1, "nome": "Jackson Rodrigues", "tipo": "aluno"},
        ), patch("super_agente_simples.perguntar_ollama", return_value="fallback nao esperado"):
            resp = self.client.post(
                "/api/whatsapp-webhook",
                json={"numero": "5511999999999", "mensagem": "quero cancelar a faculdade"},
            )

        self.assertEqual(resp.status_code, 200)
        resposta = resp.get_json().get("resposta", "").lower()
        self.assertIn("cancelamento", resposta)
        self.assertIn("protocolo", resposta)

    def test_whatsapp_webhook_aluno_boleto_fluxo_secretaria(self):
        with patch(
            "super_agente_simples.identificar_usuario_por_whatsapp",
            return_value={"id": 1, "nome": "Jackson Rodrigues", "tipo": "aluno"},
        ), patch("super_agente_simples.perguntar_ollama", return_value="fallback nao esperado"):
            resp = self.client.post(
                "/api/whatsapp-webhook",
                json={"numero": "5511999999999", "mensagem": "preciso da 2 via do boleto"},
            )

        self.assertEqual(resp.status_code, 200)
        resposta = resp.get_json().get("resposta", "").lower()
        self.assertIn("2ª via", resposta)
        self.assertIn("protocolo", resposta)

    def test_whatsapp_webhook_aluno_declaracao_fluxo_secretaria(self):
        with patch(
            "super_agente_simples.identificar_usuario_por_whatsapp",
            return_value={"id": 1, "nome": "Jackson Rodrigues", "tipo": "aluno"},
        ), patch("super_agente_simples.perguntar_ollama", return_value="fallback nao esperado"):
            resp = self.client.post(
                "/api/whatsapp-webhook",
                json={"numero": "5511999999999", "mensagem": "quero declaração de matrícula"},
            )

        self.assertEqual(resp.status_code, 200)
        resposta = resp.get_json().get("resposta", "").lower()
        self.assertIn("declaração", resposta)
        self.assertIn("protocolo", resposta)


if __name__ == "__main__":
    unittest.main()
