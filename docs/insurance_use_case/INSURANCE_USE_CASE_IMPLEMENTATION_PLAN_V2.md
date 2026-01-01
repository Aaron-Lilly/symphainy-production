# 🎯 Insurance Use Case: Updated Strategic Implementation Plan

**Date:** December 2024  
**Status:** Ready for Implementation  
**Target:** Production-Grade Data Migration & Coexistence Platform  
**Version:** 2.0 (Updated with Solution/Journey Realms, Saga Journey, and WAL)

---

## 📋 Executive Summary

This plan transforms the existing CTO demo scenario (Data Mash Coexistence) into a production-ready, multi-year transformation platform for insurance data migration. The platform will serve as a **coexistence engine** that enables hybrid operations between legacy and modern systems while gradually retiring the legacy estate.

### **Key Updates in V2**

- ✅ **Solution Realm Integration**: Multi-phase solution orchestration via Solution Composer
- ✅ **Saga Journey Orchestrator**: Automatic compensation for wave migrations
- ✅ **Write-Ahead Logging (WAL)**: Data Steward capability for audit trail and durability
- ✅ **Corrected Directory Structure**: Aligned with actual platform architecture
- ✅ **Enhanced Governance**: WAL-powered audit trails and compliance tracking

### **Current State**
- ✅ **80% capability exists** in the platform today
- ✅ **All 3 CTO demo scenarios passing** (including Data Mash Coexistence)
- ✅ **Core infrastructure ready**: File ingestion, schema mapping, transformation engine
- ✅ **Solution & Journey Realms**: Complete and ready for use
- ✅ **Saga Journey**: Implemented with automatic compensation
- ⚠️ **Gaps identified**: Canonical model management, routing engine, wave-based migration, WAL integration

### **Target State**
- Production-grade data migration platform
- Multi-year coexistence support
- Wave-based migration orchestration with automatic rollback
- Full governance and traceability with WAL-powered audit trails
- Client onboarding toolkit
- Multi-phase solution orchestration

### **Timeline**
- **Phase 1 (MVP)**: 4-6 weeks
- **Phase 2 (Production)**: 8-12 weeks  
- **Phase 3 (Enterprise)**: 12-16 weeks

---

## 🏗️ Architecture Overview

### **Platform Foundation (Existing)**
```
┌─────────────────────────────────────────────────────────────┐
│                    Smart City Realm                          │
│  Data Steward (with WAL) │ Librarian │ Content Steward │   │
│  Conductor │ Post Office │ Security Guard │ Traffic Cop    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Solution Realm                            │
│  Solution Composer │ Solution Analytics │ Deployment Mgr    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Journey Realm                             │
│  Saga Journey Orchestrator │ Structured Journey │ MVP        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Business Enablement Realm                       │
│  Content │ Insights │ Operations │ Business Outcomes        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Insurance Use Case Layer                        │
│  [NEW] Canonical Model │ Routing Engine │ Wave Orchestrator │
└─────────────────────────────────────────────────────────────┘
```

### **Insurance Migration Solution Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│         Insurance Migration Solution (Solution Realm)        │
│  Phase 1: Discovery → Phase 2: Wave Migration → Phase 3: Val │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         Phase 2: Wave Migration (Saga Journey) ⭐          │
│  Milestone 1: Ingest → Milestone 2: Map → Milestone 3: Route│
│  Milestone 4: Migrate → Milestone 5: Validate               │
│  [Automatic Compensation on Failure]                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         Business Enablement Orchestrators                    │
│  InsuranceMigrationOrchestrator │ WaveOrchestrator          │
│  PolicyTrackerOrchestrator                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         Enabling Services                                    │
│  CanonicalModelService │ RoutingEngineService               │
│  FileParserService │ SchemaMapperService │ ...              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         Data Steward (with WAL) ⭐                           │
│  Write-Ahead Logging │ Lineage Tracking │ Policy Management │
│  [Every operation logged BEFORE execution]                   │
└─────────────────────────────────────────────────────────────┘
```

### **Data Flow with WAL**

```
Legacy System
    ↓
[Intake Layer] → File Upload → Profiling → Metadata Extraction
    ↓ (WAL: Logged via Data Steward)
[Canonicalization] → Source Schema → Canonical Model → Target Schema
    ↓ (WAL: Logged via Data Steward)
[Routing Engine] → Evaluate Rules → Select Target System
    ↓ (WAL: Logged via Data Steward)
[Saga Journey] → Wave Orchestration → Quality Gates → Execute Migration
    ↓ (WAL: Logged via Data Steward)
[Target System] → New Platform / Legacy / Bridge
    ↓ (WAL: Logged via Data Steward)
[Governance] → Track Lineage → Audit Trail → Policy Tracker
    ↓
[WAL Replay] → Recovery / Debugging / Compliance Audit
```

---

## 🚀 Phase 1: Foundation & Canonical Model (MVP) - 4-6 Weeks

### **Goal**
Deliver a working MVP that can ingest legacy insurance data, map it to a canonical model, demonstrate basic routing capabilities, and integrate with Solution/Journey realms with WAL-powered audit trails.

### **Week 1-2: Canonical Policy Model & WAL Integration**

#### **1.1 Define Canonical Policy Model v1**
**Location:** `backend/business_enablement/enabling_services/canonical_model_service/`

**Deliverables:**
- [ ] Create `canonical_policy_model.py` with frozen v1 schema
- [ ] Define 7 core components:
  - Policy Core (policy_id, status, effective_date, expiration_date)
  - Coverage Sections (coverage_type, limits, deductibles)
  - Rating Components (premium, factors, calculations)
  - Payments (payment_plan, billing_frequency, payment_history)
  - Correspondence (documents, communications, notices)
  - Endorsements (changes, modifications, riders)
  - Claims (links only - references to claims system)

**Implementation:**
```python
# backend/business_enablement/enabling_services/canonical_model_service/canonical_policy_model.py

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PolicyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class CoverageType(str, Enum):
    LIFE = "life"
    HEALTH = "health"
    PROPERTY = "property"
    LIABILITY = "liability"

class CanonicalPolicyCore(BaseModel):
    """Frozen v1 - Policy Core Component"""
    policy_id: str = Field(..., description="Unique policy identifier")
    status: PolicyStatus
    effective_date: datetime
    expiration_date: Optional[datetime]
    issue_date: datetime
    policy_type: str
    carrier: str
    insured_party: Dict[str, Any]
    agent_info: Optional[Dict[str, Any]] = None

class CanonicalCoverageSection(BaseModel):
    """Frozen v1 - Coverage Section Component"""
    coverage_id: str
    coverage_type: CoverageType
    limits: Dict[str, Any]
    deductibles: Dict[str, Any]
    effective_date: datetime
    expiration_date: Optional[datetime]

class CanonicalRatingComponent(BaseModel):
    """Frozen v1 - Rating Component"""
    premium_amount: float
    premium_frequency: str
    rating_factors: Dict[str, Any]
    calculations: Dict[str, Any]
    last_rated_date: datetime

class CanonicalPayment(BaseModel):
    """Frozen v1 - Payment Component"""
    payment_plan: str
    billing_frequency: str
    payment_history: List[Dict[str, Any]]
    outstanding_balance: Optional[float] = None

class CanonicalCorrespondence(BaseModel):
    """Frozen v1 - Correspondence Component"""
    documents: List[Dict[str, Any]]
    communications: List[Dict[str, Any]]
    notices: List[Dict[str, Any]]

class CanonicalEndorsement(BaseModel):
    """Frozen v1 - Endorsement Component"""
    endorsement_id: str
    endorsement_type: str
    effective_date: datetime
    changes: Dict[str, Any]

class CanonicalPolicyModel(BaseModel):
    """Frozen v1 - Complete Canonical Policy Model"""
    version: str = "1.0.0"
    policy_core: CanonicalPolicyCore
    coverage_sections: List[CanonicalCoverageSection]
    rating_components: CanonicalRatingComponent
    payments: CanonicalPayment
    correspondence: CanonicalCorrespondence
    endorsements: List[CanonicalEndorsement]
    claims_links: List[str] = Field(default_factory=list, description="References to claims system")
    
    class Config:
        frozen = True  # Prevent modifications to v1
```

#### **1.2 Create Canonical Model Service**
**Location:** `backend/business_enablement/enabling_services/canonical_model_service/canonical_model_service.py`

**Responsibilities:**
- [ ] Register and version canonical models
- [ ] Validate data against canonical schema
- [ ] Provide model registry API
- [ ] Support model evolution (v1 → v2 migration path)
- [ ] **Integrate with Data Steward WAL** for audit trail

**Key Methods:**
```python
class CanonicalModelService(RealmServiceBase):
    async def register_canonical_model(
        self, 
        model_name: str, 
        schema: Dict[str, Any], 
        version: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register canonical model with WAL logging.
        
        WAL Integration: Logs model registration BEFORE execution via Data Steward.
        """
        # Write to WAL via Data Steward
        await self.data_steward.write_to_log(
            namespace="canonical_model",
            payload={
                "operation": "register_model",
                "model_name": model_name,
                "version": version,
                "schema": schema
            },
            target="canonical_model_registry",
            lifecycle={"retry_count": 3}
        )
        
        # Then execute registration
        ...
    
    async def validate_against_canonical(
        self, 
        data: Dict[str, Any], 
        model_name: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate data against canonical model with WAL logging.
        """
        # Write to WAL
        await self.data_steward.write_to_log(
            namespace="canonical_model",
            payload={
                "operation": "validate",
                "model_name": model_name,
                "data": data
            },
            target="canonical_validation_queue"
        )
        
        # Then validate
        ...
```

#### **1.3 Add WAL Module to Data Steward** ⭐
**Location:** `backend/smart_city/services/data_steward/modules/write_ahead_logging.py`

**Deliverables:**
- [ ] Create Write-Ahead Logging module for Data Steward
- [ ] Implement `write_to_log()` method
- [ ] Implement `replay_log()` method
- [ ] Integrate with existing lineage tracking
- [ ] Support delayed retry and cross-region replication

**Implementation:**
```python
# backend/smart_city/services/data_steward/modules/write_ahead_logging.py

class WriteAheadLogging:
    """
    Write-Ahead Logging Module for Data Steward
    
    WHAT: Logs all critical operations BEFORE execution for durability and audit
    HOW: Provides durable, replayable log with delayed retry support
    
    Netflix-inspired WAL implementation as Data Steward governance capability.
    """
    
    async def write_to_log(
        self,
        namespace: str,
        payload: Dict[str, Any],
        target: str,
        lifecycle: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Write operation to WAL BEFORE execution.
        
        This is a governance operation - ensures audit trail and durability.
        
        Args:
            namespace: Logical group (e.g., "saga_execution", "canonical_model")
            payload: Operation data
            target: Where to send after logging (Kafka topic, queue, etc.)
            lifecycle: Retry count, delay, TTL, backoff strategy
        """
        # 1. Write to durable log (via Knowledge Governance Abstraction)
        # 2. Record lineage automatically (Data Steward already does this)
        # 3. Return durable confirmation
        # 4. Consumer processes from log
        pass
    
    async def replay_log(
        self,
        namespace: str,
        from_timestamp: datetime,
        to_timestamp: datetime,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Replay operations from WAL for recovery.
        
        Governance capability - enables audit and recovery.
        """
        pass
```

**Update Data Steward Service:**
```python
# backend/smart_city/services/data_steward/data_steward_service.py

class DataStewardService(SmartCityRoleBase):
    def __init__(self, ...):
        # Existing modules
        self.policy_management_module = PolicyManagement(self)
        self.lineage_tracking_module = LineageTracking(self)
        self.quality_compliance_module = QualityCompliance(self)
        
        # NEW: Write-Ahead Logging module
        self.write_ahead_logging_module = WriteAheadLogging(self)  # ⭐ NEW
    
    # NEW: WAL SOA APIs
    async def write_to_log(self, ...):
        """Write to WAL - governance capability."""
        return await self.write_ahead_logging_module.write_to_log(...)
    
    async def replay_log(self, ...):
        """Replay from WAL - governance capability."""
        return await self.write_ahead_logging_module.replay_log(...)
```

### **Week 2-3: Enhanced Schema Mapping with WAL**

#### **2.1 Enhance SchemaMapperService for Canonical Models**
**Location:** `backend/business_enablement/enabling_services/schema_mapper_service/`

**Enhancements:**
- [ ] Add canonical model as intermediate mapping target
- [ ] Support source → canonical → target mapping chains
- [ ] Add mapping rule versioning
- [ ] Store mapping rules in governance layer
- [ ] **Integrate with Data Steward WAL** for audit trail

**New Methods:**
```python
async def map_to_canonical(
    self,
    source_schema: Dict[str, Any],
    canonical_model_name: str,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Map source schema to canonical model with WAL logging.
    """
    # Write to WAL via Data Steward
    await self.data_steward.write_to_log(
        namespace="schema_mapping",
        payload={
            "operation": "map_to_canonical",
            "source_schema": source_schema,
            "canonical_model": canonical_model_name
        },
        target="schema_mapping_queue"
    )
    
    # Then execute mapping
    ...

async def map_from_canonical(
    self,
    canonical_data: Dict[str, Any],
    target_schema: Dict[str, Any],
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Map canonical data to target schema with WAL logging.
    """
    # Write to WAL
    await self.data_steward.write_to_log(
        namespace="schema_mapping",
        payload={
            "operation": "map_from_canonical",
            "canonical_data": canonical_data,
            "target_schema": target_schema
        },
        target="schema_mapping_queue"
    )
    
    # Then execute mapping
    ...
```

### **Week 3-4: Client Onboarding Kit**

#### **3.1 CLI Tool Development**
**Location:** `scripts/insurance_use_case/data_mash_cli.py`

**Commands:**
```bash
# Ingest legacy data
data-mash ingest ./client_drop/policy_dump_0425.dat --format=csv --tenant=client_abc

# Profile ingested data
data-mash profile --file-id=<file_id> --output=profile_report.json

# Map to canonical
data-mash map-to-canonical --source-schema=<schema_id> --canonical=policy_v1

# Validate mapping
data-mash validate-mapping --mapping-id=<mapping_id>

# Generate migration plan
data-mash generate-plan --source=<source_id> --target=<target_id> --canonical=policy_v1
```

### **Week 4-5: Basic Routing Engine**

#### **4.1 Routing Rules Engine**
**Location:** `backend/business_enablement/enabling_services/routing_engine_service/`

**Core Components:**
- [ ] Routing rules definition (YAML/JSON)
- [ ] Rule evaluation engine
- [ ] Policy routing key extraction
- [ ] Target system selection
- [ ] **Integrate with Data Steward WAL** for audit trail

**Routing Rules Format:**
```yaml
routing_rules:
  version: "1.0.0"
  rules:
    - name: "migrated_policies"
      condition:
        field: "policy_id"
        operator: "in"
        value: ["A*", "B*", "C*"]
      target: "NewPlatformAPI"
      priority: 1
    
    - name: "legacy_only_policies"
      condition:
        field: "payment_plan"
        operator: "equals"
        value: "legacy-only"
      target: "LegacyBatch"
      priority: 2
    
    - name: "data_quality_issues"
      condition:
        field: "data_quality_score"
        operator: "less_than"
        value: 0.8
      target: "DataQualityQueue"
      priority: 3
    
    - name: "default_route"
      condition: true
      target: "CoexistenceBridge"
      priority: 99
```

**Implementation:**
```python
class RoutingEngineService(RealmServiceBase):
    async def evaluate_routing(
        self, 
        policy_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate routing rules with WAL logging.
        """
        # Write to WAL via Data Steward
        await self.data_steward.write_to_log(
            namespace="routing_engine",
            payload={
                "operation": "evaluate_routing",
                "policy_data": policy_data
            },
            target="routing_evaluation_queue"
        )
        
        # Then evaluate routing
        ...
```

### **Week 5-6: Solution & Journey Integration**

#### **5.1 Create Insurance Migration Solution Template**
**Location:** `backend/solution/services/solution_composer_service/`

**Deliverables:**
- [ ] Create `insurance_migration` solution template
- [ ] Define 3 phases: Discovery, Wave Migration, Validation
- [ ] Integrate with Saga Journey for Phase 2

**Solution Template:**
```python
INSURANCE_MIGRATION_SOLUTION = {
    "solution_type": "insurance_migration",
    "name": "Insurance Data Migration Solution",
    "description": "Multi-phase insurance data migration with wave-based orchestration",
    "phases": [
        {
            "phase_id": "discovery",
            "name": "Discovery & Profiling",
            "journey_type": "structured",
            "journey_template": "insurance_discovery",
            "description": "Ingest, profile, and analyze legacy insurance data"
        },
        {
            "phase_id": "wave_migration",
            "name": "Wave-Based Migration",
            "journey_type": "saga",  # ⭐ Uses Saga Journey!
            "journey_template": "insurance_wave_migration",
            "description": "Wave-based migration with automatic compensation",
            "compensation_handlers": {
                "ingest_legacy_data": "delete_ingested_data",
                "map_to_canonical": "revert_canonical_mapping",
                "route_policies": "revert_routing",
                "execute_migration": "rollback_migration",
                "validate_results": "revert_validation"
            }
        },
        {
            "phase_id": "validation",
            "name": "Validation & Reconciliation",
            "journey_type": "structured",
            "journey_template": "insurance_validation",
            "description": "Validate migrated data and reconcile with source"
        }
    ]
}
```

#### **5.2 Create Insurance Saga Journey Template**
**Location:** `backend/journey/services/saga_journey_orchestrator_service/`

**Deliverables:**
- [ ] Create `insurance_wave_migration` Saga journey template
- [ ] Define milestones for wave migration
- [ ] Define compensation handlers
- [ ] Integrate with Business Enablement orchestrators

**Saga Journey Template:**
```python
INSURANCE_WAVE_MIGRATION_SAGA = {
    "journey_type": "insurance_wave_migration",
    "name": "Insurance Wave Migration Saga",
    "description": "Wave-based migration with automatic compensation",
    "milestones": [
        {
            "milestone_id": "ingest_legacy_data",
            "name": "Ingest Legacy Data",
            "service": "InsuranceMigrationOrchestrator",
            "operation": "ingest_legacy_data",
            "compensation_handler": "delete_ingested_data"
        },
        {
            "milestone_id": "map_to_canonical",
            "name": "Map to Canonical Model",
            "service": "CanonicalModelService",
            "operation": "map_to_canonical",
            "compensation_handler": "revert_canonical_mapping"
        },
        {
            "milestone_id": "route_policies",
            "name": "Route Policies",
            "service": "RoutingEngineService",
            "operation": "evaluate_routing",
            "compensation_handler": "revert_routing"
        },
        {
            "milestone_id": "execute_migration",
            "name": "Execute Migration",
            "service": "WaveOrchestrator",
            "operation": "execute_wave_migration",
            "compensation_handler": "rollback_migration"
        },
        {
            "milestone_id": "validate_results",
            "name": "Validate Results",
            "service": "PolicyTrackerOrchestrator",
            "operation": "validate_migration",
            "compensation_handler": "revert_validation"
        }
    ]
}
```

#### **5.3 Create Insurance Orchestrators**
**Location:** `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/`

**Deliverables:**
- [ ] Create `insurance_migration_orchestrator/`
- [ ] Create `wave_orchestrator/`
- [ ] Create `policy_tracker_orchestrator/`
- [ ] Integrate with enabling services
- [ ] Integrate with Data Steward WAL

**Implementation Pattern:**
```python
# backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/insurance_migration_orchestrator/insurance_migration_orchestrator.py

class InsuranceMigrationOrchestrator(OrchestratorBase):
    """
    Insurance Migration Orchestrator for Insurance Use Case.
    
    Extends OrchestratorBase for Smart City access.
    Delegates to enabling services: CanonicalModelService, RoutingEngineService, etc.
    Integrates with Data Steward WAL for audit trail.
    """
    
    def __init__(self, delivery_manager):
        super().__init__(
            service_name="InsuranceMigrationOrchestratorService",
            realm_name=delivery_manager.realm_name,
            platform_gateway=delivery_manager.platform_gateway,
            di_container=delivery_manager.di_container,
            business_orchestrator=delivery_manager
        )
        self.delivery_manager = delivery_manager
        
        # Enabling services (lazy initialization)
        self._canonical_model_service = None
        self._routing_engine_service = None
        self._data_steward = None  # For WAL integration
    
    async def ingest_legacy_data(
        self,
        file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest legacy insurance data with WAL logging.
        """
        # Write to WAL via Data Steward
        await self.data_steward.write_to_log(
            namespace="insurance_migration",
            payload={
                "operation": "ingest_legacy_data",
                "file_id": file_id
            },
            target="insurance_migration_queue"
        )
        
        # Then execute ingestion
        ...
```

### **Week 6: Integration & Testing**

#### **6.1 Integration Points**
- [ ] Connect Canonical Model Service to Schema Mapper
- [ ] Integrate Routing Engine with Operations Orchestrator
- [ ] Wire up CLI tool to platform APIs
- [ ] Connect to existing Content/Insights/Operations pillars
- [ ] Integrate Solution Composer with Saga Journey
- [ ] Integrate all services with Data Steward WAL

#### **6.2 MVP Test Suite**
**Location:** `tests/integration/insurance_use_case/phase1_mvp/`

**Test Scenarios:**
- [ ] Legacy data ingestion → canonical mapping
- [ ] Routing rule evaluation
- [ ] Basic policy tracking
- [ ] End-to-end MVP journey
- [ ] **Saga Journey with compensation** (simulate failure)
- [ ] **WAL replay** (recover from crash scenario)
- [ ] **Solution Composer** (multi-phase execution)

---

## 🏭 Phase 2: Routing & Wave Migration (Production) - 8-12 Weeks

### **Goal**
Deliver production-grade routing capabilities with wave-based migration orchestration, bi-directional data flows, and full WAL-powered audit trails.

### **Week 7-9: Advanced Routing Engine**

#### **2.1 Multi-System Routing**
- [ ] Support for multiple target systems
- [ ] Routing decision trees
- [ ] Conditional routing based on data quality
- [ ] Fallback routing strategies
- [ ] **WAL logging for all routing decisions**

#### **2.2 Routing State Management**
- [ ] Track policy routing history
- [ ] Support routing reversals
- [ ] Handle routing conflicts
- [ ] Audit routing decisions (via WAL)

### **Week 9-11: Wave-Based Migration Orchestration**

#### **3.1 Wave Definition & Management**
**Location:** `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/wave_orchestrator/`

**Wave Structure:**
```python
class MigrationWave(BaseModel):
    wave_id: str
    wave_number: int
    name: str
    description: str
    selection_criteria: Dict[str, Any]  # Routing rules for wave
    target_system: str
    scheduled_start: datetime
    scheduled_end: Optional[datetime]
    status: WaveStatus
    policies: List[str]  # Policy IDs in this wave
    success_count: int
    failure_count: int
    quality_gates: List[Dict[str, Any]]
```

**Wave Types:**
- **Wave 0**: Clean candidates → straight-through to new system
- **Wave 1+**: Higher complexity → routed by rules with quality gates

#### **3.2 Wave Orchestrator**
**Location:** `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/wave_orchestrator/wave_orchestrator.py`

**Responsibilities:**
- [ ] Wave planning and candidate selection
- [ ] Wave execution orchestration (via Saga Journey)
- [ ] Quality gate enforcement
- [ ] Rollback capabilities (via Saga compensation)
- [ ] Progress tracking and reporting
- [ ] **WAL logging for all wave operations**

**Integration Points:**
- Uses Saga Journey Orchestrator for wave execution
- Uses Data Steward for data quality validation
- Uses Data Steward WAL for audit trail
- Uses Operations Pillar for SOP execution
- Uses Business Outcomes Pillar for KPI tracking

#### **3.3 Quality Gates**
**Gate Types:**
- Data completeness threshold
- Data quality score minimum
- Schema mapping confidence
- Business rule validation
- Target system readiness

**All quality gate checks logged via WAL.**

### **Week 11-12: Bi-Directional Data Flows**

#### **4.1 Dual-Write Pattern**
- [ ] Write to both legacy and new systems
- [ ] Conflict resolution strategies
- [ ] Sync status tracking
- [ ] Rollback on failure (via Saga compensation)
- [ ] **WAL logging for all dual-write operations**

#### **4.2 Selective-Write Pattern**
- [ ] Route writes based on policy status
- [ ] Support read-from-legacy, write-to-new
- [ ] Support read-from-new, write-to-legacy (for corrections)
- [ ] **WAL logging for all selective-write operations**

#### **4.3 Sync Orchestration**
- [ ] Scheduled sync jobs
- [ ] Event-driven sync triggers
- [ ] Sync conflict resolution
- [ ] Sync audit trails (via WAL)

---

## 🏢 Phase 3: Governance & Production Readiness (Enterprise) - 12-16 Weeks

### **Goal**
Deliver enterprise-grade governance, traceability, and operational tooling for multi-year coexistence with full WAL-powered audit trails.

### **Week 13-14: Enhanced Governance**

#### **5.1 Policy Tracker Service**
**Location:** `backend/business_enablement/delivery_manager/insurance_use_case_orchestrators/policy_tracker_orchestrator/`

**Capabilities:**
- [ ] "Where is policy 12345?" query
- [ ] Policy lifecycle tracking
- [ ] System location history
- [ ] Migration status tracking
- [ ] Cross-system policy reconciliation
- [ ] **WAL-powered audit trail for all policy operations**

**API:**
```python
GET /api/v1/policy-tracker/locate/{policy_id}
GET /api/v1/policy-tracker/history/{policy_id}
GET /api/v1/policy-tracker/status/{policy_id}
GET /api/v1/policy-tracker/reconcile/{policy_id}
GET /api/v1/policy-tracker/audit-trail/{policy_id}  # ⭐ WAL-powered
```

#### **5.2 Mapping Rule Versioning**
- [ ] Version control for mapping rules
- [ ] Mapping rule approval workflow
- [ ] Change impact assessment
- [ ] Rollback capabilities
- [ ] **WAL logging for all mapping rule changes**

#### **5.3 Change Impact Assessment**
**Location:** `backend/business_enablement/enabling_services/change_impact_service/`

**Capabilities:**
- [ ] Analyze impact of mapping rule changes
- [ ] Identify affected policies
- [ ] Estimate migration impact
- [ ] Generate impact reports
- [ ] **WAL logging for all impact assessments**

### **Week 15-16: Operational Tooling**

#### **6.1 Data Pipeline Status Dashboard**
**Integration with Business Outcomes Pillar:**
- [ ] Real-time pipeline status
- [ ] Wave progress tracking
- [ ] Quality metrics visualization
- [ ] Error monitoring and alerting
- [ ] **WAL replay interface** for recovery

#### **6.2 Mapping Editor**
**Location:** `backend/business_enablement/enabling_services/mapping_editor_service/`

**Features:**
- [ ] Visual mapping interface (API backend)
- [ ] AI-assisted mapping suggestions
- [ ] Mapping validation
- [ ] Mapping rule testing
- [ ] Client-facing mapping editor (Phase 3+)
- [ ] **WAL logging for all mapping edits**

#### **6.3 Operational APIs**
**Additional Endpoints:**
```python
# Policy Operations
GET  /api/v1/insurance/policies/{policy_id}
PUT  /api/v1/insurance/policies/{policy_id}
POST /api/v1/insurance/policies/{policy_id}/migrate
POST /api/v1/insurance/policies/{policy_id}/rollback

# Wave Operations
GET  /api/v1/migration/waves
POST /api/v1/migration/waves
GET  /api/v1/migration/waves/{wave_id}/status
POST /api/v1/migration/waves/{wave_id}/execute
POST /api/v1/migration/waves/{wave_id}/rollback

# Governance (WAL-powered)
GET  /api/v1/governance/lineage/{policy_id}
GET  /api/v1/governance/audit-trail/{policy_id}  # ⭐ WAL replay
GET  /api/v1/governance/mapping-rules
POST /api/v1/governance/mapping-rules
GET  /api/v1/governance/impact-assessment
GET  /api/v1/governance/wal/replay  # ⭐ WAL replay endpoint
```

---

## 🏗️ Technical Architecture

### **Service Mappings**

| Insurance Use Case Component | Platform Service | Status |
|------------------------------|------------------|--------|
| **Intake Layer** | Content Pillar + Content Steward | ✅ Ready |
| **Profiling Module** | Content Analysis Composition Service | ✅ Ready |
| **Metadata Extraction** | Librarian + Content Steward | ✅ Ready |
| **Canonical Model** | Canonical Model Service | 🆕 New |
| **Schema Mapping** | Schema Mapper Service | ✅ Ready (needs enhancement) |
| **Routing Engine** | Routing Engine Service | 🆕 New |
| **Wave Orchestration** | Saga Journey Orchestrator + Wave Orchestrator | 🆕 New |
| **Transformation** | Transformation Engine Service | ✅ Ready |
| **Data Quality** | Data Steward + Data Analyzer | ✅ Ready |
| **Lineage Tracking** | Data Steward | ✅ Ready |
| **Write-Ahead Logging** | Data Steward (WAL Module) | 🆕 New |
| **Policy Tracker** | Policy Tracker Orchestrator | 🆕 New |
| **Governance** | Data Steward + Governance Layer | ✅ Ready (needs enhancement) |
| **Solution Orchestration** | Solution Composer Service | ✅ Ready |
| **Journey Orchestration** | Saga Journey Orchestrator | ✅ Ready |

### **Directory Structure (Corrected)**

```
backend/business_enablement/
├── enabling_services/
│   ├── canonical_model_service/        🆕 New
│   │   ├── canonical_model_service.py
│   │   ├── canonical_policy_model.py
│   │   └── modules/
│   ├── routing_engine_service/         🆕 New
│   │   ├── routing_engine_service.py
│   │   └── modules/
│   └── ... (existing services)
│
└── delivery_manager/
    └── insurance_use_case_orchestrators/  🆕 New (corrected location)
        ├── insurance_migration_orchestrator/
        │   ├── insurance_migration_orchestrator.py
        │   └── mcp_server/
        ├── wave_orchestrator/
        │   ├── wave_orchestrator.py
        │   └── mcp_server/
        └── policy_tracker_orchestrator/
            ├── policy_tracker_orchestrator.py
            └── mcp_server/

backend/smart_city/services/data_steward/
├── data_steward_service.py
└── modules/
    ├── policy_management.py
    ├── lineage_tracking.py
    ├── quality_compliance.py
    └── write_ahead_logging.py  🆕 New WAL Module

backend/solution/services/solution_composer_service/
└── solution_composer_service.py
    └── (Insurance Migration Solution Template) 🆕 New

backend/journey/services/saga_journey_orchestrator_service/
└── saga_journey_orchestrator_service.py
    └── (Insurance Wave Migration Saga Template) 🆕 New
```

### **Integration Points**

1. **Solution Realm** → Multi-phase solution orchestration
2. **Journey Realm** → Saga Journey for wave migration with compensation
3. **Business Enablement Realm** → Insurance orchestrators and enabling services
4. **Smart City Services**:
   - **Data Steward (with WAL)** → Audit trail, durability, governance
   - **Librarian** → Knowledge management
   - **Conductor** → Workflow orchestration
   - **Post Office** → Inter-service communication

---

## 📊 Deployment Strategy (Option C Alignment)

### **Infrastructure Components**

| Component | Managed Service | Platform Integration |
|-----------|----------------|----------------------|
| **Redis** | Upstash / MemoryStore | Use existing Redis adapter |
| **ArangoDB** | ArangoDB Oasis | Use existing ArangoDB adapter |
| **Supabase** | Supabase Cloud | Use existing Supabase adapter |
| **Meilisearch** | Meilisearch Cloud | Use existing Meilisearch adapter |
| **Telemetry** | Grafana Cloud (OTel/Tempo) | Use existing OpenTelemetry utilities |
| **LLM Ops** | Hugging Face / OpenAI / Anthropic | Use existing Agentic Foundation |
| **WAL Storage** | ArangoDB Oasis (via Knowledge Governance) | Data Steward WAL module |

### **Deployment Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Execution Plane                            │
│  Cloud Run / GKE Deployments                                 │
│  - Smart City Services (Data Steward with WAL)              │
│  - Business Enablement Realms                                 │
│  - Insurance Use Case Services                               │
│  - Solution & Journey Orchestrators                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Control Plane                             │
│  GKE StatefulSets + Grafana Stack                            │
│  - DI Container                                              │
│  - Curator (Consul)                                          │
│  - OpenTelemetry Collector                                   │
│  - Tempo (traces)                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Plane                                 │
│  Managed Services (Option C)                                  │
│  - Supabase Cloud (Postgres + Auth)                          │
│  - ArangoDB Oasis (Graph DB + WAL Storage)                   │
│  - Upstash / MemoryStore (Redis)                            │
│  - Meilisearch Cloud (Search)                               │
│  - Grafana Cloud (Observability)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📅 Timeline & Milestones

### **Phase 1: MVP (4-6 Weeks)**

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 1-2 | Canonical Model v1 + WAL | Frozen schema, Canonical Model Service, Data Steward WAL module |
| 2-3 | Enhanced Schema Mapping | Canonical integration, mapping chains, WAL logging |
| 3-4 | Client Onboarding Kit | CLI tool, connectors, worksheets |
| 4-5 | Basic Routing Engine | Routing rules, policy routing, WAL logging |
| 5-6 | Solution/Journey Integration | Solution template, Saga Journey template, orchestrators |
| 6 | Integration & Testing | MVP test suite, end-to-end validation, WAL replay tests |

**Success Criteria:**
- ✅ Legacy data can be ingested and mapped to canonical model
- ✅ Basic routing rules can route policies to target systems
- ✅ CLI tool enables client onboarding
- ✅ Solution Composer orchestrates multi-phase migration
- ✅ Saga Journey provides automatic compensation
- ✅ WAL provides audit trail and replay capability
- ✅ All MVP tests passing

### **Phase 2: Production (8-12 Weeks)**

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 7-9 | Advanced Routing | Multi-system routing, state management, WAL logging |
| 9-11 | Wave Orchestration | Wave management, quality gates, Saga integration |
| 11-12 | Bi-Directional Flows | Dual-write, selective-write, sync, WAL logging |

**Success Criteria:**
- ✅ Wave-based migration orchestration working
- ✅ Quality gates enforced
- ✅ Bi-directional data flows operational
- ✅ WAL provides complete audit trail
- ✅ Production test suite passing

### **Phase 3: Enterprise (12-16 Weeks)**

| Week | Milestone | Deliverables |
|------|-----------|--------------|
| 13-14 | Enhanced Governance | Policy tracker, mapping versioning, WAL-powered audit |
| 15-16 | Operational Tooling | Dashboards, mapping editor, APIs, WAL replay interface |

**Success Criteria:**
- ✅ Policy tracker operational
- ✅ Mapping rule versioning working
- ✅ Operational dashboards deployed
- ✅ WAL replay interface operational
- ✅ Enterprise test suite passing

---

## 🔗 Dependencies & Risks

### **Dependencies**

1. **Platform Foundation** (✅ Ready)
   - Content Pillar file processing
   - Insights Pillar AI analysis
   - Operations Pillar workflow execution
   - Data Steward governance capabilities
   - Solution & Journey Realms (✅ Complete)
   - Saga Journey Orchestrator (✅ Complete)

2. **External Services** (⚠️ Need Configuration)
   - Managed database services (Supabase, ArangoDB Oasis)
   - Managed cache (Upstash/MemoryStore)
   - Managed search (Meilisearch Cloud)
   - Observability (Grafana Cloud)

3. **Client Requirements** (📋 TBD)
   - Legacy system access
   - Data dictionary documentation
   - Business rules definition
   - Target system specifications

### **Risks & Mitigations**

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Canonical model changes** | High | Medium | Freeze v1, plan v2 migration path |
| **Routing complexity** | Medium | High | Start simple, iterate based on feedback |
| **Data quality issues** | High | High | Robust quality gates, reject buckets |
| **Performance at scale** | Medium | Medium | Load testing, optimization, caching |
| **Client onboarding delays** | Medium | Medium | Comprehensive onboarding kit, templates |
| **Managed service limitations** | Low | Low | Adapter pattern allows swapping |
| **WAL performance impact** | Medium | Low | WAL writes are async, minimal overhead |
| **Saga compensation failures** | High | Low | WAL enables retry, idempotent handlers |

---

## ✅ Success Criteria

### **Phase 1 (MVP)**
- [ ] Legacy data ingestion working
- [ ] Canonical model mapping functional
- [ ] Basic routing rules operational
- [ ] CLI tool enables client onboarding
- [ ] Solution Composer orchestrates multi-phase solution
- [ ] Saga Journey provides automatic compensation
- [ ] WAL provides audit trail and replay capability
- [ ] MVP test suite passing (90%+ coverage)

### **Phase 2 (Production)**
- [ ] Wave-based migration orchestration working
- [ ] Quality gates enforced and tested
- [ ] Bi-directional data flows operational
- [ ] WAL provides complete audit trail
- [ ] Production test suite passing
- [ ] Performance benchmarks met

### **Phase 3 (Enterprise)**
- [ ] Policy tracker operational
- [ ] Mapping rule versioning working
- [ ] Operational dashboards deployed
- [ ] WAL replay interface operational
- [ ] Enterprise test suite passing
- [ ] Multi-tenant support validated

### **Overall Platform Readiness**
- [ ] All 3 CTO demo scenarios enhanced
- [ ] Insurance use case production-ready
- [ ] Option C deployment validated
- [ ] Client onboarding process documented
- [ ] Operational runbooks created
- [ ] WAL-powered audit trails operational

---

## 📚 Documentation Requirements

### **Technical Documentation**
- [ ] Canonical Policy Model v1 Specification
- [ ] Routing Rules Engine API Documentation
- [ ] Wave Orchestration Guide
- [ ] Saga Journey Integration Guide
- [ ] WAL Integration Guide (Data Steward)
- [ ] Solution Composer Integration Guide
- [ ] Client Onboarding Guide
- [ ] API Reference Documentation

### **Operational Documentation**
- [ ] Deployment Guide (Option C)
- [ ] Monitoring & Alerting Guide
- [ ] Troubleshooting Runbook
- [ ] Disaster Recovery Plan (with WAL replay)
- [ ] Performance Tuning Guide
- [ ] WAL Replay Procedures

### **Business Documentation**
- [ ] Insurance Use Case Overview
- [ ] Value Proposition Document
- [ ] Client Onboarding Checklist
- [ ] Migration Planning Guide
- [ ] ROI Calculator
- [ ] Compliance & Audit Trail Guide

---

## 🎯 Next Steps

1. **Immediate (Week 1)**
   - Review and approve this implementation plan
   - Set up project tracking (GitHub Issues/Projects)
   - Create Phase 1 branch and development environment
   - Begin Canonical Policy Model v1 design
   - Begin Data Steward WAL module design

2. **Short-term (Weeks 2-6)**
   - Execute Phase 1 MVP development
   - Weekly progress reviews
   - Continuous integration and testing
   - Client feedback incorporation

3. **Medium-term (Weeks 7-12)**
   - Execute Phase 2 production development
   - Performance testing and optimization
   - Option C deployment validation
   - Client pilot program

4. **Long-term (Weeks 13-16)**
   - Execute Phase 3 enterprise features
   - Full production deployment
   - Client onboarding and training
   - Continuous improvement

---

## 📞 Contact & Resources

**Platform Documentation:**
- [Platform README](../symphainy-platform/README.md)
- [Architecture Diagrams](../symphainy-platform/docs/architecture-diagrams.md)
- [CTO Demo Test Results](../../tests/CTO_DEMO_READINESS_REPORT.md)
- [Saga Journey Guide](../symphainy-platform/backend/journey/docs/SAGA_JOURNEY_ORCHESTRATOR.md)
- [Solution Realm Guide](../symphainy-platform/backend/solution/SOLUTION_REALM_COMPLETE.md)

**Related Documents:**
- [Original Insurance Use Case Plan](./INSURANCE_USE_CASE_STRATEGIC_IMPLEMENTATION_PLAN.md)
- [Netflix WAL Case Study](./writeaheadlogging.md)
- [Saga Pattern Documentation](./distributed_transaction_management_saga_choreography.md)
- [Hybrid Cloud Strategy (Option C)](./hybridcloudstrategy.md)
- [Data Mash Platform Analysis](../symphainy-platform/docs/CTO_Feedback/DATA_MASH_PLATFORM_ANALYSIS.md)

---

**Last Updated:** December 2024  
**Status:** Ready for Implementation  
**Version:** 2.0  
**Next Review:** After Phase 1 completion

