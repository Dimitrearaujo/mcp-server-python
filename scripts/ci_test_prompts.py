"""
CI: Testa templates de prompt — summarize_prompt, context_query_prompt, knowledge_base_prompt.
Nao chama nenhuma API.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.prompts import summarize_prompt, context_query_prompt, knowledge_base_prompt

texto = "Python e uma linguagem de programacao versatil e poderosa."

# summarize_prompt basico
prompt = summarize_prompt(texto)
assert isinstance(prompt, str), "Retorno nao e string"
assert texto in prompt, "Texto nao esta no prompt"
assert "TEXTO:" in prompt, "Secao TEXTO: nao encontrada"
assert "RESUMO:" in prompt, "Secao RESUMO: nao encontrada"
assert len(prompt) > len(texto), "Prompt mais curto que o texto original"

# com max_words
prompt_limited = summarize_prompt(texto, max_words=50)
assert "50" in prompt_limited, "max_words nao aparece no prompt"

# com language customizado
prompt_en = summarize_prompt(texto, language="ingles")
assert "ingles" in prompt_en, "Idioma nao aplicado no prompt"

# context_query_prompt
ctx_prompt = context_query_prompt("Qual o preco?", '{"preco": 497}')
assert isinstance(ctx_prompt, str), "context_query_prompt nao e string"
assert "Qual o preco?" in ctx_prompt, "Pergunta nao esta no prompt"
assert "497" in ctx_prompt, "Contexto nao esta no prompt"

# knowledge_base_prompt sem resultados
kb_prompt_empty = knowledge_base_prompt("teste", [])
assert "Nenhum documento" in kb_prompt_empty, "Mensagem de vazio nao encontrada"

# knowledge_base_prompt com resultados
results = [{"title": "Doc 1", "content": "Conteudo do documento 1", "score": 0.9}]
kb_prompt = knowledge_base_prompt("teste", results)
assert "Doc 1" in kb_prompt, "Titulo do doc nao esta no prompt"
assert "0.9" in kb_prompt, "Score nao esta no prompt"

print("PASSOU: prompts — summarize_prompt, context_query_prompt, knowledge_base_prompt OK")
