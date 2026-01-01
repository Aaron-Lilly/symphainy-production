# Experience Bridge Audit

**Date**: November 15, 2025  
**Purpose**: Audit `experience_bridge.py` and realm services for proper Experience Foundation usage

---

## Issues Found

### 🔴 Critical Issues in `experience_bridge.py`

1. **Incorrect Architecture References**:
   - ❌ Still refers to "Experience Realm" in comments and class names
   - ❌ Tries to import `ExperienceManagerService` from `experience.roles.experience_manager.experience_manager_service` (doesn't exist)
   - ❌ Tries to get "FrontendIntegrationService" from DI container (doesn't exist)

2. **Incorrect Access Pattern**:
   - ❌ Tries to instantiate services directly instead of using Experience Foundation SDK
   - ❌ Should use `ExperienceFoundationService.create_frontend_gateway()` etc.

3. **Communication Foundation Registration**:
   - ⚠️ Still registers as "experience" realm in Communication Foundation

---

## Correct Architecture

### ✅ Experience Foundation Pattern

Experience Foundation provides **SDK builders** that realms use to create experience components:

```python
# ✅ CORRECT: Use Experience Foundation SDK
experience_foundation = self.di_container.get_foundation_service("ExperienceFoundationService")

# Create components using SDK builders
frontend_gateway = await experience_foundation.create_frontend_gateway(
    realm_name="journey",
    config={"composes": [...], "api_prefix": "/api/mvp"}
)

session_manager = await experience_foundation.create_session_manager(
    realm_name="journey",
    config={"session_ttl": 3600}
)

user_experience = await experience_foundation.create_user_experience(
    realm_name="journey",
    config={"personalization_enabled": True}
)
```

### ✅ Experience Foundation Services

Services are located in `foundations/experience_foundation/services/`:
- `frontend_gateway_service/` - FrontendGatewayService
- `session_manager_service/` - SessionManagerService
- `user_experience_service/` - UserExperienceService

These are **NOT** accessed directly - they're created via SDK builders.

---

## Realm Services Audit

### ✅ Correct Usage: `mvp_journey_orchestrator_service.py`

**Location**: `backend/journey/services/mvp_journey_orchestrator_service/`

**Status**: ✅ **Correctly uses Experience Foundation SDK**

```python
# ✅ CORRECT: Get Experience Foundation
experience_foundation = self.di_container.get_foundation_service("ExperienceFoundationService")

# ✅ CORRECT: Use SDK builders
self.frontend_gateway = await experience_foundation.create_frontend_gateway(...)
self.user_experience = await experience_foundation.create_user_experience(...)
```

### ❌ Incorrect Usage: `experience_bridge.py`

**Location**: `foundations/communication_foundation/realm_bridges/experience_bridge.py`

**Issues**:
1. ❌ Tries to import from non-existent `experience.roles.experience_manager.experience_manager_service`
2. ❌ Tries to get "FrontendIntegrationService" (doesn't exist)
3. ❌ Should use Experience Foundation SDK instead

---

## Recommended Fixes

### Fix 1: Update `experience_bridge.py`

The bridge should:
1. Use Experience Foundation SDK to create gateways
2. Remove references to "Experience Realm"
3. Update to use Experience Foundation pattern

**Option A: Remove Bridge Entirely**
- Experience Foundation SDK is accessed directly by realms
- No bridge needed (similar to Agentic Foundation)

**Option B: Update Bridge to Use SDK**
- Bridge uses Experience Foundation SDK to create components
- Exposes API endpoints for created components
- Still registers with Communication Foundation

### Fix 2: Update Communication Foundation

**Location**: `foundations/communication_foundation/communication_foundation_service.py`

**Issue**: Still registers as "experience" realm

**Fix**: Either:
- Remove Experience bridge registration (if Option A)
- Update to reflect Experience Foundation (if Option B)

---

## Fixes Applied

### ✅ Fixed: `experience_bridge.py`

**Changes Made:**
1. ✅ Renamed class from `ExperienceRealmBridge` to `ExperienceFoundationBridge`
2. ✅ Updated all references from "Experience Realm" to "Experience Foundation"
3. ✅ Removed incorrect imports (non-existent `ExperienceManagerService` from `experience.roles`)
4. ✅ Updated to use Experience Foundation SDK pattern:
   - Gets `ExperienceFoundationService` from DI container (direct access)
   - Uses SDK methods: `create_frontend_gateway()`, `create_session_manager()`, `create_user_experience()`
5. ✅ Updated API endpoints to reflect SDK access pattern
6. ✅ Removed references to non-existent services

**New API Endpoints:**
- `/api/v1/experience/foundation/health` - Experience Foundation health
- `/api/v1/experience/foundation/capabilities` - Experience Foundation capabilities
- `/api/v1/experience/gateway/create` - Create frontend gateway via SDK
- `/api/v1/experience/session/create` - Create session manager via SDK
- `/api/v1/experience/user-experience/create` - Create user experience via SDK

### ✅ Fixed: `communication_foundation_service.py`

**Changes Made:**
1. ✅ Updated import from `ExperienceRealmBridge` to `ExperienceFoundationBridge`
2. ✅ Updated variable name from `experience_bridge` to `experience_foundation_bridge`
3. ✅ Updated router registration from `realm="experience"` to `realm="experience_foundation"`
4. ✅ Updated metadata from `{"realm": "experience"}` to `{"foundation": "experience"}`

## Summary

### ✅ What's Correct

1. **Realm Services**: `mvp_journey_orchestrator_service.py` correctly uses Experience Foundation SDK ✅
2. **Experience Foundation**: Correctly implemented with SDK builders ✅
3. **Foundation Access**: Direct access pattern is correct ✅
4. **experience_bridge.py**: ✅ **FIXED** - Now uses Experience Foundation SDK
5. **Communication Foundation**: ✅ **FIXED** - Updated to reflect Foundation architecture

### ✅ Architecture Validation

- [x] Experience Foundation accessed via direct DI container access
- [x] SDK builders used to create components
- [x] No references to non-existent "Experience Realm" services
- [x] Bridge uses Experience Foundation SDK pattern
- [x] Communication Foundation registers as "experience_foundation" (not "experience" realm)

---

**Last Updated**: November 15, 2025

