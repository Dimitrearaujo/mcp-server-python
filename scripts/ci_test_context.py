"""
CI: Testa BusinessContext — carrega JSON e expoe metodos uteis.
Usa arquivo temporario para nao depender do business_context.json real.
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.context import BusinessContext

ctx_data = {
    "empresa": {"nome": "Teste Corp", "segmento": "Tecnologia"},
    "servicos": [{"nome": "Serv A", "descricao": "Descricao A", "preco_base": 100}],
    "faq": [{"pergunta": "O que voces fazem?", "resposta": "Automatizamos."}],
    "diferenciais": ["Rapido", "Barato"],
}

tmp_fd, tmp_path = tempfile.mkstemp(suffix=".json")
try:
    with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
        json.dump(ctx_data, f, ensure_ascii=False)

    ctx = BusinessContext(path=tmp_path)

    assert ctx.company_name() == "Teste Corp", f"Nome errado: {ctx.company_name()}"

    services = ctx.services_summary()
    assert "Serv A" in services, "Servico nao aparece no summary"
    assert "R$" in services or "R$" in services or "100" in services, "Preco nao formatado"

    faq = ctx.faq_as_text()
    assert "O que voces fazem?" in faq, "Pergunta FAQ nao encontrada"
    assert "Automatizamos." in faq, "Resposta FAQ nao encontrada"

    text = ctx.as_text()
    assert isinstance(text, str), "as_text() nao e string"
    parsed = json.loads(text)
    assert parsed["empresa"]["nome"] == "Teste Corp", "JSON parseado com dados errados"

    ctx2 = BusinessContext(path=tmp_path)
    val = ctx2.get("diferenciais")
    assert val == ["Rapido", "Barato"], f"get() retornou valor errado: {val}"

    print("PASSOU: context — BusinessContext carrega JSON e expoe metodos OK")
finally:
    try:
        os.unlink(tmp_path)
    except OSError:
        pass
