#!/usr/bin/env python3
"""
Test Utilities for Business Enablement Realm Tests

Provides helper functions for:
- Creating test files of various types
- Managing test file lifecycle
- Content Steward integration for file storage
- Test data management
"""

import tempfile
import os
from typing import Dict, Any, Optional, Tuple
from pathlib import Path


class TestFileManager:
    """Manages test file creation and lifecycle."""
    
    @staticmethod
    def create_text_file(content: str = "Test text content\nLine 2\nLine 3") -> Tuple[str, bytes]:
        """Create a temporary text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        with open(temp_path, 'rb') as f:
            file_data = f.read()
        
        return temp_path, file_data
    
    @staticmethod
    def create_cobol_copybook_file() -> Tuple[str, bytes]:
        """Create a temporary COBOL copybook file (.cpy)."""
        copybook_content = """       01  CUSTOMER-RECORD.
           05  CUSTOMER-ID          PIC X(10).
           05  CUSTOMER-NAME        PIC X(50).
           05  CUSTOMER-ADDRESS     PIC X(100).
           05  CUSTOMER-BALANCE     PIC S9(9)V99 COMP-3.
           05  CUSTOMER-STATUS      PIC X(1).
               88  ACTIVE           VALUE 'A'.
               88  INACTIVE         VALUE 'I'.
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpy', delete=False) as f:
            f.write(copybook_content)
            temp_path = f.name
        
        with open(temp_path, 'rb') as f:
            file_data = f.read()
        
        return temp_path, file_data
    
    @staticmethod
    def create_mainframe_binary_file() -> Tuple[str, bytes]:
        """Create a temporary Mainframe binary file (.bin)."""
        # Create a simple binary file with some structured data
        # This simulates a mainframe binary file format
        binary_data = bytes([
            0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
            0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F,
            0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
            0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F
        ])
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            f.write(binary_data)
            temp_path = f.name
        
        with open(temp_path, 'rb') as f:
            file_data = f.read()
        
        return temp_path, file_data
    
    @staticmethod
    def create_html_file(content: str = "<html><body><h1>Test</h1><p>Content</p></body></html>") -> Tuple[str, bytes]:
        """Create a temporary HTML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        with open(temp_path, 'rb') as f:
            file_data = f.read()
        
        return temp_path, file_data
    
    @staticmethod
    def create_csv_file(content: str = "Name,Age,City\nJohn,30,New York\nJane,25,Boston") -> Tuple[str, bytes]:
        """Create a temporary CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        with open(temp_path, 'rb') as f:
            file_data = f.read()
        
        return temp_path, file_data
    
    @staticmethod
    def cleanup_file(file_path: str):
        """Clean up a temporary file."""
        if os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except Exception:
                pass  # Ignore cleanup errors


class ContentStewardHelper:
    """
    Enhanced helper for Content Steward integration in tests.
    
    Provides consistent API for file storage operations with:
    - Better validation and error handling
    - Automatic cleanup tracking
    - Support for both Content Steward and FileManagementAbstraction
    """
    
    def __init__(self, storage_api: Any, user_context: Dict[str, Any]):
        """
        Initialize storage helper.
        
        CRITICAL: This helper NEVER touches GOOGLE_APPLICATION_CREDENTIALS.
        Just wraps existing storage API (which already protects SSH credentials).
        
        Args:
            storage_api: Content Steward SOA API or FileManagementAbstraction
            user_context: User context for API calls (required)
        """
        if not storage_api:
            raise ValueError("Storage API is required")
        if not user_context:
            raise ValueError("User context is required")
        
        self.storage = storage_api
        self.user_context = user_context
        self.stored_files: list = []  # Track stored files for cleanup
        self.storage_type = self._detect_storage_type()
    
    def _detect_storage_type(self) -> str:
        """Detect storage type (Content Steward or FileManagementAbstraction)."""
        if hasattr(self.storage, 'process_upload'):
            return "content_steward"
        elif hasattr(self.storage, 'create_file'):
            return "file_management_abstraction"
        else:
            return "unknown"
    
    async def store_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store file and return file_id.
        
        Supports both Content Steward and FileManagementAbstraction.
        
        Args:
            file_data: File content as bytes
            filename: Original filename
            content_type: Optional content type (e.g., 'text/plain', 'application/pdf')
            metadata: Optional metadata (will be merged with filename metadata)
            
        Returns:
            file_id (uuid) if successful
            
        Raises:
            ValueError: If storage fails
        """
        try:
            # Prepare metadata with filename information
            file_metadata = metadata or {}
            file_metadata.setdefault("filename", filename)
            file_metadata.setdefault("original_filename", filename)
            
            # Extract file extension for file_type
            if "." in filename:
                file_extension = filename.split(".")[-1].lower()
                file_metadata.setdefault("file_type", file_extension)
                file_metadata.setdefault("file_extension", file_extension)
            
            # Route to appropriate storage API
            if self.storage_type == "content_steward":
                result = await self.storage.process_upload(
                    file_data=file_data,
                    content_type=content_type or self._guess_content_type(filename),
                    metadata=file_metadata,
                    user_context=self.user_context
                )
                # Extract file_id from result
                if isinstance(result, dict):
                    file_id = result.get('file_id') or result.get('uuid') or result.get('id')
                else:
                    file_id = str(result) if result else None
            elif self.storage_type == "file_management_abstraction":
                # Use FileManagementAbstraction API
                file_record = {
                    "user_id": self.user_context.get("user_id", "test_user"),
                    "tenant_id": self.user_context.get("tenant_id"),
                    "ui_name": filename,
                    "file_type": file_metadata.get("file_type", "txt"),
                    "file_content": file_data,
                    "mime_type": content_type or self._guess_content_type(filename),
                    **file_metadata
                }
                result = await self.storage.create_file(file_record)
                file_id = result.get("uuid") or result.get("file_id")
            else:
                raise ValueError(f"Unknown storage type: {self.storage_type}")
            
            if not file_id:
                raise ValueError(f"Failed to store file: {filename} (no file_id returned)")
            
            self.stored_files.append(file_id)
            return file_id
            
        except Exception as e:
            error_msg = f"Error storing file via {self.storage_type}: {e}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            raise ValueError(error_msg) from e
    
    async def get_file(self, file_id: str) -> Dict[str, Any]:
        """
        Get file by ID.
        
        Args:
            file_id: File ID (uuid)
            
        Returns:
            File record with metadata and content
            
        Raises:
            ValueError: If file not found
        """
        try:
            if self.storage_type == "content_steward":
                file_record = await self.storage.get_file(file_id)
            elif self.storage_type == "file_management_abstraction":
                file_record = await self.storage.get_file(file_id)
            else:
                raise ValueError(f"Unknown storage type: {self.storage_type}")
            
            if not file_record:
                raise ValueError(f"File not found: {file_id}")
            
            return file_record
        except Exception as e:
            raise ValueError(f"Failed to get file {file_id}: {e}") from e
    
    @staticmethod
    def _guess_content_type(filename: str) -> str:
        """Guess content type from filename."""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        content_types = {
            'txt': 'text/plain',
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls': 'application/vnd.ms-excel',
            'html': 'text/html',
            'xml': 'application/xml',
            'csv': 'text/csv',
            'cpy': 'text/plain',  # COBOL copybook
            'bin': 'application/octet-stream',  # Binary
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg'
        }
        return content_types.get(ext, 'application/octet-stream')
    
    async def cleanup(self):
        """
        Clean up all stored test files.
        
        Supports both Content Steward and FileManagementAbstraction.
        """
        if not self.storage:
            return
        
        for file_id in self.stored_files:
            try:
                if self.storage_type == "content_steward":
                    if hasattr(self.storage, 'delete_file'):
                        await self.storage.delete_file(
                            file_id=file_id,
                            user_context=self.user_context
                        )
                elif self.storage_type == "file_management_abstraction":
                    await self.storage.delete_file(file_id)
            except Exception:
                pass  # Ignore cleanup errors
        
        self.stored_files.clear()
    
    # Alias for backward compatibility
    async def cleanup_stored_files(self):
        """Alias for cleanup() - backward compatibility."""
        await self.cleanup()


class TestDataManager:
    """Manages test data for various services."""
    
    @staticmethod
    def get_validation_test_data() -> Dict[str, Any]:
        """Get test data for validation engine tests."""
        return {
            "valid_data": {
                "name": "John Doe",
                "age": 30,
                "email": "john@example.com",
                "balance": 1000.50
            },
            "invalid_data": {
                "name": "",  # Empty required field
                "age": -5,  # Invalid range
                "email": "not-an-email",  # Invalid format
                "balance": "not-a-number"  # Wrong type
            },
            "validation_rules": {
                "name": {"type": "string", "required": True, "min_length": 1},
                "age": {"type": "integer", "required": True, "min": 0, "max": 150},
                "email": {"type": "string", "required": True, "format": "email"},
                "balance": {"type": "number", "required": True, "min": 0}
            }
        }
    
    @staticmethod
    def get_transformation_test_data() -> Dict[str, Any]:
        """Get test data for transformation engine tests."""
        return {
            "source_data": {
                "first_name": "John",
                "last_name": "Doe",
                "age": 30,
                "city": "New York"
            },
            "target_schema": {
                "full_name": "{{first_name}} {{last_name}}",
                "age": "{{age}}",
                "location": "{{city}}"
            },
            "expected_output": {
                "full_name": "John Doe",
                "age": 30,
                "location": "New York"
            }
        }
    
    @staticmethod
    def get_user_context() -> Dict[str, Any]:
        """Get standard user context for tests."""
        return {
            "user_id": "test_user",
            "tenant_id": "test_tenant",
            "session_id": "test_session",
            "permissions": ["read", "write", "execute"]
        }

