"""
Policy Integration - City Manager + Security Guard Hooks (Refactored with Pure DI)

Provides policy-aware execution with City Manager governance and Security Guard authorization.
Ensures all agent actions comply with platform policies and security requirements.

WHAT (Agentic Role): I provide policy compliance and security authorization for agent actions
HOW (Policy Integration): I use pure dependency injection and integrate with City Manager and Security Guard
"""

import sys
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

# Import DIContainerService DI container
from foundations.di_container.di_container_service import DIContainerService
from utilities import UserContext


class PolicyIntegration:
    """
    Integrates with City Manager and Security Guard for policy-aware execution.
    
    Refactored to use pure dependency injection through DIContainerService.
    
    Provides:
    - Policy compliance checking via City Manager
    - Security authorization via Security Guard
    - Audit trail and governance metadata
    - Resource allocation and usage tracking
    """
    
    def __init__(self, foundation_services: DIContainerService, agentic_foundation: 'AgenticFoundationService' = None):
        """Initialize policy integration with pure dependency injection."""
        self.foundation_services = foundation_services
        self.agentic_foundation = agentic_foundation
        
        # Get utilities from foundation services DI container
        self.logger = foundation_services.get_logger("policy_integration")
        self.config = foundation_services.get_config()
        self.health = foundation_services.get_health()
        self.telemetry = foundation_services.get_telemetry()
        self.security = foundation_services.get_security()
        
        # Policy cache
        self.policy_cache = {}
        self.security_cache = {}
        
        # Audit trail
        self.audit_trail = []
        
        self.logger.info("Policy Integration initialized")
    
    async def initialize(self, agent_id: str, required_roles: List[str], tenant_context: Dict[str, Any] = None):
        """
        Initialize policy integration for specific agent with multi-tenancy support.
        
        Args:
            agent_id: Unique agent identifier
            required_roles: List of required Smart City roles
            tenant_context: Tenant context for multi-tenant operations
        """
        try:
            self.agent_id = agent_id
            self.required_roles = required_roles
            self.tenant_context = tenant_context
            
            # Load agent-specific policies with tenant context
            await self._load_agent_policies()
            
            self.logger.info(f"Policy integration initialized for agent {agent_id} with tenant context")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize policy integration: {e}")
            # Use telemetry utility for error reporting
            await self.telemetry.log_anomaly({
                "anomaly_type": "policy_integration_initialization_failed",
                "agent_id": agent_id,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            })
            raise
    
    async def _load_agent_policies(self):
        """Load policies specific to the agent and its required roles."""
        try:
            # Simulate policy loading
            # In real implementation, this would query City Manager for policies
            self.policy_cache = {
                "data_access": {
                    "allowed_roles": ["librarian", "data_steward"],
                    "restrictions": ["no_pii_access", "audit_required"]
                },
                "analysis_execution": {
                    "allowed_roles": ["conductor", "nurse"],
                    "restrictions": ["resource_limits", "timeout_limits"]
                },
                "output_generation": {
                    "allowed_roles": ["post_office"],
                    "restrictions": ["format_compliance", "content_filtering"]
                }
            }
            
            self.logger.info("Agent policies loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load agent policies: {e}")
            raise
    
    async def check_policies(self, agent_id: str, tools: List[str], context: Dict[str, Any], 
                           user_context: UserContext = None, tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check policy compliance for tool execution with multi-tenant awareness.
        
        Args:
            agent_id: Agent identifier
            tools: List of tools to execute
            context: Execution context
            user_context: User context for security and audit
            tenant_context: Tenant context for multi-tenant operations
            
        Returns:
            Dict containing policy check results
        """
        try:
            policy_result = {
                "approved": True,
                "agent_id": agent_id,
                "tools": tools,
                "timestamp": datetime.now().isoformat(),
                "violations": [],
                "warnings": [],
                "recommendations": []
            }
            
            # Check data access policies
            if any("data" in tool.lower() for tool in tools):
                data_policy_result = await self._check_data_access_policy(tools, context, user_context)
                if not data_policy_result["approved"]:
                    policy_result["approved"] = False
                    policy_result["violations"].extend(data_policy_result["violations"])
            
            # Check analysis execution policies
            if any("analysis" in tool.lower() or "process" in tool.lower() for tool in tools):
                analysis_policy_result = await self._check_analysis_policy(tools, context, user_context)
                if not analysis_policy_result["approved"]:
                    policy_result["approved"] = False
                    policy_result["violations"].extend(analysis_policy_result["violations"])
            
            # Check output generation policies
            if any("output" in tool.lower() or "format" in tool.lower() for tool in tools):
                output_policy_result = await self._check_output_policy(tools, context, user_context)
                if not output_policy_result["approved"]:
                    policy_result["approved"] = False
                    policy_result["violations"].extend(output_policy_result["violations"])
            
            # Record audit trail
            await self._record_audit_trail("policy_check", policy_result, user_context)
            
            self.logger.info(f"Policy check completed for agent {agent_id}: {policy_result['approved']}")
            return policy_result
            
        except Exception as e:
            self.logger.error(f"Policy check failed: {e}")
            self.error_handler.handle_error(e, "policy_check_failed")
            return {
                "approved": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_data_access_policy(self, tools: List[str], context: Dict[str, Any], 
                                      user_context: UserContext = None) -> Dict[str, Any]:
        """Check data access policies."""
        try:
            result = {"approved": True, "violations": []}
            
            # Check if user has data access permissions
            if user_context and not self._has_data_access_permission(user_context):
                result["approved"] = False
                result["violations"].append("User lacks data access permissions")
            
            # Check for PII access restrictions
            if context.get("contains_pii", False):
                if not self._has_pii_access_permission(user_context):
                    result["approved"] = False
                    result["violations"].append("PII access not authorized")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Data access policy check failed: {e}")
            return {"approved": False, "violations": [f"Policy check error: {e}"]}
    
    async def _check_analysis_policy(self, tools: List[str], context: Dict[str, Any], 
                                   user_context: UserContext = None) -> Dict[str, Any]:
        """Check analysis execution policies."""
        try:
            result = {"approved": True, "violations": []}
            
            # Check resource limits
            estimated_resources = context.get("estimated_resources", {})
            if estimated_resources.get("cpu_usage", 0) > 0.8:
                result["approved"] = False
                result["violations"].append("CPU usage exceeds policy limits")
            
            if estimated_resources.get("memory_usage", 0) > 0.9:
                result["approved"] = False
                result["violations"].append("Memory usage exceeds policy limits")
            
            # Check timeout limits
            estimated_duration = context.get("estimated_duration", 0)
            if estimated_duration > 300:  # 5 minutes
                result["approved"] = False
                result["violations"].append("Execution duration exceeds policy limits")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis policy check failed: {e}")
            return {"approved": False, "violations": [f"Policy check error: {e}"]}
    
    async def _check_output_policy(self, tools: List[str], context: Dict[str, Any], 
                                 user_context: UserContext = None) -> Dict[str, Any]:
        """Check output generation policies."""
        try:
            result = {"approved": True, "violations": []}
            
            # Check output format compliance
            output_format = context.get("output_format", "json")
            if output_format not in ["json", "agui", "text"]:
                result["approved"] = False
                result["violations"].append(f"Output format '{output_format}' not compliant")
            
            # Check content filtering
            if context.get("contains_sensitive_data", False):
                if not self._has_sensitive_data_permission(user_context):
                    result["approved"] = False
                    result["violations"].append("Sensitive data output not authorized")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Output policy check failed: {e}")
            return {"approved": False, "violations": [f"Policy check error: {e}"]}
    
    def _has_data_access_permission(self, user_context: UserContext = None) -> bool:
        """Check if user has data access permissions."""
        if not user_context:
            return False
        
        # Simulate permission check
        # In real implementation, this would query Security Guard
        return user_context.user_id is not None
    
    def _has_pii_access_permission(self, user_context: UserContext = None) -> bool:
        """Check if user has PII access permissions."""
        if not user_context:
            return False
        
        # Simulate PII permission check
        # In real implementation, this would query Security Guard for specific permissions
        return user_context.email is not None  # Simplified check
    
    def _has_sensitive_data_permission(self, user_context: UserContext = None) -> bool:
        """Check if user has sensitive data output permissions."""
        if not user_context:
            return False
        
        # Simulate sensitive data permission check
        return user_context.full_name is not None  # Simplified check
    
    async def validate_security(self, agent_id: str, tools: List[str], 
                              user_context: UserContext = None, tenant_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate security authorization for tool execution with multi-tenant awareness.
        
        Args:
            agent_id: Agent identifier
            tools: List of tools to execute
            user_context: User context for security validation
            tenant_context: Tenant context for multi-tenant operations
            
        Returns:
            Dict containing security validation results
        """
        try:
            security_result = {
                "authorized": True,
                "agent_id": agent_id,
                "tools": tools,
                "timestamp": datetime.now().isoformat(),
                "violations": [],
                "permissions": []
            }
            
            # Validate user authentication
            if not user_context or not user_context.user_id:
                security_result["authorized"] = False
                security_result["violations"].append("User not authenticated")
                return security_result
            
            # Check tool-specific permissions
            for tool in tools:
                tool_permissions = await self._get_tool_permissions(tool, user_context)
                if not tool_permissions["authorized"]:
                    security_result["authorized"] = False
                    security_result["violations"].extend(tool_permissions["violations"])
                else:
                    security_result["permissions"].extend(tool_permissions["permissions"])
            
            # Record security audit
            await self._record_audit_trail("security_validation", security_result, user_context)
            
            self.logger.info(f"Security validation completed for agent {agent_id}: {security_result['authorized']}")
            return security_result
            
        except Exception as e:
            self.logger.error(f"Security validation failed: {e}")
            self.error_handler.handle_error(e, "security_validation_failed")
            return {
                "authorized": False,
                "error": str(e),
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_tool_permissions(self, tool: str, user_context: UserContext) -> Dict[str, Any]:
        """Get permissions for specific tool."""
        try:
            # Simulate permission check
            # In real implementation, this would query Security Guard
            permissions = {
                "authorized": True,
                "permissions": ["read", "execute"],
                "violations": []
            }
            
            # Check for restricted tools
            restricted_tools = ["admin_tools", "system_config", "user_management"]
            if any(restricted in tool.lower() for restricted in restricted_tools):
                permissions["authorized"] = False
                permissions["violations"].append(f"Tool '{tool}' requires admin privileges")
            
            return permissions
            
        except Exception as e:
            self.logger.error(f"Failed to get tool permissions: {e}")
            return {
                "authorized": False,
                "permissions": [],
                "violations": [f"Permission check error: {e}"]
            }
    
    async def _record_audit_trail(self, action: str, result: Dict[str, Any], user_context: UserContext = None):
        """Record action in audit trail."""
        try:
            audit_entry = {
                "action": action,
                "agent_id": getattr(self, 'agent_id', 'unknown'),
                "user_id": user_context.user_id if user_context else None,
                "timestamp": datetime.now().isoformat(),
                "result": result,
                "session_id": user_context.session_id if user_context else None
            }
            
            self.audit_trail.append(audit_entry)
            
            # Keep only last 1000 entries
            if len(self.audit_trail) > 1000:
                self.audit_trail = self.audit_trail[-1000:]
            
        except Exception as e:
            self.logger.error(f"Failed to record audit trail: {e}")
    
    async def cleanup(self):
        """Cleanup policy integration resources."""
        try:
            # Clear caches
            self.policy_cache.clear()
            self.security_cache.clear()
            
            # Save audit trail (in real implementation, this would persist to database)
            self.logger.info(f"Policy integration cleanup completed. Audit trail: {len(self.audit_trail)} entries")
            
        except Exception as e:
            self.logger.error(f"Policy integration cleanup failed: {e}")
            self.error_handler.handle_error(e, "policy_integration_cleanup_failed")
    
    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit trail entries."""
        return self.audit_trail[-limit:] if self.audit_trail else []
    
    async def health_check(self) -> Dict[str, Any]:
        """Check policy integration health."""
        try:
            return {
                "status": "healthy",
                "agent_id": getattr(self, 'agent_id', 'unknown'),
                "required_roles": getattr(self, 'required_roles', []),
                "policy_cache_size": len(self.policy_cache),
                "audit_trail_entries": len(self.audit_trail),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # ============================================================================
    # ENHANCED SECURITY CAPABILITIES FOR AGENTS
    # ============================================================================
    
    async def get_enhanced_security_policies(self) -> Dict[str, Any]:
        """Get enhanced security policies for agents."""
        try:
            if self.agentic_foundation:
                # Get agent security capabilities
                access_control = getattr(self.agentic_foundation, 'agent_access_control', {})
                policy_enforcement = getattr(self.agentic_foundation, 'agent_policy_enforcement', {})
                tenant_isolation = getattr(self.agentic_foundation, 'agent_tenant_isolation', {})
                
                return {
                    "access_control": {
                        "cross_realm_agents": access_control.get("cross_realm_agents", []),
                        "realm_specific_agents": access_control.get("realm_specific_agents", []),
                        "task_agents": access_control.get("task_agents", [])
                    },
                    "policy_enforcement": {
                        "agent_deployment_policy": policy_enforcement.get("agent_deployment_policy", ""),
                        "agent_resource_limits": policy_enforcement.get("agent_resource_limits", ""),
                        "agent_communication_policy": policy_enforcement.get("agent_communication_policy", "")
                    },
                    "tenant_isolation": {
                        "agent_context_isolation": tenant_isolation.get("agent_context_isolation", False),
                        "agent_data_isolation": tenant_isolation.get("agent_data_isolation", False),
                        "agent_capability_isolation": tenant_isolation.get("agent_capability_isolation", False)
                    }
                }
            return {}
        except Exception as e:
            self.logger.error(f"Failed to get enhanced security policies: {e}")
            return {}
    
    async def apply_enhanced_security_policies(self, agent_id: str, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply enhanced security policies for agent actions."""
        try:
            if self.agentic_foundation:
                # Get enhanced security policies
                security_policies = await self.get_enhanced_security_policies()
                
                # Apply access control
                access_control = security_policies.get("access_control", {})
                if agent_id in access_control.get("cross_realm_agents", []):
                    context["access_level"] = "cross_realm"
                elif agent_id in access_control.get("realm_specific_agents", []):
                    context["access_level"] = "realm_specific"
                elif agent_id in access_control.get("task_agents", []):
                    context["access_level"] = "task_specific"
                
                # Apply policy enforcement
                policy_enforcement = security_policies.get("policy_enforcement", {})
                context["deployment_policy"] = policy_enforcement.get("agent_deployment_policy", "")
                context["resource_limits"] = policy_enforcement.get("agent_resource_limits", "")
                context["communication_policy"] = policy_enforcement.get("agent_communication_policy", "")
                
                # Apply tenant isolation
                tenant_isolation = security_policies.get("tenant_isolation", {})
                context["context_isolation"] = tenant_isolation.get("agent_context_isolation", False)
                context["data_isolation"] = tenant_isolation.get("agent_data_isolation", False)
                context["capability_isolation"] = tenant_isolation.get("agent_capability_isolation", False)
                
                return {
                    "success": True,
                    "enhanced_context": context,
                    "security_applied": True
                }
            return {"success": False, "error": "Agentic foundation not available"}
        except Exception as e:
            self.logger.error(f"Failed to apply enhanced security policies: {e}")
            return {"success": False, "error": str(e)}



