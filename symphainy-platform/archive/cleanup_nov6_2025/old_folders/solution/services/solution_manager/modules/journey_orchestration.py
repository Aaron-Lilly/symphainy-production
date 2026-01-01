#!/usr/bin/env python3
"""
Solution Manager Service - Journey Orchestration Module

Micro-module for orchestrating Journey Manager (top-down flow: Solution → Journey).
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime


class JourneyOrchestration:
    """Journey orchestration module for Solution Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def orchestrate_journey(self, journey_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate journey by calling Journey Manager.
        
        This implements the top-down flow: Solution Manager → Journey Manager
        """
        try:
            if self.service.logger:
                self.service.logger.info("🎯 Orchestrating journey via Journey Manager...")
            
            # Get Journey Manager from DI Container
            journey_manager = self.service.di_container.get_foundation_service("JourneyManagerService")
            
            if not journey_manager:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Journey Manager not available - may need to be initialized first")
                return {
                    "success": False,
                    "error": "Journey Manager not available",
                    "message": "Journey Manager must be initialized before orchestration",
                    "journey_context": journey_context
                }
            
            # Call Journey Manager's design_journey method
            if hasattr(journey_manager, "design_journey"):
                journey_result = await journey_manager.design_journey(journey_context)
                
                if self.service.logger:
                    self.service.logger.info(f"✅ Journey orchestrated successfully: {journey_result.get('success', False)}")
                
                return {
                    "success": True,
                    "journey_orchestrated": True,
                    "journey_result": journey_result,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Journey Manager does not have design_journey method")
                return {
                    "success": False,
                    "error": "Journey Manager design_journey method not available",
                    "journey_context": journey_context
                }
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to orchestrate journey: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "journey_context": journey_context,
                "timestamp": datetime.utcnow().isoformat()
            }






