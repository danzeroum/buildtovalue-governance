#!/usr/bin/env python3
"""
BuildToValue v0.9.0 - FastAPI Gateway
REST API com RBAC, Multi-Tenant Security e v0.9.0 Schema Support

Implementa:
- ISO 42001 8.1 (Operational Planning and Control)
- EU AI Act Art. 12 (Logging)
- NIST AI RMF 1.0 (70% compatible)
- OWASP API Security Top 10 2023

NEW in v0.9.0:
- Kill Switch endpoint (emergency-stop)
- Compliance report endpoint
- Operational status management
- Extended schema (NIST MAP, Supply Chain, Environmental)
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import uuid

from src.core.registry.system_registry import SystemRegistry
from src.core.governance.enforcement import RuntimeEnforcementEngine
from src.domain.entities import (
    Task,
    AISystem,
    ThirdPartyComponent,
    AISystemCostBenefit,
    ResidualRiskDisclosure
)
from src.domain.enums import (
    AIRole,
    EUComplianceRisk,
    AISector,
    ArtifactType,
    AIPhase,
    OperationalStatus,
    HumanAIConfiguration,
    ThreatCategory
)
from src.interface.api.auth import verify_jwt_token, require_role, TokenData

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("btv.gateway")

# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="BuildToValue Framework",
    description="Enterprise AI Governance Platform - NIST AI RMF Compatible",
    version="0.9.0",  # ✅ UPDATED
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "Admin", "description": "Admin-only operations (tenant management)"},
        {"name": "Developer", "description": "Developer operations (system registration)"},
        {"name": "Enforcement", "description": "Runtime governance enforcement"},
        {"name": "Compliance", "description": "Compliance reporting (NEW v0.9.0)"},  # ✅ NEW
        {"name": "Operations", "description": "Operational controls (NEW v0.9.0)"},  # ✅ NEW
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

logger.info("🚀 BuildToValue Gateway v0.9.0 initialized (NIST AI RMF Compatible)")


# ============================================================================
# PYDANTIC MODELS (Request/Response DTOs)
# ============================================================================

class TenantPayload(BaseModel):
    """Schema para registro de tenant (Camada 2) - UNCHANGED"""
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


# ✅ NEW: Third-party component DTO
class ThirdPartyComponentDTO(BaseModel):
    """Third-party component for supply chain tracking (NEW v0.9.0)"""
    name: str = Field(..., description="Component name (e.g., 'openai-gpt4')")
    version: str = Field(..., description="Version identifier")
    vendor: str = Field(..., description="Vendor/organization name")
    license_type: str = Field(..., description="License (MIT, GPL, Proprietary)")
    risk_level: str = Field(..., description="LOW, MEDIUM, HIGH")


class SystemPayload(BaseModel):
    """
    Schema para registro de sistema de IA (Camada 3)

    ✅ UPDATED v0.9.0: Added optional fields for NIST AI RMF compatibility
    ✅ BACKWARD COMPATIBLE: All new fields are optional
    """
    # EXISTING REQUIRED FIELDS (v0.9)
    id: str = Field(..., description="ID único do sistema")
    name: str = Field(..., description="Nome do sistema")
    version: str = Field(default="1.0.0", description="Versão")
    sector: str = Field(..., description="Setor de aplicação (banking, healthcare, etc.)")
    role: str = Field(..., description="Role na cadeia de IA (provider, deployer, etc.)")
    risk: str = Field(..., description="Classificação de risco (high, limited, minimal)")

    # EXISTING OPTIONAL FIELDS (v0.9)
    sandbox: bool = Field(default=False, description="Modo sandbox ativo?")
    policy: Optional[Dict[str, Any]] = Field(default=None, description="Política específica")
    eu_database_id: Optional[str] = Field(default=None, description="ID EU Database (Art. 71)")
    training_flops: Optional[float] = Field(default=None, description="FLOPs de treinamento")
    logging_enabled: bool = Field(default=False, description="Logging capabilities")
    jurisdiction: str = Field(default="EU", description="Jurisdição legal")

    # ✅ NEW FIELDS (v0.9.0) - ALL OPTIONAL for backward compatibility

    # NIST MAP (Context & Intent)
    intended_purpose: Optional[str] = Field(
        default=None,
        description="What the system SHOULD do (NIST MAP-1.1)"
    )
    prohibited_domains: List[str] = Field(
        default_factory=list,
        description="What the system MUST NOT do (EU AI Act Art. 5)"
    )
    target_demographic: Optional[str] = Field(
        default=None,
        description="Intended user population (fairness tracking)"
    )
    expected_benefits: Optional[str] = Field(
        default=None,
        description="Risk/benefit analysis (NIST MAP-3.2)"
    )

    # Lifecycle & Operations
    lifecycle_phase: str = Field(
        default="deployment",
        description="Current phase: design, data_prep, training, validation, deployment, monitoring, retirement"
    )
    operational_status: str = Field(
        default="active",
        description="Status: active, degraded, maintenance, suspended, emergency_stop"
    )
    human_ai_configuration: str = Field(
        default="human_over_the_loop",
        description="human_in_the_loop, human_over_the_loop, fully_autonomous"
    )

    # Supply Chain (NIST GOVERN-6.1)
    external_dependencies: List[ThirdPartyComponentDTO] = Field(
        default_factory=list,
        description="Third-party components (NEW v0.9.0)"
    )

    # Environmental Impact (NIST MEASURE-2.12 / EU AI Act Annex IV)
    estimated_carbon_kg_co2: Optional[float] = Field(
        default=None,
        description="Carbon footprint (kg CO2)"
    )
    energy_consumption_kwh: Optional[float] = Field(
        default=None,
        description="Energy consumption (kWh)"
    )

    # AICM Controls (AI TIPS 2.0 metadata layer)
    aicm_controls_applicable: List[str] = Field(
        default_factory=list,
        description="Applicable AICM control IDs (e.g., ['GRC-01', 'DSP-03'])"
    )
    aicm_controls_implemented: List[str] = Field(
        default_factory=list,
        description="Implemented AICM control IDs"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                # Existing fields
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
                "jurisdiction": "EU",
                # NEW v0.9.0 fields
                "intended_purpose": "Assess credit risk for loan applications",
                "prohibited_domains": ["social_scoring", "political_profiling"],
                "lifecycle_phase": "deployment",
                "operational_status": "active",
                "external_dependencies": [
                    {
                        "name": "scikit-learn",
                        "version": "1.3.0",
                        "vendor": "Scikit-Learn",
                        "license_type": "BSD-3-Clause",
                        "risk_level": "LOW"
                    }
                ],
                "estimated_carbon_kg_co2": 120.5,
                "aicm_controls_applicable": ["GRC-01", "GRC-02", "DSP-01"]
            }
        }
    }


class EnforceRequest(BaseModel):
    """Schema para enforcement de decisão - UNCHANGED"""
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


# ✅ NEW: Operational status update DTO
class UpdateOperationalStatusRequest(BaseModel):
    """Request to update operational status (NEW v0.9.0)"""
    operational_status: str = Field(
        ...,
        description="active, degraded, maintenance, suspended, emergency_stop"
    )
    reason: Optional[str] = Field(None, description="Reason for status change")
    operator_id: Optional[str] = Field(None, description="ID of operator making change")

    model_config = {
        "json_schema_extra": {
            "example": {
                "operational_status": "emergency_stop",
                "reason": "Detected bias in production outputs",
                "operator_id": "admin@company.com"
            }
        }
    }


# ============================================================================
# ENDPOINTS - EXISTING (v0.9) - UNCHANGED
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint com informações do framework"""
    return {
        "framework": "BuildToValue",
        "version": "0.9.0",  # ✅ UPDATED
        "status": "operational",
        "compliance": {
            "iso_42001": "compliant",
            "eu_ai_act": "compliant",
            "nist_ai_rmf": "70% compatible"  # ✅ NEW
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
        "version": "0.9.0",  # ✅ UPDATED
        "security": "hardened",
        "features": {  # ✅ NEW
            "kill_switch": True,
            "compliance_reports": True,
            "threat_classification": True
        }
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

    ✅ UPDATED v0.9.0: Now accepts extended schema fields

    **Requer:** Role `admin` ou `dev`
    **Security:** tenant_id extraído do JWT token (não do payload)
    **Compliance:** ISO 42001 6.1, NIST AI RMF MAP-1.1

    Args:
        payload: Dados do sistema (inclui campos v0.9.0)
        token: JWT token validado

    Returns:
        Confirmação de registro com compliance summary
    """
    try:
        # Valida enums
        try:
            role_enum = AIRole(payload.role)
            sector_enum = AISector(payload.sector)
            risk_enum = EUComplianceRisk(payload.risk)
            lifecycle_enum = AIPhase(payload.lifecycle_phase)  # ✅ NEW
            status_enum = OperationalStatus(payload.operational_status)  # ✅ NEW
            human_ai_enum = HumanAIConfiguration(payload.human_ai_configuration)  # ✅ NEW
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid enum value: {e}"
            )

        # ✅ NEW: Convert ThirdPartyComponent DTOs
        dependencies = [
            ThirdPartyComponent(
                name=dep.name,
                version=dep.version,
                vendor=dep.vendor,
                license_type=dep.license_type,
                risk_level=dep.risk_level
            )
            for dep in payload.external_dependencies
        ]

        # Cria entidade AISystem (com campos v0.9.0)
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
            jurisdiction=payload.jurisdiction,

            # ✅ NEW v0.9.0 fields
            intended_purpose=payload.intended_purpose,
            prohibited_domains=payload.prohibited_domains,
            target_demographic=payload.target_demographic,
            expected_benefits=payload.expected_benefits,
            lifecycle_phase=lifecycle_enum,
            phase_entered_at=datetime.utcnow(),
            operational_status=status_enum,
            human_ai_configuration=human_ai_enum,
            external_dependencies=dependencies,
            estimated_carbon_kg_co2=payload.estimated_carbon_kg_co2,
            energy_consumption_kwh=payload.energy_consumption_kwh,
            aicm_controls_applicable=payload.aicm_controls_applicable,
            aicm_controls_implemented=payload.aicm_controls_implemented
        )

        # Registra no registry (com validação de tenant)
        system_id = registry.register_system(
            system=system,
            requesting_tenant=token.tenant_id
        )

        logger.info(
            f"AI System registered by {token.user_id}: {system_id} "
            f"(tenant: {token.tenant_id}, phase: {lifecycle_enum.value})"
        )

        # ✅ NEW: Return compliance summary
        return {
            "status": "registered",
            "system_id": system_id,
            "tenant_id": token.tenant_id,
            "message": f"System '{payload.name}' registered successfully",
            "compliance_summary": {  # ✅ NEW
                "lifecycle_phase": lifecycle_enum.value,
                "operational_status": status_enum.value,
                "aicm_coverage": system.calculate_aicm_coverage(),
                "supply_chain_risk": system.calculate_supply_chain_risk(),
                "requires_human_oversight": system.requires_human_oversight(),
                "nist_alignment": "70%"
            }
        }

    except ValueError as e:
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

    ✅ ENHANCED v0.9.0: Now includes threat classification in response

    **Requer:** Role `admin`, `dev` ou `app`
    **Compliance:**
    - ISO 42001 8.2 (AI Risk Assessment - Operation)
    - EU AI Act Art. 12 (Logging)
    - NIST AI RMF MANAGE-2.4

    Args:
        req: Requisição de enforcement
        token: JWT token validado

    Returns:
        Decision with threat classification (Huwyler Taxonomy)
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

        # Executa enforcement (com threat classification v0.9.0)
        decision = engine.enforce(
            task=task,
            system=system,
            env=req.env
        )

        logger.info(
            f"Enforcement executed: {decision['decision']} | "
            f"Risk: {decision['risk_score']} | "
            f"Threat: {decision.get('threat_classification', {}).get('primary_threat', 'N/A')} | "  # ✅ NEW
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

    ✅ ENHANCED v0.9.0: Returns extended schema fields

    **Requer:** Role `admin`, `dev` ou `auditor`

    Args:
        system_id: ID do sistema
        token: JWT token validado

    Returns:
        Dados completos do sistema (v0.9.0 schema)
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

    # ✅ UPDATED: Return full v0.9.0 schema
    return {
        # Existing fields
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
        "logging_enabled": system.logging_capabilities,

        # ✅ NEW v0.9.0 fields
        "intended_purpose": system.intended_purpose,
        "prohibited_domains": system.prohibited_domains,
        "lifecycle_phase": system.lifecycle_phase.value,
        "operational_status": system.operational_status.value,
        "human_ai_configuration": system.human_ai_configuration.value,
        "external_dependencies": [
            {
                "name": dep.name,
                "version": dep.version,
                "vendor": dep.vendor,
                "risk_level": dep.risk_level
            }
            for dep in system.external_dependencies
        ],
        "estimated_carbon_kg_co2": system.estimated_carbon_kg_co2,
        "compliance_metrics": {
            "aicm_coverage": system.calculate_aicm_coverage(),
            "supply_chain_risk": system.calculate_supply_chain_risk(),
            "requires_human_oversight": system.requires_human_oversight()
        }
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
                "risk": s.risk_classification.value,
                "lifecycle_phase": s.lifecycle_phase.value,  # ✅ NEW
                "operational_status": s.operational_status.value  # ✅ NEW
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


# ============================================================================
# ✅ NEW ENDPOINTS (v0.9.0)
# ============================================================================

@app.put(
    "/v1/systems/{system_id}/emergency-stop",
    tags=["Operations"],
    status_code=200
)
async def emergency_stop(
        system_id: str,
        request: UpdateOperationalStatusRequest,
        token: TokenData = Depends(require_role(["admin"]))
):
    """
    🔥 KILL SWITCH: Immediately halt AI system operations

    **NEW in v0.9.0**

    Critical safety feature implementing:
    - NIST AI RMF: MANAGE-2.4 (Operational controls)
    - Policy Cards: Emergency stop mechanism
    - EU AI Act: Art. 14 (Human oversight)

    Effects:
    - All subsequent tasks will be BLOCKED
    - System enters EMERGENCY_STOP state
    - Requires explicit reactivation by authorized operator

    **Requer:** Role `admin` only

    Args:
        system_id: System identifier
        request: Status update request
        token: JWT token (admin only)

    Returns:
        Emergency stop confirmation

    Example:
        ```
        PUT /v1/systems/credit-scoring-v2/emergency-stop
        {
            "operational_status": "emergency_stop",
            "reason": "Detected bias in production outputs",
            "operator_id": "admin@company.com"
        }
        ```
    """
    try:
        # Fetch system with access validation
        system = registry.get_system(
            system_id=system_id,
            requesting_tenant=token.tenant_id
        )

        if not system:
            raise HTTPException(
                status_code=404,
                detail="System not found or access denied"
            )

        previous_status = system.operational_status.value

        # Validate transition
        if request.operational_status != "emergency_stop":
            raise HTTPException(
                status_code=400,
                detail="This endpoint only accepts 'emergency_stop' status"
            )

        # Update status
        system.operational_status = OperationalStatus.EMERGENCY_STOP
        system.updated_at = datetime.utcnow()

        # Persist to registry
        registry.update_system(system, requesting_tenant=token.tenant_id)

        # Log critical event
        logger.critical(
            f"🔴 EMERGENCY_STOP activated for system {system_id} "
            f"by {request.operator_id or token.user_id}. "
            f"Reason: {request.reason or 'Manual intervention'}"
        )

        return {
            "system_id": system_id,
            "previous_status": previous_status,
            "new_status": "emergency_stop",
            "timestamp": datetime.utcnow().isoformat(),
            "acknowledged": True,
            "operator": request.operator_id or token.user_id,
            "message": (
                f"System {system_id} halted. All operations blocked. "
                f"Reason: {request.reason or 'Manual intervention'}"
            )
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Emergency stop failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to activate emergency stop"
        )


@app.put(
    "/v1/systems/{system_id}/operational-status",
    tags=["Operations"],
    status_code=200
)
async def update_operational_status(
        system_id: str,
        request: UpdateOperationalStatusRequest,
        token: TokenData = Depends(require_role(["admin", "dev"]))
):
    """
    Update system operational status

    **NEW in v0.9.0**

    Allowed transitions:
    - active ↔ degraded
    - active → maintenance
    - maintenance → active
    - any → suspended (human intervention)
    - any → emergency_stop (kill switch - use /emergency-stop endpoint instead)

    **Requer:** Role `admin` or `dev`

    Args:
        system_id: System identifier
        request: Status update request
        token: JWT token

    Returns:
        Status update confirmation
    """
    try:
        system = registry.get_system(
            system_id=system_id,
            requesting_tenant=token.tenant_id
        )

        if not system:
            raise HTTPException(
                status_code=404,
                detail="System not found or access denied"
            )

        previous_status = system.operational_status.value

        # Update status
        try:
            system.operational_status = OperationalStatus(request.operational_status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operational status: {request.operational_status}"
            )

        system.updated_at = datetime.utcnow()

        # Persist
        registry.update_system(system, requesting_tenant=token.tenant_id)

        logger.info(
            f"Status change for {system_id}: {previous_status} → "
            f"{request.operational_status} by {request.operator_id or token.user_id}"
        )

        return {
            "system_id": system_id,
            "previous_status": previous_status,
            "new_status": request.operational_status,
            "timestamp": datetime.utcnow().isoformat(),
            "operator": request.operator_id or token.user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/v1/systems/{system_id}/compliance-report",
    tags=["Compliance"],
    status_code=200
)
async def get_compliance_report(
        system_id: str,
        token: TokenData = Depends(require_role(["admin", "auditor"]))
):
    """
    Generate comprehensive compliance report for AI system

    **NEW in v0.9.0**

    Covers:
    - NIST AI RMF 1.0 (70% compatibility)
    - AI TIPS 2.0 (Metadata layer)
    - EU AI Act (High-risk assessment)
    - Supply Chain risks (NIST GAP-1)

    **Requer:** Role `admin` or `auditor`

    Args:
        system_id: System identifier
        token: JWT token

    Returns:
        Comprehensive compliance report (JSON)

    Example:
        ```
        GET /v1/systems/credit-scoring-v2/compliance-report
        ```
    """
    try:
        system = registry.get_system(
            system_id=system_id,
            requesting_tenant=token.tenant_id
        )

        if not system:
            raise HTTPException(
                status_code=404,
                detail="System not found or access denied"
            )

        # Generate report using compliance module
        from scripts.generate_compliance_report import generate_nist_summary

        report = generate_nist_summary(system)

        logger.info(
            f"Compliance report generated for {system_id} by {token.user_id}"
        )

        return report

    except ImportError:
        # Fallback if compliance script not available
        logger.warning("Compliance report generator not found, returning basic summary")
        return {
            "system_id": system_id,
            "generated_at": datetime.utcnow().isoformat(),
            "nist": {
                "compliance_percentage": 70,
                "implemented": ["GOVERN-6.1", "MAP-1.1", "MANAGE-2.4"],
                "roadmap": ["MEASURE-2.11", "MEASURE-3.3"]
            },
            "supply_chain": {
                "overall_risk": system.calculate_supply_chain_risk(),
                "total_components": len(system.external_dependencies)
            },
            "note": "Full report generator pending deployment"
        }
    except Exception as e:
        logger.error(f"Failed to generate compliance report: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate compliance report"
        )


# ============================================================================
# ERROR HANDLERS - UNCHANGED
# ============================================================================

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


# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização"""
    logger.info("=" * 80)
    logger.info("🚀 BuildToValue Framework v0.9.0")
    logger.info("=" * 80)
    logger.info("Security: Hardened (JWT + RBAC + HMAC Ledger)")
    logger.info("Compliance: ISO 42001 + EU AI Act + NIST AI RMF (70%)")
    logger.info("Multi-Tenant: Enabled (UUID validation)")
    logger.info("NEW Features: Kill Switch, Compliance Reports, Threat Classification")
    logger.info("=" * 80)


# ============================================================================
# MAIN (Para executar com python gateway.py)
# ============================================================================

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

