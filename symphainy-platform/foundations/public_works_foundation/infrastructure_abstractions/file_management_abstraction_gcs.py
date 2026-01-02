#!/usr/bin/env python3
"""
File Management Abstraction - GCS Implementation

Corrected file management abstraction using GCS for file storage.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I manage file operations with business logic using GCS
HOW (Infrastructure Implementation): I implement business rules for file management with GCS storage
"""

import logging
import hashlib
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..abstraction_contracts.file_management_protocol import FileManagementProtocol

logger = logging.getLogger(__name__)

class FileManagementAbstraction:
    """
    File management abstraction with business logic using GCS.
    
    Implements file management operations with business rules,
    validation, and enhanced functionality for the platform.
    Uses GCS for file storage and Supabase for file metadata.
    """
    
    def __init__(self, 
                 gcs_adapter,  # Required: GCS adapter for file storage
                 supabase_adapter,  # Required: Supabase adapter for file metadata
                 config_adapter=None,
                 di_container=None):
        """
        Initialize file management abstraction with dependency injection.
        
        Args:
            gcs_adapter: GCS adapter for file storage (required)
            supabase_adapter: Supabase adapter for file metadata (required)
            config_adapter: Optional configuration adapter
            di_container: Dependency injection container
        """
        if not gcs_adapter:
            raise ValueError("FileManagementAbstraction requires gcs_adapter via dependency injection")
        if not supabase_adapter:
            raise ValueError("FileManagementAbstraction requires supabase_adapter via dependency injection")
        
        self.gcs_adapter = gcs_adapter  # For file storage
        self.supabase_adapter = supabase_adapter  # For file metadata
        self.config_adapter = config_adapter
        self.di_container = di_container
        self.service_name = "file_management_abstraction_gcs"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ File Management Abstraction initialized with GCS + Supabase (dependency injection)")
    
    # ============================================================================
    # CORE FILE OPERATIONS WITH BUSINESS LOGIC
    # ============================================================================
    
    async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create file with business logic validation using GCS + Supabase."""
        try:
            # Validate required fields
            required_fields = ["user_id", "ui_name", "file_type"]
            for field in required_fields:
                if field not in file_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate UUID first
            file_uuid = self._generate_file_uuid()
            
            # Store file in GCS first
            blob_name = None
            file_size = 0
            if "file_content" in file_data:
                blob_name = f"files/{file_uuid}"
                file_size = len(file_data["file_content"])
                
                # Use mime_type if available, otherwise derive from file_type
                content_type = file_data.get("mime_type") or file_data.get("file_type")
                # If file_type is an extension (like "txt"), convert to MIME type
                if content_type and not "/" in content_type:
                    # Simple extension to MIME type mapping
                    mime_map = {
                        "txt": "text/plain",
                        "pdf": "application/pdf",
                        "html": "text/html",
                        "json": "application/json",
                        "xml": "application/xml",
                        "csv": "text/csv",
                        "bin": "application/octet-stream",
                        "cpy": "text/plain"  # COBOL copybook
                    }
                    content_type = mime_map.get(content_type.lower(), "application/octet-stream")
                
                gcs_success = await self.gcs_adapter.upload_file(
                    blob_name=blob_name,
                    file_data=file_data["file_content"],
                    content_type=content_type,
                    metadata={
                        "user_id": file_data["user_id"],
                        "ui_name": file_data["ui_name"],
                        "file_type": file_data["file_type"]  # Keep for business logic, but filter in adapter
                    }
                )
                
                if not gcs_success:
                    raise Exception(f"Failed to upload file to GCS: {blob_name}")
            
            # Prepare metadata for Supabase (matching schema)
            supabase_metadata = {
                "uuid": file_uuid,
                "user_id": file_data["user_id"],
                "tenant_id": file_data.get("tenant_id"),
                "ui_name": file_data["ui_name"],
                "file_type": file_data["file_type"],
                "mime_type": file_data.get("mime_type") or file_data.get("file_type"),
                "original_path": blob_name or file_data.get("original_path", f"files/{file_uuid}"),
                "file_size": file_size or file_data.get("file_size"),
                "status": "uploaded",
                "created_by": file_data["user_id"],
                "upload_source": file_data.get("upload_source", "api"),
                "pillar_origin": file_data.get("pillar_origin", "content_pillar"),
                "service_context": {
                    "gcs_blob_name": blob_name,
                    "gcs_bucket": self.gcs_adapter.bucket_name if blob_name else None,
                    "storage_type": "gcs",
                    **(file_data.get("metadata", {}) or {})
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store file metadata in Supabase
            result = await self.supabase_adapter.create_file(supabase_metadata)
            
            self.logger.info(f"✅ File created: {result.get('uuid')} - {result.get('ui_name')} (GCS: {blob_name})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create file: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_file(self, file_uuid: str) -> Optional[Dict[str, Any]]:
        """Get file with business logic validation from GCS + Supabase."""
        try:
            self.logger.info(f"🔍 Getting file: {file_uuid}")
            
            # Get file metadata from Supabase
            self.logger.debug(f"  📊 Fetching metadata from Supabase...")
            result = await self.supabase_adapter.get_file(file_uuid)
            self.logger.debug(f"  📊 Supabase result: {result is not None}")
            
            if result:
                # Get file content from GCS if needed
                # gcs_blob_name is stored in service_context
                service_context = result.get("service_context", {})
                gcs_blob_name = service_context.get("gcs_blob_name") or result.get("original_path")
                
                if gcs_blob_name:
                    file_content = await self.gcs_adapter.download_file(blob_name=gcs_blob_name)
                    
                    if file_content:
                        # Validate parquet magic bytes if it's a parquet file
                        if isinstance(file_content, bytes) and len(file_content) >= 4:
                            magic_bytes = file_content[:4]
                            if magic_bytes == b'PAR1':
                                self.logger.info(f"✅ Retrieved parquet file from GCS: {len(file_content)} bytes, magic bytes validated")
                            else:
                                # Not parquet or corrupted - log for debugging
                                self.logger.debug(f"📄 Retrieved file from GCS: {len(file_content)} bytes, magic bytes: {magic_bytes}")
                        
                        result["file_content"] = file_content
                        self.logger.debug(f"✅ File content retrieved from GCS: {gcs_blob_name} ({len(file_content)} bytes)")
                    else:
                        self.logger.warning(f"⚠️ Failed to download file from GCS: {gcs_blob_name}")
                else:
                    self.logger.warning(f"⚠️ No GCS blob name found for file: {file_uuid}")
                
                self.logger.debug(f"✅ File metadata retrieved: {file_uuid}")
                
            else:
                self.logger.warning(f"⚠️ File not found: {file_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get file {file_uuid}: {e}")
            raise  # Re-raise for service layer to handle

        """Update file with business logic validation using GCS + Supabase."""
        try:
            # Validate updates
            allowed_updates = ["ui_name", "file_type", "status", "metadata"]
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_updates}
            
            if not filtered_updates:
                raise ValueError("No valid updates provided")
            
            # Add update timestamp
            filtered_updates["updated_at"] = datetime.utcnow().isoformat()
            
            # Update file metadata in Supabase
            result = await self.supabase_adapter.update_file(file_uuid, filtered_updates)
            
            self.logger.info(f"✅ File updated: {file_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update file {file_uuid}: {e}")
            raise
    
            raise  # Re-raise for service layer to handle
    async def delete_file(self, file_uuid: str) -> bool:
        """Delete file with business logic validation from GCS + Supabase, with cascade delete."""
        try:
            # Get file info first to get GCS blob name and check status
            file_info = await self.supabase_adapter.get_file(file_uuid)
            
            if not file_info:
                self.logger.warning(f"⚠️ File not found for deletion: {file_uuid}")
                return False
            
            # ✅ SIMPLIFIED: Direct deletion - no cascade
            # Users delete what they want to delete from the dashboard
            # If they want to delete related files, they can do so explicitly
            
            # Delete file from GCS
            if file_info:
                gcs_blob_name = file_info.get("service_context", {}).get("gcs_blob_name") if isinstance(file_info.get("service_context"), dict) else None
                if not gcs_blob_name:
                    gcs_blob_name = file_info.get("original_path")
                
                if gcs_blob_name:
                    try:
                        gcs_result = await self.gcs_adapter.delete_file(
                            blob_name=gcs_blob_name
                        )
                        
                        if not gcs_result:
                            self.logger.warning(f"⚠️ Failed to delete file from GCS: {gcs_blob_name}")
                    except Exception as gcs_error:
                        self.logger.warning(f"⚠️ Error deleting from GCS: {gcs_error}")
            
            # Delete file metadata from Supabase project_files
            result = await self.supabase_adapter.delete_file(file_uuid)
            
            if result:
                self.logger.info(f"✅ File deleted: {file_uuid}")
            else:
                self.logger.error(f"❌ Failed to delete file: {file_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete file {file_uuid}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def list_files(self, user_id: str, tenant_id: Optional[str] = None, 
                        filters: Optional[Dict[str, Any]] = None,
                        limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """List files with business logic validation from Supabase."""
        try:
            # Add business logic filters
            # Note: Don't filter by status="active" only - files can have status="uploaded" or "active"
            # Dashboard should show all non-deleted files for the user
            enhanced_filters = {
                "user_id": user_id,
                **(filters or {})
            }
            
            # Only add status filter if explicitly provided in filters
            # Otherwise, show all files (uploaded, active, etc.) except deleted ones
            
            if tenant_id:
                enhanced_filters["tenant_id"] = tenant_id
            
            # List files from Supabase (metadata only)
            result = await self.supabase_adapter.list_files(
                user_id=user_id,
                tenant_id=tenant_id,
                filters=enhanced_filters,
                limit=limit,
                offset=offset
            )
            
            self.logger.debug(f"✅ Listed {len(result)} files for user {user_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list files: {e}")
            raise  # Re-raise for service layer to handle

        """Create file link with business logic validation."""
        try:
            # Validate link type
            valid_link_types = ["derived", "version", "reference", "composition"]
            if link_type not in valid_link_types:
                raise ValueError(f"Invalid link type: {link_type}")
            
            # Validate generation gap
            if generation_gap < 1 or generation_gap > 10:
                raise ValueError("Generation gap must be between 1 and 10")
            
            # Create link in Supabase
            result = await self.supabase_adapter.create_file_link(
                parent_uuid=parent_uuid,
                child_uuid=child_uuid,
                link_type=link_type,
                generation_gap=generation_gap
            )
            
            self.logger.info(f"✅ File link created: {parent_uuid} -> {child_uuid} ({link_type})")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create file link: {e}")
            raise
    
            raise  # Re-raise for service layer to handle
    async def get_file_links(self, file_uuid: str, direction: str = "both") -> List[Dict[str, Any]]:
        """Get file links with business logic validation."""
        try:
            # Validate direction
            valid_directions = ["parent", "child", "both"]
            if direction not in valid_directions:
                raise ValueError(f"Invalid direction: {direction}")
            
            # Get links from Supabase
            result = await self.supabase_adapter.get_file_links(file_uuid, direction)
            
            self.logger.debug(f"✅ Retrieved {len(result)} file links for {file_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get file links for {file_uuid}: {e}")
            raise  # Re-raise for service layer to handle

        """Delete file link with business logic validation."""
        try:
            # Delete link from Supabase
            result = await self.supabase_adapter.delete_file_link(link_id)
            
            if result:
                self.logger.info(f"✅ File link deleted: {link_id}")
                
            else:
                self.logger.warning(f"⚠️ File link not found: {link_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete file link {link_id}: {e}")
            raise  # Re-raise for service layer to handle

        """Get lineage tree with business logic validation."""
        try:
            # Validate root file exists
            root_file = await self.supabase_adapter.get_file(root_uuid)
            if not root_file:
                raise ValueError(f"Root file not found: {root_uuid}")
            
            # Get lineage tree from Supabase
            result = await self.supabase_adapter.get_lineage_tree(root_uuid)
            
            self.logger.debug(f"✅ Retrieved lineage tree with {len(result)} files for root {root_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get lineage tree for {root_uuid}: {e}")
            raise  # Re-raise for service layer to handle

        """Get file descendants with business logic validation."""
        try:
            # Get descendants from Supabase
            result = await self.supabase_adapter.get_file_descendants(root_uuid)
            
            self.logger.debug(f"✅ Retrieved {len(result)} descendants for root {root_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get descendants for {root_uuid}: {e}")
            raise  # Re-raise for service layer to handle

        """Search files with business logic validation."""
        try:
            # Validate search term
            if not search_term or len(search_term.strip()) < 2:
                raise ValueError("Search term must be at least 2 characters")
            
            # Add business logic filters
            enhanced_filters = {
                "user_id": user_id,
                "status": "active"
            }
            
            if content_type:
                enhanced_filters["content_type"] = content_type
            if file_type:
                enhanced_filters["file_type"] = file_type
            
            # Search files in Supabase
            result = await self.supabase_adapter.search_files(
                user_id=user_id,
                search_term=search_term,
                content_type=content_type,
                file_type=file_type
            )
            
            self.logger.debug(f"✅ Found {len(result)} files matching search: {search_term}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to search files: {e}")
            raise  # Re-raise for service layer to handle

        """Get file statistics with business logic validation."""
        try:
            # Get statistics from Supabase
            result = await self.supabase_adapter.get_file_statistics(user_id, tenant_id)
            
            self.logger.debug(f"✅ Retrieved file statistics for user {user_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get file statistics: {e}")
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
            raise  # Re-raise for service layer to handle

        """Health check for file management abstraction."""
        try:
            # Test GCS connection
            gcs_healthy = await self.gcs_adapter.test_connection()
            
            # Test Supabase connection (connect method returns bool)
            try:
                supabase_healthy = await self.supabase_adapter.connect()
            except:
                self.logger.error(f"❌ Error: {e}")
                supabase_healthy = False
            
                raise  # Re-raise for service layer to handle

            
            result = {
                "status": "healthy" if all_healthy else "unhealthy",
                "gcs": "healthy" if gcs_healthy else "unhealthy",
                "supabase": "healthy" if supabase_healthy else "unhealthy",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return result
        except Exception as e:
            self.logger.error(f"❌ Failed to perform health check: {e}")
    
            raise  # Re-raise for service layer to handle

        """Health check for file management abstraction."""
        try:
            # Check GCS health
            gcs_health = await self.gcs_adapter.health_check()
            
            # Check Supabase health
            supabase_health = await self.supabase_adapter.health_check()
            
            # Add business logic health checks
            if gcs_health.get("status") == "healthy" and supabase_health.get("status") == "healthy":
                # Test file operations
                test_stats = await self.get_file_statistics("test_user")
                result = {
                    "status": "healthy",
                    "gcs": gcs_health,
                    "supabase": supabase_health,
                    "business_logic": "operational",
                    "test_results": {"file_stats": test_stats}
                }
            else:
                result = {
                    "status": "unhealthy",
                    "gcs": gcs_health,
                    "supabase": supabase_health,
                    "business_logic": "degraded"
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _generate_file_uuid(self) -> str:
        """Generate unique file UUID."""
        return str(uuid.uuid4())
    
    def _validate_file_type(self, file_type: str) -> bool:
        """Validate file type."""
        valid_types = [
            "text/plain", "text/html", "text/markdown",
            "application/pdf", "application/json", "application/xml",
            "image/jpeg", "image/png", "image/gif",
            "video/mp4", "video/avi", "video/mov",
            "audio/mp3", "audio/wav", "audio/ogg"
        ]
        return file_type in valid_types
