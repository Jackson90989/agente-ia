"""
Configuração de logging estruturado
"""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class LoggerFactory:
    """
    Factory para criar loggers estruturados
    Centraliza configuração de logging em um único lugar
    """
    
    _loggers = {}
    
    @staticmethod
    def criar_logger(nome: str, nivel: str = "INFO") -> logging.Logger:
        """
        Cria ou retorna um logger existente
        
        Args:
            nome: Nome do logger (ex: 'cadastro', 'ollama')
            nivel: Nível de logging (DEBUG, INFO, WARNING, ERROR)
        
        Returns:
            Logger configurado
        """
        if nome in LoggerFactory._loggers:
            return LoggerFactory._loggers[nome]
        
        logger = logging.getLogger(nome)
        logger.setLevel(getattr(logging, nivel))
        logger.propagate = False
        
        # Handler para arquivo com rotação
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        handler = RotatingFileHandler(
            log_dir / f"{nome}.log",
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # Formato detalhado
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Handler para console (apenas em DEBUG)
        if nivel == "DEBUG":
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        LoggerFactory._loggers[nome] = logger
        return logger
    
    @staticmethod
    def get_logger(nome: str) -> Optional[logging.Logger]:
        """Retorna um logger existente ou None"""
        return LoggerFactory._loggers.get(nome)
