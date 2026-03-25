import tempfile
import unittest
from pathlib import Path

from src.services.context_memory_service import MemoryContextService


class TestMemoryContextService(unittest.TestCase):
    def test_salvar_e_obter_contexto(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "memoria_test.db"
            service = MemoryContextService(db_path=db_path)

            ok1 = service.salvar_interacao("5511999999999", "publico", "user", "oi")
            ok2 = service.salvar_interacao("5511999999999", "publico", "assistant", "ola")

            self.assertTrue(ok1)
            self.assertTrue(ok2)

            contexto = service.obter_contexto_recente("5511999999999", limite=5)
            self.assertEqual(len(contexto), 2)
            self.assertEqual(contexto[0]["role"], "user")
            self.assertEqual(contexto[1]["role"], "assistant")

    def test_limpar_contexto_usuario(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "memoria_test.db"
            service = MemoryContextService(db_path=db_path)

            service.salvar_interacao("5511888888888", "aluno", "user", "minhas notas")
            removidos = service.limpar_contexto_usuario("5511888888888")
            contexto = service.obter_contexto_recente("5511888888888", limite=5)

            self.assertEqual(removidos, 1)
            self.assertEqual(contexto, [])


if __name__ == "__main__":
    unittest.main()
