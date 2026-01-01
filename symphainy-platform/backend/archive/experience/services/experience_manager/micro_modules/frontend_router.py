#!/usr/bin/env python3
"""
Frontend Router Micro-Module

Routes frontend requests to appropriate backend services and manages API coordination.

WHAT (Micro-Module): I route frontend requests to backend services
HOW (Implementation): I use routing rules, service discovery, and API coordination patterns
"""

import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from datetime import datetime
import re

from utilities import UserContext
from config.environment_loader import EnvironmentLoader

if TYPE_CHECKING:
    from typing import Any


class FrontendRouterModule:
    """
    Frontend Router Micro-Module
    
    Provides functionality to route frontend requests to appropriate backend services.
    """
    
    def __init__(self, environment: EnvironmentLoader, logger: Optional[logging.Logger] = None, parent_service: Any = None):
        """Initialize Frontend Router Module."""
        self.environment = environment
        self.logger = logger or logging.getLogger(__name__)
        self.parent_service = parent_service  # ExperienceManagerService reference
        self.is_initialized = False
        self.di_container = None
        self.business_orchestrator = None
        
        # Routing rules and patterns
        self.routing_rules = {
            # Content Pillar routes
            "content": {
                "upload_file": "/content/upload",
                "get_files": "/content/files",
                "parse_file": "/content/parse",
                "get_file_metadata": "/content/metadata"
            },
            # Insights Pillar routes
            "insights": {
                "analyze_data": "/insights/analyze",
                "get_visualizations": "/insights/visualizations",
                "generate_report": "/insights/report",
                "get_insights": "/insights/insights"
            },
            # Operations Pillar routes
            "operations": {
                "create_sop": "/operations/sop/create",
                "create_workflow": "/operations/workflow/create",
                "convert_sop_to_workflow": "/operations/convert/sop-to-workflow",
                "optimize_process": "/operations/optimize"
            },
            # Business Outcomes Pillar routes
            "business_outcomes": {
                "create_strategic_plan": "/business_outcomes/strategic_plan",
                "calculate_roi": "/business_outcomes/roi",
                "measure_outcomes": "/business_outcomes/measure",
                "get_metrics": "/business_outcomes/metrics"
            },
            # Experience routes
            "experience": {
                "get_session_state": "/experience/session/state",
                "update_session_state": "/experience/session/update",
                "get_available_pillars": "/experience/pillars"
            }
        }
        
        # API endpoint patterns
        self.api_patterns = {
            r"^/api/content/.*": "content",
            r"^/api/insights/.*": "insights", 
            r"^/api/operations/.*": "operations",
            r"^/api/business-outcomes/.*": "business_outcomes",
            r"^/api/experience/.*": "experience"
        }
        
        # Available pillars and their status
        self.available_pillars = {
            "content": {"status": "available", "endpoint": "content_pillar_service"},
            "insights": {"status": "available", "endpoint": "insights_pillar_service"},
            "operations": {"status": "available", "endpoint": "operations_pillar_service"},
            "business_outcomes": {"status": "available", "endpoint": "business_outcomes_orchestrator", "router": "/api/business-outcomes-pillar"}
        }
        
        # Permission configuration
        # MVP: All pillars are open/accessible (no restrictions)
        # Future: Configure pillar access permissions here
        self.pillar_permissions = {
            "content": {
                "required_permission": None,  # None = open access (MVP)
                "restricted": False  # MVP: all pillars are public
            },
            "insights": {
                "required_permission": None,
                "restricted": False
            },
            "operations": {
                "required_permission": None,
                "restricted": False
            },
            "business_outcomes": {
                "required_permission": None,
                "restricted": False
            }
        }
        
        # MVP mode: open permissions for all pillars
        self.mvp_mode_open_permissions = True
        
        self.logger.info("🛣️ Frontend Router Module initialized")
    
    async def initialize(self):
        """Initialize the Frontend Router Module."""
        self.logger.info("🚀 Initializing Frontend Router Module...")
        
        # Get DI container from parent service
        if self.parent_service and hasattr(self.parent_service, 'di_container'):
            self.di_container = self.parent_service.di_container
            self.logger.info("✅ DI Container accessed from parent service")
        
        # Get Business Orchestrator via parent service (if available)
        if self.parent_service and hasattr(self.parent_service, 'get_business_orchestrator'):
            try:
                self.business_orchestrator = await self.parent_service.get_business_orchestrator()
                if self.business_orchestrator:
                    self.logger.info("✅ Business Orchestrator accessed from parent service")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not get Business Orchestrator: {e}")
        
        self.is_initialized = True
        self.logger.info("✅ Frontend Router Module initialized successfully")
    
    async def shutdown(self):
        """Shutdown the Frontend Router Module."""
        self.logger.info("🛑 Shutting down Frontend Router Module...")
        # Clean up resources here
        self.is_initialized = False
        self.logger.info("✅ Frontend Router Module shutdown successfully")
    
    async def coordinate_request(self, request_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Coordinate a frontend request to appropriate backend services.
        
        Args:
            request_data: The request data from frontend.
            user_context: Context of the user.
            
        Returns:
            A dictionary containing the coordinated response.
        """
        self.logger.debug("Coordinating frontend request")
        
        try:
            # Extract request information
            endpoint = request_data.get("endpoint", "")
            method = request_data.get("method", "GET")
            payload = request_data.get("payload", {})
            
            # Determine target pillar
            target_pillar = await self._determine_target_pillar(endpoint)
            
            if not target_pillar:
                return {
                    "success": False,
                    "error": "Unknown endpoint",
                    "message": f"Could not determine target pillar for endpoint: {endpoint}"
                }
            
            # Route to appropriate pillar
            routing_result = await self.route_to_pillar(target_pillar, {
                "endpoint": endpoint,
                "method": method,
                "payload": payload
            }, user_context)
            
            return {
                "success": True,
                "target_pillar": target_pillar,
                "routing_result": routing_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to coordinate request: {e}")
            return {"success": False, "error": str(e), "message": "Failed to coordinate request"}
    
    async def route_to_pillar(self, pillar_name: str, request_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Route a request to a specific business pillar.
        
        Includes permission checking before routing.
        
        Args:
            pillar_name: The target pillar (content, insights, operations, business_outcomes).
            request_data: The request data to route.
            user_context: Context of the user.
            
        Returns:
            A dictionary containing the pillar response.
        """
        self.logger.debug(f"Routing request to pillar: {pillar_name} for user: {user_context.user_id}")
        
        try:
            # Check if pillar is available
            if pillar_name not in self.available_pillars:
                return {
                    "success": False,
                    "error": "Pillar not found",
                    "message": f"Pillar '{pillar_name}' is not available"
                }
            
            pillar_info = self.available_pillars[pillar_name]
            if pillar_info.get("status") != "available":
                return {
                    "success": False,
                    "error": "Pillar unavailable",
                    "message": f"Pillar '{pillar_name}' is currently unavailable"
                }
            
            # Check user permission to access this pillar
            has_permission = await self._check_pillar_permission(pillar_name, user_context)
            if not has_permission:
                self.logger.warning(
                    f"⚠️ Permission denied: User {user_context.user_id} attempted to access "
                    f"restricted pillar '{pillar_name}'"
                )
                return {
                    "success": False,
                    "error": "Permission denied",
                    "message": f"You do not have permission to access pillar '{pillar_name}'"
                }
            
            # Get routing rules for the pillar
            pillar_routes = self.routing_rules.get(pillar_name, {})
            
            # Determine specific endpoint
            endpoint = request_data.get("endpoint", "")
            method = request_data.get("method", "GET")
            payload = request_data.get("payload", {})
            
            # Find matching route
            matched_route = await self._find_matching_route(pillar_name, endpoint, method)
            
            if not matched_route:
                return {
                    "success": False,
                    "error": "Route not found",
                    "message": f"No route found for {method} {endpoint} in pillar {pillar_name}"
                }
            
            # Call actual pillar orchestrator
            orchestrator_response = await self._call_pillar_orchestrator(pillar_name, matched_route, payload, user_context)
            
            return {
                "success": True,
                "pillar": pillar_name,
                "route": matched_route,
                "response": orchestrator_response,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to route to pillar: {e}")
            return {"success": False, "error": str(e), "message": "Failed to route to pillar"}
    
    async def get_available_pillars(self, user_context: UserContext) -> Dict[str, Any]:
        """
        Get list of available business pillars for the user.
        
        Filters pillars based on user permissions. For MVP, all pillars are accessible.
        
        Args:
            user_context: Context of the user.
            
        Returns:
            A dictionary containing available pillars and their status.
        """
        self.logger.debug(f"Getting available pillars for user: {user_context.user_id}")
        
        try:
            user_pillars = {}
            
            for pillar_name, pillar_info in self.available_pillars.items():
                # Check if user has permission to access this pillar
                has_access = await self._check_pillar_permission(pillar_name, user_context)
                
                if has_access:
                    user_pillars[pillar_name] = {
                        "name": pillar_name,
                        "status": pillar_info.get("status"),
                        "endpoint": pillar_info.get("endpoint"),
                        "available_routes": list(self.routing_rules.get(pillar_name, {}).keys()),
                        "description": self._get_pillar_description(pillar_name),
                        "access_granted": True
                    }
                else:
                    # Log denied access (for future permission enforcement)
                    self.logger.debug(f"User {user_context.user_id} does not have access to pillar: {pillar_name}")
                    # In MVP mode, this shouldn't happen, but we log it for future reference
            
            return {
                "success": True,
                "available_pillars": user_pillars,
                "pillar_count": len(user_pillars),
                "permission_mode": "open" if self.mvp_mode_open_permissions else "restricted",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get available pillars: {e}")
            return {"success": False, "error": str(e), "message": "Failed to get available pillars"}
    
    async def _check_pillar_permission(self, pillar_name: str, user_context: UserContext) -> bool:
        """
        Check if user has permission to access a pillar.
        
        MVP Mode: Returns True for all pillars (open permissions).
        Future: Will check actual user permissions against pillar requirements.
        
        Args:
            pillar_name: Name of the pillar to check.
            user_context: Context of the user.
            
        Returns:
            True if user has access, False otherwise.
        """
        try:
            # MVP Mode: Open permissions for all pillars
            if self.mvp_mode_open_permissions:
                return True
            
            # Get pillar permission configuration
            pillar_config = self.pillar_permissions.get(pillar_name)
            if not pillar_config:
                # Unknown pillar - deny access by default (fail secure)
                self.logger.warning(f"⚠️ Unknown pillar '{pillar_name}' - denying access")
                return False
            
            # If pillar is not restricted, allow access
            if not pillar_config.get("restricted", False):
                return True
            
            # Check required permission
            required_permission = pillar_config.get("required_permission")
            if not required_permission:
                # No specific permission required - allow access
                return True
            
            # Check if user has the required permission
            user_permissions = user_context.permissions or []
            
            # Check for exact match or wildcard permissions
            if required_permission in user_permissions:
                return True
            
            # Check for wildcard permissions (e.g., "pillar:*" or "*")
            if "*" in user_permissions or f"pillar:*" in user_permissions:
                return True
            
            # Check for pillar-specific wildcard (e.g., "pillar:content:*")
            pillar_wildcard = f"pillar:{pillar_name}:*"
            if pillar_wildcard in user_permissions:
                return True
            
            # Permission denied
            self.logger.debug(
                f"Permission denied: User {user_context.user_id} does not have "
                f"'{required_permission}' for pillar '{pillar_name}'. "
                f"User permissions: {user_permissions}"
            )
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error checking pillar permission: {e}")
            # Fail secure: deny access on error
            return False
    
    async def _determine_target_pillar(self, endpoint: str) -> Optional[str]:
        """Determine which pillar an endpoint belongs to."""
        try:
            for pattern, pillar in self.api_patterns.items():
                if re.match(pattern, endpoint):
                    return pillar
            
            # Check routing rules for exact matches
            for pillar, routes in self.routing_rules.items():
                for route_name, route_path in routes.items():
                    if endpoint.startswith(route_path):
                        return pillar
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error determining target pillar: {e}")
            return None
    
    async def _find_matching_route(self, pillar_name: str, endpoint: str, method: str) -> Optional[str]:
        """Find a matching route for the given endpoint and method."""
        try:
            pillar_routes = self.routing_rules.get(pillar_name, {})
            
            # Look for exact matches first
            for route_name, route_path in pillar_routes.items():
                if endpoint == route_path:
                    return route_name
            
            # Look for pattern matches
            for route_name, route_path in pillar_routes.items():
                if endpoint.startswith(route_path):
                    return route_name
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error finding matching route: {e}")
            return None
    
    async def _call_pillar_orchestrator(self, pillar_name: str, route: str, payload: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Call actual pillar orchestrator via Business Orchestrator."""
        try:
            # Get Business Orchestrator if not already cached
            if not self.business_orchestrator:
                if self.parent_service and hasattr(self.parent_service, 'get_business_orchestrator'):
                    self.business_orchestrator = await self.parent_service.get_business_orchestrator()
                elif self.di_container:
                    # Try to get via DI container
                    delivery_manager = self.di_container.service_registry.get("DeliveryManagerService")
                    if delivery_manager and hasattr(delivery_manager, 'get_business_orchestrator'):
                        self.business_orchestrator = await delivery_manager.get_business_orchestrator()
            
            if not self.business_orchestrator:
                self.logger.warning("⚠️ Business Orchestrator not available, cannot route to pillar")
                return {
                    "success": False,
                    "error": "Business Orchestrator not available",
                    "message": "Cannot route to pillar - orchestrator not initialized"
                }
            
            # Map pillar names to orchestrator keys in mvp_orchestrators
            pillar_to_orchestrator = {
                "content": "content_analysis",
                "insights": "insights",
                "operations": "operations",
                "business_outcomes": "business_outcomes"
            }
            
            orchestrator_key = pillar_to_orchestrator.get(pillar_name)
            if not orchestrator_key:
                return {
                    "success": False,
                    "error": f"Unknown pillar: {pillar_name}",
                    "message": f"No orchestrator mapping for pillar: {pillar_name}"
                }
            
            # Get orchestrator from Business Orchestrator's mvp_orchestrators
            if not hasattr(self.business_orchestrator, 'mvp_orchestrators'):
                return {
                    "success": False,
                    "error": "MVP orchestrators not available",
                    "message": "Business Orchestrator does not have mvp_orchestrators"
                }
            
            orchestrator = self.business_orchestrator.mvp_orchestrators.get(orchestrator_key)
            if not orchestrator:
                return {
                    "success": False,
                    "error": f"Orchestrator not found: {orchestrator_key}",
                    "message": f"Orchestrator '{orchestrator_key}' not available in Business Orchestrator"
                }
            
            # Map route names to orchestrator methods
            # Note: These are simplified mappings - actual methods may have different signatures
            route_to_method = {
                "content": {
                    "upload_file": "upload_file",
                    "get_files": "list_files",
                    "parse_file": "parse_file",
                    "get_file_metadata": "get_file_metadata"
                },
                "insights": {
                    "analyze_data": "analyze_content",
                    "get_visualizations": "get_visualizations",
                    "generate_report": "generate_report",
                    "get_insights": "get_insights"
                },
                "operations": {
                    "create_sop": "generate_sop",
                    "create_workflow": "generate_workflow",
                    "convert_sop_to_workflow": "convert_sop_to_workflow",
                    "optimize_process": "optimize_process"
                },
                "business_outcomes": {
                    "create_strategic_plan": "generate_strategic_roadmap",
                    "calculate_roi": "calculate_kpis",
                    "measure_outcomes": "track_outcomes",
                    "get_metrics": "get_pillar_summaries"
                }
            }
            
            method_name = route_to_method.get(pillar_name, {}).get(route)
            if not method_name:
                self.logger.warning(f"⚠️ No method mapping for route '{route}' in pillar '{pillar_name}'")
                return {
                    "success": False,
                    "error": f"Route not mapped: {route}",
                    "message": f"No method mapping for route '{route}' in pillar '{pillar_name}'"
                }
            
            # Check if orchestrator has the method
            if not hasattr(orchestrator, method_name):
                self.logger.warning(f"⚠️ Orchestrator does not have method '{method_name}'")
                return {
                    "success": False,
                    "error": f"Method not found: {method_name}",
                    "message": f"Orchestrator does not have method '{method_name}'"
                }
            
            # Call orchestrator method
            method = getattr(orchestrator, method_name)
            
            # Prepare method arguments based on method signature
            # Most orchestrator methods take context_data and user_id
            if method_name in ["generate_strategic_roadmap", "generate_poc_proposal", "get_pillar_summaries"]:
                # Semantic API methods
                result = await method(
                    context_data=payload,
                    user_id=user_context.user_id
                )
            elif method_name in ["upload_file", "parse_file", "analyze_content"]:
                # File/content methods - pass payload directly
                result = await method(**payload) if isinstance(payload, dict) else await method(payload)
            else:
                # Default: try to call with payload as kwargs
                try:
                    result = await method(**payload) if isinstance(payload, dict) else await method(payload)
                except TypeError:
                    # Fallback: call with payload as single argument
                    result = await method(payload)
            
            # Ensure result has expected structure
            if not isinstance(result, dict):
                result = {"success": True, "data": result, "message": f"{method_name} completed successfully"}
            
            # Add metadata
            result["user_id"] = user_context.user_id
            result["timestamp"] = datetime.utcnow().isoformat()
            result["orchestrator"] = orchestrator_key
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error calling pillar orchestrator: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to call pillar orchestrator: {str(e)}"
            }
    
    def _get_pillar_description(self, pillar_name: str) -> str:
        """Get description for a pillar."""
        descriptions = {
            "content": "Upload, parse, and manage your data files with intelligent preprocessing",
            "insights": "Generate powerful visualizations, business analysis, and AI-driven insights",
            "operations": "Optimize workflows and processes with interactive blueprint design",
            "business_outcomes": "Build strategic plans and measure business outcomes with AI-powered analysis"
        }
        return descriptions.get(pillar_name, "Business pillar for data processing and analysis")
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the Frontend Router Module."""
        return {
            "module_name": "FrontendRouterModule",
            "status": "healthy" if self.is_initialized else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "available_pillars": len(self.available_pillars),
            "routing_rules": {pillar: len(routes) for pillar, routes in self.routing_rules.items()},
            "api_patterns": len(self.api_patterns),
            "message": "Frontend Router Module is operational."
        }
