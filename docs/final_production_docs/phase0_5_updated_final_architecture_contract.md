# Phase 0.5: Updated Final Architecture Contract

**Date:** January 2025  
**Status:** ✅ COMPLETE - Authoritative Architecture Document (Updated)  
**Purpose:** Single source of truth for final architecture, incorporating all findings and decisions from Phase 0.1, 0.2, 0.3, and 0.4

---

## Executive Summary

This document is the **authoritative architecture contract** for the Symphainy Platform. It incorporates:
- Findings from Phase 0.1 Deep Dive Analysis
- Decisions from Phase 0.2 Communication Pattern Pressure Test
- Decisions from Phase 0.2 Traffic Cop/Post Office Boundaries
- Content Steward/Data Steward consolidation decision
- **Phase 0.4 Realm Analysis findings:**
  - Manager hierarchy pattern (Solution Manager bootstraps all realm managers)
  - Missing managers (Insights Manager, Content Manager required)
  - Delivery Manager archival
  - Data Solution Orchestrator refocused on correlation
  - Data correlation strategy (correlation_id as primary)
  - Smart City services as aggregation points
  - Automatic correlation injection pattern
  - Data mash semantic model requirements

**This document becomes law** - all subsequent work must align with this contract.

---

## 1. Architectural North Star

Symphainy is a **purpose-driven, data-centric, city-governed platform**.

- **Infrastructure exists first**
- **Foundations exist before behavior**
- **Smart City governs activation**
- **Purpose (Solutions) drives execution**
- **Data enters once, meaning propagates everywhere**
- **Data correlation enables platform-wide visibility**

Everything below enforces these truths.

---

## 2. Lifecycle Layers (Canonical)

```
┌─────────────────────────────────────────────┐
│ INFRASTRUCTURE (containers, networks, infra)│
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ UTILITIES (logging, config, DI, telemetry)  │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ FOUNDATIONS (Experience, Agentic, Data, etc)│
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ SMART CITY (City Manager, governance layer) │
│         (REALM with business logic)          │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│ REALMS (Solution → Journey → Insights →     │
│        Content)                              │
└─────────────────────────────────────────────┘
```

**Key Principles:**
- **Experience is a Foundation**, not a realm
- **Agentic is a Foundation**, not a realm
- **Smart City is a Realm** (with business logic, not just governance)
- **Realms are called top-down by purpose**, not bottom-up by data

---

## 3. City Manager Lifecycle Contract

The **City Manager** is the *only* component allowed to:
- Decide *what* activates
- Decide *when* it activates
- Decide *why* it activates

Nothing else bootstraps realms.

### 3.1 City Manager Responsibilities

| Responsibility        | Description                       |
| --------------------- | --------------------------------- |
| Lifecycle Governance  | Owns platform startup states      |
| Dependency Resolution | Ensures prerequisites exist       |
| Lazy Activation       | Activates realms only when needed |
| Health Enforcement    | Prevents traffic until ready      |
| Contract Enforcement  | Ensures realms obey interfaces    |
| Manager Hierarchy Bootstrap | Bootstraps Solution Manager, which bootstraps all realm managers |

**Note:** City Manager provides **lifecycle governance**, not business logic exclusion. Smart City is a realm with business logic.

### 3.2 City Manager States

```python
class CityManagerState(Enum):
    INFRA_WAIT = "infra_wait"
    UTILITIES_READY = "utilities_ready"
    FOUNDATIONS_READY = "foundations_ready"
    CITY_READY = "city_ready"
    PLATFORM_IDLE = "platform_idle"
    REALM_ACTIVE = "realm_active"
```

### 3.3 Manager Hierarchy Bootstrap Pattern

**Updated Pattern (Phase 0.4):**
```
City Manager
  ↓ bootstrap_manager_hierarchy()
  ↓ _bootstrap_solution_manager()
Solution Manager
  ↓ bootstraps ALL realm managers (as peers)
  ├─ Journey Manager
  ├─ Insights Manager
  └─ Content Manager
```

**Bootstrap Sequence:**
1. **City Manager** bootstraps **Solution Manager** (EAGER)
2. **Solution Manager** bootstraps **ALL realm managers** (EAGER):
   - **Journey Manager**
   - **Insights Manager** (to be created)
   - **Content Manager** (to be created)
3. **Delivery Manager** - **TO BE ARCHIVED** (or kept for very narrow purpose if enabling services exist)

**Rationale:**
- Solution realm may need to directly access any/all other realms
- Journey realm may need to directly access Insights/Content realms
- Cascading pattern (Solution → Journey → Delivery) doesn't work cleanly with new realm architecture
- All realm managers should be peers under Solution Manager

**Manager Hierarchy States:**
- `NOT_BOOTSTRAPPED` - Manager hierarchy not initialized
- `BOOTSTRAPPING` - Manager hierarchy bootstrapping in progress
- `OPERATIONAL` - Manager hierarchy fully bootstrapped

### 3.4 City Manager Interface

```python
class CityManager(Protocol):
    async def wait_for_infrastructure(self) -> None:
        """Block until all infrastructure dependencies are healthy"""
    
    async def initialize_utilities(self) -> None:
        """ConfigAdapter, DI container, logging, telemetry"""
    
    async def initialize_foundations(self) -> None:
        """Experience, Agentic, Data foundations"""
    
    async def start_city(self) -> None:
        """Smart City governance online"""
    
    async def bootstrap_manager_hierarchy(self) -> None:
        """Bootstrap Solution Manager, which bootstraps all realm managers"""
    
    async def activate_solution(self, solution_id: str) -> None:
        """Top-down activation entrypoint"""
    
    async def get_state(self) -> CityManagerState:
        """Current lifecycle state"""
```

**Critical rule:** Nothing outside Smart City may activate a realm directly.

---

## 4. Realm Activation Dependency Graph

**Execution flows opposite of data flow.**

### 4.1 Canonical Realm Roles

| Realm    | Role                                    |
| -------- | --------------------------------------- |
| Solution | WHY (business outcome)                  |
| Journey  | HOW (workflow orchestration)            |
| Insights | ANALYSIS (quality, semantics, meaning)  |
| Content  | DATA FRONT DOOR (data mash entry point) |

### 4.2 Dependency Graph (Activation)

```
Solution
   ↓
Journey
   ↓
Insights
   ↓
Content
```

**Interpretation:**
- A **Solution** determines *why* anything runs
- A **Journey** determines *how* it runs
- **Insights** determines *what meaning exists*
- **Content** supplies raw data (once, at the door)

### 4.3 Dependency Rules (Non-Negotiable)

1. Content is **never activated directly**
2. Insights activates Content **only if needed**
3. Journeys activate Insights **only if needed**
4. Solutions are the **only public entrypoint**

This preserves the **Data Mash vision**: "Clients leave their data at the door; meaning propagates."

---

## 5. Manager Hierarchy (Updated - Phase 0.4)

### 5.1 Manager Inventory

| Manager | Status | Location | Purpose |
|---------|--------|----------|---------|
| **Solution Manager** | ✅ Implemented | `backend/solution/services/solution_manager/` | Manages Solution Orchestrators |
| **Journey Manager** | ✅ Implemented | `backend/journey/services/journey_manager/` | Manages Journey Orchestrators |
| **Insights Manager** | ❌ **REQUIRED** | `backend/insights/services/insights_manager/` (to be created) | Manages Insights Services |
| **Content Manager** | ❌ **REQUIRED** | `backend/content/services/content_manager/` (to be created) | Manages Content Services |
| **Delivery Manager** | ⚠️ **TO BE ARCHIVED** | `backend/business_enablement/delivery_manager/` | Manages enabling services (may not be needed) |

### 5.2 Manager Pattern

**All realm managers follow the same pattern:**
- Extend `ManagerServiceBase`
- Discover and manage realm services/orchestrators
- Coordinate cross-service operations
- Track realm-level state and progress
- Provide realm-level analytics

**Insights Manager and Content Manager must be created following this pattern.**

### 5.3 Lazy Instantiation Pattern

**Current Pattern:**
- **Managers:** EAGER (bootstrapped by City Manager/Solution Manager)
- **Orchestrators:** LAZY (loaded on-demand by managers)
- **Services:** LAZY (loaded on-demand by orchestrators)
- **Smart City Services:** LAZY (loaded on-demand by City Manager)

**Key Principle:** Only managers are EAGER. Everything else is LAZY.

---

## 6. Smart City Realm (Critical Clarification)

**Smart City IS a realm** and **DOES NOT have business logic exclusion**.

### 6.1 Smart City Role

**WHAT (Smart City Realm):** Orchestrate platform infrastructure capabilities and provide business functionality

**Key Principle:** Smart City provides **critical business functionality** and elevates platform infrastructure capabilities to **first-class citizens**.

### 6.2 Smart City Services (8 Services)

| Service | Business Functionality | Platform Capability Elevated |
|---------|----------------------|----------------------------|
| **City Manager** | Platform lifecycle governance, manager hierarchy orchestration, realm activation | Lifecycle Management |
| **Post Office** | Strategic communication orchestration, messaging, event distribution, WebSocket Gateway | Messaging & Routing |
| **Traffic Cop** | API Gateway routing, session management, state synchronization, rate limiting | Session & State, API Gateway |
| **Security Guard** | Zero-trust security, multi-tenancy, authentication/authorization, audit logging | Security |
| **Librarian** | Knowledge discovery, metadata governance, semantic search, content organization | Knowledge |
| **Nurse** | Health monitoring, telemetry collection, alert management, distributed tracing | Telemetry & Tracing |
| **Data Steward** | Data lifecycle management, file lifecycle, data governance, quality compliance | Data Management |
| **Conductor** | Workflow orchestration, task management, BPMN processing, cross-service coordination | Workflow & Orchestration |

**Note:** Content Steward has been **consolidated into Data Steward** (to be archived).

### 6.3 Smart City Services as Data Aggregation Points (Phase 0.4)

**Smart City services serve as aggregation points for Data Solution Orchestrator:**

| Smart City Service | Data Type | Aggregation Role |
|-------------------|-----------|-----------------|
| **Data Steward** | Client Data | Aggregates client data operations, lineage, correlation |
| **Librarian** | Semantic Data | Aggregates semantic data (embeddings, metadata, knowledge graphs) |
| **Nurse** | Platform Data | Aggregates platform data (telemetry, events, health metrics) |

**Data Solution Orchestrator coordinates all three via these aggregation points.**

### 6.4 Smart City Business Logic

**All Smart City services have business logic:**
- Security Guard: Security policies, multi-tenancy rules
- Traffic Cop: Routing decisions, load balancing strategies
- Post Office: Message routing, event distribution logic
- Librarian: Knowledge discovery algorithms, search strategies
- Nurse: Health monitoring rules, alert thresholds
- Data Steward: Data governance policies, quality rules
- Conductor: Workflow orchestration patterns
- City Manager: Lifecycle governance, activation rules

**This is correct and expected** - Smart City is a realm with business logic.

### 6.5 Smart City Privilege

**Smart City services have direct abstraction access** (no Platform Gateway):
- Access Public Works abstractions directly
- Avoids circular dependencies
- Smart City privilege is architectural, not just convenience

**Other realms access Smart City capabilities via:**
- Post Office SOA APIs (for messaging/events/WebSocket)
- Platform Gateway (for other Smart City capabilities)
- Direct access only for Smart City services

---

## 7. Solution Realm

### 7.1 Solution Realm Architecture

**WHAT:** Solution realm orchestrates complete, multi-journey solutions by composing Journey services.

**Purpose:** Business outcomes in "pillar" terms - entry point for all platform operations.

**Key Services:**
1. **Solution Composer Service** - Designs and executes multi-phase solutions
2. **Solution Analytics Service** - Measures solution success across journeys
3. **Solution Deployment Manager Service** - Manages solution deployment lifecycle

**Solution Orchestrators:**
- **DataSolutionOrchestratorService** - Entry point for data correlation (NOT operations)
- **InsightsSolutionOrchestratorService** - Entry point for insights operations
- **OperationsSolutionOrchestratorService** - Entry point for operations
- **BusinessOutcomesSolutionOrchestratorService** - Entry point for business outcomes

### 7.2 Solution Realm Pattern (Reason-Forward)

**Key Principle:** Everything starts with a Solution (business outcome).

**Flow:**
```
User Request
  ↓
Solution Orchestrator (Solution Realm)
  ├─ Orchestrates Platform Correlation:
  │  ├─ Security Guard (auth & tenant validation)
  │  ├─ Traffic Cop (session/state management)
  │  ├─ Conductor (workflow orchestration)
  │  ├─ Post Office (events & messaging)
  │  └─ Nurse (telemetry & observability)
  │
  └─ Delegates Operations:
     ↓
     Journey Orchestrator (Journey Realm)
```

### 7.3 Data Solution Orchestrator (Updated - Phase 0.4)

**Location:** `backend/solution/services/data_solution_orchestrator_service/`

**Purpose:** **Data Correlation Orchestrator** (NOT data operations orchestrator)
- Focuses on **data correlation** across client, semantic, and platform data
- Provides correlation services that data "owners" can call without circular references
- Orchestrates platform correlation (correlation_id, workflow_id, lineage, telemetry)

**Key Principle:** Data Solution Orchestrator does NOT perform data operations. It provides correlation services.

**Key Methods:**
- `correlate_client_data()` - Correlates client data via Data Steward aggregation point
- `correlate_semantic_data()` - Correlates semantic data via Librarian aggregation point
- `correlate_platform_data()` - Correlates platform data via Nurse aggregation point
- `get_correlated_data_mash()` - Provides virtual data composition layer access
- `track_data_lineage()` - Tracks data lineage across all data types
- `register_data_operation()` - Registers data operation for correlation (called automatically)

**Data Correlation Flow:**
```
ContentJourneyOrchestrator (performs data operations)
  ↓ calls register_data_operation() automatically (via middleware)
DataSolutionOrchestrator (provides correlation services)
  ↓ aggregates via Smart City services:
  ├─ Data Steward (client data)
  ├─ Librarian (semantic data)
  └─ Nurse (platform data)
  ↓ returns correlation_id and lineage
ContentJourneyOrchestrator (continues with correlated data)
```

**Rationale:**
- Prevents circular references (ContentJourneyOrchestrator can call DataSolutionOrchestrator for correlation without DataSolutionOrchestrator trying to call ContentJourneyOrchestrator)
- Data "owners" (Content, Insights realms) can call Data Solution Orchestrator for correlation
- Data Solution Orchestrator focuses on correlation, not operations
- Uses Smart City services as aggregation points (no need for separate PlatformDataSolutionOrchestrator or SemanticDataSolutionOrchestrator)

### 7.4 Automatic Correlation Injection (Phase 0.4)

**Pattern:** Automatic correlation via middleware/interceptor pattern

**Implementation:**
- Data Solution Orchestrator provides correlation middleware/interceptor
- All data operations automatically call `register_data_operation()` via base class/mixin
- Correlation happens transparently without explicit calls

**Alternative Patterns:**
- **Required Interface/Contract** - Base classes enforce correlation registration
- **Smart City Service Integration** - Data Steward, Librarian, Nurse automatically call Data Solution Orchestrator

**Critical Requirement:** All data sources MUST automatically call Data Solution Orchestrator for correlation.

---

## 8. Journey Realm

### 8.1 Journey Realm Architecture

**WHAT:** Journey realm orchestrates multi-step user journeys by composing Experience services.

**Purpose:** Operations in "pillar" terms - defines workflows and user journeys (how capabilities are consumed).

**Key Services:**
1. **Journey Orchestrator Service** - Designs and executes multi-step journeys
2. **Journey Analytics Service** - Measures journey success and optimization
3. **Journey Milestone Tracker Service** - Tracks user progress through journeys

**Journey Orchestrators:**
- **ContentJourneyOrchestrator** - Orchestrates content operations
- **InsightsJourneyOrchestrator** - Orchestrates insights operations
- **OperationsJourneyOrchestrator** - Orchestrates operations
- **User Journey Orchestrators** - Session, Structured, MVP

### 8.2 Journey Manager

**Location:** `backend/journey/services/journey_manager/`

**Purpose:** Manages Journey Orchestrators and coordinates journey-level operations.

**Key Responsibilities:**
- Discovers and manages Journey Orchestrators
- Coordinates cross-orchestrator operations
- Tracks journey-level state and progress
- Provides journey-level analytics

---

## 9. Insights Realm

### 9.1 Insights Realm Architecture

**WHAT:** Insights realm analyzes data and provides semantic meaning and quality analysis.

**Purpose:** ANALYSIS (quality, semantics, meaning) - consumes Content Realm's semantic substrate.

**Key Services:**
1. **Data Analyzer Service** - Provides EDA tools for agents
2. **Visualization Engine Service** - Generates charts and visualizations
3. **Data Mapping Agent** - Maps unstructured to structured data
4. **Field Extraction Service** - Extracts fields from unstructured data
5. **Data Quality Validation Service** - Validates data quality (**Note:** Moved from Content realm/pillar)
6. **Data Transformation Service** - Transforms data between formats
7. **Data Quality Section/Capability** - Data quality analysis and validation (newly added from Content realm)

### 9.2 Insights Realm Data Flow

**Consumes:**
- **Client Data** - Files, parsed data from Content Realm
- **Semantic Data** - Embeddings, metadata from Content Realm (via data mash)
- **Platform Data** - correlation_id, lineage from Data Steward

**Generates:**
- **Analysis Results** - EDA, quality checks, anomaly detection
- **Mapping Rules** - Field mappings, schema alignments
- **Visualizations** - Charts, graphs, dashboards
- **Insights** - Business recommendations, actionable insights

### 9.3 Insights Manager (Required - Phase 0.4)

**Location:** `backend/insights/services/insights_manager/` (to be created)

**Purpose:** Manages Insights Services and coordinates insights-level operations.

**Key Responsibilities:**
- Discovers and manages Insights Services
- Coordinates cross-service operations
- Tracks insights-level state and progress
- Provides insights-level analytics

**Status:** **REQUIRED** - Must be created following same pattern as Solution/Journey Managers.

---

## 10. Content Realm

### 10.1 Content Realm Architecture

**WHAT:** Content realm serves as data front door and handles data mash entry point.

**Purpose:** DATA FRONT DOOR (data mash entry point) - clients "leave their data at the door."

**Key Services:**
1. **FileParserService** - Parses files into structured data
2. **DataSteward** - Stores files and tracks data lineage (Smart City, not Content realm)
3. **Semantic Layer Services** - Creates embeddings and semantic metadata

**Note:** Content Steward has been consolidated into Data Steward (to be archived).

### 10.2 Content Realm Data Flow

**Ingress:**
```
Client File Upload
  ↓
ContentJourneyOrchestrator (Journey Realm)
  ↓
FileParserService (Content Realm)
  ↓
Data Steward (Smart City) - Stores files
  ↓
Semantic Layer Services (Content Realm) - Creates embeddings
  ↓ creates data mash semantic data model
  ↓ stores in vector database
Data Mash Virtual Data Composition Layer
  ↓ accessible by
All Realms
```

**Key Principle:** Content Realm is the **only** entry point for client data. No other realm ingests raw client data directly.

### 10.3 Data Mash Semantic Data Model (Critical - Phase 0.4)

**Critical Requirement:**
- **Embeddings MUST create the data mash virtual data composition layer / semantic data model**
- **All realms MUST be able to access this semantic data model**
- **Semantic data model is the foundation for data correlation across all data types**

**Semantic Layer Services:**
- Location: `backend/content/services/semantic_layer_services/` (if exists)
- Purpose: Creates embeddings and semantic metadata
- **Critical:** Creates the **data mash virtual data composition layer / semantic data model**
- Integrates with EmbeddingService (Business Enablement)
- Stores embeddings in vector database
- **Ensures embeddings create semantic data model that other realms can use/access**

### 10.4 Content Manager (Required - Phase 0.4)

**Location:** `backend/content/services/content_manager/` (to be created)

**Purpose:** Manages Content Services and coordinates content-level operations.

**Key Responsibilities:**
- Discovers and manages Content Services
- Coordinates cross-service operations
- Tracks content-level state and progress
- Provides content-level analytics

**Status:** **REQUIRED** - Must be created following same pattern as Solution/Journey Managers.

---

## 11. Data Strategy (Data as First-Class Citizen)

### 11.1 Data as First-Class Citizen Vision

**Key Principle:** Data operations are not "side effects" - they're primary operations.

**Three Types of Data:**
1. **Client Data** - Business data from client systems (files, records, transactions)
2. **Semantic Data** - Platform-generated semantic layer (embeddings, metadata, knowledge graphs)
3. **Platform Data** - Platform operational data (correlation_id, lineage, telemetry, events)

### 11.2 Data Correlation Strategy (Updated - Phase 0.4)

**Correlation Field Design:**

**Primary Correlation ID:**
- **correlation_id** (UUID) - Primary correlation identifier
  - Generated at Solution Orchestrator entry point
  - Propagated to all operations
  - More flexible than workflow_id (doesn't imply workflow exists)
  - Can be used for any operation, not just workflows

**Optional Correlation IDs:**
- **workflow_id** - Workflow-specific correlation ID (when operation is part of a defined workflow)
  - Generated by Conductor (Smart City) for workflow operations
  - Optional - not all operations have workflows

**Composite Correlation (Alternative):**
- `tenant_id` + `session_id` + `operation_id` (UUID)
- Provides multi-dimensional correlation
- Useful for operations without explicit workflow

**Recommendation:** Use **correlation_id** (UUID) as primary correlation field, with optional **workflow_id** for workflow-specific operations.

**Correlation IDs:**
- **correlation_id** - Primary correlation ID (UUID, generated at entry point)
- **workflow_id** - Optional workflow correlation ID (when operation is part of workflow)
- **user_id** - User identifier
- **session_id** - Session identifier
- **tenant_id** - Tenant identifier (multi-tenant isolation)
- **file_id** - File identifier
- **parsed_file_id** - Parsed file identifier
- **content_id** - Content identifier (semantic layer)

**Correlation Points:**
- **Solution Realm** - Generates/validates correlation_id at entry point
- **All Realms** - Tag all operations with correlation_id
- **Data Steward** - Tracks lineage and correlation relationships
- **Platform Correlation Services** - Track all operations with correlation IDs

### 11.3 Data Mash Concept

**Definition:** An AI-assisted, virtual data composition layer that dynamically stitches together data from different sources without physically moving it.

**Key Capabilities:**
- **Metadata Extraction** - Analyze source systems to build semantic models
- **Schema Alignment** - AI-powered mapping between source and target schemas
- **Virtual Composition** - Query across distributed sources without ETL
- **Execution Layer** - Materialize virtual pipelines when needed
- **Semantic Data Model** - Created by embeddings (Content Realm) and accessible by all realms

**Data Mash Creation (Embeddings):**
```
Content Realm (Semantic Layer Services)
  ↓ creates embeddings
  ↓ creates semantic data model
  ↓ stores in vector database
Data Mash Virtual Data Composition Layer
  ↓ accessible by
All Realms (Solution, Journey, Insights, Content)
```

**Data Mash Flow (Usage):**
```
DataSolutionOrchestrator (correlation services)
  ↓ aggregates via Smart City services:
  ├─ Data Steward (client data)
  ├─ Librarian (semantic data)
  └─ Nurse (platform data)
  ↓ provides correlation
ContentJourneyOrchestrator (data operations)
  ↓ composes data mash:
  ├─ Client Data: DataSteward.get_file()
  ├─ Semantic Data: semantic_data.get_embeddings() (from data mash)
  └─ Platform Data: DataSteward.track_data_lineage()
  ↓ generates
Correlated Results
```

**Critical Requirements:**
- **Embeddings MUST create the data mash virtual data composition layer / semantic data model**
- **All realms MUST be able to access this semantic data model**
- **Semantic data model is the foundation for data correlation across all data types**

### 11.4 Data Solution Orchestrator Aggregation Points (Phase 0.4)

**Architecture:**
```
DataSolutionOrchestrator (Correlation Orchestrator)
  ↓ aggregates via
  ├─ Data Steward (Smart City) - Client Data Aggregation Point
  │  └─ Tracks client data operations, lineage, correlation
  │
  ├─ Librarian (Smart City) - Semantic Data Aggregation Point
  │  └─ Tracks semantic data (embeddings, metadata, knowledge graphs)
  │
  └─ Nurse (Smart City) - Platform Data Aggregation Point
     └─ Tracks platform data (telemetry, events, health metrics)
```

**Benefits:**
- **No Duplication** - Don't need separate PlatformDataSolutionOrchestrator or SemanticDataSolutionOrchestrator
- **Leverages Existing Services** - Smart City services already handle these data types
- **Single Correlation Point** - Data Solution Orchestrator coordinates all three via Smart City services
- **Clear Ownership** - Each Smart City service owns its data type aggregation

**Data Solution Orchestrator Methods:**
- `correlate_client_data()` - Uses Data Steward as aggregation point
- `correlate_semantic_data()` - Uses Librarian as aggregation point
- `correlate_platform_data()` - Uses Nurse as aggregation point
- `get_correlated_data_mash()` - Composes all three via their aggregation points

### 11.5 Ensuring All Data Sources Call Data Solution Orchestrator (Phase 0.4)

**Pattern 1: Automatic Correlation Injection (Recommended)**
- Data Solution Orchestrator provides correlation middleware/interceptor
- All data operations automatically call `register_data_operation()` via base class/mixin
- Correlation happens transparently without explicit calls

**Pattern 2: Required Interface/Contract**
- All data operations must implement correlation interface
- Base classes enforce correlation registration
- Compile-time/runtime checks ensure compliance

**Pattern 3: Smart City Service Integration**
- Data Steward (client data) automatically calls Data Solution Orchestrator
- Librarian (semantic data) automatically calls Data Solution Orchestrator
- Nurse (platform data) automatically calls Data Solution Orchestrator

**Critical Requirement:** All data sources MUST automatically call Data Solution Orchestrator for correlation.

### 11.6 Data Strategy Recommendations

**1. Unified Correlation Pattern:**
- All operations must include `correlation_id` (UUID, generated at entry point)
- All workflow operations may include optional `workflow_id`
- All data operations must tag data with correlation IDs
- All platform services must track correlation IDs
- All data sources must automatically call Data Solution Orchestrator for correlation (via middleware/interceptor pattern)

**2. Data Steward as Single Source of Truth:**
- Data Steward tracks all data lineage
- Data Steward stores correlation relationships
- Data Steward provides correlation queries

**3. Platform Correlation Services:**
- Security Guard tracks auth with correlation_id
- Traffic Cop tracks session with correlation_id
- Conductor tracks workflow with correlation_id (and optional workflow_id)
- Post Office tracks events with correlation_id
- Nurse tracks telemetry with correlation_id (and aggregates platform data for Data Solution Orchestrator)

**4. Data Solution Orchestrator Aggregation Points:**
- Data Steward aggregates client data for Data Solution Orchestrator
- Librarian aggregates semantic data for Data Solution Orchestrator
- Nurse aggregates platform data for Data Solution Orchestrator
- Data Solution Orchestrator composes all three into correlated data mash

---

## 12. Communication Pattern (Phase 0.2 Decision)

**Decision:** ✅ **Smart City Roles (Traffic Cop + Post Office)** manage communications

### 12.1 Architecture

```
Smart City Realm
  ├── Post Office Role (WHAT: Orchestrate messaging & event distribution)
  │   ├── Messaging Service (HOW)
  │   ├── Event Distribution Service (HOW)
  │   └── WebSocket Gateway Service (HOW)
  │
  └── Traffic Cop Role (WHAT: Orchestrate session & routing)
      ├── Session Management Service (HOW)
      ├── API Gateway Routing Service (HOW)
      └── State Synchronization Service (HOW)
       ↓
All Realms (via Post Office SOA APIs + Platform Gateway)
  - Smart City: Direct access (no Platform Gateway)
  - Other Realms: Via Platform Gateway → Post Office SOA APIs
```

### 12.2 Rationale

1. **Already implemented** - WebSocket Gateway is Post Office capability (Phase 1-2 complete)
2. **No circular dependencies** - Smart City roles have direct abstraction access
3. **Smart City privilege required** - Communication requires direct abstraction access
4. **SOA API pattern** - Other realms access via Post Office SOA APIs (correct pattern)
5. **Business logic** - Communication involves business logic (routing decisions, messaging)

### 12.3 Why Not Communication Foundation?

- Would create circular dependencies (Communication Foundation ↔ Smart City)
- Would require major refactoring (WebSocket Gateway already Post Office)
- Communication requires Smart City privilege (direct abstraction access)
- Communication involves business logic (belongs in Smart City roles)

---

## 13. Traffic Cop vs Post Office Boundaries (Phase 0.2 Decision)

**Decision:** ✅ **Keep API Gateway and WebSocket Gateway separate**

### 13.1 Traffic Cop: Transport Routing

**WHAT:** Orchestrate transport routing and session/state infrastructure

**Responsibilities:**
1. **API Gateway Routing** (Transport)
   - HTTP request routing
   - Load balancing
   - Rate limiting
   - Request/response transformation
   - **Pure transport** - routes HTTP requests to services

2. **Session Management** (Infrastructure)
   - Session lifecycle (create/get/update/destroy)
   - Session validation
   - **Infrastructure capability** - used by both HTTP and WebSocket

3. **State Synchronization** (Infrastructure)
   - Cross-service state sync
   - State management
   - **Infrastructure capability** - platform-wide state

4. **Traffic Analytics** (Observability)
   - HTTP traffic metrics
   - Request analytics
   - Performance monitoring

**Boundary Rule:** Traffic Cop handles **transport routing** (HTTP → services) and **infrastructure capabilities** (sessions, state) used by transport.

### 13.2 Post Office: Messaging Routing

**WHAT:** Orchestrate messaging and event distribution

**Responsibilities:**
1. **Messaging** (Logical Routing)
   - Send/get messages
   - Message routing (logical - channels, recipients)
   - Message delivery
   - **Logical routing** - messages → channels/recipients

2. **Event Distribution** (Logical Routing)
   - Publish/subscribe events
   - Event routing (logical - channels, event types)
   - Event-driven communication
   - **Logical routing** - events → channels/subscribers

3. **WebSocket Gateway** (Transport + Logical Routing)
   - Accept WebSocket connections (transport)
   - Validate sessions via Traffic Cop (uses session abstraction)
   - Route messages to Redis channels (logical routing)
   - Connection lifecycle management
   - **Both transport and logical routing** - WebSocket → channels → agents

4. **Orchestration** (Coordination)
   - Pillar coordination
   - Realm communication
   - Service discovery routing

**Boundary Rule:** Post Office handles **messaging routing** (channels, events, logical routing) and **WebSocket Gateway** (transport + logical routing together).

### 13.3 Key Distinctions

**Transport Routing (Traffic Cop):**
- Protocol: HTTP
- Pattern: Request → Service
- Routing Logic: Based on path, method, headers
- State: Stateless (request/response)
- Purpose: Route HTTP requests to appropriate service

**Messaging Routing (Post Office):**
- Protocol: WebSocket, Redis Pub/Sub, Events
- Pattern: Message → Channel → Agent/Service
- Routing Logic: Based on channel, intent, recipient
- State: Stateful (persistent connections, subscriptions)
- Purpose: Route messages/events to appropriate channels/agents

### 13.4 Why WebSocket Gateway is Post Office (Not Traffic Cop)

**WebSocket Gateway is NOT pure transport:**
1. **Logical Routing:** Routes messages to channels (guide, pillar:content, etc.) - this is messaging logic
2. **Channel-Based:** Uses channel routing (not service routing) - this is messaging pattern
3. **Message Format:** Parses message format (channel, intent, payload) - this is messaging concern
4. **Agent Communication:** Routes to agents via channels - this is messaging domain

**WebSocket Gateway IS transport + messaging:**
- **Transport:** Accepts WebSocket connections (transport layer)
- **Messaging:** Routes messages to channels (logical routing layer)
- **Both:** Needs both transport and messaging capabilities

**Therefore:** WebSocket Gateway belongs in Post Office (messaging domain), not Traffic Cop (transport domain).

---

## 14. Foundation Services

### 14.1 Foundation Inventory

| Foundation | Why Foundation | Business Logic | Access Pattern |
|------------|---------------|----------------|----------------|
| **Public Works** | Infrastructure swappability | No (pure infrastructure) | Via abstractions |
| **Curator** | All realms need pattern enforcement, registry | Yes (acceptable - all realms need) | Via DI Container |
| **Experience** | All realms need experience SDK | Yes (acceptable - all realms need) | Via SDK builders |
| **Agentic** | All realms need agentic SDK | Yes (acceptable - all realms need) | Via SDK components |
| **Platform Gateway** | All realms need abstraction access control | Yes (acceptable - all realms need) | Via Platform Gateway |

### 14.2 Foundation Principles

**Foundations exist because all realms need access:**
- Curator: Pattern enforcement, service discovery (all realms need)
- Experience: Frontend Gateway, Session Manager, User Experience SDK (all realms need)
- Agentic: Agent SDK, agent types, tool composition (all realms need)
- Platform Gateway: Realm abstraction access control (all realms need)

**Business logic in foundations is acceptable** when all realms need access to that business logic.

### 14.3 Public Works Foundation

**Primary Purpose:** Infrastructure swappability

**Key Principle:** Abstractions follow **HOW we would swap infrastructure**, even if not currently swappable (e.g., FastAPI, Pandas).

**5-Layer Architecture:**
1. **Layer 0:** Infrastructure Adapters (Raw Technology - Redis, Supabase, GCS, ArangoDB)
2. **Layer 1:** Infrastructure Abstractions (Business Logic - with injected adapters)
3. **Layer 2:** Composition Services (Orchestration)
4. **Layer 3:** Infrastructure Registries (Initialization & Discovery)
5. **Layer 4:** Foundation Service (Public Works Foundation Service)

**Swappable Abstractions:**
- Messaging (Redis → NATS/RabbitMQ)
- Event Management (Redis → NATS/Kafka)
- File Management (Supabase/GCS → S3/Azure)
- Session (Redis → Memcached/Database)

**Non-Swappable Infrastructure:**
- FastAPI, Pandas, asyncio, httpx → Used via **direct library injection** (correct pattern)

---

## 15. Agentic Forward Pattern

### 15.1 Agent Types

1. **Stateful Agents** - Full agent capabilities with conversation state
2. **Stateless Agents** - Simple, stateless operations (e.g., HF Inference Agent)

### 15.2 Stateless HF Inference Agent

**Purpose:** Wraps Hugging Face model endpoints as stateless agents

**Key Methods:**
- `infer_column_meaning()` - Infers semantic meaning of a column
- `generate_embedding()` - Generates embedding vector for text
- `calculate_semantic_similarity()` - Calculates semantic similarity
- `find_semantic_id_candidates()` - Finds candidate semantic IDs

**Agent Pattern:**
```
Other Agents (Column Meaning Agent, Semantic Matching Agent)
  ↓ (calls as MCP tool)
Stateless HF Inference Agent
  ↓ (calls HF endpoint)
HuggingFace Model Endpoint (private)
```

**Key Properties:**
- **Stateless:** Can be called by multiple agents concurrently
- **Wraps HF Endpoint:** Abstracts HF model API
- **Multi-Tenant Safe:** Ensures tenant isolation
- **Exposed as Tool:** Other agents call it via MCP tools

---

## 16. Frontend Showcase Integration (symphainy-frontend)

### 16.1 Architecture

- **Experience Foundation** - Provides SDK builders for connecting any frontend
- **Frontend Gateway Service** - Routes frontend requests to Solution Orchestrators
- **WebSocket Gateway** - Real-time bidirectional communication (Post Office)

### 16.2 Frontend Connection Pattern

```
symphainy-frontend (React)
  ↓ HTTP requests
Traefik (Edge Gateway)
  ↓
FastAPI App (main.py)
  ↓
FrontendGatewayService (Experience Foundation)
  ↓ routes to
Solution Orchestrators (Solution Realm)
  ↓
Journey Orchestrators (Journey Realm)
  ↓
Realm Services
```

### 16.3 WebSocket Connection Pattern

```
symphainy-frontend (React)
  ↓ WebSocket connection
Traefik (Edge Gateway - /ws route)
  ↓
FastAPI WebSocket Endpoint (/ws)
  ↓
Post Office WebSocket Gateway Service
  ↓ routes to
Redis Pub/Sub Channels
  ↓
Agent Instances
```

### 16.4 Frontend Integration Requirements

1. **Use Experience Foundation SDK** - Frontend should use Experience Foundation SDK builders
2. **Use PillarAPIHandlers** - Frontend should use PillarAPIHandlers for API calls
3. **Use WebSocket Gateway** - Frontend should use Post Office WebSocket Gateway for real-time communication
4. **Fix Authentication Flow** - Frontend should use proper auth flow (not localStorage bypass)
5. **Fix State Management** - Frontend should use unified state management (not multiple overlapping systems)

---

## 17. Architectural Decisions Summary

### 17.1 Smart City is a Realm

- **Decision:** Smart City is a realm with business logic, not just governance
- **Rationale:** Smart City provides critical business functionality and elevates platform capabilities to first-class citizens
- **Impact:** All Smart City services have business logic (correct and expected)

### 17.2 Communication Pattern

- **Decision:** Smart City roles (Traffic Cop + Post Office) manage communications
- **Rationale:** Already implemented, no circular dependencies, Smart City privilege required, business logic belongs in Smart City roles
- **Impact:** Other realms access via Post Office SOA APIs

### 17.3 Gateway Boundaries

- **Decision:** Keep API Gateway and WebSocket Gateway separate
- **Rationale:** API Gateway is pure transport (Traffic Cop), WebSocket Gateway is transport + messaging (Post Office)
- **Impact:** Clear separation of concerns, single responsibility

### 17.4 Content Steward Consolidation

- **Decision:** Content Steward to be archived, Data Steward is consolidated service
- **Rationale:** Eliminates duplication, Data Steward's broader scope encompasses Content Steward
- **Impact:** Need to verify Data Steward has all capabilities, migrate references

### 17.5 Manager Hierarchy (Phase 0.4)

- **Decision:** Solution Manager bootstraps ALL realm managers (Journey, Insights, Content) as peers
- **Rationale:** Solution realm may need direct access to any/all realms, cascading pattern doesn't work cleanly
- **Impact:** Need to create Insights Manager and Content Manager, archive Delivery Manager

### 17.6 Data Solution Orchestrator Focus (Phase 0.4)

- **Decision:** Data Solution Orchestrator focuses on correlation, not operations
- **Rationale:** Prevents circular references, data "owners" can call for correlation without operations
- **Impact:** Refactor Data Solution Orchestrator to correlation services only

### 17.7 Data Correlation Strategy (Phase 0.4)

- **Decision:** Use correlation_id (UUID) as primary correlation field, workflow_id optional
- **Rationale:** More flexible than workflow_id, doesn't force everything to have a workflow
- **Impact:** All operations must include correlation_id, workflow_id optional for workflow operations

### 17.8 Smart City Services as Aggregation Points (Phase 0.4)

- **Decision:** Use Data Steward, Librarian, Nurse as aggregation points for Data Solution Orchestrator
- **Rationale:** No need for separate PlatformDataSolutionOrchestrator or SemanticDataSolutionOrchestrator, leverages existing services
- **Impact:** Data Solution Orchestrator coordinates all three via Smart City services

### 17.9 Automatic Correlation Injection (Phase 0.4)

- **Decision:** Implement automatic correlation via middleware/interceptor pattern
- **Rationale:** Ensures all data sources call Data Solution Orchestrator for correlation without manual intervention
- **Impact:** All data operations must automatically register with Data Solution Orchestrator

### 17.10 Data Mash Semantic Model (Phase 0.4)

- **Decision:** Embeddings must create accessible semantic data model for all realms
- **Rationale:** Semantic data model is foundation for data correlation across all data types
- **Impact:** Content Realm semantic layer services must create accessible data mash semantic model

---

## 18. Success Criteria

### 18.1 Architecture Alignment

- ✅ All services follow final architecture vision
- ✅ Lifecycle layers are explicit and enforced
- ✅ City Manager owns lifecycle
- ✅ Realms follow activation dependency graph
- ✅ Smart City is realm with business logic
- ✅ Communication pattern is Smart City roles
- ✅ Gateway boundaries are clear
- ✅ Manager hierarchy follows peer pattern (Solution Manager bootstraps all realm managers)
- ✅ Data correlation uses correlation_id as primary
- ✅ Data Solution Orchestrator focuses on correlation only
- ✅ All data sources automatically call Data Solution Orchestrator

### 18.2 Anti-Pattern Elimination

- ✅ No parallel implementations of same concept
- ✅ Tests validate outcomes, not internal structure
- ✅ Transport logic separate from domain logic
- ✅ Config has single source of truth
- ✅ Abstractions are stable and clear
- ✅ No circular references in data operations
- ✅ All data sources correlated automatically

### 18.3 Code Quality

- ✅ No duplicate code
- ✅ No unreachable code
- ✅ No commented-out code
- ✅ Clear contracts everywhere
- ✅ Clear documentation

### 18.4 Production Readiness

- ✅ Deterministic startup
- ✅ Health checks at all layers
- ✅ Single WebSocket gateway
- ✅ Clear observability
- ✅ Scaling safety
- ✅ Data correlation across all data types

---

## 19. Implementation Guidelines

### 19.1 When Creating New Services

1. **Determine layer:** Infrastructure → Utilities → Foundations → Smart City → Realms
2. **Choose base class:** FoundationServiceBase, RealmServiceBase, SmartCityRoleBase, ManagerServiceBase
3. **Define protocol:** Create protocol that matches implementation (not vice versa)
4. **Access patterns:** Smart City direct access, other realms via Platform Gateway
5. **Business logic:** Allowed in Smart City and realms, allowed in foundations when all realms need access
6. **Correlation:** All operations must include correlation_id, automatically register with Data Solution Orchestrator

### 19.2 When Refactoring Services

1. **Preserve well-constructed services:** Rebuild/refactor, don't delete
2. **Update contracts:** Update protocols to match implementations
3. **Maintain boundaries:** Respect Traffic Cop (transport) vs Post Office (messaging) boundaries
4. **Preserve bootstrap patterns:** Don't change Security/Telemetry bootstrap without analysis
5. **Follow swappability:** Abstractions follow HOW to swap infrastructure
6. **Ensure correlation:** All data operations must include correlation_id and register with Data Solution Orchestrator

### 19.3 When Adding Communication

1. **HTTP requests:** Use Traffic Cop API Gateway
2. **WebSocket connections:** Use Post Office WebSocket Gateway
3. **Messaging:** Use Post Office messaging APIs
4. **Events:** Use Post Office event APIs
5. **Sessions:** Use Traffic Cop session APIs

### 19.4 When Creating Managers

1. **Follow same pattern:** All realm managers follow same pattern as Solution/Journey Managers
2. **Extend ManagerServiceBase:** Use proper base class
3. **Discover services:** Managers discover and manage realm services/orchestrators
4. **Coordinate operations:** Managers coordinate cross-service operations
5. **Track state:** Managers track realm-level state and progress

---

## 20. Required Actions (Phase 0.4)

### 20.1 Manager Hierarchy

1. **Update Solution Manager** - Bootstrap ALL realm managers (Journey, Insights, Content) as peers
2. **Create Insights Manager** - Create following same pattern as Solution/Journey Managers
3. **Create Content Manager** - Create following same pattern as Solution/Journey Managers
4. **Archive Delivery Manager** - Archive (or keep only if enabling services require manager coordination)

### 20.2 Data Correlation

1. **Refactor Data Solution Orchestrator** - Focus on correlation services only, not operations
2. **Implement Automatic Correlation** - Middleware/interceptor pattern for automatic correlation registration
3. **Update Correlation Field** - Use correlation_id (UUID) as primary, workflow_id optional
4. **Integrate Smart City Aggregation** - Use Data Steward, Librarian, Nurse as aggregation points

### 20.3 Data Mash

1. **Ensure Semantic Model Creation** - Embeddings must create accessible semantic data model
2. **Verify Access Patterns** - All realms must be able to access semantic data model
3. **Document Data Mash API** - Document how realms access data mash semantic model

### 20.4 Content Steward Consolidation

1. **Verify Data Steward Capabilities** - Ensure Data Steward has all Content Steward capabilities
2. **Update Data Steward** - Include all Content Steward methods
3. **Migrate References** - Update all references from Content Steward to Data Steward
4. **Archive Content Steward** - Move to archive with documentation

### 20.5 Insights Realm Data Quality

1. **Verify Data Quality Services** - Ensure Insights Realm has data quality section/capability
2. **Document Migration** - Document that data quality moved from Content realm/pillar
3. **Update Services** - Ensure all data quality services are in Insights Realm

---

## 21. Platform Startup Sequence

### 21.1 Startup Phases

**Location:** `symphainy-platform/main.py`

**Startup Sequence:**
1. **Phase 1:** Bootstrap Foundation (EAGER)
   - DI Container
   - Public Works Foundation
   - Curator Foundation
   - Agentic Foundation
   - Experience Foundation
   - Platform Gateway Foundation

2. **Phase 2:** Register Smart City Gateway (EAGER)
   - City Manager
   - Platform Gateway

3. **Phase 2.5:** Bootstrap Manager Hierarchy (EAGER)
   - City Manager bootstraps Solution Manager
   - Solution Manager bootstraps ALL realm managers (Journey, Insights, Content) as peers
   - **Note:** Delivery Manager to be archived

4. **Phase 3:** Lazy Realm Hydration (deferred)
   - Realms, Orchestrators, Services are all LAZY
   - Loaded on-demand when first accessed

5. **Phase 4:** Background Health Watchers (async tasks)
   - Telemetry, Event Bus Heartbeats, Task Queue Watcher, Security Sentinel

6. **Phase 5:** Curator Auto-Discovery (continuous)
   - Periodic sync between service registry and running services

7. **Phase 6:** Validate Critical Services Health
   - Production readiness validation

### 21.2 Correlation ID at Startup

**Requirement:**
- Generate `platform_startup_correlation_id` (UUID) at startup
- Use `correlation_id` terminology (not `workflow_id`)
- Propagate `correlation_id` through all startup operations
- Store in `app_state["platform_startup_correlation_id"]`

### 21.3 Startup Alignment

**Critical Requirements:**
- ✅ Foundation bootstrap (Phase 1) - Must complete before Smart City
- ✅ Smart City Gateway (Phase 2) - Must complete before Manager Hierarchy
- ✅ Manager Hierarchy (Phase 2.5) - Solution Manager bootstraps ALL realm managers
- ✅ Lazy hydration (Phase 3) - No eager initialization of realms/services
- ✅ Background watchers (Phase 4) - Async tasks for health monitoring
- ✅ Curator auto-discovery (Phase 5) - Continuous service discovery

---

## 22. Gateway Routing Pattern

### 22.1 Gateway Architecture

**Components:**
1. **Universal Pillar Router** (`backend/api/universal_pillar_router.py`)
   - Routes `/api/v1/{pillar}/{path}` to Frontend Gateway Service
   - Thin HTTP adapter (~50 lines)
   - Converts HTTP → Dict format

2. **Frontend Gateway Service** (`foundations/experience_foundation/services/frontend_gateway_service/`)
   - Routes to Solution Orchestrators (entry points)
   - Discovers orchestrators via Curator
   - Handles request transformation and validation

3. **WebSocket Gateway Router** (`backend/api/websocket_gateway_router.py`)
   - Routes `/ws` to Post Office WebSocket Gateway Service
   - Single WebSocket endpoint (Post Office Gateway)

### 22.2 Routing Pattern (Required)

**Correct Pattern:**
```
Frontend Request
  ↓
Universal Pillar Router (HTTP adapter)
  ↓
Frontend Gateway Service
  ↓ routes to
Solution Orchestrators ✅ (entry point with platform correlation)
  ↓ delegates to
Journey Orchestrators
  ↓ composes
Realm Services
```

**Critical Requirement:**
- Frontend Gateway Service MUST route to Solution Orchestrators (not Journey Orchestrators directly)
- Solution Orchestrators are entry points with platform correlation
- Journey Orchestrators are operations orchestration (not entry points)

### 22.3 WebSocket Routing

**Pattern:**
```
Frontend WebSocket Connection
  ↓
WebSocket Gateway Router (/ws)
  ↓
Post Office WebSocket Gateway Service
  ↓ routes to
Redis Pub/Sub Channels
  ↓
Agent Instances
```

**Critical Requirement:**
- Single WebSocket endpoint (`/ws`) only
- Post Office owns WebSocket Gateway
- No other WebSocket endpoints

---

## 23. Container Lifecycle

### 23.1 Container Architecture

**Components:**
- Docker Compose files
- Dockerfiles
- Container orchestration
- Environment variable management

### 23.2 Container Requirements

**Key Requirements:**
- ✅ Infrastructure layer (containers, networks) exists first
- ✅ Environment variables properly managed
- ✅ Test mode support (TEST_MODE environment variable)
- ✅ GCP credential protection (critical env vars protected)
- ✅ Health checks align with City Manager lifecycle states
- ✅ Containers respect lazy hydration pattern

### 23.3 Container Startup Sequence

**Alignment with Architecture Contract:**
1. **Infrastructure Phase** - Containers, networks, infrastructure services
2. **Utilities Phase** - Config, DI, logging, telemetry
3. **Foundations Phase** - Experience, Agentic, Data foundations
4. **Smart City Phase** - City Manager, governance layer
5. **Realms Phase** - Solution, Journey, Insights, Content (lazy)

**Critical Requirement:**
- Containers must respect lazy hydration pattern
- Only managers are EAGER, everything else is LAZY
- Health checks must align with City Manager lifecycle states

---

## 24. CI/CD Alignment

### 24.1 CI/CD Requirements

**Key Requirements:**
- ✅ Tests validate outcomes, not internal structure (per architecture contract)
- ✅ Build process respects architecture layers
- ✅ Deployment process aligns with lifecycle layers
- ✅ CI/CD workflows comply with architecture contract

### 24.2 Testing Patterns

**Key Requirements (Per Architecture Contract Section 18.2):**
- ✅ Tests validate outcomes, not internal structure
- ✅ No tests that validate internal architecture details
- ✅ Tests focus on business outcomes
- ✅ Outcome-based validation pattern

**Anti-Patterns to Avoid:**
- ❌ Tests that validate internal structure
- ❌ Tests that check architecture details
- ❌ Tests that enforce implementation details

---

## 25. Next Steps

This contract is now **law** for all subsequent work:

1. **Phase 0.6:** Review platform infrastructure (startup, gateways, containers, CI/CD, testing)
2. **Phase 0.7:** Audit & Catalog - Classify all code against this contract
3. **Phase 1-7:** Cleanup & Refactoring - Align all code with this contract

---

**Document Status:** ✅ COMPLETE - Authoritative Architecture Contract (Updated)  
**Last Updated:** January 2025  
**This document is LAW** - all subsequent work must align with this contract.

