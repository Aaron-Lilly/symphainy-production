#!/usr/bin/env python3
"""
AGUI Output Formatter - Agentic Realm Business Service

Generates standardized AGUI-compliant outputs for agent responses as a business service.
Handles structured output generation, component formatting, and Post Office integration.

WHAT (Agentic Role): I provide structured AGUI-compliant output generation for agent responses
HOW (Business Service): I orchestrate output formatting and route through Post Office infrastructure
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.agui_communication_protocol import (
    AGUIMessage, AGUIResponse, AGUIEvent
)

# Import utility mixins (minimal - AgenticFoundationService wraps calls)
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin


class AGUIOutputFormatter(UtilityAccessMixin, PerformanceMonitoringMixin):
    """
    AGUI Output Formatter - Agentic Realm Business Service
    
    Generates standardized AGUI-compliant outputs for agent responses.
    Handles structured output generation, component formatting, and Post Office integration.
    
    This is a BUSINESS SERVICE that orchestrates output formatting and routes
    structured outputs through Post Office infrastructure for delivery.
    """
    
    def __init__(self, post_office_service=None, di_container=None):
        """Initialize AGUI Output Formatter with Post Office service."""
        if not di_container:
            raise ValueError("DI Container is required for AGUIOutputFormatter initialization")
        
        # Initialize utility mixins (minimal - AgenticFoundationService wraps calls)
        self._init_utility_access(di_container)
        self._init_performance_monitoring(di_container)
        
        self.post_office_service = post_office_service
        self.di_container = di_container
        self.service_name = "agui_output_formatter"
        
        # Component templates
        self.component_templates = {
            "analysis_card": self._create_analysis_card_template(),
            "data_table": self._create_data_table_template(),
            "visualization": self._create_visualization_template(),
            "progress_indicator": self._create_progress_indicator_template(),
            "action_buttons": self._create_action_buttons_template(),
            "error_display": self._create_error_display_template()
        }
        
        # Business metrics
        self.business_metrics = {
            "total_outputs_generated": 0,
            "component_types_used": {},
            "successful_deliveries": 0,
            "failed_deliveries": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        self.logger.info("✅ AGUI Output Formatter (Business Service) initialized")
    
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
            "spacing": "normal",
            "metadata": {}
        }
    
    def _create_error_display_template(self) -> Dict[str, Any]:
        """Create error display template."""
        return {
            "type": "error_display",
            "error_type": "warning",
            "title": "",
            "message": "",
            "details": {},
            "actions": [],
            "metadata": {}
        }
    
    async def format_agent_response(self, agent_name: str, response_data: Dict[str, Any], 
                                  output_type: str = "analysis_card", 
                                  recipient_id: str = None,
                                  tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format agent response into AGUI-compliant structured output.
        
        Args:
            agent_name: Name of the agent generating the response
            response_data: Raw response data from agent
            output_type: Type of AGUI component to generate
            recipient_id: ID of the recipient (if specific)
            tenant_context: Tenant context for multi-tenancy
            
        Returns:
            Dict containing formatted AGUI output
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("format_agent_response_start", success=True, 
                                                   details={"agent_name": agent_name, "output_type": output_type})
            
            # Security validation (zero-trust: secure by design)
            # Note: tenant_context is passed in, but we should validate if user_context is provided
            # For now, we'll validate tenant_context if provided
            if tenant_context:
                security = self.get_security()
                if security:
                    # Create user_context from tenant_context for validation
                    user_context_for_validation = {"tenant_id": tenant_context.get("tenant_id")}
                    if not await security.check_permissions(user_context_for_validation, "agui_formatter", "write"):
                        await self.record_health_metric("format_agent_response_access_denied", 1.0, {"agent_name": agent_name})
                        await self.log_operation_with_telemetry("format_agent_response_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("format_agent_response_tenant_denied", 1.0, {"agent_name": agent_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("format_agent_response_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            self.logger.info(f"🎨 Formatting {output_type} output for agent {agent_name}")
            
            # Get component template
            if output_type not in self.component_templates:
                raise ValueError(f"Unknown output type: {output_type}")
            
            template = self.component_templates[output_type].copy()
            
            # Format the response data into the component
            formatted_component = await self._format_component_data(
                template, response_data, agent_name, tenant_context
            )
            
            # Create AGUI message for delivery
            agui_message = await self._create_agui_message(
                agent_name=agent_name,
                component=formatted_component,
                recipient_id=recipient_id,
                tenant_context=tenant_context
            )
            
            # Route through Post Office if available
            if self.post_office_service:
                delivery_result = await self._deliver_via_post_office(
                    agui_message, recipient_id, tenant_context
                )
                formatted_component["delivery_status"] = delivery_result
            
            # Update business metrics
            self._update_business_metrics(output_type, True)
            
            # Record success metric
            await self.record_health_metric("format_agent_response_success", 1.0, {"agent_name": agent_name, "output_type": output_type})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("format_agent_response_complete", success=True, 
                                                   details={"agent_name": agent_name, "output_type": output_type})
            
            self.logger.info(f"✅ Formatted {output_type} output for agent {agent_name}")
            return {
                "success": True,
                "component": formatted_component,
                "agui_message": agui_message,
                "agent_name": agent_name,
                "output_type": output_type,
                "formatted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "format_agent_response", 
                                              details={"agent_name": agent_name, "output_type": output_type})
            self.logger.error(f"❌ Failed to format agent response: {e}")
            self._update_business_metrics(output_type, False)
            
            return {
                "success": False,
                "error": str(e),
                "agent_name": agent_name,
                "output_type": output_type
            }
    
    async def _format_component_data(self, template: Dict[str, Any], 
                                   response_data: Dict[str, Any], 
                                   agent_name: str,
                                   tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format response data into component structure."""
        try:
            component = template.copy()
            
            # Add agent context
            component["agent_name"] = agent_name
            component["generated_at"] = datetime.now().isoformat()
            
            if tenant_context:
                component["tenant_context"] = tenant_context
            
            # Format based on component type
            if component["type"] == "analysis_card":
                component = await self._format_analysis_card(component, response_data)
            elif component["type"] == "data_table":
                component = await self._format_data_table(component, response_data)
            elif component["type"] == "visualization":
                component = await self._format_visualization(component, response_data)
            elif component["type"] == "progress_indicator":
                component = await self._format_progress_indicator(component, response_data)
            elif component["type"] == "action_buttons":
                component = await self._format_action_buttons(component, response_data)
            elif component["type"] == "error_display":
                component = await self._format_error_display(component, response_data)
            
            return component
            
        except Exception as e:
            self.logger.error(f"❌ Failed to format component data: {e}")
            raise
    
    async def _format_analysis_card(self, component: Dict[str, Any], 
                                  response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis card component."""
        component["title"] = response_data.get("title", "Analysis Results")
        component["status"] = response_data.get("status", "completed")
        component["metrics"] = response_data.get("metrics", {})
        component["visualizations"] = response_data.get("visualizations", [])
        component["actions"] = response_data.get("actions", [])
        component["metadata"] = response_data.get("metadata", {})
        
        return component
    
    async def _format_data_table(self, component: Dict[str, Any], 
                               response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data table component."""
        component["columns"] = response_data.get("columns", [])
        component["data"] = response_data.get("data", [])
        component["pagination"] = response_data.get("pagination", component["pagination"])
        component["sorting"] = response_data.get("sorting", component["sorting"])
        component["filtering"] = response_data.get("filtering", component["filtering"])
        component["metadata"] = response_data.get("metadata", {})
        
        return component
    
    async def _format_visualization(self, component: Dict[str, Any], 
                                  response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format visualization component."""
        component["chart_type"] = response_data.get("chart_type", "line_chart")
        component["data"] = response_data.get("data", {})
        component["options"] = response_data.get("options", {})
        component["interactive"] = response_data.get("interactive", True)
        component["metadata"] = response_data.get("metadata", {})
        
        return component
    
    async def _format_progress_indicator(self, component: Dict[str, Any], 
                                       response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format progress indicator component."""
        component["status"] = response_data.get("status", "in_progress")
        component["progress"] = response_data.get("progress", 0)
        component["message"] = response_data.get("message", "")
        component["estimated_completion"] = response_data.get("estimated_completion")
        component["metadata"] = response_data.get("metadata", {})
        
        return component
    
    async def _format_action_buttons(self, component: Dict[str, Any], 
                                   response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format action buttons component."""
        component["buttons"] = response_data.get("buttons", [])
        component["alignment"] = response_data.get("alignment", "right")
        component["spacing"] = response_data.get("spacing", "normal")
        component["metadata"] = response_data.get("metadata", {})
        
        return component
    
    async def _format_error_display(self, component: Dict[str, Any], 
                                  response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format error display component."""
        component["error_type"] = response_data.get("error_type", "warning")
        component["title"] = response_data.get("title", "Error")
        component["message"] = response_data.get("message", "")
        component["details"] = response_data.get("details", {})
        component["actions"] = response_data.get("actions", [])
        component["metadata"] = response_data.get("metadata", {})
        
        return component
    
    async def _create_agui_message(self, agent_name: str, component: Dict[str, Any],
                                 recipient_id: str = None,
                                 tenant_context: Dict[str, Any] = None) -> AGUIMessage:
        """Create AGUI message for delivery."""
        message_id = str(uuid.uuid4())
        
        payload = {
            "component": component,
            "agent_name": agent_name,
            "recipient_id": recipient_id,
            "tenant_context": tenant_context,
            "message_type": "agui_output"
        }
        
        return AGUIMessage(
            message_id=message_id,
            action="deliver_agui_output",
            payload=payload,
            timestamp=datetime.now(),
            connection_id=recipient_id or "broadcast"
        )
    
    async def _deliver_via_post_office(self, agui_message: AGUIMessage, 
                                     recipient_id: str = None,
                                     tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Deliver AGUI message via Post Office service."""
        try:
            if not self.post_office_service:
                return {"success": False, "error": "Post Office service not available"}
            
            # Create message data for Post Office
            message_data = {
                "recipient_id": recipient_id or "broadcast",
                "content": agui_message.payload,
                "message_type": "agui_output",
                "sender_id": agui_message.payload.get("agent_name", "system"),
                "priority": "normal"
            }
            
            # Send via Post Office
            result = await self.post_office_service.send_message(message_data, tenant_context)
            
            if result.get("status") == "success":
                self.business_metrics["successful_deliveries"] += 1
                return {"success": True, "delivery_id": result.get("message_id")}
            else:
                self.business_metrics["failed_deliveries"] += 1
                return {"success": False, "error": result.get("message")}
                
        except Exception as e:
            self.logger.error(f"❌ Failed to deliver via Post Office: {e}")
            self.business_metrics["failed_deliveries"] += 1
            return {"success": False, "error": str(e)}
    
    def _update_business_metrics(self, output_type: str, success: bool):
        """Update business metrics."""
        self.business_metrics["total_outputs_generated"] += 1
        self.business_metrics["last_updated"] = datetime.now().isoformat()
        
        if output_type not in self.business_metrics["component_types_used"]:
            self.business_metrics["component_types_used"][output_type] = 0
        self.business_metrics["component_types_used"][output_type] += 1
    
    def get_business_metrics(self) -> Dict[str, Any]:
        """Get business metrics for AGUI output formatting."""
        return self.business_metrics.copy()
    
    async def get_available_component_types(self, user_context: Dict[str, Any] = None) -> List[str]:
        """Get list of available component types."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_available_component_types_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_formatter", "read"):
                        await self.record_health_metric("get_available_component_types_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_available_component_types_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_available_component_types_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_available_component_types_complete", success=False)
                            return []
            
            result = list(self.component_templates.keys())
            
            # Record success metric
            await self.record_health_metric("get_available_component_types_success", 1.0, {"component_types_count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_available_component_types_complete", success=True, 
                                                   details={"component_types_count": len(result)})
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_available_component_types")
            return []
    
    def get_component_template(self, component_type: str) -> Dict[str, Any]:
        """Get template for specific component type."""
        return self.component_templates.get(component_type, {})
    
    async def get_formatter_health(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get AGUI Output Formatter health status."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_formatter_health_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agui_formatter", "read"):
                        await self.record_health_metric("get_formatter_health_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_formatter_health_complete", success=False)
                        return {"success": False, "error": "Access denied"}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_formatter_health_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_formatter_health_complete", success=False)
                            return {"success": False, "error": "Tenant access denied"}
            
            # Get available component types (now async)
            component_types = await self.get_available_component_types(user_context)
            
            result = {
                "service_name": "AGUIOutputFormatter",
                "service_type": "business_service",
                "realm": "agentic",
                "post_office_available": self.post_office_service is not None,
                "available_component_types": component_types,
                "business_metrics": self.get_business_metrics(),
                "status": "healthy"
            }
            
            # Record success metric
            await self.record_health_metric("get_formatter_health_success", 1.0, {})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_formatter_health_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_formatter_health")
            return {"success": False, "error": str(e), "status": "error"}


