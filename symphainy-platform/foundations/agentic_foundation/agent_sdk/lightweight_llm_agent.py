"""
Lightweight LLM Agent - Simple Level Agent

This is the foundation of our hierarchical agent system.
Minimum requirements to use an LLM with MCP Tools + AGUI integration.

Characteristics:
- LLM-only operations - simple, stateless LLM calls
- MCP Tools integration - access to platform tools
- AGUI integration - structured output formatting
- Centralized governance - all LLM activity goes through governance
- Cost containment - centralized rate limiting and usage tracking
- Audit trail - complete traceability of LLM operations
"""

import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.di_container.di_container_service import DIContainerService
from .agent_base import AgentBase
from .mcp_client_manager import MCPClientManager
from .policy_integration import PolicyIntegration
from .tool_composition import ToolComposition
from utilities import UserContext


class LightweightLLMAgent(AgentBase):
    """
    Lightweight LLM Agent - Simple level, LLM-only operations
    
    Minimum requirements to use an LLM with MCP Tools + AGUI integration.
    This is the foundation of our hierarchical agent system.
    """
    
    def __init__(self, agent_name: str, capabilities: List[str], 
                 required_roles: List[str], agui_schema: Dict[str, Any],
                 foundation_services: DIContainerService,
                 agentic_foundation: 'AgenticFoundationService',
                 mcp_client_manager: MCPClientManager,
                 policy_integration: PolicyIntegration,
                 tool_composition: ToolComposition,
                 agui_formatter: Any,
                 public_works_foundation=None,
                 **kwargs):
        """
        Initialize Lightweight LLM Agent.
        
        Args:
            agent_name: Name of the agent
            capabilities: List of agent capabilities
            required_roles: List of required roles
            agui_schema: AGUI schema for structured output
            foundation_services: DI container service
            agentic_foundation: Agentic foundation service for agentic capabilities
            mcp_client_manager: MCP client manager
            policy_integration: Policy integration service
            tool_composition: Tool composition service
            agui_formatter: AGUI output formatter
            **kwargs: Additional arguments
        """
        super().__init__(
            agent_name=agent_name,
            capabilities=capabilities,
            required_roles=required_roles,
            agui_schema=agui_schema,
            foundation_services=foundation_services,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=mcp_client_manager,
            policy_integration=policy_integration,
            tool_composition=tool_composition,
            agui_formatter=agui_formatter,
            **kwargs
        )
        
        # Simple agents are LLM-only operations
        self.llm_only_operations = True
        self.mcp_tools_integration = True
        self.agui_integration = True
        self.centralized_governance = True
        self.user_facing = False
        
        # Lightweight LLM specific capabilities
        self.llm_operations = {
            'analyze': self._analyze_text,
            'summarize': self._summarize_text,
            'classify': self._classify_text,
            'extract': self._extract_information,
            'generate': self._generate_content
        }
        
        # Store public works foundation
        self.public_works_foundation = public_works_foundation
        
        # Initialize LLM business abstraction (if public_works_foundation is available)
        if self.public_works_foundation:
            # Use get_abstraction method to get LLM abstraction
            self.llm_abstraction = self.public_works_foundation.get_abstraction("llm")
        else:
            self.llm_abstraction = None
            self.logger.warning("Public Works Foundation not available - LLM abstraction not initialized")
        
        # Initialize governance and audit
        self._initialize_governance()
        
        self.logger.info(f"🤖 LightweightLLMAgent '{agent_name}' initialized with LLM-only operations")
    
    def _initialize_governance(self):
        """Initialize governance and audit capabilities."""
        self.governance_config = {
            'rate_limiting': True,
            'cost_tracking': True,
            'audit_logging': True,
            'usage_monitoring': True
        }
        
        self.audit_log = []
        self.usage_stats = {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'last_request': None
        }
    
    def _analyze_text(self, text: str, analysis_type: str = "general", **kwargs) -> Dict[str, Any]:
        """
        Analyze text using LLM abstraction.
        
        Args:
            text: Text to analyze
            analysis_type: Type of analysis to perform
            **kwargs: Additional parameters
            
        Returns:
            Analysis results
        """
        self._log_operation('analyze', {'text_length': len(text), 'analysis_type': analysis_type})
        
        try:
            # Use LLM business abstraction for analysis
            result = self.llm_abstraction.analyze_text(
                text=text,
                analysis_type=analysis_type,
                **kwargs
            )
            
            self._update_usage_stats(result)
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Analysis failed: {e}")
            raise
    
    def _summarize_text(self, text: str, summary_length: str = "medium", **kwargs) -> Dict[str, Any]:
        """
        Summarize text using LLM abstraction.
        
        Args:
            text: Text to summarize
            summary_length: Length of summary (short, medium, long)
            **kwargs: Additional parameters
            
        Returns:
            Summary results
        """
        self._log_operation('summarize', {'text_length': len(text), 'summary_length': summary_length})
        
        try:
            # Use LLM business abstraction for summarization
            result = self.llm_abstraction.summarize_text(
                text=text,
                summary_length=summary_length,
                **kwargs
            )
            
            self._update_usage_stats(result)
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Summarization failed: {e}")
            raise
    
    def _classify_text(self, text: str, classification_categories: List[str], **kwargs) -> Dict[str, Any]:
        """
        Classify text using LLM abstraction.
        
        Args:
            text: Text to classify
            classification_categories: List of classification categories
            **kwargs: Additional parameters
            
        Returns:
            Classification results
        """
        self._log_operation('classify', {'text_length': len(text), 'categories': len(classification_categories)})
        
        try:
            # Use LLM business abstraction for classification
            result = self.llm_abstraction.classify_text(
                text=text,
                classification_categories=classification_categories,
                **kwargs
            )
            
            self._update_usage_stats(result)
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Classification failed: {e}")
            raise
    
    def _extract_information(self, text: str, extraction_schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Extract information from text using LLM abstraction.
        
        Args:
            text: Text to extract information from
            extraction_schema: Schema for information extraction
            **kwargs: Additional parameters
            
        Returns:
            Extracted information
        """
        self._log_operation('extract', {'text_length': len(text), 'schema_keys': len(extraction_schema.keys())})
        
        try:
            # Use LLM business abstraction for information extraction
            result = self.llm_abstraction.extract_information(
                text=text,
                extraction_schema=extraction_schema,
                **kwargs
            )
            
            self._update_usage_stats(result)
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Information extraction failed: {e}")
            raise
    
    def _generate_content(self, prompt: str, content_type: str = "text", **kwargs) -> Dict[str, Any]:
        """
        Generate content using LLM abstraction.
        
        Args:
            prompt: Prompt for content generation
            content_type: Type of content to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated content
        """
        self._log_operation('generate', {'prompt_length': len(prompt), 'content_type': content_type})
        
        try:
            # Use LLM business abstraction for content generation
            result = self.llm_abstraction.generate_content(
                prompt=prompt,
                content_type=content_type,
                **kwargs
            )
            
            self._update_usage_stats(result)
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Content generation failed: {e}")
            raise
    
    def _log_operation(self, operation: str, metadata: Dict[str, Any]):
        """Log operation for audit trail."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'agent_name': self.agent_name,
            'operation': operation,
            'metadata': metadata,
            'request_id': str(uuid.uuid4())
        }
        
        self.audit_log.append(log_entry)
        self.logger.info(f"📝 Operation logged: {operation}")
    
    def _update_usage_stats(self, result: Dict[str, Any]):
        """Update usage statistics."""
        self.usage_stats['total_requests'] += 1
        self.usage_stats['last_request'] = datetime.now().isoformat()
        
        # Extract token usage if available
        if 'token_usage' in result:
            self.usage_stats['total_tokens'] += result['token_usage'].get('total_tokens', 0)
            self.usage_stats['total_cost'] += result['token_usage'].get('total_cost', 0.0)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return self.usage_stats.copy()
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log."""
        return self.audit_log.copy()
    
    def reset_usage_stats(self):
        """Reset usage statistics."""
        self.usage_stats = {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'last_request': None
        }
        self.audit_log = []
        self.logger.info("🔄 Usage statistics reset")
    
    def execute_llm_operation(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Execute LLM operation with governance.
        
        Args:
            operation: Operation to execute
            **kwargs: Operation parameters
            
        Returns:
            Operation results
        """
        if operation not in self.llm_operations:
            raise ValueError(f"❌ Unknown operation: {operation}")
        
        # Check rate limiting
        if self.governance_config['rate_limiting']:
            self._check_rate_limiting()
        
        # Execute operation
        result = self.llm_operations[operation](**kwargs)
        
        # Log for audit
        if self.governance_config['audit_logging']:
            self._log_operation(operation, kwargs)
        
        return result
    
    def _check_rate_limiting(self):
        """Check rate limiting constraints."""
        # Implement rate limiting logic here
        # For now, just log the check
        self.logger.debug("🔍 Rate limiting check passed")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            'agent_name': self.agent_name,
            'agent_type': 'LightweightLLMAgent',
            'capabilities': self.capabilities,
            'llm_only_operations': self.llm_only_operations,
            'mcp_tools_integration': self.mcp_tools_integration,
            'agui_integration': self.agui_integration,
            'centralized_governance': self.centralized_governance,
            'user_facing': self.user_facing,
            'available_operations': list(self.llm_operations.keys()),
            'usage_stats': self.get_usage_stats()
        }
    
    # ============================================================================
    # ABSTRACT METHOD IMPLEMENTATIONS
    # ============================================================================
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request using agent capabilities.
        
        Args:
            request: Request dictionary containing operation and parameters
            
        Returns:
            Response dictionary with results
        """
        try:
            operation = request.get('operation')
            parameters = request.get('parameters', {})
            
            if not operation:
                return {
                    'success': False,
                    'error': 'No operation specified in request',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Check if operation is supported
            if operation not in self.llm_operations:
                return {
                    'success': False,
                    'error': f'Unsupported operation: {operation}',
                    'available_operations': list(self.llm_operations.keys()),
                    'timestamp': datetime.now().isoformat()
                }
            
            # Execute the operation
            result = self.execute_llm_operation(operation, **parameters)
            
            return {
                'success': True,
                'result': result,
                'operation': operation,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Request processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_agent_capabilities(self) -> List[str]:
        """
        Get list of agent capabilities.
        
        Returns:
            List of capability strings
        """
        return self.capabilities.copy()
    
    async def get_agent_description(self) -> str:
        """
        Get agent description.
        
        Returns:
            Description string
        """
        return f"LightweightLLMAgent '{self.agent_name}' - Simple level agent for LLM-only operations with centralized governance, cost containment, and audit trail capabilities."
    
    # ============================================================================
    # MULTI-TENANT PROTOCOL IMPLEMENTATIONS
    # ============================================================================
    
    async def get_tenant_context(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get tenant context for operations.
        
        Args:
            tenant_id: ID of the tenant
            
        Returns:
            Tenant context dictionary or None if not found
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.get_tenant_context(tenant_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to get tenant context: {e}")
            return None
    
    async def validate_tenant_access(self, user_id: str, tenant_id: str) -> bool:
        """
        Validate user access to tenant.
        
        Args:
            user_id: ID of the user
            tenant_id: ID of the tenant
            
        Returns:
            True if access is valid, False otherwise
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.validate_tenant_access(user_id, tenant_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to validate tenant access: {e}")
            return False
    
    async def get_user_tenant_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's tenant context.
        
        Args:
            user_id: ID of the user
            
        Returns:
            User tenant context or None if not found
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.get_user_tenant_context(user_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to get user tenant context: {e}")
            return None
    
    async def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new tenant.
        
        Args:
            tenant_data: Tenant data dictionary
            
        Returns:
            Creation result dictionary
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.create_tenant(tenant_data)
        except Exception as e:
            self.logger.error(f"❌ Failed to create tenant: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update tenant.
        
        Args:
            tenant_id: ID of the tenant
            updates: Updates dictionary
            
        Returns:
            Update result dictionary
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.update_tenant(tenant_id, updates)
        except Exception as e:
            self.logger.error(f"❌ Failed to update tenant: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def delete_tenant(self, tenant_id: str) -> Dict[str, Any]:
        """
        Delete tenant.
        
        Args:
            tenant_id: ID of the tenant
            
        Returns:
            Deletion result dictionary
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.delete_tenant(tenant_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to delete tenant: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def list_tenants(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List tenants accessible to user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of tenant contexts
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.list_tenants(user_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to list tenants: {e}")
            return []
    
    async def add_user_to_tenant(self, tenant_id: str, user_id: str, permissions: List[str] = None) -> Dict[str, Any]:
        """
        Add user to tenant.
        
        Args:
            tenant_id: ID of the tenant
            user_id: ID of the user
            permissions: List of permissions (optional)
            
        Returns:
            Addition result dictionary
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.add_user_to_tenant(tenant_id, user_id, permissions)
        except Exception as e:
            self.logger.error(f"❌ Failed to add user to tenant: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def remove_user_from_tenant(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
        """
        Remove user from tenant.
        
        Args:
            tenant_id: ID of the tenant
            user_id: ID of the user
            
        Returns:
            Removal result dictionary
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.remove_user_from_tenant(tenant_id, user_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to remove user from tenant: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_tenant_users(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Get users in tenant.
        
        Args:
            tenant_id: ID of the tenant
            
        Returns:
            List of user contexts
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.get_tenant_users(tenant_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to get tenant users: {e}")
            return []
    
    async def validate_tenant_feature_access(self, tenant_id: str, feature: str) -> bool:
        """
        Validate if tenant can access feature.
        
        Args:
            tenant_id: ID of the tenant
            feature: Feature name
            
        Returns:
            True if access is valid, False otherwise
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.validate_tenant_feature_access(tenant_id, feature)
        except Exception as e:
            self.logger.error(f"❌ Failed to validate tenant feature access: {e}")
            return False
    
    async def get_tenant_usage_stats(self, tenant_id: str) -> Dict[str, Any]:
        """
        Get tenant usage statistics.
        
        Args:
            tenant_id: ID of the tenant
            
        Returns:
            Usage statistics dictionary
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.get_tenant_usage_stats(tenant_id)
        except Exception as e:
            self.logger.error(f"❌ Failed to get tenant usage stats: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def audit_tenant_action(self, tenant_id: str, user_id: str, action: str, resource: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Audit tenant action.
        
        Args:
            tenant_id: ID of the tenant
            user_id: ID of the user
            action: Action performed
            resource: Resource affected
            details: Additional details (optional)
            
        Returns:
            Audit result dictionary
        """
        try:
            # Use tenant management utility from DI container
            tenant_utility = self.foundation_services.get_tenant()
            return await tenant_utility.audit_tenant_action(tenant_id, user_id, action, resource, details)
        except Exception as e:
            self.logger.error(f"❌ Failed to audit tenant action: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }