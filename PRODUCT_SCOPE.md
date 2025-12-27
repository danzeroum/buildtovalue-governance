# 🛡️ BuildToValue Product Scope & Licensing Model

BuildToValue opera sob um modelo **Open Core**. Isso significa que o motor de governança, a segurança fundamental e a conformidade técnica são 100% Open Source (Apache 2.0), garantindo transparência e auditabilidade. Recursos de gestão em escala, colaboração e integrações corporativas são reservados para a versão Enterprise.

## Filosofia de Separação

- **Open Source (Core):** Tudo o que um Engenheiro/Arquiteto precisa para *executar* governança em tempo real e garantir segurança técnica.
- **Enterprise:** Tudo o que um Gestor/CISO precisa para *gerenciar* políticas em escala, visualizar dados e integrar com a infraestrutura corporativa existente.

---

## 📊 Matriz de Funcionalidades (v0.9.0)

| Categoria | Funcionalidade | Open Source (Core) | Enterprise |
| :--- | :--- | :---: | :---: |
| **Enforcement** | **Runtime Engine (Interceptor)** | ✅ Sim | ✅ Sim |
| | Multi-Agent Scoring (Technical, Regulatory, Ethical) | ✅ Sim | ✅ Sim |
| | Kill Switch (Emergency Stop API) | ✅ Sim | ✅ Sim |
| | Latency Overhead | < 50ms | < 50ms |
| **Segurança** | **HMAC-Signed Audit Ledger** | ✅ Sim | ✅ Sim |
| | Isolamento Multi-Tenant (TenantID Enforced) | ✅ Sim | ✅ Sim |
| | Threat Taxonomy (Huwyler 2025) | ✅ Sim | ✅ Sim |
| | Integração SSO / SAML / OIDC | ❌ Não | ✅ Sim |
| | Role-Based Access Control (RBAC) Granular | Básico (Admin/User) | Avançado |
| **Compliance** | **NIST AI RMF 1.0 Architecture** | ✅ Sim | ✅ Sim |
| | EU AI Act Schema (High-Risk Tracking) | ✅ Sim | ✅ Sim |
| | Supply Chain Registry (Dependencies) | ✅ Sim | ✅ Sim |
| | Gerador de Relatórios PDF/Docx (Auditor-Ready) | ❌ Não (JSON/HTML) | ✅ Sim |
| **Integração** | **Python SDK & CLI Tool** | ✅ Sim | ✅ Sim |
| | API REST Completa | ✅ Sim | ✅ Sim |
| | Docker Compose Deployment | ✅ Sim | ✅ Sim |
| | SIEM Connectors (Splunk, Datadog, ELK) | ❌ Logs JSON puros | ✅ Conectores Nativos |
| | Policy Cards Conversion (Interoperabilidade) | ⚠️ (Schema Ready) | ✅ Automático |
| **Gestão** | **Dashboard Web (GUI)** | ❌ Não (CLI/API) | ✅ Sim |
| | Editor Visual de Políticas (No-Code) | ❌ Não (YAML) | ✅ Sim |
| | Gestão de Equipes e Aprovações | ❌ Não | ✅ Sim |
| | Multi-Workspace (Organizações) | ❌ Não | ✅ Sim |
| **Observabilidade** | **Logs Estruturados (JSON)** | ✅ Sim | ✅ Sim |
| | Métricas Prometheus/OpenTelemetry | ✅ Sim (básico) | ✅ Sim (avançado) |
| | Alertas Customizados | ❌ Não | ✅ Sim |
| | Tracing Distribuído | ❌ Não | ✅ Sim |
| **Suporte** | SLA de Resposta | Community (Best Effort) | 24/7 ou 8/5 |
| | Onboarding Personalizado | ❌ Não | ✅ Sim |
| | Consultoria de Arquitetura | ❌ Não | ✅ Sim |

---

## 🎯 Princípios de Design

### 1. Segurança Não é Paywall
**Decisão Estratégica:** Todos os recursos de segurança (HMAC, Kill Switch, Threat Taxonomy, Isolamento Multi-Tenant) são Open Source.

**Justificativa:**
- Confiança da comunidade requer auditabilidade
- Segurança como paywall = "security theater"
- Diferencial competitivo está na facilidade de gestão, não na funcionalidade técnica

### 2. Enterprise = Conveniência + Gestão
**O que diferencia Enterprise:**
- **Conveniência:** Dashboard visual vs CLI/API
- **Gestão:** Aprovações, equipes, workflows vs configuração manual
- **Integrações:** Conectores nativos vs logs JSON brutos
- **Suporte:** SLA contratual vs community best effort

### 3. Migração Sem Fricção
**Garantia técnica:**
- Enterprise Edition é uma camada adicional (containers extras)
- Mesmo banco de dados, mesma API, mesmo motor Core
- Upgrade sem downtime, rollback sem perda de dados

---

## 🔮 Roadmap de Diferenciação

### Recursos Planejados para v0.9.5 (Open Source)
- [ ] **Fairness Testing Framework:** API para executar testes de bias
- [ ] **Policy Cards JSON Validator:** Validar sintaxe de Policy Cards
- [ ] **Workforce Diversity Tracking:** Campos para composição de equipes
- [ ] **Cost-Benefit Analysis:** Campos para análise ROI/TCO

### Recursos Planejados para v0.9.5 (Enterprise)
- [ ] **Dashboard Alpha:** Interface web básica (React)
- [ ] **SSO Integration (Okta):** Primeiro conector SSO
- [ ] **PDF Compliance Reports:** Geração de relatórios para auditores
- [ ] **Slack Notifications:** Alertas de violações em tempo real

### Recursos Planejados para v1.0 (Open Source)
- [ ] **Policy Cards Engine (Read-Only):** Leitura e parsing de Policy Cards
- [ ] **Environmental Impact Calculator:** Estimativa automática de carbono
- [ ] **User Feedback API:** Endpoint para registrar feedback de usuários
- [ ] **Decommissioning Workflow:** Processo automatizado de retirement

### Recursos Planejados para v1.0 (Enterprise)
- [ ] **Policy Cards Engine (Full):** Validação e enforcement ABAC complexo
- [ ] **Automated Fairness Testing:** Baterias estatísticas (AIF360 integration)
- [ ] **Predictive Compliance Scoring:** ML-based risk prediction
- [ ] **Multi-Cloud Terraform Modules:** AWS/Azure/GCP deployment
- [ ] **Advanced RBAC:** Attribute-Based Access Control (ABAC)

---

## 💼 Programa de Design Partners (Enterprise Beta)

**Status:** Aceitando 5 design partners para Q1 2026

**Benefícios:**
- ✅ Acesso antecipado ao Dashboard (Q1 2026)
- ✅ Influência no roadmap de features
- ✅ Pricing preferencial (50% desconto ano 1)
- ✅ Créditos de consultoria ($10k USD)
- ✅ Co-marketing (case study opcional)

**Requisitos:**
- Ambiente de produção com IA high-risk (EU AI Act Art. 6)
- Comprometimento com feedback semanal
- Equipe técnica dedicada (1 pessoa 20% time)

**Contato:** [enterprise@buildtovalue.com](mailto:enterprise@buildtovalue.com)

---

## 🤔 Perguntas Frequentes

### Q: Posso usar a versão Open Source em produção?
**R:** Sim. A licença Apache 2.0 permite uso comercial sem restrições. O motor é "production-ready" e contém todos os recursos de segurança críticos (HMAC, Kill Switch, Threat Taxonomy). Empresas como [CASE STUDY TBD] usam o Core em produção.

### Q: O que acontece se eu precisar migrar para Enterprise?
**R:** A migração é transparente. O Enterprise é uma camada adicional (containers extras: `btv-dashboard`, `btv-sso-proxy`) que se conecta ao mesmo banco de dados e motor Core. Nenhuma refatoração de código é necessária. Processo de upgrade estimado: < 4 horas.

### Q: Vocês oferecem suporte para a versão Open Source?
**R:** Sim, através da comunidade:
- GitHub Issues: [github.com/danzeroum/buildtovalue-governance/issues](https://github.com/danzeroum/buildtovalue-governance/issues)
- Discord: [discord.gg/buildtovalue](https://discord.gg/buildtovalue)
- Tempo de resposta: Best effort (geralmente 24-72h)

Para suporte com SLA contratual, considere o Enterprise Edition.

### Q: Por que vocês não colocaram o Dashboard no Open Source?
**R:** Decisão estratégica baseada em 3 fatores:
1. **Complexidade de manutenção:** Manter um frontend React/TypeScript requer recursos significativos
2. **Diferenciação competitiva:** Nossa pesquisa mostrou que CISOs pagam por conveniência, não por funcionalidade técnica
3. **Sustentabilidade:** Revenue do Enterprise financia o desenvolvimento do Core

**Alternativa para desenvolvedores:** Use a API REST + ferramentas de sua escolha (Grafana, Retool, etc.)

### Q: Posso criar meu próprio Dashboard usando a API?
**R:** Sim! A API REST é 100% Open Source e documentada. Você pode criar qualquer interface customizada. Inclusive, adoraríamos ver contribuições de dashboards alternativos na comunidade.

### Q: Como vocês evitam "bait and switch" (mudar features de Open para Enterprise depois)?
**R:** Compromisso público em `PRODUCT_SCOPE.md` (este arquivo):
- ✅ **Kill Switch permanece Open Source** (commitado em v0.9.0)
- ✅ **HMAC Ledger permanece Open Source** (commitado em v7.3)
- ✅ **Threat Taxonomy permanece Open Source** (commitado em v0.9.0)
- ✅ **NIST/EU AI Act Schema permanece Open Source** (commitado em v0.9.0)

**Garantia:** Qualquer mudança desses componentes para Enterprise seria uma violação de licença Apache 2.0 (que permite uso perpétuo das versões existentes) e destruiria nossa credibilidade.

### Q: Vocês planejam uma versão SaaS (hospedada)?
**R:** Sim, no roadmap para Q3 2026. Será baseado no Enterprise Edition com gerenciamento de infraestrutura incluído. Open Source continuará disponível para auto-hospedagem.

---

## 📜 Compliance com Open Source Best Practices

Este modelo segue as recomendações de:
- [Open Source Initiative - Licensing](https://opensource.org/licenses/Apache-2.0)
- [TODO Group - Best Practices for Corporate Open Source](https://todogroup.org/guides/)
- [Linux Foundation - Open Source Licensing Guide](https://www.linuxfoundation.org/resources/open-source-guides)

**Auditado em:** 2025-12-26  
**Próxima revisão:** 2026-03-26

---

## 📞 Contato

- **Open Source (Community):** [GitHub Issues](https://github.com/danzeroum/buildtovalue-governance/issues)
- **Enterprise Sales:** [enterprise@buildtovalue.com](mailto:enterprise@buildtovalue.com)
- **Security:** [security@buildtovalue.com](mailto:security@buildtovalue.com)
- **General:** [hello@buildtovalue.com](mailto:hello@buildtovalue.com)

---

**Version:** 1.0  
**Last Updated:** December 26, 2025  
**Status:** 🟢 Final (Approved for Public Release)
