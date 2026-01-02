# Active Codebase Structure

**Date:** January 2025  
**Purpose:** Define what constitutes the "active" production codebase vs archived/legacy code

---

## Active Production Codebase

The active production codebase consists of the following directories:

### 1. Core Platform (`symphainy-platform/`)

#### **Backend Services** (`backend/`)
- ✅ `backend/smart_city/` - Smart City realm services
- ✅ `backend/content/` - Content realm services
- ✅ `backend/insights/` - Insights realm services
- ✅ `backend/journey/` - Journey realm services
- ✅ `backend/solution/` - Solution realm services
- ✅ `backend/business_enablement/` - Business Enablement realm services
- ✅ `backend/api/` - API routers and endpoints

#### **Foundation Services** (`foundations/`)
- ✅ `foundations/public_works_foundation/` - Infrastructure abstractions and adapters
- ✅ `foundations/curator_foundation/` - Capability registry
- ✅ `foundations/communication_foundation/` - Inter-realm communication
- ✅ `foundations/agentic_foundation/` - Agent SDK and capabilities
- ✅ `foundations/experience_foundation/` - Experience SDK and gateway

#### **Base Classes** (`bases/`)
- ✅ `bases/foundation_service_base.py` - Foundation service base
- ✅ `bases/realm_service_base.py` - Realm service base
- ✅ `bases/orchestrator_base.py` - Orchestrator base
- ✅ `bases/smart_city_role_base.py` - Smart City role base
- ✅ `bases/mixins/` - Mixin classes
- ✅ `bases/protocols/` - Protocol definitions

#### **Platform Infrastructure** (`platform_infrastructure/`)
- ✅ `platform_infrastructure/infrastructure/platform_gateway.py` - Platform Gateway

#### **Utilities** (`utilities/`)
- ✅ `utilities/configuration/` - Configuration management
- ✅ `utilities/logging/` - Logging utilities
- ✅ `utilities/error/` - Error handling utilities
- ✅ `utilities/api_routing/` - API routing utilities

#### **Configuration** (`config/`)
- ✅ `config/` - Platform configuration files

#### **Main Entry Point** (`main.py`)
- ✅ `main.py` - Platform entry point

#### **Active Scripts** (`scripts/active/`)
- ✅ `scripts/active/` - Production-ready scripts (per scripts/README.md)

---

### 2. Frontend Application (`symphainy-frontend/`)

- ✅ `symphainy-frontend/` - React/Next.js frontend application
- ✅ All frontend code is considered active

---

### 3. Test Suite (`tests/`)

- ✅ `tests/unit/` - Unit tests
- ✅ `tests/integration/` - Integration tests
- ✅ `tests/e2e/` - End-to-end tests
- ✅ `tests/contracts/` - Contract tests
- ✅ `tests/performance/` - Performance tests
- ✅ `tests/fixtures/` - Test fixtures
- ✅ `tests/utils/` - Test utilities

---

## Archived/Non-Active Code

The following are **NOT** part of the active codebase:

### Archived Directories
- ❌ `archive/` - Explicitly archived code
- ❌ `tests_old_archive/` - Old test archive
- ❌ `symphainy-platform/archive/` - Platform-specific archive
- ❌ `symphainy-platform/docs/111125_archive/` - Old documentation archive

### Archived Scripts
- ❌ `archive/ad_hoc_tests/` - Ad hoc test scripts (moved from root)
- ❌ `archive/utility_scripts/` - Utility scripts (moved from root)
- ❌ `symphainy-platform/scripts/archive/` - Archived scripts

### Root-Level Files (Archived)
- ❌ `test_*.py` - Moved to `archive/ad_hoc_tests/`
- ❌ `test_*.sh` - Moved to `archive/ad_hoc_tests/`
- ❌ `check_*.sh` - Moved to `archive/utility_scripts/`
- ❌ `monitor_*.sh` - Moved to `archive/utility_scripts/`
- ❌ `restart_*.sh` - Moved to `archive/utility_scripts/`
- ❌ `run_*.sh` - Moved to `archive/utility_scripts/` (except CI/CD scripts)
- ❌ `verify_*.sh` - Moved to `archive/utility_scripts/`

### Legacy/Experimental Code
- ❌ Any code in `archive/` directories
- ❌ Experimental branches or features not merged to main
- ❌ Deprecated services or modules

---

## Development Guidelines

### Adding New Code
1. **Backend Services** → `symphainy-platform/backend/{realm}/`
2. **Foundation Services** → `symphainy-platform/foundations/{foundation}/`
3. **Base Classes** → `symphainy-platform/bases/`
4. **Tests** → `tests/{category}/`
5. **Scripts** → `symphainy-platform/scripts/evaluate/` (then promote to `active/`)

### Archiving Code
1. Move to appropriate `archive/` directory
2. Add README.md explaining why it was archived
3. Update this document if needed
4. Commit with clear message

### Code Review Focus
- Focus reviews on active codebase only
- Ignore archived code unless specifically needed
- Ensure new code follows active codebase patterns

---

## Maintenance

This document should be updated when:
- New directories are added to active codebase
- Code is archived
- Structure changes significantly

---

**Last Updated:** January 2025

