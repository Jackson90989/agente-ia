import unittest
from unittest.mock import patch

from src.services.services import MessageProcessingService


class _FakeStrategy:
    def processar(self, mensagem, numero_whatsapp):
        return f"ok:{numero_whatsapp}:{mensagem}"


class TestMessageProcessingIntegration(unittest.TestCase):
    @patch("src.services.services.MessageProcessorFactory.criar_strategy")
    @patch("src.services.services.UserIdentificationService.identificar_usuario")
    def test_processar_mensagem_orquestra_strategy(self, mock_identificar, mock_factory):
        mock_identificar.return_value = {
            "tipo": "publico",
            "usuario": None,
            "identificado": False,
        }
        mock_factory.return_value = _FakeStrategy()

        service = MessageProcessingService()
        resposta = service.processar_mensagem("5511999999999", "quero me cadastrar")

        self.assertEqual(resposta, "ok:5511999999999:quero me cadastrar")
        mock_identificar.assert_called_once_with("5511999999999")
        mock_factory.assert_called_once_with("publico")


if __name__ == "__main__":
    unittest.main()
