# Next Steps - Remaining Tasks

**Date**: November 14, 2025  
**Status**: Planning

---

## ✅ Recently Completed

1. ✅ **Document Processing Refactoring** - Complete
   - Refactored `DocumentIntelligenceAbstraction` to coordinate multiple adapters
   - Updated `FileParserService` to use abstraction (no fallback)
   - Exposed via Platform Gateway

2. ✅ **Architectural Pattern Enforcement** - Complete
   - Removed fallback code from `FileParserService`
   - Made abstraction required (fail fast if not available)

3. ✅ **Adapter Organization** - Complete
   - Archived duplicate/unused adapters (14 files)
   - Moved future abstractions (4 files)

---

## 🔄 Immediate Next Steps

### 1. Clean Up Legacy Code in FileParserService

**Status**: Ready to do  
**Priority**: Medium

The following methods are no longer used but still present:
- `_parse_by_type()` - Routes to format-specific parsers
- `_parse_pdf()` - Direct pdfplumber usage
- `_parse_word()` - Direct python-docx usage
- `_parse_html()` - Direct beautifulsoup usage
- `_parse_image()` - Direct pytesseract usage
- `_parse_cobol()` - Direct COBOL processing
- `_extract_file_metadata()` - Direct metadata extraction

**Action**: Remove these methods once abstraction is proven stable in production.

---

### 2. Future Roadmap Decisions

**Status**: Needs decision  
**Priority**: Medium

From `ADAPTER_REVIEW_AND_RECOMMENDATIONS.md`, we need decisions on:

#### Workflow/BPMN Adapters
- **Files**: `bpmn_adapter.py`, `bpmn_processing_adapter.py`, `workflow_visualization_adapter.py`
- **Question**: Will workflow processing evolve to hosted solutions?
- **If YES**: Create workflow processing abstractions and use adapters
- **If NO**: Archive workflow adapters

#### SOP Adapters
- **Files**: `sop_enhancement_adapter.py`, `sop_parsing_adapter.py`
- **Question**: Will SOP processing evolve to hosted solutions?
- **If YES**: Create SOP processing abstractions and use adapters
- **If NO**: Archive SOP adapters

#### Financial/Strategic Planning Adapters
- **Files**: `standard_financial_adapter.py`, `standard_strategic_planning_adapter.py`
- **Note**: Already have HuggingFace versions in `future_abstractions/` - indicates hosted solutions are planned
- **Action**: Keep standard adapters, create abstractions when ready to integrate HuggingFace versions

---

### 3. Protocol Migrations (34 remaining)

**Status**: In progress  
**Priority**: High (for abstractions we're fixing)

From `COMPLETE_ARCHITECTURAL_CHANGES.md`:

**High Priority** (used by abstractions we're fixing):
- `authentication_protocol.py`
- `authorization_protocol.py`
- `telemetry_protocol.py` ✅ (already done)
- `health_protocol.py` ✅ (already done)
- `messaging_protocol.py`
- `event_management_protocol.py`
- `task_management_protocol.py` ✅ (already done)
- `content_metadata_protocol.py` ✅ (already done)
- `content_schema_protocol.py` ✅ (already done)
- `content_insights_protocol.py` ✅ (already done)
- `policy_protocol.py` ✅ (already done)
- `alert_management_protocol.py` ✅ (already done)
- `tracing_protocol.py`
- `visualization_protocol.py`
- `business_metrics_protocol.py`

**Medium Priority** (remaining ~19 files):
- All other protocol files in `abstraction_contracts/`

---

### 4. Dependency Injection Fixes (6 remaining)

**Status**: In progress  
**Priority**: High

From `COMPLETE_ARCHITECTURAL_CHANGES.md`:

**Remaining Abstractions** (need DI fixes):
- `TaskManagementAbstraction` ✅ (already done)
- `WorkflowOrchestrationAbstraction` ✅ (already done)
- `ResourceAllocationAbstraction` ✅ (already done)
- `KnowledgeDiscoveryAbstraction` ✅ (already done)
- `KnowledgeGovernanceAbstraction` ✅ (already done)
- `AGUICommunicationAbstraction` - Need to check
- `ToolStorageAbstraction` - Need to check

**Note**: Many of these may already be done. Need to verify.

---

### 5. Registry Refactoring (1 remaining)

**Status**: In progress  
**Priority**: High

From `COMPLETE_ARCHITECTURAL_CHANGES.md`:

**Remaining Registry**:
- `ServiceDiscoveryRegistry` - Special case (creates Consul adapter internally)

**Note**: This is a special case because Consul adapter is created by the registry. May need different approach.

---

### 6. Architectural Pattern Documentation

**Status**: Needs documentation  
**Priority**: Medium

Document the architectural patterns:
- Business enablement services use Smart City SOA APIs, not direct infrastructure adapters
- Adapters are thin wrappers around raw technology
- Content-specific operations belong in abstractions, not adapters
- **NEW**: For future swap-ability (local libraries → hosted solutions), use abstractions with adapters

---

## Recommended Order

1. **Verify remaining DI fixes** - Check which abstractions still need DI fixes
2. **Complete protocol migrations** - For abstractions we're fixing
3. **Handle ServiceDiscoveryRegistry** - Special case registry
4. **Make roadmap decisions** - Workflow/BPMN, SOP, Financial adapters
5. **Clean up legacy code** - Remove unused methods from FileParserService
6. **Document patterns** - Create architectural pattern documentation

---

**Next Action**: Should we start with verifying which abstractions still need DI fixes, or make the roadmap decisions first?




