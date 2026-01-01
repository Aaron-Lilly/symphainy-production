# Phase 1 Execution Plan - Initialization Tests for All 25 Services

## 🎯 Goal

Complete initialization tests for all 25 enabling services, testing each one as we add it, and fixing any platform issues we discover.

## 📋 Current Status

**Services with initialization tests:** 5 of 25
- ✅ File Parser Service
- ✅ Data Analyzer Service
- ✅ Metrics Calculator Service
- ✅ Validation Engine Service
- ✅ Transformation Engine Service

**Services needing initialization tests:** 20 of 25
- ⚠️ Schema Mapper Service
- ⚠️ Workflow Manager Service
- ⚠️ Visualization Engine Service
- ⚠️ Report Generator Service
- ⚠️ Export Formatter Service
- ⚠️ Data Compositor Service
- ⚠️ Reconciliation Service
- ⚠️ Notification Service
- ⚠️ Audit Trail Service
- ⚠️ Configuration Service
- ⚠️ Workflow Conversion Service
- ⚠️ Insights Generator Service
- ⚠️ Insights Orchestrator Service
- ⚠️ SOP Builder Service
- ⚠️ Coexistence Analysis Service
- ⚠️ APG Processor Service
- ⚠️ POC Generation Service
- ⚠️ Roadmap Generation Service
- ⚠️ Data Insights Query Service
- ⚠️ Format Composer Service

## 🚀 Execution Strategy

### For Each Service:

1. **Add initialization test** to `test_enabling_services_comprehensive.py`
2. **Run the test** immediately
3. **If it fails:**
   - Analyze the failure (infrastructure? code? architecture?)
   - Fix the platform issue
   - Re-run the test
4. **If it passes:**
   - Verify it's actually working (not just passing)
   - Move to next service

### Test Pattern (Already Established)

```python
@pytest.mark.asyncio
async def test_<service_name>_service_initializes(self, test_infrastructure):
    """Test that <Service Name> Service initializes correctly."""
    try:
        from backend.business_enablement.enabling_services.<service_path> import <ServiceClass>
        
        infra = test_infrastructure
        service = <ServiceClass>(
            service_name="<ServiceName>Service",
            realm_name="business_enablement",
            platform_gateway=infra["platform_gateway"],
            di_container=infra["di_container"]
        )
        
        # Use timeout for initialization
        try:
            result = await asyncio.wait_for(
                service.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"<Service Name> Service initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis"
            )
        
        if not result:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"<Service Name> Service initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis\n\n"
                f"Fix: Ensure all critical infrastructure containers are running and healthy."
            )
        
        assert result is True, "<Service Name> Service should initialize"
        assert service.is_initialized, "<Service Name> Service should be marked as initialized"
        
    except ImportError as e:
        pytest.fail(
            f"<Service Name> Service not available: {e}\n\n"
            f"This indicates a code/dependency issue, not infrastructure.\n"
            f"Check that services are installed and in Python path."
        )
    except Exception as e:
        error_str = str(e).lower()
        if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"<Service Name> Service initialization failed: {e}\n\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                f"Check Docker containers: docker ps --filter name=symphainy-"
            )
        else:
            raise
```

## 📝 Services to Add (In Order)

1. Schema Mapper Service
2. Workflow Manager Service
3. Visualization Engine Service
4. Report Generator Service
5. Export Formatter Service
6. Data Compositor Service
7. Reconciliation Service
8. Notification Service
9. Audit Trail Service
10. Configuration Service
11. Workflow Conversion Service
12. Insights Generator Service
13. Insights Orchestrator Service
14. SOP Builder Service
15. Coexistence Analysis Service
16. APG Processor Service
17. POC Generation Service
18. Roadmap Generation Service
19. Data Insights Query Service
20. Format Composer Service

## ✅ Success Criteria

- All 25 services have initialization tests
- All tests pass with real infrastructure
- Any platform issues discovered are fixed
- Tests provide actionable diagnostics on failure

## 🎯 Let's Begin!

