"""
Configurações globais da aplicação (Singleton Pattern)
"""

from pathlib import Path
from typing import Optional


class Settings:
    """
    Gerenciador único de configurações
    Implementa Singleton Pattern para garantir uma única instância
    """
    
    _instance: Optional['Settings'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa configurações na primeira instância"""
        # Paths
        self.BASE_DIR = Path("C:/Users/JacksonRodrigues/Downloads/Python-3.10.19")
        self.SRC_DIR = self.BASE_DIR / "src"
        self.DB_PATH = self.BASE_DIR / "database" / "escola.db"
        self.LOGS_DIR = self.BASE_DIR / "logs"
        
        # Criar diretórios se não existirem
        self.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # OLLAMA
        self.OLLAMA_URL = "http://localhost:11434/api/generate"
        self.OLLAMA_MODEL = "llama3.2:3b"
        self.OLLAMA_TIMEOUT = 60
        self.OLLAMA_CONNECT_TIMEOUT = 10
        
        # WhatsApp
        self.WHATSAPP_API_URL = "http://localhost:3000"
        self.WHATSAPP_API_TIMEOUT = 15
        
        # Flask
        self.SECRET_KEY = "dev-secret-key-change-in-production"
        self.SESSION_TIMEOUT = 3600  # 1 hora
        
        # Logging
        self.LOG_LEVEL = "INFO"
        self.LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # Feature flags
        self.DEBUG = True
        self.ENABLE_OLLAMA = True
        self.ENABLE_CACHE = True
    
    @classmethod
    def get_instance(cls) -> 'Settings':
        """Obtém a única instância (padrão Singleton)"""
        return cls()
