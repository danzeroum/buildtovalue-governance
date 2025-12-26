"""
FastAPI Gateway - REST API com RBAC e Multi-Tenant Security

Implementa:
- ISO 42001 8.1 (Operational Planning and Control)
- EU AI Act Art. 12 (Logging)
- OWASP API Security Top 10 2023
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from src.core.registry.system_registry import SystemRegistry
from src.core.governance.enforcement import RuntimeEnforcementEngine
from src.domain.entities import Task, AISystem
from src.domain.enums import AIRole, EUComplianceRisk, AISector, ArtifactType
from src.interface.api.auth import verify_jwt_token, require_role, TokenData

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("btv.gateway")

# FastAPI App
app = FastAPI(
    title="BuildToValue Framework",
    description="Enterprise AI Governance Platform with ISO 42001 Compliance",
    version="7.3.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "Admin", "description": "Admin-only operations (tenant management)"},
        {"name": "Developer", "description": "Developer operations (system registration)"},
        {"name": "Enforcement", "description": "Runtime governance enforcement"},
        {"name": "Audit", "description": "Audit and compliance reporting"}
    ]
)

# CORS (configure para produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em prod: especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singletons (inicialização lazy)
registry = SystemRegistry()
engine = RuntimeEnforcementEngine(
    config_path=Path("src/config/governance.yaml"),
    memory_path=Path("data/compliance_memory")
)

logger.info("🚀 BuildToValue Gateway v7.3 initialized")


# === SCHEMAS (Pydantic Models) ===

class TenantPayload(BaseModel):
    """Schema para registro de tenant (Camada 2)"""
    id: str = Field(..., description="UUID v4 do tenant")
    name: str = Field(..., description="Nome da organização")
    policy: Dict[str, Any] = Field(
        default_factory=dict,
        description="Política de governança customizada"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Banco Seguro S.A.",
                "policy": {
                    "autonomy_matrix": {
                        "production": {"max_risk_level": 2.0}
                    },
                    "custom_rules": {
                        "block_public_apis_in_prod": True
                    }
                }
            }
        }
    }


class SystemPayload(BaseModel):
    """Schema para registro de sistema de IA (Camada 3)"""
    id: str = Field(..., description="ID único do sistema")
    name: str = Field(..., description="Nome do sistema")
    version: str = Field(default="1.0.0", description="Versão")
    sector: str = Field(..., description="Setor de aplicação (banking, healthcare, etc.)")
    role: str = Field(..., description="Role na cadeia de IA (provider, deployer, etc.)")
    risk: str = Field(..., description="Classificação de risco (high, limited, minimal)")
    sandbox: bool = Field(default=False, description="Modo sandbox ativo?")
    policy: Optional[Dict[str, Any]] = Field(default=None, description="Política específica")
    eu_database_id: Optional[str] = Field(default=None, description="ID EU Database (Art. 71)")
    training_flops: Optional[float] = Field(default=None, description="FLOPs de treinamento")
    logging_enabled: bool = Field(default=False, description="Logging capabilities")
    jurisdiction: str = Field(default="EU", description="Jurisdição legal")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "credit-scoring-v2",
                "name": "Credit Risk Scoring AI",
                "version": "2.1.0",
                "sector": "banking",
                "role": "deployer",
                "risk": "high",
                "sandbox": False,
                "eu_database_id": "EU-DB-12345",
                "training_flops": 1e24,
                "logging_enabled": True,
                "jurisdiction": "EU"
            }
        }
    }


class EnforceRequest(BaseModel):
    """Schema para enforcement de decisão"""
    system_id: str = Field(..., description="ID do sistema executor")
    prompt: str = Field(..., description="Prompt/tarefa a ser executada")
    env: str = Field(default="production", description="Ambiente (development, staging, production)")
    artifact_type: str = Field(default="code", description="Tipo de artefato (code, documentation, etc.)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "system_id": "credit-scoring-v2",
                "prompt": "Avaliar risco de crédito para cliente ID 12345",
                "env": "production",
                "artifact_type": "code"
            }
        }
    }


# === ENDPOINTS ===

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint com informações do framework"""
    return {
        "framework": "BuildToValue",
        "version": "7.3.0",
        "status": "operational",
        "compliance": {
            "iso_42001": "compliant",
            "eu_ai_act": "compliant"
        },
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health():
    """
    Health check endpoint (sem autenticação)

    Returns:
        Status do sistema
    """
    return {
        "status": "healthy",
        "version": "7.3.0",
        "security": "hardened"
    }


@app.post("/v1/tenants", tags=["Admin"], status_code=201)
async def register_tenant(
        payload: TenantPayload,
        token: TokenData = Depends(require_role(["admin"]))
):
    """
    Registra ou atualiza tenant (Camada 2 - Empresa)

    **Requer:** Role `admin`

    **Compliance:** ISO 42001 4.2 (Understanding Interested Parties)

    Args:
        payload: Dados do tenant
        token: JWT token validado

    Returns:
        Confirmação de registro
    """
    try:
        tenant_id = registry.register_tenant(
            tenant_id=payload.id,
            name=payload.name,
            policy=payload.policy
        )

        logger.info(
            f"Tenant registered by {token.user_id}: {tenant_id} ({payload.name})"
        )

        return {
            "status": "registered",
            "tenant_id": tenant_id,
            "message": f"Tenant '{payload.name}' registered successfully"
        }
    except Exception as e:
        logger.error(f"Failed to register tenant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/systems", tags=["Developer"], status_code=201)
async def register_system(
        payload: SystemPayload,
        token: TokenData = Depends(require_role(["admin", "dev"]))
):
    """
    Registra sistema de IA (Camada 3 - Projeto)

    **Requer:** Role `admin` ou `dev`

    **Security:** tenant_id extraído do JWT token (não do payload)

    **Compliance:** ISO 42001 6.1 (Actions to Address Risks)

    Args:
        payload: Dados do sistema
        token: JWT token validado

    Returns:
        Confirmação de registro
    """
    try:
        # Valida enums
        try:
            role_enum = AIRole(payload.role)
            sector_enum = AISector(payload.sector)
            risk_enum = EUComplianceRisk(payload.risk)
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid enum value: {e}"
            )

        # Cria entidade AISystem
        system = AISystem(
            id=payload.id,
            tenant_id=token.tenant_id,  # CRITICAL: do token, não do payload
            name=payload.name,
            version=payload.version,
            role=role_enum,
            sector=sector_enum,
            risk_classification=risk_enum,
            is_sandbox_mode=payload.sandbox,
            governance_policy=payload.policy,
            eu_database_registration_id=payload.eu_database_id,
            training_compute_flops=payload.training_flops,
            logging_capabilities=payload.logging_enabled,
            jurisdiction=payload.jurisdiction
        )

        # Registra no registry (com validação de tenant)
        system_id = registry.register_system(
            system=system,
            requesting_tenant=token.tenant_id
        )

        logger.info(
            f"AI System registered by {token.user_id}: {system_id} "
            f"(tenant: {token.tenant_id})"
        )

        return {
            "status": "registered",
            "system_id": system_id,
            "tenant_id": token.tenant_id,
            "message": f"System '{payload.name}' registered successfully"
        }

    except ValueError as e:
        # Validação de entidade falhou
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to register system: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/enforce", tags=["Enforcement"])
async def enforce(
        req: EnforceRequest,
        token: TokenData = Depends(require_role(["admin", "dev", "app"]))
):
    """
    Executa enforcement de governança em runtime

    **Requer:** Role `admin`, `dev` ou `app`

    **Compliance:**
    - ISO 42001 8.2 (AI Risk Assessment - Operation)
    - EU AI Act Art. 12 (Logging)

    Args:
        req: Requisição de enforcement
        token: JWT token validado

    Returns:
        Decisão (ALLOWED/BLOCKED) com metadados
    """
    try:
        # Busca sistema com validação de acesso (BOLA protection)
        system = registry.get_system(
            system_id=req.system_id,
            requesting_tenant=token.tenant_id
        )

        if not system:
            logger.warning(
                f"System not found or access denied: {req.system_id} "
                f"(requester: {token.user_id}, tenant: {token.tenant_id})"
            )
            raise HTTPException(
                status_code=404,
                detail="System not found or access denied"
            )

        # Cria task
        try:
            artifact_enum = ArtifactType(req.artifact_type)
        except ValueError:
            artifact_enum = ArtifactType.CODE

        task = Task(
            title=req.prompt,
            description="",
            artifact_type=artifact_enum
        )

        # Executa enforcement
        decision = engine.enforce(
            task=task,
            system=system,
            env=req.env
        )

        logger.info(
            f"Enforcement executed: {decision['decision']} | "
            f"Risk: {decision['risk_score']} | "
            f"System: {req.system_id} | "
            f"User: {token.user_id}"
        )

        return decision

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enforcement failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/systems/{system_id}", tags=["Developer"])
async def get_system(
        system_id: str,
        token: TokenData = Depends(require_role(["admin", "dev", "auditor"]))
):
    """
    Busca detalhes de um sistema de IA

    **Requer:** Role `admin`, `dev` ou `auditor`

    Args:
        system_id: ID do sistema
        token: JWT token validado

    Returns:
        Dados do sistema (se pertencer ao tenant)
    """
    system = registry.get_system(
        system_id=system_id,
        requesting_tenant=token.tenant_id
    )

    if not system:
        raise HTTPException(
            status_code=404,
            detail="System not found or access denied"
        )

    return {
        "id": system.id,
        "name": system.name,
        "version": system.version,
        "tenant_id": system.tenant_id,
        "sector": system.sector.value,
        "role": system.role.value,
        "risk_classification": system.risk_classification.value,
        "is_sandbox": system.is_sandbox_mode,
        "jurisdiction": system.jurisdiction,
        "eu_database_id": system.eu_database_registration_id,
        "logging_enabled": system.logging_capabilities
    }


@app.get("/v1/systems", tags=["Developer"])
async def list_systems(
        limit: int = 100,
        token: TokenData = Depends(require_role(["admin", "dev", "auditor"]))
):
    """
    Lista sistemas do tenant

    **Requer:** Role `admin`, `dev` ou `auditor`

    Args:
        limit: Número máximo de resultados
        token: JWT token validado

    Returns:
        Lista de sistemas do tenant
    """
    systems = registry.list_systems_by_tenant(
        tenant_id=token.tenant_id,
        limit=limit
    )

    return {
        "tenant_id": token.tenant_id,
        "count": len(systems),
        "systems": [
            {
                "id": s.id,
                "name": s.name,
                "version": s.version,
                "sector": s.sector.value,
                "risk": s.risk_classification.value
            }
            for s in systems
        ]
    }


@app.get("/v1/compliance/statistics", tags=["Audit"])
async def get_compliance_stats(
        token: TokenData = Depends(require_role(["admin", "auditor"]))
):
    """
    Estatísticas de compliance

    **Requer:** Role `admin` ou `auditor`

    Returns:
        Métricas agregadas de compliance
    """
    stats = engine.memory.get_statistics()

    return {
        "tenant_id": token.tenant_id,
        "statistics": stats,
        "compliance_status": "healthy" if stats["total_violations"] < 10 else "review_required"
    }


@app.get("/v1/audit/pending-reviews", tags=["Audit"])
async def get_pending_reviews(
        limit: int = 10,
        token: TokenData = Depends(require_role(["admin", "auditor"]))
):
    """
    Lista revisões humanas pendentes

    **Requer:** Role `admin` ou `auditor`

    **Compliance:** EU AI Act Art. 14 (Human Oversight)

    Returns:
        Lista de decisões aguardando revisão humana
    """
    reviews = engine.oversight.get_pending_reviews(limit=limit)

    return {
        "tenant_id": token.tenant_id,
        "pending_count": len(reviews),
        "reviews": reviews
    }


# === ERROR HANDLERS ===

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler customizado para HTTPException"""
    return {
        "error": True,
        "status_code": exc.status_code,
        "message": exc.detail
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler para exceções não tratadas"""
    logger.error(f"Unhandled exception: {exc}")
    return {
        "error": True,
        "status_code": 500,
        "message": "Internal server error"
    }


# === STARTUP EVENT ===

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização"""
    logger.info("=" * 80)
    logger.info("🚀 BuildToValue Framework v7.3")
    logger.info("=" * 80)
    logger.info("Security: Hardened (JWT + RBAC + HMAC Ledger)")
    logger.info("Compliance: ISO 42001 + EU AI Act")
    logger.info("Multi-Tenant: Enabled (UUID validation)")
    logger.info("=" * 80)


# === MAIN (Para executar com python gateway.py) ===

def main():
    """Entry point para execução standalone"""
    import uvicorn
    uvicorn.run(
        "src.interface.api.gateway:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
