#!/usr/bin/env python3
"""
Orchestration Module - Traffic Cop Service

Handles orchestration of Traffic Cop operations.
"""

from typing import Dict, Any
from backend.smart_city.protocols.traffic_cop_service_protocol import (
    APIGatewayRequest, SessionRequest, StateSyncRequest
)


class Orchestration:
    """Orchestration module for Traffic Cop Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def orchestrate_api_gateway(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate API Gateway operations."""
        try:
            operation = request.get("operation")
            
            api_routing = self.service.get_module("api_routing")
            
            if operation == "route_request":
                api_request = APIGatewayRequest(**request.get("api_request", {}))
                response = await api_routing.route_api_request(api_request)
                return {
                    "success": response.success,
                    "status_code": response.status_code,
                    "body": response.body,
                    "error": response.error
                }
            elif operation == "get_routes":
                routes = await api_routing.get_api_routes()
                return {
                    "success": True,
                    "routes": routes
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
        except Exception as e:
            self.service._log("error", f"Failed to orchestrate API Gateway: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def orchestrate_session_management(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate session management operations."""
        try:
            operation = request.get("operation")
            
            session_management = self.service.get_module("session_management")
            
            if operation == "create_session":
                session_request = SessionRequest(**request.get("session_request", {}))
                response = await session_management.create_session(session_request)
                return {
                    "success": response.success,
                    "session_id": response.session_id,
                    "status": response.status.value,
                    "error": response.error
                }
            elif operation == "get_session":
                session_id = request.get("session_id")
                response = await session_management.get_session(session_id)
                return {
                    "success": response.success,
                    "session_id": response.session_id,
                    "status": response.status.value,
                    "error": response.error
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
        except Exception as e:
            self.service._log("error", f"Failed to orchestrate session management: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def orchestrate_state_synchronization(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate state synchronization operations."""
        try:
            operation = request.get("operation")
            
            state_sync = self.service.get_module("state_sync")
            
            if operation == "sync_state":
                sync_request = StateSyncRequest(**request.get("sync_request", {}))
                response = await state_sync.sync_state(sync_request)
                return {
                    "success": response.success,
                    "key": response.key,
                    "sync_status": response.sync_status.value,
                    "sync_id": response.sync_id,
                    "error": response.error
                }
            elif operation == "get_sync_status":
                sync_id = request.get("sync_id")
                response = await state_sync.get_state_sync_status(sync_id)
                return {
                    "success": response.success,
                    "sync_status": response.sync_status.value,
                    "error": response.error
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown operation: {operation}"
                }
            
        except Exception as e:
            self.service._log("error", f"Failed to orchestrate state synchronization: {e}")
            return {
                "success": False,
                "error": str(e)
            }







