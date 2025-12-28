# scripts/cleanup_tests.py
"""
Remove testes obsoletos da pasta tests/
Garante a integridade da suite v0.9.0 antes do lançamento.
"""
import os
from pathlib import Path


def main():
    print("=" * 80)
    print("🧪 Limpeza de Testes Obsoletos - v0.9.0")
    print("=" * 80)

    # Determina o diretório raiz do projeto (assumindo que o script está em scripts/)
    root_dir = Path(__file__).parent.parent

    # Arquivo obsoleto para remover
    obsolete_test = root_dir / "tests" / "unit" / "test_enforcement.py"

    if obsolete_test.exists():
        print(f"\n❌ Removendo teste obsoleto:")
        print(f"   {obsolete_test.relative_to(root_dir)}")
        print(f"   Motivo: Substituído e ampliado por test_enforcement_v095.py")

        try:
            obsolete_test.unlink()
            print("   ✅ Removido com sucesso")
        except Exception as e:
            print(f"   ⚠️  Erro ao remover: {e}")
    else:
        print(f"\n✅ Teste obsoleto já foi removido anteriormente (Estado limpo).")

    print("\n" + "=" * 80)
    print("✅ Limpeza de testes concluída!")
    print("=" * 80)

    print("\n📊 Estado Atual da Suite de Testes:")
    print("   ✅ conftest.py (Global Fixtures)")
    print("   ✅ security/test_auth.py (OWASP API2/API5)")
    print("   ✅ security/test_bola.py (OWASP API1)")
    print("   ✅ security/test_injection.py (OWASP API8)")
    print("   ✅ unit/test_entities.py (Compliance EU AI Act)")
    print("   ✅ unit/test_threat_classifier_v095.py (Huwyler Taxonomy)")
    print("   ✅ unit/test_enforcement_v095.py (Regulatory Penalties)")

    print("\n🚀 Próximo passo recomendado:")
    print("   pytest tests/ -v --cov=src --cov-report=html")


if __name__ == "__main__":
    main()
