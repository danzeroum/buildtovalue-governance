# 🛡️ BuildToValue Framework

[![DOI](https://zenodo.org/badge/1124428350.svg)](https://doi.org/10.5281/zenodo.18080215)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![NIST AI RMF](https://img.shields.io/badge/NIST%20AI%20RMF-70%25%20Compatible-green.svg)](docs/compliance/NIST_AI_RMF_COMPATIBILITY.md)
[![ISO 42001](https://img.shields.io/badge/ISO%2042001-Compliant-green.svg)](docs/compliance/ISO_42001_MAPPING.md)
[![EU AI Act](https://img.shields.io/badge/EU%20AI%20Act-Ready-green.svg)](docs/compliance/EU_AI_ACT_COMPLIANCE.md)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/r/buildtovalue/btv-framework)

**O primeiro middleware open source de governança de IA com conformidade ISO 42001, EU AI Act e NIST AI RMF integrada.**
**Governança em Runtime para Sistemas de IA Autônomos**


BuildToValue é um framework open-source que impõe políticas de governança de IA em tempo real, bloqueando decisões de alto risco antes que causem danos. Pare riscos de IA em runtime com trilhas de auditoria criptográficas e controles de parada de emergência.

---

## 🚀 O Que Torna BuildToValue Diferente?

### Enforcement em Runtime > Documentação Estática
A maioria das ferramentas de governança gera PDFs. **BuildToValue bloqueia comportamento malicioso de IA em milissegundos.**

```
# Abordagem Tradicional (Reativa)
deploy_model()  # ❌ Deploy primeiro, auditoria depois
generate_compliance_report()  # 📄 PDF que ninguém lê

# Abordagem BuildToValue (Proativa)
decision = btv.enforce(task, system, env="production")
if decision.outcome == "BLOCKED":
    # 🛑 IA parada ANTES de causar dano
    alert_compliance_team(decision.reason)
```

### Kill Switch para Sistemas de IA (NOVO v0.9.0)
Primeiro framework a implementar protocolo de parada de emergência **NIST AI RMF MANAGE-2.4**.

```
# Ativar parada de emergência (interrompe TODAS as operações)
btv.emergency_stop(
    system_id="analise-credito-v2",
    reason="Viés detectado em saídas de produção",
    operator_id="admin@empresa.com"
)

# Todas as decisões subsequentes da IA bloqueadas imediatamente
# ✅ Trilha de auditoria assinada com HMAC persistida
# ✅ Equipe de conformidade notificada automaticamente
```

---

## ✨ Funcionalidades Principais

### 🛡️ Segurança & Conformidade
- **Isolamento Multi-Tenant**: Proteção BOLA/IDOR (OWASP API1:2023)
- **Ledger de Auditoria Assinado HMAC**: Logging criptográfico à prova de adulteração
- **10/10 Segurança OWASP API**: Endurecido para produção
- **ISO 42001:2023**: 32/32 controles do Anexo A implementados
- **EU AI Act**: 10 artigos críticos impostos em runtime
- **NIST AI RMF**: 70% compatível (GOVERN, MAP, MANAGE, MEASURE)

### 🧠 Avaliação Inteligente de Riscos
- **Arquitetura de 3 Agentes**: Agentes Técnico, Regulatório e Ético
- **Taxonomia de Ameaças Huwyler**: Detecção de prompt injection em tempo real
- **RAG de Memória de Conformidade**: Rastreamento histórico de violações
- **Pontuação Adaptativa**: Aprende com incidentes passados

### ⚡ Operações
- **Kill Switch**: Protocolo de parada de emergência (NIST MANAGE-2.4)
- **Rastreamento de Ciclo de Vida**: 7 fases (NIST MAP-1.1)
- **Registro de Cadeia de Suprimentos**: Rastreamento de risco de componentes (NIST GOVERN-6.1)
- **Supervisão Humana**: Fluxo de escalação (EU AI Act Art. 14)

---

## 📦 Início Rápido

### Opção 1: Docker (Pronto para Produção)

```
# Clonar repositório
git clone https://github.com/danzeroum/buildtovalue-governance.git
cd buildtovalue-governance

# Gerar segredos
./scripts/rotate_secrets.sh

# Iniciar serviços
docker-compose up -d

# Verificar saúde
curl http://localhost:8000/health
```

### Opção 2: SDK Python

```
pip install buildtovalue
```

```
from buildtovalue import BuildToValue, AISystem, Task

# Inicializar
btv = BuildToValue(api_key="sua-chave")

# Registrar sistema de IA
system = AISystem(
    id="chatbot-v1",
    name="Bot de Suporte ao Cliente",
    sector="general_commercial",
    lifecycle_phase="deployment",
    operational_status="active"
)
btv.register_system(system)

# Impor governança em runtime
task = Task(prompt="Ajudar cliente com rastreamento de pedido")
decision = btv.enforce(task, system, env="production")

if decision.outcome == "APPROVED":
    # ✅ Seguro para prosseguir
    response = seu_llm.generate(task.prompt)
else:
    # 🛑 Bloqueado por política de governança
    log_violation(decision.reason, decision.risk_score)
```

## ⚠️ Cobertura de Setores e Limitações Conhecidas

BuildToValue v0.9.0 foi validado em múltiplos setores de alto risco com níveis variados de prontidão para produção:

| Setor | Status | Taxa de Prevenção | F1-Score | Observações |
|:------|:-------|:------------------|:---------|:------------|
| **Fintech** | ✅ **Produção** | **100%** | 100% | Regras de conformidade universais (ECB/FED) validadas contra 140 cenários de ameaça. Zero falsos negativos. |
| **Saúde** | ✅ **Produção** | **100%** | 88.2% | Proteção robusta contra inferência biométrica e práticas proibidas do EU AI Act. |
| **RH e Emprego** | ✅ **Produção** | **100%** | 100% | Validado para contratação automatizada, avaliação de desempenho e gestão de força de trabalho. |
| **Educação** | 🧪 **EXPERIMENTAL** | **~46.7%** | 51.6% | **⚠️ Requer calibração manual.** Perfil padrão é intencionalmente conservador para evitar falsos positivos em políticas legítimas de admissão. **NÃO use em produção** para decisões educacionais de alto impacto (admissões, notas, alocação de recursos) sem customizar `governance.yaml` e `sector_safe_patterns.py`. Veja [EDUCATION_EXPERIMENTAL.md](./examples/simulations/EDUCATION_EXPERIMENTAL.md) para guia de calibração. |

### Por Que a Lacuna em Educação?

A diferença entre **Fintech (100%)** e **Educação (46.7%)** ilustra um princípio fundamental de governança de IA:

**Enforcement Determinístico vs. Contextual:**
- **Ameaças Fintech são binárias:** "taxa de juros discriminatória" viola lei bancária universalmente. O motor de enforcement bloqueia deterministicamente.
- **Ameaças Educacionais são contextuais:** "alocação de recursos baseada em CEP" pode ser uma política legítima de ação afirmativa *ou* prática discriminatória, dependendo do contexto institucional.

**Filosofia do BuildToValue:**  
Fornecemos o **motor de enforcement** (testado com latência <1ms em 100% dos cenários), mas não assumimos o que é "perigoso" no seu domínio. A linha de base de 46.7% demonstra que o motor funciona corretamente—ele apenas bloqueia ameaças *que você* define, não inventadas.

**Caminho para Produção:**

#### Open Source
Customize `src/core/governance/sector_safe_patterns.py` com as regras de política da sua instituição:
```
Exemplo: Padrões específicos de instituição educacional
EDUCATION_SAFE_PATTERNS = [
"ação afirmativa baseada em CEP", # Sua política permite isso
"alocação de bolsas baseada em necessidade", # Dependente de contexto
"processo holístico de revisão de admissão" # Prática legítima
]
```

#### Edição Enterprise
Nossa equipe de Serviços Profissionais entrega pacotes de políticas pré-calibrados para Educação:
- **Meta**: ≥95% de taxa de prevenção
- **Prazo**: Implementação de 2-4 semanas
- **Contato**: enterprise@buildtovalue.com

**Roadmap:** Meta de ≥85% de taxa de prevenção para setor de Educação na **v0.9.5 (Q1 2026)** com padrões contribuídos pela comunidade.

### Como Ativar Kill Switch (SDK vs. API)

**Opção 1: SDK Python**
Wrapper SDK de alto nível
```
btv = BuildToValue(api_key="sua-chave")
btv.emergency_stop(
system_id="ia-admissao-edu",
reason="Viés detectado no algoritmo de admissões",
operator_id="admin@universidade.edu.br"
)

```

**Opção 2: API REST Direta**

Chamada HTTP direta ao gateway
```
curl -X PUT http://localhost:8000/v1/systems/ia-admissao-edu/emergency-stop
-H "Authorization: Bearer $BTV_TOKEN"
-H "Content-Type: application/json"
-d '{
"operational_status": "emergency_stop",
"reason": "Viés detectado no algoritmo de admissões",
"operator_id": "admin@universidade.edu.br"
}'

```

Ambos os métodos chamam o mesmo endpoint: `PUT /v1/systems/{system_id}/emergency-stop`

---





## 🎯 Casos de Uso do Mundo Real

### 1. Serviços Financeiros - IA de Análise de Crédito

**Desafio**: EU AI Act classifica análise de crédito como "Alto Risco" (Anexo III). Conformidade manual é propensa a erros.

**Solução**:
```
credit_system = AISystem(
    id="analise-credito-v2",
    sector="banking",  # Auto-dispara classificação Alto Risco
    risk="high",
    eu_database_id="EU-DB-12345"  # Registro Art. 71
)

# Enforcement em runtime
decision = btv.enforce(
    Task(prompt="Avaliar solicitação de empréstimo para cliente 12345"),
    credit_system,
    env="production"
)

# BuildToValue automaticamente:
# ✅ Verifica palavras-chave proibidas (social scoring, discriminação)
# ✅ Valida que logging está habilitado (conformidade Art. 12)
# ✅ Escala decisões de alto risco para supervisão humana (Art. 14)
# ✅ Gera trilha de auditoria assinada com HMAC
```

---

### 2. Saúde - IA de Diagnóstico com Kill Switch

**Desafio**: FDA requer capacidade de desabilitar imediatamente dispositivos médicos de IA.

**Solução**:
```
# Operações normais
diagnostic_ai = AISystem(id="ia-radiologia-v3", sector="healthcare")
decision = btv.enforce(task, diagnostic_ai, env="production")

# 🚨 EMERGÊNCIA: Falsos positivos detectados em produção
btv.emergency_stop(
    system_id="ia-radiologia-v3",
    reason="Taxa de 30% de falsos positivos detectada nos últimos 100 exames",
    operator_id="dr.silva@hospital.com"
)

# ✅ Todas operações de IA interrompidas imediatamente
# ✅ Equipe do hospital notificada via PagerDuty
# ✅ Relatório regulatório auto-gerado
```

---

### 3. SaaS Multi-Tenant - Isolamento de Dados

**Desafio**: Prevenir que Tenant A acesse decisões de IA do Tenant B (vulnerabilidade BOLA).

**Solução**:
```
# Tenant A (Banco conservador)
bank_policy = {"autonomy_matrix": {"production": {"max_risk_level": 2.0}}}
btv.register_tenant(id="banco-uuid", policy=bank_policy)

# Tenant B (Startup permissiva)
startup_policy = {"autonomy_matrix": {"production": {"max_risk_level": 8.0}}}
btv.register_tenant(id="startup-uuid", policy=startup_policy)

# BuildToValue garante:
# ✅ Validação de token JWT (claim tenant_id)
# ✅ Isolamento em nível de banco de dados (índices compostos)
# ✅ Banco NUNCA vê dados da startup
```

---

## 🔬 Fundamentação Científica

BuildToValue é baseado em pesquisa revisada por pares:

1. **Huwyler, H.** (2025). *Taxonomia Padronizada de Ameaças para Segurança de IA*. [arXiv:2511.21901](https://arxiv.org/abs/2511.21901)
   - Usado para: Classificação de ameaças (133 incidentes analisados)

2. **Mavracic, J.** (2025). *Policy Cards: Governança de Runtime Legível por Máquina*. [arXiv:2510.24383](https://arxiv.org/abs/2510.24383)
   - Usado para: Arquitetura de kill switch, controles operacionais

3. **NIST AI RMF 1.0** (2023). [Documento Oficial](https://www.nist.gov/itl/ai-risk-management-framework)
   - Usado para: Design de schema (70% compatível)

---

## 📊 Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│               Gateway FastAPI (Auth JWT)                    │
│  POST /v1/enforce  |  PUT /emergency-stop  |  GET /docs     │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │  Prioridade Zero: Verificação Kill Switch│
        │   SE operational_status == emergency_stop:│
        │      RETORNAR BLOCKED imediatamente  │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │   Roteador de Risco Adaptativo (3 Agentes)│
        │  -  Agente Técnico (FLOPs, logging)   │
        │  -  Agente Regulatório (EU AI Act, ISO)│
        │  -  Agente Ético (palavras-chave, justiça)│
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │    Motor de Enforcement (Decisão)    │
        │  risk_score vs. environment_limit    │
        │  APPROVED | BLOCKED | ESCALATED      │
        └──────────────────┬──────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │ Ledger de Auditoria Assinado HMAC (Imutável)│
        │  enforcement_ledger.jsonl            │
        └──────────────────────────────────────┘
```

---

## 🧪 Testes

```
# Executar todos os testes
pytest tests/ -v --cov=src

# Apenas testes de segurança
pytest tests/security/ -v

# Validar integridade do ledger de auditoria
python scripts/validate_ledger.py logs/enforcement_ledger.jsonl
```

**Cobertura de Testes**: 87% (meta: 90%)

---

## 📚 Documentação

### Guias Principais
- [Início Rápido](./docs/guides/QUICK_START.md) - Setup de 15 minutos
- [Visão Geral da Arquitetura](./docs/architecture/ARCHITECTURE.md) - Como funciona
- [Referência da API](./docs/API_REFERENCE.md) - Documentação completa de endpoints
- [Design Multi-Tenant](./docs/architecture/MULTI_TENANT_DESIGN.md) - Modelo de segurança

### Padrões de Conformidade
- [Mapeamento ISO 42001](./docs/compliance/ISO_42001_MAPPING.md) - 32/32 controles
- [Conformidade EU AI Act](./docs/compliance/EU_AI_ACT_COMPLIANCE.md) - 10 artigos
- [Compatibilidade NIST AI RMF](./docs/compliance/NIST_AI_RMF_COMPATIBILITY.md) - 70% de cobertura

### Tópicos Avançados
- [Guia de Deploy](./docs/guides/DEPLOYMENT.md) - Kubernetes, AWS ECS
- [Contribuindo](./CONTRIBUTING.md) - Onboarding de desenvolvedores
- [Modelo de Governança](./GOVERNANCE.md) - BDFL + Conselho de Sucessão

---

## 🛣️ Roadmap

### v0.9.0 (Lançado: 28 de dezembro de 2025) ✅
- ✅ Kill Switch (NIST MANAGE-2.4)
- ✅ Classificação de Ameaças Huwyler
- ✅ Rastreamento de Cadeia de Suprimentos (NIST GOVERN-6.1)
- ✅ 70% de compatibilidade NIST AI RMF

### v0.9.5 (Q1 2026)
- Framework de testes de fairness (NIST MEASURE-2.11)
- Schema de Policy Cards (Mavracic 2024)
- Motor de validação AICM (CSA AI Controls Matrix)

### v1.0.0 (Q2 2026)
- Dashboard UI (React + TypeScript)
- Auto-descomissionamento (NIST MANAGE-4.1)
- 100% de cobertura NIST AI RMF
- Integração com banco de dados vetorial (ChromaDB)

[Roadmap Completo →](https://github.com/danzeroum/buildtovalue-governance/projects)

---

## 🤝 Contribuindo

Agradecemos contribuições! Veja [CONTRIBUTING.md](./CONTRIBUTING.md) para diretrizes.

**Links Rápidos**:
- [Issues Abertas](https://github.com/danzeroum/buildtovalue-governance/issues)
- [Discussões](https://github.com/danzeroum/buildtovalue-governance/discussions)
- [Código de Conduta](./CODE_OF_CONDUCT.md)

---

## 📄 Licença

**Modelo Open Core**:
- **Framework Principal**: Apache License 2.0 (Open Source)
- **Funcionalidades Enterprise**: Comercial (SSO, integração SIEM, suporte SLA)

Veja [LICENSE](./LICENSE) para detalhes.

---

## 🆘 Suporte

- **Comunidade**: [GitHub Discussions](https://github.com/danzeroum/buildtovalue-governance/discussions)
- **Email**: support@buildtovalue.com
- **Enterprise**: enterprise@buildtovalue.com

---

## 🙏 Agradecimentos

Construído com inspiração de:
- **Equipe NIST AI RMF** - Framework de governança
- **Prof. Hernan Huwyler** - Validação de taxonomia de ameaças
- **Juraj Mavracic** - Arquitetura de Policy Cards
- **Cloud Security Alliance** - AI Controls Matrix

---

**Construído por desenvolvedores que se importam com IA responsável.**

⭐ **Dê uma estrela neste repo** se BuildToValue te ajuda a construir sistemas de IA mais seguros!


## 📚 Citação Acadêmica

Se você utilizar o BuildToValue em sua pesquisa ou produto, por favor cite:

> **BuildToValue Core Team.** (2025). *BuildToValue: A Middleware Framework for Real-Time AI Governance and Compliance (v0.9.0)*. Zenodo. https://doi.org/10.5281/zenodo.18080215

Ou use o arquivo `CITATION.cff` incluído no repositório.
---

**Última Atualização**: 28 de dezembro de 2025  
**Status**: Pronto para Produção (v0.9.0 Golden Candidate)
