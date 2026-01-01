# WAL and Saga Integration Plan
## "Capability by Design, Optional by Policy" Integration into Solution → Journey → Realm Architecture

**Date:** January 2025  
**Status:** 📋 **INTEGRATION PLAN**  
**Pattern:** "Capability by Design, Optional by Policy" (inspired by "Secure by Design, Open by Policy")

---

## 🎯 Executive Summary

This plan integrates **WAL (Write Ahead Logging)** and **Saga Journey Orchestrator** into the new Solution → Journey → Realm architectural pattern using a lightweight, policy-driven approach.

**Key Principle:** Build WAL and Saga capabilities into the architecture, but make them optional and policy-driven to avoid complexity overload.

**Current State:**
- ✅ WAL implemented in Data Steward service (module)
- ✅ Saga Journey Orchestrator implemented as service
- ❌ Not integrated into Solution → Journey → Realm flows
- ❌ Not policy-driven (not optional)

**Target State:**
- ✅ WAL available to all data journey flows (optional via policy)
- ✅ Saga available to all solution/journey orchestrators (optional via policy)
- ✅ MVP solutions/journeys showcase the architecture
- ✅ Frontend vision demonstrated end-to-end

---

## 🏗️ Architecture Integration

### WAL Integration Pattern

**"Capability by Design":**
- WAL capability built into Solution Orchestrators
- Available to all data journey flows
- Automatic logging before critical operations

**"Optional by Policy":**
- Enable/disable via policy configuration
- Policy determines which operations to log
- Default: WAL available but not required

### Saga Integration Pattern

**"Capability by Design":**
- Saga capability built into Solution/Journey Orchestrators
- Available to all multi-step workflows
- Automatic compensation on failure

**"Optional by Policy":**
- Enable/disable via policy configuration
- Policy determines which workflows need Saga guarantees
- Default: Saga available but not required

---

## 📋 Implementation Plan

### Phase 1: WAL Integration into Data Journey Flows

#### Step 1.1: Add WAL Capability to DataSolutionOrchestrator

**Location:** `backend/solution/services/data_solution_orchestrator_service/data_solution_orchestrator_service.py`

**Changes:**
- Add WAL policy configuration
- Add `_write_to_wal()` helper method
- Integrate WAL logging into `orchestrate_data_ingest()`, `orchestrate_data_parse()`, etc.

**Implementation:**
```python
class DataSolutionOrchestratorService(RealmServiceBase):
    def __init__(self, ...):
        # WAL policy (capability by design, optional by policy)
        self.wal_policy = {
            "enable_wal": False,  # Default: disabled
            "log_operations": ["ingest", "parse", "embed", "expose"],
            "namespace": "data_solution"
        }
    
    async def _write_to_wal(
        self,
        operation: str,
        payload: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Write operation to WAL if enabled by policy.
        
        Pattern: "Capability by Design, Optional by Policy"
        """
        if not self.wal_policy.get("enable_wal", False):
            return None  # WAL disabled by policy
        
        if operation not in self.wal_policy.get("log_operations", []):
            return None  # Operation not in policy
        
        # Get Data Steward (WAL is a Data Steward capability)
        data_steward = await self.get_data_steward_api()
        if not data_steward:
            self.logger.warning("⚠️ Data Steward not available for WAL")
            return None
        
        # Write to WAL
        wal_result = await data_steward.write_to_log(
            namespace=self.wal_policy.get("namespace", "data_solution"),
            payload={
                "operation": operation,
                "correlation_id": user_context.get("workflow_id") if user_context else None,
                **payload
            },
            target=f"data_solution_{operation}",
            lifecycle={
                "retry_count": 3,
                "delay": 60,
                "ttl": 604800  # 7 days
            },
            user_context=user_context
        )
        
        if wal_result.get("success"):
            return wal_result.get("log_id")
        return None
    
    async def orchestrate_data_ingest(
        self,
        file_data: bytes,
        file_name: str,
        file_type: str,
        user_context: Optional[Dict[str, Any]] = None,
        wal_policy: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate data ingest with optional WAL logging.
        
        Pattern: "Capability by Design, Optional by Policy"
        """
        # Update WAL policy if provided
        if wal_policy:
            self.wal_policy.update(wal_policy)
        
        # Step 1: Write to WAL (if enabled)
        wal_log_id = await self._write_to_wal(
            operation="ingest",
            payload={
                "file_name": file_name,
                "file_type": file_type,
                "file_size": len(file_data)
            },
            user_context=user_context
        )
        
        # Step 2: Orchestrate platform correlation
        correlation_context = await self._orchestrate_platform_correlation(
            operation="data_ingest",
            user_context=user_context
        )
        
        # Step 3: Execute ingest (existing logic)
        result = await self.content_journey_orchestrator.handle_content_upload(
            file_data=file_data,
            filename=file_name,
            file_type=file_type,
            user_context=correlation_context
        )
        
        # Step 4: Update WAL status (if logged)
        if wal_log_id and result.get("success"):
            data_steward = await self.get_data_steward_api()
            if data_steward:
                await data_steward.write_ahead_logging_module.update_log_status(
                    log_id=wal_log_id,
                    status="completed",
                    result={"file_id": result.get("file_id")},
                    user_context=user_context
                )
        
        # Step 5: Record completion
        await self._record_platform_correlation_completion(
            operation="data_ingest",
            result=result,
            correlation_context=correlation_context
        )
        
        # Add WAL log_id to result if logged
        if wal_log_id:
            result["wal_log_id"] = wal_log_id
        
        return result
```

#### Step 1.2: Add WAL Capability to InsightsSolutionOrchestrator

**Similar pattern** - Add WAL logging to insights operations (analysis, mapping, visualization).

#### Step 1.3: Policy Configuration

**Location:** Configuration service or environment variables

**Default Policy:**
```python
wal_policy_default = {
    "enable_wal": False,  # Disabled by default
    "log_operations": ["ingest", "parse", "embed", "expose", "analyze", "mapping"],
    "namespace": "data_solution"
}
```

**Enable WAL via Policy:**
```python
wal_policy_enabled = {
    "enable_wal": True,  # Enabled by policy
    "log_operations": ["ingest", "parse", "embed", "expose"],
    "namespace": "data_solution"
}
```

### Phase 2: Saga Integration into Solution/Journey Orchestrators

#### Step 2.1: Add Saga Capability to Solution Orchestrators

**Location:** `backend/solution/services/*_solution_orchestrator_service/`

**Changes:**
- Add Saga policy configuration
- Add `_execute_with_saga()` helper method
- Integrate Saga into multi-step workflows

**Implementation:**
```python
class InsightsSolutionOrchestratorService(RealmServiceBase):
    def __init__(self, ...):
        # Saga policy (capability by design, optional by policy)
        self.saga_policy = {
            "enable_saga": False,  # Default: disabled
            "saga_operations": ["data_mapping", "complex_analysis"],
            "compensation_handlers": {}
        }
    
    async def _execute_with_saga(
        self,
        operation: str,
        workflow_func: Callable,
        compensation_handler: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow with Saga guarantees if enabled by policy.
        
        Pattern: "Capability by Design, Optional by Policy"
        """
        if not self.saga_policy.get("enable_saga", False):
            # Execute without Saga (normal flow)
            return await workflow_func()
        
        if operation not in self.saga_policy.get("saga_operations", []):
            # Execute without Saga (operation not in policy)
            return await workflow_func()
        
        # Get Saga Journey Orchestrator
        saga_orchestrator = await self._get_saga_journey_orchestrator()
        if not saga_orchestrator:
            self.logger.warning("⚠️ Saga Journey Orchestrator not available, executing without Saga")
            return await workflow_func()
        
        # Design Saga journey
        saga_journey = await saga_orchestrator.design_saga_journey(
            journey_type=operation,
            requirements={"operation": operation},
            compensation_handlers={
                operation: compensation_handler or f"revert_{operation}"
            },
            user_context=user_context
        )
        
        # Execute Saga journey
        saga_execution = await saga_orchestrator.execute_saga_journey(
            journey_id=saga_journey["journey_id"],
            user_id=user_context.get("user_id") if user_context else "anonymous",
            context={"operation": operation},
            user_context=user_context
        )
        
        # Execute workflow as Saga milestone
        try:
            result = await workflow_func()
            
            # Advance Saga step (success)
            await saga_orchestrator.advance_saga_step(
                saga_id=saga_execution["saga_id"],
                journey_id=saga_journey["journey_id"],
                user_id=user_context.get("user_id") if user_context else "anonymous",
                step_result={"status": "complete", **result},
                user_context=user_context
            )
            
            result["saga_id"] = saga_execution["saga_id"]
            return result
            
        except Exception as e:
            # Advance Saga step (failure) - triggers automatic compensation
            await saga_orchestrator.advance_saga_step(
                saga_id=saga_execution["saga_id"],
                journey_id=saga_journey["journey_id"],
                user_id=user_context.get("user_id") if user_context else "anonymous",
                step_result={"status": "failed", "error": str(e)},
                user_context=user_context
            )
            raise
    
    async def orchestrate_insights_mapping(
        self,
        source_file_id: str,
        target_file_id: str,
        mapping_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        saga_policy: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate insights mapping with optional Saga guarantees.
        
        Pattern: "Capability by Design, Optional by Policy"
        """
        # Update Saga policy if provided
        if saga_policy:
            self.saga_policy.update(saga_policy)
        
        # Execute with Saga if enabled
        return await self._execute_with_saga(
            operation="data_mapping",
            workflow_func=lambda: self.insights_journey_orchestrator.execute_data_mapping_workflow(
                source_file_id=source_file_id,
                target_file_id=target_file_id,
                mapping_options=mapping_options,
                user_context=user_context
            ),
            compensation_handler="revert_data_mapping",
            user_context=user_context
        )
```

#### Step 2.2: Add Saga Capability to Journey Orchestrators

**Similar pattern** - Add Saga capability to Journey Orchestrators for multi-step workflows.

#### Step 2.3: Policy Configuration

**Default Policy:**
```python
saga_policy_default = {
    "enable_saga": False,  # Disabled by default
    "saga_operations": ["data_mapping", "complex_analysis", "enterprise_migration"],
    "compensation_handlers": {}
}
```

**Enable Saga via Policy:**
```python
saga_policy_enabled = {
    "enable_saga": True,  # Enabled by policy
    "saga_operations": ["data_mapping", "enterprise_migration"],
    "compensation_handlers": {
        "data_mapping": "revert_data_mapping",
        "enterprise_migration": "rollback_migration"
    }
}
```

### Phase 3: MVP Solutions/Journeys

#### Step 3.1: Create MVPSolutionOrchestrator

**Location:** `backend/solution/services/mvp_solution_orchestrator_service/`

**Purpose:** Entry point for MVP solution, showcases Solution Realm capabilities

**Responsibilities:**
- Platform correlation
- Route to MVPJourneyOrchestrator
- Handle landing page requests
- Coordinate 4-pillar navigation

**Implementation:**
```python
class MVPSolutionOrchestratorService(RealmServiceBase):
    """
    MVP Solution Orchestrator - Entry point for MVP solution.
    
    WHAT: Orchestrates MVP solution (4-pillar navigation)
    HOW: Routes to MVPJourneyOrchestrator, coordinates platform correlation
    """
    
    async def orchestrate_mvp_session(
        self,
        user_id: str,
        session_type: str = "mvp",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate MVP session creation.
        
        Flow:
        1. Platform correlation
        2. Create session via MVPJourneyOrchestrator
        3. Return session details
        """
        # Platform correlation
        correlation_context = await self._orchestrate_platform_correlation(
            operation="mvp_session",
            user_context=user_context
        )
        
        # Get MVP Journey Orchestrator
        mvp_journey_orchestrator = await self._get_mvp_journey_orchestrator()
        
        # Create session
        session = await mvp_journey_orchestrator.create_mvp_session(
            user_id=user_id,
            session_type=session_type,
            user_context=correlation_context
        )
        
        # Record completion
        await self._record_platform_correlation_completion(
            operation="mvp_session",
            result=session,
            correlation_context=correlation_context
        )
        
        return session
    
    async def handle_request(
        self,
        method: str,
        path: str,
        params: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle HTTP requests for MVP solution.
        
        Routes:
        - POST /session -> orchestrate_mvp_session
        - GET /health -> health check
        """
        if path == "session" and method == "POST":
            return await self.orchestrate_mvp_session(
                user_id=params.get("user_id", "anonymous"),
                session_type=params.get("session_type", "mvp"),
                user_context=user_context
            )
        elif path == "health" and method == "GET":
            return {"status": "healthy", "service": "mvp_solution"}
        else:
            return {
                "success": False,
                "error": "Route not found",
                "path": path
            }
```

#### Step 3.2: Create MVPJourneyOrchestrator

**Location:** `backend/journey/orchestrators/mvp_journey_orchestrator/`

**Purpose:** Manages free navigation through 4 pillars, showcases Journey Realm capabilities

**Responsibilities:**
- Free navigation management
- Session state tracking
- Route to pillar-specific Journey Orchestrators
- Compose Session Journey Orchestrator

**Implementation:**
```python
class MVPJourneyOrchestrator(OrchestratorBase):
    """
    MVP Journey Orchestrator - Free navigation through 4 pillars.
    
    WHAT: Manages MVP user journey (free navigation)
    HOW: Composes Session Journey Orchestrator, routes to pillar orchestrators
    """
    
    async def create_mvp_session(
        self,
        user_id: str,
        session_type: str = "mvp",
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create MVP session with free navigation.
        
        Flow:
        1. Create session via Session Journey Orchestrator
        2. Initialize MVP state
        3. Return session details
        """
        # Get Session Journey Orchestrator
        session_orchestrator = await self._get_session_journey_orchestrator()
        
        # Create session
        session = await session_orchestrator.create_session(
            user_id=user_id,
            session_type=session_type,
            context={"mvp": True}
        )
        
        return session
    
    async def navigate_to_pillar(
        self,
        session_id: str,
        pillar: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Navigate to a specific pillar.
        
        Flow:
        1. Update session state
        2. Route to pillar-specific Journey Orchestrator
        3. Return pillar context
        """
        # Get pillar Journey Orchestrator
        pillar_orchestrator = await self._get_pillar_journey_orchestrator(pillar)
        
        # Get pillar context
        context = await pillar_orchestrator.get_pillar_context(
            session_id=session_id,
            user_context=user_context
        )
        
        return context
```

#### Step 3.3: Update FrontendGatewayService

**Add MVP solution routing:**
```python
pillar_map = {
    "mvp-solution": "MVPSolutionOrchestratorService",  # NEW
    "content-pillar": "ContentJourneyOrchestrator",
    "insights-solution": "InsightsSolutionOrchestratorService",
    "data-solution": "DataSolutionOrchestratorService",
    "operations-pillar": "OperationsOrchestrator",
    "business-outcomes-pillar": "BusinessOutcomesOrchestrator",
}
```

---

## 📋 Policy Examples

### Policy 1: WAL Enabled, Saga Disabled (Default)
```python
policy = {
    "wal": {
        "enable_wal": True,
        "log_operations": ["ingest", "parse", "embed"]
    },
    "saga": {
        "enable_saga": False
    }
}
```
**Use Case:** Data operations need audit trail, but no atomicity guarantees

### Policy 2: WAL Disabled, Saga Enabled (Critical Operations)
```python
policy = {
    "wal": {
        "enable_wal": False
    },
    "saga": {
        "enable_saga": True,
        "saga_operations": ["data_mapping", "enterprise_migration"]
    }
}
```
**Use Case:** Critical operations need atomicity, but WAL overhead not needed

### Policy 3: Both Enabled (Enterprise Operations)
```python
policy = {
    "wal": {
        "enable_wal": True,
        "log_operations": ["ingest", "parse", "embed", "mapping"]
    },
    "saga": {
        "enable_saga": True,
        "saga_operations": ["data_mapping", "enterprise_migration"]
    }
}
```
**Use Case:** Enterprise operations need both audit trail and atomicity

### Policy 4: Both Disabled (Simple Operations)
```python
policy = {
    "wal": {
        "enable_wal": False
    },
    "saga": {
        "enable_saga": False
    }
}
```
**Use Case:** Simple operations, no audit trail or atomicity needed

---

## 🚀 Implementation Phases

### Phase 1: WAL Integration (Week 1)
- [ ] Add WAL capability to DataSolutionOrchestrator
- [ ] Add WAL capability to InsightsSolutionOrchestrator
- [ ] Add policy configuration
- [ ] Create unit tests
- [ ] Create integration tests

### Phase 2: Saga Integration (Week 2)
- [ ] Add Saga capability to Solution Orchestrators
- [ ] Add Saga capability to Journey Orchestrators
- [ ] Add policy configuration
- [ ] Create unit tests
- [ ] Create integration tests

### Phase 3: MVP Solutions/Journeys (Week 3-4)
- [ ] Create MVPSolutionOrchestrator
- [ ] Create MVPJourneyOrchestrator
- [ ] Update FrontendGatewayService routing
- [ ] Create frontend integration
- [ ] Create E2E tests

---

## 📚 Related Documentation

- [DATA_SOLUTION_ORCHESTRATOR_REALM_INTEGRATION_PLAN.md](./DATA_SOLUTION_ORCHESTRATOR_REALM_INTEGRATION_PLAN.md) - Data solution orchestrator
- [REALM_ARCHITECTURE_MIGRATION_PLAN.md](./REALM_ARCHITECTURE_MIGRATION_PLAN.md) - Realm architecture migration
- [SAGA_JOURNEY_ORCHESTRATOR.md](../../symphainy-platform/backend/journey/docs/SAGA_JOURNEY_ORCHESTRATOR.md) - Saga journey orchestrator
- [WAL_MODULE_IMPLEMENTATION_SPEC.md](./insurance_use_case/WAL_MODULE_IMPLEMENTATION_SPEC.md) - WAL implementation spec

---

**Last Updated:** January 2025










