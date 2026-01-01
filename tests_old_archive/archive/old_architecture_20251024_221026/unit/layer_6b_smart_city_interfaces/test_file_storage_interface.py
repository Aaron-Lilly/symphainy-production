#!/usr/bin/env python3
"""
Tests for File Storage Interface.

Tests the file storage interface data models and concrete implementations
for Smart City file operations.
"""

import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add the symphainy-platform path
platform_path = project_root / "symphainy-source" / "symphainy-platform"
sys.path.insert(0, str(platform_path))

from backend.smart_city.interfaces.file_storage_interface import (
    StorageTier,
    FileType,
    FileMetadata,
    FileUploadRequest,
    FileUploadResponse,
    FileDownloadRequest,
    FileDownloadResponse,
    FileSearchRequest,
    FileSearchResponse,
    IFileStorage
)
from tests.unit.layer_5b_smart_city_interfaces.test_base import SmartCityInterfacesTestBase


class TestStorageTier:
    """Test StorageTier enum."""
    
    def test_storage_tier_values(self):
        """Test storage tier enum values."""
        assert StorageTier.HOT.value == "hot"
        assert StorageTier.WARM.value == "warm"
        assert StorageTier.COLD.value == "cold"
        assert StorageTier.ARCHIVE.value == "archive"


class TestFileType:
    """Test FileType enum."""
    
    def test_file_type_values(self):
        """Test file type enum values."""
        assert FileType.DOCUMENT.value == "document"
        assert FileType.IMAGE.value == "image"
        assert FileType.VIDEO.value == "video"
        assert FileType.AUDIO.value == "audio"
        assert FileType.DATA.value == "data"
        assert FileType.CODE.value == "code"
        assert FileType.CONFIG.value == "config"
        assert FileType.LOG.value == "log"


class TestFileMetadata:
    """Test FileMetadata data model."""
    
    def test_file_metadata_creation(self):
        """Test creating a file metadata."""
        file_metadata = FileMetadata(
            file_id="file_001",
            filename="document.pdf",
            file_type=FileType.DOCUMENT,
            size_bytes=1024000,
            content_type="application/pdf",
            storage_tier=StorageTier.HOT,
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            updated_at=datetime(2024, 1, 1, 0, 0, 0),
            owner_id="user_001",
            tags=["contract", "legal"],
            description="Important contract document",
            checksum="abc123def456",
            metadata={"department": "legal", "confidential": True}
        )
        
        assert file_metadata.file_id == "file_001"
        assert file_metadata.filename == "document.pdf"
        assert file_metadata.file_type == FileType.DOCUMENT
        assert file_metadata.size_bytes == 1024000
        assert file_metadata.content_type == "application/pdf"
        assert file_metadata.storage_tier == StorageTier.HOT
        assert file_metadata.created_at == datetime(2024, 1, 1, 0, 0, 0)
        assert file_metadata.updated_at == datetime(2024, 1, 1, 0, 0, 0)
        assert file_metadata.owner_id == "user_001"
        assert file_metadata.tags == ["contract", "legal"]
        assert file_metadata.description == "Important contract document"
        assert file_metadata.checksum == "abc123def456"
        assert file_metadata.metadata["department"] == "legal"
        assert file_metadata.metadata["confidential"] is True
    
    def test_file_metadata_defaults(self):
        """Test file metadata with default values."""
        file_metadata = FileMetadata(
            file_id="file_002",
            filename="image.jpg",
            file_type=FileType.IMAGE,
            size_bytes=512000,
            content_type="image/jpeg",
            storage_tier=StorageTier.WARM,
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            updated_at=datetime(2024, 1, 1, 0, 0, 0),
            owner_id="user_002"
        )
        
        assert file_metadata.file_id == "file_002"
        assert file_metadata.filename == "image.jpg"
        assert file_metadata.file_type == FileType.IMAGE
        assert file_metadata.tags == []
        assert file_metadata.description == ""
        assert file_metadata.checksum == ""
        assert file_metadata.metadata == {}


class TestFileUploadRequest:
    """Test FileUploadRequest data model."""
    
    def test_file_upload_request_creation(self):
        """Test creating a file upload request."""
        request = FileUploadRequest(
            filename="document.pdf",
            content_type="application/pdf",
            file_data=b"This is test file content",
            owner_id="user_001",
            storage_tier=StorageTier.HOT,
            tags=["contract", "legal"],
            description="Important contract document",
            metadata={"department": "legal"}
        )
        
        assert request.filename == "document.pdf"
        assert request.content_type == "application/pdf"
        assert request.file_data == b"This is test file content"
        assert request.owner_id == "user_001"
        assert request.storage_tier == StorageTier.HOT
        assert request.tags == ["contract", "legal"]
        assert request.description == "Important contract document"
        assert request.metadata["department"] == "legal"
    
    def test_file_upload_request_defaults(self):
        """Test file upload request with default values."""
        request = FileUploadRequest(
            filename="image.jpg",
            content_type="image/jpeg",
            file_data=b"image data",
            owner_id="user_002"
        )
        
        assert request.filename == "image.jpg"
        assert request.content_type == "image/jpeg"
        assert request.file_data == b"image data"
        assert request.owner_id == "user_002"
        assert request.storage_tier == StorageTier.HOT
        assert request.tags == []
        assert request.description == ""
        assert request.metadata == {}


class TestFileUploadResponse:
    """Test FileUploadResponse data model."""
    
    def test_file_upload_response_success(self):
        """Test creating a successful file upload response."""
        response = FileUploadResponse(
            success=True,
            file_id="file_001",
            filename="document.pdf",
            size_bytes=1024000,
            storage_tier=StorageTier.HOT,
            checksum="abc123def456"
        )
        
        assert response.success is True
        assert response.file_id == "file_001"
        assert response.filename == "document.pdf"
        assert response.size_bytes == 1024000
        assert response.storage_tier == StorageTier.HOT
        assert response.checksum == "abc123def456"
        assert response.error_message is None
    
    def test_file_upload_response_failure(self):
        """Test creating a failed file upload response."""
        response = FileUploadResponse(
            success=False,
            file_id="",
            filename="document.pdf",
            size_bytes=0,
            storage_tier=StorageTier.HOT,
            checksum="",
            error_message="File too large"
        )
        
        assert response.success is False
        assert response.file_id == ""
        assert response.filename == "document.pdf"
        assert response.size_bytes == 0
        assert response.checksum == ""
        assert response.error_message == "File too large"


class TestFileDownloadRequest:
    """Test FileDownloadRequest data model."""
    
    def test_file_download_request_creation(self):
        """Test creating a file download request."""
        request = FileDownloadRequest(
            file_id="file_001",
            include_metadata=True
        )
        
        assert request.file_id == "file_001"
        assert request.include_metadata is True
    
    def test_file_download_request_defaults(self):
        """Test file download request with default values."""
        request = FileDownloadRequest(file_id="file_002")
        
        assert request.file_id == "file_002"
        assert request.include_metadata is True


class TestFileDownloadResponse:
    """Test FileDownloadResponse data model."""
    
    def test_file_download_response_success(self):
        """Test creating a successful file download response."""
        file_metadata = FileMetadata(
            file_id="file_001",
            filename="document.pdf",
            file_type=FileType.DOCUMENT,
            size_bytes=1024000,
            content_type="application/pdf",
            storage_tier=StorageTier.HOT,
            created_at=datetime(2024, 1, 1, 0, 0, 0),
            updated_at=datetime(2024, 1, 1, 0, 0, 0),
            owner_id="user_001"
        )
        
        response = FileDownloadResponse(
            success=True,
            file_data=b"This is test file content",
            filename="document.pdf",
            content_type="application/pdf",
            metadata=file_metadata
        )
        
        assert response.success is True
        assert response.file_data == b"This is test file content"
        assert response.filename == "document.pdf"
        assert response.content_type == "application/pdf"
        assert response.metadata == file_metadata
        assert response.error_message is None
    
    def test_file_download_response_failure(self):
        """Test creating a failed file download response."""
        response = FileDownloadResponse(
            success=False,
            file_data=b"",
            filename="",
            content_type="",
            metadata=None,
            error_message="File not found"
        )
        
        assert response.success is False
        assert response.file_data == b""
        assert response.filename == ""
        assert response.content_type == ""
        assert response.metadata is None
        assert response.error_message == "File not found"


class TestFileStorageInterface(SmartCityInterfacesTestBase):
    """Test IFileStorage implementation."""
    
    @pytest.mark.asyncio
    async def test_file_storage_interface_initialization(self, mock_supabase_client, mock_utility_foundation, mock_public_works_foundation):
        """Test file storage interface initialization."""
        # Create a concrete implementation for testing
        class TestFileStorageInterface(IFileStorage):
            def __init__(self):
                self.files = {}
                self.file_count = 0
            
            async def upload_file(self, request: FileUploadRequest, user_context=None) -> FileUploadResponse:
                self.file_count += 1
                file_id = f"file_{self.file_count}"
                checksum = f"checksum_{file_id}"
                
                self.files[file_id] = {
                    "file_id": file_id,
                    "filename": request.filename,
                    "file_type": FileType.DOCUMENT,  # Default for testing
                    "size_bytes": len(request.file_data),
                    "content_type": request.content_type,
                    "storage_tier": request.storage_tier,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "owner_id": request.owner_id,
                    "tags": request.tags,
                    "description": request.description,
                    "checksum": checksum,
                    "metadata": request.metadata,
                    "file_data": request.file_data
                }
                
                return FileUploadResponse(
                    success=True,
                    file_id=file_id,
                    filename=request.filename,
                    size_bytes=len(request.file_data),
                    storage_tier=request.storage_tier,
                    checksum=checksum
                )
            
            async def download_file(self, request: FileDownloadRequest, user_context=None) -> FileDownloadResponse:
                file_data = self.files.get(request.file_id)
                if file_data:
                    metadata = None
                    if request.include_metadata:
                        metadata = FileMetadata(
                            file_id=file_data["file_id"],
                            filename=file_data["filename"],
                            file_type=file_data["file_type"],
                            size_bytes=file_data["size_bytes"],
                            content_type=file_data["content_type"],
                            storage_tier=file_data["storage_tier"],
                            created_at=file_data["created_at"],
                            updated_at=file_data["updated_at"],
                            owner_id=file_data["owner_id"],
                            tags=file_data["tags"],
                            description=file_data["description"],
                            checksum=file_data["checksum"],
                            metadata=file_data["metadata"]
                        )
                    
                    return FileDownloadResponse(
                        success=True,
                        file_data=file_data["file_data"],
                        filename=file_data["filename"],
                        content_type=file_data["content_type"],
                        metadata=metadata
                    )
                else:
                    return FileDownloadResponse(
                        success=False,
                        file_data=b"",
                        filename="",
                        content_type="",
                        metadata=None,
                        error_message="File not found"
                    )
            
            async def get_file_metadata(self, file_id: str, user_context=None) -> Optional[FileMetadata]:
                file_data = self.files.get(file_id)
                if file_data:
                    return FileMetadata(
                        file_id=file_data["file_id"],
                        filename=file_data["filename"],
                        file_type=file_data["file_type"],
                        size_bytes=file_data["size_bytes"],
                        content_type=file_data["content_type"],
                        storage_tier=file_data["storage_tier"],
                        created_at=file_data["created_at"],
                        updated_at=file_data["updated_at"],
                        owner_id=file_data["owner_id"],
                        tags=file_data["tags"],
                        description=file_data["description"],
                        checksum=file_data["checksum"],
                        metadata=file_data["metadata"]
                    )
                return None
            
            async def update_file_metadata(self, file_id: str, metadata_updates: Dict[str, Any], user_context=None) -> Dict[str, Any]:
                if file_id in self.files:
                    self.files[file_id]["metadata"].update(metadata_updates)
                    self.files[file_id]["updated_at"] = datetime.utcnow()
                    return {"status": "updated", "file_id": file_id, "message": "File metadata updated successfully"}
                return {"status": "not_found", "file_id": file_id, "message": "File not found"}
            
            async def delete_file(self, file_id: str, user_context=None) -> Dict[str, Any]:
                if file_id in self.files:
                    del self.files[file_id]
                    return {"status": "deleted", "file_id": file_id, "message": "File deleted successfully"}
                return {"status": "not_found", "file_id": file_id, "message": "File not found"}
            
            async def search_files(self, request: FileSearchRequest, user_context=None) -> FileSearchResponse:
                matching_files = []
                
                for file_data in self.files.values():
                    # Simple search logic for testing
                    if request.query.lower() in file_data["filename"].lower():
                        if not request.file_types or file_data["file_type"] in request.file_types:
                            if not request.storage_tiers or file_data["storage_tier"] in request.storage_tiers:
                                if not request.owner_id or file_data["owner_id"] == request.owner_id:
                                    metadata = FileMetadata(
                                        file_id=file_data["file_id"],
                                        filename=file_data["filename"],
                                        file_type=file_data["file_type"],
                                        size_bytes=file_data["size_bytes"],
                                        content_type=file_data["content_type"],
                                        storage_tier=file_data["storage_tier"],
                                        created_at=file_data["created_at"],
                                        updated_at=file_data["updated_at"],
                                        owner_id=file_data["owner_id"],
                                        tags=file_data["tags"],
                                        description=file_data["description"],
                                        checksum=file_data["checksum"],
                                        metadata=file_data["metadata"]
                                    )
                                    matching_files.append(metadata)
                
                # Apply limit and offset
                total_count = len(matching_files)
                start_idx = request.offset
                end_idx = start_idx + request.limit
                files = matching_files[start_idx:end_idx]
                has_more = end_idx < total_count
                
                return FileSearchResponse(
                    success=True,
                    files=files,
                    total_count=total_count,
                    has_more=has_more
                )
            
            async def move_file_tier(self, file_id: str, new_tier: StorageTier, user_context=None) -> Dict[str, Any]:
                if file_id in self.files:
                    self.files[file_id]["storage_tier"] = new_tier
                    self.files[file_id]["updated_at"] = datetime.utcnow()
                    return {"status": "moved", "file_id": file_id, "new_tier": new_tier.value, "message": "File moved to new storage tier"}
                return {"status": "not_found", "file_id": file_id, "message": "File not found"}
            
            async def copy_file(self, file_id: str, new_filename: str, user_context=None) -> Dict[str, Any]:
                if file_id in self.files:
                    self.file_count += 1
                    new_file_id = f"file_{self.file_count}"
                    original_data = self.files[file_id]
                    
                    self.files[new_file_id] = {
                        "file_id": new_file_id,
                        "filename": new_filename,
                        "file_type": original_data["file_type"],
                        "size_bytes": original_data["size_bytes"],
                        "content_type": original_data["content_type"],
                        "storage_tier": original_data["storage_tier"],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "owner_id": original_data["owner_id"],
                        "tags": original_data["tags"].copy(),
                        "description": f"Copy of {original_data['filename']}",
                        "checksum": f"checksum_{new_file_id}",
                        "metadata": original_data["metadata"].copy(),
                        "file_data": original_data["file_data"]
                    }
                    
                    return {"status": "copied", "file_id": new_file_id, "original_file_id": file_id, "message": "File copied successfully"}
                return {"status": "not_found", "file_id": file_id, "message": "File not found"}
            
            async def get_file_checksum(self, file_id: str, user_context=None) -> str:
                if file_id in self.files:
                    return self.files[file_id]["checksum"]
                return ""
            
            async def verify_file_integrity(self, file_id: str, user_context=None) -> bool:
                if file_id in self.files:
                    # Simple integrity check - in real implementation would verify checksum
                    return True
                return False
            
            async def list_user_files(self, owner_id: str, limit: int = 100, offset: int = 0, user_context=None) -> List[FileMetadata]:
                user_files = []
                for file_data in self.files.values():
                    if file_data["owner_id"] == owner_id:
                        metadata = FileMetadata(
                            file_id=file_data["file_id"],
                            filename=file_data["filename"],
                            file_type=file_data["file_type"],
                            size_bytes=file_data["size_bytes"],
                            content_type=file_data["content_type"],
                            storage_tier=file_data["storage_tier"],
                            created_at=file_data["created_at"],
                            updated_at=file_data["updated_at"],
                            owner_id=file_data["owner_id"],
                            tags=file_data["tags"],
                            description=file_data["description"],
                            checksum=file_data["checksum"],
                            metadata=file_data["metadata"]
                        )
                        user_files.append(metadata)
                
                # Apply limit and offset
                start_idx = offset
                end_idx = start_idx + limit
                return user_files[start_idx:end_idx]
            
            async def cleanup_orphaned_files(self, user_context=None) -> Dict[str, Any]:
                # Simple cleanup - in real implementation would check for orphaned files
                return {"status": "completed", "orphaned_files_removed": 0, "message": "No orphaned files found"}
            
            async def get_storage_analytics(self, user_context=None) -> Dict[str, Any]:
                total_files = len(self.files)
                total_size = sum(file_data["size_bytes"] for file_data in self.files.values())
                tier_counts = {}
                
                for file_data in self.files.values():
                    tier = file_data["storage_tier"].value
                    tier_counts[tier] = tier_counts.get(tier, 0) + 1
                
                return {
                    "total_files": total_files,
                    "total_size_bytes": total_size,
                    "tier_distribution": tier_counts,
                    "average_file_size": total_size / total_files if total_files > 0 else 0
                }
            
            async def optimize_storage(self, user_context=None) -> Dict[str, Any]:
                # Simple optimization - in real implementation would move files to appropriate tiers
                return {"status": "completed", "files_optimized": 0, "message": "Storage optimization completed"}
        
        interface = TestFileStorageInterface()
        
        assert interface is not None
        assert hasattr(interface, 'upload_file')
        assert hasattr(interface, 'download_file')
        assert hasattr(interface, 'get_file_metadata')
        assert hasattr(interface, 'update_file_metadata')
        assert hasattr(interface, 'delete_file')
        assert hasattr(interface, 'search_files')
        assert hasattr(interface, 'move_file_tier')
        assert hasattr(interface, 'copy_file')
        assert hasattr(interface, 'get_file_checksum')
        assert hasattr(interface, 'verify_file_integrity')
        assert hasattr(interface, 'list_user_files')
        assert hasattr(interface, 'cleanup_orphaned_files')
        assert hasattr(interface, 'get_storage_analytics')
        assert hasattr(interface, 'optimize_storage')
    
    @pytest.mark.asyncio
    async def test_file_storage_interface_operations(self, mock_supabase_client, mock_utility_foundation, mock_public_works_foundation):
        """Test file storage interface operations."""
        class TestFileStorageInterface(IFileStorage):
            def __init__(self):
                self.files = {}
                self.file_count = 0
            
            async def upload_file(self, request: FileUploadRequest, user_context=None) -> FileUploadResponse:
                self.file_count += 1
                file_id = f"file_{self.file_count}"
                checksum = f"checksum_{file_id}"
                
                self.files[file_id] = {
                    "file_id": file_id,
                    "filename": request.filename,
                    "file_type": FileType.DOCUMENT,
                    "size_bytes": len(request.file_data),
                    "content_type": request.content_type,
                    "storage_tier": request.storage_tier,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "owner_id": request.owner_id,
                    "tags": request.tags,
                    "description": request.description,
                    "checksum": checksum,
                    "metadata": request.metadata,
                    "file_data": request.file_data
                }
                
                return FileUploadResponse(
                    success=True,
                    file_id=file_id,
                    filename=request.filename,
                    size_bytes=len(request.file_data),
                    storage_tier=request.storage_tier,
                    checksum=checksum
                )
            
            async def download_file(self, request: FileDownloadRequest, user_context=None) -> FileDownloadResponse:
                file_data = self.files.get(request.file_id)
                if file_data:
                    metadata = None
                    if request.include_metadata:
                        metadata = FileMetadata(
                            file_id=file_data["file_id"],
                            filename=file_data["filename"],
                            file_type=file_data["file_type"],
                            size_bytes=file_data["size_bytes"],
                            content_type=file_data["content_type"],
                            storage_tier=file_data["storage_tier"],
                            created_at=file_data["created_at"],
                            updated_at=file_data["updated_at"],
                            owner_id=file_data["owner_id"],
                            tags=file_data["tags"],
                            description=file_data["description"],
                            checksum=file_data["checksum"],
                            metadata=file_data["metadata"]
                        )
                    
                    return FileDownloadResponse(
                        success=True,
                        file_data=file_data["file_data"],
                        filename=file_data["filename"],
                        content_type=file_data["content_type"],
                        metadata=metadata
                    )
                else:
                    return FileDownloadResponse(
                        success=False,
                        file_data=b"",
                        filename="",
                        content_type="",
                        metadata=None,
                        error_message="File not found"
                    )
            
            async def get_file_metadata(self, file_id: str, user_context=None) -> Optional[FileMetadata]:
                file_data = self.files.get(file_id)
                if file_data:
                    return FileMetadata(
                        file_id=file_data["file_id"],
                        filename=file_data["filename"],
                        file_type=file_data["file_type"],
                        size_bytes=file_data["size_bytes"],
                        content_type=file_data["content_type"],
                        storage_tier=file_data["storage_tier"],
                        created_at=file_data["created_at"],
                        updated_at=file_data["updated_at"],
                        owner_id=file_data["owner_id"],
                        tags=file_data["tags"],
                        description=file_data["description"],
                        checksum=file_data["checksum"],
                        metadata=file_data["metadata"]
                    )
                return None
            
            async def update_file_metadata(self, file_id: str, metadata_updates: Dict[str, Any], user_context=None) -> Dict[str, Any]:
                if file_id in self.files:
                    self.files[file_id]["metadata"].update(metadata_updates)
                    self.files[file_id]["updated_at"] = datetime.utcnow()
                    return {"status": "updated", "file_id": file_id, "message": "File metadata updated successfully"}
                return {"status": "not_found", "file_id": file_id, "message": "File not found"}
            
            async def delete_file(self, file_id: str, user_context=None) -> Dict[str, Any]:
                if file_id in self.files:
                    del self.files[file_id]
                    return {"status": "deleted", "file_id": file_id, "message": "File deleted successfully"}
                return {"status": "not_found", "file_id": file_id, "message": "File not found"}
            
            async def search_files(self, request: FileSearchRequest, user_context=None) -> FileSearchResponse:
                matching_files = []
                
                for file_data in self.files.values():
                    if request.query.lower() in file_data["filename"].lower():
                        if not request.file_types or file_data["file_type"] in request.file_types:
                            if not request.storage_tiers or file_data["storage_tier"] in request.storage_tiers:
                                if not request.owner_id or file_data["owner_id"] == request.owner_id:
                                    metadata = FileMetadata(
                                        file_id=file_data["file_id"],
                                        filename=file_data["filename"],
                                        file_type=file_data["file_type"],
                                        size_bytes=file_data["size_bytes"],
                                        content_type=file_data["content_type"],
                                        storage_tier=file_data["storage_tier"],
                                        created_at=file_data["created_at"],
                                        updated_at=file_data["updated_at"],
                                        owner_id=file_data["owner_id"],
                                        tags=file_data["tags"],
                                        description=file_data["description"],
                                        checksum=file_data["checksum"],
                                        metadata=file_data["metadata"]
                                    )
                                    matching_files.append(metadata)
                
                total_count = len(matching_files)
                start_idx = request.offset
                end_idx = start_idx + request.limit
                files = matching_files[start_idx:end_idx]
                has_more = end_idx < total_count
                
                return FileSearchResponse(
                    success=True,
                    files=files,
                    total_count=total_count,
                    has_more=has_more
                )
            
            async def move_file_tier(self, file_id: str, new_tier: StorageTier, user_context=None) -> Dict[str, Any]:
                if file_id in self.files:
                    self.files[file_id]["storage_tier"] = new_tier
                    self.files[file_id]["updated_at"] = datetime.utcnow()
                    return {"status": "moved", "file_id": file_id, "new_tier": new_tier.value, "message": "File moved to new storage tier"}
                return {"status": "not_found", "file_id": file_id, "message": "File not found"}
            
            async def copy_file(self, file_id: str, new_filename: str, user_context=None) -> Dict[str, Any]:
                if file_id in self.files:
                    self.file_count += 1
                    new_file_id = f"file_{self.file_count}"
                    original_data = self.files[file_id]
                    
                    self.files[new_file_id] = {
                        "file_id": new_file_id,
                        "filename": new_filename,
                        "file_type": original_data["file_type"],
                        "size_bytes": original_data["size_bytes"],
                        "content_type": original_data["content_type"],
                        "storage_tier": original_data["storage_tier"],
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "owner_id": original_data["owner_id"],
                        "tags": original_data["tags"].copy(),
                        "description": f"Copy of {original_data['filename']}",
                        "checksum": f"checksum_{new_file_id}",
                        "metadata": original_data["metadata"].copy(),
                        "file_data": original_data["file_data"]
                    }
                    
                    return {"status": "copied", "file_id": new_file_id, "original_file_id": file_id, "message": "File copied successfully"}
                return {"status": "not_found", "file_id": file_id, "message": "File not found"}
            
            async def get_file_checksum(self, file_id: str, user_context=None) -> str:
                if file_id in self.files:
                    return self.files[file_id]["checksum"]
                return ""
            
            async def verify_file_integrity(self, file_id: str, user_context=None) -> bool:
                if file_id in self.files:
                    # Simple integrity check - in real implementation would verify checksum
                    return True
                return False
            
            async def list_user_files(self, owner_id: str, limit: int = 100, offset: int = 0, user_context=None) -> List[FileMetadata]:
                user_files = []
                for file_data in self.files.values():
                    if file_data["owner_id"] == owner_id:
                        metadata = FileMetadata(
                            file_id=file_data["file_id"],
                            filename=file_data["filename"],
                            file_type=file_data["file_type"],
                            size_bytes=file_data["size_bytes"],
                            content_type=file_data["content_type"],
                            storage_tier=file_data["storage_tier"],
                            created_at=file_data["created_at"],
                            updated_at=file_data["updated_at"],
                            owner_id=file_data["owner_id"],
                            tags=file_data["tags"],
                            description=file_data["description"],
                            checksum=file_data["checksum"],
                            metadata=file_data["metadata"]
                        )
                        user_files.append(metadata)
                
                # Apply limit and offset
                start_idx = offset
                end_idx = start_idx + limit
                return user_files[start_idx:end_idx]
            
            async def cleanup_orphaned_files(self, user_context=None) -> Dict[str, Any]:
                # Simple cleanup - in real implementation would check for orphaned files
                return {"status": "completed", "orphaned_files_removed": 0, "message": "No orphaned files found"}
            
            async def get_storage_analytics(self, user_context=None) -> Dict[str, Any]:
                total_files = len(self.files)
                total_size = sum(file_data["size_bytes"] for file_data in self.files.values())
                tier_counts = {}
                
                for file_data in self.files.values():
                    tier = file_data["storage_tier"].value
                    tier_counts[tier] = tier_counts.get(tier, 0) + 1
                
                return {
                    "total_files": total_files,
                    "total_size_bytes": total_size,
                    "tier_distribution": tier_counts,
                    "average_file_size": total_size / total_files if total_files > 0 else 0
                }
            
            async def optimize_storage(self, user_context=None) -> Dict[str, Any]:
                # Simple optimization - in real implementation would move files to appropriate tiers
                return {"status": "completed", "files_optimized": 0, "message": "Storage optimization completed"}
        
        interface = TestFileStorageInterface()
        
        # Test upload_file
        upload_request = FileUploadRequest(
            filename="document.pdf",
            content_type="application/pdf",
            file_data=b"This is test file content",
            owner_id="user_001",
            storage_tier=StorageTier.HOT,
            tags=["contract", "legal"],
            description="Important contract document",
            metadata={"department": "legal"}
        )
        
        upload_response = await interface.upload_file(upload_request)
        assert upload_response.success is True
        assert upload_response.file_id is not None
        assert upload_response.filename == "document.pdf"
        assert upload_response.size_bytes == len(b"This is test file content")
        assert upload_response.storage_tier == StorageTier.HOT
        assert upload_response.checksum is not None
        
        file_id = upload_response.file_id
        
        # Test get_file_metadata
        metadata = await interface.get_file_metadata(file_id)
        assert metadata is not None
        assert metadata.file_id == file_id
        assert metadata.filename == "document.pdf"
        assert metadata.file_type == FileType.DOCUMENT
        assert metadata.size_bytes == len(b"This is test file content")
        assert metadata.content_type == "application/pdf"
        assert metadata.storage_tier == StorageTier.HOT
        assert metadata.owner_id == "user_001"
        assert metadata.tags == ["contract", "legal"]
        assert metadata.description == "Important contract document"
        assert metadata.metadata["department"] == "legal"
        
        # Test download_file
        download_request = FileDownloadRequest(file_id=file_id, include_metadata=True)
        download_response = await interface.download_file(download_request)
        assert download_response.success is True
        assert download_response.file_data == b"This is test file content"
        assert download_response.filename == "document.pdf"
        assert download_response.content_type == "application/pdf"
        assert download_response.metadata is not None
        assert download_response.metadata.file_id == file_id
        
        # Test update_file_metadata
        update_result = await interface.update_file_metadata(file_id, {"confidential": True, "reviewed": True})
        assert update_result["status"] == "updated"
        
        # Verify metadata update
        updated_metadata = await interface.get_file_metadata(file_id)
        assert updated_metadata.metadata["confidential"] is True
        assert updated_metadata.metadata["reviewed"] is True
        assert updated_metadata.metadata["department"] == "legal"  # Should preserve existing metadata
        
        # Test search_files
        search_request = FileSearchRequest(
            query="document",
            file_types=[FileType.DOCUMENT],
            storage_tiers=[StorageTier.HOT],
            owner_id="user_001"
        )
        
        search_response = await interface.search_files(search_request)
        assert search_response.success is True
        assert len(search_response.files) == 1
        assert search_response.files[0].file_id == file_id
        assert search_response.total_count == 1
        assert search_response.has_more is False
        
        # Test move_file_tier
        move_result = await interface.move_file_tier(file_id, StorageTier.COLD)
        assert move_result["status"] == "moved"
        assert move_result["new_tier"] == "cold"
        
        # Verify tier change
        moved_metadata = await interface.get_file_metadata(file_id)
        assert moved_metadata.storage_tier == StorageTier.COLD
        
        # Test copy_file
        copy_result = await interface.copy_file(file_id, "document_copy.pdf")
        assert copy_result["status"] == "copied"
        assert copy_result["original_file_id"] == file_id
        assert copy_result["file_id"] is not None
        
        # Test get_file_checksum
        checksum = await interface.get_file_checksum(file_id)
        assert checksum is not None
        assert checksum.startswith("checksum_")
        
        # Test verify_file_integrity
        integrity_check = await interface.verify_file_integrity(file_id)
        assert integrity_check is True
        
        # Test list_user_files
        user_files = await interface.list_user_files("user_001")
        assert len(user_files) == 2  # Original file + copy
        assert user_files[0].owner_id == "user_001"
        
        # Test get_storage_analytics
        analytics = await interface.get_storage_analytics()
        assert analytics["total_files"] == 2
        assert analytics["total_size_bytes"] == len(b"This is test file content") * 2
        assert analytics["tier_distribution"]["cold"] == 2  # Both files are now in COLD tier (original moved + copy inherited)
        assert analytics["average_file_size"] == len(b"This is test file content")
        
        # Test optimize_storage
        optimize_result = await interface.optimize_storage()
        assert optimize_result["status"] == "completed"
        
        # Test cleanup_orphaned_files
        cleanup_result = await interface.cleanup_orphaned_files()
        assert cleanup_result["status"] == "completed"
        
        # Test delete_file
        delete_result = await interface.delete_file(file_id)
        assert delete_result["status"] == "deleted"
        
        # Verify deletion
        deleted_metadata = await interface.get_file_metadata(file_id)
        assert deleted_metadata is None
        
        # Test download non-existent file
        failed_download = await interface.download_file(FileDownloadRequest(file_id="non_existent"))
        assert failed_download.success is False
        assert failed_download.error_message == "File not found"