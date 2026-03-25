"""
Cliente para comunicação com o MCP Server
"""

import json
import subprocess
import requests
from typing import Dict, Any, Optional
import asyncio
from pathlib import Path


class MCPClient:
    """Cliente para comunicação com o MCP Server"""
    
    def __init__(self, mode="stdio", server_path=None, host="localhost", port=8000):
        self.mode = mode
        self.server_path = server_path
        self.host = host
        self.port = port
        self.process = None
        
        if mode == "stdio" and server_path:
            self._start_stdio_server()
    
    def _start_stdio_server(self):
        """Inicia o servidor MCP em modo stdio"""
        try:
            self.process = subprocess.Popen(
                ["python", str(self.server_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"MCP server started (PID: {self.process.pid})")
        except Exception as e:
            print(f"Error starting MCP server: {e}")
    
    def call_tool_stdio(self, tool_name: str, arguments: Dict) -> str:
        """Chama uma ferramenta via stdio"""
        
        if not self.process:
            return "Error: MCP server is not running"
        
        # Formatar chamada no protocolo MCP
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }
        
        try:
            # Enviar requisição
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            # Ler resposta
            response = self.process.stdout.readline()
            result = json.loads(response)
            
            if "result" in result:
                return result["result"]["content"][0]["text"]
            else:
                return f"Error: {result.get('error', 'Invalid response')}"
                
        except Exception as e:
            return f"Error communicating with MCP: {e}"
    
    def call_tool_http(self, tool_name: str, arguments: Dict) -> str:
        """Chama uma ferramenta via HTTP"""
        
        url = f"http://{self.host}:{self.port}/tool"
        
        try:
            response = requests.post(
                url,
                json={
                    "tool": tool_name,
                    "arguments": arguments
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.text
            else:
                return f"HTTP error {response.status_code}: {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "Error: could not connect to MCP server"
        except Exception as e:
            return f"HTTP call error: {e}"
    
    def call_tool(self, tool_name: str, arguments: Dict) -> str:
        """Chama uma ferramenta (modo automático)"""
        
        if self.mode == "http":
            return self.call_tool_http(tool_name, arguments)
        else:
            return self.call_tool_stdio(tool_name, arguments)
    
    def stop(self):
        """Para o servidor MCP"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("MCP server stopped")
    
    def list_available_tools(self) -> list:
        """Lista ferramentas disponíveis"""
        # Implementar se necessário
        return [
            "listar_alunos",
            "consultar_aluno",
            "perguntar_sobre_aluno",
            "resumo_academico",
            "listar_cursos",
            "listar_materias_disponiveis",
            "criar_requerimento",
            "cadastrar_novo_aluno",
            "buscar_pagamentos",
            "diagnosticar_banco"
        ]


# Função auxiliar para uso simplificado
def call_mcp_tool(tool_name: str, **kwargs) -> str:
    """Função simplificada para chamar ferramentas MCP"""
    
    client = MCPClient(
        mode="stdio",
        server_path=Path(__file__).parent.parent / "mcp_server" / "escola_server.py"
    )
    
    result = client.call_tool(tool_name, kwargs)
    client.stop()
    
    return result