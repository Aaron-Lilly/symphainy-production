# Experience Foundation Migration Summary

**Date:** November 12, 2025  
**Status:** ✅ Complete

## Overview

Migrated Experience from Realm to Foundation SDK, enabling all realms to compose their own experience "heads" using the Experience SDK.

## What Was Moved

### Services Moved to Experience Foundation
1. **FrontendGatewayService** 
   - From: `backend/experience/services/frontend_gateway_service/`
   - To: `foundations/experience_foundation/services/frontend_gateway_service/`

2. **SessionManagerService**
   - From: `backend/experience/services/session_manager_service/`
   - To: `foundations/experience_foundation/services/session_manager_service/`

3. **UserExperienceService**
   - From: `backend/experience/services/user_experience_service/`
   - To: `foundations/experience_foundation/services/user_experience_service/`

## What Was Created

### Experience Foundation
- **ExperienceFoundationService** - Main foundation service providing SDK
- **SDK Builders:**
  - `FrontendGatewayBuilder` - Creates FrontendGateway instances for realms
  - `SessionManagerBuilder` - Creates SessionManager instances for realms
  - `UserExperienceBuilder` - Creates UserExperience instances for realms

### Updated Components
- **MVP Journey Orchestrator** - Now composes experience "head" using Experience SDK
- **Solution Manager API** - Added `/api/v1/solution/create` and `/api/v1/solution/readiness/solution-driven` endpoints
- **Frontend GuideAgentProvider** - Updated to use Solution Manager API

## Architecture Changes

### Before (Experience as Realm)
```
Frontend → Experience Realm → Experience Services → Business Enablement
```

### After (Experience as Foundation SDK)
```
Frontend → Solution Manager → Journey Manager → Journey composes Experience "head" using SDK
                                                      ↓
                                              Experience Foundation SDK
                                                      ↓
                                              Business Enablement
```

## Key Benefits

1. **All realms can compose experiences** - Journey Realm, Business Enablement, etc. can all use Experience SDK
2. **No separate Experience Realm needed** - Experience is now a foundation capability
3. **Solution-driven architecture** - Frontend → Solution → Journey → Experience → Business Enablement
4. **Cleaner separation** - Experience is a capability, not a realm

## Breaking Changes

- Experience Realm services moved to Experience Foundation
- Imports changed from `backend.experience.services.*` to `foundations.experience_foundation.services.*`
- MVP Journey Orchestrator now composes experience instead of discovering via Curator

## Migration Notes

- Old Experience Realm services archived in `backend/experience/archive/2025-11-12_experience_foundation_migration/`
- API routers in `backend/experience/api/` remain (they're protocol adapters, not realm services)
- Experience Manager service may still exist but is no longer the primary way to access experience capabilities

