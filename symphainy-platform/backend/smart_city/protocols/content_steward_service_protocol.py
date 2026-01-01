#!/usr/bin/env python3
"""
Content Steward Service Protocol

Defines the protocol for Content Steward Service operations including
content processing, policy enforcement, and metadata extraction.
"""

from typing import Protocol, Dict, Any, List, Optional, runtime_checkable
from datetime import datetime


@runtime_checkable
class ContentStewardServiceProtocol(Protocol):
    """Protocol for Content Steward Service operations."""
    
    # Core Content Processing Methods
    async def process_upload(self, file_data: bytes, content_type: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process uploaded file with content analysis and metadata extraction."""
        ...
    
    async def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Retrieve metadata for a specific file."""
        ...
    
    async def update_file_metadata(self, file_id: str, metadata_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update metadata for a specific file."""
        ...
    
    async def process_file_content(self, file_id: str, processing_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process file content with specified options."""
        ...
    
    # Format Conversion Methods
    async def convert_file_format(self, file_id: str, source_format: str, target_format: str, 
                                conversion_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert file from source format to target format."""
        ...
    
    async def batch_convert_formats(self, file_ids: List[str], target_format: str, 
                                  conversion_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert multiple files to target format in batch."""
        ...
    
    # Data Optimization Methods
    async def optimize_data(self, file_id: str, optimization_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize data for specific use cases."""
        ...
    
    async def compress_data(self, file_id: str, compression_type: str = "gzip") -> Dict[str, Any]:
        """Compress data using specified compression type."""
        ...
    
    async def validate_output(self, file_id: str, expected_format: str) -> Dict[str, Any]:
        """Validate output format and quality."""
        ...
    
    # Content Validation Methods
    async def validate_content(self, content_data: bytes, content_type: str) -> bool:
        """Validate content against policies and standards."""
        ...
    
    async def get_quality_metrics(self, asset_id: str) -> Dict[str, Any]:
        """Get quality metrics for content asset."""
        ...
    
    # Metadata and Lineage Methods
    async def get_asset_metadata(self, asset_id: str) -> Dict[str, Any]:
        """Get comprehensive metadata for content asset."""
        ...
    
    async def get_lineage(self, asset_id: str) -> Dict[str, Any]:
        """Get lineage information for content asset."""
        ...
    
    # Status and Capabilities Methods
    async def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status and statistics."""
        ...
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and configuration."""
        ...
