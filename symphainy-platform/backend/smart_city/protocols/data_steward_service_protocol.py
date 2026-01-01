#!/usr/bin/env python3
"""
Data Steward Service Protocol - Consolidated (Content + Data Steward)

Realm-specific protocol for consolidated Data Steward services.
Inherits standard methods from ServiceProtocol.

WHAT (Data Steward Role): I provide complete data lifecycle management (file upload,
storage, retrieval, deletion), governance for all data types (platform, client,
parsed, semantic), and query capabilities for all data types.

HOW (Data Steward Protocol): I provide file lifecycle, data governance, and
compliance capabilities for all data types.

Phase 0.1: Consolidated from Content Steward and Data Steward to eliminate gap
between file lifecycle and data governance.
"""

from typing import Protocol, Dict, Any, List, Optional
from bases.protocols.service_protocol import ServiceProtocol


class DataStewardServiceProtocol(ServiceProtocol, Protocol):
    """
    Protocol for consolidated Data Steward services.
    Inherits standard methods from ServiceProtocol.
    """
    
    # File Lifecycle Methods (from Content Steward)
    async def process_upload(
        self,
        file_data: bytes,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process uploaded file with content analysis and metadata extraction."""
        ...
    
    async def get_file(
        self,
        file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get file by ID."""
        ...
    
    async def get_file_metadata(
        self,
        file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Retrieve metadata for a specific file."""
        ...
    
    async def update_file_metadata(
        self,
        file_id: str,
        metadata_updates: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Update metadata for a specific file."""
        ...
    
    async def delete_file(
        self,
        file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delete file."""
        ...
    
    async def list_files(
        self,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """List files with optional filters."""
        ...
    
    # Data Governance Methods
    async def create_content_policy(
        self,
        data_type: str,
        rules: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create content policy for data type."""
        ...
    
    async def get_policy_for_content(
        self,
        content_type: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get policy for content type."""
        ...
    
    # Lineage Tracking Methods
    async def record_lineage(
        self,
        lineage_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record data lineage."""
        ...
    
    async def get_lineage(
        self,
        asset_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get lineage for asset."""
        ...
    
    # Data Quality Methods
    async def validate_schema(
        self,
        schema_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Validate data schema."""
        ...
    
    async def get_quality_metrics(
        self,
        asset_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get quality metrics for asset."""
        ...
    
    # Compliance Methods
    async def enforce_compliance(
        self,
        asset_id: str,
        compliance_rules: List[str],
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Enforce compliance rules for asset."""
        ...






