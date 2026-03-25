import unittest

from src.services.services import ValidacaoService


class TestValidacaoService(unittest.TestCase):
    def test_validar_email(self):
        self.assertTrue(ValidacaoService.validar_email("aluno@faculdade.edu"))
        self.assertFalse(ValidacaoService.validar_email("aluno-faculdade.edu"))

    def test_validar_cpf(self):
        self.assertTrue(ValidacaoService.validar_cpf("12345678901"))
        self.assertTrue(ValidacaoService.validar_cpf("123.456.789-01"))
        self.assertFalse(ValidacaoService.validar_cpf("12345"))

    def test_validar_senha(self):
        valido, _ = ValidacaoService.validar_senha("SenhaBoa123")
        self.assertTrue(valido)

        valido_curta, erro_curta = ValidacaoService.validar_senha("123")
        self.assertFalse(valido_curta)
        self.assertIn("6", erro_curta)

        valido_comum, erro_comum = ValidacaoService.validar_senha("123456")
        self.assertFalse(valido_comum)
        self.assertIn("comum", erro_comum.lower())

    def test_validar_estado(self):
        self.assertTrue(ValidacaoService.validar_estado("SP"))
        self.assertFalse(ValidacaoService.validar_estado("XX"))

    def test_validar_curso(self):
        self.assertTrue(ValidacaoService.validar_curso("engenharia civil"))
        self.assertFalse(ValidacaoService.validar_curso("astrologia"))


if __name__ == "__main__":
    unittest.main()
