#!/usr/bin/env python3
"""
BuildToValue v0.9.0 - FastAPI Gateway
REST API with RBAC, Multi-Tenant Security and v0.9.0 Schema Support

Implements:
- ISO 42001 8.1 (Operational Planning and Control)
- EU AI Act Art. 12 (Logging)
- NIST AI RMF 1.0 (70% compatible)
- OWASP API Security Top 10 2023

NEW in v0.9.0:
- Kill Switch endpoint (emergency-stop)
- Compliance report endpoint
- Operational status management
- Extended schema (NIST MAP, Supply Chain, Environmental)

✅ UPDATED: Fixed datetime.utcnow() and FastAPI lifespan deprecations
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, UTC
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
import logging
import uuid

from src.core.registry.system_registry import SystemRegistry
from src.core.governance.enforcement import EnforcementEngine
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
# ✅ LIFESPAN CONTEXT MANAGER (Replaces deprecated @app.on_event)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events
    ✅ Replaces deprecated @app.on_event("startup")
    """
    # Startup
    logger.info("=" * 80)
    logger.info("🚀 BuildToValue Framework v0.9.0")
    logger.info("=" * 80)
    logger.info("Security: Hardened (JWT + RBAC + HMAC Ledger)")
    logger.info("Compliance: ISO 42001 + EU AI Act + NIST AI RMF (70%)")
    logger.info("Multi-Tenant: Enabled (UUID validation)")
    logger.info("NEW Features: Kill Switch, Compliance Reports, Threat Classification")
    logger.info("=" * 80)

    yield  # Application runs here

    # Shutdown (if needed in future)
    logger.info("🛑 BuildToValue Gateway shutting down")


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="BuildToValue Framework",
    description="Enterprise AI Governance Platform - NIST AI RMF Compatible",
    version="0.9.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # ✅ ADDED: Use lifespan instead of on_event
    openapi_tags=[
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "Admin", "description": "Admin-only operations (tenant management)"},
        {"name": "Developer", "description": "Developer operations (system registration)"},
        {"name": "Enforcement", "description": "Runtime governance enforcement"},
        {"name": "Compliance", "description": "Compliance reporting (NEW v0.9.0)"},
        {"name": "Operations", "description": "Operational controls (NEW v0.9.0)"},
        {"name": "Audit", "description": "Audit and compliance reporting"}
    ]
)

# CORS (configure for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In prod: specify domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singletons (lazy initialization)
registry = SystemRegistry()
engine = EnforcementEngine(penalty_config_path="src/config/regulatory_penalties.yaml")

logger.info("🚀 BuildToValue Gateway v0.9.0 initialized (NIST AI RMF Compatible)")


# ============================================================================
# PYDANTIC MODELS (Request/Response DTOs)
# ============================================================================

class TenantPayload(BaseModel):
    """Schema for tenant registration (Layer 2) - UNCHANGED"""
    id: str = Field(..., description="Tenant UUID v4")
    name: str = Field(..., description="Organization name")
    policy: Dict[str, Any] = Field(
        default_factory=dict,
        description="Customized governance policy"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Secure Bank Inc.",
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


class ThirdPartyComponentDTO(BaseModel):
    """Third-party component for supply chain tracking (NEW v0.9.0)"""
    name: str = Field(..., description="Component name (e.g., 'openai-gpt4')")
    version: str = Field(..., description="Version identifier")
    vendor: str = Field(..., description="Vendor/organization name")
    license_type: str = Field(..., description="License (MIT, GPL, Proprietary)")
    risk_level: str = Field(..., description="LOW, MEDIUM, HIGH")


class SystemPayload(BaseModel):
    """
    Schema for AI system registration (Layer 3)
    ✅ UPDATED v0.9.0: Added optional fields for NIST AI RMF compatibility
    ✅ BACKWARD COMPATIBLE: All new fields are optional
    """
    # EXISTING REQUIRED FIELDS (v0.9)
    id: str = Field(..., description="Unique system ID")
    name: str = Field(..., description="System name")
    version: str = Field(default="1.0.0", description="Version")
    sector: str = Field(..., description="Application sector (banking, healthcare, etc.)")
    role: str = Field(..., description="AI chain role (provider, deployer, etc.)")
    risk: str = Field(..., description="Risk classification (high, limited, minimal)")

    # EXISTING OPTIONAL FIELDS (v0.9)
    sandbox: bool = Field(default=False, description="Sandbox mode active?")
    policy: Optional[Dict[str, Any]] = Field(default=None, description="Specific policy")
    eu_database_id: Optional[str] = Field(default=None, description="EU Database ID (Art. 71)")
    training_flops: Optional[float] = Field(default=None, description="Training FLOPs")
    logging_enabled: bool = Field(default=False, description="Logging capabilities")
    jurisdiction: str = Field(default="EU", description="Legal jurisdiction")

    # NEW FIELDS (v0.9.0) - ALL OPTIONAL for backward compatibility
    intended_purpose: Optional[str] = Field(default=None, description="What the system SHOULD do (NIST MAP-1.1)")
    prohibited_domains: List[str] = Field(default_factory=list,
                                          description="What the system MUST NOT do (EU AI Act Art. 5)")
    target_demographic: Optional[str] = Field(default=None, description="Intended user population (fairness tracking)")
    expected_benefits: Optional[str] = Field(default=None, description="Risk/benefit analysis (NIST MAP-3.2)")

    lifecycle_phase: str = Field(default="deployment",
                                 description="Current phase: design, data_prep, training, validation, deployment, monitoring, retirement")
    operational_status: str = Field(default="active",
                                    description="Status: active, degraded, maintenance, suspended, emergency_stop")
    human_ai_configuration: str = Field(default="human_over_the_loop",
                                        description="human_in_the_loop, human_over_the_loop, fully_autonomous")

    external_dependencies: List[ThirdPartyComponentDTO] = Field(default_factory=list,
                                                                description="Third-party components (NEW v0.9.0)")

    estimated_carbon_kg_co2: Optional[float] = Field(default=None, description="Carbon footprint (kg CO2)")
    energy_consumption_kwh: Optional[float] = Field(default=None, description="Energy consumption (kWh)")

    aicm_controls_applicable: List[str] = Field(default_factory=list, description="Applicable AICM control IDs")
    aicm_controls_implemented: List[str] = Field(default_factory=list, description="Implemented AICM control IDs")

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
                "jurisdiction": "EU",
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
    """Schema for decision enforcement - UNCHANGED"""
    system_id: str = Field(..., description="Executing system ID")
    prompt: str = Field(..., description="Prompt/task to execute")
    env: str = Field(default="production", description="Environment (development, staging, production)")
    artifact_type: str = Field(default="code", description="Artifact type (code, documentation, etc.)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "system_id": "credit-scoring-v2",
                "prompt": "Assess credit risk for customer ID 12345",
                "env": "production",
                "artifact_type": "code"
            }
        }
    }


class UpdateOperationalStatusRequest(BaseModel):
    """Request to update operational status (NEW v0.9.0)"""
    operational_status: str = Field(..., description="active, degraded, maintenance, suspended, emergency_stop")
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
# ENDPOINTS - HEALTH
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with framework information"""
    return {
        "framework": "BuildToValue",
        "version": "0.9.0",
        "status": "operational",
        "compliance": {
            "iso_42001": "compliant",
            "eu_ai_act": "compliant",
            "nist_ai_rmf": "70% compatible"
        },
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint (no authentication required)"""
    return {
        "status": "healthy",
        "version": "0.9.0",
        "security": "hardened",
        "features": {
            "kill_switch": True,
            "compliance_reports": True,
            "threat_classification": True
        }
    }


# ============================================================================
# ENDPOINTS - ADMIN
# ============================================================================

@app.post("/v1/tenants", tags=["Admin"], status_code=201)
async def register_tenant(
        payload: TenantPayload,
        token: TokenData = Depends(require_role(["admin"]))
):
    """
    Register or update tenant (Layer 2 - Organization)
    **Requires:** Role `admin`
    **Compliance:** ISO 42001 4.2 (Understanding Interested Parties)
    """
    try:
        tenant_id = registry.register_tenant(
            tenant_id=payload.id,
            name=payload.name,
            policy=payload.policy
        )

        logger.info(f"Tenant registered by {token.user_id}: {tenant_id} ({payload.name})")

        return {
            "status": "registered",
            "tenant_id": tenant_id,
            "message": f"Tenant '{payload.name}' registered successfully"
        }
    except Exception as e:
        logger.error(f"Failed to register tenant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS - DEVELOPER
# ============================================================================

@app.post("/v1/systems", tags=["Developer"], status_code=201)
async def register_system(
        payload: SystemPayload,
        token: TokenData = Depends(require_role(["admin", "dev"]))
):
    """
    Register AI system (Layer 3 - Project)
    ✅ UPDATED v0.9.0: Now accepts extended schema fields
    """
    try:
        # Validate enums
        try:
            role_enum = AIRole(payload.role)
            sector_enum = AISector(payload.sector)
            risk_enum = EUComplianceRisk(payload.risk)
            lifecycle_enum = AIPhase(payload.lifecycle_phase)
            status_enum = OperationalStatus(payload.operational_status)
            human_ai_enum = HumanAIConfiguration(payload.human_ai_configuration)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid enum value: {e}")

        # Convert ThirdPartyComponent DTOs
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

        # Create AISystem entity
        system = AISystem(
            id=payload.id,
            tenant_id=token.tenant_id,
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
            intended_purpose=payload.intended_purpose,
            prohibited_domains=payload.prohibited_domains,
            target_demographic=payload.target_demographic,
            expected_benefits=payload.expected_benefits,
            lifecycle_phase=lifecycle_enum,
            operational_status=status_enum,
            human_ai_configuration=human_ai_enum,
            external_dependencies=dependencies,
            estimated_carbon_kg_co2=payload.estimated_carbon_kg_co2,
            energy_consumption_kwh=payload.energy_consumption_kwh,
            aicm_controls_applicable=payload.aicm_controls_applicable,
            aicm_controls_implemented=payload.aicm_controls_implemented
        )

        # Register in registry
        system_id = registry.register_system(system=system, requesting_tenant=token.tenant_id)

        logger.info(f"AI System registered by {token.user_id}: {system_id} (tenant: {token.tenant_id})")

        return {
            "status": "registered",
            "system_id": system_id,
            "tenant_id": token.tenant_id,
            "message": f"System '{payload.name}' registered successfully",
            "compliance_summary": {
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
    Execute governance enforcement at runtime
    ✅ ENHANCED v0.9.0: Now includes threat classification in response
    """
    try:
        # Fetch system with access validation
        system = registry.get_system(system_id=req.system_id, requesting_tenant=token.tenant_id)

        if not system:
            logger.warning(f"System not found or access denied: {req.system_id}")
            raise HTTPException(status_code=404, detail="System not found or access denied")

        # Create task
        try:
            artifact_enum = ArtifactType(req.artifact_type)
        except ValueError:
            artifact_enum = ArtifactType.CODE

        task = Task(title=req.prompt, description="", artifact_type=artifact_enum)

        # Execute enforcement
        decision = engine.enforce(task=task, system=system, env=req.env)

        logger.info(
            f"Enforcement executed: {decision.outcome} | "
            f"Risk: {decision.risk_score} | "
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
    """Retrieve AI system details ✅ ENHANCED v0.9.0: Returns extended schema fields"""
    system = registry.get_system(system_id=system_id, requesting_tenant=token.tenant_id)

    if not system:
        raise HTTPException(status_code=404, detail="System not found or access denied")

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
        "logging_enabled": system.logging_capabilities,
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
    """List tenant systems"""
    systems = registry.list_systems_by_tenant(tenant_id=token.tenant_id, limit=limit)

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
                "lifecycle_phase": s.lifecycle_phase.value,
                "operational_status": s.operational_status.value
            }
            for s in systems
        ]
    }


# ============================================================================
# ENDPOINTS - OPERATIONS (Kill Switch)
# ============================================================================

@app.put("/v1/systems/{system_id}/emergency-stop", tags=["Operations"], status_code=200)
async def emergency_stop(
        system_id: str,
        request: UpdateOperationalStatusRequest,
        token: TokenData = Depends(require_role(["admin"]))
):
    """
    🔥 KILL SWITCH: Immediately halt AI system operations
    **NEW in v0.9.0**
    """
    try:
        system = registry.get_system(system_id=system_id, requesting_tenant=token.tenant_id)

        if not system:
            raise HTTPException(status_code=404, detail="System not found or access denied")

        previous_status = system.operational_status.value

        if request.operational_status != "emergency_stop":
            raise HTTPException(status_code=400, detail="This endpoint only accepts 'emergency_stop' status")

        # Update status
        system.operational_status = OperationalStatus.EMERGENCY_STOP
        system.updated_at = datetime.now(UTC)  # ✅ FIXED

        # Persist
        registry.update_system(system, requesting_tenant=token.tenant_id)

        logger.critical(
            f"🔴 EMERGENCY_STOP activated for system {system_id} "
            f"by {request.operator_id or token.user_id}. "
            f"Reason: {request.reason or 'Manual intervention'}"
        )

        return {
            "system_id": system_id,
            "previous_status": previous_status,
            "new_status": "emergency_stop",
            "timestamp": datetime.now(UTC).isoformat(),  # ✅ FIXED
            "acknowledged": True,
            "operator": request.operator_id or token.user_id,
            "message": f"System {system_id} halted. All operations blocked. Reason: {request.reason or 'Manual intervention'}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Emergency stop failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to activate emergency stop")


@app.put("/v1/systems/{system_id}/operational-status", tags=["Operations"], status_code=200)
async def update_operational_status(
        system_id: str,
        request: UpdateOperationalStatusRequest,
        token: TokenData = Depends(require_role(["admin", "dev"]))
):
    """Update system operational status **NEW in v0.9.0**"""
    try:
        system = registry.get_system(system_id=system_id, requesting_tenant=token.tenant_id)

        if not system:
            raise HTTPException(status_code=404, detail="System not found or access denied")

        previous_status = system.operational_status.value

        # Update status
        try:
            system.operational_status = OperationalStatus(request.operational_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid operational status: {request.operational_status}")

        system.updated_at = datetime.now(UTC)  # ✅ FIXED

        # Persist
        registry.update_system(system, requesting_tenant=token.tenant_id)

        logger.info(f"Status change for {system_id}: {previous_status} → {request.operational_status}")

        return {
            "system_id": system_id,
            "previous_status": previous_status,
            "new_status": request.operational_status,
            "timestamp": datetime.now(UTC).isoformat(),  # ✅ FIXED
            "operator": request.operator_id or token.user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ENDPOINTS - COMPLIANCE
# ============================================================================

@app.get("/v1/systems/{system_id}/compliance-report", tags=["Compliance"], status_code=200)
async def get_compliance_report(
        system_id: str,
        token: TokenData = Depends(require_role(["admin", "auditor"]))
):
    """
    Generate comprehensive compliance report for AI system
    **NEW in v0.9.0**
    """
    try:
        system = registry.get_system(system_id=system_id, requesting_tenant=token.tenant_id)

        if not system:
            raise HTTPException(status_code=404, detail="System not found or access denied")

        # Generate report using compliance module
        try:
            from scripts.generate_compliance_report import generate_nist_summary
            report = generate_nist_summary(system)
            logger.info(f"Compliance report generated for {system_id} by {token.user_id}")
            return report
        except ImportError:
            # Fallback if compliance script not available
            logger.warning("Compliance report generator not found, returning basic summary")
            return {
                "system_id": system_id,
                "generated_at": datetime.now(UTC).isoformat(),  # ✅ FIXED
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
        raise HTTPException(status_code=500, detail="Failed to generate compliance report")


# ============================================================================
# ENDPOINTS - AUDIT
# ============================================================================

@app.get("/v1/compliance/statistics", tags=["Audit"])
async def get_compliance_stats(
        token: TokenData = Depends(require_role(["admin", "auditor"]))
):
    """Compliance statistics"""
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
    """List pending human reviews"""
    reviews = engine.oversight.get_pending_reviews(limit=limit)
    return {
        "tenant_id": token.tenant_id,
        "pending_count": len(reviews),
        "reviews": reviews
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom handler for HTTPException"""
    return JSONResponse(  # ✅ CORREÇÃO: Retorna JSONResponse
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(  # ✅ CORREÇÃO: Retorna JSONResponse
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error"
        }
    )
# ============================================================================
# MAIN (For running with python gateway.py)
# ============================================================================

def main():
    """Entry point for standalone execution"""
    import uvicorn
    uvicorn.run(
        "src.interface.api.gateway:app",
        host="0.0.0.0", # nosec B104
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
