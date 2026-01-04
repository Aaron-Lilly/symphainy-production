#!/usr/bin/env python3
"""
Platform Infrastructure Gateway

Centralized access point for realm-specific infrastructure abstractions.
Provides explicit realm abstraction mappings with validation and governance.

Key Features:
- Explicit realm abstraction mappings (no implicit access)
- Validation before access (governance and audit)
- Future-ready for BYOI (Bring Your Own Infrastructure)
- Single source of truth for realm access policies

WHAT (Platform Gateway Role): I provide controlled access to Public Works abstractions for realm services
HOW (Platform Gateway Implementation): I enforce realm-specific abstraction mappings with validation
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class RealmCapability:
    """Metadata about a realm's allowed abstractions."""
    realm_name: str
    abstractions: List[str]
    description: str
    byoi_support: bool = False


class PlatformInfrastructureGateway:
    """
    Platform Infrastructure Gateway - Centralized realm abstraction access.
    
    Provides validated access to Public Works abstractions based on explicit
    realm mappings. Prevents spaghetti architecture by enforcing governance.
    """
    
    # ============================================================================
    # REALM ABSTRACTION MAPPINGS (CRITICAL - Central Configuration)
    # ============================================================================
    
    REALM_ABSTRACTION_MAPPINGS = {
        "smart_city": {
            "abstractions": [
                # Smart City owns ALL abstractions (infrastructure layer)
                "session", "state", "auth", "authorization", "tenant",
                "file_management", "content_metadata", "content_schema", 
                "content_insights", "llm", "mcp", "policy", "cache",
                "api_gateway", "messaging", "event_bus", "websocket_gateway",
                # All file parsing abstractions (for infrastructure operations)
                "excel_processing", "csv_processing", "json_processing", "text_processing",
                "pdf_processing", "word_processing", "html_processing", "image_processing",
                "mainframe_processing",
                # All analysis abstractions (for infrastructure operations)
                "visualization", "business_metrics",
                # Semantic data (for infrastructure operations)
                "semantic_data"
            ],
            "soa_apis": [],  # Smart City doesn't need SOA APIs (it owns everything)
            "description": "Smart City - Infrastructure layer with full access",
            "byoi_support": True
        },
        "content": {
            "abstractions": [
                # Content realm owns ALL file parsing abstractions (foundation layer)
                "excel_processing", "csv_processing", "json_processing", "text_processing",
                "pdf_processing", "word_processing", "html_processing", "image_processing",
                "mainframe_processing",
                # Content realm owns semantic data creation (CRITICAL - creates data mash)
                "semantic_data",
                # Content realm owns file operations
                "file_management", "content_metadata"
            ],
            "soa_apis": [
                # Content realm can access Post Office for event publishing (cross-realm communication)
                "post_office.publish_event",
                "post_office.subscribe_to_events",
                # Content realm can access Traffic Cop for session management
                "traffic_cop.get_session",
                "traffic_cop.update_session"
            ],
            "description": "Content Realm - Data front door, file parsing, semantic data creation",
            "byoi_support": False
        },
        "insights": {
            "abstractions": [
                # Insights realm owns analysis abstractions (analysis layer)
                "visualization", "business_metrics", "content_insights"
                # NOTE: semantic_data, file_management, content_metadata accessed via Content SOA APIs
            ],
            "soa_apis": [
                "content.parse_file",
                "content.create_embeddings",
                "content.get_semantic_data",
                "content.get_file",
                "content.get_metadata",
                "post_office.publish_event",  # ✅ Event bus SOA API
                "post_office.subscribe_to_events"  # ✅ Event bus SOA API
            ],
            "description": "Insights Realm - Analysis (consumes Content Realm semantic substrate)",
            "byoi_support": False
        },
        "journey": {
            "abstractions": [
                # Journey realm owns orchestration abstractions (NOT infrastructure)
                "session_orchestration", "state_orchestration"
                # NOTE: Session/state infrastructure accessed via Traffic Cop SOA APIs
                # NOTE: All data/analysis abstractions accessed via Content/Insights SOA APIs
            ],
            "soa_apis": [
                "content.parse_file",
                "content.create_embeddings",
                "content.get_semantic_data",
                "insights.analyze_data",
                "insights.validate_quality",
                "insights.generate_visualizations",
                "post_office.publish_event",  # ✅ Event bus SOA API
                "post_office.subscribe_to_events",  # ✅ Event bus SOA API
                "traffic_cop.get_session",
                "traffic_cop.update_session"
            ],
            "description": "Journey Realm - Workflow orchestration (composes Content/Insights capabilities)",
            "byoi_support": False
        },
        "solution": {
            "abstractions": [
                # Solution realm owns minimal abstractions (entry point layer)
                "solution_context"  # For landing page context (disseminated to other realms)
                # NOTE: NO "llm" abstraction - LLMs must ONLY be accessed via agents (platform rule)
                # NOTE: Solution realm uses agents for any LLM needs (via Agentic Foundation SDK)
                # NOTE: All other abstractions accessed via lower realm SOA APIs
            ],
            "soa_apis": [
                "content.parse_file",
                "content.get_semantic_data",
                "insights.analyze_data",
                "insights.generate_visualizations",
                "journey.execute_content_workflow",
                "journey.execute_insights_workflow",
                "journey.manage_session",
                "post_office.get_websocket_endpoint",
                "post_office.publish_to_agent_channel",
                "post_office.publish_event",  # ✅ Event bus SOA API
                "post_office.subscribe_to_events",  # ✅ Event bus SOA API
                "traffic_cop.get_session",
                "data_steward.store_file",
                "librarian.search_content"
            ],
            "description": "Solution Realm - Entry point (composes Journey/Insights/Content capabilities)",
            "byoi_support": False
        },
        "business_enablement": {
            "abstractions": [
                # Business Enablement is legacy - will be phased out
                # Keeping for backward compatibility during migration
                "content_metadata", "content_schema", "content_insights", 
                "file_management", "llm", "document_intelligence",
                "semantic_data",
                "bpmn_processing", "sop_processing", "sop_enhancement",
                "strategic_planning", "financial_analysis", "workflow_diagramming_orchestration",
                "visualization", "business_metrics",
                "excel_processing", "csv_processing", "json_processing", "text_processing",
                "pdf_processing", "word_processing", "html_processing", "image_processing",
                "mainframe_processing"
            ],
            "soa_apis": [],
            "description": "Business Enablement - Legacy realm (being phased out)",
            "byoi_support": False
        }
    }
    
    def __init__(self, public_works_foundation: Any, di_container: Any = None):
        """
        Initialize Platform Infrastructure Gateway.
        
        Args:
            public_works_foundation: Public Works Foundation Service instance
            di_container: Optional DI Container for accessing Curator (for SOA API discovery)
        """
        self.public_works_foundation = public_works_foundation
        self.di_container = di_container
        self.logger = logging.getLogger(f"{__name__}.PlatformGateway")
        self.is_initialized = False
        
        # Metrics tracking
        self.access_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "denied_requests": 0,
            "realm_access_counts": {},
            "soa_api_requests": 0,
            "soa_api_successful": 0,
            "soa_api_denied": 0
        }
        
        self.logger.info("✅ Platform Infrastructure Gateway initialized")
    
    async def initialize(self) -> bool:
        """Initialize Platform Gateway (async for consistency with other services)."""
        try:
            # Validate Public Works Foundation is available
            if not self.public_works_foundation:
                raise ValueError("Public Works Foundation is required for Platform Gateway")
            
            self.is_initialized = True
            self.logger.info("✅ Platform Infrastructure Gateway initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Platform Gateway: {e}")
            return False
    
    # ============================================================================
    # CORE ACCESS CONTROL METHODS
    # ============================================================================
    
    def get_abstraction(self, realm_name: str, abstraction_name: str) -> Any:
        """
        Get infrastructure abstraction with realm validation.
        
        Args:
            realm_name: Name of the requesting realm
            abstraction_name: Name of the abstraction to access
            
        Returns:
            Infrastructure abstraction instance
            
        Raises:
            ValueError: If realm doesn't have access to abstraction
        """
        self.access_metrics["total_requests"] += 1
        
        # Validate realm access
        if not self.validate_realm_access(realm_name, abstraction_name):
            self.access_metrics["denied_requests"] += 1
            allowed = self.get_realm_abstractions(realm_name)
            raise ValueError(
                f"Realm '{realm_name}' cannot access '{abstraction_name}'. "
                f"Allowed: {allowed}"
            )
        
        # Track successful access
        self.access_metrics["successful_requests"] += 1
        if realm_name not in self.access_metrics["realm_access_counts"]:
            self.access_metrics["realm_access_counts"][realm_name] = 0
        self.access_metrics["realm_access_counts"][realm_name] += 1
        
        # Get abstraction from Public Works
        try:
            abstraction = self.public_works_foundation.get_abstraction(abstraction_name)
            self.logger.debug(f"✅ Granted '{realm_name}' access to '{abstraction_name}'")
            return abstraction
        except Exception as e:
            self.logger.error(f"❌ Failed to get abstraction '{abstraction_name}' for realm '{realm_name}': {e}")
            raise
    
    def get_realm_abstractions(self, realm_name: str) -> List[str]:
        """
        Get all abstractions allowed for a realm.
        
        Args:
            realm_name: Name of the realm
            
        Returns:
            List of abstraction names the realm can access
        """
        if realm_name not in self.REALM_ABSTRACTION_MAPPINGS:
            return []
        
        return self.REALM_ABSTRACTION_MAPPINGS[realm_name]["abstractions"]
    
    def validate_realm_access(self, realm_name: str, abstraction_name: str) -> bool:
        """
        Validate if realm has access to abstraction (non-throwing).
        
        Args:
            realm_name: Name of the requesting realm
            abstraction_name: Name of the abstraction to access
            
        Returns:
            True if realm has access, False otherwise
        """
        if realm_name not in self.REALM_ABSTRACTION_MAPPINGS:
            return False
        
        allowed_abstractions = self.REALM_ABSTRACTION_MAPPINGS[realm_name]["abstractions"]
        return abstraction_name in allowed_abstractions
    
    def get_realm_capabilities(self, realm_name: str) -> Optional[RealmCapability]:
        """
        Get metadata about realm's allowed abstractions.
        
        Args:
            realm_name: Name of the realm
            
        Returns:
            RealmCapability metadata or None if realm not found
        """
        if realm_name not in self.REALM_ABSTRACTION_MAPPINGS:
            return None
        
        mapping = self.REALM_ABSTRACTION_MAPPINGS[realm_name]
        return RealmCapability(
            realm_name=realm_name,
            abstractions=mapping["abstractions"],
            description=mapping["description"],
            byoi_support=mapping.get("byoi_support", False)
        )
    
    # ============================================================================
    # SOA API ACCESS METHODS (Cross-Realm Communication)
    # ============================================================================
    
    def validate_soa_api_access(self, realm_name: str, api_name: str) -> bool:
        """
        Validate if realm has access to SOA API.
        
        Args:
            realm_name: Name of the requesting realm
            api_name: SOA API name (e.g., "content.parse_file", "post_office.get_websocket_endpoint")
            
        Returns:
            True if realm has access, False otherwise
        """
        if realm_name not in self.REALM_ABSTRACTION_MAPPINGS:
            return False
        
        soa_apis = self.REALM_ABSTRACTION_MAPPINGS[realm_name].get("soa_apis", [])
        return api_name in soa_apis
    
    def get_realm_soa_apis(self, realm_name: str) -> List[str]:
        """
        Get all SOA APIs allowed for a realm.
        
        Args:
            realm_name: Name of the realm
            
        Returns:
            List of SOA API names the realm can access
        """
        if realm_name not in self.REALM_ABSTRACTION_MAPPINGS:
            return []
        
        return self.REALM_ABSTRACTION_MAPPINGS[realm_name].get("soa_apis", [])
    
    async def get_soa_api(self, realm_name: str, api_name: str) -> Any:
        """
        Get SOA API for cross-realm communication.
        
        Args:
            realm_name: Name of the requesting realm
            api_name: SOA API name (e.g., "content.parse_file", "post_office.get_websocket_endpoint")
            
        Returns:
            SOA API callable (method) or service instance
            
        Raises:
            ValueError: If realm doesn't have access to SOA API or service not found
        """
        self.access_metrics["soa_api_requests"] += 1
        
        # Validate realm access
        if not self.validate_soa_api_access(realm_name, api_name):
            self.access_metrics["soa_api_denied"] += 1
            allowed = self.get_realm_soa_apis(realm_name)
            raise ValueError(
                f"Realm '{realm_name}' does not have access to SOA API '{api_name}'. "
                f"Allowed SOA APIs: {allowed}"
            )
        
        # Parse API name (service.method or service)
        api_parts = api_name.split(".", 1)
        service_name = api_parts[0]
        method_name = api_parts[1] if len(api_parts) > 1 else None
        
        # Map SOA API names to actual service methods
        # Some SOA APIs have different method names than the service methods
        soa_api_method_mapping = {
            "post_office.publish_event": "publish_event_soa",
            "post_office.subscribe_to_events": "subscribe_to_events_soa",
            "post_office.get_websocket_endpoint": "get_websocket_endpoint",
            "post_office.publish_to_agent_channel": "publish_to_agent_channel",
            "traffic_cop.get_session": "get_session",
            "traffic_cop.update_session": "update_session",
            "data_steward.store_file": "store_file",
            "librarian.search_content": "search_content",
            "content.parse_file": "parse_file",
            "content.create_embeddings": "create_embeddings",
            "content.get_semantic_data": "get_semantic_data",
            "content.get_file": "get_file",
            "content.get_metadata": "get_metadata",
            "insights.analyze_data": "analyze_data",
            "insights.validate_quality": "validate_quality",
            "insights.generate_visualizations": "generate_visualizations",
            "journey.execute_content_workflow": "execute_content_workflow",
            "journey.execute_insights_workflow": "execute_insights_workflow",
            "journey.manage_session": "manage_session"
        }
        
        # Use mapped method name if available
        if api_name in soa_api_method_mapping:
            method_name = soa_api_method_mapping[api_name]
        
        # Get Curator from DI Container
        if not self.di_container:
            raise ValueError("DI Container not available - cannot discover services for SOA API access")
        
        curator = self.di_container.get_foundation_service("CuratorFoundationService")
        if not curator:
            raise ValueError("Curator Foundation not available - cannot discover services for SOA API access")
        
        # Discover service via Curator
        try:
            service = await curator.discover_service_by_name(service_name)
            if not service:
                # Try with "Service" suffix
                service = await curator.discover_service_by_name(f"{service_name}Service")
            
            if not service:
                raise ValueError(f"Service '{service_name}' not found via Curator")
            
            # If method_name specified, return the method; otherwise return service instance
            if method_name:
                if not hasattr(service, method_name):
                    raise ValueError(f"Service '{service_name}' does not have method '{method_name}'")
                method = getattr(service, method_name)
                if not callable(method):
                    raise ValueError(f"'{method_name}' on service '{service_name}' is not callable")
                
                self.access_metrics["soa_api_successful"] += 1
                self.logger.debug(f"✅ Granted '{realm_name}' access to SOA API '{api_name}'")
                return method
            else:
                # Return service instance
                self.access_metrics["soa_api_successful"] += 1
                self.logger.debug(f"✅ Granted '{realm_name}' access to SOA API '{api_name}' (service instance)")
                return service
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get SOA API '{api_name}' for realm '{realm_name}': {e}")
            raise ValueError(f"Failed to get SOA API '{api_name}': {e}")
    
    def _suggest_soa_api(self, abstraction_name: str) -> str:
        """
        Suggest SOA API for an abstraction name (helper for error messages).
        
        Args:
            abstraction_name: Name of the abstraction
            
        Returns:
            Suggested SOA API name
        """
        # Simple mapping for common abstractions
        suggestions = {
            "semantic_data": "content.get_semantic_data",
            "file_management": "content.get_file",
            "content_metadata": "content.get_metadata",
            "visualization": "insights.generate_visualizations",
            "business_metrics": "insights.calculate_metrics",
            "session": "traffic_cop.get_session",
            "state": "traffic_cop.update_session"
        }
        
        return suggestions.get(abstraction_name, f"<realm>.<operation>")
    
    # ============================================================================
    # BULK INITIALIZATION METHODS
    # ============================================================================
    
    def get_all_realm_abstractions(self, realm_name: str) -> Dict[str, Any]:
        """
        Bulk load all abstractions allowed for a realm.
        
        Args:
            realm_name: Name of the realm
            
        Returns:
            Dictionary mapping abstraction names to instances
        """
        abstractions = {}
        allowed_abstractions = self.get_realm_abstractions(realm_name)
        
        for abstraction_name in allowed_abstractions:
            try:
                abstractions[abstraction_name] = self.get_abstraction(realm_name, abstraction_name)
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to load abstraction '{abstraction_name}' for realm '{realm_name}': {e}")
        
        self.logger.info(f"✅ Loaded {len(abstractions)} abstractions for realm '{realm_name}'")
        return abstractions
    
    # ============================================================================
    # FUTURE-PROOFING (BYOI Support)
    # ============================================================================
    
    def get_infrastructure_capability(self, realm_name: str, capability_type: str) -> Dict[str, Any]:
        """
        Get infrastructure capability information for BYOI support.
        
        Args:
            realm_name: Name of the realm
            capability_type: Type of capability (storage, auth, messaging, etc.)
            
        Returns:
            Capability information including BYOI options
        """
        realm_capability = self.get_realm_capabilities(realm_name)
        if not realm_capability:
            return {"error": f"Realm '{realm_name}' not found"}
        
        # Future: Return BYOI options based on capability_type
        # For now, return current capability info
        return {
            "realm": realm_name,
            "capability_type": capability_type,
            "byoi_supported": realm_capability.byoi_support,
            "current_provider": "default",  # Future: dynamic based on configuration
            "byoi_options": []  # Future: S3/GCS/Azure, Auth0/Okta/Cognito, etc.
        }
    
    # ============================================================================
    # MONITORING AND HEALTH CHECKS
    # ============================================================================
    
    def get_access_metrics(self) -> Dict[str, Any]:
        """Get access metrics for monitoring."""
        return {
            "total_requests": self.access_metrics["total_requests"],
            "successful_requests": self.access_metrics["successful_requests"],
            "denied_requests": self.access_metrics["denied_requests"],
            "success_rate": (
                self.access_metrics["successful_requests"] / max(self.access_metrics["total_requests"], 1)
            ),
            "realm_access_counts": self.access_metrics["realm_access_counts"]
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Platform Gateway."""
        try:
            # Test Public Works Foundation connectivity
            test_abstraction = self.public_works_foundation.get_abstraction("session")
            
            return {
                "status": "healthy",
                "public_works_connected": True,
                "realm_mappings_loaded": len(self.REALM_ABSTRACTION_MAPPINGS),
                "metrics": self.get_access_metrics()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "public_works_connected": False
            }
    
    # ============================================================================
    # ADMINISTRATIVE METHODS
    # ============================================================================
    
    def list_all_realms(self) -> List[str]:
        """List all configured realms."""
        return list(self.REALM_ABSTRACTION_MAPPINGS.keys())
    
    def add_realm_mapping(self, realm_name: str, abstractions: List[str], description: str, byoi_support: bool = False):
        """
        Add new realm mapping (for future BYOI support).
        
        Args:
            realm_name: Name of the realm
            abstractions: List of allowed abstractions
            description: Description of realm capabilities
            byoi_support: Whether realm supports BYOI
        """
        self.REALM_ABSTRACTION_MAPPINGS[realm_name] = {
            "abstractions": abstractions,
            "description": description,
            "byoi_support": byoi_support
        }
        self.logger.info(f"✅ Added realm mapping for '{realm_name}'")
    
    def update_realm_mapping(self, realm_name: str, abstractions: List[str], description: str = None, byoi_support: bool = None):
        """
        Update existing realm mapping.
        
        Args:
            realm_name: Name of the realm
            abstractions: New list of allowed abstractions
            description: New description (optional)
            byoi_support: New BYOI support flag (optional)
        """
        if realm_name not in self.REALM_ABSTRACTION_MAPPINGS:
            raise ValueError(f"Realm '{realm_name}' not found")
        
        mapping = self.REALM_ABSTRACTION_MAPPINGS[realm_name]
        mapping["abstractions"] = abstractions
        
        if description is not None:
            mapping["description"] = description
        if byoi_support is not None:
            mapping["byoi_support"] = byoi_support
        
        self.logger.info(f"✅ Updated realm mapping for '{realm_name}'")

