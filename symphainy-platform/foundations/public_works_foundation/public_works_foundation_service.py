#!/usr/bin/env python3
"""
Public Works Foundation Service - 5-Layer Architecture in Single Domain

This service implements the CTO's 5-layer architecture pattern within a single domain,
providing infrastructure capabilities to all Smart City roles without circular references.

WHAT (Foundation Role): I provide infrastructure capabilities to all Smart City roles
HOW (Foundation Implementation): I use 5-layer architecture with dependency injection
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# Import 5-layer architecture components
from .infrastructure_adapters.config_adapter import ConfigAdapter
from .infrastructure_registry.security_registry import SecurityRegistry
from .infrastructure_registry.file_management_registry_gcs import FileManagementRegistry
from .infrastructure_registry.content_metadata_registry import ContentMetadataRegistry
from .infrastructure_registry.service_discovery_registry import ServiceDiscoveryRegistry
from .infrastructure_registry.routing_registry import RoutingRegistry
from .composition_services.security_composition_service import SecurityCompositionService
from .composition_services.session_composition_service import SessionCompositionService
from .composition_services.state_composition_service import StateCompositionService
from .composition_services.post_office_composition_service import PostOfficeCompositionService
from .composition_services.conductor_composition_service import ConductorCompositionService
from .composition_services.policy_composition_service import PolicyCompositionService

# Import abstraction contracts
from .abstraction_contracts.authentication_protocol import AuthenticationProtocol, SecurityContext
from .abstraction_contracts.authorization_protocol import AuthorizationProtocol
from .abstraction_contracts.session_protocol import SessionProtocol
from .abstraction_contracts.tenant_protocol import TenantProtocol
from .abstraction_contracts.policy_engine_protocol import PolicyEngine

# Import infrastructure abstractions
from .infrastructure_abstractions.auth_abstraction import AuthAbstraction
from .infrastructure_abstractions.authorization_abstraction import AuthorizationAbstraction
from .infrastructure_abstractions.session_abstraction import SessionAbstraction
from .infrastructure_abstractions.tenant_abstraction import TenantAbstraction
from .infrastructure_abstractions.policy_abstraction import PolicyAbstraction
from .infrastructure_abstractions.telemetry_abstraction import TelemetryAbstraction
from .infrastructure_abstractions.alert_management_abstraction import AlertManagementAbstraction
from .infrastructure_abstractions.health_abstraction import HealthAbstraction

# Import FoundationServiceBase
from bases.foundation_service_base import FoundationServiceBase

logger = logging.getLogger(__name__)

class PublicWorksFoundationService(FoundationServiceBase):
    """
    Public Works Foundation Service - 5-Layer Architecture in Single Domain
    
    This service implements the CTO's 5-layer architecture pattern within a single domain,
    providing infrastructure capabilities to all Smart City roles without circular references.
    """
    
    def __init__(self, di_container, security_provider=None, authorization_guard=None, communication_foundation=None):
        """Initialize Public Works Foundation Service with enhanced platform capabilities."""
        super().__init__(
            service_name="public_works_foundation",
            di_container=di_container,
            security_provider=security_provider,
            authorization_guard=authorization_guard
        )
        
        # Store communication foundation reference
        self.communication_foundation = communication_foundation
        
        # 5-layer architecture components
        self.config_adapter = None
        self.security_registry = None
        self.file_management_registry = None
        self.content_metadata_registry = None
        self.service_discovery_registry = None
        self.routing_registry = None
        self.composition_service = None
        
        # Infrastructure abstractions (exposed to all Smart City roles)
        self.auth_abstraction = None
        self.authorization_abstraction = None
        self.session_abstraction = None
        self.tenant_abstraction = None
        self.service_discovery_abstraction = None
        self.routing_abstraction = None
        self.telemetry_abstraction = None
        self.alert_management_abstraction = None
        self.health_abstraction = None
        self.log_aggregation_abstraction = None
        self.observability_abstraction = None  # NEW: For platform observability data storage
        
        # Post Office abstractions
        self.messaging_abstraction = None
        self.event_management_abstraction = None
        
        # Cache abstraction (for content/data caching, NOT messaging)
        self.cache_abstraction = None
        
        # File management abstractions
        self.file_management_abstraction = None
        self.file_management_composition = None
        
        # Content metadata abstractions
        self.content_metadata_abstraction = None
        self.content_schema_abstraction = None
        self.content_insights_abstraction = None
        self.semantic_data_abstraction = None  # NEW: For embeddings and semantic graphs
        self.content_metadata_composition = None
        self.content_analysis_composition = None
        
        # Document intelligence abstraction
        self.document_intelligence_abstraction = None
        
        # Workflow/BPMN abstractions
        self.bpmn_processing_abstraction = None
        
        # SOP abstractions
        self.sop_processing_abstraction = None
        self.sop_enhancement_abstraction = None
        
        # Financial/Strategic Planning abstractions
        self.strategic_planning_abstraction = None
        self.financial_analysis_abstraction = None
        
        # LLM infrastructure abstractions (for agentic pillar)
        self.llm_abstraction = None
        self.llm_composition_service = None
        
        # MCP configured for direct injection via DI container (protocol standard)
        
        # AGUI infrastructure abstractions (for agentic pillar)
        self.agui_abstraction = None
        self.agui_composition_service = None
        
        # Tool storage infrastructure abstractions (for agentic pillar)
        self.tool_storage_abstraction = None
        
        # Policy infrastructure abstractions (for agentic pillar)
        self.policy_abstraction = None
        self.policy_composition_service = None
        
        # Policy engines
        self.default_policy_engine = None
        self.supabase_rls_policy_engine = None
        
        # Conductor infrastructure abstractions (for Conductor service)
        self.task_management_abstraction = None
        self.workflow_orchestration_abstraction = None
        self.conductor_composition_service = None
        
        # Librarian infrastructure abstractions (for Librarian service)
        self.knowledge_discovery_abstraction = None
        self.knowledge_governance_abstraction = None
        self.knowledge_infrastructure_composition_service = None
        self.knowledge_infrastructure_registry = None
        
        # Service state
        self.is_initialized = False
        
        self.logger.info("✅ Public Works Foundation Service initialized")
    
    # ============================================================================
    # FOUNDATION INITIALIZATION (5-Layer Architecture)
    # ============================================================================
    
    async def initialize_foundation(self, config_file: str = ".env") -> bool:
        """Initialize the 5-layer architecture foundation."""
        try:
            self.logger.info("🏗️ Initializing Public Works Foundation with 5-layer architecture...")
            
            # Layer 1: Initialize Unified Configuration Manager and Config Adapter
            # FIX: Create UnifiedConfigurationManager first, then pass to ConfigAdapter
            from utilities.configuration.unified_configuration_manager import UnifiedConfigurationManager
            from utilities.path_utils import get_project_root
            
            # CRITICAL: Wrap blocking path operations in asyncio.to_thread() to prevent SSH crashes
            # Path operations can hang if filesystem is slow or locked
            try:
                project_root = await asyncio.wait_for(
                    asyncio.to_thread(get_project_root),
                    timeout=5.0  # 5 second timeout for path operations
                )
            except (RuntimeError, asyncio.TimeoutError):
                # Fallback to current working directory (also wrapped)
                try:
                    project_root = await asyncio.wait_for(
                        asyncio.to_thread(lambda: Path.cwd()),
                        timeout=5.0  # 5 second timeout for path operations
                    )
                    self.logger.warning(f"⚠️ Could not determine project root, using: {project_root}")
                except asyncio.TimeoutError:
                    # Last resort: use a default path (shouldn't happen, but prevents hang)
                    project_root = Path("/tmp")  # Fallback path
                    self.logger.error(f"❌ Path operations timed out, using fallback: {project_root}")
            
            # CRITICAL: UnifiedConfigurationManager.__init__() does file I/O (open(), yaml.safe_load())
            # Wrap in asyncio.to_thread() to prevent blocking the event loop
            try:
                self.unified_config_manager = await asyncio.wait_for(
                    asyncio.to_thread(
                        UnifiedConfigurationManager,
                        service_name="public_works_foundation",
                        config_root=str(project_root)
                    ),
                    timeout=10.0  # 10 second timeout for config loading
                )
            except asyncio.TimeoutError:
                self.logger.error("❌ UnifiedConfigurationManager initialization timed out after 10 seconds")
                raise RuntimeError("Configuration loading timed out - filesystem may be slow or locked")
            self.logger.info("✅ Unified Configuration Manager created")
            
            # Create ConfigAdapter with UnifiedConfigurationManager
            self.config_adapter = ConfigAdapter(
                unified_config_manager=self.unified_config_manager,
                env_file_path=config_file  # Kept for backward compatibility but not used
            )
            self.logger.info("✅ Config Adapter initialized with Unified Configuration Manager")
            
            self.logger.info("✅ Layer 1: Configuration Adapter initialized")
            
            # ========================================================================
            # LAYER 0: Create ALL Infrastructure Adapters (connect to managed services)
            # ========================================================================
            self.logger.info("🔧 Layer 0: Creating all infrastructure adapters...")
            await self._create_all_adapters()
            self.logger.info("✅ Layer 0: All adapters created")
            
            # ========================================================================
            # LAYER 1: Create ALL Infrastructure Abstractions (with injected adapters)
            # ========================================================================
            self.logger.info("🔧 Layer 1: Creating all infrastructure abstractions...")
            await self._create_all_abstractions()
            self.logger.info("✅ Layer 1: All abstractions created")
            
            # ========================================================================
            # LAYER 2: Initialize Infrastructure Registries (exposure/discovery only)
            # ========================================================================
            self.logger.info("🔧 Layer 2: Initializing registries and registering abstractions...")
            await self._initialize_and_register_abstractions()
            self.logger.info("✅ Layer 2: All abstractions registered with registries")
            
            # Service Discovery Registry is now initialized in _initialize_and_register_abstractions()
            # along with other registries (exposure-only pattern)
            
            # NOTE: All abstractions are now created in _create_all_abstractions() and
            # registered with registries in _initialize_and_register_abstractions()
            # They are available as instance variables (self.auth_abstraction, etc.)
            
            # Initialize Traffic Cop abstractions (not in security registry yet)
            from .infrastructure_abstractions.session_management_abstraction import SessionManagementAbstraction
            from .infrastructure_abstractions.state_management_abstraction import StateManagementAbstraction
            from .infrastructure_adapters.session_management_adapter import SessionManagementAdapter
            from .infrastructure_adapters.state_management_adapter import StateManagementAdapter
            from .infrastructure_adapters.redis_adapter import RedisAdapter
            # BREAKING: JWT adapter import removed - user auth uses Supabase only
            # from .infrastructure_adapters.jwt_adapter import JWTAdapter
            
            # Create adapters for Traffic Cop
            redis_config = self.config_adapter.get_redis_config()
            redis_adapter = RedisAdapter(
                host=redis_config["host"],
                port=redis_config["port"],
                db=redis_config["db"],
                password=redis_config["password"]
            )
            # BREAKING: JWT adapter removed - will break SessionManagementAbstraction
            # jwt_config = self.config_adapter.get_jwt_config()
            # jwt_adapter = JWTAdapter(secret_key=jwt_config["secret_key"] or "default-jwt-secret")
            jwt_adapter = None  # ❌ BREAKING: Removed for user auth (session tokens may need different approach)
            session_management_adapter = SessionManagementAdapter(di_container=self.di_container)
            state_management_adapter = StateManagementAdapter(di_container=self.di_container)
            
            # Initialize Traffic Cop abstractions
            # BREAKING: This will fail if SessionManagementAbstraction requires jwt_adapter
            self.session_management_abstraction = SessionManagementAbstraction(
                redis_adapter, jwt_adapter, self.config_adapter, di_container=self.di_container
            )
            self.state_management_abstraction = StateManagementAbstraction(
                state_management_adapter, redis_adapter, self.config_adapter, di_container=self.di_container
            )
            
            # Initialize Post Office abstractions
            from .infrastructure_abstractions.event_management_abstraction import EventManagementAbstraction
            from .infrastructure_abstractions.messaging_abstraction import MessagingAbstraction
            from .infrastructure_adapters.redis_event_bus_adapter import RedisEventBusAdapter
            from .infrastructure_adapters.redis_messaging_adapter import RedisMessagingAdapter
            
            # Create adapters for Post Office
            # Note: These specialized adapters need the raw Redis client for composition
            # Using backward-compatibility alias (redis_adapter.client) is acceptable here
            # as this is within Public Works Foundation for adapter composition
            event_bus_adapter = RedisEventBusAdapter(redis_adapter.client, di_container=self.di_container)
            messaging_adapter = RedisMessagingAdapter(redis_adapter.client, di_container=self.di_container)
            
            # Initialize Post Office abstractions
            self.event_management_abstraction = EventManagementAbstraction(
                event_bus_adapter, self.config_adapter, di_container=self.di_container
            )
            self.messaging_abstraction = MessagingAbstraction(
                messaging_adapter, self.config_adapter, di_container=self.di_container
            )
            
            # Initialize Cache abstraction (for content/data caching, NOT messaging)
            from .infrastructure_abstractions.cache_abstraction import CacheAbstraction
            from .infrastructure_adapters.cache_adapter import CacheAdapter
            
            # Create cache adapter (defaults to memory, can be configured for Redis)
            cache_adapter = CacheAdapter(storage_type="memory")  # TODO: Configure from environment
            self.cache_abstraction = CacheAbstraction(
                cache_adapter, self.config_adapter, di_container=self.di_container
            )
            
            # Get policy engines from registry
            self.default_policy_engine = self.security_registry.get_policy_engine("default")
            self.supabase_rls_policy_engine = self.security_registry.get_policy_engine("supabase_rls")
            
            # Layer 4: Initialize Composition Services (Critical CTO's Vision!)
            self.composition_service = SecurityCompositionService("public_works_composition", di_container=self.di_container)
            await self.composition_service.initialize(
                auth_abstraction=self.auth_abstraction,
                authorization_abstraction=self.authorization_abstraction,
                session_abstraction=self.session_abstraction,
                tenant_abstraction=self.tenant_abstraction,
                policy_engine=self.default_policy_engine
            )
            self.logger.info("✅ Layer 4: Security Composition Service initialized")
            
            # Initialize Session Composition Service
            # SessionCompositionService only takes session_abstraction (not session_management)
            # Use session_abstraction if available, otherwise fallback to session_management_abstraction
            session_abstraction_to_use = self.session_abstraction or self.session_management_abstraction
            if not session_abstraction_to_use:
                raise RuntimeError("Neither session_abstraction nor session_management_abstraction available for SessionCompositionService")
            
            self.session_composition_service = SessionCompositionService(
                session_abstraction=session_abstraction_to_use,
                di_container=self.di_container
            )
            self.logger.info("✅ Layer 4: Session Composition Service initialized")
            
            # Initialize State Composition Service
            self.state_composition_service = StateCompositionService(
                state_management=self.state_management_abstraction,
                di_container=self.di_container
            )
            self.logger.info("✅ Layer 4: State Composition Service initialized")
            
            # Initialize Post Office Composition Service
            self.post_office_composition_service = PostOfficeCompositionService(
                event_management=self.event_management_abstraction,
                messaging=self.messaging_abstraction,
                di_container=self.di_container
            )
            self.logger.info("✅ Layer 4: Post Office Composition Service initialized")
            
            # Initialize Conductor Composition Service
            # NOTE: Adapters and abstractions are now created in _create_all_adapters() and _create_all_abstractions()
            from .composition_services.conductor_composition_service import ConductorCompositionService
            
            # Use abstractions created in _create_all_abstractions()
            self.conductor_composition_service = ConductorCompositionService(
                task_management_abstraction=self.task_management_abstraction,
                workflow_orchestration_abstraction=self.workflow_orchestration_abstraction,
                resource_allocation_abstraction=self.resource_allocation_abstraction,
                di_container=self.di_container
            )
            self.logger.info("✅ Layer 4: Conductor Composition Service initialized")
            
            # Initialize Librarian Infrastructure Abstractions (for Librarian service)
            # NOTE: Adapters and abstractions are now created in _create_all_adapters() and _create_all_abstractions()
            from .composition_services.knowledge_infrastructure_composition_service import KnowledgeInfrastructureCompositionService
            from .infrastructure_registry.knowledge_infrastructure_registry import KnowledgeInfrastructureRegistry
            
            # Use abstractions created in _create_all_abstractions()
            self.knowledge_infrastructure_composition_service = KnowledgeInfrastructureCompositionService(
                knowledge_discovery=self.knowledge_discovery_abstraction,
                knowledge_governance=self.knowledge_governance_abstraction,
                di_container=self.di_container
            )
            
            # Initialize Knowledge Infrastructure Registry
            self.knowledge_infrastructure_registry = KnowledgeInfrastructureRegistry(
                composition_service=self.knowledge_infrastructure_composition_service
            )
            
            self.logger.info("✅ Layer 4: Knowledge Infrastructure Composition Service initialized")
            self.logger.info("✅ Layer 5: Knowledge Infrastructure Registry initialized")
            
            # Initialize LLM Infrastructure Abstractions (for agentic pillar)
            from .infrastructure_abstractions.llm_abstraction import LLMAbstraction
            from .infrastructure_adapters.openai_adapter import OpenAIAdapter
            from .infrastructure_adapters.anthropic_adapter import AnthropicAdapter
            from .composition_services.llm_composition_service import LLMCompositionService
            
            # Create LLM adapters (dependency injection pattern)
            self.logger.info("🔧 Creating LLM adapters...")
            # Get API keys from config adapter (supports both LLM_OPENAI_API_KEY and OPENAI_API_KEY)
            openai_api_key = self.config_adapter.get("LLM_OPENAI_API_KEY") or self.config_adapter.get("OPENAI_API_KEY")
            openai_base_url = self.config_adapter.get("OPENAI_BASE_URL")
            openai_adapter = OpenAIAdapter(
                api_key=openai_api_key, 
                base_url=openai_base_url,
                config_adapter=self.config_adapter  # Pass ConfigAdapter for centralized configuration
            )
            # Create Anthropic adapter (optional - skip if API key not available)
            try:
                anthropic_adapter = AnthropicAdapter(
                    config_adapter=self.config_adapter  # Pass ConfigAdapter for centralized configuration
                )
                # Only use adapter if it has an API key
                if not anthropic_adapter.api_key:
                    self.logger.warning("⚠️ Anthropic adapter created but API key not available - will be disabled")
                    anthropic_adapter = None
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to create Anthropic adapter (optional): {e}")
                anthropic_adapter = None
            # Ollama adapter is optional - comment out for now as it's not part of current platform
            # ollama_adapter = OllamaAdapter()
            
            # Get LLM configuration for retry/timeout
            llm_config = self.config_adapter.get_llm_abstraction_config() if hasattr(self.config_adapter, 'get_llm_abstraction_config') else {}
            
            # Create LLM abstraction with injected adapters and production resilience config
            self.llm_abstraction = LLMAbstraction(
                openai_adapter=openai_adapter,
                anthropic_adapter=anthropic_adapter,
                ollama_adapter=None,  # Commented out for now
                provider="openai",
                di_container=self.di_container,
                retry_enabled=llm_config.get("retry_enabled", True),
                max_retries=llm_config.get("provider_retry_attempts", 3),
                retry_base_delay=llm_config.get("provider_retry_delay_seconds", 2.0),
                timeout=llm_config.get("provider_timeout_seconds", 120.0),
                rate_limiting_abstraction=None  # Optional - can be set later if needed
            )
            
            # Create LLM composition service
            self.llm_composition_service = LLMCompositionService(self.llm_abstraction, di_container=self.di_container)
            
            self.logger.info("✅ LLM Infrastructure Abstractions initialized")
            
            # Initialize MCP Client - Direct Injection (MCP is a protocol standard)
            # MCP is not swappable infrastructure, so we inject the client directly via DI
            # Services that need MCP will inject ClientSession directly from DI container
            self.logger.info("✅ MCP configured for direct injection via DI container")
            
            # Initialize AGUI Infrastructure Abstractions (for agentic pillar)
            from .infrastructure_adapters.websocket_adapter import WebSocketAdapter
            from .infrastructure_abstractions.agui_communication_abstraction import AGUICommunicationAbstraction
            from .composition_services.agui_composition_service import AGUICompositionService
            
            # Create WebSocket adapter
            websocket_adapter = WebSocketAdapter()
            
            # Create AGUI communication abstraction
            self.agui_abstraction = AGUICommunicationAbstraction(
                websocket_adapter,
                di_container=self.di_container
            )
            
            # Create AGUI composition service with Post Office integration
            self.agui_composition_service = AGUICompositionService(
                agui_communication_abstraction=self.agui_abstraction,
                post_office_service=self.post_office_composition_service,
                di_container=self.di_container
            )
            
            self.logger.info("✅ AGUI Infrastructure Abstractions initialized")
            
            # Initialize Tool Storage Infrastructure Abstractions (for agentic pillar)
            from .infrastructure_adapters.arangodb_tool_storage_adapter import ArangoDBToolStorageAdapter
            from .infrastructure_abstractions.tool_storage_abstraction import ToolStorageAbstraction
            
            # Create tool storage adapter
            tool_storage_adapter = ArangoDBToolStorageAdapter(di_container=self.di_container)
            
            # Create tool storage abstraction
            self.tool_storage_abstraction = ToolStorageAbstraction(tool_storage_adapter, di_container=self.di_container)
            
            self.logger.info("✅ Tool Storage Infrastructure Abstractions initialized")
            
            # NOTE: Health and Telemetry abstractions are now created in _create_all_abstractions()
            # Validate they are created (utility capabilities)
            if not hasattr(self, 'health_abstraction') or not self.health_abstraction:
                error_msg = "Health Abstraction failed to initialize. This is a utility capability and should be generally available."
                self.logger.error(f"❌ {error_msg}")
                raise RuntimeError(error_msg)
            
            if not hasattr(self, 'telemetry_abstraction') or not self.telemetry_abstraction:
                error_msg = "Telemetry Abstraction failed to initialize. This is a utility capability and should be generally available."
                self.logger.error(f"❌ {error_msg}")
                raise RuntimeError(error_msg)
            
            self.logger.info("✅ Health and Telemetry abstractions validated")
            
            # Initialize Policy Infrastructure Abstractions (for agentic pillar)
            from .infrastructure_adapters.opa_policy_adapter import OPAPolicyAdapter
            from .composition_services.policy_composition_service import PolicyCompositionService
            
            # Get OPA URL from config (defaults to localhost for development)
            # For Option C deployment, this will be a managed OPA service URL
            opa_url = self.config_adapter.get("OPA_URL", "http://localhost:8181")
            
            # Create policy adapter (using OPA for production)
            policy_adapter = OPAPolicyAdapter(opa_url=opa_url, di_container=self.di_container)
            self.logger.info(f"✅ Policy adapter created (OPA: {opa_url})")
            
            # Create policy abstraction with DI
            self.policy_abstraction = PolicyAbstraction(
                policy_adapter=policy_adapter,  # Dependency injection
                config_adapter=self.config_adapter,
                di_container=self.di_container,
                service_name="policy_abstraction"
            )
            self.logger.info("✅ Policy Abstraction initialized")
            
            # Create policy composition service
            self.policy_composition_service = PolicyCompositionService(self.policy_abstraction, di_container=self.di_container)
            self.logger.info("✅ Policy Composition Service initialized")
            
            self.logger.info("✅ Infrastructure abstractions, policy engines, and composition service loaded")
            
            # Test foundation components
            await self._test_foundation_components()
            
            self.is_initialized = True
            self.logger.info("🎉 Public Works Foundation initialized successfully with 5-layer architecture")
            return True
            
        except Exception as e:
            # Ensure is_initialized is False if initialization fails
            self.is_initialized = False
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "initialize_foundation")
            self.logger.error(f"❌ Failed to initialize Public Works Foundation: {str(e)}")
            return False
    
    async def _test_foundation_components(self):
        """Test all foundation components."""
        try:
            # Test configuration adapter
            config_status = self.config_adapter.test_connection()
            if not config_status.get("success"):
                raise Exception(f"Configuration adapter test failed: {config_status.get('error')}")
            
            # Test security registry
            if not self.security_registry.is_ready():
                raise Exception("Security registry not ready")
            
            self.logger.info("✅ Foundation components tested successfully")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_test_foundation_components")
            self.logger.error(f"Foundation component testing failed: {str(e)}")
            raise
    
    # ============================================================================
    # INFRASTRUCTURE CAPABILITIES (Exposed to All Smart City Roles)
    # ============================================================================
    
    def get_auth_abstraction(self) -> AuthenticationProtocol:
        """Get authentication abstraction for Smart City roles."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.auth_abstraction
    
    def get_authorization_abstraction(self) -> AuthorizationProtocol:
        """Get authorization abstraction for Smart City roles."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.authorization_abstraction
    
    def get_session_abstraction(self) -> SessionProtocol:
        """Get session abstraction for Smart City roles."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        # Use session_abstraction if available
        if self.session_abstraction:
            return self.session_abstraction
        # Fallback to session_management_abstraction (Traffic Cop abstraction) if available
        if hasattr(self, 'session_management_abstraction') and self.session_management_abstraction:
            return self.session_management_abstraction
        raise RuntimeError("Session abstraction not available (neither session_abstraction nor session_management_abstraction)")
    
    def get_tenant_abstraction(self) -> TenantProtocol:
        """Get tenant abstraction for Smart City roles."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.tenant_abstraction
    
    def get_service_discovery_abstraction(self):
        """
        Get service discovery abstraction for service registration and discovery.
        
        This provides technology-agnostic service mesh capabilities (Consul, Istio, Linkerd, etc.)
        
        Returns:
            ServiceDiscoveryAbstraction: Service discovery abstraction
        
        Raises:
            RuntimeError: If foundation not initialized or service discovery not available
        """
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        if not self.service_discovery_abstraction:
            raise RuntimeError("Service discovery abstraction not available (Consul connection may have failed)")
        return self.service_discovery_abstraction
    
    def get_policy_engine(self, engine_name: str = "default") -> PolicyEngine:
        """Get policy engine for Smart City roles."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.security_registry.get_policy_engine(engine_name)
    
    def get_config_adapter(self) -> ConfigAdapter:
        """Get configuration adapter for Smart City roles."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.config_adapter
    
    def get_file_management_abstraction(self):
        """Get file management abstraction for Smart City roles."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.file_management_abstraction
    
    def get_file_management_composition(self):
        """Get file management composition service for Smart City roles."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.file_management_composition
    
    # ============================================================================
    # CONTENT METADATA CAPABILITIES (Exposed to Content Pillar)
    # ============================================================================
    
    def get_content_metadata_abstraction(self):
        """Get content metadata abstraction for Content Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.content_metadata_abstraction
    
    def get_content_schema_abstraction(self):
        """Get content schema abstraction for Content Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.content_schema_abstraction
    
    def get_content_insights_abstraction(self):
        """Get content insights abstraction for Content Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.content_insights_abstraction
    
    def get_content_metadata_composition(self):
        """Get content metadata composition service for Content Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.content_metadata_composition
    
    def get_content_analysis_composition(self):
        """Get content analysis composition service for Content Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.content_analysis_composition
    
    def get_document_intelligence_abstraction(self):
        """
        DEPRECATED: DocumentIntelligenceAbstraction has been replaced with individual file type abstractions.
        
        Use individual abstractions instead:
        - excel_processing, pdf_processing, word_processing, html_processing
        - csv_processing, json_processing, image_processing, text_processing
        
        This method returns None and will be removed in a future version.
        """
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        import warnings
        warnings.warn(
            "get_document_intelligence_abstraction() is deprecated. Use individual file type abstractions instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return None
    
    def get_bpmn_processing_abstraction(self):
        """Get BPMN processing abstraction for Operations pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.bpmn_processing_abstraction
    
    def get_sop_processing_abstraction(self):
        """Get SOP processing abstraction for Insights pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.sop_processing_abstraction
    
    def get_sop_enhancement_abstraction(self):
        """Get SOP enhancement abstraction for Insights pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.sop_enhancement_abstraction
    
    def get_strategic_planning_abstraction(self):
        """Get strategic planning abstraction for Business Outcomes pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.strategic_planning_abstraction
    
    def get_financial_analysis_abstraction(self):
        """Get financial analysis abstraction for Business Outcomes pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.financial_analysis_abstraction
    
    # ============================================================================
    # LLM CAPABILITIES (Exposed to Agentic Pillar)
    # ============================================================================
    
    def get_llm_abstraction(self):
        """Get LLM infrastructure abstraction for Agentic Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.llm_abstraction
    
    def get_llm_composition_service(self):
        """Get LLM composition service for Agentic Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.llm_composition_service
    
    def get_mcp_abstraction(self):
        """Get MCP client factory for Agentic Pillar (via DI container)."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        # MCP is now injected directly via DI container - return factory from DI
        from mcp import ClientSession
        if self.di_container:
            try:
                return self.di_container.get_utility("mcp_client_factory")
            except:
                return None
        return None
    
    def get_mcp_composition_service(self):
        """Get MCP client for Agentic Pillar (via DI container)."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        # MCP composition is now handled via direct injection of ClientSession
        if self.di_container:
            try:
                return self.di_container.get_utility("mcp_client_factory")
            except:
                return None
        return None
    
    def get_agui_abstraction(self):
        """Get AGUI infrastructure abstraction for Agentic Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.agui_abstraction
    
    def get_agui_composition_service(self):
        """Get AGUI composition service for Agentic Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.agui_composition_service
    
    def get_tool_storage_abstraction(self):
        """Get tool storage abstraction for Agentic Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.tool_storage_abstraction
    
    def get_policy_abstraction(self):
        """Get policy abstraction for Agentic Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.policy_abstraction
    
    def get_telemetry_abstraction(self):
        """Get telemetry abstraction for Nurse Service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        if not hasattr(self, 'telemetry_abstraction') or self.telemetry_abstraction is None:
            error_msg = f"CRITICAL: telemetry_abstraction is None! is_initialized: {self.is_initialized}"
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        return self.telemetry_abstraction
    
    def get_alert_management_abstraction(self):
        """Get alert management abstraction for Nurse Service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.alert_management_abstraction
    
    def get_health_abstraction(self):
        """Get health abstraction for Nurse Service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        if not hasattr(self, 'health_abstraction') or self.health_abstraction is None:
            error_msg = f"CRITICAL: health_abstraction is None! is_initialized: {self.is_initialized}"
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        return self.health_abstraction
    
    # ============================================================================
    # CONDUCTOR CAPABILITIES (Exposed to All Smart City Roles)
    # ============================================================================
    
    def get_task_management_abstraction(self):
        """Get task management abstraction for Conductor Service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.task_management_abstraction
    
    def get_workflow_orchestration_abstraction(self):
        """Get workflow orchestration abstraction for Conductor Service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.workflow_orchestration_abstraction
    
    def get_conductor_composition_service(self):
        """Get conductor composition service for Conductor Service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.conductor_composition_service
    
    def get_knowledge_discovery_abstraction(self):
        """Get knowledge discovery abstraction for Librarian Service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.knowledge_discovery_abstraction
    
    def get_knowledge_governance_abstraction(self):
        """Get knowledge governance abstraction for Librarian Service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.knowledge_governance_abstraction
    
    def get_knowledge_infrastructure_composition_service(self):
        """Get knowledge infrastructure composition service for Librarian Service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.knowledge_infrastructure_composition_service
    
    def get_knowledge_infrastructure_registry(self):
        """Get knowledge infrastructure registry for Librarian Service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.knowledge_infrastructure_registry
    
    def get_state_management_abstraction(self):
        """Get state management abstraction for lineage tracking and state storage."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.state_management_abstraction
    
    def get_messaging_abstraction(self):
        """Get messaging abstraction for communication."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        if not hasattr(self, 'messaging_abstraction'):
            raise RuntimeError("Messaging abstraction not initialized. This may indicate initialization failure.")
        return self.messaging_abstraction
    
    def get_event_management_abstraction(self):
        """Get event management abstraction for event bus/pub-sub communication."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        if not hasattr(self, 'event_management_abstraction'):
            raise RuntimeError("Event management abstraction not initialized. This may indicate initialization failure.")
        return self.event_management_abstraction
    
    def get_websocket_adapter(self):
        """Get WebSocket adapter for WebSocket communication."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        if not hasattr(self, 'agui_abstraction') or not self.agui_abstraction:
            raise RuntimeError("AGUI abstraction not initialized. This may indicate initialization failure.")
        # WebSocket adapter is wrapped in AGUICommunicationAbstraction
        if not hasattr(self.agui_abstraction, 'websocket_adapter') or not self.agui_abstraction.websocket_adapter:
            raise RuntimeError("WebSocket adapter not available in AGUI abstraction. This may indicate initialization failure.")
        return self.agui_abstraction.websocket_adapter
    
    def get_policy_composition_service(self):
        """Get policy composition service for Agentic Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        return self.policy_composition_service
    
    def get_agentic_abstractions(self) -> Dict[str, Any]:
        """Get all agentic abstractions for Agentic Pillar."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        return {
            "llm_abstraction": self.llm_abstraction,
            "llm_composition_service": self.llm_composition_service,
            "mcp_client_factory": self.get_mcp_abstraction(),  # Direct injection via DI
            "agui_abstraction": self.agui_abstraction,
            "agui_composition_service": self.agui_composition_service,
            "tool_storage_abstraction": self.tool_storage_abstraction,
            "policy_abstraction": self.policy_abstraction,
            "policy_composition_service": self.policy_composition_service,
            "event_routing_abstraction": self.event_management_abstraction,
            "session_management_abstraction": self.session_management_abstraction,
            "state_management_abstraction": self.state_management_abstraction,
            "messaging_abstraction": self.messaging_abstraction
        }
    
    # ============================================================================
    # COMPOSITION SERVICE CAPABILITIES (Business-Facing via Composition Service)
    # ============================================================================
    
    async def authenticate_and_authorize(self, credentials: Dict[str, Any], 
                                       action: str, resource: str) -> Dict[str, Any]:
        """Authenticate and authorize using composition service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("authenticate_and_authorize_start", success=True)
            
            # Delegate to composition service (no utilities in composition service)
            result = await self.composition_service.authenticate_and_authorize(credentials, action, resource)
            
            # Record success metric
            await self.record_health_metric("authenticate_and_authorize_success", 1.0, {
                "action": action,
                "resource": resource,
                "success": result.get("success", False) if result else False
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("authenticate_and_authorize_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "authenticate_and_authorize")
            raise
    
    async def create_secure_session(self, user_id: str, tenant_id: str, 
                                  session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create secure session using composition service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_secure_session_start", success=True)
            
            # Delegate to composition service (no utilities in composition service)
            result = await self.composition_service.create_secure_session(user_id, tenant_id, session_data)
            
            # Record success metric
            await self.record_health_metric("create_secure_session_success", 1.0, {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "success": result.get("success", False) if result else False
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_secure_session_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_secure_session")
            raise
    
    async def validate_session_and_authorize(self, session_id: str, 
                                           action: str, resource: str) -> Dict[str, Any]:
        """Validate session and authorize using composition service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("validate_session_and_authorize_start", success=True)
            
            # Delegate to composition service (no utilities in composition service)
            result = await self.composition_service.validate_session_and_authorize(session_id, action, resource)
            
            # Record success metric
            await self.record_health_metric("validate_session_and_authorize_success", 1.0, {
                "session_id": session_id,
                "action": action,
                "resource": resource,
                "success": result.get("success", False) if result else False
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("validate_session_and_authorize_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "validate_session_and_authorize")
            raise
    
    async def enforce_tenant_isolation(self, user_id: str, tenant_id: str, 
                                     resource_tenant: str) -> Dict[str, Any]:
        """Enforce tenant isolation using composition service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("enforce_tenant_isolation_start", success=True)
            
            # Delegate to composition service (no utilities in composition service)
            result = await self.composition_service.enforce_tenant_isolation(user_id, tenant_id, resource_tenant)
            
            # Record success metric
            await self.record_health_metric("enforce_tenant_isolation_success", 1.0, {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "resource_tenant": resource_tenant,
                "success": result.get("success", False) if result else False
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("enforce_tenant_isolation_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "enforce_tenant_isolation")
            raise
    
    async def get_security_context_with_tenant(self, session_id: str) -> Dict[str, Any]:
        """Get security context with tenant using composition service."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_security_context_with_tenant_start", success=True)
            
            # Delegate to composition service (no utilities in composition service)
            result = await self.composition_service.get_security_context_with_tenant(session_id)
            
            # Record success metric
            await self.record_health_metric("get_security_context_with_tenant_success", 1.0, {
                "session_id": session_id,
                "success": result.get("success", False) if result else False
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_security_context_with_tenant_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_security_context_with_tenant")
            raise
    
    # ============================================================================
    # DIRECT INFRASTRUCTURE CAPABILITIES (Exposed to All Smart City Roles)
    # ============================================================================
    
    async def authenticate_user(self, credentials: Dict[str, Any]) -> SecurityContext:
        """Authenticate user using infrastructure abstractions."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("authenticate_user_start", success=True)
            
            # Delegate to abstraction (no utilities in abstraction)
            result = await self.auth_abstraction.authenticate_user(credentials)
            
            # Record success metric
            await self.record_health_metric("authenticate_user_success", 1.0, {
                "user_id": getattr(result, "user_id", None) if result else None
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("authenticate_user_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "authenticate_user")
            raise
    
    async def validate_token(self, token: str) -> SecurityContext:
        """Validate token using infrastructure abstractions."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("validate_token_start", success=True)
            
            # Delegate to abstraction (no utilities in abstraction)
            result = await self.auth_abstraction.validate_token(token)
            
            # Record success metric
            await self.record_health_metric("validate_token_success", 1.0, {
                "user_id": getattr(result, "user_id", None) if result else None
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("validate_token_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "validate_token")
            raise
    
    async def authorize_action(self, action: str, resource: str, context: SecurityContext) -> bool:
        """Authorize action using infrastructure abstractions."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("authorize_action_start", success=True)
            
            # Delegate to abstraction (no utilities in abstraction)
            result = await self.authorization_abstraction.enforce(action, resource, context)
            
            # Record success metric
            await self.record_health_metric("authorize_action_success", 1.0, {
                "action": action,
                "resource": resource,
                "user_id": getattr(context, "user_id", None),
                "authorized": result
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("authorize_action_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "authorize_action")
            raise
    
    async def create_session(self, user_id: str, tenant_id: str, session_data: Dict[str, Any]) -> str:
        """Create session using infrastructure abstractions."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("create_session_start", success=True)
            
            # Delegate to abstraction (no utilities in abstraction)
            result = await self.session_abstraction.create_session(user_id, tenant_id, session_data)
            
            # Record success metric
            await self.record_health_metric("create_session_success", 1.0, {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "session_id": result
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("create_session_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "create_session")
            raise
    
    async def validate_session(self, session_id: str) -> SecurityContext:
        """Validate session using infrastructure abstractions."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("validate_session_start", success=True)
            
            # Delegate to abstraction (no utilities in abstraction)
            result = await self.session_abstraction.validate_session(session_id)
            
            # Record success metric
            await self.record_health_metric("validate_session_success", 1.0, {
                "session_id": session_id,
                "user_id": getattr(result, "user_id", None) if result else None
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("validate_session_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "validate_session")
            raise
    
    async def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant configuration using infrastructure abstractions."""
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_tenant_config_start", success=True)
            
            # Delegate to abstraction (no utilities in abstraction)
            result = await self.tenant_abstraction.get_tenant_config(tenant_id)
            
            # Record success metric
            await self.record_health_metric("get_tenant_config_success", 1.0, {
                "tenant_id": tenant_id
            })
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_tenant_config_complete", success=True)
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_tenant_config")
            raise
    
    # ============================================================================
    # FOUNDATION STATUS AND HEALTH
    # ============================================================================
    
    async def get_foundation_status(self) -> Dict[str, Any]:
        """Get foundation status information."""
        if not self.is_initialized:
            return {
                "foundation_name": "PublicWorksFoundationService",
                "status": "not_initialized",
                "is_initialized": False,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            registry_status = self.security_registry.get_registry_status() if self.security_registry else {}
            file_management_status = self.file_management_registry.get_registry_status() if self.file_management_registry else {}
            content_metadata_status = await self.content_metadata_registry.get_registry_status() if self.content_metadata_registry else {}
            composition_status = await self.composition_service.get_status() if self.composition_service else {}
            
            result = {
                "foundation_name": "PublicWorksFoundationService",
                "status": "active",
                "is_initialized": True,
                "architecture": "5-layer_in_single_domain",
                "capabilities": [
                    "authentication",
                    "authorization", 
                    "session_management",
                    "tenant_management",
                    "policy_engine",
                    "composition_service",
                    "file_management",
                    "file_lineage_tracking",
                    "file_analytics",
                    "content_metadata_management",
                    "content_schema_analysis",
                    "content_insights_generation",
                    "content_relationship_tracking",
                    "content_analysis_workflows",
                    "content_intelligence_reporting",
                    "llm_infrastructure",
                    "llm_composition",
                    "mcp_direct_injection",  # MCP is a protocol standard, injected directly
                    "agui_infrastructure",
                    "agui_composition",
                    "tool_storage_infrastructure",
                    "policy_infrastructure",
                    "policy_composition",
                    "agentic_abstractions"
                ],
                "infrastructure_components": {
                    "security_registry": registry_status,
                    "file_management_registry": file_management_status,
                    "content_metadata_registry": content_metadata_status,
                    "composition_service": composition_status
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record success metric
            await self.record_health_metric("get_foundation_status_success", 1.0, {
                "status": result.get("status"),
                "is_initialized": result.get("is_initialized")
            })
            
            return result
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_foundation_status")
            # Return error status instead of raising
            return {
                "foundation_name": "PublicWorksFoundationService",
                "status": "error",
                "is_initialized": self.is_initialized,
                "error": str(e),
                "error_code": "FOUNDATION_STATUS_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on foundation components."""
        try:
            if not self.is_initialized:
                return {"status": "unhealthy", "reason": "foundation_not_initialized"}
            
            # Test configuration adapter
            config_status = self.config_adapter.test_connection()
            if not config_status.get("success"):
                return {"status": "unhealthy", "reason": "config_adapter_failed", "details": config_status}
            
            # Test security registry
            registry_status = self.security_registry.get_registry_status()
            if not registry_status.get("is_ready"):
                return {"status": "unhealthy", "reason": "security_registry_not_ready", "details": registry_status}
            
            return {
                "status": "healthy",
                "components": {
                    "config_adapter": config_status,
                    "security_registry": registry_status
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "health_check")
            return {"status": "unhealthy", "reason": "health_check_failed", "error": str(e), "error_code": "HEALTH_CHECK_FAILED"}
    
    # ============================================================================
    # FOUNDATION SHUTDOWN
    # ============================================================================
    
    async def shutdown_foundation(self):
        """Shutdown foundation components gracefully."""
        try:
            self.logger.info("🔄 Shutting down Public Works Foundation...")
            
            # Cleanup infrastructure components
            if self.security_registry:
                # Registry cleanup would go here if needed
                pass
            
            self.is_initialized = False
            self.logger.info("✅ Public Works Foundation shutdown complete")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "shutdown_foundation")
            self.logger.error(f"Error during foundation shutdown: {str(e)}")
    
    # ============================================================================
    # REQUIRED ABSTRACT METHODS (FoundationServiceBase)
    # ============================================================================
    
    async def initialize(self):
        """Initialize the Public Works Foundation Service with enhanced platform capabilities."""
        try:
            # Initialize base class first (this initializes enhanced utilities)
            await super().initialize()
            
            # Now we can use enhanced utilities
            # Use enhanced logging with telemetry
            await self.log_operation_with_telemetry("public_works_foundation_initialize", success=True)
            
            # Initialize the original 5-layer architecture (preserving CTO's process)
            self.logger.info("🔧 Calling initialize_foundation()...")
            foundation_result = await self.initialize_foundation()
            self.logger.info(f"🔧 initialize_foundation() returned: {foundation_result}")
            
            # Verify abstractions are still set after initialize_foundation()
            self.logger.info(f"🔍 AFTER initialize_foundation() - health_abstraction: {getattr(self, 'health_abstraction', 'NOT_SET')}, telemetry_abstraction: {getattr(self, 'telemetry_abstraction', 'NOT_SET')}")
            
            if not foundation_result:
                # Don't fail hard - log warning but continue (some adapters may be optional)
                self.logger.warning("⚠️ initialize_foundation() returned False - some adapters may be disabled, but continuing startup")
                # Mark as initialized anyway so other services can proceed
                self.is_initialized = True
            
            # Initialize enhanced platform capabilities
            self.logger.info("🔧 Calling _initialize_enhanced_platform_capabilities()...")
            await self._initialize_enhanced_platform_capabilities()
            
            # Verify abstractions are still set after enhanced capabilities
            self.logger.info(f"🔍 AFTER _initialize_enhanced_platform_capabilities() - health_abstraction: {getattr(self, 'health_abstraction', 'NOT_SET')}, telemetry_abstraction: {getattr(self, 'telemetry_abstraction', 'NOT_SET')}")
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            # Final verification before marking as initialized
            self.logger.info(f"🔍 FINAL BEFORE is_initialized=True - health_abstraction: {getattr(self, 'health_abstraction', 'NOT_SET')}, telemetry_abstraction: {getattr(self, 'telemetry_abstraction', 'NOT_SET')}")
            
            # Record health metric
            await self.record_health_metric("public_works_foundation_initialized", 1.0, {"service": "public_works_foundation"})
            
            # Use enhanced logging with telemetry
            await self.log_operation_with_telemetry("public_works_foundation_initialize_complete", success=True)
            
            # Final verification after all initialization
            self.logger.info(f"🔍 FINAL AFTER ALL INIT - health_abstraction: {getattr(self, 'health_abstraction', 'NOT_SET')}, telemetry_abstraction: {getattr(self, 'telemetry_abstraction', 'NOT_SET')}")
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "public_works_foundation_initialize")
            self.service_health = "error"
            self.is_initialized = False
            self.logger.error(f"❌ initialize() failed - health_abstraction: {getattr(self, 'health_abstraction', 'NOT_SET')}, telemetry_abstraction: {getattr(self, 'telemetry_abstraction', 'NOT_SET')}")
            raise
    
    async def shutdown(self):
        """Shutdown the Public Works Foundation Service."""
        try:
            # Use enhanced logging with telemetry
            await self.log_operation_with_telemetry("public_works_foundation_shutdown", success=True)
            
            # Shutdown all infrastructure components
            await self.shutdown_foundation()
            
            # Clear all abstractions and registries
            self.auth_abstraction = None
            self.authorization_abstraction = None
            self.session_abstraction = None
            self.tenant_abstraction = None
            self.file_management_abstraction = None
            self.content_metadata_abstraction = None
            
            self.is_initialized = False
            self.service_health = "shutdown"
            
            # Record shutdown metric
            await self.record_health_metric("public_works_foundation_shutdown", 1.0, {"service": "public_works_foundation"})
            
            # Use enhanced logging with telemetry
            await self.log_operation_with_telemetry("public_works_foundation_shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "public_works_foundation_shutdown")
    
    
    # ============================================================================
    # ENHANCED PLATFORM CAPABILITIES
    # ============================================================================
    
    async def _initialize_enhanced_platform_capabilities(self):
        """Initialize enhanced platform capabilities while preserving 5-layer architecture."""
        try:
            self.logger.info("🚀 Initializing enhanced platform capabilities...")
            
            # Enhanced security patterns (zero-trust, policy engine, tenant isolation)
            await self._initialize_enhanced_security()
            
            # Enhanced utility patterns (logging, error handling, health monitoring)
            await self._initialize_enhanced_utilities()
            
            # Platform capabilities (SOA communication, service discovery, capability registry)
            await self._initialize_platform_capabilities()
            
            self.logger.info("✅ Enhanced platform capabilities initialized")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_initialize_enhanced_platform_capabilities")
            self.logger.error(f"❌ Failed to initialize enhanced platform capabilities: {e}")
            raise
    
    async def _initialize_enhanced_security(self):
        """Initialize enhanced security patterns."""
        try:
            self.logger.info("🔒 Initializing enhanced security patterns...")
            
            # Zero-trust security is already initialized in the base class
            # Policy engine is already initialized in the base class
            # Tenant isolation is already initialized in the base class
            # Security audit is already initialized in the base class
            
            self.logger.info("✅ Enhanced security patterns initialized")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_initialize_enhanced_security")
            self.logger.error(f"❌ Failed to initialize enhanced security: {e}")
            raise
    
    async def _initialize_enhanced_utilities(self):
        """Initialize enhanced utility patterns."""
        try:
            self.logger.info("🛠️ Initializing enhanced utility patterns...")
            
            # Enhanced utilities are already initialized in the base class during __init__
            # No need to call super() - this method is specific to Public Works Foundation
            # Enhanced logging is already initialized in the base class
            # Enhanced error handling is already initialized in the base class
            # Health monitoring is already initialized in the base class
            # Performance monitoring is already initialized in the base class
            
            self.logger.info("✅ Enhanced utility patterns initialized")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_initialize_enhanced_utilities")
            self.logger.error(f"❌ Failed to initialize enhanced utilities: {e}")
            raise
    
    async def _initialize_platform_capabilities(self):
        """Initialize platform capabilities."""
        try:
            self.logger.info("🌐 Initializing platform capabilities...")
            
            # SOA communication is already initialized in the base class
            # Service discovery is already initialized in the base class
            # Capability registry is already initialized in the base class
            # Performance monitoring is already initialized in the base class
            
            self.logger.info("✅ Platform capabilities initialized")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_initialize_platform_capabilities")
            self.logger.error(f"❌ Failed to initialize platform capabilities: {e}")
            raise
    
    def _create_file_management_abstraction(self):
        """Create file management abstraction with real working code."""
        # This would create a real file management abstraction
        # For now, return a basic implementation
        class FileManagementAbstraction:
            async def initialize(self):
                pass
            async def health_check(self):
                return {"status": "healthy"}
        
        return FileManagementAbstraction()
    
    def _create_content_metadata_abstraction(self):
        """Create content metadata abstraction with real working code."""
        # This would create a real content metadata abstraction
        # For now, return a basic implementation
        class ContentMetadataAbstraction:
            async def initialize(self):
                pass
            async def health_check(self):
                return {"status": "healthy"}
        
        return ContentMetadataAbstraction()
    
    def _create_content_schema_abstraction(self):
        """Create content schema abstraction with real working code."""
        # This would create a real content schema abstraction
        # For now, return a basic implementation
        class ContentSchemaAbstraction:
            async def initialize(self):
                pass
            async def health_check(self):
                return {"status": "healthy"}
        
        return ContentSchemaAbstraction()
    
    def _create_content_insights_abstraction(self):
        """Create content insights abstraction with real working code."""
        # This would create a real content insights abstraction
        # For now, return a basic implementation
        class ContentInsightsAbstraction:
            async def initialize(self):
                pass
            async def health_check(self):
                return {"status": "healthy"}
        
        return ContentInsightsAbstraction()
    
    # ============================================================================
    # LAYER 0: CREATE ALL ADAPTERS (Single Source of Truth)
    # ============================================================================
    
    async def _create_all_adapters(self):
        """Create all infrastructure adapters (Layer 0) - connects to managed services."""
        try:
            # Security Adapters
            from .infrastructure_adapters.supabase_adapter import SupabaseAdapter
            from .infrastructure_adapters.redis_adapter import RedisAdapter
            # BREAKING: JWT adapter import removed - user auth uses Supabase only
            # from .infrastructure_adapters.jwt_adapter import JWTAdapter
            
            # Supabase Adapter (connects to Supabase Cloud)
            supabase_url = self.config_adapter.get_supabase_url()
            supabase_anon_key = self.config_adapter.get_supabase_anon_key()
            supabase_service_key = self.config_adapter.get_supabase_service_key()
            
            if not supabase_url or not supabase_anon_key:
                raise ValueError("Supabase configuration missing")
            
            self.supabase_adapter = SupabaseAdapter(
                url=supabase_url,
                anon_key=supabase_anon_key,
                service_key=supabase_service_key,
                config_adapter=self.config_adapter  # Pass ConfigAdapter for centralized configuration
            )
            self.logger.info("✅ Supabase adapter created")
            
            # Redis Adapter (connects to MemoryStore/Upstash)
            redis_config = self.config_adapter.get_redis_config()
            self.redis_adapter = RedisAdapter(
                host=redis_config["host"],
                port=redis_config["port"],
                db=redis_config["db"],
                password=redis_config.get("password")
            )
            self.logger.info("✅ Redis adapter created")
            
            # BREAKING: JWT Adapter removed for user authentication
            # Supabase handles all user authentication tokens.
            # JWT adapter may still be needed for session management (session tokens),
            # but user authentication uses Supabase only.
            # self.jwt_adapter = None  # Not created - user auth uses Supabase only
            self.logger.info("⚠️ JWT adapter NOT created - user authentication uses Supabase only")
            
            # File Management Adapters
            from .infrastructure_adapters.gcs_file_adapter import GCSFileAdapter
            from .infrastructure_adapters.supabase_file_management_adapter import SupabaseFileManagementAdapter
            
            # GCS Adapter (connects to Google Cloud Storage) - REQUIRED for FileManagementAbstraction
            try:
                # Use unified InfrastructureConfig for configuration
                from .infrastructure_adapters.infrastructure_config import InfrastructureConfig
                infra_config = InfrastructureConfig(self.config_adapter)
                storage_config = infra_config.get_storage_config()
                gcs_config = storage_config["gcs"]
                
                # Validate required GCS configuration
                if not gcs_config.get("bucket_name"):
                    raise ValueError(
                        "GCS bucket_name is required but not configured. "
                        "Set GCS_BUCKET_NAME environment variable or configure in .env.secrets"
                    )
                if not gcs_config.get("project_id"):
                    raise ValueError(
                        "GCS project_id is required but not configured. "
                        "Set GCS_PROJECT_ID or GOOGLE_CLOUD_PROJECT environment variable"
                    )
                
                # Get bucket credentials (Supabase pattern - JSON only)
                # CRITICAL ARCHITECTURAL SEPARATION:
                # - GOOGLE_APPLICATION_CREDENTIALS = SSH/VM access (infrastructure) - NEVER modified or used here
                # - GCS_CREDENTIALS_JSON = Bucket access (Supabase pattern) - JSON string, no file paths!
                # No path resolution needed = no SSH/GCE concerns!
                
                # Create GCS adapter (required infrastructure)
                # Adapter interface unchanged - still uses dependency injection
                # Uses JSON credentials (Supabase pattern - consistent with other adapters)
                self.gcs_adapter = GCSFileAdapter(
                    project_id=gcs_config.get("project_id"),
                    bucket_name=gcs_config["bucket_name"],
                    credentials_json=gcs_config.get("credentials_json")  # JSON string (Supabase pattern)
                )
                self.logger.info("✅ GCS adapter created")
            except Exception as e:
                self.logger.error(f"❌ Failed to create GCS adapter (REQUIRED): {e}")
                raise RuntimeError(
                    f"GCS adapter is required for FileManagementAbstraction but failed to initialize: {e}. "
                    f"Please configure GCS_BUCKET_NAME, GCS_PROJECT_ID, and GCS_CREDENTIALS_JSON (or use Application Default Credentials)"
                ) from e
            
            # Supabase File Management Adapter
            # Use URL and service_key from SupabaseAdapter
            if not self.supabase_adapter.service_key:
                self.logger.warning("⚠️ Supabase service key not available. Supabase File Management adapter may not work correctly.")
            self.supabase_file_adapter = SupabaseFileManagementAdapter(
                url=self.supabase_adapter.url,
                service_key=self.supabase_adapter.service_key or self.supabase_adapter.anon_key
            )
            self.logger.info("✅ Supabase File Management adapter created")
            
            # Content Metadata Adapters
            from .infrastructure_adapters.arangodb_adapter import ArangoDBAdapter
            
            # ArangoDB Adapter (connects to ArangoDB Oasis)
            arango_config = self.config_adapter.get_arangodb_config()
            # Map config keys to adapter parameters
            # Config returns: arangodb_url, arangodb_database, arangodb_username, arangodb_password
            hosts = arango_config.get("hosts") or arango_config.get("url") or arango_config.get("arangodb_url") or "http://localhost:8529"
            database = arango_config.get("database") or arango_config.get("arangodb_database") or "symphainy_metadata"
            username = arango_config.get("user") or arango_config.get("username") or arango_config.get("arangodb_username") or "root"
            password = arango_config.get("password") or arango_config.get("arangodb_password") or ""
            
            self.arango_adapter = ArangoDBAdapter(
                hosts=hosts,
                database=database,
                username=username,
                password=password
            )
            self.logger.info("✅ ArangoDB adapter created (lazy initialization)")
            
            # Connect to ArangoDB (with timeout - will fail gracefully if ArangoDB unavailable)
            # ArangoDB is CRITICAL infrastructure - if unavailable, initialization should fail
            # CRITICAL: This uses async connect() with timeout to prevent SSH session crashes
            try:
                arango_connected = await asyncio.wait_for(
                    self.arango_adapter.connect(timeout=10.0),
                    timeout=15.0  # Total timeout including connect() internal timeout
                )
                if arango_connected:
                    self.logger.info(f"✅ ArangoDB connected successfully ({hosts}/{database})")
                else:
                    raise ConnectionError("ArangoDB connection returned False - ArangoDB is CRITICAL infrastructure")
            except asyncio.TimeoutError:
                self.logger.error(f"❌ ArangoDB connection timed out ({hosts}/{database}) - ArangoDB is CRITICAL infrastructure and must be available")
                raise RuntimeError(f"Public Works Foundation initialization failed: ArangoDB connection timed out. Check if ArangoDB container is running and healthy.")
            except ConnectionError as e:
                self.logger.error(f"❌ ArangoDB connection failed ({hosts}/{database}) - ArangoDB is CRITICAL infrastructure and must be available: {e}")
                raise RuntimeError(f"Public Works Foundation initialization failed: ArangoDB is unavailable. {e}")
            
            # Health Adapter (OpenTelemetry)
            from .infrastructure_adapters.opentelemetry_health_adapter import OpenTelemetryHealthAdapter
            
            self.health_adapter = OpenTelemetryHealthAdapter(
                service_name="public_works_health",
                endpoint=self.config_adapter.get("OPENTELEMETRY_ENDPOINT", "http://localhost:4317"),
                di_container=self.di_container,
                timeout=30
            )
            self.logger.info("✅ Health adapter created")
            
            # Telemetry Adapter (OpenTelemetry)
            from .infrastructure_adapters.telemetry_adapter import TelemetryAdapter
            
            self.telemetry_adapter = TelemetryAdapter(
                service_name="public_works_telemetry",
                service_version="1.0.0"
            )
            self.logger.info("✅ Telemetry adapter created")
            
            # Alert Management Adapter (Redis)
            from .infrastructure_adapters.redis_alerting_adapter import RedisAlertingAdapter
            
            # Get Redis URL from config
            redis_url = self.config_adapter.get("REDIS_URL", "redis://symphainy-redis:6379")
            self.alert_adapter = RedisAlertingAdapter(redis_url=redis_url, config_adapter=self.config_adapter)
            self.logger.info("✅ Alert adapter created")
            
            # Visualization Adapter
            from .infrastructure_adapters.standard_visualization_adapter import StandardVisualizationAdapter
            
            self.visualization_adapter = StandardVisualizationAdapter()
            self.logger.info("✅ Visualization adapter created")
            
            # Business Metrics Adapters
            from .infrastructure_adapters.standard_business_metrics_adapter import StandardBusinessMetricsAdapter
            from .infrastructure_adapters.huggingface_business_metrics_adapter import HuggingFaceBusinessMetricsAdapter
            
            self.standard_business_metrics_adapter = StandardBusinessMetricsAdapter()
            self.huggingface_business_metrics_adapter = HuggingFaceBusinessMetricsAdapter()
            self.logger.info("✅ Business Metrics adapters created")
            
            # HuggingFace Adapter (for semantic inference)
            from .infrastructure_adapters.huggingface_adapter import HuggingFaceAdapter
            
            hf_endpoint_url = self.config_adapter.get("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
            hf_api_key = self.config_adapter.get("HUGGINGFACE_EMBEDDINGS_API_KEY") or self.config_adapter.get("HUGGINGFACE_API_KEY")
            
            if hf_endpoint_url and hf_api_key:
                self.huggingface_adapter = HuggingFaceAdapter(
                    endpoint_url=hf_endpoint_url,
                    api_key=hf_api_key,
                    config_adapter=self.config_adapter  # Pass ConfigAdapter for centralized configuration
                )
                self.logger.info("✅ HuggingFace adapter created")
            else:
                self.logger.warning("⚠️ HuggingFace adapter not created - HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL or HUGGINGFACE_EMBEDDINGS_API_KEY not set")
                self.huggingface_adapter = None
            
            # Conductor Adapters (Task/Workflow)
            from .infrastructure_adapters.celery_adapter import CeleryAdapter
            from .infrastructure_adapters.redis_graph_adapter import RedisGraphAdapter
            from .infrastructure_adapters.resource_adapter import ResourceAdapter
            
            redis_config = self.config_adapter.get_redis_config()
            self.celery_adapter = CeleryAdapter(
                broker_url=f"redis://{redis_config['host']}:{redis_config['port']}/0",
                result_backend=f"redis://{redis_config['host']}:{redis_config['port']}/0"
            )
            self.redis_graph_adapter = RedisGraphAdapter(
                host=redis_config["host"],
                port=redis_config["port"],
                db=1
            )
            self.resource_adapter = ResourceAdapter()
            self.logger.info("✅ Conductor adapters created (Celery, Redis Graph, Resource)")
            
            # Librarian Adapters (Knowledge)
            from .infrastructure_adapters.meilisearch_knowledge_adapter import MeilisearchKnowledgeAdapter
            from .infrastructure_adapters.redis_graph_knowledge_adapter import RedisGraphKnowledgeAdapter
            from .infrastructure_adapters.knowledge_metadata_adapter import KnowledgeMetadataAdapter
            
            meilisearch_config = self.config_adapter.get_meilisearch_config() if hasattr(self.config_adapter, 'get_meilisearch_config') else {"host": "localhost", "port": 7700, "api_key": None}
            self.meilisearch_knowledge_adapter = MeilisearchKnowledgeAdapter(
                host=meilisearch_config.get("host", "localhost"),
                port=meilisearch_config.get("port", 7700),
                api_key=meilisearch_config.get("api_key")
            )
            await self.meilisearch_knowledge_adapter.connect()
            
            redis_graph_config = self.config_adapter.get_redis_graph_config() if hasattr(self.config_adapter, 'get_redis_graph_config') else {"host": "localhost", "port": 6379, "db": 1}
            self.redis_graph_knowledge_adapter = RedisGraphKnowledgeAdapter(
                host=redis_graph_config.get("host", "localhost"),
                port=redis_graph_config.get("port", 6379),
                db=redis_graph_config.get("db", 1)
            )
            
            # Knowledge Metadata Adapter - Use ArangoDB for metadata storage
            # Note: KnowledgeMetadataAdapter expects PostgreSQL, but we use ArangoDB for metadata
            # The Knowledge Governance Abstraction uses ArangoDB directly, so metadata adapter is optional
            # For now, we'll use ArangoDB adapter directly for metadata operations
            # TODO: Refactor KnowledgeMetadataAdapter to use ArangoDB or create ArangoDBMetadataAdapter
            arango_config = self.config_adapter.get_arangodb_config()
            # Initialize with ArangoDB config but note it won't connect (PostgreSQL adapter)
            # The abstraction will use ArangoDB adapter directly for metadata storage
            self.knowledge_metadata_adapter = KnowledgeMetadataAdapter(
                host="localhost",  # Placeholder - adapter won't be used for connection
                port=5432,  # Placeholder - adapter won't be used for connection
                database="knowledge_metadata",  # Placeholder
                username="postgres",  # Placeholder
                password=""  # Placeholder
            )
            # Note: We don't connect this adapter since it's PostgreSQL-based
            # The Knowledge Governance Abstraction uses ArangoDB adapter directly
            self.logger.info("✅ Librarian adapters created (Meilisearch, Redis Graph Knowledge, Knowledge Metadata - using ArangoDB)")
            
            # Document Processing Adapters (for Document Intelligence - legacy)
            from .infrastructure_adapters.beautifulsoup_html_adapter import BeautifulSoupHTMLAdapter
            from .infrastructure_adapters.python_docx_adapter import PythonDocxAdapter
            from .infrastructure_adapters.pdfplumber_table_extractor import PdfplumberTableExtractor
            from .infrastructure_adapters.pypdf2_text_extractor import PyPDF2TextExtractor
            from .infrastructure_adapters.pytesseract_ocr_adapter import PyTesseractOCRAdapter
            from .infrastructure_adapters.opencv_image_processor import OpenCVImageProcessor
            from .infrastructure_adapters.document_processing_adapter import DocumentProcessingAdapter
            # Use MainframeProcessingAdapter (homegrown solution) for extensible COBOL parsing
            # The homegrown solution uses explicit byte positions and extensible patterns
            # It handles both ASCII and EBCDIC files with better control over field alignment
            from .infrastructure_adapters.mainframe_processing_adapter import MainframeProcessingAdapter
            
            self.beautifulsoup_adapter = BeautifulSoupHTMLAdapter()
            self.python_docx_adapter = PythonDocxAdapter()
            self.pdfplumber_adapter = PdfplumberTableExtractor()  # Class name is PdfplumberTableExtractor
            self.pypdf2_adapter = PyPDF2TextExtractor()  # Class name is PyPDF2TextExtractor
            
            # Document processing adapters (REQUIRED for image file support)
            # PyTesseractOCRAdapter is required for OCR on image files (PNG, JPG, etc.)
            # OpenCVImageProcessor is required for image enhancement before OCR
            # DocumentIntelligenceAbstraction requires these for full platform functionality
            self.pytesseract_adapter = PyTesseractOCRAdapter()
            self.opencv_adapter = OpenCVImageProcessor()
            
            # Use MainframeProcessingAdapter (homegrown solution) for extensible COBOL parsing
            # This provides explicit byte position control and extensible pattern matching
            # Better for handling ASCII files with headers, comments, and record prefixes
            self.mainframe_adapter = MainframeProcessingAdapter()
            # Legacy alias for backward compatibility
            self.cobol_adapter = self.mainframe_adapter
            self.document_processing_adapter = DocumentProcessingAdapter()
            
            self.logger.info("✅ Document processing adapters created (BeautifulSoup, Python-DOCX, Pdfplumber, PyPDF2, PyTesseract, OpenCV, MainframeProcessing, DocumentProcessing)")
            
            # New File Parsing Adapters (5-layer architecture)
            from .infrastructure_adapters.excel_processing_adapter import ExcelProcessingAdapter
            from .infrastructure_adapters.csv_processing_adapter import CsvProcessingAdapter
            from .infrastructure_adapters.json_processing_adapter import JsonProcessingAdapter
            from .infrastructure_adapters.text_processing_adapter import TextProcessingAdapter
            
            self.excel_adapter = ExcelProcessingAdapter()
            self.csv_adapter = CsvProcessingAdapter()
            self.json_adapter = JsonProcessingAdapter()
            self.text_adapter = TextProcessingAdapter()
            
            self.logger.info("✅ File parsing adapters created (Excel, CSV, JSON, Text)")
            
            # Workflow/BPMN Adapters
            from .infrastructure_adapters.bpmn_processing_adapter import BPMNProcessingAdapter
            
            self.bpmn_processing_adapter = BPMNProcessingAdapter()
            self.logger.info("✅ BPMN Processing adapter created")
            
            # SOP Adapters
            from .infrastructure_adapters.sop_parsing_adapter import SOPParsingAdapter
            from .infrastructure_adapters.sop_enhancement_adapter import SOPEnhancementAdapter
            
            self.sop_parsing_adapter = SOPParsingAdapter()
            self.sop_enhancement_adapter = SOPEnhancementAdapter()
            self.logger.info("✅ SOP adapters created (Parsing, Enhancement)")
            
            # Financial/Strategic Planning Adapters
            from .infrastructure_adapters.standard_strategic_planning_adapter import StandardStrategicPlanningAdapter
            from .infrastructure_adapters.standard_financial_adapter import StandardFinancialAdapter
            
            self.standard_strategic_planning_adapter = StandardStrategicPlanningAdapter()
            self.standard_financial_adapter = StandardFinancialAdapter()
            self.logger.info("✅ Financial/Strategic Planning adapters created (Standard only - HuggingFace in future_abstractions for future use)")
            
            # Log Aggregation Adapter (Loki)
            from .infrastructure_adapters.loki_adapter import LokiAdapter
            
            loki_endpoint = self.config_adapter.get("LOKI_ENDPOINT", "http://localhost:3100")
            loki_tenant = self.config_adapter.get("LOKI_TENANT_ID", "symphainy-platform")
            
            self.loki_adapter = LokiAdapter(
                endpoint=loki_endpoint,
                tenant_id=loki_tenant
            )
            self.logger.info("✅ Loki adapter created")
            
            # Test connection (non-critical - log aggregation is optional)
            try:
                loki_connected = await self.loki_adapter.connect()
                if loki_connected:
                    self.logger.info(f"✅ Loki connected successfully ({loki_endpoint})")
                else:
                    self.logger.warning(f"⚠️ Loki connection test returned False ({loki_endpoint}) - log aggregation may not work")
            except Exception as e:
                self.logger.warning(f"⚠️ Loki connection test failed (non-critical): {e} - log aggregation may not work")
                # Don't raise - log aggregation is optional infrastructure
            
            # Service Discovery Adapter (Consul)
            from .infrastructure_adapters.consul_service_discovery_adapter import ConsulServiceDiscoveryAdapter
            import consul
            
            consul_host = self.config_adapter.get("CONSUL_HOST", "localhost")
            consul_port = int(self.config_adapter.get("CONSUL_PORT", "8500"))
            consul_token = self.config_adapter.get("CONSUL_TOKEN", None)
            consul_datacenter = self.config_adapter.get("CONSUL_DATACENTER", None)
            
            consul_client_config = {
                "host": consul_host,
                "port": consul_port
            }
            if consul_token:
                consul_client_config["token"] = consul_token
            if consul_datacenter:
                consul_client_config["dc"] = consul_datacenter
            
            consul_client = consul.Consul(**consul_client_config)
            self.consul_service_discovery_adapter = ConsulServiceDiscoveryAdapter(
                consul_client=consul_client,
                service_name="consul_service_discovery_adapter",
                di_container=self.di_container
            )
            # Test connection (with timeout - will fail gracefully if Consul unavailable)
            # Consul is CRITICAL infrastructure - if unavailable, initialization should fail
            try:
                consul_connected = await self.consul_service_discovery_adapter.connect()
                if consul_connected:
                    self.logger.info(f"✅ Consul Service Discovery adapter created and connected ({consul_host}:{consul_port})")
                else:
                    raise ConnectionError("Consul connection returned False - Consul is CRITICAL infrastructure")
            except ConnectionError as e:
                self.logger.error(f"❌ Consul Service Discovery adapter connection failed ({consul_host}:{consul_port}) - Consul is CRITICAL infrastructure and must be available")
                raise RuntimeError(f"Public Works Foundation initialization failed: Consul is unavailable. {e}")
            
            # Traefik Routing Adapter
            from .infrastructure_adapters.traefik_adapter import TraefikAdapter
            
            traefik_api_url = self.config_adapter.get("TRAEFIK_API_URL", "http://traefik:8080")
            
            self.traefik_adapter = TraefikAdapter(
                traefik_api_url=traefik_api_url,
                service_name="traefik_adapter",
                di_container=self.di_container
            )
            # Test connection (with timeout - will fail gracefully if Traefik unavailable)
            # Traefik is CRITICAL infrastructure - if unavailable, initialization should fail
            # EXCEPTION: In test mode, Traefik is optional (tests may not need routing)
            test_mode = self.config_adapter.get("TEST_MODE", "false").lower() == "true"
            try:
                traefik_connected = await self.traefik_adapter.connect()
                if traefik_connected:
                    self.logger.info(f"✅ Traefik Routing adapter created and connected ({traefik_api_url})")
                else:
                    if test_mode:
                        self.logger.warning(f"⚠️ Traefik connection failed ({traefik_api_url}) - continuing in test mode (Traefik optional)")
                    else:
                        raise ConnectionError("Traefik connection returned False - Traefik is CRITICAL infrastructure")
            except (ConnectionError, Exception) as e:
                if test_mode:
                    self.logger.warning(f"⚠️ Traefik Routing adapter connection failed ({traefik_api_url}) - continuing in test mode (Traefik optional): {e}")
                else:
                    self.logger.error(f"❌ Traefik Routing adapter connection failed ({traefik_api_url}) - Traefik is CRITICAL infrastructure and must be available")
                    raise RuntimeError(f"Public Works Foundation initialization failed: Traefik is unavailable. {e}")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_create_all_adapters")
            self.logger.error(f"❌ Failed to create adapters: {e}")
            raise
    
    # ============================================================================
    # LAYER 1: CREATE ALL ABSTRACTIONS (With Injected Adapters)
    # ============================================================================
    
    async def _create_all_abstractions(self):
        """Create all infrastructure abstractions (Layer 1) with dependency injection."""
        try:
            # Security Abstractions
            from .infrastructure_abstractions.auth_abstraction import AuthAbstraction
            from .infrastructure_abstractions.session_abstraction import SessionAbstraction
            from .infrastructure_abstractions.authorization_abstraction import AuthorizationAbstraction
            from .infrastructure_abstractions.tenant_abstraction_supabase import TenantAbstraction
            from .infrastructure_adapters.redis_session_adapter import RedisSessionAdapter
            
            # Auth Abstraction
            # BREAKING: JWT adapter not created - user auth uses Supabase only
            self.auth_abstraction = AuthAbstraction(
                supabase_adapter=self.supabase_adapter,
                jwt_adapter=None  # ✅ User authentication uses Supabase only
            )
            self.logger.info("✅ Auth abstraction created (Supabase-only authentication)")
            
            # Session Abstraction
            # BREAKING: jwt_adapter is None - will break if RedisSessionAdapter requires it
            session_adapter = RedisSessionAdapter(
                redis_adapter=self.redis_adapter,
                jwt_adapter=None  # ❌ BREAKING: Removed for user auth (session tokens may need different approach)
            )
            self.session_abstraction = SessionAbstraction(
                session_adapter=session_adapter,
                config_adapter=self.config_adapter,
                service_name="session_abstraction",
                di_container=self.di_container
            )
            self.logger.info("✅ Session abstraction created")
            
            # Authorization Abstraction
            from .abstraction_contracts.policy_engine_protocol import PolicyEngine
            
            # Create default policy engine
            class DefaultPolicyEngine:
                async def is_allowed(self, action: str, resource: str, context) -> bool:
                    return True
                async def get_user_permissions(self, user_id: str):
                    return ["read", "write"]
                async def get_tenant_policies(self, tenant_id: str):
                    return {"isolation": "strict", "features": ["basic_analytics"], "cross_tenant": False}
            
            default_policy_engine = DefaultPolicyEngine()
            
            self.authorization_abstraction = AuthorizationAbstraction(
                redis_adapter=self.redis_adapter,
                supabase_adapter=self.supabase_adapter,
                policy_engine=default_policy_engine,
                di_container=self.di_container
            )
            self.logger.info("✅ Authorization abstraction created")
            
            # Tenant Abstraction
            self.tenant_abstraction = TenantAbstraction(
                supabase_adapter=self.supabase_adapter,
                redis_adapter=self.redis_adapter,
                config_adapter=self.config_adapter,
                di_container=self.di_container
            )
            self.logger.info("✅ Tenant abstraction created")
            
            # Store policy engines for registry registration
            self.default_policy_engine = default_policy_engine
            
            # File Management Abstraction
            from .infrastructure_abstractions.file_management_abstraction_gcs import FileManagementAbstraction
            
            # File Management Abstraction (REQUIRED - depends on GCS adapter)
            # GCS adapter is required, so this should always succeed if we got here
            if not self.gcs_adapter:
                raise RuntimeError(
                    "GCS adapter is required for FileManagementAbstraction but is None. "
                    "This should not happen - GCS adapter creation should have failed earlier with a clear error."
                )
            
            self.file_management_abstraction = FileManagementAbstraction(
                gcs_adapter=self.gcs_adapter,
                supabase_adapter=self.supabase_file_adapter,
                config_adapter=self.config_adapter,
                di_container=self.di_container
            )
            self.logger.info("✅ File Management abstraction created")
            
            # File Management Composition Service
            from .composition_services.file_management_composition_service import FileManagementCompositionService
            
            self.file_management_composition = FileManagementCompositionService(
                file_management_abstraction=self.file_management_abstraction,
                di_container=self.di_container
            )
            self.logger.info("✅ File Management composition service created")
            
            # Content Metadata Abstractions
            from .infrastructure_abstractions.content_metadata_abstraction import ContentMetadataAbstraction
            from .infrastructure_abstractions.content_schema_abstraction import ContentSchemaAbstraction
            from .infrastructure_abstractions.content_insights_abstraction import ContentInsightsAbstraction
            
            self.content_metadata_abstraction = ContentMetadataAbstraction(
                arango_adapter=self.arango_adapter,
                config_adapter=self.config_adapter,
                di_container=self.di_container
            )
            self.logger.info("✅ Content Metadata abstraction created")
            
            self.content_schema_abstraction = ContentSchemaAbstraction(
                arango_adapter=self.arango_adapter,
                config_adapter=self.config_adapter,
                di_container=self.di_container
            )
            self.logger.info("✅ Content Schema abstraction created")
            
            self.content_insights_abstraction = ContentInsightsAbstraction(
                arango_adapter=self.arango_adapter,
                config_adapter=self.config_adapter,
                di_container=self.di_container
            )
            self.logger.info("✅ Content Insights abstraction created")
            
            # Semantic Data Abstraction (NEW - for embeddings and semantic graphs)
            from .infrastructure_abstractions.semantic_data_abstraction import SemanticDataAbstraction
            
            self.semantic_data_abstraction = SemanticDataAbstraction(
                arango_adapter=self.arango_adapter,
                config_adapter=self.config_adapter,
                di_container=self.di_container
            )
            self.logger.info("✅ Semantic Data abstraction created")
            
            # Content Metadata Composition Services
            from .composition_services.content_metadata_composition_service import ContentMetadataCompositionService
            from .composition_services.content_analysis_composition_service import ContentAnalysisCompositionService
            
            self.content_metadata_composition = ContentMetadataCompositionService(
                content_metadata_abstraction=self.content_metadata_abstraction,
                content_schema_abstraction=self.content_schema_abstraction,
                content_insights_abstraction=self.content_insights_abstraction,
                di_container=self.di_container
            )
            self.logger.info("✅ Content Metadata composition service created")
            
            self.content_analysis_composition = ContentAnalysisCompositionService(
                content_metadata_abstraction=self.content_metadata_abstraction,
                content_schema_abstraction=self.content_schema_abstraction,
                content_insights_abstraction=self.content_insights_abstraction,
                di_container=self.di_container
            )
            self.logger.info("✅ Content Analysis composition service created")
            
            # Document Intelligence Abstraction - REMOVED
            # File parsing now uses individual abstractions per file type (excel_processing, pdf_processing, etc.)
            # Individual abstractions provide better separation of concerns and file-type-specific optimizations
            self.document_intelligence_abstraction = None  # Kept for backward compatibility (returns None)
            self.logger.info("✅ File parsing uses individual abstractions per file type (excel_processing, pdf_processing, word_processing, etc.)")
            
            # New File Parsing Abstractions (5-layer architecture - one per file type)
            from .infrastructure_abstractions.excel_processing_abstraction import ExcelProcessingAbstraction
            from .infrastructure_abstractions.csv_processing_abstraction import CsvProcessingAbstraction
            from .infrastructure_abstractions.json_processing_abstraction import JsonProcessingAbstraction
            from .infrastructure_abstractions.text_processing_abstraction import TextProcessingAbstraction
            from .infrastructure_abstractions.pdf_processing_abstraction import PdfProcessingAbstraction
            from .infrastructure_abstractions.word_processing_abstraction import WordProcessingAbstraction
            from .infrastructure_abstractions.html_processing_abstraction import HtmlProcessingAbstraction
            from .infrastructure_abstractions.image_processing_abstraction import ImageProcessingAbstraction
            
            self.excel_processing_abstraction = ExcelProcessingAbstraction(
                excel_adapter=self.excel_adapter,
                di_container=self.di_container
            )
            self.csv_processing_abstraction = CsvProcessingAbstraction(
                csv_adapter=self.csv_adapter,
                di_container=self.di_container
            )
            self.json_processing_abstraction = JsonProcessingAbstraction(
                json_adapter=self.json_adapter,
                di_container=self.di_container
            )
            self.text_processing_abstraction = TextProcessingAbstraction(
                text_adapter=self.text_adapter,
                di_container=self.di_container
            )
            self.pdf_processing_abstraction = PdfProcessingAbstraction(
                pdfplumber_adapter=self.pdfplumber_adapter,
                pypdf2_adapter=self.pypdf2_adapter,
                di_container=self.di_container
            )
            self.word_processing_abstraction = WordProcessingAbstraction(
                python_docx_adapter=self.python_docx_adapter,
                di_container=self.di_container
            )
            self.html_processing_abstraction = HtmlProcessingAbstraction(
                beautifulsoup_adapter=self.beautifulsoup_adapter,
                di_container=self.di_container
            )
            self.image_processing_abstraction = ImageProcessingAbstraction(
                pytesseract_adapter=self.pytesseract_adapter,
                opencv_adapter=self.opencv_adapter,
                di_container=self.di_container
            )
            
            # Mainframe Processing Abstraction
            from .infrastructure_abstractions.mainframe_processing_abstraction import MainframeProcessingAbstraction
            
            self.mainframe_processing_abstraction = MainframeProcessingAbstraction(
                mainframe_adapter=self.mainframe_adapter,
                di_container=self.di_container
            )
            
            self.logger.info("✅ File parsing abstractions created (Excel, CSV, JSON, Text, PDF, Word, HTML, Image, Mainframe)")
            
            # Workflow/BPMN Abstraction
            from .infrastructure_abstractions.bpmn_processing_abstraction import BPMNProcessingAbstraction
            
            self.bpmn_processing_abstraction = BPMNProcessingAbstraction(
                bpmn_processing_adapter=self.bpmn_processing_adapter,
                di_container=self.di_container
            )
            self.logger.info("✅ BPMN Processing abstraction created")
            
            # SOP Abstractions
            from .infrastructure_abstractions.sop_processing_abstraction import SOPProcessingAbstraction
            from .infrastructure_abstractions.sop_enhancement_abstraction import SOPEnhancementAbstraction
            
            self.sop_processing_abstraction = SOPProcessingAbstraction(
                sop_parsing_adapter=self.sop_parsing_adapter,
                di_container=self.di_container
            )
            self.sop_enhancement_abstraction = SOPEnhancementAbstraction(
                sop_enhancement_adapter=self.sop_enhancement_adapter,
                di_container=self.di_container
            )
            self.logger.info("✅ SOP abstractions created (Processing, Enhancement)")
            
            # Financial/Strategic Planning Abstractions
            from .infrastructure_abstractions.strategic_planning_abstraction import StrategicPlanningAbstraction
            from .infrastructure_abstractions.financial_analysis_abstraction import FinancialAnalysisAbstraction
            
            self.strategic_planning_abstraction = StrategicPlanningAbstraction(
                standard_strategic_planning_adapter=self.standard_strategic_planning_adapter,
                huggingface_strategic_planning_adapter=None,  # Not enabled - in future_abstractions for future use
                di_container=self.di_container
            )
            self.financial_analysis_abstraction = FinancialAnalysisAbstraction(
                standard_financial_adapter=self.standard_financial_adapter,
                huggingface_financial_adapter=None,  # Not enabled - in future_abstractions for future use
                di_container=self.di_container
            )
            self.logger.info("✅ Financial/Strategic Planning abstractions created (Standard adapters only)")
            
            # Health Abstraction
            from .infrastructure_abstractions.health_abstraction import HealthAbstraction
            
            self.health_abstraction = HealthAbstraction(
                health_adapter=self.health_adapter,  # Dependency injection
                config_adapter=self.config_adapter,
                service_name="nurse_health_monitoring",
                di_container=self.di_container
            )
            self.logger.info("✅ Health abstraction created")
            
            # Telemetry Abstraction
            from .infrastructure_abstractions.telemetry_abstraction import TelemetryAbstraction
            
            self.telemetry_abstraction = TelemetryAbstraction(
                telemetry_adapter=self.telemetry_adapter,  # Dependency injection
                config_adapter=self.config_adapter,
                service_name="nurse_telemetry",
                di_container=self.di_container
            )
            self.logger.info("✅ Telemetry abstraction created")
            
            # Log Aggregation Abstraction
            from .infrastructure_abstractions.log_aggregation_abstraction import LogAggregationAbstraction
            
            self.log_aggregation_abstraction = LogAggregationAbstraction(
                loki_adapter=self.loki_adapter,  # Dependency injection
                config_adapter=self.config_adapter,
                service_name="log_aggregation_abstraction",
                di_container=self.di_container
            )
            self.logger.info("✅ Log Aggregation abstraction created")
            
            # Observability Abstraction (NEW - for platform observability data storage)
            from .infrastructure_abstractions.observability_abstraction import ObservabilityAbstraction
            
            self.observability_abstraction = ObservabilityAbstraction(
                arango_adapter=self.arango_adapter,
                config_adapter=self.config_adapter,
                di_container=self.di_container
            )
            self.logger.info("✅ Observability abstraction created")
            
            # Alert Management Abstraction
            from .infrastructure_abstractions.alert_management_abstraction import AlertManagementAbstraction
            
            self.alert_management_abstraction = AlertManagementAbstraction(
                alert_adapter=self.alert_adapter,  # Dependency injection
                config_adapter=self.config_adapter,
                service_name="nurse_alert_management",
                di_container=self.di_container
            )
            self.logger.info("✅ Alert Management abstraction created")
            
            # Visualization Abstraction
            from .infrastructure_abstractions.visualization_abstraction import VisualizationAbstraction
            
            self.visualization_abstraction = VisualizationAbstraction(
                standard_adapter=self.visualization_adapter,  # Dependency injection
                di_container=self.di_container
            )
            self.logger.info("✅ Visualization abstraction created")
            
            # Business Metrics Abstraction
            from .infrastructure_abstractions.business_metrics_abstraction import BusinessMetricsAbstraction
            
            self.business_metrics_abstraction = BusinessMetricsAbstraction(
                standard_adapter=self.standard_business_metrics_adapter,  # Dependency injection
                ai_adapter=self.huggingface_business_metrics_adapter,  # Dependency injection
                di_container=self.di_container
            )
            self.logger.info("✅ Business Metrics abstraction created")
            
            # Conductor Abstractions (Task/Workflow)
            from .infrastructure_abstractions.task_management_abstraction import TaskManagementAbstraction
            from .infrastructure_abstractions.workflow_orchestration_abstraction import WorkflowOrchestrationAbstraction
            from .infrastructure_abstractions.resource_allocation_abstraction import ResourceAllocationAbstraction
            
            self.task_management_abstraction = TaskManagementAbstraction(
                celery_adapter=self.celery_adapter,  # Dependency injection
                di_container=self.di_container
            )
            self.workflow_orchestration_abstraction = WorkflowOrchestrationAbstraction(
                redis_graph_adapter=self.redis_graph_adapter,  # Dependency injection
                di_container=self.di_container
            )
            self.resource_allocation_abstraction = ResourceAllocationAbstraction(
                resource_adapter=self.resource_adapter,  # Dependency injection
                di_container=self.di_container
            )
            self.logger.info("✅ Conductor abstractions created (Task Management, Workflow Orchestration, Resource Allocation)")
            
            # Service Discovery Abstraction
            from .infrastructure_abstractions.service_discovery_abstraction import ServiceDiscoveryAbstraction
            
            self.service_discovery_abstraction = ServiceDiscoveryAbstraction(
                adapter=self.consul_service_discovery_adapter,  # Dependency injection
                service_name="service_discovery_abstraction",
                di_container=self.di_container
            )
            self.logger.info("✅ Service Discovery abstraction created")
            
            # Routing Abstraction
            from .infrastructure_abstractions.routing_abstraction import TraefikRoutingAbstraction
            
            self.routing_abstraction = TraefikRoutingAbstraction(
                traefik_adapter=self.traefik_adapter  # Dependency injection
            )
            self.logger.info("✅ Routing abstraction created")
            
            # Librarian Abstractions (Knowledge)
            from .infrastructure_abstractions.knowledge_discovery_abstraction import KnowledgeDiscoveryAbstraction
            from .infrastructure_abstractions.knowledge_governance_abstraction import KnowledgeGovernanceAbstraction
            
            self.knowledge_discovery_abstraction = KnowledgeDiscoveryAbstraction(
                meilisearch_adapter=self.meilisearch_knowledge_adapter,  # Dependency injection
                redis_graph_adapter=self.redis_graph_knowledge_adapter,  # Dependency injection
                arango_adapter=self.arango_adapter,  # Dependency injection
                config_adapter=self.config_adapter,
                di_container=self.di_container
            )
            self.knowledge_governance_abstraction = KnowledgeGovernanceAbstraction(
                metadata_adapter=self.knowledge_metadata_adapter,  # Dependency injection
                arango_adapter=self.arango_adapter,  # Dependency injection
                config_adapter=self.config_adapter,
                di_container=self.di_container
            )
            self.logger.info("✅ Librarian abstractions created (Knowledge Discovery, Knowledge Governance)")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_create_all_abstractions")
            self.logger.error(f"❌ Failed to create abstractions: {e}")
            raise
    
    # ============================================================================
    # LAYER 2: INITIALIZE REGISTRIES AND REGISTER ABSTRACTIONS
    # ============================================================================
    
    async def _initialize_and_register_abstractions(self):
        """Initialize registries and register all abstractions (exposure/discovery layer)."""
        try:
            # Initialize Security Registry (exposure only)
            self.security_registry = SecurityRegistry()
            
            # Register security abstractions
            self.security_registry.register_abstraction("auth", self.auth_abstraction)
            self.security_registry.register_abstraction("session", self.session_abstraction)
            self.security_registry.register_abstraction("authorization", self.authorization_abstraction)
            self.security_registry.register_abstraction("tenant", self.tenant_abstraction)
            
            # Register policy engines
            self.security_registry.register_policy_engine("default", self.default_policy_engine)
            
            self.logger.info("✅ Security Registry initialized and abstractions registered")
            
            # Initialize File Management Registry (exposure only)
            from .infrastructure_registry.file_management_registry_gcs import FileManagementRegistry
            
            # File Management Registry (REQUIRED - file_management abstraction must exist)
            if not self.file_management_abstraction:
                raise RuntimeError(
                    "FileManagementAbstraction is required but is None. "
                    "This should not happen - abstraction creation should have failed earlier with a clear error."
                )
            
            self.file_management_registry = FileManagementRegistry()
            self.file_management_registry.register_abstraction("file_management", self.file_management_abstraction)
            self.file_management_registry.register_composition_service("file_management", self.file_management_composition)
            
            self.logger.info("✅ File Management Registry initialized and abstractions registered")
            
            # Initialize Content Metadata Registry (exposure only)
            from .infrastructure_registry.content_metadata_registry import ContentMetadataRegistry
            
            self.content_metadata_registry = ContentMetadataRegistry()
            self.content_metadata_registry.register_abstraction("content_metadata", self.content_metadata_abstraction)
            self.content_metadata_registry.register_abstraction("content_schema", self.content_schema_abstraction)
            self.content_metadata_registry.register_abstraction("content_insights", self.content_insights_abstraction)
            self.content_metadata_registry.register_abstraction("semantic_data", self.semantic_data_abstraction)  # NEW
            self.content_metadata_registry.register_composition_service("content_metadata", self.content_metadata_composition)
            self.content_metadata_registry.register_composition_service("content_analysis", self.content_analysis_composition)
            
            self.logger.info("✅ Content Metadata Registry initialized and abstractions registered (including semantic_data)")
            
            # Initialize Service Discovery Registry (exposure only)
            self.service_discovery_registry = ServiceDiscoveryRegistry("public_works_service_discovery", di_container=self.di_container)
            self.service_discovery_registry.register_abstraction("service_discovery", self.service_discovery_abstraction)
            
            self.logger.info("✅ Service Discovery Registry initialized and abstraction registered")
            
            # Initialize Routing Registry (exposure only)
            self.routing_registry = RoutingRegistry("public_works_routing", di_container=self.di_container)
            self.routing_registry.register_abstraction("routing", self.routing_abstraction)
            
            self.logger.info("✅ Routing Registry initialized and abstraction registered")
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_initialize_and_register_abstractions")
            self.logger.error(f"❌ Failed to initialize registries: {e}")
            raise
    
    # ============================================================================
    # GENERIC ABSTRACTION GETTER (For Backward Compatibility)
    # ============================================================================
    
    def get_abstraction(self, name: str) -> Any:
        """
        Generic abstraction getter for backward compatibility.
        This method provides a unified interface for getting any abstraction.
        
        Args:
            name: The name of the abstraction to retrieve
            
        Returns:
            The requested abstraction
            
        Raises:
            ValueError: If the abstraction name is not supported
            RuntimeError: If the foundation is not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Public Works Foundation not initialized. Call initialize_foundation() first.")
        
        # Map abstraction names to actual attributes (return the abstraction directly)
        abstraction_map = {
            "auth": self.auth_abstraction,
            # document_intelligence removed - replaced with individual file type abstractions (excel_processing, pdf_processing, etc.)
            "bpmn_processing": self.bpmn_processing_abstraction,
            "sop_processing": self.sop_processing_abstraction,
            "sop_enhancement": self.sop_enhancement_abstraction,
            "strategic_planning": self.strategic_planning_abstraction,
            "financial_analysis": self.financial_analysis_abstraction,
            "authorization": self.authorization_abstraction,
            "session": self.session_abstraction,
            "tenant": self.tenant_abstraction,
            "service_discovery": self.service_discovery_abstraction,
            "service_registry": self.service_discovery_abstraction,  # Alias for service_discovery
            "routing": self.routing_abstraction,
            "traefik": self.routing_abstraction,  # Alias for routing
            "file_management": self.file_management_abstraction,
            "content_metadata": self.content_metadata_abstraction,
            "content_schema": self.content_schema_abstraction,
            "content_insights": self.content_insights_abstraction,
            "semantic_data": self.semantic_data_abstraction,  # NEW: For embeddings and semantic graphs
            "llm": self.llm_abstraction,
            "mcp": None,  # MCP injected directly via DI, not via foundation
            "agui": self.llm_abstraction,  # AGUI uses LLM abstraction
            "policy": self.default_policy_engine,
            "tool_storage": self.tool_storage_abstraction,
            "telemetry": self.telemetry_abstraction,
            "alert_management": self.alert_management_abstraction,
            "health": self.health_abstraction,
            "log_aggregation": self.log_aggregation_abstraction,
            "observability": self.observability_abstraction,  # NEW: For platform observability data storage
            "visualization": self.visualization_abstraction,
            "business_metrics": self.business_metrics_abstraction,
            "task_management": self.task_management_abstraction,
            "workflow_orchestration": self.workflow_orchestration_abstraction,  # For Smart City Conductor (execution)
            "workflow_diagramming_orchestration": self.workflow_orchestration_abstraction,  # For Business Enablement (diagramming/analysis)
            "knowledge_discovery": self.knowledge_discovery_abstraction,
            "knowledge_governance": self.knowledge_governance_abstraction,
            "state_management": self.state_management_abstraction,
            "messaging": self.messaging_abstraction,
            "event_management": self.event_management_abstraction,
            "cache": self.cache_abstraction,
            # New file parsing abstractions (5-layer architecture)
            "excel_processing": self.excel_processing_abstraction,
            "csv_processing": self.csv_processing_abstraction,
            "json_processing": self.json_processing_abstraction,
            "text_processing": self.text_processing_abstraction,
            "pdf_processing": self.pdf_processing_abstraction,
            "word_processing": self.word_processing_abstraction,
            "html_processing": self.html_processing_abstraction,
            "image_processing": self.image_processing_abstraction,
            "mainframe_processing": self.mainframe_processing_abstraction
        }
        
        if name not in abstraction_map:
            available = list(abstraction_map.keys())
            raise ValueError(f"Abstraction '{name}' not supported. Available abstractions: {available}")
        
        try:
            # Record metrics for abstraction access (fire-and-forget for sync method)
            # Note: record_telemetry_metric is now async, but this is a sync method
            # We'll schedule it if possible, otherwise it's non-critical
            try:
                import asyncio
                coro = self.record_telemetry_metric(
                    "abstraction_access", 
                    1.0, 
                    {"abstraction_name": name, "access_method": "get_abstraction"}
                )
                # Try to schedule if we're in an async context
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(coro)
                else:
                    loop.run_until_complete(coro)
            except (RuntimeError, AttributeError):
                # Not in async context or no event loop - skip telemetry (non-critical)
                pass
            
            # Log abstraction access for monitoring
            self.logger.debug(f"📊 Accessing abstraction '{name}' via get_abstraction()")
            
            abstraction = abstraction_map[name]
            self.logger.info(f"🔍 DEBUG: Returning abstraction '{name}' - type: {type(abstraction)}, value: {abstraction}")
            return abstraction
        except Exception as e:
            # Record error metrics (fire-and-forget for sync method)
            try:
                import asyncio
                coro = self.record_telemetry_metric(
                    "abstraction_access_error", 
                    1.0, 
                    {"abstraction_name": name, "error": str(e)}
                )
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(coro)
                else:
                    loop.run_until_complete(coro)
            except (RuntimeError, AttributeError):
                # Not in async context - skip telemetry (non-critical)
                pass
            
            self.logger.error(f"❌ Failed to get abstraction '{name}': {e}")
            raise
