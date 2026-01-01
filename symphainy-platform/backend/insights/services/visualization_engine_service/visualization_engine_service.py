#!/usr/bin/env python3
"""
Visualization Engine Service - Phase 2: AGUI Components for Insights Pillar

WHAT: Provides visualization generation capabilities
HOW: Generates AGUI schema-compliant components (not raw code)

Key Features:
- Generates AGUI-compliant visualization components
- Works with semantic embeddings (not raw parsed data)
- Supports chart, dashboard, and table types
- Uses plotly/matplotlib for data generation, but formats as AGUI components
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.realm_service_base import RealmServiceBase

# Import micro-modules
from .modules.initialization import Initialization
from .modules.utilities import Utilities
from .modules.agui_component_generator import AGUIComponentGenerator


class VisualizationEngineService(RealmServiceBase):
    """
    Visualization Engine enabling service for Business Enablement.
    
    Generates AGUI-compliant visualization components that agents can use.
    Works with semantic embeddings (not raw parsed data) to maintain security boundary.
    
    Key Capabilities:
    - Chart components (bar, line, scatter, histogram, etc.)
    - Dashboard components (composite visualizations)
    - Table components (data tables with sorting/filtering)
    - AGUI schema-compliant output (not raw matplotlib/plotly code)
    
    Integrates with Smart City services for semantic data access.
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Visualization Engine Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Smart City service APIs (will be initialized in initialize())
        self.librarian = None
        self.semantic_data = None  # SemanticDataAbstraction for querying embeddings
        self.nurse = None  # For observability
        
        # Initialize micro-modules
        self.utilities_module = Utilities(self)
        self.initialization_module = Initialization(self)
        self.agui_component_generator = AGUIComponentGenerator(self)
    
    async def initialize(self) -> bool:
        """Initialize Visualization Engine Service."""
        await super().initialize()
        return await self.initialization_module.initialize()
    
    # SOA API Methods
    
    async def create_agui_visualization(
        self,
        content_id: str,
        visualization_type: str,  # "chart", "dashboard", "table"
        visualization_spec: Dict[str, Any],  # What to visualize
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create AGUI-compliant visualization component.
        
        Flow:
        1. Get semantic embeddings (data to visualize)
        2. Generate AGUI component based on visualization_spec
        3. Return AGUI schema-compliant component
        
        Args:
            content_id: Content metadata ID
            visualization_type: Type of visualization ("chart", "dashboard", "table")
            visualization_spec: Specification of what to visualize:
                - For charts: {"chart_type": "bar", "x_axis": "column1", "y_axis": "column2", "title": "Chart Title"}
                - For dashboards: {"components": [...], "layout": {...}}
                - For tables: {"columns": [...], "sortable": True, "filterable": True}
            user_context: Optional user context for security and tenant validation
            
        Returns:
            Dict with AGUI-compliant component:
            {
                "success": bool,
                "content_id": str,
                "visualization_type": str,
                "component": {...},  # AGUI-compliant component
                "agui_schema": {...}  # AGUI schema reference
            }
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "create_agui_visualization_start",
                success=True,
                details={"content_id": content_id, "visualization_type": visualization_type}
            )
            
            # Step 1: Get semantic embeddings (data to visualize)
            if not self.semantic_data:
                return {
                    "success": False,
                    "error": "Semantic data abstraction not available",
                    "content_id": content_id
                }
            
            # Query embeddings with filters from visualization_spec
            tenant_id = self.utilities_module.get_tenant_id(user_context) if user_context else None
            user_ctx = {"tenant_id": tenant_id} if tenant_id else None
            
            filters = visualization_spec.get("filters", {})
            embeddings = await self.semantic_data.get_semantic_embeddings(
                content_id=content_id,
                filters=filters,
                user_context=user_ctx
            )
            
            if not embeddings:
                return {
                    "success": False,
                    "error": "No embeddings found for visualization",
                    "content_id": content_id
                }
            
            # Step 2: Generate AGUI component based on visualization_type
            if visualization_type == "chart":
                component = await self.agui_component_generator.create_chart_component(
                    embeddings, visualization_spec
                )
            elif visualization_type == "dashboard":
                component = await self.agui_component_generator.create_dashboard_component(
                    embeddings, visualization_spec
                )
            elif visualization_type == "table":
                component = await self.agui_component_generator.create_table_component(
                    embeddings, visualization_spec
                )
            else:
                return {
                    "success": False,
                    "error": f"Unknown visualization type: {visualization_type}",
                    "content_id": content_id
                }
            
            # Step 3: Return AGUI schema-compliant component
            result = {
                "success": True,
                "content_id": content_id,
                "visualization_type": visualization_type,
                "component": component,  # AGUI-compliant component
                "agui_schema": self.agui_component_generator.get_agui_schema_for_type(visualization_type)
            }
            
            # Record success
            await self.record_health_metric(
                "create_agui_visualization_success",
                1.0,
                {"content_id": content_id, "visualization_type": visualization_type}
            )
            
            await self.log_operation_with_telemetry(
                "create_agui_visualization_complete",
                success=True,
                details={"content_id": content_id, "visualization_type": visualization_type}
            )
            
            return result
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "create_agui_visualization")
            
            # Record failure
            await self.record_health_metric(
                "create_agui_visualization_failed",
                1.0,
                {"content_id": content_id, "error": type(e).__name__}
            )
            
            await self.log_operation_with_telemetry(
                "create_agui_visualization_complete",
                success=False,
                details={"content_id": content_id, "error": str(e)}
            )
            
            self.logger.error(f"❌ AGUI visualization creation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_id": content_id
            }

