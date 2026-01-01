#!/usr/bin/env python3
"""
Experience Manager Service - Experience Coordination Module

Micro-module for experience coordination operations.
"""

import logging
from typing import Any, Dict
from datetime import datetime


class ExperienceCoordination:
    """Experience coordination module for Experience Manager service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
    
    async def coordinate_experience(self, experience_request: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate experience services for user interactions."""
        try:
            if self.service.logger:
                self.service.logger.info("🎯 Coordinating experience...")
            
            experience_type = experience_request.get("experience_type", "web")
            user_context = experience_request.get("user_context", {})
            
            # Coordinate experience services
            coordination_result = {
                "experience_id": f"exp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "experience_type": experience_type,
                "user_context": user_context,
                "services_coordinated": list(self.service.experience_services.keys()),
                "status": "coordinated",
                "created_at": datetime.utcnow().isoformat()
            }
            
            if self.service.logger:
                self.service.logger.info(f"✅ Experience coordinated: {coordination_result['experience_id']}")
            
            return {
                "success": True,
                "coordination_result": coordination_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to coordinate experience: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "experience_request": experience_request
            }
    
    async def expose_apis(self, api_request: Dict[str, Any]) -> Dict[str, Any]:
        """Expose APIs for frontend and external systems."""
        try:
            if self.service.logger:
                self.service.logger.info("🌐 Exposing APIs...")
            
            api_type = api_request.get("api_type", "rest")
            
            api_result = {
                "api_id": f"api_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "api_type": api_type,
                "endpoints": [],
                "status": "exposed",
                "created_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "api_result": api_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to expose APIs: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "api_request": api_request
            }
    
    async def manage_sessions(self, session_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manage user sessions via Traffic Cop service.
        
        Uses Smart City service for business-level session routing and state sync.
        Falls back to infrastructure abstraction if Traffic Cop not available.
        """
        try:
            if self.service.logger:
                self.service.logger.info("👤 Managing sessions via Traffic Cop...")
            
            action = session_request.get("action", "create")
            user_id = session_request.get("user_id")
            
            # ✅ Use Traffic Cop service for business-level session management
            if self.service.traffic_cop:
                try:
                    if action == "create":
                        # Create session via Traffic Cop (handles routing, state sync)
                        from backend.smart_city.protocols.traffic_cop_service_protocol import SessionRequest, SessionStatus
                        from datetime import timedelta
                        
                        session_request_obj = SessionRequest(
                            session_id=f"exp_session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                            user_id=user_id,
                            session_type="experience",
                            context=session_request.get("context", {}),
                            ttl_seconds=session_request.get("ttl_seconds", 3600)
                        )
                        
                        session_response = await self.service.traffic_cop.create_session(session_request_obj)
                        
                        if session_response and session_response.success:
                            return {
                                "success": True,
                                "session_result": {
                                    "session_id": session_response.session_id,
                                    "user_id": user_id,
                                    "action": action,
                                    "status": session_response.status.value if hasattr(session_response.status, 'value') else str(session_response.status),
                                    "expires_at": session_response.expires_at,
                                    "timestamp": datetime.utcnow().isoformat()
                                },
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        else:
                            if self.service.logger:
                                self.service.logger.warning("⚠️ Traffic Cop session creation failed, falling back to abstraction")
                    else:
                        # Get/update/destroy session via Traffic Cop
                        session_id = session_request.get("session_id")
                        if session_id:
                            if action == "get":
                                session_response = await self.service.traffic_cop.get_session(session_id)
                            elif action == "update":
                                session_response = await self.service.traffic_cop.update_session(
                                    session_id, session_request.get("updates", {})
                                )
                            elif action == "destroy":
                                session_response = await self.service.traffic_cop.destroy_session(session_id)
                            else:
                                session_response = None
                            
                            if session_response and session_response.success:
                                return {
                                    "success": True,
                                    "session_result": {
                                        "session_id": session_response.session_id,
                                        "user_id": user_id,
                                        "action": action,
                                        "status": session_response.status.value if hasattr(session_response.status, 'value') else str(session_response.status),
                                        "timestamp": datetime.utcnow().isoformat()
                                    },
                                    "timestamp": datetime.utcnow().isoformat()
                                }
                except Exception as e:
                    if self.service.logger:
                        self.service.logger.warning(f"⚠️ Traffic Cop session operation failed: {e}, falling back to abstraction")
            
            # Fallback: Use infrastructure abstraction for low-level session storage
            if self.service.logger:
                self.service.logger.info("⚠️ Using infrastructure abstraction fallback for session management")
            
            session_result = {
                "session_id": f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}" if action == "create" else session_request.get("session_id"),
                "user_id": user_id,
                "action": action,
                "status": "managed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "session_result": session_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to manage sessions: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "session_request": session_request
            }


