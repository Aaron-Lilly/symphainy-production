# Unified Data Mapping System Design

**Date:** January 2025  
**Status:** 🎯 **Design Document**  
**Purpose:** Design unified data mapping system supporting both unstructured→structured and structured→structured mappings with integrated data quality validation

---

## 🎯 Overview

This document extends the original data mapping plan to support **two primary use cases**:

1. **Unstructured → Structured Mapping** (License PDF → Excel)
   - Extract fields from unstructured documents (PDFs, Word)
   - Map to structured target schemas
   - Provide citations and confidence scores

2. **Structured → Structured Mapping** (Legacy Policy Records → New Data Model)
   - Map between structured data formats (JSONL, CSV, Excel)
   - Validate data quality at record level
   - Provide cleanup actions for source file teams

**Key Innovation:** Unified system that handles both scenarios with integrated data quality validation and actionable cleanup recommendations.

---

## 📊 Use Case Scenarios

### Use Case 1: License PDF → Excel Template

**Flow:**
1. User uploads license PDF (source)
2. User uploads Excel template (target)
3. System extracts fields from PDF using LLM
4. System maps extracted fields to Excel columns
5. System populates Excel with extracted data
6. System provides citations and confidence scores

**Output:**
- Populated Excel file
- Mapping report with citations
- Confidence scores per field

---

### Use Case 2: Legacy Policy Records → New Data Model

**Flow:**
1. User uploads legacy policy records (JSONL from binary parser)
2. User uploads/selects target data model (Excel, JSON schema)
3. System maps source schema → target schema using embeddings
4. System validates each record against target schema
5. System identifies quality issues per record:
   - Missing required fields
   - Invalid data types
   - Invalid values (out of range, format issues)
   - Data inconsistencies
6. System generates cleanup actions report
7. System generates mapped output (only valid records OR all records with quality flags)

**Output:**
- Mapped data file (valid records)
- Data quality report (per record)
- Cleanup actions report (actionable recommendations)
- Quality metrics (pass rate, common issues)

---

## 🏗️ Architecture Design

### Architectural Pattern: Solution → Journey → Realm Services

Following the Content Pillar pattern:
- **Solution Realm**: Entry point (Insights Solution Orchestrator)
- **Journey Realm**: Workflows (Insights Journey Orchestrator with Data Mapping Workflow)
- **Insights Realm**: Services (Field Extraction, Data Quality Validation, Data Transformation)

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA MAPPING SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │    Insights Solution Orchestrator (Solution Realm)       │  │
│  │  - Entry point for insights operations                   │  │
│  │  - Platform correlation (workflow_id, lineage, telemetry) │  │
│  │  - Routes to Insights Journey Orchestrator               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│  ┌───────────────────────▼───────────────────────┐             │
│  │  Insights Journey Orchestrator (Journey Realm)│             │
│  │  - Data Mapping Workflow                       │             │
│  │  - Coordinates mapping process                  │             │
│  │  - Handles both use cases                       │             │
│  └───────────────────────────────────────────────┘             │
│                           │                                      │
│        ┌──────────────────┼──────────────────┐                  │
│        │                  │                  │                  │
│  ┌─────▼─────┐    ┌───────▼──────┐   ┌─────▼─────┐           │
│  │  Schema   │    │   Semantic    │   │   Data    │           │
│  │ Extraction│    │   Matching    │   │  Quality  │           │
│  │  Agent    │    │    Agent      │   │  Agent    │           │
│  │(Insights) │    │  (Insights)   │   │(Insights) │           │
│  └───────────┘    └───────────────┘   └───────────┘           │
│        │                  │                  │                  │
│        └──────────────────┼──────────────────┘                  │
│                           │                                      │
│  ┌───────────────────────▼───────────────────────┐             │
│  │         Insights Realm Services                │             │
│  │                                                 │             │
│  │  ┌──────────────────────────────────────────┐ │             │
│  │  │  Field Extraction Service                │ │             │
│  │  │  - Extract fields from unstructured      │ │             │
│  │  │  - LLM + regex patterns                  │ │             │
│  │  └──────────────────────────────────────────┘ │             │
│  │                                                 │             │
│  │  ┌──────────────────────────────────────────┐ │             │
│  │  │  Data Quality Validation Service         │ │             │
│  │  │  - Record-level validation               │ │             │
│  │  │  - Quality issue identification          │ │             │
│  │  │  - Cleanup action generation             │ │             │
│  │  └──────────────────────────────────────────┘ │             │
│  │                                                 │             │
│  │  ┌──────────────────────────────────────────┐ │             │
│  │  │  Data Transformation Service             │ │             │
│  │  │  - Apply mapping rules                   │ │             │
│  │  │  - Transform data formats                │ │             │
│  │  │  - Generate output files                 │ │             │
│  │  └──────────────────────────────────────────┘ │             │
│  └───────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Component Specifications

### 1. Insights Solution Orchestrator (Solution Realm)

**Location:** `backend/solution/services/insights_solution_orchestrator_service/`

**Responsibilities:**
- Entry point for insights operations
- Platform correlation (workflow_id, lineage, telemetry)
- Routes to Insights Journey Orchestrator
- Orchestrates platform services (Security Guard, Traffic Cop, Conductor, Post Office, Nurse)

**Pattern:** Similar to `DataSolutionOrchestratorService` but for insights operations

---

### 2. Insights Journey Orchestrator (Journey Realm)

**Location:** `backend/journey/orchestrators/insights_journey_orchestrator/`

**Responsibilities:**
- Orchestrates insights workflows (data mapping, analysis, etc.)
- Composes Insights Realm Services
- Manages workflow state and transitions
- Routes to appropriate services based on operation type

**Key Workflow:** Data Mapping Workflow

**Location:** `backend/journey/orchestrators/insights_journey_orchestrator/workflows/data_mapping_workflow.py`

**Responsibilities:**
- Orchestrate end-to-end mapping process
- Handle both use cases (unstructured→structured, structured→structured)
- Coordinate agents and services
- Track lineage and citations
- Generate quality reports

**Key Methods:**

```python
class DataMappingWorkflow:
    """
    Unified data mapping workflow supporting both use cases.
    """
    
    async def execute(
        self,
        source_file_id: str,
        target_file_id: str,
        mapping_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute data mapping workflow.
        
        Handles both:
        1. Unstructured → Structured (PDF → Excel)
        2. Structured → Structured (JSONL → Excel)
        
        Returns:
        {
            "success": bool,
            "mapping_id": str,
            "mapping_type": "unstructured_to_structured" | "structured_to_structured",
            "mapping_rules": [...],
            "mapped_data": {...},
            "data_quality": {
                "overall_quality_score": 0.85,
                "records_valid": 950,
                "records_invalid": 50,
                "records_total": 1000,
                "quality_issues": [...],
                "cleanup_actions": [...]
            },
            "output_file_id": str,
            "citations": [...],
            "confidence_scores": {...},
            "metadata": {...}
        }
        """
        # Step 1: Detect mapping type
        mapping_type = await self._detect_mapping_type(source_file_id, target_file_id)
        
        # Step 2: Extract schemas
        source_schema = await self._extract_source_schema(source_file_id, mapping_type)
        target_schema = await self._extract_target_schema(target_file_id)
        
        # Step 3: Get embeddings for semantic matching
        source_embeddings = await self._get_source_embeddings(source_file_id)
        target_embeddings = await self._get_target_embeddings(target_file_id)
        
        # Step 4: Generate mapping rules
        mapping_rules = await self._generate_mapping_rules(
            source_schema, target_schema,
            source_embeddings, target_embeddings
        )
        
        # Step 5: Extract/Transform data based on mapping type
        if mapping_type == "unstructured_to_structured":
            # Extract fields from unstructured source
            extracted_data = await self._extract_fields_from_unstructured(
                source_file_id, mapping_rules
            )
        else:
            # Transform structured source data
            extracted_data = await self._get_structured_source_data(source_file_id)
        
        # Step 6: Validate data quality (for structured→structured)
        if mapping_type == "structured_to_structured":
            quality_results = await self._validate_data_quality(
                extracted_data, target_schema, mapping_rules
            )
        else:
            quality_results = None
        
        # Step 7: Transform data to target format
        transformed_data = await self._transform_data(
            extracted_data, mapping_rules, target_schema
        )
        
        # Step 8: Generate output file
        output_file_id = await self._generate_output_file(
            transformed_data, target_schema, quality_results
        )
        
        # Step 9: Generate cleanup actions (if quality issues found)
        cleanup_actions = None
        if quality_results and quality_results.get("has_issues"):
            cleanup_actions = await self._generate_cleanup_actions(quality_results)
        
        # Step 10: Track lineage
        await self._track_mapping_lineage(
            source_file_id, target_file_id, mapping_id, quality_results
        )
        
        return {
            "success": True,
            "mapping_id": mapping_id,
            "mapping_type": mapping_type,
            "mapping_rules": mapping_rules,
            "mapped_data": transformed_data,
            "data_quality": quality_results,
            "cleanup_actions": cleanup_actions,
            "output_file_id": output_file_id,
            "citations": citations,
            "confidence_scores": confidence_scores
        }
```

---

### 2. Data Quality Validation Service (Insights Realm Service)

**Location:** `backend/insights/services/data_quality_validation_service/`

**Responsibilities:**
- Validate records against target schema
- Identify quality issues per record
- Generate quality metrics
- Generate cleanup action recommendations

**Key Methods:**

```python
class DataQualityValidationService(RealmServiceBase):
    """
    Validates data quality and generates cleanup actions.
    
    Use cases:
    - Legacy policy records → New data model validation
    - Any structured→structured mapping with quality requirements
    """
    
    async def validate_records(
        self,
        records: List[Dict[str, Any]],
        target_schema: Dict[str, Any],
        mapping_rules: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate records against target schema.
        
        Args:
            records: List of source records to validate
            target_schema: Target schema definition
            mapping_rules: Mapping rules (source field → target field)
            user_context: User context
        
        Returns:
        {
            "success": True,
            "validation_results": [
                {
                    "record_id": "record_1",
                    "record_index": 0,
                    "is_valid": False,
                    "quality_score": 0.65,
                    "issues": [
                        {
                            "field": "policy_number",
                            "issue_type": "missing_required",
                            "severity": "error",
                            "message": "Required field 'policy_number' is missing",
                            "source_field": "POLICY-NUMBER",
                            "target_field": "policy_number"
                        },
                        {
                            "field": "premium_amount",
                            "issue_type": "invalid_type",
                            "severity": "error",
                            "message": "Field 'premium_amount' must be numeric, got: 'ABC'",
                            "source_value": "ABC",
                            "expected_type": "number"
                        },
                        {
                            "field": "issue_date",
                            "issue_type": "invalid_format",
                            "severity": "warning",
                            "message": "Date format should be YYYY-MM-DD, got: '12/31/2024'",
                            "source_value": "12/31/2024",
                            "expected_format": "YYYY-MM-DD"
                        }
                    ],
                    "missing_fields": ["policy_number", "policyholder_name"],
                    "invalid_fields": ["premium_amount"],
                    "warnings": ["issue_date"]
                },
                ...
            ],
            "summary": {
                "total_records": 1000,
                "valid_records": 950,
                "invalid_records": 50,
                "overall_quality_score": 0.85,
                "common_issues": [
                    {
                        "issue_type": "missing_required",
                        "field": "policy_number",
                        "count": 25,
                        "percentage": 2.5
                    },
                    ...
                ]
            }
        }
        """
        pass
    
    async def generate_cleanup_actions(
        self,
        validation_results: Dict[str, Any],
        source_file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate actionable cleanup recommendations.
        
        Returns:
        {
            "success": True,
            "cleanup_actions": [
                {
                    "action_id": "action_1",
                    "priority": "high",
                    "action_type": "fix_missing_fields",
                    "description": "Add missing 'policy_number' field to 25 records",
                    "affected_records": 25,
                    "affected_fields": ["policy_number"],
                    "recommendation": "Update source file to include 'policy_number' for records: [1, 5, 12, ...]",
                    "example_fix": {
                        "record_id": "record_1",
                        "missing_field": "policy_number",
                        "suggested_value": "POL-12345",  # If can be inferred
                        "location_hint": "Check source system field 'POLICY-NUMBER'"
                    }
                },
                {
                    "action_id": "action_2",
                    "priority": "high",
                    "action_type": "fix_invalid_types",
                    "description": "Fix invalid data types for 'premium_amount' field",
                    "affected_records": 10,
                    "affected_fields": ["premium_amount"],
                    "recommendation": "Convert 'premium_amount' values to numeric format. Invalid values: ['ABC', 'N/A', '']",
                    "example_fix": {
                        "record_id": "record_5",
                        "invalid_field": "premium_amount",
                        "current_value": "ABC",
                        "expected_type": "number",
                        "suggestion": "Check source system for correct premium amount"
                    }
                },
                {
                    "action_id": "action_3",
                    "priority": "medium",
                    "action_type": "fix_date_format",
                    "description": "Standardize date format for 'issue_date' field",
                    "affected_records": 15,
                    "affected_fields": ["issue_date"],
                    "recommendation": "Convert dates from 'MM/DD/YYYY' to 'YYYY-MM-DD' format",
                    "example_fix": {
                        "record_id": "record_10",
                        "field": "issue_date",
                        "current_value": "12/31/2024",
                        "expected_format": "YYYY-MM-DD",
                        "transformed_value": "2024-12-31"
                    }
                }
            ],
            "summary": {
                "total_actions": 3,
                "high_priority": 2,
                "medium_priority": 1,
                "low_priority": 0,
                "estimated_fix_time": "2-4 hours"
            }
        }
        """
        pass
```

---

### 3. Data Quality Agent (Insights Realm)

**Location:** `backend/insights/agents/data_quality_agent.py`

**Responsibilities:**
- Analyze quality issues patterns
- Generate intelligent cleanup recommendations
- Prioritize issues by impact
- Suggest data transformations

**Key Methods:**

```python
class DataQualityAgent(AgentBase):
    """
    Agent for analyzing data quality and generating cleanup recommendations.
    """
    
    async def analyze_quality_issues(
        self,
        validation_results: Dict[str, Any],
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        user_context: Optional[UserContext] = None
    ) -> Dict[str, Any]:
        """
        Analyze quality issues and generate intelligent recommendations.
        
        Uses LLM to:
        - Identify patterns in quality issues
        - Suggest root causes
        - Recommend fixes
        - Prioritize by impact
        """
        pass
    
    async def generate_transformation_suggestions(
        self,
        quality_issue: Dict[str, Any],
        source_data: Dict[str, Any],
        user_context: Optional[UserContext] = None
    ) -> Dict[str, Any]:
        """
        Generate transformation suggestions for fixing quality issues.
        
        Example:
        - Date format conversion
        - Type coercion
        - Value normalization
        """
        pass
```

---

### 4. Enhanced Data Mapping Agent

**Location:** `backend/insights/orchestrators/insights_orchestrator/agents/data_mapping_agent.py`

**Enhanced to support both use cases:**

```python
class DataMappingAgent(AgentBase):
    """
    Agent for semantic schema matching and mapping generation.
    Enhanced to support both unstructured and structured sources.
    """
    
    async def extract_source_schema(
        self,
        source_file_id: str,
        mapping_type: str,
        user_context: Optional[UserContext] = None
    ) -> Dict[str, Any]:
        """
        Extract schema from source file.
        
        For unstructured files (PDF, Word):
        - Use LLM to infer field schema from content
        - Return field definitions with descriptions
        
        For structured files (JSONL, CSV, Excel):
        - Extract column schema directly
        - Return column definitions with types
        """
        pass
    
    async def generate_mapping_rules(
        self,
        source_schema: Dict[str, Any],
        target_schema: Dict[str, Any],
        source_embeddings: List[Dict[str, Any]],
        target_embeddings: List[Dict[str, Any]],
        user_context: Optional[UserContext] = None
    ) -> Dict[str, Any]:
        """
        Generate mapping rules using semantic matching.
        
        Works for both:
        - Unstructured source fields → Target columns
        - Structured source columns → Target columns
        """
        pass
```

---

## 📋 Data Quality Issue Types

### Issue Categories

1. **Missing Required Fields**
   - Field is required in target schema but missing in source
   - Severity: ERROR
   - Action: Add field to source or provide default value

2. **Invalid Data Types**
   - Field value doesn't match expected type (string vs number, etc.)
   - Severity: ERROR
   - Action: Fix data type in source or apply transformation

3. **Invalid Formats**
   - Field value format doesn't match expected format (date, email, etc.)
   - Severity: WARNING or ERROR (depending on field importance)
   - Action: Fix format in source or apply transformation

4. **Out of Range Values**
   - Numeric value outside expected range
   - Severity: WARNING
   - Action: Validate against business rules

5. **Data Inconsistencies**
   - Values that don't make logical sense (e.g., end date before start date)
   - Severity: WARNING
   - Action: Review business logic

6. **Duplicate Records**
   - Records that appear multiple times
   - Severity: WARNING
   - Action: Deduplicate

---

## 🎯 Cleanup Actions Design

### Action Types

1. **Fix Missing Fields**
   - Identify records missing required fields
   - Suggest default values (if applicable)
   - Provide record IDs for manual review

2. **Fix Invalid Types**
   - Identify records with type mismatches
   - Suggest transformations (if possible)
   - Provide examples of invalid values

3. **Fix Format Issues**
   - Identify records with format problems
   - Suggest format transformations
   - Provide before/after examples

4. **Validate Business Rules**
   - Identify records violating business rules
   - Suggest corrections
   - Provide context for manual review

5. **Deduplicate Records**
   - Identify duplicate records
   - Suggest merge strategy
   - Provide duplicate record IDs

---

## 📊 Output Formats

### 1. Mapped Data File

**For Use Case 1 (License PDF → Excel):**
- Populated Excel file with extracted data
- Citations column (showing source location)
- Confidence scores column

**For Use Case 2 (Policy Records → Excel):**
- Excel file with mapped data
- Quality flags column (VALID, INVALID, WARNING)
- Quality score column per record
- Issue summary column

---

### 2. Data Quality Report

```json
{
    "report_id": "quality_report_123",
    "source_file_id": "file_456",
    "target_schema_id": "schema_789",
    "generated_at": "2025-01-15T10:30:00Z",
    "summary": {
        "total_records": 1000,
        "valid_records": 950,
        "invalid_records": 50,
        "overall_quality_score": 0.85,
        "pass_rate": 0.95
    },
    "quality_metrics": {
        "completeness": 0.98,
        "accuracy": 0.92,
        "consistency": 0.88,
        "validity": 0.90
    },
    "common_issues": [
        {
            "issue_type": "missing_required",
            "field": "policy_number",
            "count": 25,
            "percentage": 2.5,
            "severity": "error"
        }
    ],
    "record_details": [
        {
            "record_id": "record_1",
            "record_index": 0,
            "quality_score": 0.65,
            "is_valid": false,
            "issues": [...]
        }
    ]
}
```

---

### 3. Cleanup Actions Report

```json
{
    "report_id": "cleanup_actions_123",
    "source_file_id": "file_456",
    "generated_at": "2025-01-15T10:30:00Z",
    "actions": [
        {
            "action_id": "action_1",
            "priority": "high",
            "action_type": "fix_missing_fields",
            "description": "Add missing 'policy_number' field",
            "affected_records": 25,
            "affected_fields": ["policy_number"],
            "recommendation": "Update source file to include 'policy_number' for records: [1, 5, 12, ...]",
            "estimated_impact": "High - 25 records cannot be migrated without this field",
            "example_fix": {
                "record_id": "record_1",
                "missing_field": "policy_number",
                "suggested_value": null,
                "location_hint": "Check source system field 'POLICY-NUMBER'"
            }
        }
    ],
    "summary": {
        "total_actions": 3,
        "high_priority": 2,
        "medium_priority": 1,
        "estimated_fix_time": "2-4 hours"
    }
}
```

---

## 🔄 Workflow Flows

### Flow 1: Unstructured → Structured (License PDF → Excel)

```
1. User uploads license PDF → Content Pillar parses → JSON chunks + embeddings
2. User uploads Excel template → Content Pillar parses → Schema + embeddings
3. User navigates to Insights → Data Mapping section
4. User selects source (PDF) and target (Excel)
5. System:
   a. Extracts field schema from PDF using LLM
   b. Gets embeddings for semantic matching
   c. Generates mapping rules (PDF fields → Excel columns)
   d. Extracts field values from PDF using LLM
   e. Populates Excel with extracted data
   f. Generates citations and confidence scores
6. User reviews mapping results
7. User exports populated Excel file
```

---

### Flow 2: Structured → Structured (Policy Records → New Data Model)

```
1. User uploads legacy policy records (JSONL) → Content Pillar parses → Structured data + embeddings
2. User uploads/selects target data model → Content Pillar extracts schema + embeddings
3. User navigates to Insights → Data Mapping section
4. User selects source (JSONL) and target (data model)
5. System:
   a. Extracts source schema (columns from JSONL)
   b. Extracts target schema (columns from data model)
   c. Gets embeddings for semantic matching
   d. Generates mapping rules (source columns → target columns)
   e. Validates each record against target schema
   f. Identifies quality issues per record
   g. Generates cleanup actions
   h. Transforms valid records to target format
6. System displays:
   - Quality report (pass rate, common issues)
   - Cleanup actions (actionable recommendations)
   - Mapped data preview
7. User reviews quality issues and cleanup actions
8. User exports:
   - Mapped data file (valid records only OR all records with quality flags)
   - Quality report
   - Cleanup actions report
```

---

## 🎨 Frontend UI Design

### Data Mapping Section (Insights Pillar)

**Components:**

1. **File Selection Panel**
   - Source file selector (with file type indicator)
   - Target file selector (with file type indicator)
   - Mapping type indicator (auto-detected)

2. **Mapping Configuration**
   - Quality validation options (for structured→structured)
   - Output format selection
   - Quality threshold settings

3. **Mapping Results Display**
   - Mapping rules table (source → target with confidence)
   - Quality metrics dashboard (for structured→structured)
   - Data preview (sample records)

4. **Quality Issues Panel** (for structured→structured)
   - Quality score visualization
   - Common issues list
   - Record-level issue drill-down

5. **Cleanup Actions Panel** (for structured→structured)
   - Actionable recommendations list
   - Priority indicators
   - Example fixes
   - Export cleanup report button

6. **Export Options**
   - Export mapped data
   - Export quality report
   - Export cleanup actions report

---

## 🚀 Implementation Phases

### Phase 1: Solution & Journey Layer (Weeks 1-2)
- ✅ Insights Solution Orchestrator (Solution Realm)
- ✅ Insights Journey Orchestrator (Journey Realm)
- ✅ Data Mapping Workflow (Journey Realm)
- ✅ Integration with Data Solution Orchestrator (where appropriate)

### Phase 2: Realm Services Foundation (Weeks 3-4)
- ✅ Field Extraction Service (Insights Realm)
- ✅ Schema Extraction enhancements (unstructured + structured)
- ✅ Basic data mapping workflow (unstructured→structured)

### Phase 3: Data Quality Integration (Weeks 5-6)
- ✅ Data Quality Validation Service
- ✅ Record-level validation logic
- ✅ Quality issue identification
- ✅ Quality metrics calculation

### Phase 4: Cleanup Actions (Weeks 7-8)
- ✅ Cleanup action generation
- ✅ Action prioritization
- ✅ Transformation suggestions
- ✅ Cleanup reports

### Phase 5: Structured→Structured Mapping (Weeks 9-10)
- ✅ Enhanced mapping workflow for structured sources
- ✅ Integration with quality validation
- ✅ End-to-end testing

### Phase 6: Frontend Integration (Weeks 11-12)
- ✅ Data Mapping UI section
- ✅ Quality dashboard
- ✅ Cleanup actions UI
- ✅ Export functionality

---

## 📝 API Design

### New Endpoints

**Solution Realm API:**
```python
# Insights Solution Orchestrator
POST /api/v1/insights-solution/mapping
{
    "source_file_id": "file_123",
    "target_file_id": "file_456",
    "mapping_options": {
        "mapping_type": "auto",  # or "unstructured_to_structured", "structured_to_structured"
        "quality_validation": true,  # for structured→structured
        "min_confidence": 0.8,
        "include_citations": true
    },
    "user_context": {...}
}
# Routes to Insights Journey Orchestrator → Data Mapping Workflow
```

**Journey Realm API:**
```python
# Insights Journey Orchestrator - Data Mapping Workflow
POST /api/v1/insights-journey/data-mapping/execute
{
    "source_file_id": "file_123",
    "target_file_id": "file_456",
    "mapping_options": {...},
    "user_context": {...}
}

GET /api/v1/insights-journey/data-mapping/{mapping_id}
# Returns mapping results, quality report, cleanup actions

POST /api/v1/insights-journey/data-mapping/{mapping_id}/export
{
    "output_format": "excel",
    "include_quality_flags": true,
    "include_citations": true
}
```

**Insights Realm Services API:**
```python
# Data Quality Validation Service
POST /api/v1/insights/data-quality/validate
{
    "records": [...],
    "target_schema": {...},
    "mapping_rules": [...]
}

GET /api/v1/insights/data-quality/{validation_id}/cleanup-actions
# Returns cleanup actions report
```

---

## ✅ Success Criteria

**MVP Success:**
- ✅ Both use cases supported (unstructured→structured, structured→structured)
- ✅ Quality validation for structured→structured mappings
- ✅ Cleanup actions generation
- ✅ Quality reports and cleanup reports
- ✅ Record-level quality tracking
- ✅ Export functionality

**Future Enhancements:**
- User can edit mapping rules manually
- Support for complex transformations
- Support for multi-file mapping
- Real-time quality monitoring
- Automated fix suggestions with user approval

---

## 🔒 Considerations

### MVP Limitations
- Focus on high-confidence mappings (>0.8)
- Support common data types (string, number, date, boolean)
- Basic quality checks (missing, invalid type, invalid format)
- Simple cleanup actions (no complex transformations)

### Scalability
- Process records in batches
- Use async processing for large files
- Cache validation results
- Stream output for large datasets

---

## 📚 Next Steps

1. Review and approve this design
2. Create implementation tickets
3. Start Phase 1 (Foundation)
4. Iterate based on testing results

---

**Status:** Ready for implementation  
**Last Updated:** January 2025

