"""
CI: Testa KnowledgeBase — insert, search, tokenize, cosine similarity, delete.
Sem dependencias externas alem da stdlib.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.knowledge_base import KnowledgeBase, _tokenize, _tf_vector, _cosine_similarity

tmpdir = tempfile.mkdtemp()
try:
    db_path = os.path.join(tmpdir, "test_kb.db")
    kb = KnowledgeBase(db_path=db_path)

    # Insert
    doc_id = kb.insert("Clinica Veterinaria", "Atendemos caes e gatos com carinho e profissionalismo.", "vet")
    assert doc_id == 1, f"Esperado id=1, obtido {doc_id}"

    kb.insert("Academia Fitness", "Treinamentos personalizados para todos os niveis.", "academia")
    kb.insert("Studio de Danca", "Aulas de ballet, jazz e contemporaneo.", "studio")

    assert kb.count() == 3, f"Esperado 3 docs, obtido {kb.count()}"

    # Search
    results = kb.search("veterinario cachorro", max_results=2)
    assert len(results) > 0, "Search nao retornou resultados"
    assert "title" in results[0], "Resultado sem campo title"
    assert "content" in results[0], "Resultado sem campo content"
    assert "score" in results[0], "Resultado sem campo score"
    assert results[0]["score"] >= 0.0, f"Score invalido: {results[0]['score']}"
    assert results[0]["title"] == "Clinica Veterinaria", f"Resultado inesperado: {results[0]['title']}"

    # Tokenizer
    tokens = _tokenize("Ola mundo teste 123.")
    assert "ola" in tokens, f"Tokenizador falhou: {tokens}"
    assert "123" in tokens, f"Tokenizador ignorou numero: {tokens}"

    # Cosine similarity
    va = _tf_vector(["python", "python", "code"])
    vb = _tf_vector(["python", "code", "test"])
    sim = _cosine_similarity(va, vb)
    assert 0.0 < sim <= 1.0, f"Similaridade fora do range: {sim}"

    # Delete
    deleted = kb.delete(1)
    assert deleted, "Delete retornou False"
    assert kb.count() == 2, f"Esperado 2 docs apos delete, obtido {kb.count()}"

    print("PASSOU: knowledge_base — insert, search, tokenize, cosine, delete OK")

finally:
    # Fecha conexoes SQLite (necessario no Windows para liberar lock de arquivo)
    try:
        del kb
    except Exception:
        pass
    import shutil
    try:
        shutil.rmtree(tmpdir, ignore_errors=True)
    except Exception:
        pass
