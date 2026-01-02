#!/usr/bin/env python3
"""
Realm Service Base Class

Simplified base class for realm services that composes focused mixins.
Implements RealmServiceProtocol with clean, composable architecture.

WHAT (Realm Service Role): I provide the foundation for all realm services
HOW (Realm Service): I compose 6 mixins for comprehensive realm capabilities
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC
import uuid

from bases.protocols.realm_service_protocol import RealmServiceProtocol
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.infrastructure_access_mixin import InfrastructureAccessMixin
from bases.mixins.security_mixin import SecurityMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin
from bases.mixins.platform_capabilities_mixin import PlatformCapabilitiesMixin
from bases.mixins.communication_mixin import CommunicationMixin
from bases.mixins.micro_module_support_mixin import MicroModuleSupportMixin
from bases.startup_policy import StartupPolicy


class RealmServiceBase(
    RealmServiceProtocol,
    UtilityAccessMixin,
    InfrastructureAccessMixin,
    SecurityMixin,
    PerformanceMonitoringMixin,
    PlatformCapabilitiesMixin,
    CommunicationMixin,
    MicroModuleSupportMixin,
    ABC
):
    """
    Realm Service Base Class - Simplified Foundation for ALL Realm Services
    
    Composes 6 focused mixins to provide comprehensive realm capabilities with
    controlled access to Public Works abstractions through Platform Gateway.
    
    ARCHITECTURE PATTERNS (PLEASE READ - CRITICAL FOR PROPER IMPLEMENTATION):
    
    1. ABSTRACTION ACCESS (via Platform Gateway):
       ```python
       # ✅ CORRECT: Get abstractions through validated Platform Gateway
       self.file_management = self.get_abstraction("file_management")
       self.content_metadata = self.get_abstraction("content_metadata")
       
       # ❌ WRONG: Direct DI Container access (bypasses validation)
        self.file_management = self.get_abstraction("file_management")
       ```
    
    2. SMART CITY SERVICE DISCOVERY (via Curator):
       ```python
       # ✅ CORRECT: Discover Smart City services via convenience methods
       self.librarian = await self.get_librarian_api()
       self.content_steward = await self.get_content_steward_api()
       self.data_steward = await self.get_data_steward_api()
       
       # ❌ WRONG: Direct Communication Foundation access
       await self.communication_foundation.send_message(...)
       ```
    
    3. SOA API PATTERN (3-5 core capabilities per service):
       ```python
       # ✅ CORRECT: Define clear, atomic SOA APIs
       async def parse_file(self, file_path: str, format: str) -> ParsedDocument:
           '''Parse file into structured format (SOA API).'''
           # Complete implementation using Smart City services
           librarian = await self.get_librarian_api()
           content_steward = await self.get_content_steward_api()
           # ... orchestrate and return result
       ```
    
    4. USE SMART CITY SERVICES (Don't Reinvent):
       ```python
       # ✅ CORRECT: Use helper methods that delegate to Smart City
       result = await self.store_document(document_data, metadata)
       validated = await self.validate_data_quality(data, rules)
       workflow_result = await self.orchestrate_workflow(workflow_def)
       
       # ❌ WRONG: Custom implementations (spaghetti code)
       with open(f"/tmp/{file}", "w") as f:  # Custom storage
           f.write(data)
       ```
    
    5. CURATOR REGISTRATION (standardized):
       ```python
       # ✅ CORRECT: Use standardized registration helper
       async def initialize(self):
           await super().initialize()
           
           # Get infrastructure and Smart City services
           self.file_management = self.get_abstraction("file_management")
           self.librarian = await self.get_librarian_api()
           
           # Register with Curator (one line!)
           await self.register_with_curator(
               capabilities=["file_parsing", "format_conversion"],
               soa_apis=["parse_file", "detect_file_type"],
               mcp_tools=["parse_file_tool", "detect_file_type_tool"]
           )
       ```
    
    6. MCP SERVER PATTERN (wraps SOA APIs as tools):
       ```python
       # ✅ CORRECT: MCP Server delegates to service SOA APIs
       class MyServiceMCPServer(MCPServerBase):
           def __init__(self, service, di_container):
               super().__init__(
                   server_name="my_service_mcp",
                   di_container=di_container,
                   server_type="single_service"  # 1:1 for realm services
               )
               self.service = service
               self._register_tools()
           
           async def execute_tool(self, tool_name: str, parameters: dict):
               # Route to service SOA API
               return await self.service.parse_file(**parameters)
       ```
    
    ANTI-PATTERNS (DON'T DO THESE):
    
    ❌ Direct Public Works access:
       self.file_mgmt = self.di_container.get_abstraction("file_management")
       → Use: self.file_mgmt = self.get_abstraction("file_management")
    
    ❌ Direct Communication Foundation:
       await self.communication_foundation.send_message(...)
       → Use: post_office = await self.get_post_office_api()
               await post_office.send_message(...)
    
    ❌ Custom storage implementations:
       with open(f"/tmp/{file}", "w") as f: ...
       → Use: await self.store_document(data, metadata)
    
    ❌ Custom validation logic:
       if not data.get("required_field"): raise Error(...)
       → Use: await self.validate_data_quality(data, rules)
    
    ❌ Custom orchestration:
       for step in workflow: await execute_step(step)
       → Use: await self.orchestrate_workflow(workflow_def)
    
    Inherits from mixins via multiple inheritance to enable direct method access.
    """
    
    # Startup policy: Realm services are LAZY by default (loaded on-demand)
    startup_policy: StartupPolicy = StartupPolicy.LAZY
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Realm Service Base with composed mixins."""
        # Core service properties
        self.service_name = service_name
        self.realm_name = realm_name
        self.platform_gateway = platform_gateway
        self.di_container = di_container
        self.start_time = datetime.utcnow()
        self.is_initialized = False
        self.service_health = "unknown"
        
        # Initialize mixins
        self._init_utility_access(di_container)
        self._init_infrastructure_access(di_container)
        self._init_security(di_container)
        self._init_performance_monitoring(di_container)
        self._init_platform_capabilities(di_container)
        self._init_communication(di_container)
        self._init_micro_module_support(service_name, di_container)
        
        # Initialize logger (with fallback if utility not available)
        try:
            self.logger = self.get_logger()
            if self.logger is None:
                # Fallback to standard logging if utility not available
                import logging
                self.logger = logging.getLogger(f"{service_name}")
        except Exception:
            # Fallback to standard logging if get_logger fails
            import logging
            self.logger = logging.getLogger(f"{service_name}")
        
        if self.logger:
            self.logger.info(f"🏗️ RealmServiceBase '{service_name}' initialized for realm '{realm_name}'")
    
    async def initialize(self) -> bool:
        """Initialize the realm service."""
        try:
            self.logger.info(f"🚀 Initializing {self.service_name}...")
            
            # Realm-specific initialization
            self.service_health = "healthy"
            self.is_initialized = True
            
            self.logger.info(f"✅ {self.service_name} Realm Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.service_name}: {e}")
            self.service_health = "unhealthy"
            return False
    
    async def shutdown(self) -> bool:
        """Shutdown the realm service gracefully."""
        try:
            self.logger.info(f"🛑 Shutting down {self.service_name}...")
            
            # Realm-specific shutdown
            self.is_initialized = False
            self.service_health = "shutdown"
            
            self.logger.info(f"✅ {self.service_name} Realm Service shutdown successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to shutdown {self.service_name}: {e}")
            return False
    
    # ============================================================================
    # INFRASTRUCTURE ACCESS - Explicit delegation to mixin
    # ============================================================================
    # Override to ensure mixin's implementation is used (not protocol's)
    # The Protocol defines get_infrastructure_abstraction with ..., but the mixin has the real implementation
    # CRITICAL: Protocol comes before Mixin in MRO, so we must explicitly call the mixin
    def get_infrastructure_abstraction(self, name: str) -> Any:
        """Get infrastructure abstraction - explicitly call mixin's implementation."""
        # Directly call the mixin's method to bypass Protocol's placeholder
        return InfrastructureAccessMixin.get_infrastructure_abstraction(self, name)
    
    def get_auth_abstraction(self) -> Any:
        """Get authentication abstraction - explicitly call mixin's implementation."""
        # Directly call the mixin's method to bypass Protocol's placeholder
        return InfrastructureAccessMixin.get_auth_abstraction(self)
    
    # ============================================================================
    # UTILITY ACCESS - Explicit delegation to mixin
    # ============================================================================
    # Override to ensure mixin's implementation is used (not protocol's)
    # The Protocol defines get_utility with ..., but the mixin has the real implementation
    # CRITICAL: Protocol comes before Mixin in MRO, so we must explicitly call the mixin
    def get_utility(self, name: str) -> Any:
        """Get utility service - explicitly call mixin's implementation."""
        # Directly call the mixin's method to bypass Protocol's placeholder
        return UtilityAccessMixin.get_utility(self, name)
    
    def _get_config_adapter(self) -> Any:
        """
        Get ConfigAdapter from PublicWorksFoundationService.
        
        Returns:
            ConfigAdapter instance (required - raises error if not available)
        
        Raises:
            ValueError: If ConfigAdapter is not available (Public Works Foundation not initialized)
        """
        try:
            # Get PublicWorksFoundationService from DI Container
            if not self.di_container:
                raise ValueError(
                    "DI Container not available. "
                    "ConfigAdapter requires Public Works Foundation to be initialized."
                )
            
            if not hasattr(self.di_container, 'get_foundation_service'):
                raise ValueError(
                    "DI Container does not have get_foundation_service method. "
                    "ConfigAdapter requires Public Works Foundation to be initialized."
                )
            
            public_works = self.di_container.get_foundation_service("PublicWorksFoundationService")
            if not public_works:
                raise ValueError(
                    "Public Works Foundation Service not available. "
                    "Ensure Public Works Foundation is initialized before using ConfigAdapter."
                )
            
            if not hasattr(public_works, 'config_adapter') or not public_works.config_adapter:
                raise ValueError(
                    "ConfigAdapter not available in Public Works Foundation. "
                    "Ensure Public Works Foundation is fully initialized."
                )
            
            return public_works.config_adapter
            
        except ValueError:
            # Re-raise ValueError (our own errors)
            raise
        except Exception as e:
            # Wrap other exceptions
            raise ValueError(
                f"Failed to get ConfigAdapter from Public Works Foundation: {e}. "
                "Ensure Public Works Foundation is initialized before using ConfigAdapter."
            ) from e
    
    def get_abstraction(self, abstraction_name: str) -> Any:
        """Get abstraction through Platform Gateway."""
        return self.platform_gateway.get_abstraction(self.realm_name, abstraction_name)
    
    def get_realm_abstractions(self) -> Dict[str, Any]:
        """Get all allowed abstractions for this realm."""
        return self.platform_gateway.get_realm_abstractions(self.realm_name)
    
    def get_realm_context(self) -> Dict[str, Any]:
        """Get realm-specific context and configuration."""
        return {
            "realm_name": self.realm_name,
            "service_name": self.service_name,
            "available_abstractions": list(self.get_realm_abstractions().keys()),
            "is_initialized": self.is_initialized,
            "service_health": self.service_health
        }
    
    def validate_realm_access(self, resource: str, action: str) -> bool:
        """Validate access within realm context."""
        return self.validate_access(resource, action)
    
    def get_configuration(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        config = self.get_config()
        return config.get(key, default)
    
    def get_service_metadata(self) -> Dict[str, Any]:
        """Get service metadata and information."""
        return {
            "service_name": self.service_name,
            "realm_name": self.realm_name,
            "service_type": "realm",
            "is_initialized": self.is_initialized,
            "service_health": self.service_health,
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds()
        }
    
    # ============================================================================
    # SMART CITY SERVICE DISCOVERY METHODS (Via Curator)
    # ============================================================================
    # Note: get_smart_city_api() is provided by PlatformCapabilitiesMixin (inherited via multiple inheritance)
    # These convenience methods delegate to the inherited get_smart_city_api method
    
    async def get_security_guard_api(self) -> Optional[Any]:
        """Convenience method to get Security Guard service."""
        # Delegate to inherited get_smart_city_api from PlatformCapabilitiesMixin
        return await self.get_smart_city_api("SecurityGuard")
    
    async def get_traffic_cop_api(self) -> Optional[Any]:
        """Convenience method to get Traffic Cop service."""
        return await self.get_smart_city_api("TrafficCop")
    
    async def get_conductor_api(self) -> Optional[Any]:
        """Convenience method to get Conductor service."""
        return await self.get_smart_city_api("Conductor")
    
    async def get_post_office_api(self) -> Optional[Any]:
        """Convenience method to get Post Office service."""
        return await self.get_smart_city_api("PostOffice")
    
    async def get_librarian_api(self) -> Optional[Any]:
        """Convenience method to get Librarian service."""
        return await self.get_smart_city_api("Librarian")
    
    async def get_content_steward_api(self) -> Optional[Any]:
        """Convenience method to get Content Steward service."""
        return await self.get_smart_city_api("ContentSteward")
    
    async def get_data_steward_api(self) -> Optional[Any]:
        """Convenience method to get Data Steward service."""
        return await self.get_smart_city_api("DataSteward")
    
    async def get_nurse_api(self) -> Optional[Any]:
        """Convenience method to get Nurse service."""
        return await self.get_smart_city_api("Nurse")
    
    async def get_city_manager_api(self) -> Optional[Any]:
        """Convenience method to get City Manager service."""
        return await self.get_smart_city_api("CityManager")
    
    # ============================================================================
    # CURATOR REGISTRATION HELPER (Standardized Pattern)
    # ============================================================================
    
    async def register_with_curator(
        self,
        capabilities: list,
        soa_apis: list,
        mcp_tools: list,
        protocols: Optional[List[Dict[str, Any]]] = None,
        routing_metadata: Optional[Dict[str, Any]] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register service with Curator (unified registration flow - Phase 2 refactoring).
        
        Aligned with revised design:
        1. Register capabilities (using CapabilityDefinition) - routes automatically tracked
        2. Register service protocols (Python typing.Protocol)
        3. Register routes in endpoint registry (domains define, Curator tracks)
        4. Report service mesh policies (domain owns, Curator reports)
        5. Register with service discovery (via Public Works)
        
        Args:
            capabilities: List of service capabilities (dicts with name, protocol, description, semantic_mapping, contracts)
            soa_apis: List of SOA API method names (e.g., ["parse_file", "detect_file_type"])
            mcp_tools: List of MCP tool names (e.g., ["parse_file_tool", "detect_file_type_tool"])
            protocols: Optional list of protocol definitions (Python typing.Protocol)
            routing_metadata: Optional routing metadata with policies
            additional_metadata: Optional additional metadata
        
        Returns:
            True if registration successful, False otherwise
        
        Example:
            ```python
            await self.register_with_curator(
                capabilities=[
                    {
                        "name": "file_parsing",
                        "protocol": "IFileParser",
                        "description": "Parse files into structured formats",
                        "semantic_mapping": {
                            "domain_capability": "content.upload_file",
                            "semantic_api": "/api/v1/content-pillar/upload-file"
                        },
                        "contracts": {
                            "rest_api": {
                                "endpoint": "/api/v1/content-pillar/upload-file",
                                "method": "POST"
                            }
                        }
                    }
                ],
                soa_apis=["parse_file", "detect_file_type"],
                mcp_tools=["parse_file_tool", "detect_file_type_tool"],
                protocols=[{
                    "name": "IFileParser",
                    "definition": {"methods": {...}}
                }],
                routing_metadata={
                    "policies": {
                        "load_balancing": "round_robin",
                        "timeout": "30s"
                    }
                }
            )
            ```
        """
        try:
            curator = self.get_curator()
            if not curator:
                self.logger.warning("⚠️ Curator Foundation not available")
                return False
            
            # Import CapabilityDefinition
            from foundations.curator_foundation.models.capability_definition import CapabilityDefinition
            
            # 1. Register capabilities (using CapabilityDefinition) - routes automatically tracked
            for capability in capabilities:
                # Handle both dict and string formats (backward compatibility)
                if isinstance(capability, str):
                    # Simple string format - convert to dict
                    capability = {
                        "name": capability,
                        "description": capability,
                        "protocol": f"I{self.service_name}"
                    }
                
                # Convert capability dict to CapabilityDefinition (new Phase 2 structure)
                # Extract capability name (required)
                capability_name = capability.get("name", capability.get("capability_name"))
                if not capability_name:
                    self.logger.warning(f"⚠️ Capability missing 'name' or 'capability_name', using description as fallback")
                    capability_name = capability.get("description", "unknown_capability").lower().replace(" ", "_")
                
                # Extract protocol name (required)
                protocol_name = capability.get("protocol", capability.get("protocol_name"))
                if not protocol_name:
                    # Default to service protocol name
                    protocol_name = f"{self.service_name}Protocol"
                
                # Ensure contracts exist (required)
                contracts = capability.get("contracts", {})
                if not contracts:
                    self.logger.warning(f"⚠️ Capability '{capability_name}' missing contracts, creating empty contracts dict")
                    contracts = {}
                
                # Convert capability dict to CapabilityDefinition
                # Smart City services don't need semantic mapping (not user-facing)
                semantic_mapping = None
                if self.realm_name != "smart_city":
                    # Public-facing realms require semantic mapping for user-facing APIs
                    semantic_mapping = capability.get("semantic_mapping")
                else:
                    # Smart City services are platform enablers, not user-facing
                    # Semantic mapping is optional (can be provided but not required)
                    semantic_mapping = capability.get("semantic_mapping")  # Optional for Smart City
                
                capability_def = CapabilityDefinition(
                    capability_name=capability_name,
                    service_name=self.service_name,
                    protocol_name=protocol_name,
                    description=capability.get("description", capability.get("name", "")),
                    realm=self.realm_name,
                    contracts=contracts,  # REQUIRED
                    semantic_mapping=semantic_mapping,  # Optional for Smart City, required for public-facing
                    version=capability.get("version", "1.0.0")
                )
                await curator.register_domain_capability(capability_def)
            
            # 2. Register service protocols (Python typing.Protocol)
            if protocols:
                for protocol in protocols:
                    await curator.register_service_protocol(
                        service_name=self.service_name,
                        protocol_name=protocol["name"],
                        protocol=protocol["definition"]
                    )
            
            # 3. Register routes in endpoint registry (domains define, Curator tracks)
            # Routes are automatically registered when capabilities are registered
            # If SOA APIs have route metadata, register them explicitly
            for soa_api in soa_apis:
                if isinstance(soa_api, dict) and soa_api.get("route_metadata"):
                    await curator.register_route(soa_api["route_metadata"])
            
            # 4. Report service mesh policies (domain owns, Curator reports)
            # Smart City services don't have user-facing routes, so routing metadata is optional
            if routing_metadata and routing_metadata.get("policies"):
                await curator.report_service_mesh_policies(
                    service_name=self.service_name,
                    policies={
                        "source": self.realm_name,
                        "policies": routing_metadata["policies"]
                    }
                )
            elif self.realm_name == "smart_city":
                # Smart City services can skip routing metadata (no user-facing routes)
                self.logger.debug(f"ℹ️ Smart City service {self.service_name} skipping routing metadata (not user-facing)")
            
            # 5. Register with service discovery (via Public Works)
            # Use existing register_service method for backward compatibility
            registration_data = {
                "service_name": self.service_name,
                "service_type": "realm_service",
                "realm": self.realm_name,
                "capabilities": capabilities,
                "soa_apis": soa_apis,
                "mcp_tools": mcp_tools,
                "service_instance": self,
                "health_check_endpoint": f"{self.service_name}/health",
                "start_time": self.start_time.isoformat(),
                "metadata": additional_metadata or {}
            }
            
            result = await curator.register_service(
                service_instance=self,
                service_metadata=registration_data
            )
            success = result.get("success", False)
            
            if success:
                self.logger.info(f"✅ Registered {self.service_name} with Curator (Phase 2 pattern)")
                self.logger.debug(f"   Capabilities: {len(capabilities)}")
                self.logger.debug(f"   SOA APIs: {len(soa_apis)}")
                self.logger.debug(f"   MCP Tools: {len(mcp_tools)}")
                if protocols:
                    self.logger.debug(f"   Protocols: {len(protocols)}")
            else:
                error_msg = result.get("error", "Unknown error")
                error_code = result.get("error_code", "UNKNOWN")
                self.logger.warning(f"⚠️ Failed to register {self.service_name} with Curator: {error_code} - {error_msg}")
                self.logger.debug(f"   Full registration result: {result}")
            
            return success
            
        except Exception as e:
            import traceback
            self.logger.error(f"❌ Curator registration failed: {e}")
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return False
    
    # ============================================================================
    # SMART CITY DELEGATION HELPERS (Prevent Spaghetti Code)
    # ============================================================================
    # These methods delegate to Smart City services instead of allowing custom
    # implementations. Use these helpers to ensure proper architecture patterns.
    
    async def store_document(
        self,
        document_data: Any,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store document via Content Steward service.
        
        IMPORTANT: Use this instead of implementing custom storage.
        Content Steward provides centralized file/document storage with
        file management infrastructure (GCS + Supabase).
        
        ARCHITECTURE: Document storage is a platform capability exposed by Content Steward.
        - Public Works: file_management infrastructure (Supabase/GCS)
        - Content Steward: Wraps infrastructure, provides file storage SOA APIs
        - Realm Services: Access via Content Steward SOA APIs (this method)
        
        Args:
            document_data: Document content to store (dict, bytes, or string)
            metadata: Document metadata (title, author, tags, etc.)
        
        Returns:
            Storage result with document_id (file_uuid) and metadata
        """
        content_steward = await self.get_content_steward_api()
        if not content_steward:
            raise ValueError("Content Steward service not available")
        
        # Convert document_data to bytes if needed
        import json
        if isinstance(document_data, (dict, list)):
            file_data = json.dumps(document_data).encode('utf-8')
            content_type = "application/json"
        elif isinstance(document_data, str):
            file_data = document_data.encode('utf-8')
            content_type = metadata.get("content_type", "text/plain")
        elif isinstance(document_data, bytes):
            file_data = document_data
            content_type = metadata.get("content_type", "application/octet-stream")
        else:
            # Convert to JSON string then bytes
            file_data = json.dumps(document_data).encode('utf-8')
            content_type = "application/json"
        
        # Prepare metadata for Content Steward
        # Content Steward expects: ui_name, file_type (extension), and other metadata
        content_steward_metadata = {
            "ui_name": metadata.get("title") or metadata.get("ui_name") or f"document_{uuid.uuid4()}",
            "file_type": metadata.get("file_type") or "json",  # Extension
            "original_filename": metadata.get("title") or "document.json",
            **metadata  # Include all other metadata
        }
        
        # Store via Content Steward SOA API
        result = await content_steward.process_upload(
            file_data=file_data,
            content_type=content_type,
            metadata=content_steward_metadata
        )
        
        # Return in expected format (document_id = file_uuid)
        return {
            "document_id": result.get("uuid") or result.get("file_id"),
            "file_uuid": result.get("uuid"),
            "metadata": result.get("metadata", {}),
            **result
        }
    
    async def retrieve_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve file via Content Steward SOA API.
        
        ARCHITECTURE: File storage is a platform capability exposed by Content Steward.
        - Public Works: file_management infrastructure (Supabase/GCS)
        - Content Steward: Wraps infrastructure, provides file storage SOA APIs
        - Realm Services: Access via Content Steward SOA APIs (this method)
        
        Content Steward owns file storage business logic and exposes it to realms.
        
        Args:
            document_id: ID of file to retrieve
        
        Returns:
            File data with metadata, or None if not found
        """
        try:
            # Get Content Steward via Smart City discovery
            content_steward = await self.get_content_steward_api()
            if not content_steward:
                self.logger.warning("⚠️ Content Steward not available for file retrieval")
                return None
            
            # Get file via Content Steward SOA API (aligns with FileManagementProtocol)
            file_record = await content_steward.get_file(document_id)
            
            if not file_record:
                self.logger.debug(f"File not found: {document_id}")
                return None
            
            return file_record
            
        except Exception as e:
            self.logger.error(f"❌ Failed to retrieve file {document_id}: {e}")
            return None
    
    async def search_documents(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        Search documents via Librarian service.
        
        ARCHITECTURE: Knowledge search is a platform capability exposed by Librarian.
        - Librarian: Provides knowledge discovery, semantic search, and content cataloging
        - Realm Services: Access via Librarian SOA APIs (this method)
        
        Args:
            query: Search query string
            filters: Optional filters dict for metadata filtering
        
        Returns:
            List of matching documents with metadata
        """
        librarian = await self.get_librarian_api()
        if not librarian:
            raise ValueError("Librarian service not available")
        
        result = await librarian.search_knowledge(query, filters)
        
        # Return results list (Librarian returns dict with 'results' key)
        return result.get("results", []) if isinstance(result, dict) else result
    
    
    async def validate_data_quality(
        self,
        schema_data: Dict[str, Any]
    ) -> bool:
        """
        Validate data via Data Steward service.
        
        IMPORTANT: Use this instead of implementing custom validation.
        Data Steward provides centralized schema validation with governance
        and audit trails.
        
        ARCHITECTURE: Data validation is a platform capability exposed by Data Steward.
        - Data Steward: Provides schema validation, quality metrics, compliance
        - Realm Services: Access via Data Steward SOA APIs (this method)
        
        Args:
            schema_data: Schema data dict with 'name', 'type', 'fields', etc.
        
        Returns:
            True if schema is valid, False otherwise
        """
        data_steward = await self.get_data_steward_api()
        if not data_steward:
            raise ValueError("Data Steward service not available")
        
        return await data_steward.validate_schema(schema_data)
    
    async def track_data_lineage(
        self,
        lineage_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Track data lineage via Data Steward service.
        
        ARCHITECTURE: Lineage tracking is a platform capability exposed by Data Steward.
        - Data Steward: Provides data governance, lineage tracking, and audit trails
        - Realm Services: Access via Data Steward SOA APIs (this method)
        
        Args:
            lineage_data: Lineage data dict with 'asset_id', 'parent_assets', 'child_assets', 'transformation', etc.
        
        Returns:
            Lineage ID (str) if lineage recorded successfully, None if Data Steward not available
        """
        data_steward = await self.get_data_steward_api()
        if not data_steward:
            # Log warning but don't fail - lineage tracking is optional for analysis to proceed
            self.logger.warning("⚠️ Data Steward service not available - skipping lineage tracking")
            return None  # Return None instead of raising error
        
        try:
            return await data_steward.record_lineage(lineage_data)
        except Exception as e:
            # Log error but don't fail - lineage tracking is optional
            self.logger.warning(f"⚠️ Lineage tracking failed: {e} - continuing without lineage")
            return None
    
    async def orchestrate_workflow(
        self,
        workflow_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Orchestrate workflow via Conductor service.
        
        IMPORTANT: Use this instead of implementing custom orchestration.
        Conductor provides centralized workflow management with state tracking,
        error handling, retry logic, and audit trails.
        
        Args:
            workflow_definition: Workflow steps and dependencies
        
        Returns:
            Workflow execution results
        """
        conductor = await self.get_conductor_api()
        if not conductor:
            raise ValueError("Conductor service not available")
        
        return await conductor.execute_workflow(workflow_definition)
    
    async def enrich_content_metadata(
        self,
        content_id: str,
        enrichment_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Enrich content metadata via Content Steward service.
        
        ARCHITECTURE: Metadata enrichment is a platform capability exposed by Content Steward.
        - Content Steward: Provides metadata extraction and enrichment
        - Realm Services: Access via Content Steward SOA APIs (this method)
        
        Args:
            content_id: ID of content to enrich
            enrichment_types: Optional list of enrichment source IDs (if provided, gets metadata from each)
        
        Returns:
            Enriched metadata dictionary
        """
        content_steward = await self.get_content_steward_api()
        if not content_steward:
            raise ValueError("Content Steward service not available")
        
        # Get metadata for the main content
        main_metadata = await content_steward.get_asset_metadata(content_id)
        
        # If enrichment_types (source IDs) provided, get metadata from each source and merge
        if enrichment_types:
            enriched_metadata = main_metadata.copy() if main_metadata else {}
            for source_id in enrichment_types:
                try:
                    source_metadata = await content_steward.get_asset_metadata(source_id)
                    if source_metadata:
                        # Merge source metadata into enriched metadata
                        if isinstance(source_metadata, dict):
                            enriched_metadata.update(source_metadata)
                        elif isinstance(enriched_metadata, dict):
                            enriched_metadata[f"source_{source_id}"] = source_metadata
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to get metadata from enrichment source {source_id}: {e}")
                    continue
            
            return enriched_metadata
        
        return main_metadata or {}
    
    async def send_notification(
        self,
        message: Dict[str, Any],
        recipients: list
    ) -> bool:
        """
        Send notification via Post Office service.
        
        IMPORTANT: Use this instead of implementing custom messaging.
        Post Office provides centralized message routing, delivery tracking,
        and multi-channel support (email, SMS, webhooks).
        
        Args:
            message: Message content and metadata
            recipients: List of recipient IDs or addresses
        
        Returns:
            True if message sent successfully
        """
        post_office = await self.get_post_office_api()
        if not post_office:
            raise ValueError("Post Office service not available")
        
        return await post_office.send_message(message, recipients)
    
    async def route_request(
        self,
        request: Dict[str, Any],
        destination: str
    ) -> Dict[str, Any]:
        """
        Route request via Traffic Cop service.
        
        IMPORTANT: Use this instead of implementing custom routing.
        Traffic Cop provides intelligent request routing, load balancing,
        and rate limiting.
        
        Args:
            request: Request data to route
            destination: Destination service or endpoint
            
        Returns:
            Response from destination service
        """