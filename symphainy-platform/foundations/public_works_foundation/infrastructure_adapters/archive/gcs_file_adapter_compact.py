#!/usr/bin/env python3
"""
GCS File Adapter - Raw Technology Client (Compact)

Raw Google Cloud Storage client wrapper for file operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw GCS operations for file storage
HOW (Infrastructure Implementation): I use real GCS client with no business logic
"""

import logging
from typing import Dict, Any, Optional, List, BinaryIO
from datetime import datetime, timedelta

try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound, GoogleCloudError
except ImportError:
    class storage:
        class Client:
            def __init__(self): pass
        class Blob:
            def __init__(self): pass
    class NotFound(Exception): pass
    class GoogleCloudError(Exception): pass

logger = logging.getLogger(__name__)

class GCSFileAdapter:
    """Raw GCS client wrapper for file operations - no business logic."""
    
    def __init__(self, project_id: str, bucket_name: str, credentials_path: str = None):
        """Initialize GCS file adapter with real connection."""
        self.project_id = project_id
        self.bucket_name = bucket_name
        
        if credentials_path:
            self.client = storage.Client.from_service_account_json(credentials_path)
        else:
            self.client = storage.Client(project=project_id)
        
        self.bucket = self.client.bucket(bucket_name)
        logger.info(f"✅ GCS File adapter initialized with bucket: {bucket_name}")
    
    # ============================================================================
    # RAW FILE UPLOAD OPERATIONS
    # ============================================================================
    
    async def upload_file(self, blob_name: str, file_data: bytes, 
                         content_type: str = None, metadata: Dict[str, str] = None) -> bool:
        """Raw file upload - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            if content_type:
                blob.content_type = content_type
            if metadata:
                blob.metadata = metadata
            blob.upload_from_string(file_data)
            return True
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to upload file {blob_name}: {e}")
            return False
    
    async def upload_file_from_path(self, blob_name: str, file_path: str,
                                   content_type: str = None, metadata: Dict[str, str] = None) -> bool:
        """Raw file upload from path - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            if content_type:
                blob.content_type = content_type
            if metadata:
                blob.metadata = metadata
            blob.upload_from_filename(file_path)
            return True
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to upload file from path {blob_name}: {e}")
            return False
    
    async def upload_file_from_stream(self, blob_name: str, file_stream: BinaryIO,
                                     content_type: str = None, metadata: Dict[str, str] = None) -> bool:
        """Raw file upload from stream - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            if content_type:
                blob.content_type = content_type
            if metadata:
                blob.metadata = metadata
            blob.upload_from_file(file_stream)
            return True
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to upload file from stream {blob_name}: {e}")
            return False
    
    # ============================================================================
    # RAW FILE DOWNLOAD OPERATIONS
    # ============================================================================
    
    async def download_file(self, blob_name: str) -> Optional[bytes]:
        """Raw file download - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                return None
            return blob.download_as_bytes()
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to download file {blob_name}: {e}")
            return None
    
    async def download_file_to_path(self, blob_name: str, file_path: str) -> bool:
        """Raw file download to path - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                return False
            blob.download_to_filename(file_path)
            return True
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to download file to path {blob_name}: {e}")
            return False
    
    async def download_file_to_stream(self, blob_name: str, file_stream: BinaryIO) -> bool:
        """Raw file download to stream - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                return False
            blob.download_to_file(file_stream)
            return True
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to download file to stream {blob_name}: {e}")
            return False
    
    # ============================================================================
    # RAW FILE METADATA OPERATIONS
    # ============================================================================
    
    async def get_file_metadata(self, blob_name: str) -> Optional[Dict[str, Any]]:
        """Raw file metadata retrieval - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                return None
            
            blob.reload()
            return {
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "time_created": blob.time_created.isoformat() if blob.time_created else None,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "etag": blob.etag,
                "md5_hash": blob.md5_hash,
                "crc32c": blob.crc32c,
                "metadata": blob.metadata or {}
            }
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to get file metadata {blob_name}: {e}")
            return None
    
    async def update_file_metadata(self, blob_name: str, metadata: Dict[str, str]) -> bool:
        """Raw file metadata update - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                return False
            blob.metadata = metadata
            blob.patch()
            return True
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to update file metadata {blob_name}: {e}")
            return False
    
    # ============================================================================
    # RAW FILE LISTING OPERATIONS
    # ============================================================================
    
    async def list_files(self, prefix: str = None, delimiter: str = None) -> List[Dict[str, Any]]:
        """Raw file listing - no business logic."""
        try:
            blobs = self.bucket.list_blobs(prefix=prefix, delimiter=delimiter)
            files = []
            for blob in blobs:
                files.append({
                    "name": blob.name,
                    "size": blob.size,
                    "content_type": blob.content_type,
                    "time_created": blob.time_created.isoformat() if blob.time_created else None,
                    "updated": blob.updated.isoformat() if blob.updated else None,
                    "etag": blob.etag
                })
            return files
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to list files: {e}")
            return []
    
    async def file_exists(self, blob_name: str) -> bool:
        """Raw file existence check - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            return blob.exists()
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to check file existence {blob_name}: {e}")
            return False
    
    # ============================================================================
    # RAW FILE DELETION OPERATIONS
    # ============================================================================
    
    async def delete_file(self, blob_name: str) -> bool:
        """Raw file deletion - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                return False
            blob.delete()
            return True
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to delete file {blob_name}: {e}")
            return False
    
    async def delete_files(self, blob_names: List[str]) -> int:
        """Raw multiple file deletion - no business logic."""
        try:
            blobs = [self.bucket.blob(name) for name in blob_names]
            self.client.delete_blobs(blobs)
            return len(blob_names)
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to delete files: {e}")
            return 0
    
    # ============================================================================
    # RAW FILE COPY OPERATIONS
    # ============================================================================
    
    async def copy_file(self, source_blob_name: str, destination_blob_name: str) -> bool:
        """Raw file copy - no business logic."""
        try:
            source_blob = self.bucket.blob(source_blob_name)
            if not source_blob.exists():
                return False
            self.bucket.copy_blob(source_blob, self.bucket, destination_blob_name)
            return True
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to copy file {source_blob_name}: {e}")
            return False
    
    async def move_file(self, source_blob_name: str, destination_blob_name: str) -> bool:
        """Raw file move - no business logic."""
        try:
            copy_success = await self.copy_file(source_blob_name, destination_blob_name)
            if not copy_success:
                return False
            delete_success = await self.delete_file(source_blob_name)
            if not delete_success:
                await self.delete_file(destination_blob_name)
                return False
            return True
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to move file {source_blob_name}: {e}")
            return False
    
    # ============================================================================
    # RAW URL OPERATIONS
    # ============================================================================
    
    async def generate_signed_url(self, blob_name: str, expiration: int = 3600,
                                 method: str = "GET") -> Optional[str]:
        """Raw signed URL generation - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                return None
            return blob.generate_signed_url(
                expiration=datetime.utcnow() + timedelta(seconds=expiration),
                method=method
            )
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to generate signed URL {blob_name}: {e}")
            return None
    
    async def get_public_url(self, blob_name: str) -> Optional[str]:
        """Raw public URL generation - no business logic."""
        try:
            blob = self.bucket.blob(blob_name)
            if not blob.exists():
                return None
            return blob.public_url
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to get public URL {blob_name}: {e}")
            return None
    
    # ============================================================================
    # RAW BUCKET OPERATIONS
    # ============================================================================
    
    async def get_bucket_info(self) -> Dict[str, Any]:
        """Raw bucket info - no business logic."""
        try:
            return {
                "name": self.bucket.name,
                "location": self.bucket.location,
                "storage_class": self.bucket.storage_class,
                "time_created": self.bucket.time_created.isoformat() if self.bucket.time_created else None,
                "updated": self.bucket.updated.isoformat() if self.bucket.updated else None,
                "versioning_enabled": self.bucket.versioning_enabled,
                "labels": self.bucket.labels or {}
            }
        except GoogleCloudError as e:
            logger.error(f"❌ Failed to get bucket info: {e}")
            return {}
    
    async def test_connection(self) -> bool:
        """Raw connection test - no business logic."""
        try:
            self.bucket.reload()
            return True
        except GoogleCloudError as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False

