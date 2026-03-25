"""
Authorization matrix for domain actions.
Keep business permissions in code, not in prompts.
"""

POLICY_MATRIX = {
    "aluno": {
        "CONSULTAR_DADOS",
        "CONSULTAR_NOTAS",
        "CONSULTAR_GRADE",
        "CONSULTAR_HISTORICO",
        "GERAR_DECLARACAO",
        "CONSULTAR_FINANCEIRO",
        "SOLICITAR_TRANCAMENTO",
        "SOLICITAR_CANCELAMENTO",
        "SOLICITAR_SEGUNDA_VIA_BOLETO",
        "AJUSTAR_GRADE_INCLUSAO",
        "AJUSTAR_GRADE_REMOCAO",
    },
    "secretaria": {
        "CONSULTAR_TOTAL_ALUNOS",
        "LISTAR_ALUNOS",
        "LISTAR_NOVOS_CADASTROS",
        "CONSULTAR_DADOS",
        "CONSULTAR_NOTAS",
        "CONSULTAR_GRADE",
        "CONSULTAR_HISTORICO",
        "GERAR_DECLARACAO",
        "CONSULTAR_FINANCEIRO",
        "SOLICITAR_TRANCAMENTO",
        "SOLICITAR_CANCELAMENTO",
        "SOLICITAR_SEGUNDA_VIA_BOLETO",
        "AJUSTAR_GRADE_INCLUSAO",
        "AJUSTAR_GRADE_REMOCAO",
    },
}
