# Container Rebuild & Cleanup Plan

**Date:** 2025-12-04  
**Status:** 🚧 **READY TO EXECUTE**

---

## ✅ **Dependencies Updated**

### **Changes Made:**

1. **pyproject.toml:**
   - ✅ Uncommented `python-docx = "^0.8.11"`
   - ✅ Added `openpyxl = "^3.1.0"`
   - ✅ `reportlab` already present

2. **requirements.txt:**
   - ✅ Uncommented `python-docx==0.8.11`
   - ✅ Added `openpyxl>=3.1.0`
   - ✅ `reportlab` already present

---

## 🐳 **Docker Cleanup & Rebuild Steps**

### **Step 1: Stop Running Containers**

```bash
cd /home/founders/demoversion
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.test.yml down
docker-compose -f symphainy-platform/docker-compose.infrastructure.yml down
```

### **Step 2: Clean Up Docker Fragments**

```bash
# Remove stopped containers
docker container prune -f

# Remove unused images (optional - be careful!)
docker image prune -f

# Remove unused volumes (optional - be careful!)
docker volume prune -f

# Remove unused networks (optional - be careful!)
docker network prune -f

# Full cleanup (removes everything not in use)
docker system prune -f
```

### **Step 3: Rebuild Backend Container**

```bash
cd /home/founders/demoversion
docker-compose -f docker-compose.prod.yml build --no-cache backend
```

### **Step 4: Verify Dependencies Installed**

```bash
# Start backend container
docker-compose -f docker-compose.prod.yml up -d backend

# Check if dependencies are installed
docker exec symphainy-backend-prod python3 -c "import openpyxl; import docx; import reportlab; print('✅ All dependencies installed')"
```

### **Step 5: Rebuild Frontend (if needed)**

```bash
docker-compose -f docker-compose.prod.yml build --no-cache frontend
```

---

## 🧪 **Testing After Rebuild**

### **1. Run File Type Tests**

```bash
cd /home/founders/demoversion/symphainy_source
TEST_MODE=true TEST_SKIP_RESOURCE_CHECK=true pytest tests/e2e/production/test_content_pillar_capabilities.py::TestContentPillarCapabilities::test_file_parsing_excel -v
TEST_MODE=true TEST_SKIP_RESOURCE_CHECK=true pytest tests/e2e/production/test_content_pillar_capabilities.py::TestContentPillarCapabilities::test_file_parsing_pdf -v
TEST_MODE=true TEST_SKIP_RESOURCE_CHECK=true pytest tests/e2e/production/test_content_pillar_capabilities.py::TestContentPillarCapabilities::test_file_parsing_docx -v
TEST_MODE=true TEST_SKIP_RESOURCE_CHECK=true pytest tests/e2e/production/test_content_pillar_capabilities.py::TestContentPillarCapabilities::test_file_parsing_binary_with_copybook -v
```

### **2. Run All File Type Tests**

```bash
TEST_MODE=true TEST_SKIP_RESOURCE_CHECK=true pytest tests/e2e/production/test_content_pillar_capabilities.py -v
```

---

## 📋 **Playwright Test Review**

After file type tests pass, review Playwright tests to ensure they match current implementation:

1. **Check API Endpoints:**
   - Verify semantic APIs (`/api/v1/*-pillar/*`)
   - Check for old endpoints (`/api/mvp/*`, `/api/global/*`)

2. **Check Authentication:**
   - Verify Supabase auth flow
   - Check session management

3. **Check UI Selectors:**
   - Verify component selectors match current frontend
   - Check for renamed components

---

**Status:** ✅ **Dependencies Updated** | 🚧 **Ready for Container Rebuild**



