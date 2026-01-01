# Experience API Files Analysis

**Date:** 2025-12-02  
**Status:** 🔍 **ANALYSIS COMPLETE**

---

## Files Overview

### 1. `lib/api/experience.ts` (245 lines)
**Purpose:** Main/current implementation of Experience API functions
- Uses new standardized response types (`ExperienceRoadmapResponse`, `ExperiencePOCResponse`, etc.)
- Direct API calls to backend
- Modern TypeScript interfaces
- **Status:** ✅ **ACTIVE - This is the main implementation**

**Exports:**
- `getSourceFiles()`
- `storeAdditionalContext()`
- `generateExperienceOutputs()`
- `getExperienceSessionState()`
- `analyzeFileForRoadmap()`
- `performComprehensiveAnalysis()`
- `generatePOCProposal()`
- `generatePOCDocument()`
- `getExperienceSession()`
- `createExperienceSession()`
- `getInsightsData()`
- `getOperationsData()`
- Types: `SourceFile`, `AdditionalContextRequest`, `ExperienceSessionState`, `ExperienceRequest`

### 2. `lib/api/experience-adapted.ts` (129 lines)
**Purpose:** Backward compatibility wrapper
- **Imports functions from `experience.ts`**
- Wraps them with type adapters to convert new types to legacy types
- Provides legacy-compatible function signatures
- **Status:** ❓ **UNCLEAR USAGE - Appears to be for backward compatibility**

**Exports:**
- `analyzeFileForRoadmapAdapted()` → wraps `analyzeFileForRoadmap()`
- `generatePOCProposalAdapted()` → wraps `generatePOCProposal()`
- `generatePOCDocumentAdapted()` → wraps `generatePOCDocument()`
- `getExperienceSessionAdapted()` → wraps `getExperienceSession()`
- `createExperienceSessionAdapted()` → wraps `createExperienceSession()`
- `getInsightsDataAdapted()` → wraps `getInsightsData()`
- `getOperationsDataAdapted()` → wraps `getOperationsData()`
- Legacy types: `LegacyRoadmapData`, `LegacyPOCProposal`, etc.

---

## Usage Analysis

### Files Using `experience.ts`:
1. ✅ `components/experience/SourceFilesDisplay.tsx` - Imports `SourceFile` type
2. ✅ `shared/services/experience/core.ts` - Uses functions from `experience.ts`
3. ✅ `shared/services/experience/roadmap-generation.ts` - Uses `analyzeFileForRoadmap`
4. ✅ `shared/services/experience/poc-generation.ts` - Uses `generatePOCProposal`
5. ✅ `shared/services/experience/index.ts` - Re-exports from `experience.ts`

### Files Using `experience-adapted.ts`:
- ❌ **NONE FOUND** - No imports detected

### Services Layer:
- `shared/services/experience/` uses functions directly from `experience.ts`
- No references to `experience-adapted.ts` found

---

## Relationship

```
experience.ts (MAIN)
    ↓
    ├─→ Directly used by services and components
    └─→ experience-adapted.ts (WRAPPER)
            ↓
            └─→ Wraps experience.ts functions with type adapters
            └─→ Provides legacy-compatible interfaces
            └─→ NOT CURRENTLY USED
```

---

## Recommendation

### Option 1: Archive `experience-adapted.ts` (Recommended)
**Rationale:**
- No active usage found
- All components/services use `experience.ts` directly
- Legacy adapters may not be needed if no legacy components exist
- Reduces code duplication and maintenance burden

**Action:**
1. Move `experience-adapted.ts` to `lib/api/archived/experience-adapted.ts`
2. Add deprecation notice if needed
3. Monitor for any breaking changes

### Option 2: Keep Both (If Legacy Support Needed)
**Rationale:**
- If there are legacy components that need the adapted types
- If migration is in progress

**Action:**
1. Document which components should use which file
2. Create migration plan to move all to `experience.ts`
3. Add deprecation warnings to adapted functions

---

## Decision

**Recommendation:** **Archive `experience-adapted.ts`**

**Reasoning:**
1. ✅ No active usage found in codebase
2. ✅ All current code uses `experience.ts` directly
3. ✅ Services layer abstracts the API, so components don't need adapters
4. ✅ Reduces maintenance burden
5. ✅ Can be restored from git history if needed

**If legacy support is needed later:**
- The adapters are in `shared/types/adapters.ts`
- Can recreate the wrapper if needed
- Git history preserves the code

---

## Next Steps

1. ✅ Verify no active usage (DONE - none found)
2. ⏳ Archive `experience-adapted.ts` to `lib/api/archived/`
3. ⏳ Update any documentation references
4. ⏳ Rebuild frontend to verify no breakage






