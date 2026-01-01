# Phase 0: DIL Foundation Setup
## Establishing Data Intelligence Layer Foundation

**Date:** January 2025  
**Status:** 🎯 **READY FOR IMPLEMENTATION**  
**Duration:** 2-3 weeks  
**Based on:** DIL_HOLISTIC_ROADMAP.md

---

## Executive Summary

Phase 0 establishes the Data Intelligence Layer (DIL) as a new foundation in the platform architecture. DIL consolidates orchestration, data runtime, semantic layer, agent fabric, PII patterns, and observability into a unified foundation that sits between Smart City Foundation and Public Works Foundation.

**Key Principle:** Establish foundation structure and contracts first, implement capabilities incrementally in subsequent phases.

---

## Goals

1. **Create DIL Foundation Structure** - Folder structure, service boundaries, contracts
2. **Integrate with Existing Architecture** - Startup sequence, DI container, foundation registry
3. **Define DIL Capability Domains** - 6 domains with contracts (initially lightweight)
4. **Prepare for Data Steward Consolidation** - Integration hooks for Phase 0.1
5. **Set Foundation for Future Phases** - WAL/Saga, Data Mash, Semantic Layer, etc.

---

## DIL Foundation Architecture

### Foundation Structure

```
foundations/
└── data_intelligence_foundation/
    ├── __init__.py
    ├── data_intelligence_foundation_service.py  # Main foundation service
    ├── protocols/
    │   ├── dil_foundation_protocol.py
    │   ├── dil_orchestration_protocol.py
    │   ├── dil_data_runtime_protocol.py
    │   ├── dil_semantic_layer_protocol.py
    │   ├── dil_agent_fabric_protocol.py
    │   ├── dil_pii_protocol.py
    │   └── dil_observability_protocol.py
    ├── capability_domains/
    │   ├── __init__.py
    │   ├── orchestration/
    │   │   ├── __init__.py
    │   │   ├── dil_orchestration_service.py  # Phase 1 implementation
    │   │   └── contracts.py  # WAL/Saga contracts
    │   ├── data_runtime/
    │   │   ├── __init__.py
    │   │   ├── dil_data_runtime_service.py  # Phase 2 implementation
    │   │   └── contracts.py  # Data Mash contracts
    │   ├── semantic_layer/
    │   │   ├── __init__.py
    │   │   ├── dil_semantic_layer_service.py  # Phase 3 implementation
    │   │   └── contracts.py  # Semantic layer contracts
    │   ├── agent_fabric/
    │   │   ├── __init__.py
    │   │   ├── dil_agent_fabric_service.py  # Phase 4 implementation
    │   │   └── contracts.py  # Agent fabric contracts
    │   ├── pii_deidentification/
    │   │   ├── __init__.py
    │   │   ├── dil_pii_service.py  # Phase 5 implementation
    │   │   └── contracts.py  # PII contracts
    │   └── observability/
    │       ├── __init__.py
    │       ├── dil_observability_service.py  # Phase 6 implementation
    │       └── contracts.py  # Observability contracts
    └── README.md
```

---

## Step 1: Create DIL Foundation Service

### 1.1: Foundation Service Structure

**File:** `foundations/data_intelligence_foundation/data_intelligence_foundation_service.py`

**Purpose:** Main DIL foundation service that initializes and coordinates all DIL capability domains.

**Implementation:**
```python
#!/usr/bin/env python3
"""
Data Intelligence Layer (DIL) Foundation Service

Consolidates orchestration, data runtime, semantic layer, agent fabric,
PII patterns, and observability into a unified foundation.

WHAT (Foundation): I provide data intelligence capabilities across all realms
HOW (Service): I coordinate DIL capability domains and integrate with existing foundations
"""

from typing import Dict, Any, Optional
from datetime import datetime

from bases.foundation_service_base import FoundationServiceBase
from foundations.data_intelligence_foundation.protocols.dil_foundation_protocol import DILFoundationProtocol

class DataIntelligenceFoundationService(FoundationServiceBase, DILFoundationProtocol):
    """
    Data Intelligence Layer Foundation Service
    
    Coordinates 6 capability domains:
    1. Orchestration (WAL/Saga) - Phase 1
    2. Data Runtime & Transport (Data Mash) - Phase 2
    3. Semantic Layer - Phase 3
    4. Agent Fabric - Phase 4
    5. PII & De-identification - Phase 5
    6. Observability & Telemetry - Phase 6
    """
    
    def __init__(self, di_container: Any, 
                 public_works_foundation: Any = None,
                 curator_foundation: Any = None,
                 agentic_foundation: Any = None):
        """Initialize DIL Foundation Service."""
        super().__init__(
            service_name="DataIntelligenceFoundationService",
            di_container=di_container
        )
        
        # Foundation dependencies
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        self.agentic_foundation = agentic_foundation
        
        # DIL capability domains (initialized in initialize())
        self.orchestration_service = None  # Phase 1
        self.data_runtime_service = None  # Phase 2
        self.semantic_layer_service = None  # Phase 3
        self.agent_fabric_service = None  # Phase 4
        self.pii_service = None  # Phase 5
        self.observability_service = None  # Phase 6
        
        # Service state
        self.is_initialized = False
        self.capability_domains_status = {}
        
        self.logger.info("🏗️ Data Intelligence Layer Foundation Service initialized")
    
    async def initialize(self) -> bool:
        """Initialize DIL Foundation Service and all capability domains."""
        try:
            self.logger.info("🚀 Initializing Data Intelligence Layer Foundation...")
            
            # Initialize capability domains (initially lightweight)
            await self._initialize_capability_domains()
            
            # Register with Curator Foundation
            if self.curator_foundation:
                await self._register_with_curator()
            
            self.is_initialized = True
            self.logger.info("✅ Data Intelligence Layer Foundation initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize DIL Foundation: {e}")
            return False
    
    async def _initialize_capability_domains(self):
        """Initialize all DIL capability domains (initially lightweight)."""
        # Phase 0: Create domain services with contracts only
        # Phase 1-6: Implement capabilities incrementally
        
        from foundations.data_intelligence_foundation.capability_domains.orchestration.dil_orchestration_service import DILOrchestrationService
        from foundations.data_intelligence_foundation.capability_domains.data_runtime.dil_data_runtime_service import DILDataRuntimeService
        from foundations.data_intelligence_foundation.capability_domains.semantic_layer.dil_semantic_layer_service import DILSemanticLayerService
        from foundations.data_intelligence_foundation.capability_domains.agent_fabric.dil_agent_fabric_service import DILAgentFabricService
        from foundations.data_intelligence_foundation.capability_domains.pii_deidentification.dil_pii_service import DILPIIService
        from foundations.data_intelligence_foundation.capability_domains.observability.dil_observability_service import DILObservabilityService
        
        # Initialize orchestration (Phase 1 - contracts only for now)
        self.orchestration_service = DILOrchestrationService(
            di_container=self.di_container,
            public_works_foundation=self.public_works_foundation
        )
        await self.orchestration_service.initialize()
        self.capability_domains_status["orchestration"] = "initialized"
        
        # Initialize data runtime (Phase 2 - contracts only for now)
        self.data_runtime_service = DILDataRuntimeService(
            di_container=self.di_container,
            public_works_foundation=self.public_works_foundation
        )
        await self.data_runtime_service.initialize()
        self.capability_domains_status["data_runtime"] = "initialized"
        
        # Initialize semantic layer (Phase 3 - contracts only for now)
        self.semantic_layer_service = DILSemanticLayerService(
            di_container=self.di_container,
            public_works_foundation=self.public_works_foundation
        )
        await self.semantic_layer_service.initialize()
        self.capability_domains_status["semantic_layer"] = "initialized"
        
        # Initialize agent fabric (Phase 4 - contracts only for now)
        self.agent_fabric_service = DILAgentFabricService(
            di_container=self.di_container,
            agentic_foundation=self.agentic_foundation
        )
        await self.agent_fabric_service.initialize()
        self.capability_domains_status["agent_fabric"] = "initialized"
        
        # Initialize PII (Phase 5 - contracts only for now)
        self.pii_service = DILPIIService(
            di_container=self.di_container
        )
        await self.pii_service.initialize()
        self.capability_domains_status["pii"] = "initialized"
        
        # Initialize observability (Phase 6 - contracts only for now)
        self.observability_service = DILObservabilityService(
            di_container=self.di_container,
            public_works_foundation=self.public_works_foundation
        )
        await self.observability_service.initialize()
        self.capability_domains_status["observability"] = "initialized"
        
        self.logger.info(f"✅ All DIL capability domains initialized: {list(self.capability_domains_status.keys())}")
    
    async def _register_with_curator(self):
        """Register DIL Foundation with Curator Foundation."""
        if self.curator_foundation and hasattr(self.curator_foundation, 'capability_registry'):
            await self.curator_foundation.capability_registry.register_capability(
                capability_name="data_intelligence_layer",
                capability_type="foundation",
                service_instance=self,
                metadata={
                    "version": "1.0.0",
                    "capability_domains": list(self.capability_domains_status.keys()),
                    "status": "initialized"
                }
            )
            self.logger.info("✅ DIL Foundation registered with Curator")
```

---

## Step 2: Create DIL Protocols

### 2.1: DIL Foundation Protocol

**File:** `foundations/data_intelligence_foundation/protocols/dil_foundation_protocol.py`

**Purpose:** Protocol defining DIL Foundation interface.

**Implementation:**
```python
#!/usr/bin/env python3
"""
DIL Foundation Protocol

Defines the interface for Data Intelligence Layer Foundation Service.
"""

from typing import Protocol, Dict, Any, Optional

class DILFoundationProtocol(Protocol):
    """Protocol for DIL Foundation Service."""
    
    async def initialize(self) -> bool:
        """Initialize DIL Foundation and all capability domains."""
        ...
    
    async def get_orchestration_service(self) -> Any:
        """Get DIL-Orchestration service."""
        ...
    
    async def get_data_runtime_service(self) -> Any:
        """Get DIL-Data Runtime service."""
        ...
    
    async def get_semantic_layer_service(self) -> Any:
        """Get DIL-Semantic Layer service."""
        ...
    
    async def get_agent_fabric_service(self) -> Any:
        """Get DIL-Agent Fabric service."""
        ...
    
    async def get_pii_service(self) -> Any:
        """Get DIL-PII service."""
        ...
    
    async def get_observability_service(self) -> Any:
        """Get DIL-Observability service."""
        ...
    
    async def get_capability_domains_status(self) -> Dict[str, str]:
        """Get status of all capability domains."""
        ...
```

### 2.2: Capability Domain Protocols

Create protocols for each capability domain (orchestration, data_runtime, semantic_layer, agent_fabric, pii, observability) with contracts for future implementation.

---

## Step 3: Integrate DIL into Platform Startup

### 3.1: Update Platform Startup Sequence

**File:** `main.py` (or `platform_orchestrator.py`)

**Changes:**
1. Add DIL Foundation initialization after Curator, before Agentic
2. Register DIL Foundation in DI container
3. Pass dependencies (Public Works, Curator, Agentic) to DIL

**Implementation:**
```python
# In _initialize_foundation_infrastructure() method

# After Curator Foundation initialization
# ...

# Initialize Data Intelligence Layer Foundation (NEW)
from foundations.data_intelligence_foundation.data_intelligence_foundation_service import DataIntelligenceFoundationService

dil_foundation = DataIntelligenceFoundationService(
    di_container=di_container,
    public_works_foundation=public_works_foundation,
    curator_foundation=curator_foundation,
    agentic_foundation=None  # Will be set after Agentic Foundation initializes
)
await dil_foundation.initialize()
self.infrastructure_services["dil_foundation"] = dil_foundation
self.foundation_services["DataIntelligenceFoundationService"] = dil_foundation
di_container.service_registry["DataIntelligenceFoundationService"] = dil_foundation
self.logger.info("✅ Data Intelligence Layer Foundation initialized and registered")

# Initialize Agentic Foundation (existing)
# ...

# Update DIL Foundation with Agentic Foundation reference
if dil_foundation and agentic_foundation:
    dil_foundation.agentic_foundation = agentic_foundation
    await dil_foundation.agent_fabric_service.update_agentic_foundation(agentic_foundation)
```

---

## Step 4: Create Capability Domain Services (Lightweight)

### 4.1: DIL-Orchestration Service (Phase 1 Contract)

**File:** `foundations/data_intelligence_foundation/capability_domains/orchestration/dil_orchestration_service.py`

**Purpose:** Orchestration service with WAL/Saga contracts (implementation in Phase 1).

**Implementation:**
```python
#!/usr/bin/env python3
"""
DIL-Orchestration Service

Orchestration capabilities with WAL/Saga patterns.
Phase 0: Contracts only
Phase 1: WAL/Saga implementation
"""

from typing import Dict, Any, Optional
from foundations.data_intelligence_foundation.protocols.dil_orchestration_protocol import DILOrchestrationProtocol

class DILOrchestrationService(DILOrchestrationProtocol):
    """DIL-Orchestration Service (Phase 0: Contracts, Phase 1: Implementation)."""
    
    def __init__(self, di_container: Any, public_works_foundation: Any = None):
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        self.logger = di_container.get_logger("DILOrchestrationService")
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize DIL-Orchestration Service (Phase 0: Contracts only)."""
        self.logger.info("🏗️ DIL-Orchestration Service initialized (contracts only)")
        self.is_initialized = True
        return True
    
    # Phase 1: Implement these methods
    async def execute_with_wal(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute operation with WAL pattern (Phase 1)."""
        raise NotImplementedError("Phase 1: WAL pattern implementation")
    
    async def execute_with_saga(self, operations: list, compensations: list) -> Dict[str, Any]:
        """Execute operations with Saga pattern (Phase 1)."""
        raise NotImplementedError("Phase 1: Saga pattern implementation")
```

### 4.2: Other Capability Domain Services

Create similar lightweight services for:
- `DILDataRuntimeService` (Phase 2)
- `DILSemanticLayerService` (Phase 3)
- `DILAgentFabricService` (Phase 4)
- `DILPIIService` (Phase 5)
- `DILObservabilityService` (Phase 6)

---

## Step 5: Integration with Data Steward Consolidation

### 5.1: Prepare Integration Hooks

**Purpose:** Set up hooks for Data Steward consolidation (Phase 0.1 from original plan).

**Changes:**
1. Add DIL-Data Runtime hooks for Data Mash pipeline
2. Add DIL-Orchestration hooks for data operation orchestration
3. Add DIL-Observability hooks for data operation telemetry

**Integration Points:**
- Data Steward → DIL-Data Runtime (for Data Mash)
- Data Steward → DIL-Orchestration (for WAL/Saga in Phase 1)
- Data Steward → DIL-Observability (for telemetry in Phase 6)

---

## Step 6: Documentation and Contracts

### 6.1: DIL Foundation README

**File:** `foundations/data_intelligence_foundation/README.md`

**Content:**
- DIL Foundation overview
- Capability domains description
- Integration points
- Phase roadmap
- Contracts and protocols

### 6.2: DIL Spec v1

**File:** `docs/DIL_SPEC_V1.md`

**Content:**
- DIL architecture diagram
- Capability domain contracts
- Data contracts and dependencies
- Integration patterns

---

## Testing Checklist

### Phase 0 Testing

- [ ] DIL Foundation initializes successfully
- [ ] DIL Foundation appears in foundation registry
- [ ] All 6 capability domains initialize (contracts only)
- [ ] DIL Foundation registered with Curator
- [ ] Platform startup sequence includes DIL
- [ ] No breaking changes to existing functionality
- [ ] DIL Foundation accessible via DI container

---

## Success Criteria

### Phase 0 Complete When:

1. ✅ DIL Foundation structure created
2. ✅ DIL Foundation service operational
3. ✅ All 6 capability domains initialized (contracts)
4. ✅ DIL integrated into platform startup
5. ✅ DIL registered with Curator
6. ✅ Documentation complete (README, Spec v1)
7. ✅ Integration hooks prepared for Phase 0.1

---

## Next Steps

After Phase 0 completion:

1. **Proceed with Data Steward Consolidation** (Phase 0.1 from original plan)
   - Integrate with DIL-Data Runtime hooks
   - Prepare for Data Mash pipeline

2. **Begin Phase 1: DIL-Orchestration + WAL/Saga**
   - Implement WAL pattern
   - Implement Saga pattern
   - Migrate ContentAnalysisOrchestrator

3. **Continue with Phase 2: DIL-Data Runtime + Data Mash**
   - Implement Data Mash pipeline
   - Add schema inference
   - Add metadata lineage

---

## Conclusion

Phase 0 establishes the DIL Foundation structure and integrates it with the existing platform architecture. All capability domains are initialized with contracts only, enabling incremental implementation in subsequent phases. This foundation supports Data Steward consolidation and sets the stage for the full DIL vision.

**Key Deliverables:**
- DIL Foundation service structure
- 6 capability domain services (contracts)
- Platform startup integration
- Curator registration
- Documentation and contracts

**Duration:** 2-3 weeks  
**Risk Level:** Low (foundation structure only, no breaking changes)


