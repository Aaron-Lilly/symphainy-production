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
                "session", "state", "auth", "authorization", "tenant",
                "file_management", "content_metadata", "content_schema", 
                "content_insights", "llm", "mcp", "policy", "cache",
                "api_gateway"
                # REMOVED: "messaging", "event_management", "websocket", "event_bus"
                # Smart City should get communication capabilities from Communication Foundation via Platform Gateway
            ],
            "description": "Smart City - First-class citizen with full access (except communication abstractions)",
            "byoi_support": True
        },
        "business_enablement": {
            "abstractions": [
                "content_metadata", "content_schema", "content_insights", 
                "file_management", "llm", "document_intelligence",
                "semantic_data",  # ✅ NEW: For embeddings and semantic graphs
                "bpmn_processing", "sop_processing", "sop_enhancement",
                "strategic_planning", "financial_analysis", "workflow_diagramming_orchestration",
                "visualization", "business_metrics",
                # New file parsing abstractions (5-layer architecture)
                "excel_processing", "csv_processing", "json_processing", "text_processing",
                "pdf_processing", "word_processing", "html_processing", "image_processing",
                "mainframe_processing"
            ],
            "description": "Business workflow capabilities",
            "byoi_support": False
        },
        "content": {
            "abstractions": [
                "file_management", "content_metadata",
                "semantic_data",  # ✅ For embedding creation and storage (Content creates semantic data layer)
                # File parsing abstractions (5-layer architecture) - needed for FileParserService
                "excel_processing", "csv_processing", "json_processing", "text_processing",
                "pdf_processing", "word_processing", "html_processing", "image_processing",
                "mainframe_processing"
            ],
            "description": "Content processing, file parsing, and semantic data layer creation",
            "byoi_support": False
        },
        "solution": {
            "abstractions": [
                "llm", "content_metadata", "file_management",
                "semantic_data"  # ✅ For embedding retrieval via FrontendGatewayService (platform-wide gateway)
            ],
            "description": "Solution design capabilities",
            "byoi_support": False
        },
        "journey": {
            "abstractions": [
                "llm", "session", "content_metadata",
                "semantic_data"  # ✅ For embedding creation and semantic layer access (ContentJourneyOrchestrator)
            ],
            "description": "Journey orchestration capabilities",
            "byoi_support": False
        },
        "insights": {
            "abstractions": [
                "file_management", "content_metadata", "content_insights",
                "llm", "semantic_data",  # For data analysis and semantic queries
                "visualization", "business_metrics"  # For visualization and metrics
            ],
            "description": "Data analysis and insights generation capabilities",
            "byoi_support": False
        }
    }
    
    def __init__(self, public_works_foundation: Any):
        """
        Initialize Platform Infrastructure Gateway.
        
        Args:
            public_works_foundation: Public Works Foundation Service instance
        """
        self.public_works_foundation = public_works_foundation
        self.logger = logging.getLogger(f"{__name__}.PlatformGateway")
        self.is_initialized = False
        
        # Metrics tracking
        self.access_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "denied_requests": 0,
            "realm_access_counts": {}
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

