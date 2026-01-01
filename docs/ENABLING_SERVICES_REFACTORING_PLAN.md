# Enabling Services Refactoring Plan

**Date:** December 15, 2024  
**Status:** 🎯 **STRATEGIC REFACTORING**  
**Goal:** Move realm-specific services to their proper realms, keep only true cross-realm utilities in Business Enablement

---

## 🎯 Executive Summary

**Problem:**
- Business Enablement `enabling_services/` contains ~25 services
- Many are realm-specific (Content, Insights) but live in Business Enablement
- This creates spaghetti code where realms call enabling services directly instead of using proper realm boundaries
- True enabling services should be a small subset of cross-realm utilities (like Smart City services)

**Solution:**
- **Move realm-specific services** to their proper realms
- **Keep only true cross-realm utilities** in Business Enablement
- Each realm owns its domain services (like Smart City owns its services)

---

## 📊 Service Categorization

### ✅ **TRUE ENABLING SERVICES** (Stay in Business Enablement)
**Criteria:** Used by 2+ realms, generic utility functions

**Examples:**
- `validation_engine_service` - Generic validation (all realms need)
- `transformation_engine_service` - Generic data transformation (all realms need)
- `schema_mapper_service` - Generic schema mapping (all realms need)
- `workflow_manager_service` - Generic workflow management (all realms need)
- `notification_service` - Generic notifications (all realms need)
- `audit_trail_service` - Generic audit logging (all realms need)
- `configuration_service` - Generic configuration (all realms need)
- `export_formatter_service` - Generic export formatting (all realms need)

**Location:** `backend/business_enablement/enabling_services/` ✅

---

### ❌ **REALM-SPECIFIC SERVICES** (Move to Respective Realms)
**Criteria:** Used by only 1 realm, domain-specific functionality

#### **Content Realm Services** (Move to `backend/content/services/`)
- `file_parser_service` - Parses files (Content domain)
- `embedding_service` - Creates embeddings from parsed content (Content domain)
- `content_metadata_extraction_service` - Extracts content metadata (Content domain)

**Location:** `backend/content/services/` ✅

#### **Insights Realm Services** (Move to `backend/insights/services/`)
- `data_analyzer_service` - Analyzes data (Insights domain)
- `metrics_calculator_service` - Calculates metrics (Insights domain)
- `visualization_engine_service` - Creates visualizations (Insights domain)
- `apg_processor_service` - Processes APG (Insights domain)
- `insights_generator_service` - Generates insights (Insights domain)
- `data_insights_query_service` - Queries data insights (Insights domain)

**Location:** `backend/insights/services/` ✅

#### **Journey Realm Services** (Move to `backend/journey/services/`)
- `workflow_conversion_service` - Converts workflows (Journey domain)
- `sop_builder_service` - Builds SOPs (Journey domain)
- `coexistence_analysis_service` - Analyzes coexistence (Journey domain)

**Location:** `backend/journey/services/` ✅

#### **Solution Realm Services** (Move to `backend/solution/services/`)
- `roadmap_generation_service` - Generates roadmaps (Solution domain)
- `poc_generation_service` - Generates POCs (Solution domain)
- `strategic_planning_service` - Strategic planning (Solution domain)
- `financial_analysis_service` - Financial analysis (Solution domain)
- `business_metrics_service` - Business metrics (Solution domain)

**Location:** `backend/solution/services/` ✅

#### **Unclear/Generic Services** (Evaluate case-by-case)
- `semantic_enrichment_service` - Could be Content or Insights? Evaluate usage
- `semantic_enrichment_gateway` - Gateway pattern, evaluate usage
- `data_compositor_service` - Generic? Evaluate usage
- `reconciliation_service` - Generic? Evaluate usage
- `report_generator_service` - Generic? Evaluate usage
- `format_composer_service` - Generic? Evaluate usage

**Action:** Analyze usage patterns to determine proper location

---

## 🏗️ Target Architecture

### **Before (Current State):**
```
business_enablement/
└── enabling_services/
    ├── file_parser_service (Content-specific)
    ├── embedding_service (Content-specific)
    ├── content_metadata_extraction_service (Content-specific)
    ├── data_analyzer_service (Insights-specific)
    ├── metrics_calculator_service (Insights-specific)
    ├── visualization_engine_service (Insights-specific)
    ├── validation_engine_service (TRUE enabling - cross-realm)
    └── ... (~25 services total)
```

### **After (Target State):**
```
content/
└── services/
    ├── file_parser_service ✅ (moved from business_enablement)
    ├── embedding_service ✅ (moved from business_enablement)
    └── content_metadata_extraction_service ✅ (moved from business_enablement)

insights/
└── services/
    ├── data_analyzer_service ✅ (moved from business_enablement)
    ├── metrics_calculator_service ✅ (moved from business_enablement)
    ├── visualization_engine_service ✅ (moved from business_enablement)
    └── ... (other Insights-specific services)

business_enablement/
└── enabling_services/
    ├── validation_engine_service ✅ (TRUE enabling - stays)
    ├── transformation_engine_service ✅ (TRUE enabling - stays)
    ├── schema_mapper_service ✅ (TRUE enabling - stays)
    └── ... (~8-10 TRUE enabling services only)
```

---

## 🔄 Migration Strategy

### **Phase 1: Content Realm Services** (Week 1)
1. Create `backend/content/services/` directory
2. Move `file_parser_service` → `backend/content/services/file_parser_service/`
3. Move `embedding_service` → `backend/content/services/embedding_service/`
4. Move `content_metadata_extraction_service` → `backend/content/services/content_metadata_extraction_service/`
5. Update `ContentOrchestrator` to use local services (not `get_enabling_service()`)
6. Update imports across codebase
7. Test Content realm functionality

### **Phase 2: Insights Realm Services** (Week 2)
1. Create `backend/insights/services/` directory
2. Move Insights-specific services
3. Update `InsightsOrchestrator` to use local services
4. Update imports across codebase
5. Test Insights realm functionality

### **Phase 3: Journey & Solution Realm Services** (Week 3)
1. Move Journey-specific services
2. Move Solution-specific services
3. Update orchestrators
4. Test all realm functionality

### **Phase 4: Cleanup** (Week 4)
1. Remove moved services from `business_enablement/enabling_services/`
2. Update documentation
3. Verify only TRUE enabling services remain in Business Enablement
4. Update `get_enabling_service()` pattern to only discover TRUE enabling services

---

## 🎯 Key Principles

1. **Realm Ownership:** Each realm owns its domain services (like Smart City owns its services)
2. **No Cross-Realm Dependencies:** Realms should not call other realms' services directly
3. **True Enabling Services Only:** Business Enablement should only contain services used by 2+ realms
4. **Service Discovery:** Use Curator for TRUE enabling services, direct imports for realm-specific services
5. **Clear Boundaries:** Each realm is self-contained with its own services, orchestrators, agents, and MCP servers

---

## 📋 Migration Checklist

### **Content Realm**
- [ ] Create `backend/content/services/` directory
- [ ] Move `file_parser_service`
- [ ] Move `embedding_service`
- [ ] Move `content_metadata_extraction_service`
- [ ] Update `ContentOrchestrator` imports
- [ ] Update `ContentManagerService` (if exists)
- [ ] Test file upload → parse → embed flow
- [ ] Remove from `business_enablement/enabling_services/`

### **Insights Realm**
- [ ] Create `backend/insights/services/` directory
- [ ] Move `data_analyzer_service`
- [ ] Move `metrics_calculator_service`
- [ ] Move `visualization_engine_service`
- [ ] Move other Insights-specific services
- [ ] Update `InsightsOrchestrator` imports
- [ ] Test insights generation flow
- [ ] Remove from `business_enablement/enabling_services/`

### **Journey Realm**
- [ ] Create `backend/journey/services/` directory
- [ ] Move Journey-specific services
- [ ] Update `JourneyOrchestrator` imports
- [ ] Test journey workflows
- [ ] Remove from `business_enablement/enabling_services/`

### **Solution Realm**
- [ ] Create `backend/solution/services/` directory
- [ ] Move Solution-specific services
- [ ] Update `SolutionOrchestrator` imports
- [ ] Test solution workflows
- [ ] Remove from `business_enablement/enabling_services/`

### **Business Enablement Cleanup**
- [ ] Audit remaining services in `enabling_services/`
- [ ] Verify each is used by 2+ realms
- [ ] Move any remaining realm-specific services
- [ ] Update `get_enabling_service()` documentation
- [ ] Update architecture documentation

---

## 🚨 Breaking Changes

1. **Import Paths:** All imports of moved services will break
2. **Service Discovery:** `get_enabling_service()` will no longer find realm-specific services
3. **Realm Boundaries:** Realms must use direct imports for their own services (not Curator discovery)

---

## ✅ Success Criteria

1. **Content Realm:** Owns all content-related services (file parsing, embeddings, metadata)
2. **Insights Realm:** Owns all insights-related services (data analysis, metrics, visualization)
3. **Business Enablement:** Only contains TRUE enabling services (used by 2+ realms)
4. **No Spaghetti Code:** Realms don't call other realms' services directly
5. **Clear Boundaries:** Each realm is self-contained with clear ownership

---

## 📚 References

- Smart City services as model (self-contained, clear ownership)
- Realm Architecture Refactoring Plan (realm separation strategy)
- Business Enablement Strategic Refactoring Plan (enabling services vision)




