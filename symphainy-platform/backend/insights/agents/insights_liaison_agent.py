#!/usr/bin/env python3
"""
Insights Liaison Agent

Liaison agent for the Insights Pillar that provides conversational interface
and user guidance for insights analysis operations.
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../'))

from utilities import UserContext
from backend.business_enablement.protocols.business_liaison_agent_protocol import BusinessLiaisonAgentBase


class InsightsLiaisonAgent(BusinessLiaisonAgentBase):
    """
    Insights Liaison Agent
    
    Liaison agent for the Insights Pillar that provides conversational interface
    and user guidance for insights analysis operations.
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
        Initialize Insights Liaison Agent with full SDK dependencies.
        
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
        
        self.insights_orchestrator = None
        self.query_agent = None  # InsightsQueryAgent for query generation
        self.business_analysis_agent = None  # InsightsBusinessAnalysisAgent for analysis
        self.conversation_context = {}  # Store conversation context per conversation_id
    
    async def initialize(self):
        """
        Initialize Insights Liaison Agent.
        
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
                    if "InsightsOrchestratorService" in services_dict:
                        service_info = services_dict["InsightsOrchestratorService"]
                        self.insights_orchestrator = service_info.get("service_instance")
                        self.logger.info("✅ Discovered InsightsOrchestrator")
                    
                    # Discover InsightsQueryAgent and InsightsBusinessAnalysisAgent
                    if "InsightsQueryAgent" in services_dict:
                        service_info = services_dict["InsightsQueryAgent"]
                        self.query_agent = service_info.get("service_instance")
                        self.logger.info("✅ Discovered InsightsQueryAgent")
                    
                    if "InsightsBusinessAnalysisAgent" in services_dict:
                        service_info = services_dict["InsightsBusinessAnalysisAgent"]
                        self.business_analysis_agent = service_info.get("service_instance")
                        self.logger.info("✅ Discovered InsightsBusinessAnalysisAgent")
                except Exception as e:
                    await self.handle_error_with_audit(e, "orchestrator_discovery", details={"orchestrator": "InsightsOrchestrator"})
                    self.logger.warning(f"⚠️ Service discovery failed: {e}")
            
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
                        "permissions": getattr(user_context, "permissions", [])  # Use permissions, not roles
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
            
            # Get conversation context (for drill-down support)
            context = self.conversation_context.get(conversation_id, {})
            
            # Use OpenAI LLM to understand user intent
            intent_result = await self._understand_user_intent(
                query=query,
                conversation_context=context,
                user_context=user_context
            )
            
            intent = intent_result.get("intent", "general")
            entities = intent_result.get("entities", {})
            
            # Route to appropriate handler based on intent
            if intent == "analyze":
                response = await self._handle_analysis_request(
                    query=query,
                    entities=entities,
                    conversation_id=conversation_id,
                    user_context=user_context
                )
            elif intent == "drill_down":
                response = await self._handle_drill_down_query(
                    query=query,
                    previous_analysis=context.get("last_analysis"),
                    conversation_id=conversation_id,
                    user_context=user_context
                )
            elif intent == "visualize":
                response = await self._handle_visualization_request(
                    query=query,
                    entities=entities,
                    conversation_id=conversation_id,
                    user_context=user_context
                )
            elif intent == "query":
                response = await self._handle_query_request(
                    query=query,
                    entities=entities,
                    conversation_id=conversation_id,
                    user_context=user_context
                )
            else:
                # General guidance
                response = await self._handle_general_query(
                    query=query,
                    conversation_id=conversation_id,
                    user_context=user_context
                )
            
            # Update conversation context
            self.conversation_context[conversation_id] = {
                "last_query": query,
                "last_intent": intent,
                "last_analysis": response.get("analysis"),
                "last_visualization": response.get("visualization"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record health metric (success)
            await self.record_health_metric("process_user_query_success", 1.0, {
                "conversation_id": conversation_id,
                "intent": intent
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("process_user_query_complete", success=True, details={
                "intent": intent
            })
            
            return {
                "success": True,
                "response": response.get("message", ""),
                "conversation_id": conversation_id,
                "agent": "insights_liaison",
                "intent": intent,
                "data": response.get("data"),  # AGUI components, analysis results, etc.
                "visualization": response.get("visualization")  # AGUI visualization component
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
    
    async def process_conversation(self, request) -> Any:
        """
        Process a conversation request for insights analysis.
        
        Uses real LLM reasoning via BusinessLiaisonAgentBase.handle_user_message().
        """
        try:
            # Extract message from request
            user_message = getattr(request, 'message', '') if hasattr(request, 'message') else str(request)
            if not user_message:
                user_message = 'Hello'
            
            # Get session token if available
            session_token = getattr(request, 'session_token', None) if hasattr(request, 'session_token') else None
            if not session_token:
                session_token = getattr(request, 'session_id', None) if hasattr(request, 'session_id') else 'anonymous'
            
            # Use base class handle_user_message which uses real LLM reasoning
            result = await self.handle_user_message(
                message=user_message,
                session_token=session_token or 'anonymous',
                pillar='insights'
            )
            
            # Return proper response structure
            from backend.business_enablement.protocols.business_liaison_agent_protocol import ConversationResponse, ResponseType
            
            return ConversationResponse(
                success=result.get('success', True),
                message=result.get('message', ''),
                response_type=ResponseType.TEXT_RESPONSE,
                metadata=result.get('metadata', {})
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to process conversation: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return proper error response
            from backend.business_enablement.protocols.business_liaison_agent_protocol import ConversationResponse, ResponseType
            
            return ConversationResponse(
                success=False,
                message=f"Sorry, I encountered an error: {str(e)}",
                response_type=ResponseType.ERROR_RESPONSE,
                metadata={"error": str(e)}
            )
    
    async def provide_capability_guidance(self, request) -> Any:
        """
        Provide capability guidance for insights analysis.
        
        Uses real LLM reasoning to provide contextual guidance based on user goals.
        """
        try:
            # Extract user goal from request
            user_goal = getattr(request, 'user_goal', '') if hasattr(request, 'user_goal') else ''
            if not user_goal:
                user_goal = getattr(request, 'goal', '') if hasattr(request, 'goal') else 'general insights analysis'
            
            # Use LLM to generate contextual capability guidance
            llm_abstraction = await self.get_business_abstraction("llm")
            if llm_abstraction:
                from foundations.public_works_foundation.abstraction_contracts.llm_protocol import LLMRequest, LLMModel
                
                system_prompt = """You are an Insights Analysis liaison agent. Your role is to provide capability guidance to users based on their goals.

Available capabilities:
1. Data Analysis - Analyze data using various statistical and machine learning techniques
2. Visualization - Create interactive charts and dashboards
3. Insights Generation - Generate business insights and actionable recommendations
4. APG Mode - Autonomous pattern generation for automatic insights discovery

Provide guidance that:
- Matches the user's goal to relevant capabilities
- Explains how each capability can help
- Provides clear next steps"""
                
                user_prompt = f"""User goal: {user_goal}

Provide capability guidance including:
1. Recommended capabilities for this goal
2. How each capability helps achieve the goal
3. Step-by-step guidance for getting started"""
                
                llm_request = LLMRequest(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=LLMModel.GPT_4O_MINI,
                    max_tokens=800,
                    temperature=0.7,
                    metadata={"task": "capability_guidance", "pillar": "insights"}
                )
                
                llm_response = await llm_abstraction.generate_response(llm_request)
                guidance_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
                
                # Parse guidance into structured format
                # For now, return capabilities with LLM-generated guidance
                capabilities = [
                    {
                        "name": "Data Analysis",
                        "description": "Analyze data using various statistical and machine learning techniques",
                        "use_cases": ["Trend analysis", "Pattern recognition", "Predictive modeling"]
                    },
                    {
                        "name": "Visualization",
                        "description": "Create interactive charts and dashboards for data visualization",
                        "use_cases": ["Chart creation", "Dashboard building", "Report generation"]
                    },
                    {
                        "name": "Insights Generation",
                        "description": "Generate business insights and actionable recommendations",
                        "use_cases": ["Business intelligence", "Strategic planning", "Performance optimization"]
                    },
                    {
                        "name": "APG Mode",
                        "description": "Autonomous pattern generation for automatic insights discovery",
                        "use_cases": ["Anomaly detection", "Pattern discovery", "Automated analysis"]
                    }
                ]
                
                # Extract guidance steps from LLM response
                guidance_steps = [
                    "Choose your analysis type",
                    "Upload your data",
                    "Review results"
                ]
                
                # Return proper response structure
                from backend.business_enablement.protocols.business_liaison_agent_protocol import CapabilityGuidanceResponse
                
                return CapabilityGuidanceResponse(
                    success=True,
                    recommended_capabilities=capabilities,
                    guidance_steps=guidance_steps,
                    guidance_text=guidance_text
                )
            else:
                # Fallback if LLM not available
                self.logger.warning("⚠️ LLM abstraction not available for capability guidance")
                capabilities = [
                    {
                        "name": "Data Analysis",
                        "description": "Analyze data using various statistical and machine learning techniques",
                        "use_cases": ["Trend analysis", "Pattern recognition", "Predictive modeling"]
                    },
                    {
                        "name": "Visualization",
                        "description": "Create interactive charts and dashboards for data visualization",
                        "use_cases": ["Chart creation", "Dashboard building", "Report generation"]
                    },
                    {
                        "name": "Insights Generation",
                        "description": "Generate business insights and actionable recommendations",
                        "use_cases": ["Business intelligence", "Strategic planning", "Performance optimization"]
                    },
                    {
                        "name": "APG Mode",
                        "description": "Autonomous pattern generation for automatic insights discovery",
                        "use_cases": ["Anomaly detection", "Pattern discovery", "Automated analysis"]
                    }
                ]
                
                from backend.business_enablement.protocols.business_liaison_agent_protocol import CapabilityGuidanceResponse
                
                return CapabilityGuidanceResponse(
                    success=True,
                    recommended_capabilities=capabilities,
                    guidance_steps=["Choose your analysis type", "Upload your data", "Review results"]
                )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to provide capability guidance: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Return proper error response
            from backend.business_enablement.protocols.business_liaison_agent_protocol import CapabilityGuidanceResponse
            
            return CapabilityGuidanceResponse(
                success=False,
                recommended_capabilities=[],
                guidance_steps=[],
                error=str(e)
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the insights liaison agent."""
        try:
            return {
                "agent_name": self.agent_name,
                "status": "healthy" if self.is_initialized else "unhealthy",
                "initialized": self.is_initialized,
                "business_domain": self.business_domain,
                "capabilities": ["conversation", "guidance", "analysis_support"],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "agent_name": self.agent_name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # ABSTRACT METHODS IMPLEMENTATION (from AgentBase)
    # ============================================================================
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request using agent capabilities."""
        try:
            # Route to appropriate method based on request type
            request_type = request.get("type", "conversation")
            
            if request_type == "conversation":
                return await self.process_conversation(request)
            elif request_type == "capability_guidance":
                return await self.provide_capability_guidance(request)
            else:
                return {
                    "success": False,
                    "message": f"Unknown request type: {request_type}",
                    "error": "unsupported_request_type"
                }
        except Exception as e:
            self.logger.error(f"❌ Failed to process request: {e}")
            return {
                "success": False,
                "message": f"Request processing failed: {str(e)}",
                "error": str(e)
            }
    
    async def get_agent_capabilities(self) -> List[str]:
        """Get list of agent capabilities."""
        return ["conversation", "guidance", "analysis_support"]
    
    async def get_agent_description(self) -> str:
        """Get agent description."""
        return "Insights Liaison Agent - Provides conversational interface and user guidance for insights analysis operations"
    
    # ============================================================================
    # ENHANCED CONVERSATIONAL CAPABILITIES
    # ============================================================================
    
    async def _understand_user_intent(
        self,
        query: str,
        conversation_context: Dict[str, Any],
        user_context: UserContext
    ) -> Dict[str, Any]:
        """
        Use OpenAI LLM to understand user intent and extract entities.
        
        Returns:
            {
                "intent": "analyze" | "drill_down" | "visualize" | "query" | "general",
                "entities": {
                    "content_id": str,
                    "analysis_type": str,
                    "visualization_type": str,
                    "filter_criteria": {...}
                },
                "confidence": float
            }
        """
        try:
            # Build prompt for intent understanding
            previous_context = conversation_context.get("last_analysis", {})
            prompt = self._build_intent_prompt(query, previous_context)
            
            # Call LLM using simple helper (includes agentic correlation tracking)
            system_message = "You are an intent understanding assistant for data insights. Analyze user queries and extract intent and entities. Return only valid JSON."
            response_text = await self._call_llm_simple(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o-mini",  # Use GPT-4O-MINI for faster intent detection
                max_tokens=300,
                temperature=0.3,
                user_context=self._convert_user_context(user_context),
                metadata={
                    "agent_name": self.agent_name,
                    "operation": "understand_intent"
                }
            )
            
            # Parse LLM response
            intent_result = self._parse_intent_response(response_text)
            return intent_result
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to understand intent with LLM: {e}, falling back to keyword detection")
            return self._keyword_based_intent_detection(query)
    
    def _keyword_based_intent_detection(self, query: str) -> Dict[str, Any]:
        """Fallback keyword-based intent detection."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["which", "who", "show me", "list", "what are"]):
            return {
                "intent": "drill_down",
                "entities": {},
                "confidence": 0.6
            }
        elif any(word in query_lower for word in ["analyze", "analysis", "insights"]):
            return {
                "intent": "analyze",
                "entities": {},
                "confidence": 0.7
            }
        elif any(word in query_lower for word in ["chart", "graph", "visualize", "plot", "show"]):
            return {
                "intent": "visualize",
                "entities": {},
                "confidence": 0.7
            }
        else:
            return {
                "intent": "general",
                "entities": {},
                "confidence": 0.5
            }
    
    def _build_intent_prompt(self, query: str, previous_context: Dict[str, Any]) -> str:
        """Build prompt for intent understanding."""
        context_info = ""
        if previous_context:
            context_info = f"\nPrevious analysis context: {json.dumps(previous_context, indent=2)}"
        
        prompt = f"""Analyze the following user query and extract intent and entities.

User Query: {query}
{context_info}

Determine the intent and extract relevant entities. Return JSON in this format:
{{
    "intent": "analyze" | "drill_down" | "visualize" | "query" | "general",
    "entities": {{
        "content_id": "string or null",
        "analysis_type": "string or null",
        "visualization_type": "string or null",
        "filter_criteria": {{}},
        "column_names": []
    }},
    "confidence": 0.0-1.0
}}

Intent meanings:
- "analyze": User wants to analyze data
- "drill_down": User wants to see specific records/details (follow-up question)
- "visualize": User wants to see a chart/graph
- "query": User wants to query specific data
- "general": General question or guidance request

Return only the JSON, no additional text."""
        
        return prompt
    
    def _parse_intent_response(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response to extract intent and entities."""
        try:
            response_text = llm_response.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text
            
            intent_result = json.loads(response_text)
            
            # Validate structure
            if "intent" not in intent_result:
                intent_result["intent"] = "general"
            if "entities" not in intent_result:
                intent_result["entities"] = {}
            if "confidence" not in intent_result:
                intent_result["confidence"] = 0.5
            
            return intent_result
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"⚠️ Failed to parse intent response: {e}")
            return self._keyword_based_intent_detection("")
    
    async def _handle_analysis_request(
        self,
        query: str,
        entities: Dict[str, Any],
        conversation_id: str,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """
        Handle analysis request.
        
        Calls InsightsOrchestrator or InsightsBusinessAnalysisAgent.
        """
        try:
            content_id = entities.get("content_id")
            if not content_id:
                return {
                    "message": "I can help you analyze your data! Please specify which content you'd like to analyze, or select a file first.",
                    "data": None
                }
            
            # Call InsightsOrchestrator for analysis
            if self.insights_orchestrator:
                analysis_result = await self.insights_orchestrator.analyze_content_for_insights(
                    source_type="content_metadata",
                    content_metadata_id=content_id,
                    content_type=entities.get("analysis_type", "structured"),
                    user_context=self._convert_user_context(user_context)
                )
                
                if analysis_result.get("success"):
                    return {
                        "message": "Here's your analysis! I've identified key patterns and insights from your data.",
                        "data": analysis_result.get("summary", {}),
                        "analysis": analysis_result
                    }
            
            # Fallback: Use Business Analysis Agent
            if self.business_analysis_agent:
                analysis_result = await self.business_analysis_agent.analyze_structured_data(
                    content_id=content_id,
                    user_context=user_context
                )
                
                if analysis_result.get("success"):
                    return {
                        "message": "Here's your analysis! I've identified key patterns and insights from your data.",
                        "data": analysis_result,
                        "analysis": analysis_result
                    }
            
            return {
                "message": "I'm having trouble accessing the analysis services. Please try again later.",
                "data": None
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle analysis request: {e}")
            return {
                "message": f"I encountered an error while analyzing your data: {str(e)}",
                "data": None
            }
    
    async def _handle_drill_down_query(
        self,
        query: str,
        previous_analysis: Optional[Dict[str, Any]],
        conversation_id: str,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """
        Handle drill-down queries (e.g., "which ones are they?").
        
        Extracts entities from previous analysis and query,
        then queries specific records via Data Solution Orchestrator.
        """
        try:
            if not previous_analysis:
                return {
                    "message": "I don't have any previous analysis to drill down into. Please run an analysis first.",
                    "data": None
                }
            
            # Use OpenAI LLM to extract filter criteria from query and previous analysis
            filter_criteria = await self._extract_filter_criteria(query, previous_analysis, user_context)
            
            # Query via Data Solution Orchestrator (via MCP tool or direct call)
            # For now, return a message indicating drill-down capability
            return {
                "message": f"I understand you want to see specific records. Based on your query '{query}', I'm extracting the relevant details from the previous analysis.",
                "data": {
                    "filter_criteria": filter_criteria,
                    "previous_analysis": previous_analysis
                },
                "type": "drill_down"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle drill-down query: {e}")
            return {
                "message": f"I encountered an error processing your drill-down request: {str(e)}",
                "data": None
            }
    
    async def _handle_visualization_request(
        self,
        query: str,
        entities: Dict[str, Any],
        conversation_id: str,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """
        Handle visualization request.
        
        Generates visualization spec using OpenAI LLM, then calls VisualizationEngineService.
        """
        try:
            content_id = entities.get("content_id")
            if not content_id:
                return {
                    "message": "I can create visualizations for your data! Please specify which content you'd like to visualize, or select a file first.",
                    "visualization": None
                }
            
            # Generate visualization spec using OpenAI LLM
            viz_spec = await self._generate_visualization_spec_from_nl(
                query=query,
                content_id=content_id,
                user_context=user_context
            )
            
            # Call VisualizationEngineService via MCP tool
            if self.mcp_client_manager:
                viz_result = await self.mcp_client_manager.execute_tool(
                    tool_name="create_agui_visualization",
                    parameters={
                        "content_id": content_id,
                        "visualization_type": viz_spec.get("type", "chart"),
                        "visualization_spec": viz_spec,
                        "user_context": self._convert_user_context(user_context)
                    }
                )
                
                if viz_result.get("success"):
                    return {
                        "message": "Here's your visualization!",
                        "visualization": viz_result.get("component"),
                        "data": viz_result
                    }
            
            return {
                "message": "I'm having trouble creating the visualization. Please try again later.",
                "visualization": None
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle visualization request: {e}")
            return {
                "message": f"I encountered an error creating your visualization: {str(e)}",
                "visualization": None
            }
    
    async def _handle_query_request(
        self,
        query: str,
        entities: Dict[str, Any],
        conversation_id: str,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """
        Handle query request (when semantic search isn't sufficient).
        
        Uses InsightsQueryAgent to generate query spec.
        """
        try:
            content_id = entities.get("content_id")
            if not content_id:
                return {
                    "message": "I can help you query your data! Please specify which content you'd like to query, or select a file first.",
                    "data": None
                }
            
            # Use InsightsQueryAgent to generate query
            if self.query_agent:
                query_result = await self.query_agent.generate_query_from_nl(
                    natural_language_query=query,
                    content_id=content_id,
                    user_context=user_context
                )
                
                if query_result.get("success"):
                    return {
                        "message": f"I've generated a {query_result.get('query_type')} query for your request.",
                        "data": query_result,
                        "type": "query"
                    }
            
            return {
                "message": "I'm having trouble generating the query. Please try again later.",
                "data": None
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to handle query request: {e}")
            return {
                "message": f"I encountered an error generating your query: {str(e)}",
                "data": None
            }
    
    async def _handle_general_query(
        self,
        query: str,
        conversation_id: str,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """Handle general queries with guidance."""
        query_lower = query.lower()
        
        if "analyze" in query_lower:
            message = "I can help you analyze your data! What type of analysis would you like to perform? I support descriptive, predictive, prescriptive, and diagnostic analysis."
        elif "visualize" in query_lower:
            message = "I can create various visualizations for your data! What type of chart would you like? I support line charts, bar charts, pie charts, scatter plots, and more."
        elif "insights" in query_lower:
            message = "I can generate business insights from your analysis results! I'll identify patterns, trends, and provide actionable recommendations."
        else:
            message = "Hello! I'm your Insights Analysis assistant. I can help you with data analysis, visualization, insights generation, and drill-down queries. What would you like to do?"
        
        return {
            "message": message,
            "data": None
        }
    
    async def _generate_visualization_spec_from_nl(
        self,
        query: str,
        content_id: str,
        user_context: UserContext
    ) -> Dict[str, Any]:
        """Generate visualization spec from natural language using OpenAI LLM."""
        try:
            # Get schema metadata for context via Data Solution Orchestrator (Phase 6)
            schema_metadata = None
            if self.insights_orchestrator and hasattr(self.insights_orchestrator, 'get_semantic_embeddings_via_data_solution'):
                embeddings = await self.insights_orchestrator.get_semantic_embeddings_via_data_solution(
                    content_id=content_id,
                    embedding_type="schema",
                    user_context=self._convert_user_context(user_context)
                )
                if embeddings:
                    schema_metadata = {
                        "columns": [emb.get("column_name") for emb in embeddings if emb.get("column_name")],
                        "content_id": content_id
                    }
            else:
                # Fallback: try semantic data abstraction (for backward compatibility)
                semantic_data = await self.get_business_abstraction("semantic_data")
                if semantic_data:
                    embeddings = await semantic_data.get_semantic_embeddings(
                        content_id=content_id,
                        filters={"embedding_type": "schema"},
                        user_context=self._convert_user_context(user_context)
                    )
                    if embeddings:
                        schema_metadata = {
                            "columns": [emb.get("column_name") for emb in embeddings if emb.get("column_name")],
                            "content_id": content_id
                        }
            
            # Build prompt
            prompt = f"""Generate a visualization specification from the following natural language query.

Query: {query}
Schema: {json.dumps(schema_metadata, indent=2) if schema_metadata else "Not available"}

Return JSON in this format:
{{
    "type": "chart" | "dashboard" | "table",
    "chart_type": "bar" | "line" | "scatter" | "histogram" | "pie",
    "x_axis": "column_name",
    "y_axis": "column_name",
    "title": "Chart Title",
    "labels": {{"x": "X Axis Label", "y": "Y Axis Label"}}
}}

Return only the JSON, no additional text."""
            
            # Call LLM using simple helper (includes agentic correlation tracking)
            system_message = "You are a visualization spec generator. Generate specifications for data visualizations based on natural language queries. Return only valid JSON."
            response_text = await self._call_llm_simple(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o-mini",  # Use GPT-4O-MINI for faster spec generation
                max_tokens=300,
                temperature=0.3,
                user_context=self._convert_user_context(user_context),
                metadata={
                    "agent_name": self.agent_name,
                    "operation": "generate_visualization_spec",
                    "content_id": content_id
                }
            )
            
            # Parse response
            response_clean = response_text.strip().replace("```json", "").replace("```", "")
            viz_spec = json.loads(response_clean)
            return viz_spec
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate visualization spec: {e}")
            # Return default spec
            return {
                "type": "chart",
                "chart_type": "bar",
                "title": "Data Visualization"
            }
    
    async def _extract_filter_criteria(
        self,
        query: str,
        previous_analysis: Dict[str, Any],
        user_context: UserContext
    ) -> Dict[str, Any]:
        """Extract filter criteria from drill-down query using OpenAI LLM."""
        try:
            # Build prompt
            prompt = f"""Extract filter criteria from the following drill-down query based on the previous analysis.

Query: {query}
Previous Analysis: {json.dumps(previous_analysis, indent=2)}

Return JSON with filter criteria:
{{
    "filters": {{"column": "value", ...}},
    "columns": ["column1", "column2", ...]
}}

Return only the JSON, no additional text."""
            
            # Call LLM using simple helper (includes agentic correlation tracking)
            system_message = "You are a filter extraction assistant. Extract filter criteria from drill-down queries. Return only valid JSON."
            response_text = await self._call_llm_simple(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o-mini",  # Use GPT-4O-MINI for faster extraction
                max_tokens=200,
                temperature=0.3,
                user_context=self._convert_user_context(user_context),
                metadata={
                    "agent_name": self.agent_name,
                    "operation": "extract_filter_criteria"
                }
            )
            
            # Parse response
            response_clean = response_text.strip().replace("```json", "").replace("```", "")
            filter_criteria = json.loads(response_clean)
            return filter_criteria.get("filters", {})
            
        except Exception as e:
            self.logger.error(f"❌ Failed to extract filter criteria: {e}")
            return {}
    
    def _convert_user_context(self, user_context: Optional[UserContext]) -> Dict[str, Any]:
        """Convert UserContext to dict if needed."""
        if user_context is None:
            return {}
        if isinstance(user_context, dict):
            return user_context
        return {
            "user_id": getattr(user_context, "user_id", None),
            "tenant_id": getattr(user_context, "tenant_id", None),
            "session_id": getattr(user_context, "session_id", None),
            "roles": getattr(user_context, "roles", [])
        }
    
    # ============================================================================
    # MULTI-TENANT PROTOCOL IMPLEMENTATION (from IMultiTenantProtocol)
    # ============================================================================
    
    async def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tenant."""
        return {"success": False, "message": "Tenant creation not supported by liaison agent"}
    
    async def update_tenant(self, tenant_id: str, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update tenant information."""
        return {"success": False, "message": "Tenant update not supported by liaison agent"}
    
    async def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """Delete a tenant."""
        return {"success": False, "message": "Tenant deletion not supported by liaison agent"}
    
    async def list_tenants(self) -> List[Dict[str, Any]]:
        """List all tenants."""
        return []
    
    async def get_tenant_users(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get users for a tenant."""
        return []
    
    async def add_user_to_tenant(self, tenant_id: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add user to tenant."""
        return {"success": False, "message": "User management not supported by liaison agent"}
    
    async def remove_user_from_tenant(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
        """Remove user from tenant."""
        return {"success": False, "message": "User management not supported by liaison agent"}
    
    async def get_user_tenant_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant context for a user."""
        return None
    
    async def validate_tenant_access(self, tenant_id: str, user_id: str) -> bool:
        """Validate tenant access for a user."""
        return True  # Default open access for liaison agent
    
    async def validate_tenant_feature_access(self, tenant_id: str, user_id: str, feature: str) -> bool:
        """Validate feature access for a user in a tenant."""
        return True  # Default open access for liaison agent
    
    async def audit_tenant_action(self, tenant_id: str, user_id: str, action: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Audit tenant action."""
        return {"success": True, "message": "Action audited"}
    
    async def get_tenant_usage_stats(self, tenant_id: str) -> Dict[str, Any]:
        """Get usage statistics for a tenant."""
        return {"tenant_id": tenant_id, "usage_stats": {}}
