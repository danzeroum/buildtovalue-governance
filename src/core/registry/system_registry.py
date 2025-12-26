"""
System Registry com Isolamento Multi-Tenant (BOLA Protection)

Implementa:
- SQL Injection Prevention (SQLAlchemy ORM)
- BOLA/IDOR Protection (tenant_id validation)
- ISO 42001 A.10.2 (Allocating Responsibilities)
"""

from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional, Dict
import logging

from src.domain.entities import AISystem
from src.domain.enums import AISector, AIRole, EUComplianceRisk

Base = declarative_base()
logger = logging.getLogger("btv.registry")


class TenantModel(Base):
    """
    Modelo de Tenant (Camada 2 - Empresa)

    Armazena políticas de governança específicas da organização
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
    Modelo de Sistema de IA (Camada 3 - Projeto)

    Implementa isolamento multi-tenant via tenant_id index
    """
    __tablename__ = "ai_systems"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False, index=True)  # FK lógica + Index
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Índice composto para performance em queries multi-tenant
    __table_args__ = (
        Index('idx_tenant_system', 'tenant_id', 'id'),
    )

    def __repr__(self):
        return f"<AISystem(id={self.id}, tenant={self.tenant_id}, risk={self.risk_classification})>"


class SystemRegistry:
    """
    Registry de Sistemas de IA com Isolamento Multi-Tenant

    Security Features:
    - SQL Injection Prevention: SQLAlchemy ORM (no raw queries)
    - BOLA Protection: tenant_id validation em todas as queries
    - Audit Trail: created_at/updated_at timestamps
    """

    def __init__(self, db_url: str = "sqlite:///./data/btv_registry.db"):
        """
        Inicializa registry com banco de dados

        Args:
            db_url: Database URL (SQLite ou PostgreSQL)
        """
        self.engine = create_engine(
            db_url,
            echo=False,  # Set True para debug SQL
            pool_pre_ping=True,  # Valida conexões
        )
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"SystemRegistry initialized with {db_url}")

    # === TENANT MANAGEMENT (Camada 2) ===

    def register_tenant(self, tenant_id: str, name: str, policy: Dict) -> str:
        """
        Registra ou atualiza tenant (Upsert)

        Args:
            tenant_id: UUID v4 do tenant
            name: Nome da organização
            policy: Política de governança (JSON)

        Returns:
            tenant_id registrado

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
            session.merge(tenant)  # Upsert seguro
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
        Busca política do tenant com CONTROLE DE ACESSO

        Args:
            tenant_id: ID do tenant alvo
            requesting_tenant: ID do tenant que está fazendo a requisição

        Returns:
            Política de governança (ou {} se acesso negado)

        Security:
            BOLA Protection - Tenant só pode acessar suas próprias políticas
        """
        # CRITICAL: Validação de acesso cross-tenant
        if tenant_id != requesting_tenant:
            logger.warning(
                f"SECURITY ALERT: Cross-tenant access attempt detected! "
                f"Requester: {requesting_tenant} tried to access {tenant_id}"
            )
            # Retorna vazio (não expõe se tenant existe)
            return {}

        session = self.Session()
        try:
            # Query usando ORM (previne SQL Injection)
            tenant = session.query(TenantModel).filter_by(id=tenant_id).first()

            if not tenant:
                logger.warning(f"Tenant not found: {tenant_id}")
                return {}

            return tenant.governance_policy or {}
        finally:
            session.close()

    # === AI SYSTEM MANAGEMENT (Camada 3) ===

    def register_system(
            self,
            system: AISystem,
            requesting_tenant: str
    ) -> str:
        """
        Registra sistema de IA com validação de tenant

        Args:
            system: Entidade AISystem
            requesting_tenant: Tenant ID do JWT token

        Returns:
            system_id registrado

        Security:
            Mass Assignment Protection - tenant_id vem do token, não do payload

        Raises:
            ValueError: Se tenant_id do payload não match com o do token
        """
        # CRITICAL: Previne Mass Assignment Attack
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
                tenant_id=requesting_tenant,  # Força uso do token
                name=system.name,
                version=system.version,
                sector=system.sector.value,
                role=system.role.value,
                risk_classification=system.risk_classification.value,
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
                f"Risk: {system.risk_classification.value}"
            )
            return system.id
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to register system {system.id}: {e}")
            raise
        finally:
            session.close()

    def get_system(
            self,
            system_id: str,
            requesting_tenant: str
    ) -> Optional[AISystem]:
        """
        Busca sistema com isolamento multi-tenant

        Args:
            system_id: ID do sistema
            requesting_tenant: Tenant ID do JWT token

        Returns:
            AISystem entity ou None se não encontrado/sem acesso

        Security:
            BOLA Protection - Query filtra por system_id AND tenant_id
        """
        session = self.Session()
        try:
            # CRITICAL: Query com tenant_id (isolamento)
            model = session.query(AISystemModel).filter_by(
                id=system_id,
                tenant_id=requesting_tenant  # Garante isolamento
            ).first()

            if not model:
                logger.warning(
                    f"System not found or access denied: {system_id} "
                    f"(requester: {requesting_tenant})"
                )
                return None

            # Reconstrói entity
            return AISystem(
                id=model.id,
                tenant_id=model.tenant_id,
                name=model.name,
                version=model.version,
                role=AIRole(model.role),
                sector=AISector(model.sector),
                risk_classification=EUComplianceRisk(model.risk_classification),
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
        Lista todos os sistemas de um tenant

        Args:
            tenant_id: ID do tenant
            limit: Número máximo de resultados

        Returns:
            Lista de AISystem entities
        """
        session = self.Session()
        try:
            models = session.query(AISystemModel).filter_by(
                tenant_id=tenant_id
            ).limit(limit).all()

            return [
                AISystem(
                    id=m.id,
                    tenant_id=m.tenant_id,
                    name=m.name,
                    version=m.version,
                    role=AIRole(m.role),
                    sector=AISector(m.sector),
                    risk_classification=EUComplianceRisk(m.risk_classification),
                    high_risk_flags=m.high_risk_flags or [],
                    governance_policy=m.governance_policy or {},
                    is_sandbox_mode=bool(m.is_sandbox_mode),
                    training_compute_flops=m.training_compute_flops,
                    eu_database_registration_id=m.eu_database_registration_id,
                    logging_capabilities=bool(m.logging_capabilities),
                    jurisdiction=m.jurisdiction
                )
                for m in models
            ]
        finally:
            session.close()
