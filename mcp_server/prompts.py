"""
prompts.py — Templates de prompt para as tools do MCP server.

Nenhuma chamada de API aqui: apenas formatação de strings.
"""

from typing import Optional


def summarize_prompt(text: str, max_words: Optional[int] = None, language: str = "português") -> str:
    """
    Gera prompt formatado para sumarização de texto.

    Args:
        text: Texto a ser sumarizado.
        max_words: Limite de palavras para o resumo (opcional).
        language: Idioma do resumo.

    Returns:
        Prompt pronto para enviar a um LLM.
    """
    word_instruction = f" com no máximo {max_words} palavras" if max_words else ""
    return (
        f"Você é um assistente especializado em sumarização.\n\n"
        f"Resuma o texto abaixo em {language}{word_instruction}. "
        f"O resumo deve capturar os pontos principais de forma clara e objetiva.\n\n"
        f"TEXTO:\n{text}\n\n"
        f"RESUMO:"
    )


def context_query_prompt(question: str, context: str) -> str:
    """
    Gera prompt para responder perguntas com base em contexto de negócio.

    Args:
        question: Pergunta do usuário.
        context: Contexto JSON serializado como string.

    Returns:
        Prompt pronto para enviar a um LLM.
    """
    return (
        f"Você é um assistente de negócios da CD Tech.\n\n"
        f"Use o contexto abaixo para responder à pergunta do usuário.\n"
        f"Se a resposta não estiver no contexto, diga que não sabe.\n\n"
        f"CONTEXTO:\n{context}\n\n"
        f"PERGUNTA: {question}\n\n"
        f"RESPOSTA:"
    )


def knowledge_base_prompt(query: str, results: list) -> str:
    """
    Gera prompt para responder com base em resultados da knowledge base.

    Args:
        query: Consulta original do usuário.
        results: Lista de documentos retornados pela KB.

    Returns:
        Prompt formatado com os documentos encontrados.
    """
    if not results:
        docs_section = "Nenhum documento relevante encontrado."
    else:
        docs_section = "\n\n".join(
            f"[{i+1}] {r['title']} (score: {r['score']})\n{r['content']}"
            for i, r in enumerate(results)
        )

    return (
        f"Você é um assistente com acesso à base de conhecimento.\n\n"
        f"DOCUMENTOS RELEVANTES:\n{docs_section}\n\n"
        f"PERGUNTA: {query}\n\n"
        f"Responda com base nos documentos acima. Cite as fontes pelo número quando relevante.\n\n"
        f"RESPOSTA:"
    )
