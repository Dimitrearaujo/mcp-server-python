"""
CI: Testa que as 3 tools estao registradas com name, description e input_schema.
Nao instancia o servidor MCP — testa apenas os metadados.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.tools import TOOL_DEFINITIONS, TOOL_HANDLERS

expected_names = {"search_knowledge_base", "summarize_text", "get_business_context"}

# Verifica que as 3 tools estao definidas
defined_names = {t["name"] for t in TOOL_DEFINITIONS}
assert defined_names == expected_names, f"Tools faltando: {expected_names - defined_names}"

# Verifica metadados de cada tool
for tool in TOOL_DEFINITIONS:
    name = tool.get("name", "?")
    assert "name" in tool, f"Tool sem name: {tool}"
    assert "description" in tool, f"Tool sem description: {name}"
    assert "input_schema" in tool, f"Tool sem input_schema: {name}"
    assert len(tool["description"]) > 10, f"Description muito curta: {name}"
    schema = tool["input_schema"]
    assert schema.get("type") == "object", f"input_schema nao e object: {name}"
    assert "properties" in schema, f"input_schema sem properties: {name}"

# Verifica que handlers existem e sao callable
for name in expected_names:
    assert name in TOOL_HANDLERS, f"Handler nao encontrado: {name}"
    assert callable(TOOL_HANDLERS[name]), f"Handler nao e callable: {name}"

print("PASSOU: tools — 3 tools com name/description/schema/handler OK")
