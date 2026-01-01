"""
AGUI Output Formatter - Structured Output Generation (Refactored with AgenticServiceBase)

Generates standardized AGUI-compliant outputs for agent responses.
Provides consistent UI components and structured data formats.

WHAT (Agentic Role): I provide structured AGUI-compliant output generation for agent responses
HOW (AGUI Output Formatter): I use AgenticServiceBase with proper error handling and multi-tenancy
"""

import sys
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

# Import RealmServiceBase
from bases.realm_service_base import RealmServiceBase


class AGUIOutputFormatter(RealmServiceBase):
    """
    Formats agent outputs into AGUI-compliant structured components.
    
    Refactored to use pure dependency injection through DIContainerService.
    
    Provides:
    - Analysis cards with metrics and visualizations
    - Data tables with sorting and filtering
    - Interactive components and actions
    - Progress indicators and status displays
    - Error handling and user feedback
    """
    
    def __init__(self, foundation_services, public_works_foundation=None):
        """Initialize AGUI output formatter with AgenticServiceBase."""
        super().__init__("agui_output_formatter", foundation_services, public_works_foundation)
        
        # Component templates
        self.component_templates = {
            "analysis_card": self._create_analysis_card_template(),
            "data_table": self._create_data_table_template(),
            "visualization": self._create_visualization_template(),
            "progress_indicator": self._create_progress_indicator_template(),
            "action_buttons": self._create_action_buttons_template(),
            "error_display": self._create_error_display_template()
        }
    
    def _create_analysis_card_template(self) -> Dict[str, Any]:
        """Create analysis card template."""
        return {
            "type": "analysis_card",
            "title": "",
            "status": "completed",
            "metrics": {},
            "visualizations": [],
            "actions": [],
            "metadata": {}
        }
    
    def _create_data_table_template(self) -> Dict[str, Any]:
        """Create data table template."""
        return {
            "type": "data_table",
            "columns": [],
            "data": [],
            "pagination": {"page_size": 50, "total_rows": 0, "current_page": 1},
            "sorting": {"enabled": True, "default_sort": None},
            "filtering": {"enabled": True, "filters": []},
            "metadata": {}
        }
    
    def _create_visualization_template(self) -> Dict[str, Any]:
        """Create visualization template."""
        return {
            "type": "visualization",
            "chart_type": "line_chart",
            "data": {},
            "options": {},
            "interactive": True,
            "metadata": {}
        }
    
    def _create_progress_indicator_template(self) -> Dict[str, Any]:
        """Create progress indicator template."""
        return {
            "type": "progress_indicator",
            "status": "in_progress",
            "progress": 0,
            "message": "",
            "estimated_completion": None,
            "metadata": {}
        }
    
    def _create_action_buttons_template(self) -> Dict[str, Any]:
        """Create action buttons template."""
        return {
            "type": "action_buttons",
            "buttons": [],
            "alignment": "right",
            "metadata": {}
        }
    
    def _create_error_display_template(self) -> Dict[str, Any]:
        """Create error display template."""
        return {
            "type": "error_display",
            "error_type": "error",
            "message": "",
            "details": {},
            "actions": [],
            "metadata": {}
        }
    
    async def format_output(self, results: Dict[str, Any], agent_id: str, session_id: str, 
                          capabilities: List[str], expertise: str = None) -> Dict[str, Any]:
        """
        Format agent execution results into AGUI-compliant output with multi-tenant awareness.
        
        Args:
            results: Agent execution results
            agent_id: Agent identifier
            session_id: Session identifier
            capabilities: Agent capabilities
            expertise: Agent expertise domain
            tenant_context: Tenant context for multi-tenant operations
            
        Returns:
            Dict containing AGUI-formatted output
        """
        try:
            agui_output = {
                "type": "agent_output",
                "version": "1.0",
                "agent_id": agent_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "expertise": expertise,
                "capabilities": capabilities,
                "components": []
            }
            
            # Process results and create components
            if results.get("success", False):
                components = await self._create_success_components(results)
            else:
                components = await self._create_error_components(results)
            
            agui_output["components"] = components
            
            self.logger.info(f"AGUI output formatted for agent {agent_id}")
            return agui_output
            
        except Exception as e:
            self.logger.error(f"Failed to format AGUI output: {e}")
            self.error_handler.handle_error(e, "agui_output_formatting_failed")
            return self._create_error_output(agent_id, session_id, str(e))
    
    async def _create_success_components(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create AGUI components for successful execution."""
        try:
            components = []
            
            # Create analysis card if analysis results exist
            if "analysis_results" in results:
                analysis_card = await self._create_analysis_card(results["analysis_results"])
                components.append(analysis_card)
            
            # Create data table if data exists
            if "data" in results:
                data_table = await self._create_data_table(results["data"])
                components.append(data_table)
            
            # Create visualizations if chart data exists
            if "visualizations" in results:
                for viz_data in results["visualizations"]:
                    visualization = await self._create_visualization(viz_data)
                    components.append(visualization)
            
            # Create action buttons
            action_buttons = await self._create_action_buttons(results)
            components.append(action_buttons)
            
            return components
            
        except Exception as e:
            self.logger.error(f"Failed to create success components: {e}")
            return [await self._create_error_component(str(e))]
    
    async def _create_error_components(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create AGUI components for error cases."""
        try:
            components = []
            
            # Create error display
            error_display = await self._create_error_display(results)
            components.append(error_display)
            
            return components
            
        except Exception as e:
            self.logger.error(f"Failed to create error components: {e}")
            return [await self._create_error_component(str(e))]
    
    async def _create_analysis_card(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create analysis card component."""
        try:
            card = self.component_templates["analysis_card"].copy()
            
            card.update({
                "title": analysis_data.get("title", "Analysis Results"),
                "status": analysis_data.get("status", "completed"),
                "metrics": analysis_data.get("metrics", {}),
                "visualizations": analysis_data.get("charts", []),
                "actions": [
                    {"type": "download", "label": "Export Results", "action": "export"},
                    {"type": "share", "label": "Share Analysis", "action": "share"},
                    {"type": "schedule", "label": "Schedule Recurring", "action": "schedule"}
                ],
                "metadata": {
                    "analysis_id": analysis_data.get("analysis_id"),
                    "timestamp": analysis_data.get("timestamp"),
                    "confidence": analysis_data.get("confidence", 0.8)
                }
            })
            
            return card
            
        except Exception as e:
            self.logger.error(f"Failed to create analysis card: {e}")
            return await self._create_error_component(f"Analysis card creation failed: {e}")
    
    async def _create_data_table(self, data: Any) -> Dict[str, Any]:
        """Create data table component."""
        try:
            table = self.component_templates["data_table"].copy()
            
            # Handle different data types
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    # List of dictionaries
                    columns = list(data[0].keys())
                    table_data = data
                else:
                    # Simple list
                    columns = ["value"]
                    table_data = [{"value": item} for item in data]
            elif hasattr(data, 'to_dict'):
                # Pandas DataFrame
                df_dict = data.to_dict("records")
                columns = list(df_dict[0].keys()) if df_dict else []
                table_data = df_dict
            else:
                # Fallback
                columns = ["data"]
                table_data = [{"data": str(data)}]
            
            table.update({
                "columns": columns,
                "data": table_data,
                "pagination": {
                    "page_size": 50,
                    "total_rows": len(table_data),
                    "current_page": 1
                },
                "sorting": {
                    "enabled": True,
                    "default_sort": columns[0] if columns else None
                },
                "filtering": {
                    "enabled": True,
                    "filters": ["text_search", "date_range"] if columns else []
                },
                "metadata": {
                    "row_count": len(table_data),
                    "column_count": len(columns)
                }
            })
            
            return table
            
        except Exception as e:
            self.logger.error(f"Failed to create data table: {e}")
            return await self._create_error_component(f"Data table creation failed: {e}")
    
    async def _create_visualization(self, viz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create visualization component."""
        try:
            viz = self.component_templates["visualization"].copy()
            
            viz.update({
                "chart_type": viz_data.get("chart_type", "line_chart"),
                "data": viz_data.get("data", {}),
                "options": viz_data.get("options", {}),
                "interactive": viz_data.get("interactive", True),
                "metadata": {
                    "title": viz_data.get("title", "Chart"),
                    "description": viz_data.get("description", ""),
                    "created_at": datetime.now().isoformat()
                }
            })
            
            return viz
            
        except Exception as e:
            self.logger.error(f"Failed to create visualization: {e}")
            return await self._create_error_component(f"Visualization creation failed: {e}")
    
    async def _create_action_buttons(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create action buttons component."""
        try:
            buttons = self.component_templates["action_buttons"].copy()
            
            # Default actions
            default_actions = [
                {"type": "primary", "label": "View Details", "action": "view_details"},
                {"type": "secondary", "label": "Export", "action": "export"},
                {"type": "secondary", "label": "Share", "action": "share"}
            ]
            
            # Add context-specific actions
            if results.get("analysis_results"):
                default_actions.append({"type": "secondary", "label": "Re-run Analysis", "action": "rerun"})
            
            if results.get("data"):
                default_actions.append({"type": "secondary", "label": "Download Data", "action": "download"})
            
            buttons.update({
                "buttons": default_actions,
                "alignment": "right",
                "metadata": {
                    "context": "agent_results",
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            return buttons
            
        except Exception as e:
            self.logger.error(f"Failed to create action buttons: {e}")
            return await self._create_error_component(f"Action buttons creation failed: {e}")
    
    async def _create_error_display(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create error display component."""
        try:
            error_display = self.component_templates["error_display"].copy()
            
            error_display.update({
                "error_type": "error",
                "message": results.get("error", "An unknown error occurred"),
                "details": {
                    "agent_id": results.get("agent_id"),
                    "timestamp": results.get("timestamp"),
                    "error_code": results.get("error_code", "UNKNOWN")
                },
                "actions": [
                    {"type": "primary", "label": "Retry", "action": "retry"},
                    {"type": "secondary", "label": "Report Issue", "action": "report"}
                ],
                "metadata": {
                    "session_id": results.get("session_id"),
                    "capabilities": results.get("capabilities", [])
                }
            })
            
            return error_display
            
        except Exception as e:
            self.logger.error(f"Failed to create error display: {e}")
            return await self._create_error_component(f"Error display creation failed: {e}")
    
    async def _create_error_component(self, error_message: str) -> Dict[str, Any]:
        """Create generic error component."""
        return {
            "type": "error_display",
            "error_type": "error",
            "message": error_message,
            "details": {},
            "actions": [
                {"type": "primary", "label": "Retry", "action": "retry"}
            ],
            "metadata": {
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _create_error_output(self, agent_id: str, session_id: str, error_message: str) -> Dict[str, Any]:
        """Create error output when formatting fails."""
        return {
            "type": "agent_output",
            "version": "1.0",
            "agent_id": agent_id,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "components": [
                {
                    "type": "error_display",
                    "error_type": "critical",
                    "message": f"Output formatting failed: {error_message}",
                    "details": {},
                    "actions": [
                        {"type": "primary", "label": "Retry", "action": "retry"}
                    ],
                    "metadata": {}
                }
            ]
        }
    
    async def create_analysis_card(self, title: str, metrics: Dict[str, Any], visualizations: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create an analysis card component."""
        try:
            analysis_data = {
                "title": title,
                "metrics": metrics,
                "visualizations": visualizations or []
            }
            
            card = await self._create_analysis_card(analysis_data)
            return card
            
        except Exception as e:
            self.logger.error(f"Failed to create analysis card: {e}")
            return await self._create_error_component(f"Failed to create analysis card: {str(e)}")
    
    async def _initialize_service(self):
        """Initialize AGUI formatter specific functionality."""
        # AGUI formatter doesn't need additional initialization beyond templates
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the AGUI formatter."""
        return {
            "status": "healthy" if self.is_initialized else "not_initialized",
            "component_templates": len(self.component_templates),
            "tenant_context": {
                "tenant_id": self.tenant_id,
                "tenant_user_id": self.tenant_user_id,
                "isolation_enabled": self.tenant_isolation_enabled
            },
            "agentic_abstractions_count": len(self.agentic_abstractions),
            "timestamp": datetime.now().isoformat()
        }



