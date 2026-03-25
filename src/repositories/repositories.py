"""
Repository Pattern - Abstração da camada de dados
Separa a lógica de negócio do acesso aos dados
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from src.models.models import Aluno, Conversa, Usuario
import sqlite3
from src.config.settings import Settings


class Repository(ABC):
    """Interface base para todos os repositórios"""
    
    @abstractmethod
    def criar(self, entidade: Any) -> bool:
        """Cria uma nova entidade"""
        pass
    
    @abstractmethod
    def buscar_por_id(self, id: int) -> Optional[Any]:
        """Busca entidade por ID"""
        pass
    
    @abstractmethod
    def atualizar(self, entidade: Any) -> bool:
        """Atualiza uma entidade existente"""
        pass
    
    @abstractmethod
    def deletar(self, id: int) -> bool:
        """Deleta uma entidade"""
        pass
    
    @abstractmethod
    def listar_todos(self) -> List[Any]:
        """Lista todas as entidades"""
        pass


class AlunoRepository(Repository):
    """Repository para Alunos"""
    
    def __init__(self):
        self.settings = Settings.get_instance()
    
    def _get_connection(self):
        """Obtém conexão com o banco"""
        conn = sqlite3.connect(self.settings.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def criar(self, aluno: Aluno) -> bool:
        """
        Cria um novo aluno
        Pattern: Repository + DTO (Data Transfer Object)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alunos (
                    nome, email, cpf, telefone, whatsapp, data_nascimento,
                    endereco, cidade, estado, curso_interesse, senha,
                    consentimento_dados, consentimento_comunicacao,
                    data_consentimento, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aluno.nome, aluno.email, aluno.cpf, aluno.telefone,
                aluno.whatsapp, aluno.data_nascimento, aluno.endereco,
                aluno.cidade, aluno.estado, aluno.curso_interesse,
                aluno.senha, aluno.consentimento_dados,
                aluno.consentimento_comunicacao, aluno.data_consentimento,
                aluno.status.value
            ))
            
            aluno.id = cursor.lastrowid
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False
    
    def buscar_por_id(self, id: int) -> Optional[Aluno]:
        """Busca aluno por ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM alunos WHERE id = ?", (id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._map_row_to_aluno(row)
            return None
        except:
            return None
    
    def buscar_por_email(self, email: str) -> Optional[Aluno]:
        """Busca aluno por email"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM alunos WHERE email = ?", (email,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._map_row_to_aluno(row)
            return None
        except:
            return None
    
    def buscar_por_whatsapp(self, whatsapp: str) -> Optional[Aluno]:
        """Busca aluno por WhatsApp"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM alunos WHERE whatsapp = ?", (whatsapp,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._map_row_to_aluno(row)
            return None
        except:
            return None
    
    def atualizar(self, aluno: Aluno) -> bool:
        """Atualiza aluno existente"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE alunos SET
                    nome=?, email=?, cpf=?, telefone=?, whatsapp=?,
                    data_nascimento=?, endereco=?, cidade=?, estado=?,
                    curso_interesse=?, status=?, consentimento_dados=?,
                    consentimento_comunicacao=?
                WHERE id = ?
            """, (
                aluno.nome, aluno.email, aluno.cpf, aluno.telefone,
                aluno.whatsapp, aluno.data_nascimento, aluno.endereco,
                aluno.cidade, aluno.estado, aluno.curso_interesse,
                aluno.status.value, aluno.consentimento_dados,
                aluno.consentimento_comunicacao, aluno.id
            ))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def deletar(self, id: int) -> bool:
        """Deleta aluno (soft delete - marca como cancelado)"""
        try:
            aluno = self.buscar_por_id(id)
            if aluno:
                aluno.status.CANCELADO
                return self.atualizar(aluno)
            return False
        except:
            return False
    
    def listar_todos(self) -> List[Aluno]:
        """Lista todos os alunos"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM alunos ORDER BY data_cadastro DESC")
            rows = cursor.fetchall()
            conn.close()
            
            return [self._map_row_to_aluno(row) for row in rows]
        except:
            return []
    
    def listar_ativos(self) -> List[Aluno]:
        """Lista alunos ativos"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM alunos 
                WHERE status = ? 
                ORDER BY data_cadastro DESC
            """, ('Ativo',))
            rows = cursor.fetchall()
            conn.close()
            
            return [self._map_row_to_aluno(row) for row in rows]
        except:
            return []
    
    @staticmethod
    def _map_row_to_aluno(row) -> Aluno:
        """Mapeia row do DB para objeto Aluno"""
        return Aluno(
            id=row['id'],
            nome=row['nome'],
            email=row['email'],
            cpf=row['cpf'],
            telefone=row['telefone'],
            whatsapp=row.get('whatsapp', ''),
            data_nascimento=row.get('data_nascimento'),
            endereco=row.get('endereco', ''),
            cidade=row.get('cidade', ''),
            estado=row.get('estado', ''),
            curso_interesse=row.get('curso_interesse', ''),
            status=row.get('status', 'Pré-cadastro')
        )


class ConversaRepository(Repository):
    """Repository para Conversas de Cadastro"""
    
    def __init__(self):
        self.settings = Settings.get_instance()
    
    def _get_connection(self):
        """Obtém conexão com o banco"""
        conn = sqlite3.connect(self.settings.DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    def criar(self, conversa: Conversa) -> bool:
        """Cria uma nova conversa"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO conversas_cadastro (
                    session_id, etapa, dados, ip, user_agent
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                conversa.session_id,
                conversa.etapa.value,
                str(conversa.dados),
                "whatsapp",
                "WhatsApp"
            ))
            
            conversa.id = cursor.lastrowid
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def buscar_por_session_id(self, session_id: str) -> Optional[Conversa]:
        """Busca conversa por session_id"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM conversas_cadastro 
                WHERE session_id = ? 
                ORDER BY atualizada_em DESC LIMIT 1
            """, (session_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._map_row_to_conversa(row)
            return None
        except:
            return None
    
    def buscar_por_id(self, id: int) -> Optional[Conversa]:
        """Busca conversa por ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM conversas_cadastro WHERE id = ?", (id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self._map_row_to_conversa(row)
            return None
        except:
            return None
    
    def atualizar(self, conversa: Conversa) -> bool:
        """Atualiza conversa"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE conversas_cadastro 
                SET etapa = ?, dados = ?, atualizada_em = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (conversa.etapa.value, str(conversa.dados), conversa.id))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def deletar(self, id: int) -> bool:
        """Deleta conversa"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversas_cadastro WHERE id = ?", (id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def listar_todos(self) -> List[Conversa]:
        """Lista todas as conversas"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM conversas_cadastro 
                ORDER BY atualizada_em DESC
            """)
            rows = cursor.fetchall()
            conn.close()
            
            return [self._map_row_to_conversa(row) for row in rows]
        except:
            return []
    
    @staticmethod
    def _map_row_to_conversa(row) -> Conversa:
        """Mapeia row do DB para objeto Conversa"""
        import json
        from src.models.models import EtapaCadastro
        
        try:
            dados = json.loads(row['dados'])
        except:
            dados = {}
        
        return Conversa(
            id=row['id'],
            session_id=row['session_id'],
            etapa=EtapaCadastro(row['etapa']),
            dados=dados,
            criada_em=row['criada_em'],
            atualizada_em=row['atualizada_em']
        )
