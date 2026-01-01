# Remaining Enabling Services Test Plan

## Summary

This document tracks the remaining enabling services that need to be tested before moving to Business Outcomes Orchestrator and Agentic Foundation testing.

---

## ✅ Already Tested Services (11)

1. ✅ file_parser_service
2. ✅ data_analyzer_service
3. ✅ metrics_calculator_service
4. ✅ validation_engine_service
5. ✅ export_formatter_service
6. ✅ visualization_engine_service
7. ✅ report_generator_service
8. ✅ workflow_conversion_service
9. ✅ coexistence_analysis_service
10. ✅ sop_builder_service
11. ✅ roadmap_generation_service
12. ✅ poc_generation_service (just completed)

---

## ⏳ Remaining Services to Test (13)

### High Priority (for Business Outcomes)
1. ⏳ **transformation_engine_service** - Data transformation
2. ⏳ **schema_mapper_service** - Schema mapping
3. ⏳ **workflow_manager_service** - Workflow management

### Medium Priority (cross-cutting)
4. ⏳ **data_compositor_service** - Data composition
5. ⏳ **reconciliation_service** - Data reconciliation
6. ⏳ **format_composer_service** - Format composition
7. ⏳ **data_insights_query_service** - NLP queries for insights
8. ⏳ **insights_generator_service** - Insights generation
9. ⏳ **insights_orchestrator_service** - Insights orchestration

### Lower Priority (infrastructure/support)
10. ⏳ **apg_processor_service** - APG processing
11. ⏳ **audit_trail_service** - Audit trail tracking
12. ⏳ **configuration_service** - Configuration management
13. ⏳ **notification_service** - Notifications

---

## Testing Strategy

### Pattern to Follow
Each service test should:
1. Use `smart_city_infrastructure` fixture
2. Function-scope fixtures
3. Timeout protections (60s for init, 120s for tests)
4. Test all SOA API methods
5. Architecture verification
6. Detailed logging

### Test Template
```python
@pytest.fixture(scope="function")
async def {service_name}_service(smart_city_infrastructure):
    """{ServiceName}Service instance for each test."""
    from backend.business_enablement.enabling_services.{service_name}.{service_name} import {ServiceName}Service
    
    service = {ServiceName}Service(
        service_name="{ServiceName}Service",
        realm_name="business_enablement",
        platform_gateway=infra["platform_gateway"],
        di_container=infra["di_container"]
    )
    
    result = await asyncio.wait_for(service.initialize(), timeout=60.0)
    if not result:
        pytest.fail("Service failed to initialize")
    
    yield service

class Test{ServiceName}ServiceFunctional:
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_service_initialization(self, {service_name}_service):
        """Test service initialization."""
        assert {service_name}_service.is_initialized is True
    
    # Test each SOA API method
    # ...
    
    @pytest.mark.asyncio
    @pytest.mark.timeout_120
    async def test_architecture_verification(self, {service_name}_service):
        """Test architecture patterns."""
        from bases.realm_service_base import RealmServiceBase
        assert isinstance({service_name}_service, RealmServiceBase)
```

---

## Execution Order

1. **Phase 1: High Priority** (3 services)
   - transformation_engine_service
   - schema_mapper_service
   - workflow_manager_service

2. **Phase 2: Medium Priority** (6 services)
   - data_compositor_service
   - reconciliation_service
   - format_composer_service
   - data_insights_query_service
   - insights_generator_service
   - insights_orchestrator_service

3. **Phase 3: Lower Priority** (4 services)
   - apg_processor_service
   - audit_trail_service
   - configuration_service
   - notification_service

---

## Estimated Time

- Per service: 15-30 minutes (depending on complexity)
- Total: ~4-6 hours for all 13 services

---

## Next Steps After Testing

1. ✅ Test all remaining enabling services
2. ✅ Test Business Outcomes Orchestrator end-to-end
3. ✅ Instantiate Agentic Foundation
4. ✅ Test agents with mocks
5. ✅ Test agents with real API calls




