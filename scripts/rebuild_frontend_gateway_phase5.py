#!/usr/bin/env python3
"""
Phase 5: Rebuild FrontendGatewayService with New Routing Only

Extracts essential parts and rebuilds the file without old hardcoded routing.
"""

import re
import sys

def extract_section(content, start_pattern, end_pattern):
    """Extract section between patterns."""
    start_idx = content.find(start_pattern)
    if start_idx == -1:
        return None, None
    end_idx = content.find(end_pattern, start_idx)
    if end_idx == -1:
        return content[start_idx:], start_idx
    return content[start_idx:end_idx + len(end_pattern)], start_idx

def extract_handler_methods(content):
    """Extract all handler methods."""
    handlers = []
    # Pattern to match async def handle_* methods
    pattern = r'(    async def handle_\w+\([^)]*\)[^:]*:.*?(?=\n    (?:async )?def |\Z))'
    matches = re.finditer(pattern, content, re.DOTALL)
    for match in matches:
        handlers.append(match.group(1))
    return handlers

def rebuild_file():
    """Rebuild frontend_gateway_service.py with new routing only."""
    
    input_file = "/home/founders/demoversion/symphainy_source/symphainy-platform/foundations/experience_foundation/services/frontend_gateway_service/frontend_gateway_service.py"
    output_file = "/home/founders/demoversion/symphainy_source/symphainy-platform/foundations/experience_foundation/services/frontend_gateway_service/frontend_gateway_service_new.py"
    
    with open(input_file, 'r') as f:
        content = f.read()
    
    # Extract header (up to class definition)
    header_end = content.find("class FrontendGatewayService")
    header = content[:header_end]
    
    # Extract __init__ method
    init_start = content.find("    def __init__")
    init_end = content.find("\n    async def _ensure_city_manager_available", init_start)
    if init_end == -1:
        init_end = content.find("\n    async def initialize", init_start)
    init_method = content[init_start:init_end]
    
    # Extract initialize method
    init_method_start = content.find("    async def initialize(self) -> bool:")
    init_method_end = content.find("\n    async def _discover_orchestrators", init_method_start)
    if init_method_end == -1:
        init_method_end = content.find("\n    async def _register_routes_with_curator", init_method_start)
    initialize_method = content[init_method_start:init_method_end]
    
    # Extract helper methods (before route_frontend_request)
    helper_methods = []
    helper_patterns = [
        ("_ensure_city_manager_available", "_discover_orchestrators"),
        ("_discover_orchestrators", "_register_routes_with_curator"),
        ("_register_routes_with_curator", "_discover_routes_from_curator"),
        ("_discover_routes_from_curator", "_route_via_discovery"),
        ("_route_via_discovery", "route_frontend_request"),
    ]
    
    for start_pattern, end_pattern in helper_patterns:
        start_idx = content.find(f"    async def {start_pattern}")
        if start_idx != -1:
            end_idx = content.find(f"    async def {end_pattern}", start_idx + 1)
            if end_idx == -1:
                end_idx = content.find(f"    def {end_pattern}", start_idx + 1)
            if end_idx != -1:
                helper_methods.append(content[start_idx:end_idx])
    
    # Extract route_frontend_request - simplified version
    route_start = content.find("    async def route_frontend_request(")
    # Find the end - it's before the first handler method
    route_end = content.find("    async def handle_", route_start)
    if route_end == -1:
        route_end = content.find("    async def transform_for_frontend", route_start)
    
    # Extract all handler methods
    handler_start = content.find("    async def handle_")
    handler_section = content[handler_start:]
    
    # Extract transform_for_frontend
    transform_start = content.find("    async def transform_for_frontend")
    transform_end = content.find("\n    async def health_check", transform_start)
    if transform_end == -1:
        transform_end = content.find("\n    # ========================================================================", transform_start)
    transform_method = content[transform_start:transform_end]
    
    # Extract health_check and get_service_capabilities
    health_start = content.find("    async def health_check")
    health_end = content.find("\n    async def get_routing_metrics", health_start)
    health_methods = content[health_start:health_end]
    
    # Extract routing metrics methods
    metrics_start = content.find("    async def get_routing_metrics")
    metrics_end = len(content)
    metrics_methods = content[metrics_start:metrics_end]
    
    # Build new file
    new_content = header
    
    # Add class definition
    new_content += """class FrontendGatewayService(RealmServiceBase):
    \"\"\"
    REST API Gateway Service (via Experience Foundation SDK)
    
    Routes REST API requests to Business Enablement orchestrators.
    This is the REST API experience implementation - any client can consume these APIs.
    
    symphainy-frontend is one client consuming these REST APIs (MVP implementation).
    Other clients (mobile, CLI, API clients) can consume the same REST APIs.
    
    WHAT: Routes REST API requests to Business Enablement orchestrators
    HOW: Uses route discovery from Curator via APIRoutingUtility (Phase 5: New Routing Only)
    
    Composes:
    - ContentAnalysisOrchestrator → /api/v1/content-pillar/*
    - InsightsOrchestrator → /api/v1/insights-pillar/*
    - OperationsOrchestrator → /api/v1/operations-pillar/*
    - BusinessOutcomesOrchestrator → /api/v1/business-outcomes-pillar/*
    \"\"\"
    
"""
    
    # Add __init__
    new_content += init_method + "\n"
    
    # Add helper methods
    for method in helper_methods:
        new_content += method + "\n"
    
    # Add simplified route_frontend_request
    new_content += """    async def route_frontend_request(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        \"\"\"
        Universal request router - routes requests using discovered routes (Phase 5: New Routing Only).
        
        All routing is now handled via route discovery from Curator and APIRoutingUtility.
        The old hardcoded routing logic has been removed.
        
        Args:
            request: Frontend request data
                - endpoint: "/api/{pillar}/{path}" 
                - method: "GET" | "POST" | "PUT" | "DELETE"
                - params: Request parameters/body
                - headers: Optional headers
                - query_params: Optional query parameters
                - user_id: Optional user identifier
        
        Returns:
            Frontend-ready response
        \"\"\"
        try:
            # Start telemetry tracking
            endpoint = request.get("endpoint", "")
            method = request.get("method", "POST")
            await self.log_operation_with_telemetry("route_frontend_request_start", success=True, metadata={"endpoint": endpoint, "method": method})
            
            # Route via discovery (new routing only - Phase 5)
            start_time = datetime.utcnow()
            result = await self._route_via_discovery(request)
            elapsed_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Track metrics for routing
            if self.routing_monitoring_enabled:
                self.routing_metrics["new_routing"]["requests"] += 1
                self.routing_metrics["new_routing"]["total_time_ms"] += elapsed_ms
                if result.get("success") is not False and result.get("error") != "Route not found":
                    self.routing_metrics["new_routing"]["successes"] += 1
                else:
                    self.routing_metrics["new_routing"]["errors"] += 1
                # Update average
                if self.routing_metrics["new_routing"]["requests"] > 0:
                    self.routing_metrics["new_routing"]["avg_time_ms"] = (
                        self.routing_metrics["new_routing"]["total_time_ms"] / 
                        self.routing_metrics["new_routing"]["requests"]
                    )
                self.logger.debug(f"✅ Routing: {endpoint} ({elapsed_ms:.2f}ms)")
            
            # Transform for frontend
            if result:
                frontend_response = await self.transform_for_frontend(result)
                
                # Log request via Librarian
                try:
                    await self.store_document(
                        document_data={
                            "request": request,
                            "response": frontend_response,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        metadata={
                            "type": "api_request_log",
                            "endpoint": endpoint,
                            "method": method
                        }
                    )
                except Exception as log_error:
                    self.logger.warning(f"⚠️  Failed to log request: {log_error}")
                
                # Record health metric
                await self.record_health_metric("route_frontend_request_success", 1.0, {"endpoint": endpoint})
                
                # End telemetry tracking
                await self.log_operation_with_telemetry("route_frontend_request_complete", success=True)
                
                return frontend_response
            
            # No result - return error
            await self.record_health_metric("route_frontend_request_no_handler", 1.0, {"endpoint": endpoint})
            await self.log_operation_with_telemetry("route_frontend_request_complete", success=False)
            
            return {
                "success": False,
                "error": "Route Not Found",
                "message": f"No route found for: {endpoint}"
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "route_frontend_request")
            self.logger.error(f"❌ Route frontend request failed: {e}")
            await self.log_operation_with_telemetry("route_frontend_request_complete", success=False)
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": "Internal Server Error",
                "message": str(e)
            }
    
"""
    
    # Add all handler methods
    new_content += handler_section
    
    # Add transform_for_frontend
    new_content += transform_method + "\n"
    
    # Add health methods
    new_content += health_methods + "\n"
    
    # Add metrics methods
    new_content += metrics_methods
    
    # Write new file
    with open(output_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Rebuilt file: {output_file}")
    print(f"   Original: {len(content)} lines")
    print(f"   New: {len(new_content)} lines")
    print(f"   Reduction: {len(content) - len(new_content)} lines ({((len(content) - len(new_content)) / len(content) * 100):.1f}%)")

if __name__ == "__main__":
    rebuild_file()











