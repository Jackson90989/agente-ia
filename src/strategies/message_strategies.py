"""
Strategy Pattern - Strategies para processar diferentes tipos de mensagens
Define diferentes estratégias de processamento que podem ser trocadas em tempo de execução
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.models.models import Aluno, Conversa
from src.repositories.repositories import AlunoRepository, ConversaRepository


class MessageProcessorStrategy(ABC):
    """
    Interface base para estratégias de processamento
    Define o contrato que todas as estratégias devem seguir
    """
    
    @abstractmethod
    def processar(self, mensagem: str, numero_whatsapp: str) -> str:
        """
        Processa uma mensagem e retorna resposta
        
        Args:
            mensagem: Conteúdo da mensagem do usuário
            numero_whatsapp: Número de WhatsApp do remetente
        
        Returns:
            Resposta para o usuário
        """
        pass


class AlunoStrategy(MessageProcessorStrategy):
    """Estratégia para processar mensagens de alunos cadastrados"""
    
    def __init__(self):
        self.aluno_repo = AlunoRepository()
    
    def processar(self, mensagem: str, numero_whatsapp: str) -> str:
        """Processa mensagem de aluno"""
        aluno = self.aluno_repo.buscar_por_whatsapp(numero_whatsapp)
        
        if not aluno:
            return "❌ Não consegui encontrar seus dados."
        
        msg_lower = mensagem.lower()
        
        # Tratamento de comandos específicos
        if any(p in msg_lower for p in ['meus dados', 'minhas informações']):
            return self._formatar_dados_aluno(aluno)
        
        elif any(p in msg_lower for p in ['ajuda', 'menu']):
            return self._retornar_menu_aluno(aluno)
        
        else:
            # Delegaria para OLLAMA ou fallback
            return f"👋 Olá {aluno.nome}! Como posso ajudar?"
    
    @staticmethod
    def _formatar_dados_aluno(aluno: Aluno) -> str:
        """Formata dados do aluno para exibição"""
        return f"""📋 **SEUS DADOS**

👤 Nome: {aluno.nome}
📧 Email: {aluno.email}
📱 Telefone: {aluno.telefone}
📚 Curso: {aluno.curso_interesse}
✅ Status: {aluno.status.value}"""
    
    @staticmethod
    def _retornar_menu_aluno(aluno: Aluno) -> str:
        """Retorna menu de opções para aluno"""
        return """📱 **MENU DO ALUNO**

• *Meus dados* - Ver suas informações
• *Notas* - Consultar notas (em breve)
• *Pagamentos* - Situação financeira (em breve)
• *Ajuda* - Ver este menu novamente

Ou faça uma pergunta normalmente!"""


class SecretariaStrategy(MessageProcessorStrategy):
    """Estratégia para processar mensagens da secretaria"""
    
    def __init__(self):
        self.aluno_repo = AlunoRepository()
    
    def processar(self, mensagem: str, numero_whatsapp: str) -> str:
        """Processa mensagem de secretaria"""
        msg_lower = mensagem.lower()
        
        if any(p in msg_lower for p in ['quantos aluno', 'total']):
            return self._obter_estatisticas()
        
        elif any(p in msg_lower for p in ['lista', 'alunos']):
            return self._listar_alunos()
        
        elif any(p in msg_lower for p in ['menu', 'ajuda']):
            return self._retornar_menu_secretaria()
        
        return "👋 Como posso ajudar?"
    
    def _obter_estatisticas(self) -> str:
        """Retorna estatísticas de alunos"""
        alunos = self.aluno_repo.listar_todos()
        ativos = self.aluno_repo.listar_ativos()
        
        return f"""📊 **ESTATÍSTICAS**

Total de alunos: {len(alunos)}
Alunos ativos: {len(ativos)}
Taxa de ativação: {(len(ativos)/len(alunos)*100):.1f}%"""
    
    def _listar_alunos(self) -> str:
        """Lista alunos recentes"""
        alunos = self.aluno_repo.listar_todos()[:5]
        
        if not alunos:
            return "📭 Nenhum aluno encontrado."
        
        resposta = "📋 **ÚLTIMOS ALUNOS:**\n\n"
        for aluno in alunos:
            resposta += f"• {aluno.nome} - {aluno.email}\n"
        
        return resposta
    
    @staticmethod
    def _retornar_menu_secretaria() -> str:
        """Retorna menu da secretaria"""
        return """👑 **MENU DA SECRETARIA**

• *Quantos alunos?* - Ver total
• *Lista* - Ver últimos alunos
• *Estatísticas* - Ver dados gerais

Ou faça uma pergunta normalmente!"""


class PublicoStrategy(MessageProcessorStrategy):
    """Estratégia para processar mensagens do público (usuários não identificados)"""
    
    def processar(self, mensagem: str, numero_whatsapp: str) -> str:
        """Processa mensagem de usuário não cadastrado"""
        msg_lower = mensagem.lower()
        
        # Verificar se quer iniciar cadastro
        palavras_cadastro = [
            'quero me cadastrar', 'cadastrar', 'matricular',
            'inscrever', 'quero estudar'
        ]
        
        for palavra in palavras_cadastro:
            if palavra in msg_lower:
                return self._iniciar_cadastro()
        
        # Responder perguntas comuns
        if any(p in msg_lower for p in ['contato', 'endereço', 'endereco', 'localização', 'localizacao', 'onde fica']):
            return self._informar_contato()

        elif any(p in msg_lower for p in ['valores', 'preço', 'preco', 'mensalidade', 'mensalidades']):
            return self._informar_valores()
        
        elif any(p in msg_lower for p in ['cursos', 'curso', 'quais cursos', 'faculdade', 'como e a faculdade', 'como é a faculdade']):
            return self._listar_cursos()
        
        return "👋 Olá! Como posso ajudar você?"
    
    @staticmethod
    def _iniciar_cadastro() -> str:
        """Inicia processo de cadastro"""
        return """📝 **Bem-vindo ao cadastro!** 😊

Para começar, qual é o seu **nome completo**?

💡 *Digite seu nome e sobrenome*"""
    
    @staticmethod
    def _listar_cursos() -> str:
        """Lista cursos disponíveis"""
        return """📚 **CURSOS DISPONÍVEIS**

• Administração
• Engenharia Civil
• Engenharia da Computação
• Direito
• Medicina
• Psicologia
• Arquitetura
• Pedagogia

Quer saber mais sobre algum curso?"""
    
    @staticmethod
    def _informar_valores() -> str:
        """Informa valores das mensalidades"""
        return """💰 **VALORES**

Graduação: R$ 800 a R$ 2.500/mês
Bolsas: Até 50% de desconto
Financiamento: FIES disponível

Para uma simulação personalizada, é só chamar!"""
    
    @staticmethod
    def _informar_contato() -> str:
        """Informa dados de contato"""
        return """📍 **LOCALIZAÇÃO**

Endereço: Rua da Faculdade, 123 - Centro
Telefone: (19) 3333-3333
WhatsApp: (19) 99999-9999

Estamos aqui para ajudar! 😊"""


class MessageProcessorFactory:
    """
    Factory Pattern - Cria estratégias de processamento apropriadas
    Encapsula a lógica de criação de estratégias
    """
    
    @staticmethod
    def criar_strategy(tipo_usuario: str) -> MessageProcessorStrategy:
        """
        Cria a estratégia apropriada baseado no tipo de usuário
        
        Args:
            tipo_usuario: 'aluno', 'secretaria', ou 'publico'
        
        Returns:
            Estratégia apropriada
        """
        estrategias = {
            'aluno': AlunoStrategy,
            'secretaria': SecretariaStrategy,
            'publico': PublicoStrategy,
        }
        
        strategy_class = estrategias.get(tipo_usuario, PublicoStrategy)
        return strategy_class()
