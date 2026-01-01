#!/usr/bin/env python3
"""
Utilities Module - Post Office Service

Provides utility methods and infrastructure validation.
"""

from typing import Dict, Any
from datetime import datetime


class Utilities:
    """Utilities module for Post Office Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate that proper infrastructure mapping is working correctly."""
        try:
            validation_results = {
                "messaging_redis": False,
                "event_management_redis": False,
                "session_redis": False,
                "overall_status": False
            }
            
            # Test Messaging (Redis)
            try:
                if self.service.messaging_abstraction:
                    test_result = await self.service.messaging_abstraction.health_check()
                    validation_results["messaging_redis"] = True
            except Exception as e:
                if self.service.logger:
                    self.service.logger.warning(f"⚠️ Messaging (Redis) test failed: {str(e)}")
            
            # Test Event Management (Redis)
            try:
                if self.service.event_management_abstraction:
                    test_result = await self.service.event_management_abstraction.health_check()
                    validation_results["event_management_redis"] = True
            except Exception as e:
                if self.service.logger:
                    self.service.logger.warning(f"⚠️ Event Management (Redis) test failed: {str(e)}")
            
            # Test Session (Redis)
            try:
                if self.service.session_abstraction:
                    test_result = await self.service.session_abstraction.health_check()
                    validation_results["session_redis"] = True
            except Exception as e:
                if self.service.logger:
                    self.service.logger.warning(f"⚠️ Session (Redis) test failed: {str(e)}")
            
            # Overall status
            validation_results["overall_status"] = all([
                validation_results["messaging_redis"],
                validation_results["event_management_redis"],
                validation_results["session_redis"]
            ])
            
            if self.service.logger:
                self.service.logger.info("🔍 Proper infrastructure mapping validation completed:")
                self.service.logger.info(f"  - Messaging (Redis): {'✅' if validation_results['messaging_redis'] else '❌'}")
                self.service.logger.info(f"  - Event Management (Redis): {'✅' if validation_results['event_management_redis'] else '❌'}")
                self.service.logger.info(f"  - Session (Redis): {'✅' if validation_results['session_redis'] else '❌'}")
                self.service.logger.info(f"  - Overall Status: {'✅' if validation_results['overall_status'] else '❌'}")
            
            return validation_results
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error validating proper infrastructure mapping: {str(e)}")
            return {
                "messaging_redis": False,
                "event_management_redis": False,
                "session_redis": False,
                "overall_status": False,
                "error": str(e)
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities with proper infrastructure status."""
        try:
            return {
                "service_name": "PostOfficeService",
                "service_type": "strategic_communication_orchestrator",
                "realm": "smart_city",
                "capabilities": [
                    "strategic_communication_orchestration",
                    "cross_pillar_coordination",
                    "realm_orchestration",
                    "event_driven_communication",
                    "message_routing",
                    "agent_registration",
                    "infrastructure_integration"
                ],
                "infrastructure_connections": {
                    "messaging": "Redis",
                    "event_management": "Redis",
                    "session": "Redis"
                },
                "infrastructure_status": {
                    "connected": self.service.is_infrastructure_connected,
                    "messaging_available": self.service.messaging_abstraction is not None,
                    "event_management_available": self.service.event_management_abstraction is not None,
                    "session_available": self.service.session_abstraction is not None
                },
                "infrastructure_correct_from_start": True,
                "soa_apis": self.service.soa_apis,
                "mcp_tools": self.service.mcp_tools,
                "status": "active",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error getting service capabilities: {str(e)}")
            return {
                "service_name": "PostOfficeService",
                "error": str(e),
                "status": "error"
            }

