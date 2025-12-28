"""
System Registry with Multi-Tenant Isolation (BOLA Protection)
✅ UPDATED v0.9.0: Added Kill Switch support and NIST AI RMF schema

Implements:
- SQL Injection Prevention (SQLAlchemy ORM)
- BOLA/IDOR Protection (tenant_id validation)
- ISO 42001 A.10.2 (Allocating Responsibilities)
- Kill Switch (operational_status column)
- NIST AI RMF lifecycle tracking (lifecycle_phase column)
"""

from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional, Dict
import logging
import os

from src.domain.entities import AISystem
from src.domain.enums import (
    AISector,
    AIRole,
    EUComplianceRisk,
    AIPhase,                      # ✅ ADDED v0.9.0
    OperationalStatus,            # ✅ ADDED v0.9.0
    HumanAIConfiguration          # ✅ ADDED v0.9.0
)

Base = declarative_base()
logger = logging.getLogger("btv.registry")


class TenantModel(Base):
    """
    Tenant Model (Layer 2 - Organization)

    Stores organization-specific governance policies
    """
    __tablename__ = "tenants"

    id = Column(String, primary_key=True)  # UUID v4
    name = Column(String, nullable=False)
    governance_policy = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Tenant(id={self.id}, name={self.name})>"


class AISystemModel(Base):
    """
    AI System Model (Layer 3 - Project)
    ✅ UPDATED v0.9.0: Added columns for Kill Switch and NIST lifecycle tracking

    Implements multi-tenant isolation via tenant_id index
    """
    __tablename__ = "ai_systems"

    # Existing columns (unchanged)
    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False, index=True)  # Logical FK + Index
    name = Column(String, nullable=False)
    version = Column(String, default="1.0.0")
    sector = Column(String, nullable=False)
    role = Column(String, nullable=False)
    risk_classification = Column(String, nullable=False)
    high_risk_flags = Column(JSON, default=list)
    governance_policy = Column(JSON, nullable=True)
    is_sandbox_mode = Column(Integer, default=0)
    training_compute_flops = Column(Integer, nullable=True)
    eu_database_registration_id = Column(String, nullable=True)
    logging_capabilities = Column(Integer, default=0)
    jurisdiction = Column(String, default="EU")

    # ✅ NEW COLUMNS v0.9.0 (Kill Switch + NIST AI RMF)
    lifecycle_phase = Column(String, default="deployment")
    operational_status = Column(String, default="active")
    human_ai_configuration = Column(String, default="human_over_the_loop")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Composite index for multi-tenant query performance
    __table_args__ = (
        Index('idx_tenant_system', 'tenant_id', 'id'),
    )

    def __repr__(self):
        return f"<AISystem(id={self.id}, tenant={self.tenant_id}, name={self.name})>"


class SystemRegistry:
    """
    AI System Registry with Multi-Tenant Isolation
    ✅ UPDATED v0.9.0: Added update_system() method for Kill Switch persistence

    Security Features:
    - SQL Injection Prevention: SQLAlchemy ORM (no raw queries)
    - BOLA Protection: tenant_id validation in all queries
    - Audit Trail: created_at/updated_at timestamps
    """

    def __init__(self, db_url: str = None):
        """
        Initialize registry with database

        Args:
            db_url: Database URL (SQLite or PostgreSQL)
                    If None, reads from DB_URL env var or defaults to SQLite
        """
        # ✅ IMPROVED: Support environment variable
        if not db_url:
            db_url = os.getenv("DB_URL", "sqlite:///./data/btv_registry.db")

        self.engine = create_engine(
            db_url,
            echo=False,  # Set True for SQL debug
            pool_pre_ping=True,  # Validate connections
        )

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"SystemRegistry initialized with {db_url}")

    # === TENANT MANAGEMENT (Layer 2) ===

    def register_tenant(self, tenant_id: str, name: str, policy: Dict) -> str:
        """
        Register or update tenant (Upsert)

        Args:
            tenant_id: Tenant UUID v4
            name: Organization name
            policy: Governance policy (JSON)

        Returns:
            Registered tenant_id

        Compliance:
            ISO 42001 4.2 (Understanding interested parties)
        """
        session = self.Session()
        try:
            tenant = TenantModel(
                id=tenant_id,
                name=name,
                governance_policy=policy
            )

            session.merge(tenant)  # Safe upsert
            session.commit()
            logger.info(f"Tenant registered: {tenant_id} ({name})")
            return tenant_id

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to register tenant {tenant_id}: {e}")
            raise
        finally:
            session.close()

    def get_tenant_policy(
            self,
            tenant_id: str,
            requesting_tenant: str
    ) -> Dict:
        """
        Retrieve tenant policy with ACCESS CONTROL

        Args:
            tenant_id: Target tenant ID
            requesting_tenant: Requesting tenant ID

        Returns:
            Governance policy (or {} if access denied)

        Security:
            BOLA Protection - Tenant can only access its own policies
        """
        # CRITICAL: Cross-tenant access validation
        if tenant_id != requesting_tenant:
            logger.warning(
                f"SECURITY ALERT: Cross-tenant access attempt detected! "
                f"Requester: {requesting_tenant} tried to access {tenant_id}"
            )
            # Returns empty (does not expose if tenant exists)
            return {}

        session = self.Session()
        try:
            # Query using ORM (prevents SQL Injection)
            tenant = session.query(TenantModel).filter_by(id=tenant_id).first()

            if not tenant:
                logger.warning(f"Tenant not found: {tenant_id}")
                return {}

            return tenant.governance_policy or {}

        finally:
            session.close()

    # === AI SYSTEM MANAGEMENT (Layer 3) ===

    def register_system(
            self,
            system: AISystem,
            requesting_tenant: str
    ) -> str:
        """
        Register AI system with tenant validation
        ✅ UPDATED v0.9.0: Now persists operational_status, lifecycle_phase, human_ai_configuration

        Args:
            system: AISystem entity
            requesting_tenant: Tenant ID from JWT token

        Returns:
            Registered system_id

        Security:
            Mass Assignment Protection - tenant_id comes from token, not payload

        Raises:
            ValueError: If payload tenant_id doesn't match token
        """
        # CRITICAL: Prevents Mass Assignment Attack
        if system.tenant_id != requesting_tenant:
            raise ValueError(
                f"Tenant ID mismatch: System claims tenant_id={system.tenant_id} "
                f"but JWT token belongs to {requesting_tenant}. "
                f"Possible security attack detected!"
            )

        session = self.Session()
        try:
            model = AISystemModel(
                id=system.id,
                tenant_id=requesting_tenant,  # Forces token usage
                name=system.name,
                version=system.version,
                sector=system.sector.value,
                role=system.role.value,
                risk_classification=system.risk_classification.value,

                # ✅ NEW v0.9.0: Map Kill Switch and lifecycle fields
                lifecycle_phase=system.lifecycle_phase.value,
                operational_status=system.operational_status.value,
                human_ai_configuration=system.human_ai_configuration.value,

                high_risk_flags=system.high_risk_flags,
                governance_policy=system.governance_policy,
                is_sandbox_mode=1 if system.is_sandbox_mode else 0,
                training_compute_flops=system.training_compute_flops,
                eu_database_registration_id=system.eu_database_registration_id,
                logging_capabilities=1 if system.logging_capabilities else 0,
                jurisdiction=system.jurisdiction
            )

            session.merge(model)  # Upsert
            session.commit()
            logger.info(
                f"AI System registered: {system.id} | "
                f"Tenant: {requesting_tenant} | "
                f"Risk: {system.risk_classification.value} | "
                f"Status: {system.operational_status.value}"  # ✅ Log status
            )
            return system.id

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to register system {system.id}: {e}")
            raise
        finally:
            session.close()

    def update_system(
            self,
            system: AISystem,
            requesting_tenant: str
    ) -> str:
        """
        ✅ ADDED v0.9.0: Update existing AI system (alias for register_system)

        This method was missing and caused HTTP 500 errors in /emergency-stop endpoint.
        Since SQLAlchemy's merge() performs upsert, we can reuse register_system().

        Args:
            system: AISystem entity with updated fields
            requesting_tenant: Tenant ID from JWT token

        Returns:
            Updated system_id

        Usage:
            Used by Kill Switch endpoint to persist operational_status changes
        """
        return self.register_system(system, requesting_tenant)

    def get_system(
            self,
            system_id: str,
            requesting_tenant: str
    ) -> Optional[AISystem]:
        """
        Retrieve system with multi-tenant isolation
        ✅ UPDATED v0.9.0: Reconstructs entity with v0.9.0 fields (backward compatible)

        Args:
            system_id: System ID
            requesting_tenant: Tenant ID from JWT token

        Returns:
            AISystem entity or None if not found/no access

        Security:
            BOLA Protection - Query filters by system_id AND tenant_id
        """
        session = self.Session()
        try:
            # CRITICAL: Query with tenant_id (isolation)
            model = session.query(AISystemModel).filter_by(
                id=system_id,
                tenant_id=requesting_tenant  # Ensures isolation
            ).first()

            if not model:
                logger.warning(
                    f"System not found or access denied: {system_id} "
                    f"(requester: {requesting_tenant})"
                )
                return None

            # ✅ BACKWARD COMPATIBILITY: Handle old records without v0.9.0 columns
            lifecycle = getattr(model, 'lifecycle_phase', 'deployment') or 'deployment'
            status = getattr(model, 'operational_status', 'active') or 'active'
            human_cfg = getattr(model, 'human_ai_configuration', 'human_over_the_loop') or 'human_over_the_loop'

            # Rebuild entity
            return AISystem(
                id=model.id,
                tenant_id=model.tenant_id,
                name=model.name,
                version=model.version,
                role=AIRole(model.role),
                sector=AISector(model.sector),
                risk_classification=EUComplianceRisk(model.risk_classification),

                # ✅ NEW v0.9.0: Reconstruct with lifecycle fields
                lifecycle_phase=AIPhase(lifecycle),
                operational_status=OperationalStatus(status),
                human_ai_configuration=HumanAIConfiguration(human_cfg),

                high_risk_flags=model.high_risk_flags or [],
                governance_policy=model.governance_policy or {},
                is_sandbox_mode=bool(model.is_sandbox_mode),
                training_compute_flops=model.training_compute_flops,
                eu_database_registration_id=model.eu_database_registration_id,
                logging_capabilities=bool(model.logging_capabilities),
                jurisdiction=model.jurisdiction
            )

        finally:
            session.close()

    def list_systems_by_tenant(self, tenant_id: str, limit: int = 100) -> list:
        """
        List all systems of a tenant
        ✅ UPDATED v0.9.0: Returns systems with v0.9.0 fields

        Args:
            tenant_id: Tenant ID
            limit: Maximum number of results

        Returns:
            List of AISystem entities
        """
        session = self.Session()
        try:
            models = session.query(AISystemModel).filter_by(
                tenant_id=tenant_id
            ).limit(limit).all()

            # ✅ Use get_system() for consistent entity reconstruction
            systems = []
            for model in models:
                system = self.get_system(model.id, tenant_id)
                if system:
                    systems.append(system)

            return systems

        finally:
            session.close()
