# Production Readiness Checklist

**Date:** December 2024  
**Status:** ⚠️ **NOT READY** - Multiple issues identified during deployment attempt  
**Purpose:** Comprehensive checklist of issues to resolve before production deployment

---

## 🎯 **Executive Summary**

During our deployment attempt, we encountered multiple issues that indicate the codebase is not fully production-ready. This checklist documents all issues found and provides actionable steps to resolve them.

---

## 📋 **Category 1: Build & Compilation Issues**

### **1.1 Frontend Build Issues** ⚠️ **CRITICAL**

#### **Issue 1.1.1: Test Files Included in Production Build**
- **Problem:** TypeScript test files (`TestUtils.tsx`) are being compiled during production build
- **Error:** `Property 'toHaveTextContent' does not exist on type 'JestMatchers<any>'`
- **Impact:** Build fails
- **Status:** ⚠️ Partially fixed (temporarily ignoring TypeScript errors)
- **Action Required:**
  - [ ] Properly exclude test files from Next.js build
  - [ ] Update `tsconfig.json` to exclude `**/testing/**/*`, `**/__tests__/**/*`
  - [ ] Update `.dockerignore` to exclude test directories
  - [ ] Update `next.config.js` to exclude test files from webpack compilation
  - [ ] Remove temporary `ignoreBuildErrors: true` after proper exclusion

#### **Issue 1.1.2: package-lock.json Excluded from Docker Build**
- **Problem:** `.dockerignore` was excluding `package-lock.json`
- **Error:** `npm ci` requires package-lock.json
- **Impact:** Frontend build fails
- **Status:** ✅ Fixed
- **Action Required:**
  - [x] Verify fix is in place
  - [ ] Test that `npm ci` works without errors

#### **Issue 1.1.3: Peer Dependency Conflicts**
- **Problem:** npm peer dependency conflicts during `npm ci`
- **Error:** Dependency resolution conflicts
- **Impact:** Build fails
- **Status:** ⚠️ Workaround applied (`--legacy-peer-deps`)
- **Action Required:**
  - [ ] Review and fix peer dependency conflicts properly
  - [ ] Update package.json to resolve conflicts
  - [ ] Remove `--legacy-peer-deps` workaround once conflicts resolved

#### **Issue 1.1.4: Deprecated npm Flag**
- **Problem:** Dockerfile used `--only=production` (deprecated)
- **Impact:** Build warnings/errors
- **Status:** ✅ Fixed (changed to install all deps for build)
- **Action Required:**
  - [x] Verify fix is in place

---

### **1.2 Backend Build Issues** ⚠️ **CRITICAL**

#### **Issue 1.2.1: Missing Dependencies**
- **Problem:** `gotrue` module not found
- **Error:** `ModuleNotFoundError: No module named 'gotrue'`
- **Impact:** Backend fails to start
- **Status:** ⚠️ Partially fixed (added to pyproject.toml, but poetry.lock needs update)
- **Action Required:**
  - [ ] Verify `gotrue` is in `pyproject.toml`
  - [ ] Regenerate `poetry.lock` file
  - [ ] Test that `gotrue` imports successfully
  - [ ] Consider migrating to `supabase_auth` (gotrue is deprecated)

#### **Issue 1.2.2: Poetry Lock File Out of Sync**
- **Problem:** `poetry.lock` doesn't match `pyproject.toml` after adding dependencies
- **Error:** `pyproject.toml changed significantly since poetry.lock was last generated`
- **Impact:** Build fails
- **Status:** ⚠️ Workaround applied (regenerate during build)
- **Action Required:**
  - [ ] Regenerate `poetry.lock` file properly (run `poetry lock` locally)
  - [ ] Commit updated `poetry.lock` to repository
  - [ ] Remove workaround from Dockerfile (remove `poetry lock || true`)

#### **Issue 1.2.3: Poetry Not Available on VM**
- **Problem:** Poetry command not found when trying to run locally on VM
- **Impact:** Cannot update dependencies on VM
- **Status:** ⚠️ Not critical (Poetry runs in Docker)
- **Action Required:**
  - [ ] Document that Poetry is only needed in Docker
  - [ ] OR install Poetry on VM if needed for local development
  - [ ] Update deployment documentation

---

## 📋 **Category 2: Code Organization & Build Context**

### **2.1 Non-Production Files in Build Context** ⚠️ **HIGH PRIORITY**

#### **Issue 2.1.1: Documentation Files in Build**
- **Problem:** Documentation, test files, and non-production scripts included in Docker build context
- **Impact:** 
  - Larger build context
  - Slower builds
  - Potential security issues (secrets in docs)
  - Test files causing build errors
- **Action Required:**
  - [ ] Create `.dockerignore` files for both frontend and backend
  - [ ] Exclude: `docs/`, `tests/`, `*.md`, `archive/`, `scripts/` (non-deployment)
  - [ ] Exclude: `.git/`, `.github/`, IDE files
  - [ ] Exclude: Development config files
  - [ ] Verify build context size reduction

#### **Issue 2.1.2: Test Files in Production Code**
- **Problem:** Test utilities and test files are being imported/compiled
- **Impact:** Build errors, larger production bundles
- **Action Required:**
  - [ ] Move test utilities to separate directory
  - [ ] Update imports to exclude test files
  - [ ] Ensure test files are not imported in production code
  - [ ] Add build-time validation to catch test file imports

#### **Issue 2.1.3: Archive/Development Files**
- **Problem:** Archive folders and development files in repository
- **Impact:** Cluttered codebase, potential confusion
- **Action Required:**
  - [ ] Move archive folders to `.archive/` or separate branch
  - [ ] Move development-only scripts to `scripts/dev/`
  - [ ] Document what should/shouldn't be in production build

---

## 📋 **Category 3: Configuration & Environment**

### **3.1 Missing Production Configuration** ⚠️ **CRITICAL**

#### **Issue 3.1.1: GCS Configuration Missing**
- **Problem:** `GCS_PROJECT_ID` and `GCS_BUCKET_NAME` only in `development.env`, not in production config
- **Error:** `GCS project_id is required but not configured`
- **Impact:** Backend fails to start (PublicWorksFoundationService initialization fails)
- **Current State:**
  - `GCS_PROJECT_ID` in `config/development.env`
  - `GCS_BUCKET_NAME` in `config/development.env`
  - `GCS_CREDENTIALS_JSON` in `.env.secrets` (with "type", "project_id", "private_key_id")
- **Action Required:**
  - [ ] Add `GCS_PROJECT_ID` to `config/production.env`
  - [ ] Add `GCS_BUCKET_NAME` to `config/production.env`
  - [ ] Verify `GCS_CREDENTIALS_JSON` format in `.env.secrets` is correct
  - [ ] Test GCS adapter initialization with production config
  - [ ] Document GCS setup requirements

#### **Issue 3.1.2: Environment Variable Organization**
- **Problem:** Configuration scattered across multiple files
- **Impact:** Hard to track what's needed for production
- **Action Required:**
  - [ ] Audit all environment variables used in production
  - [ ] Document required vs optional variables
  - [ ] Create `config/production.env.example` with all required variables
  - [ ] Verify `.env.secrets` has all required secrets
  - [ ] Create configuration validation script

#### **Issue 3.1.3: Configuration File Locations**
- **Problem:** Unclear which config files are used when
- **Action Required:**
  - [ ] Document configuration file precedence
  - [ ] Verify production uses `config/production.env`
  - [ ] Ensure `.env.secrets` is loaded correctly
  - [ ] Test configuration loading in production environment

---

## 📋 **Category 4: Docker & Infrastructure**

### **4.1 Network Configuration** ⚠️ **CRITICAL**

#### **Issue 4.1.1: Network Isolation**
- **Problem:** Infrastructure services on `symphainy-platform_smart_city_net`, application services on `symphainy-network`
- **Error:** Services can't communicate
- **Impact:** Backend can't connect to infrastructure (Consul, Redis, ArangoDB, etc.)
- **Status:** ⚠️ Partially fixed (backend connected to both networks)
- **Action Required:**
  - [ ] Standardize on single network for all services
  - [ ] Update `docker-compose.prod.yml` to use same network as infrastructure
  - [ ] OR update infrastructure compose to use external network
  - [ ] Document network architecture
  - [ ] Test service-to-service communication
  - [ ] Verify all services can reach each other

#### **Issue 4.1.2: Network Name Consistency**
- **Problem:** Network names differ between infrastructure and application compose files
- **Impact:** Services can't find each other
- **Action Required:**
  - [ ] Use consistent network naming
  - [ ] Document network strategy
  - [ ] Create network setup script or documentation

#### **Issue 4.1.3: Service Discovery**
- **Problem:** Services need to discover each other by name
- **Action Required:**
  - [ ] Verify service names are consistent
  - [ ] Test DNS resolution between containers
  - [ ] Document service naming conventions

---

### **4.2 Docker Compose Configuration**

#### **Issue 4.2.1: Obsolete Version Attribute**
- **Problem:** `version: '3.8'` is obsolete in docker-compose
- **Warning:** `the attribute 'version' is obsolete`
- **Impact:** Warnings (not blocking)
- **Action Required:**
  - [ ] Remove `version` from `docker-compose.prod.yml`
  - [ ] Remove `version` from `docker-compose.infrastructure.yml`
  - [ ] Test that compose files still work

#### **Issue 4.2.2: Health Check Configuration**
- **Problem:** Health checks may be too strict or not configured correctly
- **Action Required:**
  - [ ] Review health check timeouts and intervals
  - [ ] Verify health check endpoints exist
  - [ ] Test health check behavior
  - [ ] Adjust start_period if services need more time

---

## 📋 **Category 5: Dependencies & Package Management**

### **5.1 Python Dependencies**

#### **Issue 5.1.1: Poetry Lock File Management**
- **Problem:** Lock file gets out of sync with pyproject.toml
- **Action Required:**
  - [ ] Establish process for updating dependencies
  - [ ] Always commit `poetry.lock` after dependency changes
  - [ ] Add pre-commit hook to verify lock file is up to date
  - [ ] Document dependency update process

#### **Issue 5.1.2: Missing Dependencies**
- **Problem:** Dependencies added to code but not to pyproject.toml
- **Action Required:**
  - [ ] Audit all imports in production code
  - [ ] Verify all imported packages are in pyproject.toml
  - [ ] Add missing dependencies
  - [ ] Create import validation script

#### **Issue 5.1.3: Deprecated Dependencies**
- **Problem:** `gotrue` is deprecated, should use `supabase_auth`
- **Action Required:**
  - [ ] Migrate from `gotrue` to `supabase_auth`
  - [ ] Update all imports
  - [ ] Test Supabase authentication still works
  - [ ] Remove `gotrue` dependency

---

### **5.2 Node.js Dependencies**

#### **Issue 5.2.1: Peer Dependency Conflicts**
- **Problem:** npm peer dependency conflicts
- **Action Required:**
  - [ ] Review and resolve peer dependency conflicts
  - [ ] Update package.json to compatible versions
  - [ ] Remove `--legacy-peer-deps` workaround
  - [ ] Test build without workaround

#### **Issue 5.2.2: package-lock.json Management**
- **Problem:** Lock file needs to be committed and up to date
- **Action Required:**
  - [ ] Ensure `package-lock.json` is committed
  - [ ] Verify lock file is up to date
  - [ ] Document npm dependency update process

---

## 📋 **Category 6: Service Initialization & Startup**

### **6.1 Foundation Service Initialization**

#### **Issue 6.1.1: GCS Adapter Required but Not Configured**
- **Problem:** FileManagementAbstraction requires GCS adapter, but GCS not configured
- **Error:** `GCS adapter is required for FileManagementAbstraction but failed to initialize`
- **Impact:** PublicWorksFoundationService fails to initialize
- **Action Required:**
  - [ ] Configure GCS for production (see Issue 3.1.1)
  - [ ] OR make GCS optional and use Supabase file management only
  - [ ] Test file management with chosen approach
  - [ ] Document file storage strategy

#### **Issue 6.1.2: Adapter Initialization Order**
- **Problem:** Adapters must be created before abstractions
- **Impact:** If adapter creation fails, abstractions can't be created
- **Action Required:**
  - [ ] Review initialization order
  - [ ] Add better error handling for missing adapters
  - [ ] Consider making some adapters optional
  - [ ] Add initialization validation

#### **Issue 6.1.3: Health and Telemetry Abstractions**
- **Problem:** Health and telemetry abstractions are None when adapters fail
- **Impact:** Foundation service fails to initialize
- **Action Required:**
  - [ ] Ensure health and telemetry adapters are created successfully
  - [ ] Add fallback mechanisms if adapters fail
  - [ ] Improve error messages

---

## 📋 **Category 7: Documentation & Process**

### **7.1 Deployment Documentation**

#### **Issue 7.1.1: Missing Production Setup Steps**
- **Problem:** Deployment guide doesn't cover all configuration requirements
- **Action Required:**
  - [ ] Document GCS setup requirements
  - [ ] Document network configuration
  - [ ] Document all required environment variables
  - [ ] Create pre-deployment validation checklist
  - [ ] Add troubleshooting section for common issues

#### **Issue 7.1.2: Configuration Examples**
- **Problem:** No clear examples of production configuration
- **Action Required:**
  - [ ] Create `config/production.env.example`
  - [ ] Create `.env.secrets.example` (with placeholders, no real secrets)
  - [ ] Document what each variable does
  - [ ] Add validation scripts

---

## 📋 **Category 8: Testing & Validation**

### **8.1 Pre-Deployment Validation**

#### **Issue 8.1.1: No Pre-Deployment Checks**
- **Problem:** Issues discovered during deployment, not before
- **Action Required:**
  - [ ] Create pre-deployment validation script
  - [ ] Check all required config files exist
  - [ ] Validate environment variables
  - [ ] Check network connectivity
  - [ ] Verify dependencies are installed
  - [ ] Test Docker builds locally before deployment

#### **Issue 8.1.2: Production Build Testing**
- **Problem:** Production builds not tested before deployment
- **Action Required:**
  - [ ] Test production Docker builds locally
  - [ ] Verify all services start correctly
  - [ ] Test health checks
  - [ ] Run smoke tests against production build

---

## 🎯 **Priority Action Items**

### **🔴 CRITICAL - Must Fix Before Production:**

1. **GCS Configuration** (Issue 3.1.1)
   - Add GCS_PROJECT_ID and GCS_BUCKET_NAME to production config
   - Verify GCS_CREDENTIALS_JSON format

2. **Network Configuration** (Issue 4.1.1)
   - Standardize on single network
   - Ensure all services can communicate

3. **Test Files Exclusion** (Issue 1.1.1, 2.1.2)
   - Properly exclude test files from production builds
   - Remove temporary workarounds

4. **Dependency Management** (Issue 1.2.1, 1.2.2)
   - Regenerate poetry.lock properly
   - Verify all dependencies are in pyproject.toml

### **🟡 HIGH PRIORITY - Should Fix Soon:**

5. **Build Context Cleanup** (Issue 2.1.1)
   - Create comprehensive .dockerignore files
   - Reduce build context size

6. **Configuration Documentation** (Issue 3.1.2, 7.1.1)
   - Document all required configuration
   - Create example files

7. **Pre-Deployment Validation** (Issue 8.1.1)
   - Create validation scripts
   - Test builds locally

### **🟢 MEDIUM PRIORITY - Nice to Have:**

8. **Dependency Updates** (Issue 5.1.3, 5.2.1)
   - Migrate from deprecated packages
   - Resolve peer dependency conflicts

9. **Documentation** (Issue 7.1.2)
   - Improve deployment documentation
   - Add troubleshooting guides

---

## 📝 **Recommended Workflow**

### **Phase 1: Critical Fixes (Do First)**
1. Fix GCS configuration
2. Fix network configuration
3. Fix test file exclusions
4. Fix dependency issues

### **Phase 2: Build Optimization**
1. Clean up build context
2. Optimize Dockerfiles
3. Reduce build time

### **Phase 3: Validation & Testing**
1. Create validation scripts
2. Test production builds locally
3. Update documentation

### **Phase 4: Final Deployment**
1. Run pre-deployment checks
2. Deploy to production
3. Verify all services
4. Run smoke tests

---

## ✅ **Completion Criteria**

Before attempting production deployment again, ensure:

- [ ] All CRITICAL issues resolved
- [ ] All HIGH PRIORITY issues resolved
- [ ] Pre-deployment validation script passes
- [ ] Production build tested locally
- [ ] All configuration documented
- [ ] Network connectivity verified
- [ ] Health checks passing
- [ ] Smoke tests passing

---

**Last Updated:** December 2024  
**Next Review:** After Phase 1 completion

