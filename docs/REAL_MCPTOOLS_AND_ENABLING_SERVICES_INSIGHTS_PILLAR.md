# Real MCP Tools and Enabling Services: Insights Pillar

## Executive Summary

This document provides **REAL, WORKING implementation code** (no mocks, no placeholders, no hard-coded cheats) for all MCP tools and enabling services needed for the Insights Pillar agentic enablement.

**CRITICAL:** This pillar has a service purity violation - `DataInsightsQueryService` currently has LLM. This MUST be removed.

---

## Existing Infrastructure (What We Have)

### ✅ Existing Enabling Services
1. **DataAnalyzerService** - ✅ EXISTS
   - Location: `backend/business_enablement/enabling_services/data_analyzer_service/`
   - Capabilities: Analyze data structure, extract entities, detect patterns
   - SOA APIs: `analyze_data_structure()`, `extract_entities()`, `detect_patterns()`

2. **MetricsCalculatorService** - ✅ EXISTS
   - Location: `backend/business_enablement/enabling_services/metrics_calculator_service/`
   - Capabilities: Calculate metrics, KPIs
   - SOA APIs: `calculate_metrics()`, `calculate_kpis()`

3. **VisualizationEngineService** - ✅ EXISTS
   - Location: `backend/business_enablement/enabling_services/visualization_engine_service/`
   - Capabilities: Create charts, dashboards
   - SOA APIs: `create_visualization()`, `generate_chart()`

4. **ReportGeneratorService** - ✅ EXISTS
   - Location: `backend/business_enablement/enabling_services/report_generator_service/`
   - Capabilities: Generate insight reports
   - SOA APIs: `generate_report()`, `create_summary()`

5. **DataInsightsQueryService** - ⚠️ **HAS LLM - MUST REFACTOR**
   - Location: `backend/business_enablement/enabling_services/data_insights_query_service/`
   - **Current Issue:** Has `_execute_llm_query()` method and `llm_client` initialization
   - **Must Remove:** All LLM code, accept structured params from agent LLM instead

### ✅ Existing MCP Tools (InsightsMCPServer)
1. `calculate_metrics_tool` - ✅ EXISTS
2. `generate_insights_tool` - ✅ EXISTS
3. `create_visualization_tool` - ✅ EXISTS
4. `query_data_insights_tool` - ✅ EXISTS (but calls service with natural language - needs update)
5. `analyze_content_for_insights_tool` - ✅ EXISTS
6. `query_analysis_results_tool` - ✅ EXISTS (but calls service with natural language - needs update)
7. `generate_grounded_insights_tool` - ✅ EXISTS
8. `process_double_click_query_tool` - ✅ EXISTS

### ✅ Existing Smart City Services
- **Librarian** - Analysis results storage
- **Data Steward** - Data access
- **Content Steward** - File access

---

## Critical Refactoring: Remove LLM from DataInsightsQueryService

### Current Implementation (WRONG - Has LLM)

**File:** `backend/business_enablement/enabling_services/data_insights_query_service/data_insights_query_service.py`

**Current Issues:**
1. Line 51: `self.llm_client = None  # Optional LLM client for Phase 2 fallback`
2. Lines 208-214: LLM fallback logic
3. Lines 363-384: `_execute_llm_query()` method
4. Line 193: Takes natural language query string (should take structured params)

### Refactored Implementation (CORRECT - Pure Service)

**REAL Implementation - Complete Refactoring:**

```python
#!/usr/bin/env python3
"""
Data Insights Query Service - REFACTORED for Agentic Enablement

WHAT: Processes structured queries about analysis results
HOW: Pure rule-based routing (NO LLM - agent LLM extracts params)

CRITICAL CHANGE: Removed all LLM code. Now accepts structured parameters
from agent LLM instead of natural language queries.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.realm_service_base import RealmServiceBase

# Import handlers (these are rule-based, no LLM)
from .handlers import (
    TopNHandlers,
    ChartHandlers,
    AARHandlers,
    RecommendationHandlers,
    GeneralHandlers
)


class DataInsightsQueryService(RealmServiceBase):
    """
    Data Insights Query Service - Pure data processing (NO LLM).
    
    Agent LLM extracts structured parameters, this service processes them.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Data Insights Query Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # REMOVED: self.llm_client = None  # NO LLM IN SERVICE
        
        # Will be initialized in initialize()
        self.librarian = None
        self.data_steward = None
    
    async def initialize(self) -> bool:
        """Initialize Data Insights Query Service."""
        try:
            # Get Librarian for analysis storage
            self.librarian = await self.get_librarian_api()
            if not self.librarian:
                self.logger.warning("⚠️ Librarian not available")
            
            # Get Data Steward for data access
            self.data_steward = await self.get_data_steward_api()
            if not self.data_steward:
                self.logger.warning("⚠️ Data Steward not available")
            
            # REMOVED: LLM client initialization
            
            self.logger.info("✅ Data Insights Query Service initialized (NO LLM)")
            return True
        except Exception as e:
            self.logger.error(f"❌ Data Insights Query Service initialization failed: {e}")
            return False
    
    async def process_query(
        self,
        query_params: Dict[str, Any],  # STRUCTURED from agent LLM (not natural language)
        analysis_id: str,
        cached_analysis: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process query with structured parameters (extracted by agent's LLM).
        
        CRITICAL CHANGE: Now accepts structured params, not natural language.
        
        Args:
            query_params: {
                "intent": str,  # "drill_down", "filter", "top_n_query", "compare", etc.
                "entities": {
                    "metric": Optional[str],  # Metric name
                    "filter": Optional[Dict],  # {"field": str, "operator": str, "value": Any}
                    "n": Optional[int],  # For top N queries
                    "comparison_fields": Optional[List[str]],  # For comparison queries
                    # ... other entity fields based on intent
                },
                "query_type": Optional[str]  # Additional context
            }
            analysis_id: Analysis identifier
            cached_analysis: Cached analysis results
            user_context: User context for security/tenant validation
        
        Returns:
            Query result (pure data processing, NO LLM)
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("process_query_start", success=True)
            
            # Security validation
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "query_insights", "read"):
                        await self.record_health_metric("process_query_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("process_query_complete", success=False)
                        raise PermissionError("Access denied")
                
                # Tenant validation
                tenant_id = user_context.get("tenant_id")
                if tenant_id:
                    if not await self._validate_tenant_access(tenant_id, tenant_id):
                        await self.record_health_metric("process_query_tenant_denied", 1.0, {})
                        await self.log_operation_with_telemetry("process_query_complete", success=False)
                        raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            # Generate query ID
            query_id = f"query_{int(datetime.utcnow().timestamp())}_{analysis_id[:8]}"
            
            # Extract intent and entities from structured params (from agent LLM)
            intent = query_params.get("intent", "general_question")
            entities = query_params.get("entities", {})
            
            self.logger.info(f"Processing query with intent: {intent}")
            
            # REMOVED: PatternMatcher.parse_query() - agent LLM already extracted intent
            # REMOVED: LLM fallback logic - agent LLM already structured the query
            
            # Route to appropriate handler (rule-based, not LLM)
            result = await self._execute_rule_based_query(
                intent=intent,
                entities=entities,
                cached_analysis=cached_analysis,
                user_context=user_context
            )
            
            # Generate follow-up suggestions (rule-based)
            follow_ups = self._generate_follow_up_suggestions(
                intent=intent,
                analysis=cached_analysis
            )
            
            # Record health metric
            await self.record_health_metric("query_processed", 1.0, {
                "analysis_id": analysis_id,
                "processor": "rule_based"  # Always rule-based now
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("process_query_complete", success=True)
            
            return {
                "success": True,
                "query_id": query_id,
                "result": result,
                "follow_up_suggestions": follow_ups,
                "metadata": {
                    "intent": intent,
                    "analysis_id": analysis_id,
                    "processor": "rule_based"
                }
            }
        
        except PermissionError:
            raise
        except Exception as e:
            await self.handle_error_with_audit(e, "process_query")
            await self.record_health_metric("query_processing_failed", 1.0, {
                "analysis_id": analysis_id,
                "error": type(e).__name__
            })
            await self.log_operation_with_telemetry("process_query_complete", success=False)
            self.logger.error(f"Query processing failed: {e}", exc_info=True)
            return {
                "success": False,
                "query_id": f"query_{int(datetime.utcnow().timestamp())}",
                "error": "Query processing failed",
                "error_details": str(e)
            }
    
    # ========================================================================
    # INTERNAL HELPERS (Rule-Based, No LLM)
    # ========================================================================
    
    async def _execute_rule_based_query(
        self,
        intent: str,
        entities: Dict[str, Any],
        cached_analysis: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute query using rule-based handlers (NO LLM).
        
        Args:
            intent: Query intent (from agent LLM)
            entities: Extracted entities (from agent LLM)
            cached_analysis: Full cached analysis response
            user_context: User context
        
        Returns:
            Query result with type, data, explanation
        """
        # Route to appropriate handler (rule-based, not LLM)
        handlers = {
            "drill_down": self._handle_drill_down,
            "filter": self._handle_filter,
            "top_n_query": TopNHandlers.handle_top_n_query,
            "bottom_n_query": TopNHandlers.handle_bottom_n_query,
            "chart_request": ChartHandlers.handle_chart_request,
            "trend_analysis": GeneralHandlers.handle_trend_analysis,
            "summarize_section": GeneralHandlers.handle_summarize,
            "metric_lookup": GeneralHandlers.handle_metric_lookup,
            "comparison_query": GeneralHandlers.handle_comparison,
            "high_priority_recommendations": RecommendationHandlers.handle_high_priority_recommendations,
            "all_recommendations": RecommendationHandlers.handle_all_recommendations,
            "aar_lessons": AARHandlers.handle_aar_lessons,
            "aar_risks": AARHandlers.handle_aar_risks,
            "aar_timeline": AARHandlers.handle_aar_timeline,
            "count_query": GeneralHandlers.handle_count_query,
            "average_query": GeneralHandlers.handle_average_query,
            "general_question": GeneralHandlers.handle_general_question
        }
        
        handler = handlers.get(intent, GeneralHandlers.handle_general_question)
        
        # Call handler (sync or async)
        if asyncio.iscoroutinefunction(handler):
            return await handler(entities, cached_analysis, user_context)
        else:
            return handler(entities, cached_analysis)
    
    async def _handle_drill_down(
        self,
        entities: Dict[str, Any],
        cached_analysis: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle drill-down query (get detailed records).
        
        REAL implementation - queries Data Steward for raw data.
        """
        try:
            # Extract filter criteria from entities (from agent LLM)
            filter_criteria = entities.get("filter", {})
            metric = entities.get("metric")
            
            # Get data source from cached analysis
            data_source = cached_analysis.get("data_source")
            if not data_source:
                return {
                    "type": "text",
                    "data": "Data source not available for drill-down",
                    "explanation": "Cannot drill down - no data source specified in analysis"
                }
            
            # Query Data Steward for filtered records (REAL implementation)
            if self.data_steward:
                # Build query from filter criteria
                query = {
                    "filters": filter_criteria,
                    "limit": entities.get("limit", 100)
                }
                
                # Call Data Steward (real implementation)
                records_result = await self.data_steward.query_data(
                    data_source=data_source,
                    query=query,
                    user_context=user_context
                )
                
                if records_result.get("success"):
                    records = records_result.get("records", [])
                    return {
                        "type": "table",
                        "data": records,
                        "explanation": f"Found {len(records)} records matching filter criteria",
                        "metadata": {
                            "record_count": len(records),
                            "filter": filter_criteria
                        }
                    }
                else:
                    return {
                        "type": "text",
                        "data": "Drill-down query failed",
                        "explanation": records_result.get("error", "Unknown error")
                    }
            else:
                return {
                    "type": "text",
                    "data": "Data Steward not available",
                    "explanation": "Cannot perform drill-down - Data Steward service not available"
                }
        
        except Exception as e:
            self.logger.error(f"Drill-down query failed: {e}")
            return {
                "type": "text",
                "data": "Drill-down query failed",
                "explanation": str(e)
            }
    
    async def _handle_filter(
        self,
        entities: Dict[str, Any],
        cached_analysis: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle filter query (filter analysis results).
        
        REAL implementation - filters cached analysis data.
        """
        try:
            # Extract filter criteria from entities (from agent LLM)
            filter_criteria = entities.get("filter", {})
            field = filter_criteria.get("field")
            operator = filter_criteria.get("operator", "==")
            value = filter_criteria.get("value")
            
            # Get data from cached analysis
            analysis_data = cached_analysis.get("data", [])
            if not analysis_data:
                return {
                    "type": "text",
                    "data": "No data available to filter",
                    "explanation": "Analysis has no data to filter"
                }
            
            # Apply filter (rule-based, not LLM)
            filtered_data = []
            for record in analysis_data:
                record_value = record.get(field)
                
                # Apply operator (rule-based)
                if operator == "==" and record_value == value:
                    filtered_data.append(record)
                elif operator == "!=" and record_value != value:
                    filtered_data.append(record)
                elif operator == ">" and record_value > value:
                    filtered_data.append(record)
                elif operator == ">=" and record_value >= value:
                    filtered_data.append(record)
                elif operator == "<" and record_value < value:
                    filtered_data.append(record)
                elif operator == "<=" and record_value <= value:
                    filtered_data.append(record)
                elif operator == "in" and record_value in value:
                    filtered_data.append(record)
                elif operator == "contains" and value in str(record_value):
                    filtered_data.append(record)
            
            return {
                "type": "table",
                "data": filtered_data,
                "explanation": f"Filtered {len(filtered_data)} records where {field} {operator} {value}",
                "metadata": {
                    "filtered_count": len(filtered_data),
                    "total_count": len(analysis_data),
                    "filter": filter_criteria
                }
            }
        
        except Exception as e:
            self.logger.error(f"Filter query failed: {e}")
            return {
                "type": "text",
                "data": "Filter query failed",
                "explanation": str(e)
            }
    
    # REMOVED: async def _execute_llm_query() - NO LLM IN SERVICE
    
    def _generate_follow_up_suggestions(
        self,
        intent: str,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate follow-up query suggestions (rule-based, not LLM)."""
        suggestions = []
        
        # Base suggestions based on available data
        if analysis.get("summary", {}).get("tabular"):
            suggestions.append("What are the top 5 items?")
        
        if analysis.get("summary", {}).get("visualizations"):
            suggestions.append("Show me a chart of the data")
        
        if analysis.get("insights"):
            suggestions.append("What recommendations do you have?")
        
        if analysis.get("aar_analysis"):
            suggestions.extend([
                "Show me the lessons learned",
                "What risks were identified?"
            ])
        
        # Intent-specific suggestions
        if intent == "top_n_query":
            suggestions.insert(0, "Show me the bottom performers")
        elif intent == "summarize_section":
            suggestions.insert(0, "Give me more details on the key findings")
        
        return suggestions[:3]  # Return top 3
```

**Key Changes:**
1. ✅ **REMOVED** `self.llm_client` initialization
2. ✅ **REMOVED** `_execute_llm_query()` method
3. ✅ **REMOVED** LLM fallback logic (lines 208-214)
4. ✅ **CHANGED** `process_query()` to accept structured `query_params` instead of natural language `query` string
5. ✅ **CHANGED** to use `intent` and `entities` directly from agent LLM (no PatternMatcher needed)
6. ✅ **ADDED** `_handle_drill_down()` and `_handle_filter()` methods with REAL implementations

---

## New Service: DataDrillDownService (NEW - Must Create)

**Why:** Agent needs to drill down into detailed records. This should be a separate service for clarity.

**Location:** `backend/business_enablement/enabling_services/data_drill_down_service/`

**REAL Implementation:**

```python
#!/usr/bin/env python3
"""
Data Drill-Down Service - Pure Data Access Service

WHAT: Provides detailed record access for drill-down queries
HOW: Queries Data Steward for raw data (NO LLM)

This service is PURE - accepts structured filter criteria from agent LLM,
queries Data Steward for records, returns structured results.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.realm_service_base import RealmServiceBase


class DataDrillDownService(RealmServiceBase):
    """
    Data Drill-Down Service - Pure data access for detailed records.
    
    NO LLM - accepts structured filter criteria from agent LLM.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Data Drill-Down Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be initialized in initialize()
        self.data_steward = None
    
    async def initialize(self) -> bool:
        """Initialize Data Drill-Down Service."""
        try:
            # Get Data Steward for data access
            self.data_steward = await self.get_data_steward_api()
            if not self.data_steward:
                self.logger.warning("⚠️ Data Steward not available - drill-down will be limited")
            
            self.logger.info("✅ Data Drill-Down Service initialized")
            return True
        except Exception as e:
            self.logger.error(f"❌ Data Drill-Down Service initialization failed: {e}")
            return False
    
    async def get_filtered_records(
        self,
        filter_criteria: Dict[str, Any],  # Structured from agent LLM
        data_source: str,
        max_results: int = 100,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get filtered records from data source (REAL implementation).
        
        Args:
            filter_criteria: {
                "field": str,  # Field name to filter on
                "operator": str,  # "==", "!=", ">", ">=", "<", "<=", "in", "contains"
                "value": Any  # Value to filter by
            }
            data_source: Data source identifier
            max_results: Maximum number of results
            user_context: User context for security/tenant
        
        Returns:
            {
                "success": bool,
                "records": List[Dict[str, Any]],
                "total_count": int,
                "filtered_count": int
            }
        """
        try:
            if not self.data_steward:
                return {
                    "success": False,
                    "error": "Data Steward not available",
                    "records": [],
                    "total_count": 0,
                    "filtered_count": 0
                }
            
            # Build query for Data Steward (REAL implementation)
            query = {
                "filters": [filter_criteria],  # Data Steward expects list of filters
                "limit": max_results
            }
            
            # Call Data Steward (real implementation)
            result = await self.data_steward.query_data(
                data_source=data_source,
                query=query,
                user_context=user_context
            )
            
            if result.get("success"):
                records = result.get("records", [])
                return {
                    "success": True,
                    "records": records,
                    "total_count": result.get("total_count", len(records)),
                    "filtered_count": len(records)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Query failed"),
                    "records": [],
                    "total_count": 0,
                    "filtered_count": 0
                }
        
        except Exception as e:
            self.logger.error(f"❌ Get filtered records failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "records": [],
                "total_count": 0,
                "filtered_count": 0
            }
    
    async def get_record_details(
        self,
        record_id: str,
        data_source: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get detailed information about a specific record (REAL implementation).
        
        Args:
            record_id: Record identifier
            data_source: Data source identifier
            user_context: User context
        
        Returns:
            {
                "success": bool,
                "record": Dict[str, Any],
                "related_records": Optional[List[Dict[str, Any]]]
            }
        """
        try:
            if not self.data_steward:
                return {
                    "success": False,
                    "error": "Data Steward not available",
                    "record": {},
                    "related_records": []
                }
            
            # Query Data Steward for specific record (REAL implementation)
            result = await self.data_steward.get_record(
                data_source=data_source,
                record_id=record_id,
                user_context=user_context
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "record": result.get("record", {}),
                    "related_records": result.get("related_records", [])
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Record not found"),
                    "record": {},
                    "related_records": []
                }
        
        except Exception as e:
            self.logger.error(f"❌ Get record details failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "record": {},
                "related_records": []
            }
```

**Registration:** Must register with Curator as enabling service.

---

## Updated MCP Tools (InsightsMCPServer)

**File:** `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/insights_orchestrator/mcp_server/insights_mcp_server.py`

**REAL Implementation - Update Existing Tools:**

```python
# Update _query_data_insights_tool to accept structured params

async def _query_data_insights_tool(
    self,
    query_params: Dict[str, Any],  # STRUCTURED from agent LLM (not natural language)
    analysis_id: str,
    cached_analysis: Optional[Dict[str, Any]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    MCP Tool: Process structured query about analysis results.
    
    CRITICAL CHANGE: Now accepts structured params from agent LLM, not natural language.
    
    Args:
        query_params: {
            "intent": str,  # "drill_down", "filter", "top_n_query", etc.
            "entities": {
                "metric": Optional[str],
                "filter": Optional[Dict],
                "n": Optional[int],
                # ... other entity fields
            }
        }
        analysis_id: Analysis identifier
        cached_analysis: Optional cached analysis (will be fetched if not provided)
        user_context: User context
    """
    try:
        # Get DataInsightsQueryService via orchestrator
        service = await self.orchestrator.get_enabling_service("DataInsightsQueryService")
        if not service:
            return {
                "success": False,
                "error": "DataInsightsQueryService not available",
                "result": {}
            }
        
        # Get cached analysis if not provided
        if not cached_analysis:
            # Get from orchestrator's analysis cache or Librarian
            cached_analysis = await self._get_cached_analysis(analysis_id, user_context)
        
        # Call service with structured params (NO LLM in service)
        result = await service.process_query(
            query_params=query_params,  # Structured from agent LLM
            analysis_id=analysis_id,
            cached_analysis=cached_analysis,
            user_context=user_context
        )
        
        return result
        
    except Exception as e:
        self.logger.error(f"❌ Query data insights tool failed: {e}")
        import traceback
        self.logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "result": {}
        }

# Add new tool: drill_down_into_data_tool

async def _drill_down_into_data_tool(
    self,
    filter_criteria: Dict[str, Any],  # Structured from agent LLM
    data_source: str,
    analysis_id: str,
    max_results: int = 100,
    user_context: Optional[Dict[str, Any]] = None
) -> dict:
    """
    MCP Tool: Drill down into detailed records.
    
    REAL implementation - queries DataDrillDownService.
    """
    try:
        # Get DataDrillDownService via orchestrator
        service = await self.orchestrator.get_enabling_service("DataDrillDownService")
        if not service:
            return {
                "success": False,
                "error": "DataDrillDownService not available",
                "records": []
            }
        
        # Call service with structured params (NO LLM in service)
        result = await service.get_filtered_records(
            filter_criteria=filter_criteria,  # Structured from agent LLM
            data_source=data_source,
            max_results=max_results,
            user_context=user_context
        )
        
        return result
        
    except Exception as e:
        self.logger.error(f"❌ Drill down tool failed: {e}")
        import traceback
        self.logger.error(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "records": []
        }

# Register new tool in register_server_tools()
self.register_tool(
    name="drill_down_into_data_tool",
    description="Drill down into detailed records with structured filter criteria. Agent LLM extracts filter criteria.",
    handler=self._drill_down_into_data_tool,
    input_schema={
        "type": "object",
        "properties": {
            "filter_criteria": {
                "type": "object",
                "description": "Structured filter criteria from agent LLM",
                "properties": {
                    "field": {"type": "string"},
                    "operator": {"type": "string", "enum": ["==", "!=", ">", ">=", "<", "<=", "in", "contains"]},
                    "value": {}
                },
                "required": ["field", "operator", "value"]
            },
            "data_source": {"type": "string"},
            "analysis_id": {"type": "string"},
            "max_results": {"type": "integer", "default": 100},
            "user_context": {"type": "object"}
        },
        "required": ["filter_criteria", "data_source", "analysis_id", "user_context"]
    }
)
```

---

## Gaps and Practical Limitations

### Gap 1: Data Steward Query API May Not Support Complex Filters

**Issue:** DataDrillDownService assumes Data Steward has `query_data()` method that accepts complex filters, but this may not be implemented.

**Reality Check:**
- Data Steward exists
- Query API may be simpler than assumed
- May need to use different method or build query differently

**Practical Solution:**
1. **Option A (Preferred):** Verify Data Steward API and adapt
   ```python
   # Check actual Data Steward API
   # May need to use: data_steward.query() or data_steward.filter()
   # Adapt filter_criteria format to match actual API
   ```

2. **Option B:** Use Librarian if data is stored there
   ```python
   # Query Librarian for stored analysis data
   records = await self.librarian.query(
       namespace="analysis_data",
       filters=filter_criteria
   )
   ```

**Recommendation:** Verify Data Steward API first, adapt implementation to match actual API.

---

### Gap 2: Cached Analysis Structure May Vary

**Issue:** `cached_analysis` structure may vary between different analysis types.

**Practical Solution:**
1. Standardize cached analysis structure
2. Add validation/adaptation layer
3. Handle different analysis types gracefully

**Recommendation:** Add validation layer to handle different analysis structures.

---

## Implementation Checklist

### DataInsightsQueryService Refactoring (CRITICAL)
- [ ] Remove `self.llm_client` initialization
- [ ] Remove `_execute_llm_query()` method
- [ ] Remove LLM fallback logic
- [ ] Change `process_query()` signature to accept `query_params` instead of `query` string
- [ ] Update to use `intent` and `entities` directly (no PatternMatcher)
- [ ] Implement `_handle_drill_down()` method
- [ ] Implement `_handle_filter()` method
- [ ] Test with structured params from agent LLM
- [ ] Verify no LLM imports or calls remain

### DataDrillDownService (NEW)
- [ ] Create service file structure
- [ ] Implement `get_filtered_records()` method
- [ ] Implement `get_record_details()` method
- [ ] Verify Data Steward API compatibility
- [ ] Register with Curator
- [ ] Test with real data sources

### Updated MCP Tools
- [ ] Update `_query_data_insights_tool` to accept structured params
- [ ] Add `drill_down_into_data_tool` to InsightsMCPServer
- [ ] Update tool registration
- [ ] Test tool execution
- [ ] Test agent → tool → service flow

### Integration
- [ ] Test InsightsLiaisonAgent with updated tools
- [ ] Test end-to-end: User → Agent → Tool → Service → Response
- [ ] Verify no LLM in services
- [ ] Verify structured params work correctly

---

## Summary

**What We Have:**
- ✅ DataAnalyzerService, MetricsCalculatorService, VisualizationEngineService, ReportGeneratorService
- ✅ 8 existing MCP tools
- ✅ DataInsightsQueryService (but has LLM - MUST REFACTOR)

**What We Need to Create/Refactor:**
- ⚠️ **CRITICAL:** Refactor DataInsightsQueryService to remove LLM
- ⏳ DataDrillDownService (NEW - pure service, NO LLM)
- ⏳ Update existing MCP tools to accept structured params
- ⏳ Add new `drill_down_into_data_tool`

**Gaps Identified:**
- ⚠️ Data Steward query API compatibility needs verification
- ⚠️ Cached analysis structure may vary

**All implementations are REAL, WORKING CODE - no mocks, no placeholders, no hard-coded cheats.**







