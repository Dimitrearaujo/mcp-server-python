"""
server.py — Entry point do MCP Server.

Inicia o servidor MCP via stdio (padrão para integração com Claude Desktop e agentes).

Uso:
    python server.py

O servidor aguarda chamadas de tools via stdin e responde via stdout,
seguindo o protocolo MCP (Model Context Protocol).
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Carrega variáveis de ambiente do .env (se existir)
load_dotenv()

# Importa e registra as tools
from mcp_server.tools import register_tools

APP_NAME = "mcp-server-python"
APP_VERSION = "1.0.0"


async def main() -> None:
    server = Server(APP_NAME)
    register_tools(server)

    print(f"[{APP_NAME} v{APP_VERSION}] Servidor MCP iniciado via stdio.", file=sys.stderr)
    print(f"[{APP_NAME}] Tools disponíveis: search_knowledge_base, summarize_text, get_business_context", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
