# Insurance Use Case: Orchestrator Completion Plan

**Date:** December 2024  
**Status:** 📋 **IMPLEMENTATION PLAN**

---

## 🎯 Problem Summary

We have orchestrator methods defined, but they're **not fully implementing the orchestration logic**. They call one enabling service and return, rather than actually "stitching together" Smart City services, Enabling Services, and Agents to do the complete work.

---

## ✅ Solution: Complete Orchestrator Implementation

Following the pattern from `ContentAnalysisOrchestrator.analyze_document()`, we need to complete each orchestrator method to actually coordinate multiple services.

---

## 📋 Implementation Tasks

### **Task 1: Complete `ingest_legacy_data()` Orchestration**

**Current:** Only calls FileParserService  
**Target:** Orchestrate complete ingestion workflow

**Implementation:**
```python
async def ingest_legacy_data(self, file_id: str, file_data: Optional[bytes] = None, ...):
    """
    Complete orchestration:
    1. Upload/get file via Content Steward
    2. Parse file via File Parser Service
    3. Profile data via Data Steward
    4. Extract schema via Schema Mapper Service
    5. Store metadata via Librarian
    6. Track lineage via Data Steward
    7. Log all operations to WAL
    """
    # Step 1: Upload/get file
    content_steward = await self.get_content_steward_api()
    if file_data:
        upload_result = await content_steward.upload_file(file_data, filename, ...)
        file_id = upload_result["file_id"]
    else:
        file_metadata = await content_steward.get_file_metadata(file_id)
    
    # Step 2: Parse file
    file_parser = await self.get_enabling_service("FileParserService")
    parse_result = await file_parser.parse_file(file_id, ...)
    
    # Step 3: Profile data quality
    data_steward = await self.get_data_steward_api()
    profile_result = await data_steward.profile_data(parse_result["parsed_data"], ...)
    
    # Step 4: Extract schema
    schema_mapper = await self.get_enabling_service("SchemaMapperService")
    schema_result = await schema_mapper.extract_schema(parse_result["parsed_data"], ...)
    
    # Step 5: Store metadata
    librarian = await self.get_librarian_api()
    await librarian.store_document({
        "file_id": file_id,
        "schema": schema_result["schema"],
        "quality_metrics": profile_result["metrics"]
    }, ...)
    
    # Step 6: Track lineage
    await data_steward.track_lineage({
        "source": file_id,
        "operation": "ingest_legacy_data",
        "metadata": {...}
    })
    
    # Step 7: WAL logging (already done)
    
    return {
        "success": True,
        "file_id": file_id,
        "parsed_data": parse_result["parsed_data"],
        "schema": schema_result["schema"],
        "quality_metrics": profile_result["metrics"]
    }
```

---

### **Task 2: Complete `map_to_canonical()` Orchestration**

**Current:** Only calls CanonicalModelService  
**Target:** Orchestrate complete mapping workflow

**Implementation:**
```python
async def map_to_canonical(self, source_data: Dict, source_schema_id: Optional[str] = None, ...):
    """
    Complete orchestration:
    1. Get source schema from Librarian (if not provided)
    2. Validate source data via Data Steward
    3. Map source → canonical via Schema Mapper Service
    4. Validate canonical data via Canonical Model Service
    5. Store mapping rules via Librarian
    6. Track mapping lineage
    7. Log all operations to WAL
    """
    # Step 1: Get source schema
    librarian = await self.get_librarian_api()
    if source_schema_id:
        source_schema = await librarian.get_document(source_schema_id)
    else:
        # Extract schema from source_data
        schema_mapper = await self.get_enabling_service("SchemaMapperService")
        source_schema = await schema_mapper.extract_schema(source_data)
    
    # Step 2: Validate source data
    data_steward = await self.get_data_steward_api()
    validation_result = await data_steward.validate_data(source_data, source_schema)
    
    # Step 3: Map source → canonical
    schema_mapper = await self.get_enabling_service("SchemaMapperService")
    mapping_result = await schema_mapper.map_to_canonical(
        source_data=source_data,
        source_schema=source_schema,
        canonical_model_name="policy_v1"
    )
    
    # Step 4: Validate canonical data
    canonical_service = await self._get_canonical_model_service()
    canonical_validation = await canonical_service.validate_against_canonical(
        data=mapping_result["canonical_data"],
        model_name="policy_v1"
    )
    
    # Step 5: Store mapping rules
    await librarian.store_document({
        "mapping_id": mapping_result["mapping_id"],
        "source_schema": source_schema,
        "canonical_model": "policy_v1",
        "mapping_rules": mapping_result["mapping_rules"]
    }, ...)
    
    # Step 6: Track lineage
    await data_steward.track_lineage({
        "source": source_data.get("policy_id"),
        "operation": "map_to_canonical",
        "canonical_data_id": mapping_result["canonical_data_id"]
    })
    
    return {
        "success": True,
        "canonical_data": mapping_result["canonical_data"],
        "mapping_id": mapping_result["mapping_id"],
        "validation": canonical_validation
    }
```

---

### **Task 3: Complete `route_policies()` Orchestration**

**Current:** Only calls RoutingEngineService  
**Target:** Orchestrate complete routing workflow

**Implementation:**
```python
async def route_policies(self, policy_data: Dict, ...):
    """
    Complete orchestration:
    1. Get policy status from Policy Tracker
    2. Extract routing key via Routing Engine Service
    3. Evaluate routing rules via Routing Engine Service
    4. Update policy location via Policy Tracker
    5. Store routing decision via Librarian
    6. Track routing lineage
    7. Log all operations to WAL
    """
    policy_id = policy_data.get("policy_id")
    
    # Step 1: Get policy status
    policy_tracker = await self._get_policy_tracker()
    policy_status = await policy_tracker.get_policy_location(policy_id)
    
    # Step 2: Extract routing key
    routing_engine = await self._get_routing_engine_service()
    routing_key = await routing_engine.extract_routing_key(policy_data)
    
    # Step 3: Evaluate routing rules
    routing_result = await routing_engine.evaluate_routing(
        policy_data=policy_data,
        routing_key=routing_key
    )
    
    # Step 4: Update policy location
    target_system = routing_result["target_system"]
    await policy_tracker.update_migration_status(
        policy_id=policy_id,
        status="in_progress" if target_system != "legacy_system" else "not_started",
        details={"target_system": target_system}
    )
    
    # Step 5: Store routing decision
    librarian = await self.get_librarian_api()
    await librarian.store_document({
        "routing_id": routing_result["routing_id"],
        "policy_id": policy_id,
        "routing_key": routing_key,
        "target_system": target_system,
        "routing_rules": routing_result["rules_applied"]
    }, ...)
    
    # Step 6: Track lineage
    data_steward = await self.get_data_steward_api()
    await data_steward.track_lineage({
        "source": policy_id,
        "operation": "route_policies",
        "target_system": target_system
    })
    
    return {
        "success": True,
        "policy_id": policy_id,
        "target_system": target_system,
        "routing_key": routing_key,
        "routing_decision": routing_result
    }
```

---

## 🎯 Priority Order

1. **High Priority:** Complete `ingest_legacy_data()` - This is the entry point
2. **High Priority:** Complete `map_to_canonical()` - Core transformation logic
3. **Medium Priority:** Complete `route_policies()` - Routing decision logic
4. **Low Priority:** Add error handling and compensation for all methods
5. **Low Priority:** Add state management and resumption capabilities

---

## 📚 Reference Implementation

See `ContentAnalysisOrchestrator.analyze_document()` for the pattern:
- Coordinates multiple enabling services
- Calls Smart City services for infrastructure
- Tracks lineage and metadata
- Handles errors gracefully
- Returns comprehensive results

---

## ✅ Success Criteria

Each orchestrator method should:
1. ✅ Coordinate 3+ services (enabling + Smart City)
2. ✅ Handle errors gracefully with compensation
3. ✅ Track lineage and metadata
4. ✅ Log all operations to WAL
5. ✅ Return comprehensive results

---

**Last Updated:** December 2024  
**Status:** 📋 **READY FOR IMPLEMENTATION**











