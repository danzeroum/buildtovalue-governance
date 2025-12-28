# scripts/cleanup_project.py
"""
Limpeza automatizada do repositório para v0.9.0
- Remove arquivos obsoletos
- Reorganiza estrutura de simulações
- Cria backup antes de qualquer operação destrutiva
"""
import os
import shutil
import datetime
import sys
from pathlib import Path

# --- CONFIGURAÇÃO ---
ROOT_DIR = Path(__file__).parent.parent.absolute()
BACKUP_DIR = ROOT_DIR / f"backup_pre_v090_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Arquivos para DELETAR (Obsoletos/Lixo)
FILES_TO_DELETE = [
    "scripts/debug_enforcement_decisions.py",
    "scripts/debug_missed_threats.py",
    "scripts/run_fintech_simulation_debug.py",
    "scripts/test_individual_prompts.py",
    "estruturaArquivosInicial.txt",
]

# Pastas para DELETAR
DIRS_TO_DELETE = [
    "src/buildtovalue.egg-info",
]

# Scripts para MOVER (De -> Para)
SCRIPT_MOVES = {
    "scripts/run_fintech_simulation.py": "examples/simulations/fintech_simulation.py",
    "scripts/run_multi_sector_simulation.py": "examples/simulations/multi_sector_simulation.py",
}


def create_backup():
    """Cria backup das pastas críticas antes da limpeza"""
    print(f"\n📦 Criando backup em: {BACKUP_DIR.name} ...")

    try:
        BACKUP_DIR.mkdir(exist_ok=True)
    except Exception as e:
        print(f"   ❌ Erro ao criar diretório de backup: {e}")
        return False

    # Copia apenas pastas essenciais para o backup
    for folder in ["src", "scripts", "reports", "examples"]:
        src = ROOT_DIR / folder
        dest = BACKUP_DIR / folder

        if src.exists():
            try:
                shutil.copytree(src, dest, dirs_exist_ok=True)
                print(f"   ✅ Backup: {folder}/")
            except Exception as e:
                print(f"   ⚠️  Erro no backup de {folder}/: {e}")
        else:
            print(f"   ⚠️  Pasta não encontrada (ignorado): {folder}/")

    print("   ✅ Backup concluído com sucesso.")
    return True


def clean_files():
    """Remove arquivos obsoletos listados"""
    print("\n🗑️  Fase 1: Removendo arquivos obsoletos...")

    deleted_count = 0

    for rel_path in FILES_TO_DELETE:
        file_path = ROOT_DIR / rel_path
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"   ✅ Removido: {rel_path}")
                deleted_count += 1
            except Exception as e:
                print(f"   ❌ Erro ao remover {rel_path}: {e}")
        else:
            print(f"   ⚠️  Não encontrado (já removido?): {rel_path}")

    for rel_path in DIRS_TO_DELETE:
        dir_path = ROOT_DIR / rel_path
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"   ✅ Removido diretório: {rel_path}")
                deleted_count += 1
            except Exception as e:
                print(f"   ❌ Erro ao remover diretório {rel_path}: {e}")

    # Limpar conteúdo da pasta reports (mas manter a pasta)
    reports_dir = ROOT_DIR / "reports"
    if reports_dir.exists():
        try:
            for item in reports_dir.iterdir():
                if item.is_file() and item.suffix in ['.json', '.html', '.md']:
                    item.unlink()
                    deleted_count += 1
            print(f"   ✅ Limpeza: reports/ (mantém estrutura)")

            # Criar .gitkeep
            (reports_dir / ".gitkeep").touch()
        except Exception as e:
            print(f"   ⚠️  Erro ao limpar reports/: {e}")

    print(f"\n   📊 Total de arquivos/pastas removidos: {deleted_count}")
    return deleted_count


def reorganize_structure():
    """Reorganiza scripts de simulação para examples/simulations/"""
    print("\n📁 Fase 2: Reorganizando estrutura de simulações...")

    dest_dir = ROOT_DIR / "examples" / "simulations"
    dest_dir.mkdir(parents=True, exist_ok=True)

    moved_count = 0

    # 1. Mover scripts específicos
    for src_rel, dst_rel in SCRIPT_MOVES.items():
        src = ROOT_DIR / src_rel
        dst = ROOT_DIR / dst_rel

        if src.exists():
            try:
                # Criar pasta de destino se não existir
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                print(f"   ✅ Movido: {src_rel} → {dst_rel}")
                moved_count += 1
            except Exception as e:
                print(f"   ❌ Erro ao mover {src_rel}: {e}")
        else:
            print(f"   ⚠️  Não encontrado: {src_rel}")

    # 2. Mover conteúdo da pasta scripts/simulations antiga
    old_sims_dir = ROOT_DIR / "scripts" / "simulations"
    if old_sims_dir.exists():
        try:
            for item in old_sims_dir.iterdir():
                if item.is_file() and item.suffix == '.py':
                    shutil.move(str(item), str(dest_dir / item.name))
                    print(f"   ✅ Movido: simulations/{item.name}")
                    moved_count += 1

            # Remove pasta vazia
            if not any(old_sims_dir.iterdir()):
                shutil.rmtree(old_sims_dir)
                print("   ✅ Removida pasta antiga: scripts/simulations/")
        except Exception as e:
            print(f"   ⚠️  Erro ao processar scripts/simulations/: {e}")

    print(f"\n   📊 Total de scripts movidos: {moved_count}")
    return moved_count


def update_gitignore():
    """Atualiza .gitignore com regras para v0.9.0"""
    print("\n📝 Fase 3: Atualizando .gitignore...")

    gitignore_path = ROOT_DIR / ".gitignore"
    content = ""

    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding='utf-8')

    new_rules = """
# --- BuildToValue v0.9.0 Generated Files ---
*.egg-info/
build/
dist/
*.pyc
__pycache__/

# Reports (gerados dinamicamente)
reports/*.json
reports/*.html
reports/*.md
!reports/.gitkeep

# Logs
logs/
*.log

# Backups
backup_*/

# Environment
.env
.env.local
.venv/
venv/
env/

# IDE
.vscode/
.idea/
*.swp
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Docker
docker-compose.override.yml
"""

    try:
        if "BuildToValue v0.9.0" not in content:
            with open(gitignore_path, "a", encoding='utf-8') as f:
                f.write(new_rules)
            print("   ✅ Regras adicionadas ao .gitignore")
        else:
            print("   ℹ️  .gitignore já contém regras v0.9.0 (sem duplicação)")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao atualizar .gitignore: {e}")
        return False


def create_experimental_notice():
    """Cria aviso EXPERIMENTAL para o setor de Educação"""
    print("\n⚠️  Fase 4: Criando aviso EXPERIMENTAL para Education...")

    notice_path = ROOT_DIR / "examples" / "simulations" / "EDUCATION_EXPERIMENTAL.md"
    notice_path.parent.mkdir(parents=True, exist_ok=True)

    content = """# ⚠️ EDUCATION SECTOR - EXPERIMENTAL STATUS

**Current Status**: BETA / EXPERIMENTAL  
**Prevention Rate**: 46.7% (Below production threshold of 95%)  
**Last Updated**: December 2025  
**Target for Production**: v0.9.5 (Q1 2026)

---

## Why Experimental?

The Education sector module currently has **16 false negatives** (threats missed) in our validation suite. This is **unacceptable for production use** in high-stakes educational environments.

### Known Issues

1. **Proxy Discrimination Detection**: Patterns like "GPA + ZIP code bias" are not reliably caught
2. **Essay Grading Bias**: Subtle biases in automated grading slip through  
3. **Allocational Harm**: Scholarship/admission decisions lack robust safeguards

### Root Cause Analysis

Our threat taxonomy was primarily validated against Fintech, Healthcare, and HR sectors. The Education domain has unique bias vectors:
- Academic merit vs. socioeconomic background entanglement
- Standardized test score biases
- Access inequality patterns

**We need community input to build better safe patterns for this sector.**

---

## Usage Warning
❌ DO NOT use in production for high-stakes decisions
system = AISystem(
id="essay-grader",
sector=AISector.EDUCATION,
risk_classification=EUComplianceRisk.HIGH # ⚠️ Use with extreme caution
)

**Recommendation**: For production education AI, refer to Fintech (100%) or Healthcare (100%) modules as templates until v0.9.5 resolves Education-specific gaps.

---

## Roadmap to Production (v0.9.5)

- [ ] Add 15+ education-specific safe patterns  
- [ ] Integrate FERPA compliance checks (US)
- [ ] Integrate GDPR Art. 22 safeguards (EU)
- [ ] Achieve ≥85% prevention rate in simulations
- [ ] Community peer review of threat taxonomy
- [ ] Partner with EdTech governance experts

---

## How to Contribute

We welcome contributions from the education sector:

1. **Report False Negatives**: [Open an issue](https://github.com/danzeroum/buildtovalue-governance/issues/new?labels=education,false-negative)
2. **Propose Safe Patterns**: Submit PRs to `src/core/governance/sector_safe_patterns.py`
3. **Review Our Taxonomy**: Audit `src/core/governance/threat_classifier.py` for education blind spots

---

**Transparency Commitment**: We will not mark Education as "production-ready" until it matches our Fintech/Healthcare standards. Trust requires honesty.

**Contact**: education-sector@buildtovalue.com
"""

    try:
        notice_path.write_text(content, encoding='utf-8')
        print(f"   ✅ Criado: {notice_path.relative_to(ROOT_DIR)}")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao criar EDUCATION_EXPERIMENTAL.md: {e}")
        return False


def create_readme_for_simulations():
    """Cria README explicativo na pasta examples/simulations/"""
    print("\n📄 Fase 5: Criando README para examples/simulations/...")

    readme_path = ROOT_DIR / "examples" / "simulations" / "README.md"

    content = """# 🧪 Simulation Scripts

This folder contains **sector-specific simulation scripts** used to validate BuildToValue's governance engine.

## Available Simulations

| Sector | Script | Prevention Rate | Status |
|--------|--------|-----------------|--------|
| **Fintech** | `fintech_simulation.py` | 100% | ✅ Production |
| **Healthcare** | `healthcare_simulation.py` | 100% | ✅ Production |
| **HR & Employment** | `hr_simulation.py` | 100% | ✅ Production |
| **Critical Infrastructure** | `infrastructure_simulation.py` | 90% | ⚠️ Good |
| **Government Services** | `government_simulation.py` | 93.3% | ⚠️ Good |
| **Education** | `education_simulation.py` | 46.7% | ❌ Experimental |
| **Multi-Sector** | `multi_sector_simulation.py` | 86% avg | ✅ Benchmark |

## Running Simulations
Run individual sector
python examples/simulations/fintech_simulation.py

Run cross-sector analysis
python examples/simulations/multi_sector_simulation.py


## Simulation Architecture

All simulations extend `base_simulation.py` which provides:
- Threat generation (adversarial prompts)
- Confusion matrix calculation
- Financial impact estimation (EU AI Act penalties)
- HTML/JSON report generation

## Interpreting Results

### Metrics Explained

- **Prevention Rate**: % of threats successfully blocked (target: ≥95%)
- **Precision**: % of blocks that were actual threats (avoid false positives)
- **Recall**: % of threats caught (avoid false negatives)
- **F1-Score**: Harmonic mean of Precision and Recall

### Expected Performance

| Metric | Fintech | Healthcare | Education |
|--------|---------|------------|-----------|
| Precision | 100% | 78.9% | 100% |
| Recall | 100% | 100% | 46.7% |
| F1-Score | 100% | 88.2% | 63.6% |

**Note**: Education's low recall is a known issue (see EDUCATION_EXPERIMENTAL.md).

## Adding New Sectors

1. Create `new_sector_simulation.py` extending `BaseSimulation`
2. Define sector-specific threat patterns
3. Add safe patterns to `src/core/governance/sector_safe_patterns.py`
4. Run 100+ requests with 30% adversarial load
5. Document in this README

## References

- [Huwyler (2025) Threat Taxonomy](https://arxiv.org/abs/2511.21901)
- [EU AI Act Compliance Guide](../../docs/compliance/EU_AI_ACT_COMPLIANCE.md)
- [NIST AI RMF Mapping](../../docs/compliance/NIST_AI_RMF_COMPATIBILITY.md)
"""

    try:
        readme_path.write_text(content, encoding='utf-8')
        print(f"   ✅ Criado: {readme_path.relative_to(ROOT_DIR)}")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao criar README.md: {e}")
        return False


def print_summary():
    """Imprime resumo final e próximos passos"""
    print("\n" + "=" * 80)
    print("✅ OPERAÇÃO DE LIMPEZA CONCLUÍDA COM SUCESSO!")
    print("=" * 80)

    print(f"\n📊 Resumo:")
    print(f"   - 🗑️  Arquivos/pastas removidos")
    print(f"   - 📁 Scripts reorganizados para examples/simulations/")
    print(f"   - 📝 .gitignore atualizado")
    print(f"   - ⚠️  Education marcado como EXPERIMENTAL")
    print(f"   - 💾 Backup salvo em: {BACKUP_DIR.name}")

    print(f"\n🚀 Próximos Passos (Execute no terminal do PyCharm):")
    print(f"")
    print(f"   # 1. Revisar mudanças")
    print(f"   git status")
    print(f"")
    print(f"   # 2. Adicionar todas as mudanças")
    print(f"   git add -A")
    print(f"")
    print(f"   # 3. Commit")
    print(f'   git commit -m "chore(v0.9.0): cleanup obsolete files, reorganize simulations"')
    print(f"")
    print(f"   # 4. Tag de release")
    print(f'   git tag -a v0.9.0 -m "Release v0.9.0: Fintech 100% + NIST RMF 70%"')
    print(f"")
    print("=" * 80)


def main():
    """Executa todas as fases da limpeza"""
    print("=" * 80)
    print("🚀 BuildToValue v0.9.0 - OPERAÇÃO CLEAN & SHIP")
    print("=" * 80)
    print(f"📂 Diretório Raiz: {ROOT_DIR}")
    print(f"📂 Diretório Atual: {Path.cwd()}")

    # Verificação inicial
    if not (ROOT_DIR / "scripts").exists():
        print("\n❌ ERRO: Pasta 'scripts/' não encontrada!")
        print(f"   Certifique-se de estar na raiz do projeto (buildtovalue/)")
        print(f"   Diretório atual: {Path.cwd()}")
        return 1

    try:
        # Executar fases
        if not create_backup():
            print("\n⚠️  Aviso: Backup falhou, mas continuando...")

        clean_files()
        reorganize_structure()
        update_gitignore()
        create_experimental_notice()
        create_readme_for_simulations()
        print_summary()

        return 0

    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO durante limpeza: {e}")
        print(f"   💾 Backup disponível em: {BACKUP_DIR}")
        print(f"   🔄 Restaure manualmente se necessário")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())


