#!/usr/bin/env python3
"""
Content Management Interface

Interface for content management capabilities provided by the Content Pillar role.
Defines the contract for file upload, parsing, validation, and conversion operations.

WHAT (Business Enablement Role): I manage all content ingestion, parsing, and preparation
HOW (Interface): I define the contract for content management operations
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from utilities import UserContext


class FileType(Enum):
    """Supported file types for content management."""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    CSV = "csv"
    TXT = "txt"
    JSON = "json"
    XML = "xml"
    COBOL = "cobol"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    UNKNOWN = "unknown"


class ProcessingStatus(Enum):
    """File processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# FILE MANAGEMENT UTILITIES - Following Modern Platform Patterns
# =============================================================================
# WHAT (Content Management Role): I need to manage file identifiers and extensions properly
# HOW (Content Management Service): I use utility functions for consistent file handling

def extract_file_components(filename: str) -> tuple[str, str, FileType]:
    """
    Extract filename, extension, and FileType from filename.
    
    WHAT (Content Management Role): I need to separate filename components for proper storage
    HOW (Content Management Service): I extract name, extension, and type separately
    
    Args:
        filename: Original filename with extension
        
    Returns:
        Tuple of (filename_without_extension, extension, FileType)
    """
    if '.' in filename:
        name, ext = filename.rsplit('.', 1)
        try:
            file_type = FileType(ext.lower())
        except ValueError:
            file_type = FileType.UNKNOWN
        return name, f'.{ext}', file_type
    return filename, '', FileType.UNKNOWN

def generate_file_id(filename: str) -> str:
    """
    Generate unique file_id from filename and timestamp.
    
    WHAT (Content Management Role): I need to create unique identifiers for files
    HOW (Content Management Service): I generate file_id using filename and timestamp
    
    Args:
        filename: Original filename
        
    Returns:
        Unique file_id string
    """
    import time
    timestamp = int(time.time())
    name_part = filename.replace(' ', '_').replace('.', '_')[:20]  # Clean and truncate
    return f"{name_part}_{timestamp}"

def detect_mime_type_from_extension(file_extension: str) -> str:
    """
    Detect MIME type from file extension.
    
    WHAT (Content Management Role): I need to determine MIME types for proper handling
    HOW (Content Management Service): I map extensions to MIME types
    
    Args:
        file_extension: File extension (e.g., '.pdf', '.csv')
        
    Returns:
        MIME type string
    """
    mime_map = {
        '.pdf': 'application/pdf',
        '.csv': 'text/csv',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.txt': 'text/plain',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
    }
    
    return mime_map.get(file_extension.lower(), 'application/octet-stream')


@dataclass
class FileMetadata:
    """File metadata structure following modern platform patterns."""
    file_id: str
    filename: str
    file_type: FileType
    file_size: int
    upload_timestamp: datetime
    user_id: str
    session_id: str
    content_hash: str
    mime_type: str
    encoding: Optional[str] = None
    language: Optional[str] = None
    metadata: Dict[str, Any] = None
    status: str = "uploaded"
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class UploadRequest:
    """Request to upload a file."""
    file_data: bytes
    filename: str
    file_type: FileType
    user_id: str
    session_id: str
    metadata: Dict[str, Any] = None
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.options is None:
            self.options = {}


@dataclass
class UploadResponse:
    """Response from file upload."""
    success: bool
    file_id: str
    file_metadata: FileMetadata
    processing_status: ProcessingStatus
    message: str
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class ParseRequest:
    """Request to parse a file."""
    file_id: str
    parse_options: Dict[str, Any]
    user_context: UserContext
    session_id: str
    
    def __post_init__(self):
        if self.parse_options is None:
            self.parse_options = {}


@dataclass
class ParseResponse:
    """Response from file parsing."""
    success: bool
    file_id: str
    parsed_content: Dict[str, Any]
    extracted_metadata: Dict[str, Any]
    processing_time: float
    message: str
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class ConvertRequest:
    """Request to convert file format."""
    file_id: str
    target_format: FileType
    conversion_options: Dict[str, Any]
    user_context: UserContext
    session_id: str
    
    def __post_init__(self):
        if self.conversion_options is None:
            self.conversion_options = {}


@dataclass
class ConvertResponse:
    """Response from file conversion."""
    success: bool
    file_id: str
    converted_file_id: str
    converted_content: bytes
    conversion_metadata: Dict[str, Any]
    processing_time: float
    message: str
    error_details: Optional[Dict[str, Any]] = None


@dataclass
class ValidationRequest:
    """Request to validate file content."""
    file_id: str
    validation_rules: Dict[str, Any]
    user_context: UserContext
    session_id: str
    
    def __post_init__(self):
        if self.validation_rules is None:
            self.validation_rules = {}


@dataclass
class ValidationResponse:
    """Response from file validation."""
    success: bool
    file_id: str
    is_valid: bool
    validation_results: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    message: str


class IContentManagement(ABC):
    """
    Content Management Interface
    
    Defines the contract for content management operations provided by the Content Pillar role.
    Handles file upload, parsing, validation, and conversion operations.
    
    WHAT (Business Enablement Role): I manage all content ingestion, parsing, and preparation
    HOW (Interface): I define the contract for content management operations
    """
    
    @abstractmethod
    async def upload_file(self, request: UploadRequest, user_context: UserContext) -> UploadResponse:
        """
        Upload a file for content management.
        
        Args:
            request: Upload request with file data and metadata
            user_context: User context for authentication and authorization
            
        Returns:
            UploadResponse with upload result and file metadata
        """
        pass
    
    @abstractmethod
    async def parse_file(self, request: ParseRequest) -> ParseResponse:
        """
        Parse a file to extract content and metadata.
        
        Args:
            request: Parse request with file ID and options
            
        Returns:
            ParseResponse with parsed content and metadata
        """
        pass
    
    @abstractmethod
    async def convert_file(self, request: ConvertRequest) -> ConvertResponse:
        """
        Convert a file to a different format.
        
        Args:
            request: Convert request with file ID and target format
            
        Returns:
            ConvertResponse with converted file data
        """
        pass
    
    @abstractmethod
    async def validate_file(self, request: ValidationRequest) -> ValidationResponse:
        """
        Validate file content against specified rules.
        
        Args:
            request: Validation request with file ID and rules
            
        Returns:
            ValidationResponse with validation results
        """
        pass
    
    @abstractmethod
    async def get_file_metadata(self, file_id: str, user_context: UserContext) -> Optional[FileMetadata]:
        """
        Get metadata for a specific file.
        
        Args:
            file_id: The file ID to query
            user_context: User context for authorization
            
        Returns:
            FileMetadata or None if not found
        """
        pass
    
    @abstractmethod
    async def list_user_files(self, user_id: str, user_context: UserContext, 
                             file_type: Optional[FileType] = None, 
                             limit: int = 100, offset: int = 0) -> List[FileMetadata]:
        """
        List files for a specific user.
        
        Args:
            user_id: The user ID to query
            user_context: User context for authorization
            file_type: Optional file type filter
            limit: Maximum number of files to return
            offset: Number of files to skip
            
        Returns:
            List of FileMetadata objects
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Delete a file and its associated data.
        
        Args:
            file_id: The file ID to delete
            user_context: User context for authorization
            
        Returns:
            Dict with deletion status
        """
        pass
    
    @abstractmethod
    async def get_file_content(self, file_id: str, user_context: UserContext) -> bytes:
        """
        Get the raw content of a file.
        
        Args:
            file_id: The file ID to retrieve
            user_context: User context for authorization
            
        Returns:
            Raw file content as bytes
        """
        pass
    
    @abstractmethod
    async def search_files(self, query: str, user_context: UserContext, 
                          file_type: Optional[FileType] = None,
                          limit: int = 100) -> List[FileMetadata]:
        """
        Search files by content or metadata.
        
        Args:
            query: Search query string
            user_context: User context for authorization
            file_type: Optional file type filter
            limit: Maximum number of results
            
        Returns:
            List of matching FileMetadata objects
        """
        pass
    
    @abstractmethod
    async def get_processing_status(self, file_id: str, user_context: UserContext) -> ProcessingStatus:
        """
        Get the current processing status of a file.
        
        Args:
            file_id: The file ID to query
            user_context: User context for authorization
            
        Returns:
            Current processing status
        """
        pass
    
    @abstractmethod
    async def get_content_analytics(self, user_context: UserContext, 
                                   time_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """
        Get content management analytics and statistics.
        
        Args:
            user_context: User context for analytics
            time_range: Optional time range for analytics
            
        Returns:
            Dict with analytics data
        """
        pass
    
    @abstractmethod
    async def batch_upload_files(self, requests: List[UploadRequest], 
                                user_context: UserContext) -> List[UploadResponse]:
        """
        Upload multiple files in a batch operation.
        
        Args:
            requests: List of upload requests
            user_context: User context for authorization
            
        Returns:
            List of upload responses
        """
        pass
    
    @abstractmethod
    async def batch_parse_files(self, file_ids: List[str], parse_options: Dict[str, Any],
                               user_context: UserContext) -> List[ParseResponse]:
        """
        Parse multiple files in a batch operation.
        
        Args:
            file_ids: List of file IDs to parse
            parse_options: Parse options for all files
            user_context: User context for authorization
            
        Returns:
            List of parse responses
        """
        pass
    
    @abstractmethod
    async def get_supported_formats(self) -> Dict[str, List[str]]:
        """
        Get list of supported file formats and conversion options.
        
        Returns:
            Dict mapping file types to supported conversions
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Get health status of the content management service.
        
        Returns:
            Dict with health status information
        """
        pass