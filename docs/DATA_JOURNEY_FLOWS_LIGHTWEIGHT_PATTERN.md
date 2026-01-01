# Data Journey Flows: Lightweight Pattern
## Rollback, Forward Documentation, and Planning - "Capability by Design, Optional by Policy"

**Date:** January 2025  
**Status:** 📋 **DESIGN PROPOSAL**  
**Pattern:** "Capability by Design, Optional by Policy" (inspired by "Secure by Design, Open by Policy")

---

## 🎯 Executive Summary

This document proposes a **lightweight, hybrid pattern** for incorporating rollback, forward documentation, and planning capabilities into data journey flows. The pattern follows the architectural principle: **"Capability by Design, Optional by Policy"** - similar to the "Secure by Design, Open by Policy" approach.

**Key Principle:** Build the capability into the architecture, but make it optional and policy-driven to avoid complexity overload.

---

## 📊 Current State

### Existing Capabilities

1. **Saga Journey Orchestrator** (Full Implementation)
   - Automatic compensation (rollback)
   - Reverse-order compensation handlers
   - Saga state tracking
   - **Use Case:** Multi-service workflows requiring atomicity

2. **Structured Journey Orchestrator** (Base Implementation)
   - Linear, enforced progression
   - Milestone tracking
   - **Use Case:** Guided workflows without rollback

3. **Data Journey Flows** (Current)
   - Upload → Parse → Embed → Expose
   - No rollback capability
   - No forward documentation
   - No planning integration

### Gap Analysis

**Missing Capabilities:**
- ❌ Lightweight rollback for data operations (without full Saga)
- ❌ Forward documentation (documenting what will happen)
- ❌ Planning integration (AI-assisted planning before execution)

**Complexity Concern:**
- Full Saga implementation adds significant overhead
- Not all data operations need atomicity guarantees
- Need a middle ground between "no rollback" and "full Saga"

---

## 🏗️ Proposed Pattern: "Capability by Design, Optional by Policy"

### Pattern Overview

**"Capability by Design":**
- Build rollback, documentation, and planning capabilities into the architecture
- Make them available to all data journey flows
- Design them to be lightweight and non-intrusive

**"Optional by Policy":**
- Enable/disable via policy (configuration, not hard-coding)
- Policy determines when to use each capability
- Default: Capabilities available but not required

### Architecture

```
Data Journey Flow (Base)
  ├─ Rollback Capability (Optional)
  │   ├─ Lightweight rollback handlers
  │   ├─ State checkpointing
  │   └─ Policy: enable_rollback = true/false
  │
  ├─ Forward Documentation (Optional)
  │   ├─ Pre-execution documentation
  │   ├─ Plan generation
  │   └─ Policy: enable_forward_docs = true/false
  │
  └─ Planning Integration (Optional)
      ├─ AI-assisted planning
      ├─ Plan validation
      └─ Policy: enable_planning = true/false
```

---

## 🔧 Implementation Design

### 1. Lightweight Rollback Pattern

#### Design Principles

**Not Full Saga:**
- No automatic compensation
- No reverse-order execution
- No saga state machine

**Lightweight Rollback:**
- Checkpoint state at key milestones
- Store rollback handlers (simple undo operations)
- Manual rollback trigger (not automatic)
- Idempotent rollback operations

#### Implementation

```python
class LightweightRollbackCapability:
    """
    Lightweight rollback capability for data journey flows.
    
    Pattern: "Capability by Design, Optional by Policy"
    - Built into architecture (capability by design)
    - Enabled via policy (optional by policy)
    """
    
    async def checkpoint_milestone(
        self,
        milestone_id: str,
        state: Dict[str, Any],
        rollback_handler: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Checkpoint milestone state for potential rollback.
        
        Args:
            milestone_id: Unique milestone identifier
            state: Current state snapshot
            rollback_handler: Optional rollback handler name
        
        Returns:
            Checkpoint ID
        """
        # Store checkpoint in Librarian
        checkpoint = {
            "checkpoint_id": f"checkpoint_{milestone_id}_{uuid.uuid4()}",
            "milestone_id": milestone_id,
            "state": state,
            "rollback_handler": rollback_handler,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.librarian.store_document(
            document_id=checkpoint["checkpoint_id"],
            content=checkpoint,
            metadata={"type": "rollback_checkpoint"}
        )
        
        return checkpoint
    
    async def rollback_to_checkpoint(
        self,
        checkpoint_id: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Rollback to a specific checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to rollback to
            user_context: User context
        
        Returns:
            Rollback result
        """
        # Retrieve checkpoint
        checkpoint = await self.librarian.retrieve_document(checkpoint_id)
        if not checkpoint:
            return {"success": False, "error": "Checkpoint not found"}
        
        # Execute rollback handler if provided
        if checkpoint.get("rollback_handler"):
            rollback_result = await self._execute_rollback_handler(
                checkpoint["rollback_handler"],
                checkpoint["state"],
                user_context
            )
            return rollback_result
        
        # Otherwise, return checkpoint state for manual restoration
        return {
            "success": True,
            "checkpoint_id": checkpoint_id,
            "state": checkpoint["state"],
            "message": "Checkpoint restored (manual restoration required)"
        }
```

#### Policy Configuration

```python
# Policy: Enable lightweight rollback
data_journey_policy = {
    "enable_rollback": True,  # Capability available
    "rollback_checkpoints": [
        "upload_complete",
        "parse_complete",
        "embed_complete"
    ],
    "auto_checkpoint": True  # Automatically checkpoint at milestones
}
```

### 2. Forward Documentation Pattern

#### Design Principles

**Pre-Execution Documentation:**
- Document what will happen before execution
- Generate execution plan
- Validate plan before execution

**Lightweight:**
- Simple plan generation (not full AI planning)
- Template-based documentation
- Optional validation

#### Implementation

```python
class ForwardDocumentationCapability:
    """
    Forward documentation capability for data journey flows.
    
    Pattern: "Capability by Design, Optional by Policy"
    """
    
    async def generate_execution_plan(
        self,
        journey_type: str,
        requirements: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate execution plan before execution.
        
        Args:
            journey_type: Type of journey (e.g., "data_ingest")
            requirements: Journey requirements
            user_context: User context
        
        Returns:
            Execution plan with steps, estimated time, resources
        """
        plan = {
            "plan_id": f"plan_{uuid.uuid4()}",
            "journey_type": journey_type,
            "steps": self._generate_steps(journey_type, requirements),
            "estimated_time": self._estimate_time(journey_type, requirements),
            "resources": self._estimate_resources(journey_type, requirements),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Store plan in Librarian
        await self.librarian.store_document(
            document_id=plan["plan_id"],
            content=plan,
            metadata={"type": "execution_plan"}
        )
        
        return plan
    
    async def document_forward(
        self,
        plan_id: str,
        step: str,
        action: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Document forward-looking action before execution.
        
        Args:
            plan_id: Execution plan ID
            step: Current step
            action: Action to be taken
            context: Action context
        
        Returns:
            Documentation result
        """
        doc = {
            "doc_id": f"forward_doc_{uuid.uuid4()}",
            "plan_id": plan_id,
            "step": step,
            "action": action,
            "context": context,
            "documented_at": datetime.utcnow().isoformat()
        }
        
        await self.librarian.store_document(
            document_id=doc["doc_id"],
            content=doc,
            metadata={"type": "forward_documentation"}
        )
        
        return doc
```

#### Policy Configuration

```python
# Policy: Enable forward documentation
data_journey_policy = {
    "enable_forward_docs": True,
    "generate_plan": True,  # Generate plan before execution
    "document_steps": True,  # Document each step before execution
    "validate_plan": False  # Optional: Validate plan before execution
}
```

### 3. Planning Integration Pattern

#### Design Principles

**AI-Assisted Planning:**
- Use AI to generate execution plans
- Validate plans before execution
- Learn from execution results

**Lightweight:**
- Optional AI planning (not required)
- Template-based fallback
- Simple validation

#### Implementation

```python
class PlanningIntegrationCapability:
    """
    Planning integration capability for data journey flows.
    
    Pattern: "Capability by Design, Optional by Policy"
    """
    
    async def generate_ai_plan(
        self,
        journey_type: str,
        requirements: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI-assisted execution plan.
        
        Args:
            journey_type: Type of journey
            requirements: Journey requirements
            user_context: User context
        
        Returns:
            AI-generated execution plan
        """
        # Use AI to generate plan (optional - can fallback to template)
        if self.policy.get("enable_ai_planning", False):
            plan = await self._generate_ai_plan(journey_type, requirements)
        else:
            plan = await self._generate_template_plan(journey_type, requirements)
        
        return plan
    
    async def validate_plan(
        self,
        plan: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate execution plan before execution.
        
        Args:
            plan: Execution plan
            user_context: User context
        
        Returns:
            Validation result
        """
        validation = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Validate plan steps
        for step in plan.get("steps", []):
            step_validation = await self._validate_step(step, user_context)
            if not step_validation["valid"]:
                validation["valid"] = False
                validation["errors"].extend(step_validation["errors"])
            validation["warnings"].extend(step_validation.get("warnings", []))
        
        return validation
```

#### Policy Configuration

```python
# Policy: Enable planning integration
data_journey_policy = {
    "enable_planning": True,
    "enable_ai_planning": False,  # Use AI for planning (optional)
    "validate_plan": True,  # Validate plan before execution
    "learn_from_results": False  # Learn from execution results (future)
}
```

---

## 🎯 Integration with Data Journey Flows

### Example: Data Ingest Flow with Capabilities

```python
async def orchestrate_data_ingest_with_capabilities(
    self,
    file_data: bytes,
    file_name: str,
    file_type: str,
    user_context: Optional[Dict[str, Any]] = None,
    policy: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Orchestrate data ingest with optional capabilities.
    
    Pattern: "Capability by Design, Optional by Policy"
    """
    # Default policy (capabilities available but not required)
    default_policy = {
        "enable_rollback": False,
        "enable_forward_docs": False,
        "enable_planning": False
    }
    policy = policy or default_policy
    
    # Step 1: Generate plan (if enabled)
    plan = None
    if policy.get("enable_planning"):
        plan = await self.planning_capability.generate_ai_plan(
            journey_type="data_ingest",
            requirements={"file_name": file_name, "file_type": file_type},
            user_context=user_context
        )
        
        # Validate plan (if enabled)
        if policy.get("validate_plan"):
            validation = await self.planning_capability.validate_plan(plan, user_context)
            if not validation["valid"]:
                return {"success": False, "errors": validation["errors"]}
    
    # Step 2: Document forward (if enabled)
    if policy.get("enable_forward_docs") and plan:
        await self.forward_docs_capability.document_forward(
            plan_id=plan["plan_id"],
            step="upload",
            action="upload_file",
            context={"file_name": file_name}
        )
    
    # Step 3: Execute with checkpointing (if enabled)
    if policy.get("enable_rollback"):
        checkpoint = await self.rollback_capability.checkpoint_milestone(
            milestone_id="before_upload",
            state={"file_name": file_name},
            rollback_handler="delete_uploaded_file"
        )
    
    # Step 4: Execute upload
    result = await self.content_journey_orchestrator.handle_content_upload(
        file_data=file_data,
        filename=file_name,
        file_type=file_type,
        user_context=user_context
    )
    
    # Step 5: Checkpoint after upload (if enabled)
    if policy.get("enable_rollback") and result.get("success"):
        await self.rollback_capability.checkpoint_milestone(
            milestone_id="upload_complete",
            state={"file_id": result.get("file_id")},
            rollback_handler="delete_uploaded_file"
        )
    
    return result
```

---

## 📋 Policy Examples

### Policy 1: No Capabilities (Default)
```python
policy = {
    "enable_rollback": False,
    "enable_forward_docs": False,
    "enable_planning": False
}
```
**Use Case:** Simple data operations, no rollback needed

### Policy 2: Rollback Only
```python
policy = {
    "enable_rollback": True,
    "rollback_checkpoints": ["upload_complete", "parse_complete"],
    "enable_forward_docs": False,
    "enable_planning": False
}
```
**Use Case:** Data operations where rollback is useful but not critical

### Policy 3: Full Capabilities (Critical Operations)
```python
policy = {
    "enable_rollback": True,
    "enable_forward_docs": True,
    "enable_planning": True,
    "enable_ai_planning": True,
    "validate_plan": True
}
```
**Use Case:** Critical data operations requiring full traceability

### Policy 4: Documentation Only
```python
policy = {
    "enable_rollback": False,
    "enable_forward_docs": True,
    "enable_planning": True,
    "enable_ai_planning": False  # Use template planning
}
```
**Use Case:** Operations where documentation is important but rollback not needed

---

## ⚠️ Important Considerations

### 1. Complexity Management

**Lightweight Pattern:**
- ✅ Capabilities are optional (not required)
- ✅ Policy-driven (not hard-coded)
- ✅ Simple implementations (not full Saga)

**Avoid:**
- ❌ Making capabilities mandatory
- ❌ Complex state machines
- ❌ Automatic compensation (use Saga for that)

### 2. Performance Impact

**Minimal Overhead:**
- Checkpointing: Simple document storage
- Forward docs: Simple document storage
- Planning: Optional AI calls (can use templates)

**When to Use:**
- ✅ When capabilities add value
- ✅ When policy enables them
- ❌ Don't enable by default (keep lightweight)

### 3. When to Use Full Saga

**Use Full Saga When:**
- Multi-service workflows requiring atomicity
- Automatic compensation required
- Financial transactions
- Critical business processes

**Use Lightweight Pattern When:**
- Single-service operations
- Manual rollback acceptable
- Documentation useful but not critical
- Planning helpful but not required

---

## 🚀 Implementation Phases

### Phase 1: Lightweight Rollback (MVP)
- [ ] Implement `LightweightRollbackCapability`
- [ ] Add checkpointing to data journey flows
- [ ] Add policy configuration
- [ ] Create unit tests
- [ ] Create integration tests

### Phase 2: Forward Documentation (MVP)
- [ ] Implement `ForwardDocumentationCapability`
- [ ] Add plan generation to data journey flows
- [ ] Add policy configuration
- [ ] Create unit tests
- [ ] Create integration tests

### Phase 3: Planning Integration (Future)
- [ ] Implement `PlanningIntegrationCapability`
- [ ] Add AI planning (optional)
- [ ] Add plan validation
- [ ] Create unit tests
- [ ] Create integration tests

---

## 📚 Related Documentation

- [Saga Journey Orchestrator](../../symphainy-platform/backend/journey/docs/SAGA_JOURNEY_ORCHESTRATOR.md) - Full Saga implementation
- [DATA_SOLUTION_ORCHESTRATOR_REALM_INTEGRATION_PLAN.md](./DATA_SOLUTION_ORCHESTRATOR_REALM_INTEGRATION_PLAN.md) - Data solution orchestrator
- [REALM_ARCHITECTURE_MIGRATION_PLAN.md](./REALM_ARCHITECTURE_MIGRATION_PLAN.md) - Realm architecture migration

---

**Last Updated:** January 2025










