"""
CI: Verifica sintaxe de todos os arquivos .py do projeto.
Usado pelo workflow do GitHub Actions.
"""
import ast
import os
import sys

SKIP_DIRS = {".venv", ".git", "__pycache__", "node_modules"}

errors = []
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for dirpath, dirnames, filenames in os.walk(root_dir):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fname in filenames:
        if not fname.endswith(".py"):
            continue
        path = os.path.join(dirpath, fname)
        with open(path, "r", encoding="utf-8") as fh:
            src = fh.read()
        try:
            ast.parse(src)
            print(f"OK: {path}")
        except SyntaxError as e:
            print(f"ERRO: {path} — {e}")
            errors.append(path)

if errors:
    print(f"\n{len(errors)} arquivo(s) com erro de sintaxe.")
    sys.exit(1)

print(f"\nTodos os arquivos Python OK.")
