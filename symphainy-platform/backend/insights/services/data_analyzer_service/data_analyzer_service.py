#!/usr/bin/env python3
"""
Data Analyzer Service - Phase 1: EDA Tools for Insights Pillar

WHAT: Provides exploratory data analysis tools for agents
HOW: Works with semantic embeddings, provides deterministic results

Key Features:
- Works with semantic embeddings (schema/metadata)
- Provides deterministic EDA results (same input = same output)
- Supports structured data analysis
- Exposes MCP tools for agents
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.realm_service_base import RealmServiceBase

# Import micro-modules
from .modules.initialization import Initialization
from .modules.utilities import Utilities
from .modules.eda_analysis import EDAAnalysis


class DataAnalyzerService(RealmServiceBase):
    """
    Data Analyzer enabling service for Business Enablement.
    
    Provides EDA (Exploratory Data Analysis) tools that agents can call.
    Works with semantic embeddings (not raw parsed data) to maintain security boundary.
    
    Key Capabilities:
    - Statistics calculation (mean, median, std, min, max, etc.)
    - Correlation analysis between numerical columns
    - Distribution analysis (skewness, kurtosis, quartiles)
    - Missing values analysis
    - Deterministic results (same input = same output)
    
    Integrates with Smart City services for semantic data access.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Data Analyzer Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Smart City service APIs (will be initialized in initialize())
        self.librarian = None
        self.semantic_data = None  # SemanticDataAbstraction for querying embeddings
        self.nurse = None  # For observability
        
        # Initialize micro-modules
        self.utilities_module = Utilities(self)
        self.initialization_module = Initialization(self)
        self.eda_analysis_module = EDAAnalysis(self)
    
    async def initialize(self) -> bool:
        """Initialize Data Analyzer Service."""
        await super().initialize()
        return await self.initialization_module.initialize()
    
    # SOA API Methods
    
    async def run_eda_analysis(
        self,
        content_id: str,
        analysis_types: List[str],  # ["statistics", "correlations", "distributions", "missing_values"]
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run EDA analysis on structured data using semantic embeddings.
        
        Flow:
        1. Get semantic embeddings (schema/metadata) from semantic data abstraction
        2. Extract schema information from embeddings
        3. Run EDA analysis tools (deterministic)
        4. Return structured results
        
        Args:
            content_id: Content metadata ID
            analysis_types: List of analysis types to run
                - "statistics": Descriptive statistics (mean, median, std, etc.)
                - "correlations": Correlation matrix for numerical columns
                - "distributions": Distribution information (skewness, kurtosis, quartiles)
                - "missing_values": Missing value analysis
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with EDA results (deterministic - same input = same output):
            {
                "success": bool,
                "content_id": str,
                "analysis_types": List[str],
                "eda_results": {
                    "statistics": {...},
                    "correlations": {...},
                    "distributions": {...},
                    "missing_values": {...}
                },
                "schema_info": {...}
            }
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "run_eda_analysis_start",
                success=True,
                details={"content_id": content_id, "analysis_types": analysis_types}
            )
            
            # Step 1: Get semantic embeddings (schema/metadata)
            # Use semantic data abstraction to query embeddings
            if not self.semantic_data:
                return {
                    "success": False,
                    "error": "Semantic data abstraction not available",
                    "content_id": content_id
                }
            
            # Query embeddings using get_semantic_embeddings
            # Note: Embeddings are stored with embedding_type="structured" (not "schema")
            # So we query by content_id without the embedding_type filter, or use "structured"
            tenant_id = self.utilities_module.get_tenant_id(user_context) if user_context else None
            user_ctx = {"tenant_id": tenant_id} if tenant_id else None
            
            # Try querying with embedding_type="structured" first (how embeddings are actually stored)
            embeddings = await self.semantic_data.get_semantic_embeddings(
                content_id=content_id,
                filters={"embedding_type": "structured"},
                user_context=user_ctx
            )
            
            # If no results, try without embedding_type filter (fallback)
            if not embeddings:
                self.logger.warning(f"⚠️ No embeddings found with embedding_type='structured', trying without filter")
                embeddings = await self.semantic_data.get_semantic_embeddings(
                    content_id=content_id,
                    filters=None,  # Query all embeddings for this content_id
                    user_context=user_ctx
                )
            
            if not embeddings:
                return {
                    "success": False,
                    "error": "No embeddings found for content_id",
                    "content_id": content_id,
                    "suggestion": "Ensure embeddings have been created for this file using /api/v1/content-pillar/create-embeddings"
                }
            
            # Step 2: Extract schema information from embeddings
            schema_info = self.eda_analysis_module.extract_schema_from_embeddings(embeddings)
            
            # Step 3: Run EDA analysis tools (deterministic)
            eda_results = {}
            
            if "statistics" in analysis_types:
                eda_results["statistics"] = await self.eda_analysis_module.calculate_statistics(schema_info)
            
            if "correlations" in analysis_types:
                eda_results["correlations"] = await self.eda_analysis_module.calculate_correlations(schema_info)
            
            if "distributions" in analysis_types:
                eda_results["distributions"] = await self.eda_analysis_module.calculate_distributions(schema_info)
            
            if "missing_values" in analysis_types:
                eda_results["missing_values"] = await self.eda_analysis_module.analyze_missing_values(schema_info)
            
            # Step 4: Return structured results (deterministic)
            result = {
                "success": True,
                "content_id": content_id,
                "analysis_types": analysis_types,
                "eda_results": eda_results,
                "schema_info": schema_info  # Include schema for context
            }
            
            # Record success
            await self.record_health_metric(
                "run_eda_analysis_success",
                1.0,
                {"content_id": content_id, "analysis_types": analysis_types}
            )
            
            await self.log_operation_with_telemetry(
                "run_eda_analysis_complete",
                success=True,
                details={"content_id": content_id, "analysis_types": analysis_types}
            )
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "run_eda_analysis")
            
            # Record failure
            await self.record_health_metric(
                "run_eda_analysis_failed",
                1.0,
                {"content_id": content_id, "error": type(e).__name__}
            )
            
            await self.log_operation_with_telemetry(
                "run_eda_analysis_complete",
                success=False,
                details={"content_id": content_id, "error": str(e)}
            )
            
            self.logger.error(f"❌ EDA analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_id": content_id
            }

