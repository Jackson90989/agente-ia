"""
Services - Camada de serviços que orquestra a lógica de negócio
Integra repositories, strategies e outros componentes
"""

from typing import Optional, Dict, Any
from src.models.models import Aluno, Conversa, EtapaCadastro
from src.repositories.repositories import AlunoRepository, ConversaRepository
from src.strategies.message_strategies import (
    MessageProcessorFactory, 
    PublicoStrategy
)
from src.config.logger import LoggerFactory


class UserIdentificationService:
    """Serviço para identificar usuários"""
    
    def __init__(self):
        self.aluno_repo = AlunoRepository()
        self.logger = LoggerFactory.criar_logger('user_identification')
    
    def identificar_usuario(self, numero_whatsapp: str) -> Dict[str, Any]:
        """
        Identifica o tipo de usuário baseado no número
        
        Returns:
            Dict com 'tipo' e 'usuario'
        """
        # Buscar como aluno
        aluno = self.aluno_repo.buscar_por_whatsapp(numero_whatsapp)
        
        if aluno:
            self.logger.info(f"Usuário identificado como aluno: {aluno.nome}")
            return {
                'tipo': 'aluno',
                'usuario': aluno,
                'identificado': True
            }
        
        # Padrão: público
        self.logger.info(f"Usuário não identificado, tratando como público")
        return {
            'tipo': 'publico',
            'usuario': None,
            'identificado': False
        }


class MessageProcessingService:
    """Serviço para processar mensagens"""
    
    def __init__(self):
        self.logger = LoggerFactory.criar_logger('message_processing')
        self.user_service = UserIdentificationService()
    
    def processar_mensagem(self, numero_whatsapp: str, mensagem: str) -> str:
        """
        Processa uma mensagem seguindo padrão Strategy
        
        Args:
            numero_whatsapp: Número do remetente
            mensagem: Conteúdo da mensagem
        
        Returns:
            Resposta para o usuário
        """
        self.logger.info(f"Processando mensagem de {numero_whatsapp}")
        
        # Identificar usuário
        identificacao = self.user_service.identificar_usuario(numero_whatsapp)
        tipo_usuario = identificacao['tipo']
        
        # Obter estratégia apropriada
        strategy = MessageProcessorFactory.criar_strategy(tipo_usuario)
        
        # Processar com estratégia
        try:
            resposta = strategy.processar(mensagem, numero_whatsapp)
            self.logger.info(f"Resposta gerada para {tipo_usuario}")
            return resposta
        except Exception as e:
            self.logger.error(f"Erro ao processar: {e}")
            return "❌ Desculpe, ocorreu um erro. Tente novamente."


class CadastroService:
    """Serviço para gerenciar cadastros de alunos"""
    
    def __init__(self):
        self.aluno_repo = AlunoRepository()
        self.conversa_repo = ConversaRepository()
        self.logger = LoggerFactory.criar_logger('cadastro_service')
    
    def iniciar_cadastro(self, numero_whatsapp: str) -> Conversa:
        """
        Inicia um novo processo de cadastro
        
        Returns:
            Conversa criada
        """
        session_id = f"whatsapp_{numero_whatsapp}"
        
        conversa = Conversa(
            session_id=session_id,
            numero_whatsapp=numero_whatsapp,
            etapa=EtapaCadastro.NOME
        )
        
        self.conversa_repo.criar(conversa)
        self.logger.info(f"Cadastro iniciado para {numero_whatsapp}")
        
        return conversa
    
    def obter_cadastro_em_andamento(self, numero_whatsapp: str) -> Optional[Conversa]:
        """Obtém cadastro em andamento se existir"""
        session_id = f"whatsapp_{numero_whatsapp}"
        conversa = self.conversa_repo.buscar_por_session_id(session_id)
        
        if conversa and conversa.etapa != EtapaCadastro.CONCLUIDO:
            return conversa
        
        return None
    
    def finalizar_cadastro(self, conversa: Conversa) -> bool:
        """
        Finaliza cadastro criando aluno no banco
        
        Returns:
            True se sucesso, False se erro
        """
        try:
            aluno = self._criar_aluno_de_conversa(conversa)
            
            if not aluno.eh_valido():
                self.logger.warning(f"Aluno inválido: {aluno.email}")
                return False
            
            sucesso = self.aluno_repo.criar(aluno)
            
            if sucesso:
                conversa.etapa = EtapaCadastro.CONCLUIDO
                self.conversa_repo.atualizar(conversa)
                self.logger.info(f"Cadastro concluído: {aluno.email}")
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Erro ao finalizar cadastro: {e}")
            return False
    
    @staticmethod
    def _criar_aluno_de_conversa(conversa: Conversa) -> Aluno:
        """Converte dados de conversa em objeto Aluno"""
        aluno = Aluno(
            nome=conversa.dados.get('nome', ''),
            email=conversa.dados.get('email', ''),
            cpf=conversa.dados.get('cpf', ''),
            telefone=conversa.dados.get('telefone', ''),
            whatsapp=conversa.numero_whatsapp,
            data_nascimento=conversa.dados.get('data_nascimento'),
            endereco=conversa.dados.get('endereco', ''),
            cidade=conversa.dados.get('cidade', ''),
            estado=conversa.dados.get('estado', ''),
            curso_interesse=conversa.dados.get('curso_interesse', ''),
            senha=conversa.dados.get('senha', ''),
        )
        return aluno


class ValidacaoService:
    """Serviço para validações"""
    
    ESTADOS_VALIDOS = {
        'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES',
        'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR',
        'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
        'SP', 'SE', 'TO'
    }
    
    CURSOS_VALIDOS = [
        'administração', 'engenharia civil', 'engenharia da computação',
        'direito', 'medicina', 'psicologia', 'arquitetura',
        'design', 'pedagoga', 'enfermagem'
    ]
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato de email"""
        import re
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida se CPF tem 11 dígitos"""
        cpf_limpo = cpf.replace('.', '').replace('-', '')
        return len(cpf_limpo) == 11 and cpf_limpo.isdigit()
    
    @staticmethod
    def validar_senha(senha: str) -> tuple[bool, str]:
        """
        Valida força da senha
        
        Returns:
            (é_válida, mensagem_erro)
        """
        if len(senha) < 6:
            return False, "Senha deve ter mínimo 6 caracteres"
        
        if senha.isdigit() and len(set(senha)) == 1:
            return False, "Senha muito simples (números iguais)"
        
        senhas_comuns = ['123456', 'password', 'qwerty', 'abc123']
        if senha.lower() in senhas_comuns:
            return False, "Senha muito comum"
        
        return True, ""
    
    @staticmethod
    def validar_estado(estado: str) -> bool:
        """Valida se estado é uma sigla válida"""
        return estado.upper() in ValidacaoService.ESTADOS_VALIDOS
    
    @staticmethod
    def validar_curso(curso: str) -> bool:
        """Valida se curso está na lista"""
        return any(c in curso.lower() for c in ValidacaoService.CURSOS_VALIDOS)
