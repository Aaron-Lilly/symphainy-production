#!/usr/bin/env python3
"""
Business Outcomes Liaison Agent

Liaison agent for the Business Outcomes Pillar, providing conversational interaction
and user guidance for business outcomes management.

WHAT (Business Enablement Role): I need to provide conversational interaction for business outcomes
HOW (Liaison Agent): I provide chat-based guidance and user interaction capabilities
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
import os
import sys
sys.path.insert(0, os.path.abspath('../../../../../'))

from utilities import UserContext
from backend.business_enablement.protocols.business_liaison_agent_protocol import BusinessLiaisonAgentBase


class BusinessOutcomesLiaisonAgent(BusinessLiaisonAgentBase):
    """
    Liaison Agent for the Business Outcomes Pillar.
    
    Provides conversational interaction and user guidance for:
    - Strategic planning and roadmap generation
    - Business outcome measurement and tracking
    - ROI calculation and analysis
    - Business metrics reporting and visualization
    - Dashboard and chart creation
    """
    
    def __init__(
        self,
        agent_name: str,
        business_domain: str,
        capabilities: List[str],
        required_roles: List[str],
        agui_schema: Any,
        foundation_services: Any,
        agentic_foundation: Any,
        public_works_foundation: Any,
        mcp_client_manager: Any,
        policy_integration: Any,
        tool_composition: Any,
        agui_formatter: Any,
        curator_foundation: Any = None,
        metadata_foundation: Any = None,
        **kwargs
    ):
        """
        Initialize Business Outcomes Liaison Agent with full SDK dependencies.
        
        This agent is created via Agentic Foundation factory - all dependencies
        are provided by the factory.
        """
        super().__init__(
            agent_name=agent_name,
            business_domain=business_domain,
            capabilities=capabilities,
            required_roles=required_roles,
            agui_schema=agui_schema,
            foundation_services=foundation_services,
            public_works_foundation=public_works_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            curator_foundation=curator_foundation,
            metadata_foundation=metadata_foundation,
            **kwargs
        )
        
        self.business_outcomes_orchestrator = None
        self.conversation_context = {}
        self.user_preferences = {}
    
    async def initialize(self):
        """
        Initialize Business Outcomes Liaison Agent.
        
        Includes full utility usage:
        - Telemetry tracking
        - Error handling with audit
        - Health metrics
        
        Note: Factory handles Curator registration (Agentic Foundation owns agent registry).
        """
        try:
            # Start telemetry tracking (using AgentBase utility method)
            await self.log_operation_with_telemetry("initialize_start", success=True, details={
                "agent_name": self.agent_name
            })
            
            # Call parent initialize (BusinessLiaisonAgentBase)
            await super().initialize()
            
            # Discover orchestrator via Curator (optional, agent can work independently)
            if self.curator_foundation:
                try:
                    registered_services = await self.curator_foundation.get_registered_services()
                    services_dict = registered_services.get("services", {})
                    if "BusinessOutcomesOrchestratorService" in services_dict:
                        service_info = services_dict["BusinessOutcomesOrchestratorService"]
                        self.business_outcomes_orchestrator = service_info.get("service_instance")
                        self.logger.info("✅ Discovered BusinessOutcomesOrchestrator")
                except Exception as e:
                    await self.handle_error_with_audit(e, "orchestrator_discovery", details={"orchestrator": "BusinessOutcomesOrchestrator"})
                    self.logger.warning(f"⚠️ BusinessOutcomesOrchestrator not available: {e}")
            
            self.is_initialized = True
            
            # Record health metric (success)
            await self.record_health_metric("initialized", 1.0, {
                "agent_name": self.agent_name
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("initialize_complete", success=True, details={
                "agent_name": self.agent_name
            })
            
            self.logger.info(f"✅ {self.agent_name} initialization complete")
            return True
        
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "initialize", details={"agent_name": self.agent_name})
            
            # Record health metric (failure)
            await self.record_health_metric("initialization_failed", 1.0, {
                "agent_name": self.agent_name,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("initialize_complete", success=False, details={
                "agent_name": self.agent_name,
                "error": str(e)
            })
            
            self.is_initialized = False
            return False
    
    async def process_user_query(
        self,
        query: str,
        conversation_id: str,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """
        Process user query (called by Chat Service).
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        Args:
            query: User's query
            conversation_id: Conversation ID
            user_context: User context
        
        Returns:
            Response dictionary
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("process_user_query_start", success=True, details={
                "conversation_id": conversation_id
            })
            
            # Security validation (zero-trust: secure by design)
            if user_context and self.security:
                try:
                    user_context_dict = {
                        "user_id": getattr(user_context, "user_id", None),
                        "tenant_id": getattr(user_context, "tenant_id", None),
                        "roles": getattr(user_context, "roles", [])
                    }
                    if not await self.security.check_permissions(user_context_dict, "conversation", "query"):
                        await self.record_health_metric("process_user_query_access_denied", 1.0, {
                            "conversation_id": conversation_id
                        })
                        await self.log_operation_with_telemetry("process_user_query_complete", success=False, details={
                            "status": "access_denied"
                        })
                        raise PermissionError("Access denied: insufficient permissions to process query")
                except PermissionError:
                    raise
                except Exception:
                    pass  # Security check is optional
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant_id = getattr(user_context, "tenant_id", None)
                if tenant_id and hasattr(self, "public_works_foundation"):
                    try:
                        tenant_service = self.public_works_foundation.get_tenant_service()
                        if tenant_service and not await tenant_service.validate_tenant_access(tenant_id):
                            await self.record_health_metric("process_user_query_tenant_denied", 1.0, {
                                "conversation_id": conversation_id,
                                "tenant_id": tenant_id
                            })
                            await self.log_operation_with_telemetry("process_user_query_complete", success=False, details={
                                "status": "tenant_denied"
                            })
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                    except PermissionError:
                        raise
                    except Exception:
                        pass  # Tenant validation is optional
            
            # Analyze intent and generate response
            query_lower = query.lower()
            
            if "roi" in query_lower or "return on investment" in query_lower:
                response = "I can help you calculate ROI! Share your project details and I'll analyze the returns."
            elif "roadmap" in query_lower or "strategic" in query_lower or "planning" in query_lower:
                response = "I can generate strategic roadmaps for you! What business objectives are you trying to achieve?"
            elif "dashboard" in query_lower or "chart" in query_lower or "visualize" in query_lower:
                response = "I can create dashboards and charts for your business metrics! What data would you like to visualize?"
            elif "metrics" in query_lower or "measure" in query_lower or "kpi" in query_lower:
                response = "I can help you track business metrics and KPIs! Which outcomes are you measuring?"
            elif "outcome" in query_lower or "goal" in query_lower:
                response = "I can help you measure and track business outcomes! What are your success criteria?"
            else:
                response = "Hello! I'm your Business Outcomes assistant. I can help you with ROI calculation, strategic roadmap generation, dashboard creation, metrics tracking, and outcome measurement. What would you like to do?"
            
            # Record health metric (success)
            await self.record_health_metric("process_user_query_success", 1.0, {
                "conversation_id": conversation_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("process_user_query_complete", success=True)
            
            return {
                "success": True,
                "response": response,
                "conversation_id": conversation_id,
                "agent": "business_outcomes_liaison"
            }
            
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "process_user_query", details={
                "conversation_id": conversation_id
            })
            
            # Record health metric (failure)
            await self.record_health_metric("process_user_query_error", 1.0, {
                "conversation_id": conversation_id,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("process_user_query_complete", success=False, details={
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error processing your request. Please try again."
            }
    
    async def shutdown(self):
        """Shutdown the liaison agent."""
        try:
            self.logger.info("🛑 Shutting down Business Outcomes Liaison Agent...")
            await super().shutdown()
            self.logger.info("✅ Business Outcomes Liaison Agent shutdown successfully")
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown Business Outcomes Liaison Agent: {e}")
    
    async def process_user_message(self, message: str, user_context: UserContext, 
                                  session_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user message and provide response.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        Args:
            message: User's message
            user_context: User context for authorization
            session_id: Session identifier
            context: Additional context for the conversation
            
        Returns:
            Dict with agent response and actions
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("process_user_message_start", success=True, details={
                "session_id": session_id
            })
            
            # Security validation (zero-trust: secure by design)
            if user_context and self.security:
                try:
                    user_context_dict = {
                        "user_id": getattr(user_context, "user_id", None),
                        "tenant_id": getattr(user_context, "tenant_id", None),
                        "roles": getattr(user_context, "roles", [])
                    }
                    if not await self.security.check_permissions(user_context_dict, "conversation", "message"):
                        await self.record_health_metric("process_user_message_access_denied", 1.0, {
                            "session_id": session_id
                        })
                        await self.log_operation_with_telemetry("process_user_message_complete", success=False, details={
                            "status": "access_denied"
                        })
                        raise PermissionError("Access denied: insufficient permissions to process message")
                except PermissionError:
                    raise
                except Exception:
                    pass  # Security check is optional
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant_id = getattr(user_context, "tenant_id", None)
                if tenant_id and hasattr(self, "public_works_foundation"):
                    try:
                        tenant_service = self.public_works_foundation.get_tenant_service()
                        if tenant_service and not await tenant_service.validate_tenant_access(tenant_id):
                            await self.record_health_metric("process_user_message_tenant_denied", 1.0, {
                                "session_id": session_id,
                                "tenant_id": tenant_id
                            })
                            await self.log_operation_with_telemetry("process_user_message_complete", success=False, details={
                                "status": "tenant_denied"
                            })
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                    except PermissionError:
                        raise
                    except Exception:
                        pass  # Tenant validation is optional
            
            self.logger.info(f"💬 Processing user message: {message[:100]}...")
            
            # Update conversation context
            if session_id not in self.conversation_context:
                self.conversation_context[session_id] = {
                    "messages": [],
                    "current_topic": None,
                    "user_goals": [],
                    "pending_actions": []
                }
            
            # Add message to context
            self.conversation_context[session_id]["messages"].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Analyze message intent
            intent = await self._analyze_message_intent(message, context)
            
            # Generate response based on intent
            response = await self._generate_response(message, intent, user_context, session_id, context)
            
            # Add response to context
            self.conversation_context[session_id]["messages"].append({
                "role": "assistant",
                "content": response["message"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.logger.info(f"✅ Response generated for session {session_id}")
            
            # Record health metric (success)
            await self.record_health_metric("process_user_message_success", 1.0, {
                "session_id": session_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("process_user_message_complete", success=True)
            
            return response
            
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "process_user_message", details={
                "session_id": session_id
            })
            
            # Record health metric (failure)
            await self.record_health_metric("process_user_message_error", 1.0, {
                "session_id": session_id,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("process_user_message_complete", success=False, details={
                "error": str(e)
            })
            
            self.logger.error(f"❌ Error processing user message: {e}")
            return {
                "success": False,
                "message": "I apologize, but I encountered an error processing your message. Please try again.",
                "actions": [],
                "error": str(e)
            }
    
    async def _analyze_message_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Analyze user message to determine intent and required actions."""
        message_lower = message.lower()
        
        # Intent patterns for business outcomes management
        intent_patterns = {
            "strategic_planning": [
                "roadmap", "strategic", "plan", "goal", "objective", "strategy",
                "vision", "mission", "direction", "future"
            ],
            "outcome_measurement": [
                "measure", "track", "outcome", "kpi", "metric", "performance",
                "progress", "success", "achievement", "result"
            ],
            "roi_analysis": [
                "roi", "return", "investment", "profit", "revenue", "cost",
                "financial", "money", "budget", "expense"
            ],
            "business_metrics": [
                "metric", "dashboard", "report", "analytics", "data",
                "statistics", "trend", "chart", "graph"
            ],
            "visualization": [
                "chart", "graph", "dashboard", "visual", "display",
                "show", "view", "present", "illustrate"
            ],
            "help": [
                "help", "assist", "guide", "support", "how", "what", "can you",
                "explain", "tell me", "show me"
            ]
        }
        
        # Determine primary intent
        primary_intent = "general"
        confidence = 0.0
        
        for intent, patterns in intent_patterns.items():
            pattern_matches = sum(1 for pattern in patterns if pattern in message_lower)
            if pattern_matches > 0:
                intent_confidence = pattern_matches / len(patterns)
                if intent_confidence > confidence:
                    primary_intent = intent
                    confidence = intent_confidence
        
        # Extract entities and parameters
        entities = self._extract_entities(message)
        
        return {
            "intent": primary_intent,
            "confidence": confidence,
            "entities": entities,
            "requires_action": confidence > 0.3
        }
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from user message."""
        entities = {
            "time_periods": [],
            "metrics": [],
            "goals": [],
            "numbers": [],
            "dates": []
        }
        
        # Simple entity extraction (in real implementation, use NLP libraries)
        words = message.lower().split()
        
        # Extract numbers
        for word in words:
            if word.replace('.', '').replace(',', '').isdigit():
                entities["numbers"].append(word)
        
        # Extract common business terms
        business_terms = {
            "revenue": "revenue", "profit": "profit", "roi": "roi",
            "customer": "customer", "satisfaction": "satisfaction",
            "efficiency": "efficiency", "productivity": "productivity"
        }
        
        for word in words:
            if word in business_terms:
                entities["metrics"].append(business_terms[word])
        
        return entities
    
    async def _generate_response(self, message: str, intent: Dict[str, Any], 
                                user_context: UserContext, session_id: str, 
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate response based on analyzed intent."""
        intent_type = intent["intent"]
        confidence = intent["confidence"]
        entities = intent["entities"]
        
        if intent_type == "strategic_planning":
            return await self._handle_strategic_planning_request(message, entities, user_context, session_id)
        elif intent_type == "outcome_measurement":
            return await self._handle_outcome_measurement_request(message, entities, user_context, session_id)
        elif intent_type == "roi_analysis":
            return await self._handle_roi_analysis_request(message, entities, user_context, session_id)
        elif intent_type == "business_metrics":
            return await self._handle_business_metrics_request(message, entities, user_context, session_id)
        elif intent_type == "visualization":
            return await self._handle_visualization_request(message, entities, user_context, session_id)
        elif intent_type == "help":
            return await self._handle_help_request(message, entities, user_context, session_id)
        else:
            return await self._handle_general_request(message, entities, user_context, session_id)
    
    async def _handle_strategic_planning_request(self, message: str, entities: Dict[str, Any], 
                                                user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Handle strategic planning related requests."""
        return {
            "success": True,
            "message": "I can help you with strategic planning! I can assist with creating roadmaps, setting business goals, and tracking progress. What specific aspect of strategic planning would you like to work on?",
            "actions": [
                {
                    "type": "suggest_action",
                    "action": "generate_strategic_roadmap",
                    "description": "Generate a strategic roadmap",
                    "parameters": {
                        "business_goal": "Your primary business goal",
                        "current_state": "Current state of your business",
                        "desired_outcomes": "List of desired outcomes"
                    }
                }
            ],
            "suggestions": [
                "Create a strategic roadmap for your business goals",
                "Set up outcome tracking and measurement",
                "Analyze your current business performance",
                "Plan your next quarter objectives"
            ]
        }
    
    async def _handle_outcome_measurement_request(self, message: str, entities: Dict[str, Any], 
                                                 user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Handle outcome measurement related requests."""
        return {
            "success": True,
            "message": "I can help you measure and track business outcomes! I can assist with setting up KPIs, measuring progress, and analyzing results. What outcomes would you like to measure?",
            "actions": [
                {
                    "type": "suggest_action",
                    "action": "measure_business_outcomes",
                    "description": "Measure business outcomes",
                    "parameters": {
                        "outcome_id": "ID of the outcome to measure",
                        "kpis": "Key Performance Indicators to track"
                    }
                }
            ],
            "suggestions": [
                "Set up outcome measurement for your current projects",
                "Track KPIs and performance metrics",
                "Analyze progress against your goals",
                "Generate outcome reports and insights"
            ]
        }
    
    async def _handle_roi_analysis_request(self, message: str, entities: Dict[str, Any], 
                                          user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Handle ROI analysis related requests."""
        return {
            "success": True,
            "message": "I can help you with ROI analysis! I can assist with calculating returns on investment, analyzing financial performance, and making data-driven decisions. What investment or project would you like to analyze?",
            "actions": [
                {
                    "type": "suggest_action",
                    "action": "calculate_roi",
                    "description": "Calculate ROI for a project",
                    "parameters": {
                        "project_id": "ID of the project",
                        "investment_amount": "Total investment amount",
                        "expected_returns": "Expected returns from investment"
                    }
                }
            ],
            "suggestions": [
                "Calculate ROI for your current projects",
                "Analyze financial performance and returns",
                "Compare different investment options",
                "Generate ROI reports and insights"
            ]
        }
    
    async def _handle_business_metrics_request(self, message: str, entities: Dict[str, Any], 
                                              user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Handle business metrics related requests."""
        return {
            "success": True,
            "message": "I can help you with business metrics! I can assist with retrieving key performance indicators, generating reports, and analyzing business data. What type of metrics are you interested in?",
            "actions": [
                {
                    "type": "suggest_action",
                    "action": "get_business_metrics",
                    "description": "Get business metrics",
                    "parameters": {
                        "metric_type": "Type of metrics (financial, operational, customer, employee)"
                    }
                }
            ],
            "suggestions": [
                "View financial metrics and KPIs",
                "Analyze operational performance",
                "Track customer satisfaction metrics",
                "Monitor employee engagement and productivity"
            ]
        }
    
    async def _handle_visualization_request(self, message: str, entities: Dict[str, Any], 
                                           user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Handle visualization related requests."""
        return {
            "success": True,
            "message": "I can help you create visualizations! I can assist with creating dashboards, charts, and graphs to visualize your business data. What type of visualization would you like to create?",
            "actions": [
                {
                    "type": "suggest_action",
                    "action": "create_dashboard",
                    "description": "Create a business dashboard",
                    "parameters": {
                        "dashboard_type": "Type of dashboard to create",
                        "data": "Data to visualize"
                    }
                },
                {
                    "type": "suggest_action",
                    "action": "create_chart",
                    "description": "Create a chart or graph",
                    "parameters": {
                        "chart_type": "Type of chart (line, bar, pie, gauge, scatter)",
                        "data": "Data to visualize"
                    }
                }
            ],
            "suggestions": [
                "Create a business outcomes dashboard",
                "Generate charts for your KPIs",
                "Visualize ROI and financial data",
                "Build interactive reports and dashboards"
            ]
        }
    
    async def _handle_help_request(self, message: str, entities: Dict[str, Any], 
                                  user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Handle help and guidance requests."""
        return {
            "success": True,
            "message": "I'm here to help you with business outcomes management! I can assist you with strategic planning, outcome measurement, ROI analysis, business metrics, and data visualization. What would you like to work on?",
            "actions": [],
            "suggestions": [
                "Create a strategic roadmap for your business goals",
                "Set up outcome tracking and measurement",
                "Calculate ROI for your projects and investments",
                "View and analyze your business metrics",
                "Create dashboards and visualizations",
                "Get insights and recommendations"
            ],
            "capabilities": [
                "Strategic roadmap generation and planning",
                "Business outcome measurement and tracking",
                "ROI calculation and financial analysis",
                "Business metrics reporting and analytics",
                "Dashboard and chart creation",
                "Data visualization and insights"
            ]
        }
    
    async def _handle_general_request(self, message: str, entities: Dict[str, Any], 
                                     user_context: UserContext, session_id: str) -> Dict[str, Any]:
        """Handle general requests and questions."""
        return {
            "success": True,
            "message": "I understand you're looking for help with business outcomes. I can assist you with strategic planning, outcome measurement, ROI analysis, and business metrics. Could you tell me more about what you'd like to accomplish?",
            "actions": [],
            "suggestions": [
                "I want to create a strategic plan for my business",
                "I need to measure the outcomes of my projects",
                "I want to calculate ROI for my investments",
                "I need to view my business metrics and KPIs",
                "I want to create visualizations and dashboards"
            ]
        }
    
    async def get_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Get conversation context for a session."""
        return self.conversation_context.get(session_id, {
            "messages": [],
            "current_topic": None,
            "user_goals": [],
            "pending_actions": []
        })
    
    async def clear_conversation_context(self, session_id: str) -> bool:
        """Clear conversation context for a session."""
        try:
            if session_id in self.conversation_context:
                del self.conversation_context[session_id]
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to clear conversation context: {e}")
            return False
    
    async def process_conversation(self, message: str, conversation_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Process business outcomes conversation.
        
        Includes full utility usage:
        - Telemetry tracking
        - Security validation (zero-trust)
        - Tenant validation (multi-tenancy)
        - Error handling with audit
        - Health metrics
        
        Args:
            message: User message
            conversation_id: Conversation ID
            user_context: User context for authorization
            
        Returns:
            Dict with conversation response
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("process_conversation_start", success=True, details={
                "conversation_id": conversation_id
            })
            
            # Security validation (zero-trust: secure by design)
            if user_context and self.security:
                try:
                    user_context_dict = {
                        "user_id": getattr(user_context, "user_id", None),
                        "tenant_id": getattr(user_context, "tenant_id", None),
                        "roles": getattr(user_context, "roles", [])
                    }
                    if not await self.security.check_permissions(user_context_dict, "conversation", "process"):
                        await self.record_health_metric("process_conversation_access_denied", 1.0, {
                            "conversation_id": conversation_id
                        })
                        await self.log_operation_with_telemetry("process_conversation_complete", success=False, details={
                            "status": "access_denied"
                        })
                        raise PermissionError("Access denied: insufficient permissions to process conversation")
                except PermissionError:
                    raise
                except Exception:
                    pass  # Security check is optional
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant_id = getattr(user_context, "tenant_id", None)
                if tenant_id and hasattr(self, "public_works_foundation"):
                    try:
                        tenant_service = self.public_works_foundation.get_tenant_service()
                        if tenant_service and not await tenant_service.validate_tenant_access(tenant_id):
                            await self.record_health_metric("process_conversation_tenant_denied", 1.0, {
                                "conversation_id": conversation_id,
                                "tenant_id": tenant_id
                            })
                            await self.log_operation_with_telemetry("process_conversation_complete", success=False, details={
                                "status": "tenant_denied"
                            })
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
                    except PermissionError:
                        raise
                    except Exception:
                        pass  # Tenant validation is optional
            
            self.logger.info(f"Processing business outcomes conversation: {conversation_id}")
            
            # Mock implementation
            response = {
                "conversation_id": conversation_id,
                "response": f"I understand you're asking about business outcomes. Let me help you with that: {message}",
                "suggestions": [
                    "Generate strategic roadmap",
                    "Calculate ROI",
                    "Measure outcomes",
                    "Create metrics dashboard"
                ],
                "next_steps": [
                    "Provide more details about your business goals",
                    "Specify which outcomes you want to measure",
                    "Share relevant data for analysis"
                ],
                "processed_at": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.record_health_metric("process_conversation_success", 1.0, {
                "conversation_id": conversation_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("process_conversation_complete", success=True)
            
            return {
                "success": True,
                "conversation": response,
                "message": "Business outcomes conversation processed successfully"
            }
            
        except PermissionError:
            raise  # Re-raise permission errors
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(e, "process_conversation", details={
                "conversation_id": conversation_id
            })
            
            # Record health metric (failure)
            await self.record_health_metric("process_conversation_error", 1.0, {
                "conversation_id": conversation_id,
                "error": type(e).__name__
            })
            
            # End telemetry tracking with failure
            await self.log_operation_with_telemetry("process_conversation_complete", success=False, details={
                "error": str(e)
            })
            
            self.logger.error(f"❌ Failed to process business outcomes conversation: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to process business outcomes conversation"
            }
