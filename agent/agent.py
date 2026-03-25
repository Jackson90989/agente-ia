"""
Agente de IA Principal - Com Ollama Embutido
"""

import json
import requests
import socket
import subprocess
import time
import os
import sys
import platform
from typing import Dict, Any, Optional
from datetime import datetime
import threading

from agent.memory import ConversationMemory, LongTermMemory
from agent.planner import ActionPlanner
from agent.tools import MCPClient
from config.config import *


class OllamaManager:
    """Gerenciador do Ollama - inicia e monitora o processo"""
    
    def __init__(self):
        self.process = None
        self.port = 11434
        self.host = "127.0.0.1"
        self.is_running = False
        self.output_thread = None
        
    def check_port_available(self):
        """Verifica se a porta está disponível"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result != 0  # 0 significa porta em uso
        except:
            return True
    
    def is_ollama_running(self):
        """Verifica se o Ollama já está rodando"""
        try:
            response = requests.get(f"http://{self.host}:{self.port}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start(self):
        """Inicia o Ollama se necessário"""
        
        # Verificar se já está rodando
        if self.is_ollama_running():
            print("Ollama is already running")
            self.is_running = True
            return True
        
        # Verificar se a porta está disponível
        if not self.check_port_available():
            print("Port 11434 is in use by another process")
            return False
        
        print("Starting Ollama...")
        
        try:
            # Detectar sistema operacional
            system = platform.system()
            
            if system == "Windows":
                # No Windows, usar criação de processo diferente
                self.process = subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
            else:
                # Linux/Mac
                self.process = subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    start_new_session=True
                )
            
            # Aguardar inicialização
            max_attempts = 30
            for i in range(max_attempts):
                time.sleep(1)
                if self.is_ollama_running():
                    print(f"Ollama started after {i+1} seconds")
                    self.is_running = True
                    
                    # Iniciar thread para ler output (opcional)
                    self.output_thread = threading.Thread(target=self._read_output, daemon=True)
                    self.output_thread.start()
                    
                    # Verificar modelo padrão
                    self.ensure_model(DEFAULT_MODEL)
                    
                    return True
                print(f"Waiting for Ollama... ({i+1}/{max_attempts})")
            
            print("Timeout while starting Ollama")
            return False
            
        except FileNotFoundError:
            print("Ollama not found! Install it first:")
            self.show_installation_instructions()
            return False
        except Exception as e:
            print(f"Error starting Ollama: {e}")
            return False
    
    def ensure_model(self, model_name: str):
        """Garante que o modelo está baixado"""
        try:
            print(f"Checking model {model_name}...")
            
            # Verificar se modelo já existe
            response = requests.get(f"http://{self.host}:{self.port}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    if model["name"].startswith(model_name):
                        print(f"Model {model_name} is already available")
                        return True
            
            # Baixar modelo
            print(f"Downloading model {model_name} (this may take a few minutes)...")
            
            payload = {
                "name": model_name
            }
            
            # Usar stream para mostrar progresso
            response = requests.post(
                f"http://{self.host}:{self.port}/api/pull",
                json=payload,
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if "status" in data:
                                print(f"   {data['status']}")
                            if "completed" in data:
                                print(f"   Progresso: {data.get('completed', 0)}/{data.get('total', 0)}")
                        except:
                            pass
                print(f"Model {model_name} downloaded successfully!")
                return True
            else:
                print(f"Warning: error downloading model: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Warning: error checking model: {e}")
            return False
    
    def show_installation_instructions(self):
        """Mostra instruções de instalação do Ollama"""
        system = platform.system()
        
        print("\n" + "="*50)
        print("INSTALLATION INSTRUCTIONS FOR OLLAMA:")
        print("="*50)
        
        if system == "Windows":
            print("1. Acesse: https://ollama.com/download/windows")
            print("2. Baixe e execute o instalador (OllamaSetup.exe)")
            print("3. Após instalar, abra um novo terminal")
            print("4. Execute: ollama serve")
        elif system == "Darwin":  # macOS
            print("1. Acesse: https://ollama.com/download/mac")
            print("2. Baixe e instale o Ollama")
            print("3. Ou via terminal: curl -fsSL https://ollama.com/install.sh | sh")
        else:  # Linux
            print("1. Via terminal:")
            print("   curl -fsSL https://ollama.com/install.sh | sh")
        
        print("\nApós instalar, execute:")
        print("   ollama pull llama3.2:3b")
        print("="*50)
    
    def stop(self):
        """Para o Ollama"""
        if self.process:
            print("Stopping Ollama...")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.is_running = False
            print("Ollama stopped")
    
    def _read_output(self):
        """Lê output do processo em background"""
        while self.process and self.process.poll() is None:
            try:
                output = self.process.stdout.readline()
                if output:
                    # Opcional: logar output
                    # print(f"[Ollama] {output.decode().strip()}")
                    pass
            except:
                break


class EscolaAgent:
    """Agente principal do sistema escolar com Ollama embutido"""
    
    def __init__(self, user_id: str = "default", auto_start_ollama: bool = True):
        self.user_id = user_id
        self.auto_start_ollama = auto_start_ollama
        
        # Gerenciador do Ollama
        self.ollama_manager = OllamaManager()
        
        # Inicializar componentes
        self.memory = ConversationMemory(max_history=MAX_HISTORY)
        self.ltm = LongTermMemory(DB_PATH.parent / "memory.db")
        self.planner = ActionPlanner()
        
        # Inicializar cliente MCP
        self.mcp = MCPClient(
            mode=MCP_MODE,
            server_path=MCP_SERVER_PATH,
            host=MCP_HOST,
            port=MCP_PORT
        )
        
        # Verificar/iniciar Ollama
        self.ollama_available = self._setup_ollama()
        
        # Carregar contexto do usuário
        self.load_user_context()
        
        print(f"\nAgent initialized for user: {user_id}")
        print(f"Mode: {'Full AI' if self.ollama_available else 'Tools only'}")
        if not self.ollama_available:
            print("   Digite /ollama para ver instruções de instalação")
    
    def _setup_ollama(self):
        """Configura o Ollama (inicia se necessário)"""
        
        # Verificar se já está rodando
        if self.ollama_manager.is_ollama_running():
            print("Ollama detected")
            return True
        
        # Se auto_start_ollama estiver ativado, tentar iniciar
        if self.auto_start_ollama:
            print("Trying to start Ollama automatically...")
            return self.ollama_manager.start()
        
        return False
    
    def load_user_context(self):
        """Carrega contexto do usuário da memória de longo prazo"""
        user_info = self.ltm.recall(self.user_id)
        context = {}
        for item in user_info:
            context[item["key"]] = item["value"]
        self.memory.context = context
    
    def query_llm(self, prompt: str, model: str = DEFAULT_MODEL) -> str:
        """Consulta o LLM via Ollama"""
        
        if not self.ollama_available:
            return None
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": TEMPERATURE
                }
            }
            
            response = requests.post(
                f"{OLLAMA_URL}/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                print(f"Warning: LLM error: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            self.ollama_available = False
            print("Warning: connection to Ollama lost")
            return None
        except Exception as e:
            print(f"Warning: error querying LLM: {e}")
            return None
    
    def format_tool_results(self, tool_results: list) -> str:
        """Formata os resultados das ferramentas"""
        if not tool_results:
            return "Nenhum dado encontrado no sistema."
        
        formatted = []
        for i, result in enumerate(tool_results, 1):
            clean_result = result.replace("**", "").replace("__", "")
            formatted.append(f"Dados {i}:\n{clean_result}")
        
        return "\n\n".join(formatted)
    
    def generate_response_without_llm(self, query: str, tool_results: list) -> str:
        """Gera resposta sem LLM"""
        if not tool_results:
            return "Não encontrei informações sobre isso no sistema."
        
        for result in tool_results:
            if result and "não encontrado" not in result.lower():
                clean = result.replace("**", "").replace("__", "")
                return clean
        
        return "Consultei o sistema mas não encontrei dados específicos."
    
    def process_query(self, query: str) -> str:
        """Processa uma consulta do usuário"""
        
        self.memory.add("user", query)
        actions = self.planner.plan_actions(query, self.memory.context)
        
        tool_results = []
        executed_tools = []
        
        for action in actions:
            if action["tool"] and action["confidence"] > 0.5:
                print(f"Executing: {action['tool']} (confidence: {action['confidence']:.2f})")
                result = self.mcp.call_tool(action["tool"], action["args"])
                if result and "Error" not in result:
                    tool_results.append(result)
                    executed_tools.append(action["tool"])
        
        if not executed_tools:
            return "Não entendi sua pergunta. Digite /help para ver os comandos."
        
        # Tentar usar LLM
        if self.ollama_available:
            combined_results = self.format_tool_results(tool_results)
            history = self.memory.get_recent(5)
            
            prompt = f"""Você é um assistente de secretaria escolar.

Histórico:
{history}

Pergunta atual: {query}

Dados do sistema:
{combined_results}

Com base APENAS nos dados acima, responda a pergunta de forma clara e objetiva.
Use linguagem natural e profissional."""

            response = self.query_llm(prompt)
            if response:
                self.memory.add("assistant", response, {"actions": executed_tools})
                return response
        
        # Fallback
        fallback = self.generate_response_without_llm(query, tool_results)
        self.memory.add("assistant", fallback, {"actions": executed_tools, "mode": "fallback"})
        return fallback
    
    def handle_conversation(self, user_input: str) -> str:
        """Gerencia a conversa completa"""
        
        # Comandos especiais
        cmd = user_input.lower()
        
        if cmd in ["/help", "/ajuda"]:
            return self.show_help()
        
        if cmd == "/clear":
            self.memory.clear()
            return "Memory cleared!"
        
        if cmd == "/memory":
            return self.memory.get_recent(20)
        
        if cmd == "/status":
            return self.show_status()
        
        if cmd == "/ollama":
            return self.show_ollama_status()
        
        if cmd == "/reiniciar":
            return self.restart_ollama()
        
        return self.process_query(user_input)
    
    def show_status(self) -> str:
        """Mostra status do sistema"""
        status = f"""
**SYSTEM STATUS:**

**Ollama:** {'Online' if self.ollama_available else 'Offline'}
   • Porta: 11434
   • Modelo: {DEFAULT_MODEL}

**Memory:** {len(self.memory.history)} messages
**MCP Server:** {'Active' if self.mcp.process else 'Inactive'}
**User:** {self.user_id}

**Database:** {DB_PATH}
    • Exists: {'Yes' if DB_PATH.exists() else 'No'}
"""
        return status
    
    def show_ollama_status(self) -> str:
        """Mostra status do Ollama e opções"""
        
        if self.ollama_available:
            return """
**Ollama is running!**

Comandos úteis:
• /reiniciar - Reinicia o Ollama
• /status - Ver status completo
• /help - Ajuda
"""
        else:
            return """
**Ollama is not running**

Para instalar e iniciar:
1. Digite /install para ver instruções
2. Ou execute: ollama serve em outro terminal

Comandos:
• /install - Mostra instruções de instalação
• /status - Verificar novamente
"""
    
    def restart_ollama(self) -> str:
        """Reinicia o Ollama"""
        
        if self.ollama_manager.process:
            self.ollama_manager.stop()
            time.sleep(2)
        
        if self.ollama_manager.start():
            self.ollama_available = True
            return "Ollama restarted successfully!"
        else:
            return "Failed to restart Ollama"
    
    def show_help(self) -> str:
        """Mostra ajuda"""
        help_text = """
**SCHOOL ASSISTANT - HELP**

📚 **Consultas:**
• "Listar alunos"
• "Ver informações do aluno [ID]"
• "Notas do aluno [ID]"
• "Cursos disponíveis"
• "Matérias do curso [ID]"

💰 **Financeiro:**
• "Pagamentos do aluno [ID]"
• "Boletos pendentes"

📋 **Requisições:**
• "Criar requerimento para aluno [ID] do tipo [tipo]"

🛠️ **COMANDOS DO SISTEMA:**
• /help     - Mostra esta ajuda
• /clear    - Limpa memória
• /memory   - Mostra histórico
• /status   - Status do sistema
• /ollama   - Status do Ollama
• /reiniciar- Reinicia Ollama
• /sair     - Encerra

**Dica:** Faça perguntas diretas e específicas!
"""
        return help_text
    
    def close(self):
        """Finaliza o agente"""
        self.mcp.stop()
        self.ollama_manager.stop()
        print("👋 Agente finalizado")


# Função de conveniência
def criar_agente(user_id: str = "default", auto_start_ollama: bool = True) -> EscolaAgent:
    """Cria um novo agente com Ollama automático"""
    return EscolaAgent(user_id, auto_start_ollama)