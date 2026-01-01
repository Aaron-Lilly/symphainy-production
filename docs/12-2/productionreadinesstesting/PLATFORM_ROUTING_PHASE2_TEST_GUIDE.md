# Platform Routing: Phase 2 Test Guide

**Date:** December 2024  
**Status:** 🧪 Test Guide Ready  
**Purpose:** Verify route registration with Curator

---

## 🎯 Test Objectives

1. ✅ Verify routes are registered during FrontendGatewayService initialization
2. ✅ Verify routes are discoverable from Curator
3. ✅ Verify route metadata is complete and correct
4. ✅ Verify handler methods exist for all registered routes

---

## 🧪 Test Methods

### **Method 1: Check Logs During Initialization**

**Steps:**
1. Start the platform
2. Watch initialization logs for FrontendGatewayService
3. Look for route registration messages

**Expected Log Output:**
```
📋 Registering routes with Curator...
✅ Route registered: /api/v1/content-pillar/upload-file
✅ Route registered: /api/v1/content-pillar/process-file/{file_id}
✅ Route registered: /api/v1/content-pillar/list-uploaded-files
✅ Route registered: /api/v1/content-pillar/get-file-details/{file_id}
✅ Route registered: /api/v1/content-pillar/health
✅ Route registered: /api/v1/insights-pillar/analyze-content
...
✅ Registered 15/15 routes with Curator
```

**Success Criteria:**
- ✅ All 15 routes show "Route registered" messages
- ✅ Final message shows "Registered 15/15 routes"
- ✅ No error messages during registration

---

### **Method 2: Query Routes from Curator**

**Steps:**
1. Get Curator API
2. Call `discover_routes()` method
3. Verify routes are returned

**Python Code:**
```python
# Get Curator API
curator = await get_curator_api()

# Discover all routes
all_routes = await curator.discover_routes()

# Discover routes by pillar
content_routes = await curator.discover_routes(pillar="content-pillar")
insights_routes = await curator.discover_routes(pillar="insights-pillar")

# Verify counts
assert len(content_routes) == 5, f"Expected 5 Content routes, got {len(content_routes)}"
assert len(insights_routes) == 8, f"Expected 8 Insights routes, got {len(insights_routes)}"
```

**Expected Results:**
- ✅ `all_routes` contains 15 routes
- ✅ `content_routes` contains 5 routes
- ✅ `insights_routes` contains 8 routes
- ✅ Each route has complete metadata

---

### **Method 3: Verify Route Metadata**

**Steps:**
1. Get a route from Curator
2. Verify all required fields are present
3. Verify field values are correct

**Python Code:**
```python
# Get a route
routes = await curator.discover_routes(pillar="content-pillar")
route = routes[0]  # Get first route

# Verify required fields
required_fields = [
    "route_id",
    "path",
    "method",
    "pillar",
    "realm",
    "service_name",
    "capability_name",
    "handler",
    "handler_service",
    "description",
    "version",
    "defined_by"
]

for field in required_fields:
    assert field in route, f"Missing required field: {field}"

# Verify specific values
assert route["pillar"] == "content-pillar"
assert route["realm"] == "business_enablement"
assert route["service_name"] == "FrontendGatewayService"
assert route["handler_service"] == "FrontendGatewayService"
assert route["defined_by"] == "experience_foundation"
```

**Expected Results:**
- ✅ All required fields present
- ✅ Field values match expected values
- ✅ Handler method exists in FrontendGatewayService

---

### **Method 4: Verify Handler Methods Exist**

**Steps:**
1. Get all registered routes
2. For each route, verify handler method exists in FrontendGatewayService

**Python Code:**
```python
# Get FrontendGatewayService
gateway = await get_frontend_gateway_service()

# Get all routes
routes = await curator.discover_routes()

# Verify handlers exist
for route in routes:
    handler_name = route.get("handler")
    handler_service = route.get("handler_service")
    
    if handler_service == "FrontendGatewayService":
        assert hasattr(gateway, handler_name), \
            f"Handler method not found: {handler_name}"
        
        handler = getattr(gateway, handler_name)
        assert callable(handler), \
            f"Handler is not callable: {handler_name}"
```

**Expected Results:**
- ✅ All handler methods exist
- ✅ All handlers are callable
- ✅ No missing handlers

---

### **Method 5: Test Route Discovery Integration**

**Steps:**
1. Enable feature flag (optional - for Phase 3)
2. Check that routes are discovered and registered with APIRoutingUtility

**Python Code:**
```python
# Enable feature flag
gateway.use_discovered_routing = True

# Initialize gateway (triggers route discovery)
await gateway.initialize()

# Check discovered routes
assert len(gateway.discovered_routes) > 0, "No routes discovered"

# Check APIRoutingUtility routes
if gateway.api_router:
    routes = await gateway.api_router.list_routes()
    assert len(routes) > 0, "No routes in APIRoutingUtility"
```

**Expected Results:**
- ✅ Routes discovered from Curator
- ✅ Routes registered with APIRoutingUtility
- ✅ Routes available for new routing approach

---

## 📋 Test Checklist

### **Route Registration**
- [ ] Routes registered during initialization
- [ ] All 15 routes registered successfully
- [ ] No errors during registration
- [ ] Registration logged correctly

### **Route Discovery**
- [ ] Routes discoverable from Curator
- [ ] Routes filtered by pillar correctly
- [ ] Routes filtered by realm correctly
- [ ] Route metadata complete

### **Route Metadata**
- [ ] All required fields present
- [ ] Field values correct
- [ ] Handler methods exist
- [ ] Handler methods callable

### **Integration**
- [ ] Routes discoverable by FrontendGatewayService
- [ ] Routes registerable with APIRoutingUtility
- [ ] Ready for Phase 3 testing

---

## 🐛 Troubleshooting

### **Issue: Routes Not Registered**

**Symptoms:**
- No "Route registered" messages in logs
- `discover_routes()` returns empty list

**Possible Causes:**
1. RouteRegistryService not available
2. Curator not initialized
3. Registration method not called

**Solutions:**
1. Check Curator initialization logs
2. Verify RouteRegistryService is available
3. Check that `_register_routes_with_curator()` is called in `initialize()`

### **Issue: Handler Methods Not Found**

**Symptoms:**
- "Handler method not found" warnings
- Routes not registered

**Possible Causes:**
1. Handler method name mismatch
2. Handler method doesn't exist
3. Handler method renamed

**Solutions:**
1. Verify handler method names in route metadata
2. Check that handler methods exist in FrontendGatewayService
3. Update route metadata if handlers renamed

### **Issue: Route Metadata Incomplete**

**Symptoms:**
- Routes registered but missing fields
- Discovery returns incomplete metadata

**Possible Causes:**
1. Route metadata definition incomplete
2. RouteRegistryService not storing all fields

**Solutions:**
1. Check route metadata in `_register_routes_with_curator()`
2. Verify RouteRegistryService stores all fields
3. Update route metadata if needed

---

## 📊 Expected Test Results

### **Route Counts**
- **Total Routes:** 15
- **Content Pillar:** 5 routes
- **Insights Pillar:** 8 routes
- **Operations Pillar:** 1 route
- **Business Outcomes Pillar:** 1 route

### **Route Examples**

**Content Pillar:**
- `POST /api/v1/content-pillar/upload-file`
- `POST /api/v1/content-pillar/process-file/{file_id}`
- `GET /api/v1/content-pillar/list-uploaded-files`
- `GET /api/v1/content-pillar/get-file-details/{file_id}`
- `GET /api/v1/content-pillar/health`

**Insights Pillar:**
- `POST /api/v1/insights-pillar/analyze-content`
- `POST /api/v1/insights-pillar/query-analysis`
- `GET /api/v1/insights-pillar/available-content-metadata`
- `POST /api/v1/insights-pillar/validate-content-metadata`
- `GET /api/v1/insights-pillar/analysis-results/{analysis_id}`
- `GET /api/v1/insights-pillar/analysis-visualizations/{analysis_id}`
- `GET /api/v1/insights-pillar/user-analyses`
- `GET /api/v1/insights-pillar/health`

---

## ✅ Success Criteria

- [x] All 15 routes registered successfully
- [x] Routes discoverable from Curator
- [x] Route metadata complete and correct
- [x] Handler methods exist and are callable
- [x] No errors during registration
- [x] Ready for Phase 3 testing

---

**Last Updated:** December 2024  
**Status:** Test Guide Ready


