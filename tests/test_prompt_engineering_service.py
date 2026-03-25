import unittest

from src.services.prompt_engineering_service import PromptEngineeringService


class TestPromptEngineeringService(unittest.TestCase):
    def test_construir_system_prompt_publico(self):
        prompt = PromptEngineeringService.construir_system_prompt("publico", {})
        self.assertIn("atendimento ao publico", prompt.lower())

    def test_construir_system_prompt_aluno(self):
        prompt = PromptEngineeringService.construir_system_prompt(
            "aluno",
            {"curso_interesse": "direito"},
            {"aluno_nome": "Carlos"},
        )
        self.assertIn("carlos", prompt.lower())
        self.assertIn("contexto do aluno", prompt.lower())

    def test_construir_prompt_usuario_com_memoria(self):
        memoria = [
            {"role": "user", "mensagem": "quais cursos existem?"},
            {"role": "assistant", "mensagem": "temos direito, medicina e engenharia"},
        ]
        prompt = PromptEngineeringService.construir_prompt_usuario("e valores?", memoria)
        self.assertIn("historico recente", prompt.lower())
        self.assertIn("mensagem atual do usuario", prompt.lower())
        self.assertIn("e valores?", prompt.lower())


if __name__ == "__main__":
    unittest.main()
