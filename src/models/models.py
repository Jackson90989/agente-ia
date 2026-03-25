"""
Modelos de domínio (Domain Models)
Representam as entidades principais do sistema
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class StatusAluno(Enum):
    """Estados possíveis de um aluno"""
    PRE_CADASTRO = "Pré-cadastro"
    ATIVO = "Ativo"
    INATIVO = "Inativo"
    CANCELADO = "Cancelado"


class EtapaCadastro(Enum):
    """Etapas do processo de cadastro"""
    INICIO = "inicio"
    NOME = "nome"
    EMAIL = "email"
    CPF = "cpf"
    TELEFONE = "telefone"
    NASCIMENTO = "nascimento"
    ENDERECO = "endereco"
    CIDADE = "cidade"
    ESTADO = "estado"
    CURSO = "curso"
    SENHA = "senha"
    CONFIRMAR_SENHA = "confirmar_senha"
    CONSENTIMENTO = "consentimento"
    COMUNICACAO = "comunicacao"
    CONCLUIDO = "concluido"


@dataclass
class Aluno:
    """Modelo de um aluno"""
    id: Optional[int] = None
    nome: str = ""
    email: str = ""
    cpf: str = ""
    telefone: str = ""
    whatsapp: str = ""
    data_nascimento: Optional[str] = None
    endereco: str = ""
    cidade: str = ""
    estado: str = ""
    curso_interesse: str = ""
    senha: str = ""
    status: StatusAluno = StatusAluno.PRE_CADASTRO
    consentimento_dados: bool = False
    consentimento_comunicacao: bool = False
    data_consentimento: Optional[datetime] = None
    data_cadastro: Optional[datetime] = None
    
    def eh_valido(self) -> bool:
        """Valida se aluno tem dados mínimos obrigatórios"""
        return all([
            self.nome,
            self.email,
            self.cpf,
            self.telefone
        ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'cpf': self.cpf,
            'telefone': self.telefone,
            'whatsapp': self.whatsapp,
            'data_nascimento': self.data_nascimento,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'estado': self.estado,
            'curso_interesse': self.curso_interesse,
            'status': self.status.value,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
        }


@dataclass
class Conversa:
    """Modelo de uma conversa de cadastro"""
    id: Optional[int] = None
    session_id: str = ""
    numero_whatsapp: str = ""
    etapa: EtapaCadastro = EtapaCadastro.INICIO
    dados: Dict[str, Any] = field(default_factory=dict)
    historico: list = field(default_factory=list)
    criada_em: Optional[datetime] = None
    atualizada_em: Optional[datetime] = None
    
    def adicionar_mensagem(self, role: str, conteudo: str):
        """Adiciona mensagem ao histórico"""
        self.historico.append({
            'timestamp': datetime.now(),
            'role': role,
            'conteudo': conteudo
        })
    
    def obter_contexto_resumido(self, ultimas_n: int = 5) -> str:
        """Retorna últimas N mensagens como contexto"""
        return "\n".join([
            f"{m['role']}: {m['conteudo']}"
            for m in self.historico[-ultimas_n:]
        ])


@dataclass
class Usuario:
    """Modelo de um usuário (secretaria, admin)"""
    id: Optional[int] = None
    nome: str = ""
    email: str = ""
    tipo: str = "secretaria"  # 'secretaria', 'admin'
    telefone: Optional[str] = None
    ativo: bool = True
    data_criacao: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'tipo': self.tipo,
            'telefone': self.telefone,
            'ativo': self.ativo,
        }


@dataclass
class Mensagem:
    """Modelo de uma mensagem"""
    id: Optional[int] = None
    numero_whatsapp: str = ""
    conteudo: str = ""
    tipo: str = "texto"  # 'texto', 'imagem', 'documento'
    de_usuario: bool = True  # True se do usuário, False se do bot
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'numero_whatsapp': self.numero_whatsapp,
            'conteudo': self.conteudo,
            'tipo': self.tipo,
            'de_usuario': self.de_usuario,
            'timestamp': self.timestamp.isoformat(),
        }
