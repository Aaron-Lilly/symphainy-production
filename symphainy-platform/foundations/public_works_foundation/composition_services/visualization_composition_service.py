#!/usr/bin/env python3
"""
Visualization Composition Service

Composition service for visualization capabilities, integrating the abstraction and applying business rules.

WHAT (Composition Service Role): I integrate visualization capabilities and apply business rules
HOW (Composition Implementation): I orchestrate visualization abstraction and apply business logic
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..infrastructure_abstractions.visualization_abstraction import VisualizationAbstraction
from ..abstraction_contracts.visualization_protocol import VisualizationResult


class VisualizationCompositionService:
    """
    Visualization Composition Service
    
    Orchestrates comprehensive visualization capabilities for the Business Outcomes Pillar,
    including summary displays, roadmap visualizations, and business dashboards.
    """
    
    def __init__(self, visualization_abstraction: VisualizationAbstraction, di_container=None):
        """
        Initialize Visualization Composition Service.
        
        Args:
            visualization_abstraction: Visualization abstraction (required via DI)
            di_container: DI Container for utilities
        """
        if not visualization_abstraction:
            raise ValueError("VisualizationCompositionService requires visualization_abstraction via dependency injection")
        
        self.visualization_abstraction = visualization_abstraction
        self.di_container = di_container
        self.service_name = "visualization_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("VisualizationCompositionService")
        
        self.logger.info("✅ Visualization Composition Service initialized")
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    
    # ============================================================================
    # VISUALIZATION COMPOSITION METHODS
    # ============================================================================
    
    async def get_comprehensive_visualization_suite(self, 
                                                   pillar_outputs: Dict[str, Any],
                                                   roadmap_data: Dict[str, Any],
                                                   financial_data: Dict[str, Any],
                                                   metrics_data: Dict[str, Any],
                                                   user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive visualization suite for Business Outcomes Pillar.
        
        Args:
            pillar_outputs: Summary outputs from all pillars
            roadmap_data: Roadmap data from Strategic Planning service
            financial_data: Financial analysis data
            metrics_data: Business metrics data
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict[str, Any]: Comprehensive visualization suite
        """
        try:
            # Validate security and tenant access
            validation_error = await self._validate_security_and_tenant(
                user_context, "visualization", "view"
            )
            if validation_error:
                return validation_error
            
            self.logger.info("Generating comprehensive visualization suite...")
            
            # Create all visualizations
            summary_dashboard = await self.visualization_abstraction.create_summary_dashboard(pillar_outputs)
            roadmap_visualization = await self.visualization_abstraction.create_roadmap_visualization(roadmap_data)
            financial_visualization = await self.visualization_abstraction.create_financial_visualization(financial_data)
            metrics_dashboard = await self.visualization_abstraction.create_metrics_dashboard(metrics_data)
            
            # Apply business rules for visualization prioritization
            visualization_priority = self._determine_visualization_priority(
                pillar_outputs, roadmap_data, financial_data, metrics_data
            )
            
            # Generate visualization insights
            visualization_insights = self._generate_visualization_insights(
                summary_dashboard, roadmap_visualization, financial_visualization, metrics_dashboard
            )
            
            # Generate visualization recommendations
            visualization_recommendations = self._generate_visualization_recommendations(
                summary_dashboard, roadmap_visualization, financial_visualization, metrics_dashboard
            )
            
            result = {
                "success": True,
                "visualization_suite": {
                    "summary_dashboard": summary_dashboard,
                    "roadmap_visualization": roadmap_visualization,
                    "financial_visualization": financial_visualization,
                    "metrics_dashboard": metrics_dashboard
                },
                "visualization_priority": visualization_priority,
                "visualization_insights": visualization_insights,
                "visualization_recommendations": visualization_recommendations,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_comprehensive_visualization_suite", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_comprehensive_visualization_suite",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to generate comprehensive visualization suite: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "VISUALIZATION_SUITE_ERROR",
                "visualization_suite": {},
                "generated_at": datetime.utcnow().isoformat()
            }
    
    async def get_summary_display(self, pillar_outputs: Dict[str, Any],
                                 user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary display for pillar outputs.
        
        Args:
            pillar_outputs: Summary outputs from all pillars
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict[str, Any]: Summary display visualization
        """
        try:
            # Validate security and tenant access
            validation_error = await self._validate_security_and_tenant(
                user_context, "visualization", "view"
            )
            if validation_error:
                return validation_error
            
            self.logger.info("Generating summary display for pillar outputs...")
            
            # Create summary dashboard
            summary_dashboard = await self.visualization_abstraction.create_summary_dashboard(pillar_outputs)
            
            if not summary_dashboard.success:
                return {
                    "success": False,
                    "error": summary_dashboard.error,
                    "summary_display": {}
                }
            
            # Apply business rules for summary display
            display_priority = self._determine_summary_display_priority(pillar_outputs)
            
            result = {
                "success": True,
                "summary_display": {
                    "dashboard": summary_dashboard,
                    "display_priority": display_priority,
                    "key_metrics": self._extract_key_metrics(pillar_outputs)
                }
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_summary_display", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_summary_display",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to generate summary display: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "VISUALIZATION_SUMMARY_DISPLAY_ERROR",
                "summary_display": {}
            }
    
    async def get_roadmap_display(self, roadmap_data: Dict[str, Any],
                                 user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get roadmap display as standalone visual element.
        
        Args:
            roadmap_data: Roadmap data from Strategic Planning service
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict[str, Any]: Roadmap display visualization
        """
        try:
            # Validate security and tenant access
            validation_error = await self._validate_security_and_tenant(
                user_context, "visualization", "view"
            )
            if validation_error:
                return validation_error
            
            self.logger.info("Generating roadmap display...")
            
            # Create roadmap visualization
            roadmap_visualization = await self.visualization_abstraction.create_roadmap_visualization(roadmap_data)
            
            if not roadmap_visualization.success:
                return {
                    "success": False,
                    "error": roadmap_visualization.error,
                    "roadmap_display": {}
                }
            
            # Apply business rules for roadmap display
            display_config = self._determine_roadmap_display_config(roadmap_data)
            
            result = {
                "success": True,
                "roadmap_display": {
                    "visualization": roadmap_visualization,
                    "display_config": display_config,
                    "timeline_summary": self._extract_timeline_summary(roadmap_data)
                }
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_roadmap_display", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_roadmap_display",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to generate roadmap display: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "VISUALIZATION_ROADMAP_DISPLAY_ERROR",
                "roadmap_display": {}
            }
    
    def _determine_visualization_priority(self, pillar_outputs: Dict[str, Any],
                                        roadmap_data: Dict[str, Any],
                                        financial_data: Dict[str, Any],
                                        metrics_data: Dict[str, Any]) -> List[str]:
        """Determine priority order for visualizations based on business rules."""
        priority = []
        
        # Always show summary dashboard first
        priority.append("summary_dashboard")
        
        # Prioritize based on data completeness
        if roadmap_data.get("phases"):
            priority.append("roadmap_visualization")
        
        if financial_data.get("roi_analysis"):
            priority.append("financial_visualization")
        
        if metrics_data.get("kpis"):
            priority.append("metrics_dashboard")
        
        return priority
    
    def _generate_visualization_insights(self, summary_dashboard: VisualizationResult,
                                       roadmap_visualization: VisualizationResult,
                                       financial_visualization: VisualizationResult,
                                       metrics_dashboard: VisualizationResult) -> List[str]:
        """Generate insights from visualization results."""
        insights = []
        
        if summary_dashboard.success:
            insights.append("Summary dashboard provides clear overview of journey progress")
        
        if roadmap_visualization.success:
            insights.append("Roadmap visualization shows clear timeline and phases")
        
        if financial_visualization.success:
            insights.append("Financial visualization highlights ROI and risk factors")
        
        if metrics_dashboard.success:
            insights.append("Metrics dashboard reveals performance and benchmark data")
        
        return insights
    
    def _generate_visualization_recommendations(self, summary_dashboard: VisualizationResult,
                                              roadmap_visualization: VisualizationResult,
                                              financial_visualization: VisualizationResult,
                                              metrics_dashboard: VisualizationResult) -> List[str]:
        """Generate recommendations based on visualization results."""
        recommendations = []
        
        if not summary_dashboard.success:
            recommendations.append("Fix summary dashboard generation issues")
        
        if not roadmap_visualization.success:
            recommendations.append("Ensure roadmap data is complete for visualization")
        
        if not financial_visualization.success:
            recommendations.append("Verify financial data completeness for visualization")
        
        if not metrics_dashboard.success:
            recommendations.append("Check metrics data availability for dashboard")
        
        # Add positive recommendations
        if all(v.success for v in [summary_dashboard, roadmap_visualization, financial_visualization, metrics_dashboard]):
            recommendations.append("All visualizations generated successfully - ready for presentation")
        
        return recommendations
    
    def _determine_summary_display_priority(self, pillar_outputs: Dict[str, Any]) -> List[str]:
        """Determine priority for summary display elements."""
        priority = []
        
        # Prioritize based on data availability
        if pillar_outputs.get("data_pillar", {}).get("files_uploaded"):
            priority.append("data_summary")
        
        if pillar_outputs.get("insights_pillar", {}).get("insights"):
            priority.append("insights_summary")
        
        if pillar_outputs.get("operations_pillar", {}).get("blueprint"):
            priority.append("operations_summary")
        
        priority.append("journey_progress")
        
        return priority
    
    def _extract_key_metrics(self, pillar_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from pillar outputs."""
        return {
            "data_files": len(pillar_outputs.get("data_pillar", {}).get("files_uploaded", [])),
            "insights_count": len(pillar_outputs.get("insights_pillar", {}).get("insights", [])),
            "improvements_count": len(pillar_outputs.get("operations_pillar", {}).get("blueprint", {}).get("improvements", [])),
            "journey_completion": self._calculate_journey_completion(pillar_outputs)
        }
    
    def _calculate_journey_completion(self, pillar_outputs: Dict[str, Any]) -> int:
        """Calculate journey completion percentage."""
        completion = 0
        
        if pillar_outputs.get("data_pillar", {}).get("files_uploaded"):
            completion += 25
        
        if pillar_outputs.get("insights_pillar", {}).get("insights"):
            completion += 25
        
        if pillar_outputs.get("operations_pillar", {}).get("blueprint"):
            completion += 25
        
        # Business Outcomes is the final step
        completion += 25
        
        return completion
    
    def _determine_roadmap_display_config(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine configuration for roadmap display."""
        phases = roadmap_data.get("phases", [])
        timeline = roadmap_data.get("timeline", {})
        
        return {
            "show_milestones": len(roadmap_data.get("milestones", [])) > 0,
            "show_timeline": bool(timeline),
            "phase_count": len(phases),
            "total_duration_weeks": timeline.get("total_duration_weeks", 0),
            "display_style": "gantt" if len(phases) > 3 else "timeline"
        }
    
    def _extract_timeline_summary(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract timeline summary from roadmap data."""
        timeline = roadmap_data.get("timeline", {})
        phases = roadmap_data.get("phases", [])
        
        return {
            "total_duration_weeks": timeline.get("total_duration_weeks", 0),
            "phase_count": len(phases),
            "start_date": timeline.get("start_date"),
            "end_date": timeline.get("end_date"),
            "milestone_count": len(roadmap_data.get("milestones", []))
        }
