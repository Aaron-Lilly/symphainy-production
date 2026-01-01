# Break-and-Fix: Caller Updates Required

## Summary
After updating RealmServiceBase to use correct Smart City service signatures, all callers must be updated to match.

## Changes Required

### 1. `search_documents(query: str, filters: Optional[Dict] = None)`
**Old:** `search_documents({"type": "deployment", "id": "123"})`  
**New:** `search_documents("deployment", {"type": "deployment", "id": "123"})`

**Files to Update:**
- `metrics_calculator_service.py` (1 usage)
- `solution_deployment_manager_service.py` (2 usages)
- `solution_analytics_service.py` (3 usages)
- `solution_composer_service.py` (1 usage)
- `structured_journey_orchestrator_service.py` (1 usage)
- `journey_milestone_tracker_service.py` (5 usages)
- `journey_analytics_service.py` (3 usages)

**Pattern:**
```python
# Old
results = await self.search_documents({"type": "milestone", "journey_id": journey_id})

# New
results = await self.search_documents("milestone", {"type": "milestone", "journey_id": journey_id})
```

### 2. `validate_data_quality(schema_data: Dict[str, Any]) -> bool`
**Old:** `validate_data_quality(data=data, validation_rules={...})`  
**New:** `validate_data_quality(schema_data={...})`

**Files to Update:**
- `data_analyzer_service.py` (1 usage) ✅ FIXED
- `metrics_calculator_service.py` (1 usage)
- `export_formatter_service.py` (1 usage)
- `validation_engine_service.py` (1 usage)

**Pattern:**
```python
# Old
validation_result = await self.validate_data_quality(
    data=data,
    validation_rules={"required_fields": [], "quality_checks": ["completeness"]}
)

# New
schema_data = {
    "name": "validation_schema",
    "type": "validation",
    "fields": [],
    "rules": {"required_fields": [], "quality_checks": ["completeness"]}
}
is_valid = await self.validate_data_quality(schema_data)
```

### 3. `track_data_lineage(lineage_data: Dict[str, Any]) -> str`
**Old:** `track_data_lineage(source="id1", destination="id2", transformation={...})`  
**New:** `track_data_lineage(lineage_data={...})`

**Files to Update:**
- `transformation_engine_service.py` (4 usages)
- `workflow_manager_service.py` (1 usage)
- `roadmap_generation_service.py` (1 usage - check if exists)

**Pattern:**
```python
# Old
await self.track_data_lineage(
    source=data_id,
    destination=storage_result.get("document_id"),
    transformation={"type": "data_transformation", "rules": transformation_rules}
)

# New
lineage_data = {
    "asset_id": storage_result.get("document_id"),
    "parent_assets": [data_id],
    "child_assets": [],
    "transformation": {"type": "data_transformation", "rules": transformation_rules}
}
lineage_id = await self.track_data_lineage(lineage_data)
```

## Implementation Order

1. ✅ Fix `validate_data_quality` in `data_analyzer_service.py` (DONE)
2. Fix `validate_data_quality` in remaining files
3. Fix `track_data_lineage` in all files
4. Fix `search_documents` in all files

## Notes

- Return type changed: `validate_data_quality` now returns `bool` (was `Dict`)
- Return type changed: `track_data_lineage` now returns `str` (lineage_id, was `bool`)
- All changes are breaking - no backward compatibility






