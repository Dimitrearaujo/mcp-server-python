# mcp-server-python

[![CI](https://github.com/dimitrearaujo/mcp-server-python/actions/workflows/ci.yml/badge.svg)](https://github.com/dimitrearaujo/mcp-server-python/actions/workflows/ci.yml)

MCP server em Python com tools customizadas para agentes IA — knowledge base local, contexto de negócio e sumarização de texto.

---

## O que é MCP?

**MCP (Model Context Protocol)** é um protocolo aberto criado pela Anthropic que permite que agentes IA (como o Claude) se conectem a servidores externos para acessar dados, executar ações e usar ferramentas customizadas.

Com um MCP server, você pode:

- Dar ao Claude acesso à sua base de conhecimento interna
- Expor dados de negócio sem precisar colocá-los no prompt manualmente
- Criar pipelines de processamento de texto reutilizáveis
- Integrar qualquer sistema externo como uma "tool" para o agente

Este servidor expõe **3 tools prontas**:

| Tool | O que faz |
|------|-----------|
| `search_knowledge_base` | Busca documentos relevantes numa SQLite local via cosine similarity |
| `summarize_text` | Formata um prompt de sumarização (sem chamar API — retorna o prompt pronto) |
| `get_business_context` | Retorna contexto de negócio de um JSON local |

---

## Instalação

### Pré-requisitos

- Python 3.12+
- pip

### Passos

```bash
# Clone o repositório
git clone https://github.com/dimitrearaujo/mcp-server-python.git
cd mcp-server-python

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env conforme necessário
```

### Configuração

Edite o arquivo `.env`:

```env
BUSINESS_CONTEXT_PATH=./business_context.json
KB_DATABASE_PATH=./data/knowledge_base.db
KB_MAX_RESULTS=5
```

Edite o `business_context.json` com os dados da sua empresa.

---

## Como rodar

```bash
python server.py
```

O servidor inicia via **stdio** e aguarda chamadas de tools. A saída de log vai para stderr.

---

## Integração com Claude Desktop

Adicione ao seu `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-server-python": {
      "command": "python",
      "args": ["/caminho/para/mcp-server-python/server.py"],
      "env": {
        "BUSINESS_CONTEXT_PATH": "/caminho/para/mcp-server-python/business_context.json",
        "KB_DATABASE_PATH": "/caminho/para/mcp-server-python/data/knowledge_base.db"
      }
    }
  }
}
```

**Localização do arquivo de configuração:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

Após reiniciar o Claude Desktop, as tools aparecerão disponíveis no chat.

---

## Populando a Knowledge Base

Use o Python interativo ou um script para inserir documentos:

```python
from mcp_server.knowledge_base import KnowledgeBase

kb = KnowledgeBase(db_path="./data/knowledge_base.db")

# Inserir documentos
kb.insert(
    title="Política de Atendimento",
    content="Atendemos de segunda a sexta, das 8h às 18h. Urgências via WhatsApp.",
    category="atendimento"
)

kb.insert(
    title="Tabela de Preços",
    content="Consulta simples: R$ 150. Consulta especializada: R$ 250. Retorno em 30 dias: gratuito.",
    category="precos"
)

# Buscar
results = kb.search("qual o preço da consulta?")
for r in results:
    print(f"[{r['score']:.2f}] {r['title']}: {r['content'][:80]}...")
```

---

## Como adicionar novas tools

1. **Defina a tool** em `mcp_server/tools.py`, adicionando um item a `TOOL_DEFINITIONS`:

```python
{
    "name": "minha_nova_tool",
    "description": "Descrição clara do que a tool faz.",
    "input_schema": {
        "type": "object",
        "properties": {
            "parametro": {"type": "string", "description": "..."},
        },
        "required": ["parametro"],
    },
}
```

2. **Implemente o handler** assíncrono:

```python
async def handle_minha_nova_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    resultado = faz_algo(arguments["parametro"])
    return [TextContent(type="text", text=json.dumps(resultado, ensure_ascii=False))]
```

3. **Registre o handler** no dicionário `TOOL_HANDLERS`:

```python
TOOL_HANDLERS = {
    # ... tools existentes ...
    "minha_nova_tool": handle_minha_nova_tool,
}
```

4. Pronto. A tool já aparece automaticamente via `list_tools`.

---

## Estrutura do projeto

```
mcp-server-python/
├── .env.example              # Variáveis de ambiente necessárias
├── .gitignore
├── .github/workflows/ci.yml  # CI: syntax check + unit tests
├── README.md
├── requirements.txt
├── server.py                 # Entry point — inicia o MCP server via stdio
├── mcp_server/
│   ├── __init__.py
│   ├── tools.py              # Definição e registro das 3 tools
│   ├── knowledge_base.py     # SQLite + busca vetorial TF cosine
│   ├── context.py            # Carrega business_context.json
│   └── prompts.py            # Templates de prompt
├── business_context.json     # Contexto de negócio (edite com seus dados)
└── data/                     # Pasta para arquivos da KB (SQLite)
    └── .gitkeep
```

---

## Tecnologias

- **[MCP SDK](https://github.com/modelcontextprotocol/python-sdk)** — protocolo de comunicação com agentes IA
- **SQLite** — armazenamento local da knowledge base (sem servidor externo)
- **TF Cosine Similarity** — busca vetorial simples sem embeddings externos
- **python-dotenv** — gerenciamento de variáveis de ambiente

---

## Desenvolvido por

**CD Tech** — Automação e Agentes IA para Pequenos Negócios
Fortaleza, CE — Brasil
[cd-tech-lp.pages.dev](https://cd-tech-lp.pages.dev)

---

<details>
<summary>🇺🇸 English</summary>

# mcp-server-python

[![CI](https://github.com/dimitrearaujo/mcp-server-python/actions/workflows/ci.yml/badge.svg)](https://github.com/dimitrearaujo/mcp-server-python/actions/workflows/ci.yml)

Python MCP server with custom tools for AI agents — local knowledge base, business context and text summarization.

---

## What is MCP?

**MCP (Model Context Protocol)** is an open protocol created by Anthropic that lets AI agents (like Claude) connect to external servers to access data, execute actions and use custom tools.

With an MCP server, you can:

- Give Claude access to your internal knowledge base
- Expose business data without having to paste it into the prompt manually
- Build reusable text-processing pipelines
- Integrate any external system as a "tool" for the agent

This server exposes **3 ready-to-use tools**:

| Tool | What it does |
|------|-----------|
| `search_knowledge_base` | Searches relevant documents in a local SQLite via cosine similarity |
| `summarize_text` | Formats a summarization prompt (no API call — returns the ready prompt) |
| `get_business_context` | Returns business context from a local JSON file |

---

## Installation

### Prerequisites

- Python 3.12+
- pip

### Steps

```bash
# Clone the repository
git clone https://github.com/dimitrearaujo/mcp-server-python.git
cd mcp-server-python

# Create and activate the virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env as needed
```

### Configuration

Edit the `.env` file:

```env
BUSINESS_CONTEXT_PATH=./business_context.json
KB_DATABASE_PATH=./data/knowledge_base.db
KB_MAX_RESULTS=5
```

Edit `business_context.json` with your company's data.

---

## How to run

```bash
python server.py
```

The server starts via **stdio** and waits for tool calls. Log output goes to stderr.

---

## Claude Desktop integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mcp-server-python": {
      "command": "python",
      "args": ["/path/to/mcp-server-python/server.py"],
      "env": {
        "BUSINESS_CONTEXT_PATH": "/path/to/mcp-server-python/business_context.json",
        "KB_DATABASE_PATH": "/path/to/mcp-server-python/data/knowledge_base.db"
      }
    }
  }
}
```

**Config file location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

After restarting Claude Desktop, the tools will show up as available in the chat.

---

## Populating the Knowledge Base

Use interactive Python or a script to insert documents:

```python
from mcp_server.knowledge_base import KnowledgeBase

kb = KnowledgeBase(db_path="./data/knowledge_base.db")

# Insert documents
kb.insert(
    title="Support Policy",
    content="We're open Monday to Friday, 8am to 6pm. Urgent requests via WhatsApp.",
    category="support"
)

kb.insert(
    title="Price Table",
    content="Basic consultation: $30. Specialized consultation: $50. Follow-up within 30 days: free.",
    category="pricing"
)

# Search
results = kb.search("what's the price of a consultation?")
for r in results:
    print(f"[{r['score']:.2f}] {r['title']}: {r['content'][:80]}...")
```

---

## How to add new tools

1. **Define the tool** in `mcp_server/tools.py`, adding an entry to `TOOL_DEFINITIONS`:

```python
{
    "name": "my_new_tool",
    "description": "Clear description of what the tool does.",
    "input_schema": {
        "type": "object",
        "properties": {
            "parameter": {"type": "string", "description": "..."},
        },
        "required": ["parameter"],
    },
}
```

2. **Implement the async handler**:

```python
async def handle_my_new_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    result = do_something(arguments["parameter"])
    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]
```

3. **Register the handler** in the `TOOL_HANDLERS` dict:

```python
TOOL_HANDLERS = {
    # ... existing tools ...
    "my_new_tool": handle_my_new_tool,
}
```

4. Done. The tool automatically shows up via `list_tools`.

---

## Project structure

```
mcp-server-python/
├── .env.example              # Required environment variables
├── .gitignore
├── .github/workflows/ci.yml  # CI: syntax check + unit tests
├── README.md
├── requirements.txt
├── server.py                 # Entry point — starts the MCP server via stdio
├── mcp_server/
│   ├── __init__.py
│   ├── tools.py              # Definition and registration of the 3 tools
│   ├── knowledge_base.py     # SQLite + TF cosine vector search
│   ├── context.py            # Loads business_context.json
│   └── prompts.py            # Prompt templates
├── business_context.json     # Business context (edit with your data)
└── data/                     # Folder for KB files (SQLite)
    └── .gitkeep
```

---

## Technologies

- **[MCP SDK](https://github.com/modelcontextprotocol/python-sdk)** — communication protocol with AI agents
- **SQLite** — local knowledge base storage (no external server)
- **TF Cosine Similarity** — simple vector search without external embeddings
- **python-dotenv** — environment variable management

---

## Developed by

**CD Tech** — AI Automation & Agents for Small Businesses
Fortaleza, Brazil
[cd-tech-lp.pages.dev](https://cd-tech-lp.pages.dev)

</details>

---

[← Back to profile](https://github.com/Dimitrearaujo)
