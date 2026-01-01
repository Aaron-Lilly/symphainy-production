# Platform Routing: Parallel Implementation Plan

**Date:** December 2024  
**Status:** 🚀 Ready for Parallel Implementation  
**Strategy:** Strangler Fig Pattern - Build new alongside old, switch when ready

---

## 🎯 Strategy Overview

**Approach:** Parallel implementation with feature flag
- ✅ Keep existing routing working (zero downtime)
- ✅ Build new routing layer alongside
- ✅ Test new approach with subset of routes
- ✅ Gradually migrate routes
- ✅ Switch over when validated
- ✅ Remove old code after switch

**Benefits:**
- Zero risk to production
- Can test incrementally
- Easy rollback if issues
- No "big bang" switchover

---

## 📋 Implementation Phases

### **Phase 1: Infrastructure Setup (Week 1)**

**Goal:** Set up new routing infrastructure without breaking existing

**Tasks:**

1. **Add Feature Flag**
   ```python
   # In FrontendGatewayService
   self.use_discovered_routing = config.get("routing.use_discovered_routing", False)
   ```

2. **Initialize APIRoutingUtility**
   ```python
   # In FrontendGatewayService.__init__()
   self.api_routing_utility = APIRoutingUtility(self.di_container)
   await self.api_routing_utility.initialize()
   ```

3. **Add Route Discovery Method**
   ```python
   async def _discover_routes_from_curator(self):
       """Discover routes from Curator (new approach)."""
       try:
           curator = await self.get_curator_api()
           routes = await curator.discover_routes(status="active")
           
           # Build route registry
           for route in routes:
               if route.get("handler_service") == "FrontendGatewayService":
                   handler = getattr(self, route["handler"], None)
                   if handler:
                       await self.api_routing_utility.register_route(
                           method=HTTPMethod(route["method"]),
                           path=route["path"],
                           handler=handler,
                           pillar=route.get("pillar", ""),
                           realm=route.get("realm", "")
                       )
       except Exception as e:
           self.logger.warning(f"⚠️ Route discovery failed: {e}, using hardcoded routing")
   ```

4. **Add New Routing Method**
   ```python
   async def _route_via_discovery(self, request: Dict[str, Any]) -> Dict[str, Any]:
       """Route using discovered routes (new approach)."""
       endpoint = request.get("endpoint", "")
       method = request.get("method", "POST")
       
       # Find route
       route_info = await self.api_routing_utility.find_route(
           method=HTTPMethod(method),
           path=endpoint
       )
       
       if not route_info:
           return {"success": False, "error": "Route not found"}
       
       # Execute route with middleware
       user_context = self._build_user_context(request)
       response = await self.api_routing_utility.route_request(
           method=HTTPMethod(method),
           path=endpoint,
           request_data=request.get("params", {}),
           user_context=user_context
       )
       
       return response.body
   ```

**Success Criteria:**
- ✅ Feature flag added
- ✅ APIRoutingUtility initialized
- ✅ Route discovery method added
- ✅ New routing method added
- ✅ **Existing routing still works** (no changes to current code)

---

### **Phase 2: Route Registration (Week 1-2)**

**Goal:** Register routes with Curator (doesn't affect existing routing)

**Tasks:**

1. **Update Service Registration**
   ```python
   # In each enabling service's initialize()
   await curator.register_route({
       "route_id": f"{service_name}_{capability_name}",
       "path": "/api/v1/content-pillar/upload-file",
       "method": "POST",
       "pillar": "content-pillar",
       "realm": "business_enablement",
       "service_name": service_name,
       "capability_name": capability_name,
       "handler": "handle_upload_file_request",
       "handler_service": "FrontendGatewayService",
       "description": "...",
       "version": "v1",
       "defined_by": "business_enablement_realm"
   })
   ```

2. **Start with One Pillar (Content)**
   - Register all Content Pillar routes
   - Test route registration
   - Verify routes appear in Curator

3. **Gradually Add Other Pillars**
   - Register Insights Pillar routes
   - Register Operations Pillar routes
   - Register Business Outcomes Pillar routes

**Success Criteria:**
- ✅ All routes registered with Curator
- ✅ Routes discoverable via `curator.discover_routes()`
- ✅ **Existing routing still works** (registration doesn't affect routing)

---

### **Phase 3: Parallel Testing (Week 2-3)**

**Goal:** Test new routing with subset of routes

**Tasks:**

1. **Add Route-Level Feature Flag**
   ```python
   # In route metadata
   {
       "route_id": "...",
       "path": "/api/v1/content-pillar/upload-file",
       "use_discovered_routing": True,  # Enable for this route
       ...
   }
   ```

2. **Update route_frontend_request() with Feature Flag**
   ```python
   async def route_frontend_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
       """Route request (supports both old and new approaches)."""
       
       # Check if new routing is enabled globally
       if self.use_discovered_routing:
           # Try new routing first
           try:
               result = await self._route_via_discovery(request)
               if result.get("success") is not False:
                   return result
           except Exception as e:
               self.logger.warning(f"⚠️ Discovered routing failed: {e}, falling back to hardcoded")
       
       # Fall back to existing hardcoded routing (always works)
       return await self._route_via_hardcoded(request)
   ```

3. **Test with One Route**
   - Enable new routing for `/api/v1/content-pillar/upload-file`
   - Test both old and new approaches
   - Compare results
   - Verify middleware works

4. **Gradually Enable More Routes**
   - Enable new routing for all Content Pillar routes
   - Test thoroughly
   - Enable for Insights Pillar
   - Test thoroughly
   - Continue for other pillars

**Success Criteria:**
- ✅ New routing works for subset of routes
- ✅ Old routing still works (fallback)
- ✅ Results match between old and new
- ✅ Middleware works correctly

---

### **Phase 4: Full Migration (Week 3-4)**

**Goal:** Switch all routes to new approach

**Tasks:**

1. **Enable New Routing Globally**
   ```python
   # In config
   routing.use_discovered_routing = True
   ```

2. **Monitor and Validate**
   - Monitor error rates
   - Compare performance
   - Verify all routes work
   - Check middleware execution

3. **Keep Old Code as Fallback**
   ```python
   # Keep _route_via_hardcoded() as emergency fallback
   # Can be re-enabled via feature flag if needed
   ```

**Success Criteria:**
- ✅ All routes use new routing
- ✅ Performance equivalent or better
- ✅ Error rates same or lower
- ✅ All tests pass

---

### **Phase 5: Cleanup (Week 4-5)**

**Goal:** Remove old routing code after validation period

**Tasks:**

1. **Wait for Validation Period**
   - Run new routing in production for 1-2 weeks
   - Monitor for issues
   - Collect metrics

2. **Remove Old Code**
   ```python
   # Remove _route_via_hardcoded() method
   # Remove hardcoded if/elif chains
   # Remove feature flag (always use new routing)
   ```

3. **Update Documentation**
   - Update routing documentation
   - Remove references to old approach

**Success Criteria:**
- ✅ Old routing code removed
- ✅ Codebase cleaner (95% reduction)
- ✅ All tests pass
- ✅ Documentation updated

---

## 🔄 Parallel Run Architecture

### **Request Flow (Parallel Mode)**

```
Request
  ↓
Universal Router
  ↓
FrontendGatewayService.route_frontend_request()
  ↓
Feature Flag Check
  ├─→ use_discovered_routing = True
  │     ↓
  │   _route_via_discovery()
  │     ↓
  │   APIRoutingUtility.find_route()
  │     ↓
  │   Curator.discover_routes()
  │     ↓
  │   Handler (via APIRoutingUtility)
  │
  └─→ use_discovered_routing = False (fallback)
        ↓
      _route_via_hardcoded()
        ↓
      Hardcoded if/elif chains
        ↓
      Handler (direct call)
```

### **Gradual Migration Path**

```
Week 1: Infrastructure setup (both work)
Week 2: Register routes (old still works)
Week 3: Test new routing (old as fallback)
Week 4: Enable new routing (old as fallback)
Week 5: Remove old code (new only)
```

---

## 🧪 Testing Strategy

### **1. Unit Tests**

**Test new routing in isolation:**
```python
async def test_route_discovery():
    """Test route discovery from Curator."""
    routes = await curator.discover_routes(pillar="content-pillar")
    assert len(routes) > 0
    assert routes[0]["path"] == "/api/v1/content-pillar/upload-file"
```

### **2. Integration Tests**

**Test routing with real requests:**
```python
async def test_parallel_routing():
    """Test both old and new routing produce same results."""
    request = {
        "endpoint": "/api/v1/content-pillar/upload-file",
        "method": "POST",
        "params": {...}
    }
    
    # Test old routing
    old_result = await gateway._route_via_hardcoded(request)
    
    # Test new routing
    new_result = await gateway._route_via_discovery(request)
    
    # Results should match
    assert old_result == new_result
```

### **3. A/B Testing**

**Test in production with feature flag:**
```python
# Enable for 10% of requests
if random.random() < 0.1:
    use_discovered_routing = True
else:
    use_discovered_routing = False
```

### **4. Shadow Mode**

**Run new routing in parallel, log differences:**
```python
# Run both, compare results
old_result = await gateway._route_via_hardcoded(request)
new_result = await gateway._route_via_discovery(request)

if old_result != new_result:
    logger.warning(f"⚠️ Routing mismatch: {old_result} vs {new_result}")
```

---

## 🚨 Rollback Plan

### **If Issues Detected:**

1. **Immediate Rollback**
   ```python
   # Disable new routing via feature flag
   routing.use_discovered_routing = False
   ```

2. **Investigate Issue**
   - Check logs
   - Compare old vs new results
   - Fix issue in new routing

3. **Re-enable After Fix**
   ```python
   # Re-enable after fix
   routing.use_discovered_routing = True
   ```

### **Emergency Fallback**

**Keep old code until fully validated:**
- Old routing always available as fallback
- Can switch instantly via feature flag
- No code changes needed for rollback

---

## 📊 Success Metrics

### **Before Switchover:**
- ✅ All routes registered with Curator
- ✅ Route discovery works
- ✅ New routing produces same results as old
- ✅ Performance equivalent or better
- ✅ All tests pass

### **After Switchover:**
- ✅ 95% code reduction (4000+ lines → ~200 lines)
- ✅ Zero routing-related errors
- ✅ New routes can be added without code changes
- ✅ Service mesh ready

---

## 🎯 Implementation Checklist

### **Phase 1: Infrastructure**
- [ ] Add feature flag
- [ ] Initialize APIRoutingUtility
- [ ] Add route discovery method
- [ ] Add new routing method
- [ ] Verify existing routing still works

### **Phase 2: Registration**
- [ ] Register Content Pillar routes
- [ ] Register Insights Pillar routes
- [ ] Register Operations Pillar routes
- [ ] Register Business Outcomes Pillar routes
- [ ] Verify routes in Curator

### **Phase 3: Testing**
- [ ] Test one route with new routing
- [ ] Test all Content Pillar routes
- [ ] Test all Insights Pillar routes
- [ ] Test all Operations Pillar routes
- [ ] Test all Business Outcomes Pillar routes
- [ ] Compare old vs new results

### **Phase 4: Migration**
- [ ] Enable new routing globally
- [ ] Monitor error rates
- [ ] Monitor performance
- [ ] Validate all routes work

### **Phase 5: Cleanup**
- [ ] Wait for validation period
- [ ] Remove old routing code
- [ ] Update documentation
- [ ] Celebrate 95% code reduction! 🎉

---

## 📚 Related Documentation

- [Platform Routing Strategy Assessment](./PLATFORM_ROUTING_STRATEGY_ASSESSMENT.md)
- [Routing Ownership Strategy](./11-12/ROUTING_OWNERSHIP_STRATEGY.md)
- [APIRoutingUtility](../symphainy-platform/utilities/api_routing/api_routing_utility.py)

---

**Last Updated:** December 2024  
**Status:** Ready for Parallel Implementation


