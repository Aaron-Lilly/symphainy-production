#!/usr/bin/env python3
"""
Business Liaison Agent Protocol

Defines the standard protocol for Business Enablement liaison agents.
All Business Enablement liaison agents must follow this protocol.

WHAT (Business Enablement Role): I provide conversational interface and user guidance
HOW (Liaison Agent Protocol): I follow the standard agent structure and patterns
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from utilities import UserContext
from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase


class ConversationType(Enum):
    """Types of conversations the liaison agent can handle."""
    GENERAL_INQUIRY = "general_inquiry"
    CAPABILITY_GUIDANCE = "capability_guidance"
    WORKFLOW_ASSISTANCE = "workflow_assistance"
    TROUBLESHOOTING = "troubleshooting"
    FEATURE_EXPLANATION = "feature_explanation"
    INTEGRATION_HELP = "integration_help"


class ResponseType(Enum):
    """Types of responses the liaison agent can provide."""
    TEXT_RESPONSE = "text_response"
    GUIDANCE_STEPS = "guidance_steps"
    CAPABILITY_LIST = "capability_list"
    WORKFLOW_SUGGESTION = "workflow_suggestion"
    ERROR_RESOLUTION = "error_resolution"
    INTEGRATION_GUIDE = "integration_guide"


@dataclass
class ConversationRequest:
    """Request for conversation with liaison agent."""
    message: str
    conversation_type: ConversationType
    user_context: UserContext
    session_id: str
    context: Dict[str, Any] = None
    previous_messages: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if self.previous_messages is None:
            self.previous_messages = []


@dataclass
class ConversationResponse:
    """Response from liaison agent conversation."""
    success: bool
    response_type: ResponseType
    message: str
    guidance_steps: List[str] = None
    suggested_capabilities: List[str] = None
    workflow_suggestions: List[Dict[str, Any]] = None
    error_resolution: Dict[str, Any] = None
    integration_guide: Dict[str, Any] = None
    confidence_score: float = 0.0
    processing_time: float = 0.0
    conversation_id: str = ""
    error_details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.guidance_steps is None:
            self.guidance_steps = []
        if self.suggested_capabilities is None:
            self.suggested_capabilities = []
        if self.workflow_suggestions is None:
            self.workflow_suggestions = []
        if self.error_resolution is None:
            self.error_resolution = {}


@dataclass
class CapabilityGuidanceRequest:
    """Request for capability guidance."""
    user_goal: str
    current_context: Dict[str, Any]
    user_context: UserContext
    session_id: str
    preferred_approach: Optional[str] = None
    
    def __post_init__(self):
        if self.current_context is None:
            self.current_context = {}


@dataclass
class CapabilityGuidanceResponse:
    """Response from capability guidance."""
    success: bool
    recommended_capabilities: List[str]
    guidance_steps: List[str]
    alternative_approaches: List[str]
    prerequisites: List[str]
    estimated_time: str
    difficulty_level: str
    confidence_score: float
    processing_time: float
    message: str = ""
    error_details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.recommended_capabilities is None:
            self.recommended_capabilities = []
        if self.guidance_steps is None:
            self.guidance_steps = []
        if self.alternative_approaches is None:
            self.alternative_approaches = []
        if self.prerequisites is None:
            self.prerequisites = []


class BusinessLiaisonAgentProtocol(ABC):
    """
    Business Liaison Agent Protocol
    
    Abstract base class that defines the standard protocol for Business Enablement liaison agents.
    All Business Enablement liaison agents must inherit from this class.
    
    WHAT (Business Enablement Role): I provide conversational interface and user guidance
    HOW (Liaison Agent Protocol): I follow the standard agent structure and patterns
    """
    
    def __init__(self, agent_name: str, business_domain: str, utility_foundation=None):
        """Initialize Business liaison agent protocol."""
        self.agent_name = agent_name
        self.business_domain = business_domain
        self.utility_foundation = utility_foundation
        self.conversation_history = []
        self.capabilities = []
        
    @abstractmethod
    async def initialize(self, user_context: UserContext = None):
        """Initialize the Business liaison agent."""
        pass
    
    @abstractmethod
    async def process_conversation(self, request: ConversationRequest) -> ConversationResponse:
        """
        Process a conversation request.
        
        Args:
            request: Conversation request with user message and context
            
        Returns:
            ConversationResponse with agent response and guidance
        """
        pass
    
    @abstractmethod
    async def provide_capability_guidance(self, request: CapabilityGuidanceRequest) -> CapabilityGuidanceResponse:
        """
        Provide guidance on business capabilities.
        
        Args:
            request: Capability guidance request with user goal
            
        Returns:
            CapabilityGuidanceResponse with recommendations and steps
        """
        pass
    
    @abstractmethod
    async def get_available_capabilities(self) -> List[str]:
        """Get list of available business capabilities."""
        pass
    
    @abstractmethod
    async def get_conversation_history(self, session_id: str, user_context: UserContext) -> List[ConversationResponse]:
        """Get conversation history for a session."""
        pass
    
    @abstractmethod
    async def clear_conversation_history(self, session_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Clear conversation history for a session."""
        pass
    
    @abstractmethod
    async def get_agent_analytics(self) -> Dict[str, Any]:
        """Get analytics for this liaison agent."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of this liaison agent."""
        pass


class BusinessLiaisonAgentBase(AgentBase):
    """
    Business Liaison Agent Base Class (Refactored with Pure DI)
    
    Base class for Business Enablement liaison agents that provides common functionality.
    Refactored to inherit from the new AgentBase with pure dependency injection.
    
    WHAT (Business Enablement Role): I need to implement liaison agents with standard patterns
    HOW (Liaison Agent Base): I provide common agent functionality and business integration using pure DI
    """
    
    def __init__(self, agent_name: str, business_domain: str, capabilities: List[str], 
                 required_roles: List[str], agui_schema: 'AGUISchema', 
                 foundation_services: 'DIContainerService',
                 agentic_foundation: 'AgenticFoundationService',  # Required by AgentBase
                 public_works_foundation: 'PublicWorksFoundationService',
                 mcp_client_manager: 'MCPClientManager',
                 policy_integration: 'PolicyIntegration',
                 tool_composition: 'ToolComposition',
                 agui_formatter: 'AGUIOutputFormatter',
                 curator_foundation=None, metadata_foundation=None, **kwargs):
        """Initialize Business liaison agent base with pure dependency injection."""
        # Import here to avoid circular imports
        from foundations.agentic_foundation.agent_sdk.agent_base import AgentBase
        
        # Initialize the base AgentBase with all required dependencies
        super().__init__(
            agent_name=agent_name,
            capabilities=capabilities,
            required_roles=required_roles,
            agui_schema=agui_schema,
            foundation_services=foundation_services,
            agentic_foundation=agentic_foundation,  # Required by AgentBase
            public_works_foundation=public_works_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator_foundation,
            metadata_foundation=metadata_foundation,
            **kwargs
        )
        
        # Business-specific properties
        self.business_domain = business_domain
        self.agent_protocol = None
        self.conversation_sessions = {}
        
        # WebSocket SDK (initialized in initialize())
        self.websocket_sdk = None
        self.websocket_connection_id: Optional[str] = None
        self.pillar: Optional[str] = None  # Set by orchestrator (content, insights, operations, business_outcomes)
        
        # Note: Agents use MCP tools (not SOA APIs) via mcp_client_manager (from AgentBase)
        # MCP Client Manager is initialized in AgentBase.initialize()
        
    async def initialize(self):
        """Initialize the Business liaison agent with WebSocket SDK and MCP tools."""
        # Call parent initialize first
        await super().initialize()
        
        if self.agent_protocol:
            await self.agent_protocol.initialize()
        
        try:
            # ✅ Get Agentic Foundation WebSocket SDK
            if self.agentic_foundation:
                self.websocket_sdk = await self.agentic_foundation.create_agent_websocket_sdk()
                if self.websocket_sdk:
                    self.logger.info("✅ Liaison Agent WebSocket SDK initialized")
                else:
                    self.logger.warning("⚠️ Failed to create WebSocket SDK")
            
            # ✅ Agents use MCP tools (not SOA APIs) - MCP Client Manager is initialized in AgentBase
            # No need to get service instances - agents use execute_role_tool() to call MCP tools
            if self.mcp_client_manager:
                self.logger.info("✅ Liaison Agent MCP Client Manager available (for Smart City MCP tools)")
            else:
                self.logger.warning("⚠️ Liaison Agent MCP Client Manager not available - MCP tools will not work")
            
            # Note: WebSocket connection is established per-session (not per-agent)
            # The connection is created when a user connects via the WebSocket endpoint
            # See Phase 5 for WebSocket endpoint implementation
            
            self.logger.info("✅ Liaison Agent initialization complete with WebSocket SDK and MCP tools")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Liaison Agent WebSocket/MCP tools: {e}")
            # Don't fail initialization - agent can still work without WebSocket/MCP tools
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        self.is_initialized = True
    
    async def handle_user_message(self, message: str, session_token: str, pillar: str) -> Dict[str, Any]:
        """
        Handle user message - composes WebSocket SDK + Smart City MCP Tools (pillar-specific).
        
        This method is called by the WebSocket endpoint (Phase 5) to process user messages.
        
        Args:
            message: User message
            session_token: User session token
            pillar: Pillar name (content, insights, operations, business_outcomes)
        
        Returns:
            Response dict with message and metadata
        """
        try:
            # ✅ Step 1: Session Management (via Traffic Cop MCP Tool)
            session = None
            session_id = None
            if self.mcp_client_manager:
                try:
                    # Use Traffic Cop MCP tool to create/get session
                    # Note: MCP tool is "create_session", we'll use session_token as session_id
                    session_result = await self.execute_role_tool(
                        "traffic_cop",
                        "create_session",
                        {
                            "session_id": session_token or "anonymous",
                            "user_id": session_token or "anonymous"
                        }
                    )
                    if session_result and isinstance(session_result, dict):
                        if session_result.get("success") or session_result.get("status") == "success":
                            session_id = session_result.get("session_id") or session_token
                            session = {"session_id": session_id}
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to get session via Traffic Cop MCP tool: {e}")
                    # Fallback: use session_token as session_id
                    session_id = session_token or "anonymous"
                    session = {"session_id": session_id}
            else:
                # Fallback: use session_token as session_id
                session_id = session_token or "anonymous"
                session = {"session_id": session_id}
            
            # ✅ Step 2: Store Message in History (via Post Office MCP Tool)
            # Note: Conversation history is stored per agent_type (pillar-specific)
            agent_type = f"{pillar}_liaison"  # e.g., "content_liaison", "insights_liaison"
            if self.mcp_client_manager and session_id:
                try:
                    await self.execute_role_tool(
                        "post_office",
                        "message_sender",
                        {
                            "request": {
                                "message_content": {"text": message},
                                "sender": agent_type,
                                "recipient": session_id,
                                "message_type": "chat"
                            }
                        }
                    )
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to store message via Post Office MCP tool: {e}")
            
            # ✅ Step 3: Process User Query (agent's own capability)
            # Call the agent's process_user_query method if available
            response_message = None
            intent = {"intent": "general", "confidence": 0.5}
            orchestrator_response = None
            
            if hasattr(self, 'process_user_query'):
                try:
                    # Create user context from session
                    from utilities.security_authorization.user_context import UserContext
                    user_context = UserContext(
                        user_id=session.get("user_id") if session and isinstance(session, dict) else "anonymous",
                        tenant_id=session.get("tenant_id") if session and isinstance(session, dict) else None,
                        roles=session.get("roles", []) if session and isinstance(session, dict) else [],
                        permissions=session.get("permissions", []) if session and isinstance(session, dict) else []
                    )
                    
                    # ⭐ NEW: Get solution context for enhanced prompting (Phase 5.1)
                    specialization_context = None
                    if session_id:
                        try:
                            # Get MVP Journey Orchestrator via Curator
                            curator = self.curator_foundation if hasattr(self, 'curator_foundation') and self.curator_foundation else None
                            if curator:
                                mvp_orchestrator = await curator.discover_service_by_name("MVPJourneyOrchestratorService")
                                if mvp_orchestrator:
                                    specialization_context = await mvp_orchestrator.get_specialization_context(session_id)
                                    if specialization_context:
                                        # Add specialization_context to user_context as attribute
                                        user_context.specialization_context = specialization_context
                                        self.logger.debug(f"✅ Solution context retrieved for session: {session_id}")
                        except Exception as e:
                            self.logger.warning(f"⚠️ Failed to get solution context: {e}")
                            # Continue without solution context - not critical
                    
                    # Call process_user_query
                    result = await self.process_user_query(
                        query=message,
                        session_id=session.get("session_id") if session and isinstance(session, dict) else session_id,
                        user_context=user_context
                    )
                    
                    if result and isinstance(result, dict):
                        response_message = result.get("message") or result.get("response")
                        intent = result.get("intent", intent)
                        orchestrator_response = result
                except Exception as e:
                    self.logger.error(f"❌ Failed to process user query via process_user_query: {e}")
                    import traceback
                    self.logger.error(f"Traceback: {traceback.format_exc()}")
                    # Log to stderr for immediate visibility
                    import sys
                    sys.stderr.write(f"\n❌ [LIAISON_AGENT] process_user_query failed: {e}\n")
                    sys.stderr.write(f"Traceback: {traceback.format_exc()}\n")
                    sys.stderr.flush()
            
            # Fallback: Use analyze intent if process_user_query not available or failed
            if not response_message:
                intent = await self._analyze_query_intent(message) if hasattr(self, '_analyze_query_intent') else {"intent": "general", "confidence": 0.5}
                
                # ✅ Step 4: Coordinate with Orchestrator (agent's own capability)
                if hasattr(self, 'coordinate_with_orchestrator'):
                    try:
                        orchestrator_response = await self.coordinate_with_orchestrator(intent, session)
                    except Exception as e:
                        self.logger.warning(f"⚠️ Failed to coordinate with orchestrator: {e}")
                
                # ✅ Step 5: Generate Response using LLM reasoning (agent's own capability)
                # Use LLM to provide intelligent response instead of echoing
                try:
                    llm_abstraction = await self.get_business_abstraction("llm")
                    if llm_abstraction:
                        from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
                        
                        # Build context-aware prompt
                        system_prompt = f"""You are a helpful {pillar} liaison agent. Your role is to provide intelligent, contextual responses to user queries. 
                        
Do NOT simply repeat or echo the user's question. Instead:
1. Understand what the user is asking
2. Provide helpful, actionable guidance
3. Reference the {pillar} pillar context when relevant
4. Be concise but informative

If you cannot answer the question, acknowledge it and suggest how the user might get help."""
                        
                        user_prompt = f"""User message: {message}
                        
Context:
- Pillar: {pillar}
- Intent: {intent.get('intent', 'general')}
- Session: {session.get('session_id', 'unknown') if session and isinstance(session, dict) else 'unknown'}

Provide a helpful response to the user's message."""
                        
                        llm_request = LLMRequest(
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}
                            ],
                            model=LLMModel.GPT_4O_MINI,
                            max_tokens=500,
                            temperature=0.7,
                            metadata={"task": "liaison_response", "pillar": pillar}
                        )
                        
                        llm_response = await llm_abstraction.generate_response(llm_request)
                        response_message = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
                        self.logger.info(f"✅ Generated LLM-based response for {pillar} liaison agent")
                    else:
                        self.logger.warning("⚠️ LLM abstraction not available for liaison response")
                        response_message = f"I'm here to help with {pillar}. How can I assist you?"
                except Exception as e:
                    self.logger.error(f"❌ Failed to generate LLM response: {e}")
                    import traceback
                    self.logger.error(f"Traceback: {traceback.format_exc()}")
                    response_message = f"I'm here to help with {pillar}. How can I assist you?"
                
                # Use orchestrator response if available and better
                if orchestrator_response and isinstance(orchestrator_response, dict):
                    orchestrator_msg = orchestrator_response.get("message") or orchestrator_response.get("response")
                    if orchestrator_msg and len(orchestrator_msg) > len(response_message):
                        response_message = orchestrator_msg
            
            # Ensure we have a response message
            if not response_message:
                response_message = f"I'm here to help with {pillar}. How can I assist you?"
            
            # Return response (WebSocket endpoint will send it)
            return {
                "type": "chat_response",
                "agent_type": "liaison",
                "pillar": pillar,
                "message": response_message,
                "session_token": session_token,
                "session_id": session.get("session_id") if session and isinstance(session, dict) else None,
                "intent": intent,
                "orchestrator_response": orchestrator_response
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle user message: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "type": "error",
                "agent_type": "liaison",
                "pillar": pillar,
                "message": "I encountered an error processing your message. Please try again.",
                "session_token": session_token,
                "error": str(e)
            }
    
    async def shutdown(self):
        """Shutdown the Business liaison agent."""
        if self.agent_protocol:
            await self.agent_protocol.shutdown()
        self.is_initialized = False
    
    async def process_conversation(self, request: ConversationRequest) -> ConversationResponse:
        """Process a conversation request."""
        if self.agent_protocol:
            return await self.agent_protocol.process_conversation(request)
        else:
            return ConversationResponse(
                success=False,
                response_type=ResponseType.TEXT_RESPONSE,
                message="Agent protocol not initialized",
                error_details={"error": "Agent protocol not initialized"}
            )
    
    async def provide_capability_guidance(self, request: CapabilityGuidanceRequest) -> CapabilityGuidanceResponse:
        """Provide capability guidance."""
        if self.agent_protocol:
            return await self.agent_protocol.provide_capability_guidance(request)
        else:
            return CapabilityGuidanceResponse(
                success=False,
                recommended_capabilities=[],
                guidance_steps=[],
                alternative_approaches=[],
                prerequisites=[],
                estimated_time="Unknown",
                difficulty_level="Unknown",
                confidence_score=0.0,
                processing_time=0.0,
                message="Agent protocol not initialized",
                error_details={"error": "Agent protocol not initialized"}
            )
    
    async def get_available_capabilities(self) -> List[str]:
        """Get available capabilities."""
        if self.agent_protocol:
            return await self.agent_protocol.get_available_capabilities()
        else:
            return []
    
    async def get_conversation_history(self, session_id: str, user_context: UserContext) -> List[ConversationResponse]:
        """Get conversation history."""
        if self.agent_protocol:
            return await self.agent_protocol.get_conversation_history(session_id, user_context)
        else:
            return []
    
    async def clear_conversation_history(self, session_id: str, user_context: UserContext) -> Dict[str, Any]:
        """Clear conversation history."""
        if self.agent_protocol:
            return await self.agent_protocol.clear_conversation_history(session_id, user_context)
        else:
            return {"success": False, "error": "Agent protocol not initialized"}
    
    async def get_agent_analytics(self) -> Dict[str, Any]:
        """Get agent analytics."""
        if self.agent_protocol:
            return await self.agent_protocol.get_agent_analytics()
        else:
            return {"error": "Agent protocol not initialized"}
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status."""
        return {
            "agent_name": self.agent_name,
            "business_domain": self.business_domain,
            "status": "healthy" if self.is_initialized else "unhealthy",
            "initialized": self.is_initialized,
            "timestamp": datetime.utcnow().isoformat()
        }
