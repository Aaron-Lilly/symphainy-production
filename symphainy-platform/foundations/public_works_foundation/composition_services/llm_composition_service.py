#!/usr/bin/env python3
"""
LLM Composition Service

Composition service for LLM capabilities.
Orchestrates LLM abstractions for agentic capabilities.

WHAT (Composition Role): I orchestrate LLM capabilities for agentic workflows
HOW (Composition Implementation): I provide business logic for agent interpretation and guidance
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

from ..infrastructure_abstractions.llm_abstraction import LLMAbstraction
from ..abstraction_contracts.llm_protocol import LLMRequest, LLMResponse, LLMModel


class LLMCompositionService:
    """Composition service for LLM capabilities."""
    
    def __init__(self, llm_abstraction: LLMAbstraction, di_container=None):
        """
        Initialize LLM composition service.
        
        Args:
            llm_abstraction: LLM abstraction instance
            di_container: DI Container for utilities
        """
        self.llm_abstraction = llm_abstraction
        self.di_container = di_container
        self.service_name = "llm_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("LLMCompositionService")
        
        # Service status
        self.is_initialized = False
        
        # Initialize service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the composition service."""
        try:
            self.logger.info("✅ LLM composition service initialized")
            self.is_initialized = True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM composition service: {e}")
            self.is_initialized = False
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    
    # ============================================================================
    # AGENTIC LLM CAPABILITIES
    # ============================================================================
    
    async def interpret_results(self, results: Dict[str, Any], context: str, 
                              expertise: str = None, format: str = "agui",
                              user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Interpret analysis results using LLM with optional expertise.
        
        Args:
            results: Analysis results from MCP tools
            context: Context for interpretation (e.g., "insights analysis")
            expertise: Optional expertise domain (e.g., "call center volumetric analysis")
            format: Output format ("agui", "json", "text")
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Interpreted insights
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm", "interpret"
                )
                if validation_error:
                    return validation_error
            
            # Build system prompt
            system_prompt = f"You are an expert in {context} and excel at using analysis tools to provide compelling insights."
            
            if expertise:
                system_prompt += f" You have specialized expertise in {expertise}."
            
            # Build user prompt
            user_prompt = f"""
            Analysis Results: {json.dumps(results, indent=2)}
            
            Provide:
            1. Key insights in {format} format
            2. Business implications
            3. Recommendations
            4. Next steps
            """
            
            # Create LLM request
            request = LLMRequest(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=LLMModel.GPT_4O_MINI,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Generate response
            response = await self.llm_abstraction.generate_response(request)
            
            # Format response based on requested format
            formatted_response = self._format_response(response.content, format)
            
            self.logger.info(f"✅ Results interpreted for context: {context}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("interpret_results", {
                    "context": context,
                    "format": format,
                    "success": True
                })
            
            return formatted_response
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "interpret_results",
                    "context": context,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to interpret results: {e}")
            return {
                "error": str(e),
                "error_code": "LLM_INTERPRET_ERROR",
                "format": format,
                "timestamp": datetime.now().isoformat()
            }
    
    async def guide_user(self, user_input: str, available_tools: List[str], 
                        context: str, expertise: str = None,
                        user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Guide user through available tools with optional expertise.
        
        Args:
            user_input: User's input/question
            available_tools: List of available MCP tools
            context: Context for guidance (e.g., "insights pillar")
            expertise: Optional expertise domain
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Guidance and recommendations
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm", "guide"
                )
                if validation_error:
                    return validation_error
            
            # Build system prompt
            system_prompt = f"You are an expert guide in {context}. Available tools: {', '.join(available_tools)}"
            
            if expertise:
                system_prompt += f" You have specialized expertise in {expertise}."
            
            # Build user prompt
            user_prompt = f"""
            User Input: {user_input}
            
            Provide:
            1. Recommended next steps
            2. Which tools to use
            3. Expected outcomes
            4. Potential challenges
            """
            
            # Create LLM request
            request = LLMRequest(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=LLMModel.GPT_4O_MINI,
                max_tokens=1500,
                temperature=0.7
            )
            
            # Generate response
            response = await self.llm_abstraction.generate_response(request)
            
            # Format as AGUI response
            formatted_response = self._format_response(response.content, "agui")
            
            self.logger.info(f"✅ User guidance provided for context: {context}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("guide_user", {
                    "context": context,
                    "tools_count": len(available_tools),
                    "success": True
                })
            
            return formatted_response
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "guide_user",
                    "context": context,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to guide user: {e}")
            return {
                "error": str(e),
                "error_code": "LLM_GUIDE_USER_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_agent_response(self, prompt: str, context: Dict[str, Any] = None, 
                                    model: LLMModel = LLMModel.GPT_4O_MINI,
                                    user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate agent response with context.
        
        Args:
            prompt: Agent prompt
            context: Agent context
            model: LLM model
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Agent response
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm", "generate"
                )
                if validation_error:
                    return validation_error
            
            # Build messages with context
            messages = []
            
            # Add system context if provided
            if context and context.get("system_prompt"):
                messages.append({
                    "role": "system",
                    "content": context["system_prompt"]
                })
            
            # Add conversation history if provided
            if context and context.get("conversation_history"):
                for msg in context["conversation_history"]:
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Add current prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Create LLM request
            request = LLMRequest(
                messages=messages,
                model=model,
                max_tokens=context.get("max_tokens", 2000) if context else 2000,
                temperature=context.get("temperature", 0.7) if context else 0.7
            )
            
            # Generate response
            response = await self.llm_abstraction.generate_response(request)
            
            # Format agent response
            agent_response = {
                "content": response.content,
                "model": response.model.value,
                "usage": response.usage,
                "finish_reason": response.finish_reason,
                "response_id": response.response_id,
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Agent response generated using {model.value}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("generate_agent_response", {
                    "model": model.value,
                    "success": True
                })
            
            return agent_response
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "generate_agent_response",
                    "model": model.value,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to generate agent response: {e}")
            return {
                "content": "",
                "error": str(e),
                "error_code": "LLM_AGENT_RESPONSE_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    async def generate_agent_embeddings(self, text: str, model: str = "text-embedding-ada-002",
                                      user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate embeddings for agent text processing.
        
        Args:
            text: Input text
            model: Embedding model
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Embeddings result
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm", "embed"
                )
                if validation_error:
                    return validation_error
            
            # Generate embeddings
            embeddings = await self.llm_abstraction.generate_embeddings(text, model)
            
            # Format embeddings result
            embeddings_result = {
                "embeddings": embeddings,
                "model": model,
                "text_length": len(text),
                "embedding_dimension": len(embeddings),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Embeddings generated for text (length: {len(text)})")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("generate_agent_embeddings", {
                    "model": model,
                    "text_length": len(text),
                    "success": True
                })
            
            return embeddings_result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "generate_agent_embeddings",
                    "model": model,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to generate embeddings: {e}")
            return {
                "embeddings": [],
                "error": str(e),
                "error_code": "LLM_EMBEDDINGS_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_agent_capabilities(self, agent_description: str, 
                                       capabilities: List[str],
                                       user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze agent capabilities using LLM.
        
        Args:
            agent_description: Agent description
            capabilities: List of capabilities
            user_context: User context with user_id, tenant_id, security_context
            
        Returns:
            Dict: Analysis result
        """
        try:
            # Validate security and tenant access if user_context provided
            if user_context:
                validation_error = await self._validate_security_and_tenant(
                    user_context, "llm", "analyze"
                )
                if validation_error:
                    return validation_error
            
            # Build analysis prompt
            prompt = f"""
            Analyze the following agent capabilities:
            
            Agent Description: {agent_description}
            
            Capabilities: {', '.join(capabilities)}
            
            Please provide:
            1. Capability assessment
            2. Potential improvements
            3. Missing capabilities
            4. Overall rating (1-10)
            """
            
            # Generate analysis
            response = await self.generate_agent_response(
                prompt=prompt,
                context={
                    "system_prompt": "You are an expert in AI agent capability analysis. Provide detailed, actionable insights.",
                    "max_tokens": 1000,
                    "temperature": 0.3
                },
                user_context=user_context
            )
            
            # Format analysis result
            analysis_result = {
                "agent_description": agent_description,
                "capabilities": capabilities,
                "analysis": response["content"],
                "model": response["model"],
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"✅ Agent capabilities analyzed for {len(capabilities)} capabilities")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("analyze_agent_capabilities", {
                    "capabilities_count": len(capabilities),
                    "success": True
                })
            
            return analysis_result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "analyze_agent_capabilities",
                    "capability_count": len(capabilities),
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to analyze agent capabilities: {e}")
            return {
                "error": str(e),
                "error_code": "LLM_CAPABILITY_ANALYSIS_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    def _format_response(self, response: str, format: str) -> Dict[str, Any]:
        """Format LLM response based on requested format."""
        if format == "agui":
            return self._format_agui_response(response)
        elif format == "json":
            return self._format_json_response(response)
        else:
            return {"text": response, "format": "text"}
    
    def _format_agui_response(self, response: str) -> Dict[str, Any]:
        """Format response for AGUI consumption."""
        return {
            "type": "llm_interpretation",
            "content": response,
            "timestamp": datetime.now().isoformat(),
            "format": "agui"
        }
    
    def _format_json_response(self, response: str) -> Dict[str, Any]:
        """Format response as JSON."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"text": response, "format": "text"}
    
    # ============================================================================
    # SERVICE MANAGEMENT
    # ============================================================================
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        Get composition service status.
        
        Returns:
            Dict: Service status
        """
        try:
            # Get LLM abstraction status
            llm_health = await self.llm_abstraction.health_check()
            
            result = {
                "service": "LLMCompositionService",
                "initialized": self.is_initialized,
                "llm_abstraction": llm_health,
                "timestamp": datetime.now().isoformat()
            }
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_service_status", {
                    "success": True
                })
            
            return result
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_service_status",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Failed to get service status: {e}")
            return {
                "service": "LLMCompositionService",
                "initialized": self.is_initialized,
                "error": str(e),
                "error_code": "LLM_SERVICE_STATUS_ERROR",
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all components.
        
        Returns:
            Dict: Health check result
        """
        try:
            health_status = {
                "healthy": True,
                "components": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Check LLM abstraction
            try:
                llm_health = await self.llm_abstraction.health_check()
                health_status["components"]["llm_abstraction"] = llm_health
                
                if not llm_health.get("healthy", False):
                    health_status["healthy"] = False
                    
            except Exception as e:
                health_status["components"]["llm_abstraction"] = {
                    "healthy": False,
                    "error": str(e)
                }
                health_status["healthy"] = False
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("health_check", {
                    "healthy": health_status.get("healthy", False),
                    "success": True
                })
            
            return health_status
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "health_check",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "error_code": "LLM_HEALTH_CHECK_ERROR",
                "timestamp": datetime.now().isoformat()
            }