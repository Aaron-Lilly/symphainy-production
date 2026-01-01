# Universal Mapper Specialist - Declarative Migration

## Overview

This document describes the migration of `UniversalMapperSpecialist` from hardcoded logic to the declarative agent pattern. This is our first real agent migration, serving as a proof-of-concept for the declarative architecture.

## Migration Status

✅ **Completed:**
- Declarative implementation created (`universal_mapper_specialist_declarative.py`)
- Configuration file updated
- Interface methods maintained for compatibility
- Documentation created

⏳ **Next Steps:**
- Update orchestrator to use declarative version
- Test with real LLM abstraction
- Validate behavior matches original
- Remove old hardcoded implementation

## What Changed

### Before (Hardcoded)

```python
class UniversalMapperSpecialist(SpecialistCapabilityAgent):
    async def suggest_mappings(self, source_schema, target_schema_name, ...):
        # Hardcoded logic:
        # 1. Get target schema
        target_schema = await self._get_target_schema(target_schema_name)
        
        # 2. Query knowledge base
        similar_patterns = await self._query_similar_patterns(...)
        
        # 3. Generate suggestions
        suggestions = await self._generate_mapping_suggestions(...)
        
        # 4. Calculate confidence
        for suggestion in suggestions:
            suggestion["confidence"] = self._calculate_suggestion_confidence(...)
        
        return {"suggestions": suggestions, ...}
```

**Anti-patterns:**
- Direct service discovery (Librarian, CanonicalModelService) via Curator
- Placeholder semantic similarity calculation
- Hardcoded pattern matching logic
- No LLM reasoning (just heuristics)

### After (Declarative)

```python
class UniversalMapperSpecialist(DeclarativeAgentBase):
    async def suggest_mappings(self, source_schema, target_schema_name, ...):
        # Build request for declarative agent
        request = {
            "message": f"Suggest mappings from source schema to {target_schema_name}",
            "task": "suggest_mappings",
            "data": {
                "source_schema": source_schema,
                "target_schema_name": target_schema_name,
                "client_id": client_id
            },
            "user_context": user_context or {}
        }
        
        # Process request using declarative pattern (LLM does reasoning)
        result = await self.process_request(request)
        
        # Extract suggestions from LLM response and tool results
        return self._extract_suggestions(result)
```

**Benefits:**
- LLM does the reasoning (not hardcoded)
- Uses MCP tools (not direct service access)
- Configuration-driven (easy to change)
- Scoped tools (only sees relevant tools)

## Configuration File

**Location:** `backend/business_enablement/agents/configs/universal_mapper_specialist.yaml`

**Key Configuration:**
```yaml
agent_name: UniversalMapperSpecialist
role: Schema Mapping Specialist
goal: Create accurate field mappings between legacy schemas and canonical models
backstory: You are an expert in schema mapping...
allowed_tools:
  - map_to_canonical_tool
  - ingest_legacy_data_tool
  - route_policies_tool
  - get_migration_status_tool
```

## Interface Compatibility

The declarative version maintains the same interface methods for backward compatibility:

1. **`suggest_mappings()`** - Suggests mappings using learned patterns and AI
2. **`learn_from_mappings()`** - Learns mapping patterns from successful mappings
3. **`validate_mappings()`** - Validates mapping rules before application
4. **`learn_from_correction()`** - Learns from human corrections (with approval)

**How it works:**
- Each method builds a request dictionary
- Calls `process_request()` (declarative pattern)
- Extracts results from LLM response and tool execution
- Returns same format as original implementation

## Migration Steps

### Step 1: Update Orchestrator

**File:** `insurance_migration_orchestrator.py`

**Change:**
```python
# Before
from backend.business_enablement.agents.specialists.universal_mapper_specialist import UniversalMapperSpecialist

# After
from backend.business_enablement.agents.specialists.universal_mapper_specialist_declarative import UniversalMapperSpecialist
```

**Note:** The import path changes, but the class name stays the same, so no other code changes needed!

### Step 2: Ensure Orchestrator Sets Agent

**File:** `insurance_migration_orchestrator.py`

**Add after agent initialization:**
```python
if self._universal_mapper_agent and hasattr(self._universal_mapper_agent, 'set_orchestrator'):
    self._universal_mapper_agent.set_orchestrator(self)
    self.logger.info("✅ Universal Mapper Agent orchestrator set for MCP tool access")
```

### Step 3: Test Migration

1. **Test suggest_mappings():**
   ```python
   result = await agent.suggest_mappings(
       source_schema={...},
       target_schema_name="canonical_policy",
       client_id="client_1"
   )
   assert result["success"] == True
   assert len(result["suggestions"]) > 0
   ```

2. **Test learn_from_mappings():**
   ```python
   result = await agent.learn_from_mappings(
       source_schema={...},
       target_schema={...},
       mapping_rules={...},
       client_id="client_1"
   )
   assert result["success"] == True
   assert "pattern_id" in result
   ```

3. **Test validate_mappings():**
   ```python
   result = await agent.validate_mappings(
       source_schema={...},
       target_schema={...},
       mapping_rules={...}
   )
   assert result["success"] == True
   assert "is_valid" in result
   ```

### Step 4: Validate Behavior

Compare behavior with original implementation:
- Same method signatures
- Same return formats
- Same error handling
- Better reasoning (LLM-powered)

### Step 5: Remove Old Implementation

Once validated:
1. Archive old file: `universal_mapper_specialist.py` → `universal_mapper_specialist_legacy.py`
2. Update imports to use declarative version
3. Remove legacy file after full validation

## Key Differences

### 1. Service Discovery

**Before:**
```python
# Direct service discovery via Curator
librarian = await self.curator_foundation.discover_service("LibrarianService")
canonical_service = await self.curator_foundation.discover_service("CanonicalModelService")
```

**After:**
```python
# No direct service discovery - uses MCP tools via orchestrator
# Orchestrator provides MCP server with tools
# Agent calls tools, not services directly
```

### 2. Semantic Similarity

**Before:**
```python
def _calculate_semantic_similarity(self, source_field, target_field):
    # Placeholder - simple string matching
    if source_lower == target_lower:
        return 1.0
    # ... hardcoded logic
```

**After:**
```python
# LLM calculates semantic similarity as part of reasoning
# No hardcoded logic - LLM understands semantics
```

### 3. Pattern Matching

**Before:**
```python
async def _generate_mapping_suggestions(self, ...):
    # Hardcoded pattern matching logic
    for source_field in source_fields:
        # Find best match from patterns
        best_match = None
        # ... hardcoded matching logic
```

**After:**
```python
# LLM does pattern matching as part of reasoning
# Uses learned patterns from knowledge base
# More intelligent matching via LLM
```

## Testing Strategy

### Unit Tests

Test each interface method:
- `suggest_mappings()` with various schemas
- `learn_from_mappings()` with different mapping rules
- `validate_mappings()` with valid/invalid mappings
- `learn_from_correction()` with corrections

### Integration Tests

Test with real orchestrator:
- Agent initialized by orchestrator
- Orchestrator sets agent (MCP server access)
- Agent can execute MCP tools
- Results match expected format

### Comparison Tests

Compare with original:
- Same inputs → similar outputs
- Better reasoning (LLM-powered)
- Same error handling
- Same telemetry/audit

## Success Criteria

✅ **Migration Complete When:**
- [x] Declarative implementation created
- [x] Configuration file created
- [x] Interface methods maintained
- [ ] Orchestrator updated to use declarative version
- [ ] Tests pass with real LLM abstraction
- [ ] Behavior validated against original
- [ ] Old implementation archived

## Known Limitations

1. **MCP Tool Names**: Configuration uses `map_to_canonical_tool` but agent may need additional tools like `discover_schema`, `validate_mapping`, `get_similar_patterns`. These may need to be added to the MCP server.

2. **Tool Result Parsing**: The declarative version extracts results from tool execution. May need refinement based on actual tool response formats.

3. **LLM Response Parsing**: LLM responses are parsed as JSON. May need more robust parsing for complex responses.

## Next Steps

1. **Update Orchestrator** to use declarative version
2. **Test with Real LLM** abstraction
3. **Validate Behavior** matches original
4. **Add Missing MCP Tools** if needed
5. **Archive Old Implementation** after validation

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-19  
**Status:** Migration Ready - Pending Orchestrator Update









