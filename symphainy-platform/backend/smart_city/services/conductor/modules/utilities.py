#!/usr/bin/env python3
"""
Utilities Module - Conductor Service

Provides utility methods and service capabilities.
"""

from typing import Dict, Any
from datetime import datetime


class Utilities:
    """Utilities module for Conductor Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get Conductor service capabilities with proper infrastructure status."""
        try:
            return {
                "service_name": "ConductorService",
                "service_type": "workflow_orchestrator",
                "realm": "smart_city",
                "capabilities": [
                    "workflow_orchestration",
                    "task_management",
                    "orchestration_patterns",
                    "graph_dsl_execution",
                    "distributed_task_execution",
                    "infrastructure_integration"
                ],
                "infrastructure_connections": {
                    "task_management": "Celery",
                    "workflow_orchestration": "Redis Graph"
                },
                "infrastructure_status": {
                    "connected": self.service.is_infrastructure_connected,
                    "task_management_available": self.service.task_management_abstraction is not None,
                    "workflow_orchestration_available": self.service.workflow_orchestration_abstraction is not None
                },
                "infrastructure_correct_from_start": True,
                "soa_apis": self.service.soa_apis,
                "mcp_tools": self.service.mcp_tools,
                "status": "active",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.service._log("error", f"❌ Error getting service capabilities: {str(e)}")
            return {
                "service_name": "ConductorService",
                "error": str(e),
                "status": "error"
            }







