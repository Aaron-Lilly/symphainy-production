#!/usr/bin/env python3
"""
Journey Manager Service - Experience Orchestration Module

Micro-module for orchestrating Experience Manager (top-down flow: Journey → Experience).
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime


class ExperienceOrchestration:
    """Experience orchestration module for Journey Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def orchestrate_experience(self, experience_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate experience by calling Experience Manager.
        
        This implements the top-down flow: Journey Manager → Experience Manager
        """
        try:
            if self.service.logger:
                self.service.logger.info("🎯 Orchestrating experience via Experience Manager...")
            
            # Get Experience Manager from DI Container
            experience_manager = self.service.di_container.get_foundation_service("ExperienceManagerService")
            
            if not experience_manager:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Experience Manager not available - may need to be initialized first")
                return {
                    "success": False,
                    "error": "Experience Manager not available",
                    "message": "Experience Manager must be initialized before orchestration",
                    "experience_context": experience_context
                }
            
            # Call Experience Manager's coordinate_experience method
            if hasattr(experience_manager, "coordinate_experience"):
                experience_result = await experience_manager.coordinate_experience(experience_context)
                
                if self.service.logger:
                    self.service.logger.info(f"✅ Experience orchestrated successfully: {experience_result.get('success', False)}")
                
                return {
                    "success": True,
                    "experience_orchestrated": True,
                    "experience_result": experience_result,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Experience Manager does not have coordinate_experience method")
                return {
                    "success": False,
                    "error": "Experience Manager coordinate_experience method not available",
                    "experience_context": experience_context
                }
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to orchestrate experience: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "experience_context": experience_context,
                "timestamp": datetime.utcnow().isoformat()
            }






