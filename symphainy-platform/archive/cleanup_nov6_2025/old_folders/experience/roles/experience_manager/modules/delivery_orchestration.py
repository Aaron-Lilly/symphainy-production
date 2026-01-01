#!/usr/bin/env python3
"""
Experience Manager Service - Delivery Orchestration Module

Micro-module for orchestrating Delivery Manager (top-down flow: Experience → Delivery).
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime


class DeliveryOrchestration:
    """Delivery orchestration module for Experience Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def orchestrate_delivery(self, delivery_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate delivery by calling Delivery Manager.
        
        This implements the top-down flow: Experience Manager → Delivery Manager
        """
        try:
            if self.service.logger:
                self.service.logger.info("🎯 Orchestrating delivery via Delivery Manager...")
            
            # Get Delivery Manager from DI Container
            delivery_manager = self.service.di_container.get_foundation_service("DeliveryManagerService")
            
            if not delivery_manager:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Delivery Manager not available - may need to be initialized first")
                return {
                    "success": False,
                    "error": "Delivery Manager not available",
                    "message": "Delivery Manager must be initialized before orchestration",
                    "delivery_context": delivery_context
                }
            
            # Call Delivery Manager's orchestrate_business_enablement method
            if hasattr(delivery_manager, "orchestrate_business_enablement"):
                delivery_result = await delivery_manager.orchestrate_business_enablement(delivery_context)
                
                if self.service.logger:
                    self.service.logger.info(f"✅ Delivery orchestrated successfully: {delivery_result.get('success', False)}")
                
                return {
                    "success": True,
                    "delivery_orchestrated": True,
                    "delivery_result": delivery_result,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Delivery Manager does not have orchestrate_business_enablement method")
                return {
                    "success": False,
                    "error": "Delivery Manager orchestrate_business_enablement method not available",
                    "delivery_context": delivery_context
                }
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to orchestrate delivery: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "delivery_context": delivery_context,
                "timestamp": datetime.utcnow().isoformat()
            }






