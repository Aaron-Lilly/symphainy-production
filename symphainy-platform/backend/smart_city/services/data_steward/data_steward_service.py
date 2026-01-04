#!/usr/bin/env python3
"""
Data Steward Service - Consolidated (Content + Data Steward)

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for complete data lifecycle management,
governance, and query capabilities.

WHAT (Smart City Role): I provide complete data lifecycle management (file upload,
storage, retrieval, deletion), governance for all data types (platform, client,
parsed, semantic), and query capabilities for all data types.

HOW (Service Implementation): I use SmartCityRoleBase with correct infrastructure
abstractions for file management, data governance, and semantic layer access.

Phase 0.1: Consolidated from Content Steward and Data Steward to eliminate gap
between file lifecycle and data governance.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

# Import base and protocol
from bases.smart_city_role_base import SmartCityRoleBase
from backend.smart_city.protocols.data_steward_service_protocol import DataStewardServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.file_lifecycle import FileLifecycle
from .modules.policy_management import PolicyManagement
from .modules.lineage_tracking import LineageTracking
from .modules.quality_compliance import QualityCompliance
from .modules.write_ahead_logging import WriteAheadLogging
from .modules.soa_mcp import SoaMcp
from .modules.utilities import Utilities


class DataStewardService(SmartCityRoleBase, DataStewardServiceProtocol):
    """
    Data Steward Service - Consolidated (Content + Data Steward)
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for complete data lifecycle management,
    governance, and query capabilities.
    
    WHAT (Smart City Role): I provide complete data lifecycle management (file upload,
    storage, retrieval, deletion), governance for all data types (platform, client,
    parsed, semantic), and query capabilities for all data types.
    
    HOW (Service Implementation): I use SmartCityRoleBase with correct infrastructure
    abstractions for file management, data governance, and semantic layer access.
    
    Phase 0.1: Consolidated from Content Steward and Data Steward to eliminate gap
    between file lifecycle and data governance.
    """
    
    def __init__(self, di_container: Any):
        """Initialize Data Steward Service with proper infrastructure mapping."""
        super().__init__(
            service_name="DataStewardService",
            role_name="data_steward",
            di_container=di_container
        )
        
        # Infrastructure Abstractions (will be initialized in initialize())
        self.file_management_abstraction = None  # GCS + Supabase (from Content Steward)
        self.content_metadata_abstraction = None  # ArangoDB (semantic layer)
        self.knowledge_governance_abstraction = None  # ArangoDB + Metadata
        self.state_management_abstraction = None  # ArangoDB for lineage
        self.messaging_abstraction = None  # Redis for caching
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        self.mcp_server_enabled = False
        
        # Service-specific state (backward compatibility)
        self.data_catalog: Dict[str, Dict[str, Any]] = {}
        self.policy_registry: Dict[str, Dict[str, Any]] = {}
        self.lineage_tracking: Dict[str, Dict[str, Any]] = {}
        self.quality_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.file_lifecycle_module = FileLifecycle(self)  # ⭐ NEW: File lifecycle from Content Steward
        from .modules.parsed_file_processing import ParsedFileProcessing
        self.parsed_file_processing_module = ParsedFileProcessing(self)  # ⭐ NEW: Parsed file processing from Content Steward
        self.policy_management_module = PolicyManagement(self)
        self.lineage_tracking_module = LineageTracking(self)
        self.quality_compliance_module = QualityCompliance(self)
        self.write_ahead_logging_module = WriteAheadLogging(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # Logger is initialized by SmartCityRoleBase
        if self.logger:
            self.logger.info("✅ Data Steward Service (Consolidated - Content + Data Steward) initialized")
    
    async def initialize(self) -> bool:
        """Initialize Data Steward Service with proper infrastructure connections."""
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "data_steward_initialize_start",
            success=True
        )
        
        try:
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register capabilities with curator
            # Register capabilities with curator (Phase 2 pattern - simplified for Smart City)
            await self.soa_mcp_module.register_capabilities()
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            # Record health metric
            await self.record_health_metric(
                "data_steward_initialized",
                1.0,
                {"service": "DataStewardService"}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "data_steward_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(
                e,
                "data_steward_initialize",
                {
                    "service": "DataStewardService",
                    "error_type": type(e).__name__
                }
            )
            
            self.service_health = "unhealthy"
            
            # Log failure
            await self.log_operation_with_telemetry(
                "data_steward_initialize_complete",
                success=False,
                details={"error": str(e), "error_type": type(e).__name__}
            )
            
            # Record health metric
            await self.record_health_metric(
                "data_steward_initialized",
                0.0,
                metadata={"error_type": type(e).__name__}
            )
            
            return False
    
    # ============================================================================
    # FILE LIFECYCLE METHODS (from Content Steward)
    # ============================================================================
    
    async def process_upload(
        self,
        file_data: bytes,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process uploaded file with content analysis and metadata extraction."""
        return await self.file_lifecycle_module.process_upload(file_data, content_type, metadata, user_context)
    
    async def get_file(self, file_id: str, user_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get file via file_management infrastructure (SOA API).
        
        Data Steward wraps Public Works file_management and exposes it
        as an SOA API for realm services to access file storage.
        
        Args:
            file_id: ID of file to retrieve
            user_context: Optional user context for security and tenant validation
            
        Returns:
            File data with metadata, or None if not found
        """
        return await self.file_lifecycle_module.get_file(file_id, user_context)
    
    async def get_file_metadata(self, file_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve metadata for a specific file."""
        file_record = await self.file_lifecycle_module.get_file(file_id, user_context)
        if not file_record:
            return {
                "status": "error",
                "error": "File not found",
                "message": f"File {file_id} not found"
            }
        return {
            "file_id": file_id,
            "metadata": file_record.get("metadata", {}),
            "content_type": file_record.get("file_type"),
            "created_at": file_record.get("created_at"),
            "status": "success"
        }
    
    async def update_file_metadata(
        self,
        file_id: str,
        metadata_updates: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update metadata for a specific file."""
        return await self.file_lifecycle_module.update_file_metadata(file_id, metadata_updates, user_context)
    
    async def delete_file(self, file_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Delete file."""
        return await self.file_lifecycle_module.delete_file(file_id, user_context)
    
    async def list_files(
        self,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List files with optional filters."""
        return await self.file_lifecycle_module.list_files(filters, user_context)
    
    # ============================================================================
    # PARSED FILE METHODS (from Content Steward consolidation)
    # ============================================================================
    
    async def store_parsed_file(
        self,
        file_id: str,
        parsed_file_data: bytes,
        format_type: str,
        content_type: str,
        parse_result: Dict[str, Any],
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Store parsed file in GCS and metadata in Supabase parsed_data_files table."""
        return await self.parsed_file_processing_module.store_parsed_file(
            file_id, parsed_file_data, format_type, content_type, parse_result, workflow_id
        )
    
    async def get_parsed_file(
        self,
        parsed_file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get parsed file data and metadata."""
        return await self.parsed_file_processing_module.get_parsed_file(parsed_file_id, user_context)
    
    async def list_parsed_files(
        self,
        file_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """List parsed files for a given original file or for a user."""
        return await self.parsed_file_processing_module.list_parsed_files(file_id, user_id, user_context)
    
    # ============================================================================
    # DATA GOVERNANCE METHODS
    # ============================================================================
    
    async def create_content_policy(self, data_type: str, rules: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
        """Create content policy for data type."""
        # Service-level method delegates to module (module handles utilities)
        return await self.policy_management_module.create_content_policy(data_type, rules, user_context)
    
    async def get_policy_for_content(self, content_type: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get policy for content type."""
        # Service-level method delegates to module (module handles utilities)
        return await self.policy_management_module.get_policy_for_content(content_type, user_context)
    
    # ============================================================================
    # LINEAGE TRACKING METHODS
    # ============================================================================
    
    async def track_lineage(self, lineage_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Track data lineage (SOA API - Phase 3.3).
        
        Wrapper for record_lineage that returns a dict with lineage_id.
        
        Args:
            lineage_data: Lineage data including source_id, target_id, operation, etc.
            user_context: Optional user context for security
            
        Returns:
            Dict with lineage_id and status
        """
        lineage_id = await self.lineage_tracking_module.record_lineage(lineage_data, user_context)
        return {
            "success": True,
            "lineage_id": lineage_id,
            "status": "tracked"
        }
    
    async def record_lineage(self, lineage_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
        """Record data lineage (legacy method name)."""
        # Service-level method delegates to module (module handles utilities)
        return await self.lineage_tracking_module.record_lineage(lineage_data, user_context)
    
    async def get_lineage(self, asset_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get lineage for asset."""
        # Service-level method delegates to module (module handles utilities)
        return await self.lineage_tracking_module.get_lineage(asset_id, user_context)
    
    async def query_lineage(
        self,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query lineage with filters (SOA API - Phase 3.3).
        
        Args:
            filters: Optional filters (asset_id, operation, timestamp_range, etc.)
            user_context: Optional user context for security
            
        Returns:
            List of lineage records matching filters
        """
        return await self.lineage_tracking_module.query_lineage(filters, user_context)
    
    # ============================================================================
    # DATA QUALITY METHODS
    # ============================================================================
    
    async def validate_schema(self, schema_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Validate data schema."""
        # Service-level method delegates to module (module handles utilities)
        return await self.quality_compliance_module.validate_schema(schema_data, user_context)
    
    async def get_quality_metrics(self, asset_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get quality metrics for asset."""
        # Service-level method delegates to module (module handles utilities)
        return await self.quality_compliance_module.get_quality_metrics(asset_id, user_context)
    
    # ============================================================================
    # COMPLIANCE METHODS
    # ============================================================================
    
    async def enforce_compliance(self, asset_id: str, compliance_rules: List[str], user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Enforce compliance rules for asset."""
        # Service-level method delegates to module (module handles utilities)
        return await self.quality_compliance_module.enforce_compliance(asset_id, compliance_rules, user_context)
    
    # ============================================================================
    # WRITE-AHEAD LOGGING METHODS (WAL)
    # ============================================================================
    
    async def write_to_log(
        self,
        namespace: str,
        payload: Dict[str, Any],
        target: str,
        lifecycle: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Write operation to WAL BEFORE execution.
        
        Governance capability - ensures audit trail and durability.
        """
        return await self.write_ahead_logging_module.write_to_log(
            namespace, payload, target, lifecycle, user_context
        )
    
    async def replay_log(
        self,
        namespace: str,
        from_timestamp: datetime,
        to_timestamp: datetime,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Replay operations from WAL for recovery, debugging, or audit.
        
        Governance capability - enables audit and recovery.
        """
        return await self.write_ahead_logging_module.replay_log(
            namespace, from_timestamp, to_timestamp, filters, user_context
        )
    
    async def update_log_status(
        self,
        log_id: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update WAL entry status after operation execution.
        """
        return await self.write_ahead_logging_module.update_log_status(
            log_id, status, result, error, user_context
        )
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate infrastructure mapping."""
        return await self.utilities_module.validate_infrastructure_mapping()
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get Data Steward service capabilities."""
        return await self.utilities_module.get_service_capabilities()
