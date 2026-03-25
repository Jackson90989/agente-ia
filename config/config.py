"""
Configurações do Agente Escolar
"""

import os
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent.parent.absolute()
DB_PATH = BASE_DIR / "database" / "escola.db"
MCP_SERVER_PATH = BASE_DIR / "mcp_server" / "escola_server.py"

# Modelos de IA
OLLAMA_URL = "http://localhost:11434/api"
DEFAULT_MODEL = "llama3.2:3b"  # Modelo leve para testes
ADVANCED_MODEL = "llama3.1:8b"  # Modelo mais potente

# Configurações do agente
MAX_HISTORY = 50  # Máximo de mensagens na memória
TEMPERATURE = 0.7  # Criatividade do modelo

# MCP Server
MCP_MODE = "stdio"  # stdio ou http
MCP_HOST = "localhost"
MCP_PORT = 8000

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "agent.log"

# Garantir que diretórios existam
for dir_path in [BASE_DIR / "database", BASE_DIR / "logs"]:
    dir_path.mkdir(exist_ok=True)