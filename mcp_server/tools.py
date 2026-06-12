"""
tools.py — Definição e registro das tools MCP.

Cada tool é uma função assíncrona decorada com @mcp.tool().
O servidor MCP expõe essas tools automaticamente via stdio.
"""

import os
import json
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

from .knowledge_base import KnowledgeBase
from .context import BusinessContext
from .prompts import summarize_prompt, context_query_prompt, knowledge_base_prompt


# ---------------------------------------------------------------------------
# Instâncias compartilhadas (singletons por processo)
# ---------------------------------------------------------------------------

_kb: Optional[KnowledgeBase] = None
_ctx: Optional[BusinessContext] = None


def _get_kb() -> KnowledgeBase:
    global _kb
    if _kb is None:
        db_path = os.getenv("KB_DATABASE_PATH", "./data/knowledge_base.db")
        _kb = KnowledgeBase(db_path=db_path)
    return _kb


def _get_ctx() -> BusinessContext:
    global _ctx
    if _ctx is None:
        _ctx = BusinessContext()
    return _ctx


# ---------------------------------------------------------------------------
# Definições das tools (metadados — usados para registro e testes)
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "search_knowledge_base",
        "description": (
            "Busca documentos relevantes na base de conhecimento local usando "
            "similaridade textual (TF cosine). Retorna os documentos mais "
            "relevantes e um prompt formatado para o LLM responder com base neles."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Texto ou pergunta a buscar na knowledge base.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Número máximo de documentos a retornar (padrão: 5).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "summarize_text",
        "description": (
            "Gera um prompt formatado para sumarização de texto. "
            "Não chama nenhuma API — retorna o prompt pronto para enviar ao LLM. "
            "Útil para pipelines de sumarização em cadeia."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Texto a ser sumarizado.",
                },
                "max_words": {
                    "type": "integer",
                    "description": "Limite de palavras para o resumo (opcional).",
                },
                "language": {
                    "type": "string",
                    "description": "Idioma do resumo (padrão: português).",
                    "default": "português",
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "get_business_context",
        "description": (
            "Retorna o contexto completo de negócio carregado do arquivo "
            "business_context.json. Pode retornar o contexto completo ou "
            "uma seção específica (empresa, servicos, faq, diferenciais)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": (
                        "Seção específica a retornar: 'empresa', 'servicos', "
                        "'faq', 'diferenciais', ou 'all' para tudo (padrão: 'all')."
                    ),
                    "default": "all",
                },
                "question": {
                    "type": "string",
                    "description": (
                        "Pergunta opcional. Se fornecida, retorna também um "
                        "prompt formatado para o LLM responder com base no contexto."
                    ),
                },
            },
            "required": [],
        },
    },
]


# ---------------------------------------------------------------------------
# Handlers das tools
# ---------------------------------------------------------------------------

async def handle_search_knowledge_base(arguments: Dict[str, Any]) -> List[TextContent]:
    """Executa busca na knowledge base e retorna resultados + prompt."""
    query = arguments["query"]
    max_results = int(arguments.get("max_results", 5))

    kb = _get_kb()
    results = kb.search(query, max_results=max_results)
    prompt = knowledge_base_prompt(query, results)

    output = {
        "results": results,
        "total_found": len(results),
        "prompt": prompt,
    }
    return [TextContent(type="text", text=json.dumps(output, ensure_ascii=False, indent=2))]


async def handle_summarize_text(arguments: Dict[str, Any]) -> List[TextContent]:
    """Formata e retorna o prompt de sumarização."""
    text = arguments["text"]
    max_words = arguments.get("max_words")
    language = arguments.get("language", "português")

    prompt = summarize_prompt(text, max_words=max_words, language=language)

    output = {
        "prompt": prompt,
        "input_length_chars": len(text),
        "input_words_approx": len(text.split()),
    }
    return [TextContent(type="text", text=json.dumps(output, ensure_ascii=False, indent=2))]


async def handle_get_business_context(arguments: Dict[str, Any]) -> List[TextContent]:
    """Retorna contexto de negócio (seção ou completo) + prompt opcional."""
    section = arguments.get("section", "all")
    question = arguments.get("question")

    ctx = _get_ctx()

    if section == "all":
        context_data = ctx.data
    elif section in ctx.data:
        context_data = ctx.data[section]
    else:
        context_data = ctx.data

    context_str = json.dumps(context_data, ensure_ascii=False, indent=2)

    output: Dict[str, Any] = {
        "section": section,
        "context": context_data,
    }

    if question:
        output["prompt"] = context_query_prompt(question, context_str)

    return [TextContent(type="text", text=json.dumps(output, ensure_ascii=False, indent=2))]


# ---------------------------------------------------------------------------
# Mapeamento nome → handler
# ---------------------------------------------------------------------------

TOOL_HANDLERS = {
    "search_knowledge_base": handle_search_knowledge_base,
    "summarize_text": handle_summarize_text,
    "get_business_context": handle_get_business_context,
}


def register_tools(server: Server) -> None:
    """Registra todas as tools no servidor MCP."""

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        return [
            Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["input_schema"],
            )
            for t in TOOL_DEFINITIONS
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        handler = TOOL_HANDLERS.get(name)
        if not handler:
            raise ValueError(f"Tool desconhecida: '{name}'")
        return await handler(arguments)
