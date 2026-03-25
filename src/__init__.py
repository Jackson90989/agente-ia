"""
Agente de Atendimento Acadêmico via WhatsApp
Arquitetura baseada em Design Patterns para nível TCC
"""

__version__ = "1.0.0"
__author__ = "Jackson Rodrigues"

from src.config.settings import Settings
from src.config.logger import LoggerFactory

# Inicializar configurações globais
settings = Settings()
logger_factory = LoggerFactory()
