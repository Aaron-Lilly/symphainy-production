# Server Disconnection During File Upload - Analysis

**Date:** December 2024  
**Status:** 🔍 **INVESTIGATION IN PROGRESS**

---

## ✅ Findings

### **1. Backend is Healthy**
- ✅ Backend container: `Up 11 minutes (healthy)`
- ✅ Health endpoint: Returns 200 OK
- ✅ Login endpoint: Works correctly (200 OK)
- ✅ Direct backend test: Works (200 OK when testing `172.18.0.14:8000` directly)

### **2. Traefik Configuration**
- ✅ Timeout config updated: `readTimeout: 300s`, `writeTimeout: 300s`
- ✅ Config loaded in Traefik container
- ✅ Traefik restarted to apply changes

### **3. Issue Location**
- ❌ **Traefik is dropping connections** during file uploads
- ❌ Requests through Traefik (`35.215.64.103`) fail with "Empty reply from server"
- ✅ Direct backend requests (`172.18.0.14:8000`) work correctly

---

## 🔍 Root Cause Hypothesis

### **ForwardAuth Middleware Issue**

The ForwardAuth middleware (`supabase-auth`) is configured to validate tokens before routing requests. For file uploads:

1. **Request Flow:**
   - Client → Traefik → ForwardAuth (`/api/auth/validate-token`) → Backend
   - ForwardAuth validates token → Returns 200 OK with headers
   - Traefik forwards request to backend → Backend processes file upload

2. **Potential Issues:**
   - ForwardAuth might be timing out during token validation
   - ForwardAuth might be trying to read the multipart/form-data body (it shouldn't)
   - ForwardAuth request might be causing a loop or deadlock
   - Backend might be slow to respond to ForwardAuth, causing Traefik to timeout

3. **Evidence:**
   - curl test shows: `100 Continue` → waits 7 seconds → `Empty reply from server`
   - This suggests ForwardAuth is being called but timing out
   - Direct backend test works (bypasses ForwardAuth)

---

## 🔧 Solutions to Try

### **Option 1: Add Timeout to ForwardAuth**
```yaml
supabase-auth:
  forwardAuth:
    address: "http://backend:8000/api/auth/validate-token"
    # Add timeout configuration
    # (Note: Traefik ForwardAuth doesn't have explicit timeout config)
```

**Status:** ⚠️ Traefik ForwardAuth doesn't support explicit timeout configuration

### **Option 2: Bypass ForwardAuth for File Uploads**
Create a separate router for file uploads that doesn't use ForwardAuth:

```yaml
# In docker-compose.prod.yml
- "traefik.http.routers.backend-upload.rule=PathPrefix(`/api/v1/content-pillar/upload-file`)"
- "traefik.http.routers.backend-upload.middlewares=backend-chain@file"  # No ForwardAuth
- "traefik.http.routers.backend-upload.priority=200"  # Higher than backend router
```

**Status:** ✅ **RECOMMENDED** - File uploads can validate auth in the handler itself

### **Option 3: Optimize ForwardAuth Endpoint**
- Make `/api/auth/validate-token` faster
- Add caching for token validation
- Skip unnecessary processing

**Status:** ⚠️ May not solve the root cause

### **Option 4: Use Header-Based Auth for File Uploads**
- Skip ForwardAuth for file uploads
- Validate token in the upload handler itself
- Extract user context from token in handler

**Status:** ✅ **RECOMMENDED** - More flexible and faster

---

## 📋 Next Steps

1. ✅ **Test Option 2:** Create separate router for file uploads without ForwardAuth
2. ✅ **Test Option 4:** Validate auth in upload handler instead of ForwardAuth
3. ⚠️ **Monitor:** Check if ForwardAuth is actually the issue (add logging)
4. ⚠️ **Fallback:** If ForwardAuth is the issue, consider disabling it for file uploads

---

## 🧪 Test Results

### **Direct Backend Test:**
```bash
curl -X POST http://172.18.0.14:8000/api/v1/content-pillar/upload-file -F "file=@/dev/null"
# Result: 200 OK (works correctly)
```

### **Through Traefik Test:**
```bash
curl -X POST http://35.215.64.103/api/v1/content-pillar/upload-file -F "file=@/dev/null"
# Result: Empty reply from server (disconnects after 7 seconds)
```

### **ForwardAuth Test:**
```bash
curl -X GET http://35.215.64.103/api/auth/validate-token -H "Authorization: Bearer test"
# Result: 401 Unauthorized (works correctly, but returns quickly)
```

---

## 💡 Recommendation

**Create a separate router for file uploads that bypasses ForwardAuth:**

1. File uploads are typically authenticated via token in the handler
2. ForwardAuth adds latency and complexity
3. File upload handlers can validate tokens themselves
4. This is a common pattern for file upload endpoints

**Implementation:**
- Add router with higher priority (200) for `/api/v1/*/upload-file`
- Use `backend-chain@file` middleware (no ForwardAuth)
- Validate auth in the upload handler itself

