# 🛠️ BuildToValue Operation Scripts

Este diretório contém ferramentas essenciais para a operação, manutenção e auditoria do BuildToValue Governance.

---

## 📋 Ferramentas Disponíveis

### 1. Governança e Compliance

#### `generate_compliance_report.py` ⭐
Gera o relatório executivo de conformidade (HTML/JSON) certificando a eficácia dos bloqueios contra as regulações suportadas.

**Uso:**
Relatório padrão (Fintech Gold Master)
python scripts/generate_compliance_report.py

Relatório customizado com dados multi-setor
python scripts/generate_compliance_report.py
--multi-sector reports/multi_sector_results.json
--output reports/auditoria_q1_2026.html


**Saída:**
- Relatório HTML executivo
- JSON estruturado para integração com ferramentas de auditoria
- Compatível com ISO 42001 e EU AI Act Art. 72 (Transparência)

**Frequência Recomendada:** Trimestral ou antes de auditorias externas

---

#### `validate_ledger.py` 🔐
Verifica a integridade criptográfica (HMAC) dos logs de decisão. Essencial para auditorias forenses.

**Uso:**
Validar ledger padrão
python scripts/validate_ledger.py logs/enforcement_ledger.jsonl

Validar ledger customizado
python scripts/validate_ledger.py /caminho/custom_ledger.jsonl


**Alerta:** Detecta se qualquer linha do log foi alterada manualmente (adulteração).

**Quando Executar:**
- Semanalmente (rotina de segurança)
- Antes de auditorias externas
- Após incidentes de segurança suspeitos

**Compliance:** ISO 42001 Art. 9.1 (Monitoramento) + EU AI Act Art. 12 (Record-keeping)

---

### 2. Segurança e Acesso

#### `rotate_secrets.sh` 🔄
Automatiza a rotação de segredos (JWT Secrets, HMAC Keys, DB Passwords) conforme exigido pela ISO 42001 (Controle B.6.1.2).

**Uso:**
Linux/Mac
./scripts/rotate_secrets.sh

Se necessário, dar permissão de execução primeiro:
chmod +x scripts/rotate_secrets.sh


**O que é rotacionado:**
- `JWT_SECRET_KEY` (autenticação de usuários)
- `HMAC_SECRET_KEY` (integridade do ledger)
- `DATABASE_PASSWORD` (se aplicável)

**Frequência Recomendada:** A cada 90 dias (requisito ISO 42001)

**⚠️ Atenção:** 
- Criar backup do `.env` antes da rotação
- Tokens JWT emitidos antes da rotação serão invalidados
- Reinicie o servidor após a rotação

---

#### `generate_token.py` 🎫
Gerador de tokens JWT para acesso administrativo ou integração de sistemas (M2M).

**Uso - Bootstrap Admin:**
Criar token admin inicial (90 dias)
python scripts/generate_token.py
--role admin
--tenant global_admin
--days 90


**Uso - Aplicação M2M:**
Token para sistema integrado (365 dias)
python scripts/generate_token.py
--role app
--tenant <tenant_uuid>
--days 365
--user "Sistema de RH"


**Uso - Desenvolvedor:**
Token dev (30 dias)
python scripts/generate_token.py
--role dev
--tenant <tenant_uuid>
--user dev@empresa.com.br
--days 30


**Quando Usar:**
- **Bootstrap inicial:** Criar primeiro admin após instalação
- **Integração M2M:** Sistemas externos precisam acessar API
- **Recuperação de acesso:** Admin perdeu credenciais
- **Testes de desenvolvimento:** Gerar tokens para ambientes de teste

---

### 3. Desenvolvimento

#### `setup_dev_env.sh` 🚀
Configura o ambiente de desenvolvimento local (venv, dependências, secrets iniciais).

**Uso:**
Linux/Mac
./scripts/setup_dev_env.sh

Se necessário, dar permissão de execução primeiro:
chmod +x scripts/setup_dev_env.sh


**O que é configurado:**
- Cria ambiente virtual Python (.venv)
- Instala dependências do `requirements.txt`
- Gera `.env` inicial com secrets aleatórios
- Cria estrutura de pastas (logs/, reports/)
- Inicializa banco de dados SQLite

**Quando Usar:**
- Onboarding de novos desenvolvedores
- Setup de ambiente CI/CD
- Reset completo do ambiente local

---

## 🪟 Scripts Específicos por Plataforma

O BuildToValue fornece scripts nativos para todas as principais plataformas:

| Plataforma | Script de Setup | Rotação de Secrets | Notas |
|------------|-----------------|-------------------|-------|
| **Linux/macOS** | `setup_dev_env.sh` | `rotate_secrets.sh` | Bash 4.0+ |
| **Windows** | `setup_dev_env.ps1` | `rotate_secrets.ps1` | PowerShell 5.1+ |
| **Multi-plataforma** | Git Bash, WSL | Git Bash, WSL | Alternativa para Windows |

### Executando Scripts no Windows

**Opção 1: PowerShell (Recomendado)**
Configurar ambiente
.\scripts\setup_dev_env.ps1

Rotacionar secrets
.\scripts\rotate_secrets.ps1


**Opção 2: Git Bash**
Configurar ambiente
bash scripts/setup_dev_env.sh

Rotacionar secrets
bash scripts/rotate_secrets.sh

**Opção 3: WSL (Windows Subsystem for Linux)**
Configurar ambiente
./scripts/setup_dev_env.sh

Rotacionar secrets
./scripts/rotate_secrets.sh


### Política de Execução (Apenas PowerShell)

Se receber erros de "política de execução":

**Verificar política atual**
Get-ExecutionPolicy

**Permitir scripts para usuário atual**
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Ou executar com bypass (uma vez)
powershell -ExecutionPolicy Bypass -File .\scripts\setup_dev_env.ps1


---

## 📊 Resumo das Ferramentas

| Script | Propósito | Frequência | Criticidade |
|--------|-----------|------------|-------------|
| `generate_compliance_report.py` | Relatório executivo de conformidade | Trimestral | ⭐⭐⭐ |
| `validate_ledger.py` | Auditoria forense de logs | Semanal | ⭐⭐⭐ |
| `rotate_secrets.sh` | Rotação de credenciais | 90 dias | ⭐⭐⭐ |
| `generate_token.py` | Geração de tokens JWT | Sob demanda | ⭐⭐ |
| `setup_dev_env.sh` | Setup de ambiente | Inicial | ⭐⭐ |

---

## 🔒 Notas de Segurança

### Permissões de Execução (Linux/Mac)
Dar permissão de execução para scripts shell
chmod +x scripts/*.sh

Verificar permissões
ls -la scripts/


### Proteção de Secrets
- **NUNCA** commite arquivos `.env` no Git
- Use `.env.example` como template (sem valores reais)
- Rotacione secrets a cada 90 dias conforme ISO 42001

### Auditoria de Mudanças
Ver histórico de execução de scripts
git log --oneline -- scripts/

Ver quem executou rotação de secrets
git log -p scripts/rotate_secrets.sh


---

## 🆘 Troubleshooting

### Script não executa (Permission Denied)
Solução: Dar permissão de execução
chmod +x scripts/<nome_do_script>.sh


### Token JWT não funciona
Possíveis causas:
1. JWT_SECRET_KEY foi rotacionado (token antigo invalida)
2. Token expirado (verificar --days na geração)
3. .env não carregado (verificar python-dotenv)
Solução: Gerar novo token
python scripts/generate_token.py --role admin --tenant global_admin --days 90


### Ledger inválido detectado
Se validate_ledger.py detectar adulteração:
1. NÃO delete o ledger (é evidência forense)
2. Isole o arquivo: mv logs/enforcement_ledger.jsonl logs/compromised_$(date +%Y%m%d).jsonl
3. Investigue: revisar git log, auditoria de acesso ao servidor
4. Crie novo ledger: reinicie o servidor (gera novo ledger limpo)

---

## 📚 Referências

- **ISO/IEC 42001:2023** - AI Management System (Cláusula 9.1 - Monitoramento)
- **EU AI Act (Regulation 2024/1689)** - Art. 12 (Record-keeping), Art. 72 (Transparência)
- **NIST AI RMF 1.0** - GOVERN-1.3 (Auditability), MEASURE-2.10 (Logging)
- **Huwyler (2025)** - Threat Taxonomy (arXiv:2511.21901v1 [cs.CR])

---

## 🤝 Contribuindo

Para adicionar novos scripts à toolkit:

1. **Nomeie claramente:** `<verbo>_<substantivo>.py` (ex: `export_audit_trail.py`)
2. **Documente no topo:** Propósito, uso, frequência recomendada
3. **Adicione ao README:** Mantenha este arquivo atualizado
4. **Teste isoladamente:** Execute em ambiente dev antes de commit

**Exemplo de estrutura:**
```
#!/usr/bin/env python3
"""
BuildToValue v0.9.0 - <Nome da Ferramenta>
Propósito: <Breve descrição>
Uso: python scripts/<script>.py [opções]
Frequência: <Quando executar>
"""
```

---

**Maintainer:** BuildToValue Core Team  
**Last Updated:** December 28, 2025  
**Version:** 0.9.0 Gold Master  
**License:** Consulte LICENSE no root do repositório