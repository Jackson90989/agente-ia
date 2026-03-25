"""
Planejador - Decide quais ferramentas usar baseado na pergunta
"""

import re
from typing import Dict, List, Tuple, Optional


class ActionPlanner:
    """Planeja as ações do agente baseado na entrada do usuário"""
    
    def __init__(self):
        # Padrões de intenção
        self.intent_patterns = {
            "listar_alunos": [
                r"listar.*alunos",
                r"mostrar.*alunos",
                r"quem s[ãa]o os alunos",
                r"todos os alunos"
            ],
            "consultar_aluno": [
                r"consulta.*aluno",
                r"informaç[ãõ]es do aluno",
                r"dados do aluno",
                r"aluno.*id[:\s]*(\d+)"
            ],
            "resumo_academico": [
                r"notas?",
                r"desempenho",
                r"boletim",
                r"m[eé]dia",
                r"disciplinas",
                r"matrículas?",
                r"rendimento"
            ],
            "listar_cursos": [
                r"cursos?",
                r"gradua[çc][ãa]o",
                r"matérias disponíveis",
                r"o que estudar"
            ],
            "buscar_pagamentos": [
                r"pagamentos?",
                r"boletos?",
                r"mensalidade",
                r"d[ée]bitos",
                r"financeiro"
            ],
            "criar_requerimento": [
                r"requerimento",
                r"solicitar",
                r"pedir",
                r"declara[çc][ãa]o",
                r"certid[ãa]o"
            ],
            "cadastrar_novo_aluno": [
                r"cadastrar.*aluno",
                r"novo.*aluno",
                r"inscrever",
                r"matricular"
            ]
        }
        
        # Extração de entidades
        self.entity_patterns = {
            "aluno_id": r"aluno[:\s]*(\d+)|id[:\s]*(\d+)",
            "curso_id": r"curso[:\s]*(\d+)|curso[:\s]*([a-zA-Z\s]+)",
            "nome": r"nome[:\s]*([a-zA-ZÀ-ÿ\s]+)",
            "email": r"[\w\.-]+@[\w\.-]+\.\w+"
        }
    
    def detect_intent(self, query: str) -> List[Tuple[str, float]]:
        """Detecta as intenções na query do usuário"""
        
        query_lower = query.lower()
        intents = []
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    # Calcular confiança básica
                    confidence = 0.8  # Confiança base
                    
                    # Aumentar confiança se match exato
                    if re.search(r"\b" + pattern + r"\b", query_lower):
                        confidence = 0.95
                    
                    intents.append((intent, confidence))
                    break
        
        return intents
    
    def extract_entities(self, query: str) -> Dict[str, any]:
        """Extrai entidades da query"""
        
        entities = {}
        
        for entity, pattern in self.entity_patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                # Pegar o primeiro grupo que não é None
                for group in match.groups():
                    if group:
                        entities[entity] = group.strip()
                        break
        
        return entities
    
    def plan_actions(self, query: str, context: Dict = None) -> List[Dict]:
        """Planeja as ações baseado na query e contexto"""
        
        intents = self.detect_intent(query)
        entities = self.extract_entities(query)
        
        actions = []
        
        for intent, confidence in intents:
            action = {
                "tool": intent,
                "confidence": confidence,
                "args": {}
            }
            
            # Adicionar entidades relevantes
            if "aluno_id" in entities and intent in ["consultar_aluno", "resumo_academico", 
                                                     "buscar_pagamentos", "criar_requerimento"]:
                action["args"]["aluno_id"] = int(entities["aluno_id"])
            
            if "curso_id" in entities and intent == "listar_materias_disponiveis":
                action["args"]["curso_id"] = int(entities["curso_id"])
            
            if "nome" in entities and intent == "cadastrar_novo_aluno":
                action["args"]["nome"] = entities["nome"]
            
            actions.append(action)
        
        # Se não detectou intenção clara, retornar None
        if not actions:
            return [{
                "tool": None,
                "confidence": 0.0,
                "args": {}
            }]
        
        return actions
    
    def create_prompt_with_context(self, query: str, tool_results: str) -> str:
        """Cria um prompt para o LLM com contexto"""
        
        prompt = f"""Você é um assistente de secretaria escolar especializado.

Pergunta do usuário: {query}

Dados obtidos do sistema:
{tool_results}

Com base nos dados acima, responda a pergunta do usuário de forma clara, educada e profissional.
Se não houver dados suficientes, explique isso ao usuário e sugira o próximo passo.

Formato da resposta:
- Seja conciso mas completo
- Use linguagem natural
- Destaque informações importantes
- Se for uma lista, apresente de forma organizada
"""
        
        return prompt