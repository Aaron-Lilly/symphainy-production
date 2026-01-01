# Frontend API URL Fix - Traefik Routing

**Date:** December 17, 2024  
**Issue:** File upload failing with "Failed to fetch" / `ERR_CONNECTION_REFUSED`

---

## 🔍 Problem

The frontend was trying to connect directly to the backend on port 8000:
- `http://35.215.64.103:8000/api/v1/content-pillar/upload-file`
- `ws://127.0.0.1:8000/api/ws/guide`

However, in the production Docker setup:
- **Backend container does NOT expose port 8000 directly**
- **All traffic must go through Traefik on port 80**
- Traefik routes `/api` to the backend service

---

## ✅ Solution

Updated frontend code to use Traefik route (port 80, no explicit port):

### **1. ContentAPIManager.ts** ✅
**Before:**
```typescript
const uploadURL = 'http://35.215.64.103:8000/api/v1/content-pillar/upload-file';
```

**After:**
```typescript
const apiBaseURL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://35.215.64.103';
const cleanApiBaseURL = apiBaseURL.replace(':8000', '');
const uploadURL = `${cleanApiBaseURL}/api/v1/content-pillar/upload-file`;
```

### **2. useExperienceChat.ts** ✅
**Before:**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://35.215.64.103:8000";
```

**After:**
```typescript
const apiBaseURL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "http://35.215.64.103";
const API_URL = apiBaseURL.replace(':8000', '');
```

### **3. useUnifiedAgentChat.ts** ✅
**Before:**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
```

**After:**
```typescript
const apiBaseURL = process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || (typeof window !== 'undefined' ? window.location.origin : "http://35.215.64.103");
const API_URL = apiBaseURL.replace(':8000', '');
```

---

## 🔧 Changes Made

1. **Removed hardcoded port 8000** from all API URLs
2. **Added environment variable support** (`NEXT_PUBLIC_API_URL` or `NEXT_PUBLIC_BACKEND_URL`)
3. **Automatic port removal** - strips `:8000` if present in environment variable
4. **Traefik-compatible URLs** - uses port 80 (default HTTP port)

---

## 📋 Correct URLs

### **Production (Traefik):**
- ✅ `http://35.215.64.103/api/v1/content-pillar/upload-file` (port 80, default)
- ✅ `ws://35.215.64.103/api/ws/guide` (WebSocket via Traefik)

### **Incorrect (Direct Backend):**
- ❌ `http://35.215.64.103:8000/api/v1/content-pillar/upload-file` (port 8000 not exposed)
- ❌ `ws://127.0.0.1:8000/api/ws/guide` (localhost won't work from browser)

---

## 🚀 Testing

After these changes:
1. **Rebuild frontend container:**
   ```bash
   docker-compose build frontend
   docker-compose up -d frontend
   ```

2. **Verify file upload works:**
   - Navigate to Content Pillar
   - Upload a file
   - Should succeed without "Failed to fetch" error

3. **Verify WebSocket connections:**
   - Check browser console for WebSocket connection success
   - Guide Agent chat should connect

---

## 📝 Environment Variables

You can override the API URL via environment variables:

```bash
# In docker-compose.yml or .env
NEXT_PUBLIC_API_URL=http://35.215.64.103
# or
NEXT_PUBLIC_BACKEND_URL=http://35.215.64.103
```

**Note:** The code automatically removes `:8000` if present, so both work:
- `http://35.215.64.103` ✅
- `http://35.215.64.103:8000` ✅ (will be cleaned to remove :8000)

---

## ✅ Status

- ✅ ContentAPIManager fixed
- ✅ useExperienceChat fixed (both occurrences)
- ✅ useUnifiedAgentChat fixed
- ⚠️ **Frontend container needs to be rebuilt** for changes to take effect

---

**Last Updated:** December 17, 2024







