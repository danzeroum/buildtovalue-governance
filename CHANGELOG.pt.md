# Registro de Alterações

Todas as mudanças notáveis do BuildToValue Framework serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/spec/v2.0.0.html).

---

## [0.9.0] - 2025-12-28

**Lançamento Principal: Pronto para Produção com Conformidade Total ISO 42001**

### 🎉 Adicionado

#### Segurança
- **Isolamento Multi-Tenant** com proteção BOLA/IDOR (OWASP API1:2023)
  - Validação UUID v4 para `tenant_id`
  - Isolamento de tenant em nível de banco de dados com índices compostos
  - Claims JWT como fonte única de verdade
  - Prevenção de ataques Mass Assignment
- **Ledger de Auditoria Assinado HMAC-SHA256**
  - Logging à prova de adulteração (ISO 42001 A.7.5)
  - Validação de integridade criptográfica
- **10/10 mitigações OWASP API Security Top 10 2023** implementadas
  - Prevenção de SQL Injection (SQLAlchemy ORM)
  - Proteção contra bypass de autenticação (validação JWT)
  - Limitação de taxa (100 req/min padrão)
- **RBAC com 4 papéis**: `admin`, `dev`, `auditor`, `app`

#### Conformidade
- **ISO 42001:2023** - 32/32 controles do Anexo A implementados
- **EU AI Act** - 10 artigos críticos implementados:
  - Art. 5: Práticas Proibidas (bloqueio automatizado)
  - Art. 6: Classificação de Risco (setores Anexo III)
  - Art. 9: Gestão de Riscos (avaliação 3 agentes)
  - Art. 12: Logging (retenção de 5 anos)
  - Art. 14: Supervisão Humana (fluxo de escalação)
  - Art. 51: Risco Sistêmico GPAI (validação FLOPs)
  - Art. 71: Base de Dados UE (rastreamento de registro)
- **Conformidade GDPR** - Art. 25 (Privacidade por Design), Art. 32 (Segurança)
- **NIST AI RMF 1.0** - 70% de compatibilidade (GOVERN, MAP, MANAGE, MEASURE)

#### Camada de Inteligência
- **Roteador de Risco Adaptativo** com 3 agentes especializados:
  - **Agente Técnico**: FLOPs, logging, complexidade
  - **Agente Regulatório**: EU AI Act, ISO 42001, setores
  - **Agente Ético**: palavras-chave, justiça, transparência
- **RAG de Memória de Conformidade**: Rastreamento histórico de violações
- **Serviço de Supervisão Humana**: Fluxo de trabalho para escalações
- **Taxonomia de Ameaças Huwyler** (2024): Classificação padronizada de ameaças
  - 133 incidentes de segurança de IA analisados
  - Detecção de prompt injection em tempo real
  - Mapeamento de domínio MISUSE

#### Operações (NOVO v0.9.0)
- **Kill Switch** - Protocolo de Parada de Emergência
  - Endpoint: `PUT /v1/systems/{system_id}/emergency-stop`
  - Implementação NIST AI RMF MANAGE-2.4
  - Interrupção imediata de todas operações do sistema
  - Trilha de auditoria assinada HMAC
  - Persistência de status operacional no banco de dados
- **Gestão de Status Operacional**
  - 5 estados: `active`, `degraded`, `maintenance`, `suspended`, `emergency_stop`
  - Rastreamento de fase do ciclo de vida (NIST MAP-1.1)
  - Registro de componentes da cadeia de suprimentos (NIST GOVERN-6.1)

#### Experiência do Desenvolvedor
- **Gateway FastAPI** com docs OpenAPI interativos (`/docs`)
- **Setup Docker Compose** (dev + produção segura)
- **Scripts Automatizados**:
  - `generate_token.py` - Geração de token JWT
  - `rotate_secrets.sh` - Rotação de segredos (ciclo de 90 dias)
  - `validate_ledger.py` - Verificação de integridade HMAC
  - `generate_compliance_report.py` - Relatórios HTML/JSON
  - `setup_dev_env.sh` - Setup de desenvolvimento com um comando

#### Documentação
- **Mapeamento de Conformidade ISO 42001** - Pacote completo de evidências
- **Guia de Conformidade EU AI Act** - Implementação artigo por artigo
- **Compatibilidade NIST AI RMF** - Evidência de cobertura de 70%
- **Documentação de Arquitetura** - Design em camadas (DDD)
- **Design de Segurança Multi-Tenant** - Modelo de ameaças e mitigações
- **Referência da API** - Documentação completa de endpoints (bilíngue EN/PT)
- **Guia de Início Rápido** - Setup de 15 minutos (bilíngue EN/PT)
- **Guia de Deploy** - Docker, Kubernetes, AWS ECS

#### Testes
- **87% de cobertura de código** (meta: 90%)
- **Suite de testes de segurança**:
  - `test_bola.py` - Prevenção de acesso cross-tenant
  - `test_injection.py` - SQL injection, path traversal
  - `test_auth.py` - Validação JWT, RBAC, escalação de privilégios
- **Testes unitários** para entidades de domínio e motor de enforcement
- **Testes de integração** para fluxos end-to-end

### 🔄 Alterado

- **Estratégia de Merge de Políticas**: Merge conservador (mais restritivo vence)
- **Pontuação de Risco**: Média ponderada (Técnico 30%, Regulatório 40%, Ético 30%)
- **Schema do Banco de Dados**: 
  - Adicionada coluna `operational_status` à tabela `ai_systems`
  - Adicionada coluna `lifecycle_phase` para alinhamento NIST
  - Adicionada `human_ai_configuration` para conformidade Art. 14
  - Índices compostos para performance multi-tenant
- **Respostas de Erro**: Formato JSON padronizado com exception handlers
- **Assinatura do Motor de Enforcement**: Agora requer parâmetro `env` (mudança quebrada)

### 🐛 Corrigido

**Hotfixes Críticos (2025-12-28)**:
- ✅ **Incompatibilidade de assinatura do Enforcement Engine**: Parâmetro `env` ausente causando erros 422/500
- ✅ **Erro de serialização JSON do Gateway**: Objetos dataclass Decision retornando dict em vez de JSONResponse
- ✅ **Bug de persistência do Kill Switch**: Colunas de banco de dados ausentes (`operational_status`, `lifecycle_phase`)
- ✅ **Bug do exception handler**: Respostas de erro não formatadas adequadamente como JSON

**Correções de Segurança**:
- ✅ **Vulnerabilidade BOLA**: Validação de Tenant ID em todas as queries
- ✅ **Vulnerabilidade Mass Assignment**: Claims JWT sobrescrevem payload
- ✅ **SQL Injection**: Queries parametrizadas via SQLAlchemy ORM
- ✅ **Ataques de timing**: `hmac.compare_digest()` para comparação em tempo constante
- ✅ **Expiração JWT**: Reduzida de 24h para 30min (padrão)

### 🔒 Segurança

- **Status CVE**: Sem vulnerabilidades conhecidas
- **Status de Teste de Penetração**: Pronto para auditoria externa
- **Gestão de Segredos**: Variáveis de ambiente + Docker secrets
- **TLS 1.3**: Obrigatório em produção (config nginx)

### ⚠️ Mudanças Quebradas

**CRÍTICO**: Todos os usuários devem atualizar código para incluir parâmetro `env`.

#### SDK Python
❌ ANTIGO (v0.8.x) - VAI FALHAR
decision = engine.enforce(task, system)

✅ NOVO (v0.9.0) - OBRIGATÓRIO
decision = engine.enforce(task, system, env="production")


#### REST API
❌ ANTIGO - Retorna Erro 422
curl -X POST /v1/enforce -d '{"system_id": "...", "prompt": "..."}'

✅ NOVO - Campo Obrigatório
curl -X POST /v1/enforce -d '{"system_id": "...", "prompt": "...", "env": "production"}'


#### Outras Mudanças Quebradas
- Tokens JWT **devem incluir** claim `tenant_id`
- Schema de banco de dados alterado (migração necessária - veja guia de upgrade)
- Versão mínima Python: **3.10** (era 3.8)

### 🗑️ Descontinuado

**Descontinuações v0.9.0** (serão removidas em v1.0.0):
- Modo single-tenant (multi-tenant agora é obrigatório)
- SQLite em produção (use PostgreSQL)

---

## [0.8.0] - 2024-11-15

**Lançamento Beta**

### Adicionado
- Motor de enforcement básico
- Suporte SQLite para desenvolvimento
- Configuração de política simples

### Alterado
- Migrado de Flask para FastAPI

---

## [0.7.0] - 2024-10-01

**Protótipo**

### Adicionado
- Prova de conceito inicial
- Avaliação de risco básica
- Configuração YAML

---

## [Não Lançado]

Planejado para **v0.9.5** (Q1 2026) e **v1.0.0** (Q2 2026)

### Funcionalidades (v0.9.5 - Reforço de Fundação)
- ✨ Framework de testes de fairness (NIST MEASURE-2.11)
- ✨ Schema de Policy Cards (governança de runtime legível por máquina)
- ✨ Motor de validação AICM (CSA AI Controls Matrix)
- 🔧 Otimização de performance (enforcement <100ms de latência)

### Funcionalidades (v1.0.0 - Enterprise em Produção)
- 🚀 **Dashboard UI** (React + TypeScript)
  - Monitoramento de conformidade em tempo real
  - Interface de supervisão humana
  - Visualizações estilo Grafana
- 🚀 **Integração de Banco de Dados Vetorial** (ChromaDB)
  - Busca de similaridade semântica para violações
  - RAG baseado em embeddings
- 🚀 **Agentes de Auto-Remediação**
  - Sugestões de políticas baseadas em LLM
  - Ações corretivas automatizadas
- 🚀 **Integrações Aprimoradas**
  - Notificações Slack
  - Alertas PagerDuty
  - Métricas Datadog
  - Envio de logs Splunk
- 🚀 **Lógica de Enforcement de Policy Cards** (Mavracic 2024)
- 🚀 **Auto-Descomissionamento** (NIST MANAGE-4.1)
- 📈 **100% de cobertura NIST AI RMF**

### Suporte a Banco de Dados
- Suporte MongoDB (opção NoSQL)
- Suporte Cassandra (deployments de alta escala)
- Ferramenta de migração de banco de dados

### Deploy
- Helm charts Kubernetes
- Módulos Terraform (AWS, Azure, GCP)
- Guias de deploy multi-cloud

### Conformidade
- Certificação SOC 2 Type II
- Certificação ISO 27001:2022

---

## Estratégia de Versionamento

- **Major (X.0.0)**: Mudanças quebradas de API, nova arquitetura
- **Minor (0.X.0)**: Novas funcionalidades, retrocompatível
- **Patch (0.9.X)**: Correções de bugs, patches de segurança

---

## Guia de Upgrade

### De v0.8.x para v0.9.0

#### 1. Migração de Banco de Dados

-- Adicionar tenant_id aos sistemas existentes
ALTER TABLE ai_systems ADD COLUMN tenant_id VARCHAR(36);

-- Atribuir tenant legado
UPDATE ai_systems SET tenant_id = 'legacy-tenant-uuid';

-- Adicionar novas colunas v0.9.0
ALTER TABLE ai_systems ADD COLUMN operational_status VARCHAR(50) DEFAULT 'active';
ALTER TABLE ai_systems ADD COLUMN lifecycle_phase VARCHAR(50) DEFAULT 'deployment';
ALTER TABLE ai_systems ADD COLUMN human_ai_configuration JSONB;

-- Adicionar restrições
ALTER TABLE ai_systems ALTER COLUMN tenant_id SET NOT NULL;
CREATE INDEX idx_tenant_system ON ai_systems(tenant_id, id);


#### 2. Mudanças de Configuração

**governance.yaml (NOVO)**:
Enforcement de práticas proibidas
prohibited_practices:

social_scoring

subliminal_manipulation

Configuração de logging
logging:
retention_days: 1825 # 5 anos
tamper_proof: true


#### 3. Mudanças de Código

ANTIGO (v0.8.x)
decision = engine.enforce(task, system)

NOVO (v0.9.0) - Adicionar parâmetro environment
decision = engine.enforce(task, system, env="production")


#### 4. Variáveis de Ambiente

Adicionar ao .env
OPERATIONAL_STATUS_DEFAULT=active
LIFECYCLE_PHASE_DEFAULT=deployment


---

## Contribuidores

### Equipe Principal
- **Daniel Zero** - Líder de Projeto & Arquitetura
- **Comunidade BuildToValue** - 12 contribuidores

### Auditores de Segurança
- [Sua Empresa de Segurança] - Teste de penetração (planejado Q1 2026)

### Contribuidores de Pesquisa
- **Prof. Hernan Huwyler** (2024) - Validação de Taxonomia de Ameaças
- **Juraj Mavracic** (2024) - Arquitetura de Policy Cards
- **Equipe NIST AI RMF** - Framework de governança
- **Cloud Security Alliance** - AI Controls Matrix

---

## Licença

Apache License 2.0 - Veja [LICENSE](./LICENSE) para detalhes.

**Modelo Open Core**:
- Motor de governança principal: **Open Source**
- Funcionalidades enterprise (SSO, SIEM, SLA): **Comercial**

---

## Suporte

Para instruções detalhadas de upgrade, veja [UPGRADING.md](./UPGRADING.md)  
Para avisos de segurança, veja [SECURITY.md](./SECURITY.md)

---

**Última Atualização**: 28 de dezembro de 2025  
**Status**: Pronto para Produção (v0.9.0 Golden Candidate)