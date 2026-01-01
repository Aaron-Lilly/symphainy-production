#!/usr/bin/env python3
"""
Chat Service for Experience Realm

WHAT: Provides chat interface for Guide Agent and Liaison Agents
HOW: Routes chat messages to appropriate agents, maintains conversation state

This service connects the frontend chat panel to the backend agents,
enabling the conversational MVP experience per MVP_Description_For_Business_and_Technical_Readiness.md
"""

import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

sys.path.insert(0, os.path.abspath('../../../../../'))

from bases.realm_service_base import RealmServiceBase


class ChatService(RealmServiceBase):
    """
    Chat Service for Experience realm.
    
    Provides persistent chat panel functionality for Guide Agent
    and pillar-specific liaison agents.
    
    Implements MVP requirement: "Persistent UI elements include a navbar 
    across the top for each of the four pillars and a chat panel along 
    the right hand side where the GuideAgent and pillar specific liaison agents live."
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Chat Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Will be discovered via Curator
        self.guide_agent = None
        
        # Liaison agents (accessed via orchestrators)
        self.content_liaison = None
        self.insights_liaison = None
        self.operations_liaison = None
        self.business_outcomes_liaison = None
        
        # Session Manager (for conversation persistence)
        self.session_manager = None
    
    async def initialize(self) -> bool:
        """Initialize Chat Service."""
        await super().initialize()
        
        try:
            # 1. Get Session Manager (for conversation persistence)
            self.session_manager = await self.get_session_manager_api()
            
            # 2. Discover Guide Agent
            await self._discover_guide_agent()
            
            # 3. Discover Liaison Agents via orchestrators
            await self._discover_liaison_agents()
            
            # 4. Register with Curator
            await self.register_with_curator(
                capabilities=["chat", "agent_routing", "conversation_management"],
                soa_apis=[
                    "send_message_to_guide", "send_message_to_liaison",
                    "get_conversation_history", "create_conversation",
                    "get_active_agent", "switch_agent"
                ],
                mcp_tools=[],
                additional_metadata={
                    "layer": "experience",
                    "provides": "chat_interface"
                }
            )
            
            self.logger.info("✅ Chat Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Chat Service initialization failed: {e}")
            return False
    
    async def _discover_guide_agent(self):
        """Discover Guide Agent."""
        try:
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            if curator:
                try:
                    self.guide_agent = await curator.get_service("GuideAgent")
                    self.logger.info("✅ Discovered GuideAgent")
                except Exception as e:
                    self.logger.warning(f"⚠️ GuideAgent not available: {e}")
            else:
                self.logger.warning("⚠️ Curator not available")
        except Exception as e:
            self.logger.error(f"❌ Guide Agent discovery failed: {e}")
    
    async def _discover_liaison_agents(self):
        """Discover liaison agents via orchestrators."""
        try:
            curator = self.di_container.curator if hasattr(self.di_container, 'curator') else None
            if curator:
                # Get orchestrators and access their liaison agents
                try:
                    content_orch = await curator.get_service("ContentAnalysisOrchestrator")
                    self.content_liaison = getattr(content_orch, 'liaison_agent', None)
                    if self.content_liaison:
                        self.logger.info("✅ Discovered Content Liaison Agent")
                except Exception as e:
                    self.logger.warning(f"⚠️ Content Liaison not available: {e}")
                
                try:
                    insights_orch = await curator.get_service("InsightsOrchestrator")
                    self.insights_liaison = getattr(insights_orch, 'liaison_agent', None)
                    if self.insights_liaison:
                        self.logger.info("✅ Discovered Insights Liaison Agent")
                except Exception as e:
                    self.logger.warning(f"⚠️ Insights Liaison not available: {e}")
                
                try:
                    operations_orch = await curator.get_service("OperationsOrchestrator")
                    self.operations_liaison = getattr(operations_orch, 'liaison_agent', None)
                    if self.operations_liaison:
                        self.logger.info("✅ Discovered Operations Liaison Agent")
                except Exception as e:
                    self.logger.warning(f"⚠️ Operations Liaison not available: {e}")
                
                try:
                    business_orch = await curator.get_service("BusinessOutcomesOrchestrator")
                    self.business_outcomes_liaison = getattr(business_orch, 'liaison_agent', None)
                    if self.business_outcomes_liaison:
                        self.logger.info("✅ Discovered Business Outcomes Liaison Agent")
                except Exception as e:
                    self.logger.warning(f"⚠️ Business Outcomes Liaison not available: {e}")
                
                self.logger.info("✅ Liaison agent discovery complete")
        except Exception as e:
            self.logger.warning(f"⚠️ Some liaison agents not available: {e}")
    
    # ========================================================================
    # SOA APIs
    # ========================================================================
    
    async def send_message_to_guide(
        self,
        message: str,
        session_id: str,  # CHANGED from conversation_id
        user_id: str
    ) -> Dict[str, Any]:
        """
        Send message to Guide Agent (SOA API).
        
        Implements: Landing page Guide Agent interaction and persistent chat panel.
        
        Args:
            message: User's message
            session_id: Session ID (conversations stored in session)
            user_id: User ID
        
        Returns:
            Response from Guide Agent
        """
        try:
            if not self.guide_agent:
                return {
                    "success": False,
                    "error": "Guide Agent not available"
                }
            
            # Add user message to conversation via Session Manager
            if self.session_manager:
                await self.session_manager.add_conversation_message(
                    session_id=session_id,
                    agent_type="guide_agent",
                    role="user",
                    content=message
                )
            
            # Send to Guide Agent
            try:
                # Guide Agent provides guidance via its provide_guidance method
                response = await self.guide_agent.provide_guidance({
                    "message": message,
                    "session_id": session_id,  # Pass session_id
                    "user_id": user_id,
                    "user_context": {}
                })
                
                guidance_text = response.get("guidance", "") if isinstance(response, dict) else str(response)
                
                # Extract orchestrator context if available
                orchestrator_context = None
                if isinstance(response, dict) and response.get("workflow_id"):
                    orchestrator_context = {
                        "orchestrator": response.get("orchestrator"),
                        "workflow_id": response.get("workflow_id"),
                        "status": response.get("status", "active")
                    }
                
            except Exception as e:
                self.logger.error(f"Guide Agent error: {e}")
                guidance_text = f"I'm here to help! (Service initializing: {str(e)[:50]})"
                orchestrator_context = None
            
            # Add assistant response to conversation via Session Manager
            if self.session_manager:
                await self.session_manager.add_conversation_message(
                    session_id=session_id,
                    agent_type="guide_agent",
                    role="assistant",
                    content=guidance_text,
                    orchestrator_context=orchestrator_context
                )
            
            return {
                "success": True,
                "response": guidance_text,
                "session_id": session_id,  # Return session_id
                "agent": "guide"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Send message to guide failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_message_to_liaison(
        self,
        message: str,
        pillar: str,
        session_id: str,  # CHANGED from conversation_id
        user_id: str
    ) -> Dict[str, Any]:
        """
        Send message to pillar-specific liaison agent (SOA API).
        
        Implements: Pillar-specific liaison chat per MVP requirements.
        
        Args:
            message: User's message
            pillar: Pillar name (content, insights, operations, business_outcomes)
            session_id: Session ID (conversations stored in session)
            user_id: User ID
        
        Returns:
            Response from liaison agent
        """
        try:
            # Get appropriate liaison agent
            liaison_agents = {
                "content": self.content_liaison,
                "insights": self.insights_liaison,
                "operations": self.operations_liaison,
                "business_outcomes": self.business_outcomes_liaison
            }
            
            liaison = liaison_agents.get(pillar)
            if not liaison:
                return {
                    "success": False,
                    "error": f"Liaison agent for {pillar} not available"
                }
            
            # Map pillar to agent_type
            agent_type_map = {
                "content": "content_liaison",
                "insights": "insights_liaison",
                "operations": "operations_liaison",
                "business_outcomes": "business_outcomes_liaison"
            }
            agent_type = agent_type_map.get(pillar, f"{pillar}_liaison")
            
            # Add user message to conversation via Session Manager
            if self.session_manager:
                await self.session_manager.add_conversation_message(
                    session_id=session_id,
                    agent_type=agent_type,
                    role="user",
                    content=message
                )
            
            # Send to liaison agent
            try:
                # Liaison agents have process_user_query method
                from utilities import UserContext
                user_context = UserContext(
                    user_id=user_id,
                    tenant_id="default",  # TODO: Get from session
                    roles=["user"]
                )
                
                # Pass session_id instead of conversation_id
                response = await liaison.process_user_query(
                    query=message,
                    session_id=session_id,  # CHANGED from conversation_id
                    user_context=user_context
                )
                
                response_text = response.get("response", "") if isinstance(response, dict) else str(response)
                
                # Extract orchestrator context if available
                orchestrator_context = None
                if isinstance(response, dict) and response.get("workflow_id"):
                    orchestrator_context = {
                        "orchestrator": response.get("orchestrator"),
                        "workflow_id": response.get("workflow_id"),
                        "status": response.get("status", "active")
                    }
                
            except Exception as e:
                self.logger.error(f"Liaison Agent error: {e}")
                response_text = f"I'm here to help with {pillar}! (Service initializing: {str(e)[:50]})"
                orchestrator_context = None
            
            # Add assistant response to conversation via Session Manager
            if self.session_manager:
                await self.session_manager.add_conversation_message(
                    session_id=session_id,
                    agent_type=agent_type,
                    role="assistant",
                    content=response_text,
                    orchestrator_context=orchestrator_context
                )
            
            return {
                "success": True,
                "response": response_text,
                "session_id": session_id,  # Return session_id
                "pillar": pillar,
                "agent": f"{pillar}_liaison"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Send message to liaison failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_conversation_history(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Get conversation history (SOA API).
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            Conversation history
        """
        if conversation_id in self.conversations:
            return {
                "success": True,
                "conversation": self.conversations[conversation_id]
            }
        return {
            "success": False,
            "error": "Conversation not found"
        }
    
    async def create_conversation(
        self,
        user_id: str,
        initial_agent: str = "guide"
    ) -> Dict[str, Any]:
        """
        Create new conversation (SOA API).
        
        Args:
            user_id: User ID
            initial_agent: Initial agent (guide, content, insights, operations, business_outcomes)
        
        Returns:
            New conversation details
        """
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "active_agent": initial_agent,
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "active_agent": initial_agent
        }
    
    async def get_active_agent(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Get active agent for conversation (SOA API).
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            Active agent details
        """
        if conversation_id in self.conversations:
            return {
                "success": True,
                "active_agent": self.conversations[conversation_id]["active_agent"]
            }
        return {
            "success": False,
            "error": "Conversation not found"
        }
    
    async def switch_agent(
        self,
        conversation_id: str,
        new_agent: str
    ) -> Dict[str, Any]:
        """
        Switch active agent in conversation (SOA API).
        
        Enables switching between Guide Agent and pillar liaisons.
        
        Args:
            conversation_id: Conversation ID
            new_agent: New agent (guide, content, insights, operations, business_outcomes)
        
        Returns:
            Switch result
        """
        if conversation_id in self.conversations:
            old_agent = self.conversations[conversation_id]["active_agent"]
            self.conversations[conversation_id]["active_agent"] = new_agent
            
            # Add system message about switch
            self.conversations[conversation_id]["messages"].append({
                "from": "system",
                "message": f"Switched from {old_agent} to {new_agent}",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": True,
                "old_agent": old_agent,
                "new_agent": new_agent
            }
        return {
            "success": False,
            "error": "Conversation not found"
        }
    
    # ========================================================================
    # HEALTH & METADATA
    # ========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check (inherited from RealmServiceBase)."""
        return {
            "status": "healthy" if self.is_initialized else "unhealthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "guide_agent_available": self.guide_agent is not None,
            "liaison_agents_available": {
                "content": self.content_liaison is not None,
                "insights": self.insights_liaison is not None,
                "operations": self.operations_liaison is not None,
                "business_outcomes": self.business_outcomes_liaison is not None
            },
            "active_conversations": len(self.conversations),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities (inherited from RealmServiceBase)."""
        return {
            "service_name": self.service_name,
            "service_type": "experience_service",
            "realm": "experience",
            "layer": "chat_interface",
            "capabilities": ["chat", "agent_routing", "conversation_management"],
            "soa_apis": [
                "send_message_to_guide", "send_message_to_liaison",
                "get_conversation_history", "create_conversation",
                "get_active_agent", "switch_agent"
            ],
            "mcp_tools": [],
            "agents_supported": {
                "guide": self.guide_agent is not None,
                "content_liaison": self.content_liaison is not None,
                "insights_liaison": self.insights_liaison is not None,
                "operations_liaison": self.operations_liaison is not None,
                "business_outcomes_liaison": self.business_outcomes_liaison is not None
            }
        }


