# Phase 1 Security Integration: Testing Guide

**Date:** December 2024  
**Status:** 📋 **TESTING GUIDE CREATED**

---

## 🎯 Testing Overview

This guide provides step-by-step instructions for testing Phase 1 Security Integration:
1. ForwardAuth endpoint validation
2. Tenant-aware routing
3. Tenant isolation

---

## 📋 Prerequisites

1. **Platform Running:**
   ```bash
   # Start infrastructure
   cd symphainy-platform
   docker-compose -f docker-compose.infrastructure.yml up -d
   
   # Start backend
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Supabase Token:**
   - Get a valid Supabase JWT token from your Supabase project
   - Or use the login endpoint to get a token:
     ```bash
     curl -X POST http://localhost/api/auth/login \
       -H "Content-Type: application/json" \
       -d '{"email": "your@email.com", "password": "your_password"}'
     ```

3. **Environment Variables:**
   ```bash
   export SYMPHAINY_API_URL="http://localhost/api"
   export SYMPHAINY_API_TOKEN="your_supabase_jwt_token"  # Optional for some tests
   ```

---

## 🧪 Test 1: ForwardAuth Endpoint - Valid Token

**Purpose:** Verify ForwardAuth endpoint validates valid tokens and returns user context headers.

**Steps:**
1. Get a valid Supabase JWT token
2. Call the ForwardAuth endpoint with the token
3. Verify response is 200 OK
4. Verify headers contain X-User-Id, X-Tenant-Id, etc.

**Command:**
```bash
curl -X GET http://localhost/api/auth/validate-token \
  -H "Authorization: Bearer YOUR_SUPABASE_JWT_TOKEN" \
  -v
```

**Expected Response:**
- Status: 200 OK
- Headers:
  - `X-User-Id: <user_id>`
  - `X-Tenant-Id: <tenant_id>`
  - `X-User-Roles: <roles>`
  - `X-User-Permissions: <permissions>`
  - `X-Auth-Origin: supabase_validation`

**Automated Test:**
```bash
python3 scripts/test_phase1_security_integration.py
# (with SYMPHAINY_API_TOKEN set)
```

---

## 🧪 Test 2: ForwardAuth Endpoint - Invalid Token

**Purpose:** Verify ForwardAuth endpoint rejects invalid tokens.

**Steps:**
1. Call ForwardAuth endpoint with invalid token
2. Verify response is 401 Unauthorized

**Command:**
```bash
curl -X GET http://localhost/api/auth/validate-token \
  -H "Authorization: Bearer invalid_token_12345" \
  -v
```

**Expected Response:**
- Status: 401 Unauthorized
- Body: "Unauthorized: Invalid token"

**Automated Test:**
```bash
python3 scripts/test_phase1_security_integration.py
# (runs automatically, no token needed)
```

---

## 🧪 Test 3: ForwardAuth Endpoint - Missing Token

**Purpose:** Verify ForwardAuth endpoint rejects requests without tokens.

**Steps:**
1. Call ForwardAuth endpoint without Authorization header
2. Verify response is 401 Unauthorized

**Command:**
```bash
curl -X GET http://localhost/api/auth/validate-token \
  -v
```

**Expected Response:**
- Status: 401 Unauthorized
- Body: "Unauthorized: Missing or invalid token"

**Automated Test:**
```bash
python3 scripts/test_phase1_security_integration.py
# (runs automatically, no token needed)
```

---

## 🧪 Test 4: Tenant-Aware Routing

**Purpose:** Verify tenant context is extracted and propagated to backend services.

**Steps:**
1. Make API request with valid token
2. Verify request includes tenant context
3. Verify tenant validation occurs
4. Verify tenant context propagated to services

**Command:**
```bash
curl -X GET http://localhost/api/v1/content-pillar/health \
  -H "Authorization: Bearer YOUR_SUPABASE_JWT_TOKEN" \
  -v
```

**Expected Behavior:**
- Request goes through Traefik ForwardAuth
- Traefik adds X-Tenant-Id, X-User-Id headers
- FrontendGatewayService extracts tenant context
- Tenant validation occurs
- Request proceeds to backend service

**Check Logs:**
```bash
# Check backend logs for tenant context
docker logs symphainy-backend-prod | grep -i tenant

# Check Traefik logs for ForwardAuth
docker logs symphainy-traefik | grep -i forwardauth
```

---

## 🧪 Test 5: Tenant Isolation

**Purpose:** Verify tenant isolation is enforced.

**Steps:**
1. Create test data for Tenant A
2. Attempt to access Tenant A data with Tenant B token
3. Verify access is denied

**Note:** This test requires:
- Two different tenant accounts
- Test data in the system
- Proper tenant isolation implementation in services

**Manual Test:**
1. Login as Tenant A user → get token A
2. Login as Tenant B user → get token B
3. Create resource with token A
4. Attempt to access resource with token B
5. Verify 403 Forbidden or "Tenant access denied"

---

## 🧪 Automated Test Suite

**Run All Tests:**
```bash
cd /home/founders/demoversion/symphainy_source
python3 scripts/test_phase1_security_integration.py
```

**With Token:**
```bash
export SYMPHAINY_API_TOKEN="your_supabase_jwt_token"
python3 scripts/test_phase1_security_integration.py
```

**Expected Output:**
```
======================================================================
Phase 1: Security Integration - Test Suite
======================================================================

🧪 Test 1: ForwardAuth with Valid Token
   ✅ Success: Token validated
   Headers: {...}

🧪 Test 2: ForwardAuth with Invalid Token
   ✅ Success: Invalid token correctly rejected (401)

🧪 Test 3: ForwardAuth with Missing Token
   ✅ Success: Missing token correctly rejected (401)

🧪 Test 4: Tenant-Aware Routing
   ✅ Success: Tenant context detected

======================================================================
Test Summary
======================================================================
✅ PASS: forwardauth_valid_token
✅ PASS: forwardauth_invalid_token
✅ PASS: forwardauth_missing_token
✅ PASS: tenant_aware_routing

Results: 4/4 tests passed
```

---

## 🔍 Troubleshooting

### **ForwardAuth Returns 503 Service Unavailable**

**Issue:** Security Guard service not available

**Solution:**
1. Check if Security Guard is running:
   ```bash
   docker logs symphainy-backend-prod | grep -i security
   ```
2. Verify Security Guard initialized:
   ```bash
   curl http://localhost/api/health
   ```
3. Check Security Guard logs for errors

### **ForwardAuth Returns 401 for Valid Token**

**Issue:** Token validation failing

**Solution:**
1. Verify token is valid Supabase JWT:
   ```bash
   # Decode JWT (check structure)
   echo "YOUR_TOKEN" | cut -d. -f2 | base64 -d
   ```
2. Check Supabase configuration:
   - Verify SUPABASE_URL is set
   - Verify SUPABASE_ANON_KEY is set
3. Check AuthAbstraction logs:
   ```bash
   docker logs symphainy-backend-prod | grep -i auth
   ```

### **Tenant Context Not Propagated**

**Issue:** X-Tenant-Id header not reaching services

**Solution:**
1. Verify Traefik middleware is applied:
   ```bash
   # Check Traefik dashboard
   curl http://localhost:8080/api/http/routers
   ```
2. Verify FrontendGatewayService extracts headers:
   ```bash
   docker logs symphainy-backend-prod | grep -i "X-Tenant-Id"
   ```
3. Check Traefik labels:
   ```bash
   docker inspect symphainy-backend-prod | grep -i traefik
   ```

### **Traefik Not Routing to Backend**

**Issue:** Requests not reaching backend

**Solution:**
1. Check Traefik router configuration:
   ```bash
   curl http://localhost:8080/api/http/routers/backend
   ```
2. Verify backend service is healthy:
   ```bash
   curl http://localhost/api/health
   ```
3. Check Traefik service discovery:
   ```bash
   docker logs symphainy-traefik | grep -i backend
   ```

---

## 📊 Test Results Template

```markdown
## Phase 1 Security Integration - Test Results

**Date:** [Date]
**Tester:** [Name]
**Environment:** [Local/Staging/Production]

### Test Results

| Test | Status | Notes |
|------|--------|-------|
| ForwardAuth - Valid Token | ✅ PASS / ❌ FAIL | |
| ForwardAuth - Invalid Token | ✅ PASS / ❌ FAIL | |
| ForwardAuth - Missing Token | ✅ PASS / ❌ FAIL | |
| Tenant-Aware Routing | ✅ PASS / ❌ FAIL | |
| Tenant Isolation | ✅ PASS / ❌ FAIL | |

### Issues Found

1. [Issue description]
   - Impact: [High/Medium/Low]
   - Status: [Open/Resolved]

### Next Steps

- [ ] Fix identified issues
- [ ] Re-run tests
- [ ] Proceed to Phase 2
```

---

## ✅ Success Criteria

Phase 1 is considered complete when:

- ✅ ForwardAuth endpoint validates valid tokens (200 OK)
- ✅ ForwardAuth endpoint rejects invalid tokens (401)
- ✅ ForwardAuth endpoint rejects missing tokens (401)
- ✅ Tenant context extracted from headers
- ✅ Tenant validation occurs before routing
- ✅ Tenant context propagated to services
- ✅ Tenant isolation enforced (if test data available)

---

## 🚀 Next Steps

After successful testing:

1. **Document any issues found**
2. **Fix identified problems**
3. **Re-run tests to verify fixes**
4. **Proceed to Phase 2: Client Config Foundation**

---

**Last Updated:** December 2024  
**Status:** Ready for Testing




