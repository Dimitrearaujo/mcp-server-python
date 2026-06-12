"""
context.py — Carrega e expõe o contexto de negócio a partir de um JSON local.
"""

import json
import os
from typing import Any, Dict, Optional


_DEFAULT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "business_context.json",
)


class BusinessContext:
    """Gerencia o contexto de negócio carregado de um arquivo JSON."""

    def __init__(self, path: Optional[str] = None):
        self.path = path or os.getenv("BUSINESS_CONTEXT_PATH", _DEFAULT_PATH)
        self._data: Optional[Dict[str, Any]] = None

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            raise FileNotFoundError(
                f"Arquivo de contexto não encontrado: {self.path}\n"
                f"Crie o arquivo business_context.json na raiz do projeto."
            )
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    @property
    def data(self) -> Dict[str, Any]:
        """Retorna os dados do contexto (lazy load com cache)."""
        if self._data is None:
            self._data = self._load()
        return self._data

    def reload(self) -> None:
        """Força recarregamento do arquivo."""
        self._data = self._load()

    def get(self, key: str, default: Any = None) -> Any:
        """Acessa uma chave de nível raiz do JSON."""
        return self.data.get(key, default)

    def as_text(self) -> str:
        """Retorna o contexto formatado como string JSON indentada."""
        return json.dumps(self.data, ensure_ascii=False, indent=2)

    def company_name(self) -> str:
        """Atalho para o nome da empresa."""
        empresa = self.data.get("empresa", {})
        return empresa.get("nome", "Empresa")

    def services_summary(self) -> str:
        """Retorna resumo dos serviços disponíveis."""
        servicos = self.data.get("servicos", [])
        if not servicos:
            return "Nenhum serviço cadastrado."
        lines = []
        for s in servicos:
            preco = s.get("preco_base")
            preco_str = f" — R$ {preco:,.0f}" if preco else ""
            lines.append(f"• {s.get('nome', '?')}: {s.get('descricao', '')}{preco_str}")
        return "\n".join(lines)

    def faq_as_text(self) -> str:
        """Retorna FAQ formatado como texto."""
        faq = self.data.get("faq", [])
        if not faq:
            return "Nenhuma FAQ cadastrada."
        lines = []
        for item in faq:
            lines.append(f"P: {item.get('pergunta', '')}")
            lines.append(f"R: {item.get('resposta', '')}\n")
        return "\n".join(lines)
