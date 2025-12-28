# scripts/audit_rag_memory.py
"""
Auditoria técnica do módulo rag_memory.py
Verifica se há dependências pesadas (LangChain, ChromaDB, Torch, etc.)
"""
import ast
import sys
from pathlib import Path


def audit_module(file_path: Path):
    """
    Analisa estaticamente os imports e a complexidade do módulo rag_memory.py.
    Não executa o código, apenas lê a árvore sintática (AST).
    """
    if not file_path.exists():
        return None

    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    # Detecção de bibliotecas pesadas que não queremos no Core v0.9.0
    heavy_libs = [
        'langchain', 'chromadb', 'openai', 'transformers',
        'torch', 'sentence_transformers', 'pinecone', 'faiss',
        'llama_index', 'anthropic'
    ]

    heavy_deps_found = [
        imp for imp in imports
        if any(heavy in str(imp).lower() for heavy in heavy_libs)
    ]

    return {
        "lines": len(source.splitlines()),
        "imports": imports,
        "heavy_deps": heavy_deps_found,
        "classes": [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)],
        "functions": [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    }


def main():
    target_file = Path("src/compliance/analytics/rag_memory.py")

    print("=" * 80)
    print(f"🔬 AUDITORIA TÉCNICA: {target_file}")
    print("=" * 80)

    result = audit_module(target_file)

    if not result:
        print(f"❌ Arquivo não encontrado: {target_file}")
        print("   ✅ Ação: Nada a fazer (arquivo já não existe ou caminho incorreto).")
        return 0

    print(f"\n📊 Estatísticas:")
    print(f"   - Linhas de código: {result['lines']}")
    print(f"   - Classes definidas: {len(result['classes'])} → {result['classes']}")
    print(f"   - Funções definidas: {len(result['functions'])}")
    print(f"   - Total de imports: {len(result['imports'])}")

    print(f"\n📦 Imports Detectados:")
    for imp in result['imports'][:10]:  # Mostra apenas primeiros 10
        print(f"   - {imp}")
    if len(result['imports']) > 10:
        print(f"   ... e mais {len(result['imports']) - 10} imports")

    print("\n🔍 Verificação de Dependências Pesadas:")
    if result['heavy_deps']:
        print("   🚨 ALERTA VERMELHO: Dependências pesadas detectadas!")
        for dep in result['heavy_deps']:
            print(f"      🔴 {dep}")
        print("\n⛔ VEREDITO DO ARQUITETO: REMOVER DA v0.9.0")
        print("   Motivo: Estas bibliotecas aumentam o tamanho do Docker em >2GB.")
        print("   Ação: Deletar src/compliance/analytics/rag_memory.py antes da limpeza.")
        print("\n🛠️  Comando:")
        print(f"   rm {target_file}  # Linux/Mac")
        print(f"   del {target_file}  # Windows CMD")
        return 1
    else:
        print("   ✅ Nenhuma dependência pesada (LangChain/Torch/OpenAI) detectada.")
        print("\n🟢 VEREDITO DO ARQUITETO: APROVADO PARA v0.9.0")
        print("   Motivo: O módulo é leve e usa apenas bibliotecas padrão ou leves.")
        print("   Ação: Pode prosseguir com a limpeza.")
        return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
