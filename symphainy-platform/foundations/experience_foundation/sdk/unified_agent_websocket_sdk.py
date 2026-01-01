#!/usr/bin/env python3
"""
Unified Agent WebSocket SDK - Experience Foundation

Provides unified websocket endpoint for all agents (Guide + Liaison).
Single connection per user, routes messages to appropriate agent.

WHAT (Experience SDK): I provide unified agent websocket for user-facing communication
HOW (SDK Implementation): I compose Experience WebSocketSDK + Agentic Foundation for routing
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class UnifiedAgentWebSocketSDK:
    """
    Unified Agent WebSocket SDK - Experience Foundation
    
    Provides unified websocket endpoint for all agents (Guide + Liaison).
    Single connection per user, routes messages to appropriate agent.
    
    Architecture:
    - Uses Experience Foundation WebSocketSDK for connection management
    - Uses Agentic Foundation for agent discovery/routing
    - Routes messages based on agent_type and pillar
    - Manages conversation context per agent
    """
    
    def __init__(self, experience_foundation: Any):
        """
        Initialize Unified Agent WebSocket SDK.
        
        Args:
            experience_foundation: Experience Foundation Service instance
        """
        self.experience_foundation = experience_foundation
        self.di_container = experience_foundation.di_container if hasattr(experience_foundation, 'di_container') else None
        self.platform_orchestrator = None  # Will be set during initialization
        self.logger = logging.getLogger("UnifiedAgentWebSocketSDK")
        
        # SDK dependencies
        self.websocket_sdk = None  # Experience Foundation WebSocketSDK
        self.agentic_foundation = None  # For agent discovery/routing
        
        # Connection tracking
        self.active_connections: Dict[str, Dict[str, Any]] = {}  # connection_id -> connection_data
        self.conversation_contexts: Dict[str, Dict[str, Any]] = {}  # conversation_id -> context
        
        self.is_initialized = False
        self.logger.info("🏗️ Unified Agent WebSocket SDK initialized")
    
    async def initialize(self):
        """Initialize Unified Agent WebSocket SDK."""
        self.logger.info("🚀 Initializing Unified Agent WebSocket SDK...")
        
        try:
            # Get Experience Foundation WebSocketSDK
            if hasattr(self.experience_foundation, 'get_websocket_sdk'):
                self.websocket_sdk = await self.experience_foundation.get_websocket_sdk()
                if self.websocket_sdk:
                    if not self.websocket_sdk.is_initialized:
                        await self.websocket_sdk.initialize()
                    self.logger.info("✅ WebSocket SDK obtained")
                else:
                    self.logger.warning("⚠️ WebSocket SDK not available")
            else:
                self.logger.warning("⚠️ Experience Foundation does not expose WebSocket SDK")
            
            # Get Agentic Foundation for agent routing
            if self.di_container:
                try:
                    self.agentic_foundation = self.di_container.get_foundation_service("AgenticFoundationService")
                    if self.agentic_foundation:
                        self.logger.info("✅ Agentic Foundation obtained")
                    else:
                        self.logger.warning("⚠️ Agentic Foundation not available in DI Container")
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to get Agentic Foundation: {e}")
            else:
                self.logger.warning("⚠️ DI Container not available")
            
            self.is_initialized = True
            self.logger.info("✅ Unified Agent WebSocket SDK initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Unified Agent WebSocket SDK: {e}")
            raise
    
    async def handle_agent_message(
        self,
        websocket: Any,
        message: Dict[str, Any],
        session_token: str,
        connection_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle agent message with routing.
        
        Routes to appropriate agent based on message.agent_type and message.pillar.
        
        Args:
            websocket: WebSocket connection
            message: Message from client
                {
                    "agent_type": "guide" | "liaison",
                    "pillar": "content" | "insights" | "operations" | "business_outcomes" (required if liaison),
                    "message": "user message",
                    "conversation_id": "optional conversation ID"
                }
            session_token: Session token for user
            connection_id: Optional connection ID
        
        Returns:
            Response dictionary with agent response
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Extract routing information
            agent_type = message.get("agent_type", "guide")
            pillar = message.get("pillar")
            user_message = message.get("message", "")
            conversation_id = message.get("conversation_id")
            
            if not user_message:
                return {
                    "type": "error",
                    "message": "Message is required",
                    "agent_type": agent_type,
                    "pillar": pillar
                }
            
            # Generate conversation_id if not provided
            if not conversation_id:
                conversation_id = f"{agent_type}_{pillar or 'guide'}_{uuid.uuid4().hex[:8]}"
            
            # Get or create conversation context
            context_key = f"{session_token}_{conversation_id}"
            if context_key not in self.conversation_contexts:
                self.conversation_contexts[context_key] = {
                    "conversation_id": conversation_id,
                    "agent_type": agent_type,
                    "pillar": pillar,
                    "session_token": session_token,
                    "messages": [],
                    "created_at": datetime.utcnow().isoformat()
                }
            
            conversation_context = self.conversation_contexts[context_key]
            
            # Route to appropriate agent
            if agent_type == "guide":
                agent = await self._get_guide_agent()
                if not agent:
                    return {
                        "type": "error",
                        "message": "Guide Agent not available",
                        "agent_type": agent_type
                    }
                
                # Process with Guide Agent
                response = await agent.handle_user_message(
                    user_message=user_message,
                    session_token=session_token or "anonymous",
                    conversation_id=conversation_id
                )
                
            elif agent_type == "liaison":
                if not pillar:
                    return {
                        "type": "error",
                        "message": "Pillar is required for liaison agent",
                        "agent_type": agent_type
                    }
                
                agent = await self._get_liaison_agent(pillar)
                if not agent:
                    return {
                        "type": "error",
                        "message": f"Liaison Agent for pillar '{pillar}' not available",
                        "agent_type": agent_type,
                        "pillar": pillar
                    }
                
                # Process with Liaison Agent
                from utilities.security_authorization.security_authorization_utility import UserContext
                user_context = UserContext(
                    user_id=session_token or "anonymous",
                    email=f"{session_token or 'anonymous'}@websocket.local",
                    full_name=session_token or "Anonymous User",
                    session_id=session_token or "anonymous",
                    permissions=["write", "execute"],  # Grant permissions for websocket connections (testing/MVP)
                    tenant_id=conversation_context.get("tenant_id")
                )
                
                response = await agent.process_user_query(
                    query=user_message,
                    conversation_id=conversation_id,
                    user_context=user_context
                )
                
            else:
                return {
                    "type": "error",
                    "message": f"Unknown agent_type: {agent_type}",
                    "agent_type": agent_type
                }
            
            # Update conversation context
            conversation_context["messages"].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            conversation_context["messages"].append({
                "role": "assistant",
                "content": response.get("response", response.get("message", "")),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Add routing metadata to response
            response["agent_type"] = agent_type
            if pillar:
                response["pillar"] = pillar
            response["conversation_id"] = conversation_id
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle agent message: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "type": "error",
                "message": f"Internal error: {str(e)}",
                "agent_type": message.get("agent_type", "unknown"),
                "pillar": message.get("pillar")
            }
    
    async def _get_guide_agent(self) -> Optional[Any]:
        """
        Get Guide Agent via Journey Manager, Delivery Manager, or Curator.
        
        Follows the same pattern as websocket_router.py get_guide_agent().
        
        Returns:
            Guide Agent instance or None
        """
        try:
            if not self.di_container:
                self.logger.warning("⚠️ DI Container not available")
                return None
            
            # Try Journey Manager first (via Platform Orchestrator)
            try:
                if self.platform_orchestrator:
                    journey_manager = await self.platform_orchestrator.get_manager("journey_manager")
                    if journey_manager and hasattr(journey_manager, 'guide_agent'):
                        self.logger.info("✅ Found Guide Agent via Journey Manager")
                        return journey_manager.guide_agent
            except Exception as e:
                self.logger.debug(f"Could not get Guide Agent via Journey Manager: {e}")
            
            # Try Delivery Manager (via Platform Orchestrator)
            try:
                if self.platform_orchestrator:
                    delivery_manager = await self.platform_orchestrator.get_manager("delivery_manager")
                    if delivery_manager and hasattr(delivery_manager, 'guide_agent'):
                        self.logger.info("✅ Found Guide Agent via Delivery Manager")
                        return delivery_manager.guide_agent
            except Exception as e:
                self.logger.debug(f"Could not get Guide Agent via Delivery Manager: {e}")
            
            # Try Curator's agent registry (via Platform Orchestrator or DI Container)
            try:
                curator = None
                if self.platform_orchestrator and hasattr(self.platform_orchestrator, 'di_container'):
                    curator = self.platform_orchestrator.di_container.get_curator_foundation() if hasattr(self.platform_orchestrator.di_container, 'get_curator_foundation') else None
                elif self.di_container:
                    curator = self.di_container.get_curator_foundation() if hasattr(self.di_container, 'get_curator_foundation') else None
                
                if curator and hasattr(curator, 'agent_capability_registry'):
                    guide_agent = await curator.agent_capability_registry.get_agent("GuideCrossDomainAgent")
                    if guide_agent:
                        self.logger.info("✅ Found Guide Agent via Curator agent registry")
                        return guide_agent
            except Exception as e:
                self.logger.debug(f"Could not get Guide Agent via Curator agent registry: {e}")
            
            self.logger.warning("⚠️ Guide Agent not found via any method")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get Guide Agent: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def _get_liaison_agent(self, pillar: str) -> Optional[Any]:
        """
        Get Liaison Agent for pillar via orchestrator discovery.
        
        Args:
            pillar: Pillar name (content, insights, operations, business_outcomes)
        
        Returns:
            Liaison Agent instance or None
        """
        try:
            # Try to get Delivery Manager via Platform Orchestrator
            delivery_manager = None
            
            if self.platform_orchestrator and hasattr(self.platform_orchestrator, 'get_manager'):
                try:
                    delivery_manager = await self.platform_orchestrator.get_manager("delivery_manager")
                except Exception as e:
                    self.logger.debug(f"Could not get Delivery Manager via Platform Orchestrator: {e}")
            
            # Fallback: Try to get via Curator's service registry
            if not delivery_manager and self.di_container:
                try:
                    curator = None
                    if hasattr(self.di_container, 'get_curator_foundation'):
                        curator = self.di_container.get_curator_foundation()
                    
                    if curator and hasattr(curator, 'registered_services'):
                        # Check for DeliveryManagerService in registered services
                        service_variants = ["DeliveryManagerService", "DeliveryManager", "delivery_manager"]
                        for variant in service_variants:
                            service_registration = curator.registered_services.get(variant)
                            if service_registration:
                                delivery_manager = service_registration.get("service_instance")
                                if delivery_manager:
                                    self.logger.debug(f"✅ Found Delivery Manager via Curator: {variant}")
                                    break
                except Exception as e:
                    self.logger.debug(f"Could not get Delivery Manager via Curator: {e}")
            
            if not delivery_manager:
                self.logger.warning("⚠️ Delivery Manager not available")
                return None
            
            # Pillar-to-Orchestrator Mapping (from websocket_router.py)
            pillar_map = {
                "content": {
                    "orchestrator_key": "content_analysis",
                    "liaison_agent_name": "ContentLiaisonAgent"
                },
                "insights": {
                    "orchestrator_key": "insights",
                    "liaison_agent_name": "InsightsLiaisonAgent"
                },
                "operations": {
                    "orchestrator_key": "operations",
                    "liaison_agent_name": "OperationsLiaisonAgent"
                },
                "business_outcomes": {
                    "orchestrator_key": "business_outcomes",
                    "liaison_agent_name": "BusinessOutcomesLiaisonAgent"
                }
            }
            
            pillar_config = pillar_map.get(pillar)
            if not pillar_config:
                self.logger.warning(f"⚠️ Unknown pillar: {pillar}")
                return None
            
            # Get orchestrator
            orchestrator = delivery_manager.mvp_pillar_orchestrators.get(pillar_config["orchestrator_key"])
            if not orchestrator:
                self.logger.warning(f"⚠️ Orchestrator not found for pillar: {pillar}")
                return None
            
            # Ensure orchestrator is initialized (agents are created during initialization)
            if hasattr(orchestrator, 'is_initialized') and not orchestrator.is_initialized:
                self.logger.debug(f"🔧 Orchestrator not initialized, initializing now...")
                try:
                    await orchestrator.initialize()
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to initialize orchestrator: {e}")
            
            # Get liaison agent from orchestrator
            # Try direct attribute first (most reliable), then get_agent method
            liaison_agent = None
            if hasattr(orchestrator, 'liaison_agent'):
                liaison_agent = orchestrator.liaison_agent
                if liaison_agent:
                    self.logger.debug(f"✅ Found liaison agent via direct attribute")
            elif hasattr(orchestrator, 'get_agent'):
                # get_agent is async, await it
                try:
                    liaison_agent = await orchestrator.get_agent(pillar_config["liaison_agent_name"])
                    if liaison_agent:
                        self.logger.debug(f"✅ Found liaison agent via get_agent method")
                except Exception as e:
                    self.logger.debug(f"Could not get agent via get_agent method: {e}")
            
            if not liaison_agent:
                self.logger.warning(f"⚠️ Liaison Agent not found: {pillar_config['liaison_agent_name']}")
                return None
            
            return liaison_agent
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get Liaison Agent for pillar '{pillar}': {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None
    
    async def get_conversation_context(self, session_token: str, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation context.
        
        Args:
            session_token: Session token
            conversation_id: Conversation ID
        
        Returns:
            Conversation context or None
        """
        context_key = f"{session_token}_{conversation_id}"
        return self.conversation_contexts.get(context_key)
    
    async def close_connection(self, connection_id: str):
        """
        Close connection and clean up.
        
        Args:
            connection_id: Connection ID
        """
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            self.logger.info(f"🔌 Connection closed: {connection_id}")

