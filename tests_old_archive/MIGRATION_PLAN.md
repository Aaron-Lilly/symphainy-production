# Production Readiness Migration Plan

**Date:** December 2024  
**Purpose:** Systematic plan to address all production readiness issues

---

## 🔄 **1. Migrate from gotrue to supabase_auth**

### **Current State:**
- `gotrue.errors.AuthError` imported in 3 files:
  - `supabase_adapter.py`
  - `supabase_file_management_adapter.py`
  - `supabase_metadata_adapter.py`
- `gotrue = "^2.0.0"` in `pyproject.toml`
- Supabase client version: 2.17.0

### **Migration Strategy:**
The Supabase Python client (v2.17.0+) handles auth internally. We should:
1. Use `supabase.lib.client_options.ClientOptions` exceptions or catch generic `Exception` from auth operations
2. The supabase client's `auth` module handles errors internally
3. Remove `gotrue` dependency entirely

### **Implementation:**
- Replace `from gotrue.errors import AuthError` with proper exception handling
- Use `Exception` or create a custom `SupabaseAuthError` wrapper
- Test that auth operations still work correctly

---

## 📋 **2. Configuration Management Enhancement**

### **Current State:**
- `UnifiedConfigurationManager` exists with layered architecture
- Loads: secrets → environment → business_logic → defaults
- `DIContainerService` uses `UnifiedConfigurationManager`

### **Enhancement Needed:**
1. **Production Config Validation:**
   - Add validation method to check all required production variables
   - Create `validate_production_config()` method
   - Return clear error messages for missing config

2. **Configuration Precedence Documentation:**
   - Document which layer overrides which
   - Add logging for config source (which layer provided value)
   - Create config audit trail

3. **GCS Configuration:**
   - Add `GCS_PROJECT_ID` and `GCS_BUCKET_NAME` to `config/production.env`
   - Verify `GCS_CREDENTIALS_JSON` format in `.env.secrets`

### **Implementation:**
- Enhance `UnifiedConfigurationManager` with validation
- Add production config validation script
- Document configuration architecture

---

## 🌐 **3. Docker Network Architecture**

### **Current State:**
- Infrastructure: `symphainy-platform_smart_city_net` (from `docker-compose.infrastructure.yml`)
- Application: `symphainy_source_symphainy-network` (from `docker-compose.prod.yml`)
- Backend currently connected to both (workaround)

### **Proposed Architecture:**
**Single Network Strategy (Recommended):**
- All services on `symphainy-platform_smart_city_net`
- Infrastructure compose creates network
- Application compose uses external network
- Consistent naming: `symphainy-platform_smart_city_net`

### **Implementation:**
1. Update `docker-compose.prod.yml`:
   - Remove `symphainy-network` creation
   - Use `smart_city_net` as external network
   - Connect all services to `smart_city_net`

2. Document network architecture:
   - Why single network
   - Service discovery patterns
   - Network isolation strategy (if needed later)

---

## 🔍 **4. Curator Foundation Service Discovery**

### **Current State:**
- `CuratorFoundationService` registers services with service discovery
- Uses `ServiceDiscoveryAbstraction` from Public Works Foundation
- Consul adapter handles actual registration

### **Verification Needed:**
1. **Service Registration:**
   - Verify services register with correct network addresses
   - Check service discovery uses container names (DNS)
   - Ensure health checks are registered

2. **Network Integration:**
   - Verify Curator can discover services on `smart_city_net`
   - Test service lookup by name
   - Verify health check endpoints are accessible

### **Implementation:**
- Review `CuratorFoundationService.register_service()`
- Verify service discovery uses container names
- Test service discovery in Docker network context
- Document service discovery patterns

---

## 🏥 **5. Docker Health Check Updates**

### **Current State:**
- Backend health check: `curl -f http://localhost:8000/health`
- Frontend health check: `curl -f http://localhost:3000`
- Health endpoint exists: `/health` in `main.py`

### **Issues:**
- `curl` may not be available in all images
- Health checks should use native tools when possible
- Python images can use `python -c` or `wget`

### **Proposed Solution:**
**Backend (Python):**
```yaml
healthcheck:
  test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s  # Increased for foundation initialization
```

**Frontend (Node.js):**
```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000"] || exit 1
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### **Implementation:**
- Update health checks in `docker-compose.prod.yml`
- Test health checks work correctly
- Adjust `start_period` based on actual startup time

---

## 📦 **6. Adapter Initialization**

### **Current State:**
- All adapters are required (no optional adapters)
- Initialization order: adapters → abstractions
- If adapter fails, foundation fails

### **User Feedback:**
- Adapters are infrastructure exposure - all required
- Lazy loading might add complexity without much gain
- Keep current approach but improve error messages

### **Enhancement:**
- Better error messages when adapters fail
- Clear indication of which adapter failed and why
- Document initialization order and dependencies

---

## ✅ **Implementation Order**

1. **Phase 1: Critical Fixes**
   - [ ] Migrate gotrue → supabase_auth
   - [ ] Add GCS config to production.env
   - [ ] Standardize Docker network
   - [ ] Update health checks

2. **Phase 2: Enhancements**
   - [ ] Enhance configuration validation
   - [ ] Verify Curator service discovery
   - [ ] Document network architecture

3. **Phase 3: Testing**
   - [ ] Test all changes locally
   - [ ] Verify production build
   - [ ] Run smoke tests

---

**Next Steps:** Start with Phase 1 critical fixes.

