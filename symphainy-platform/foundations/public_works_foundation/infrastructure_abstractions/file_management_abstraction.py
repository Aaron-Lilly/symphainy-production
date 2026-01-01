#!/usr/bin/env python3
"""
File Management Abstraction - Business Logic Implementation

Implements file management operations with business logic.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I manage file operations with business logic
HOW (Infrastructure Implementation): I implement business rules for file management
"""

import logging
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..abstraction_contracts.file_management_protocol import FileManagementProtocol

logger = logging.getLogger(__name__)

class FileManagementAbstraction(FileManagementProtocol):
    """
    File management abstraction with business logic.
    
    Implements file management operations with business rules,
    validation, and enhanced functionality for the platform.
    """
    
    def __init__(self, supabase_adapter, config_adapter, di_container=None):
        """Initialize file management abstraction."""
        self.supabase_adapter = supabase_adapter
        self.config_adapter = config_adapter
        self.di_container = di_container
        self.service_name = "file_management_abstraction"
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ File Management Abstraction initialized")
    
    # ============================================================================
    # CORE FILE OPERATIONS WITH BUSINESS LOGIC
    # ============================================================================
    
    async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create file with business logic validation."""
        try:
            # Validate required fields
            required_fields = ["user_id", "ui_name", "file_type"]
            for field in required_fields:
                if field not in file_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Add business logic metadata
            enhanced_file_data = {
                **file_data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "deleted": False,
                "status": file_data.get("status", "uploaded"),
                "content_type": file_data.get("content_type", "unstructured"),
                "lineage_depth": file_data.get("lineage_depth", 0),
                "generation": file_data.get("generation", 0),
                "version": file_data.get("version", 1),
                "access_level": file_data.get("access_level", "open"),
                "data_classification": file_data.get("data_classification", "public"),
                "pillar_origin": file_data.get("pillar_origin", "content_pillar")
            }
            
            # Calculate file hash if file_data is provided
            if "file_data" in file_data:
                file_bytes = file_data["file_data"]
                if isinstance(file_bytes, str):
                    file_bytes = file_bytes.encode('utf-8')
                enhanced_file_data["file_hash"] = hashlib.sha256(file_bytes).hexdigest()
                enhanced_file_data["file_size"] = len(file_bytes)
            
            # Create file
            result = await self.supabase_adapter.create_file(enhanced_file_data)
            
            self.logger.info(f"✅ File created: {result.get('uuid')} - {result.get('ui_name')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create file: {e}")
            raise
    
            raise  # Re-raise for service layer to handle
    
    async def update_file(self, file_uuid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update file with business logic validation."""
        try:
            # Validate that file exists
            existing_file = await self.supabase_adapter.get_file(file_uuid)
            if not existing_file:
                raise ValueError(f"File not found: {file_uuid}")
            
            # Validate data_classification if being updated
            if "data_classification" in updates:
                valid_classifications = ["client", "platform", "public", "private"]
                if updates["data_classification"] not in valid_classifications:
                    raise ValueError(f"Invalid data_classification: {updates['data_classification']}. Must be one of: {valid_classifications}")
            
            # Add business logic metadata
            enhanced_updates = {
                **updates,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update file via adapter
            result = await self.supabase_adapter.update_file(file_uuid, enhanced_updates)
            
            self.logger.info(f"✅ File updated: {file_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update file {file_uuid}: {e}")
            raise
    
    async def get_file(self, file_uuid: str) -> Optional[Dict[str, Any]]:
        """Get file with business logic validation."""
        try:
            result = await self.supabase_adapter.get_file(file_uuid)
            
            if result:
                self.logger.debug(f"✅ File retrieved: {file_uuid}")
                
                # Record platform operation event
            else:
                self.logger.warning(f"⚠️ File not found: {file_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get file {file_uuid}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def delete_file(self, file_uuid: str) -> bool:
        """Delete file with business logic validation."""
        try:
            # Validate file exists
            existing_file = await self.get_file(file_uuid)
            if not existing_file:
                self.logger.warning(f"⚠️ File not found for deletion: {file_uuid}")
            
            # Check if file has children (business rule)
            children = await self.get_file_links(file_uuid, "child")
            if children:
                # Allow deletion if all children are parsed files (they should be cascade deleted)
                # Check if all children are parsed files (have "parsed_from" link type)
                all_parsed = all(
                    link.get("link_type") == "parsed_from" 
                    for link in children
                )
                if not all_parsed:
                    self.logger.warning(f"⚠️ Cannot delete file with non-parsed children: {file_uuid}")
                    return False
                # If all children are parsed files, delete them first (cascade delete)
                self.logger.info(f"🗑️ [delete_file] Deleting {len(children)} parsed file children before deleting parent")
                for child_link in children:
                    child_uuid = child_link.get("child_uuid")
                    if child_uuid:
                        try:
                            await self.delete_file(child_uuid)  # Recursive delete
                        except Exception as child_delete_error:
                            self.logger.warning(f"⚠️ Failed to delete child file {child_uuid}: {child_delete_error}")
            
            result = await self.supabase_adapter.delete_file(file_uuid)
            
            if result:
                self.logger.info(f"✅ File deleted: {file_uuid}")
                
                # Record platform operation event
            else:
                self.logger.error(f"❌ Failed to delete file: {file_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete file {file_uuid}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def list_files(self, user_id: str, tenant_id: Optional[str] = None, 
                        filters: Optional[Dict[str, Any]] = None,
                        limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """List files with business logic filtering."""
        try:
            # Apply business logic filters
            enhanced_filters = filters or {}
            
            # Add default filters
            if "deleted" not in enhanced_filters:
                enhanced_filters["deleted"] = False
            
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
            # Validate parent file exists
            parent_file = await self.get_file(parent_uuid)
            if not parent_file:
                raise ValueError(f"Parent file not found: {parent_uuid}")
            
            # Validate child file exists
            child_file = await self.get_file(child_uuid)
            if not child_file:
                raise ValueError(f"Child file not found: {child_uuid}")
            
            # Validate link type
            valid_link_types = [
                'parsed_from', 'metadata_from', 'insights_from', 'deliverable_from',
                'variant_of', 'alternate_format', 'derived_from'
            ]
            if link_type not in valid_link_types:
                raise ValueError(f"Invalid link type: {link_type}")
            
            # Calculate generation gap
            parent_generation = parent_file.get("generation", 0)
            child_generation = child_file.get("generation", 0)
            generation_gap = child_generation - parent_generation
            
            # Create link
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
            # Validate file exists
            file_record = await self.get_file(file_uuid)
            if not file_record:
                self.logger.warning(f"⚠️ File not found for links: {file_uuid}")
            
            result = await self.supabase_adapter.get_file_links(file_uuid, direction)
            
            self.logger.debug(f"✅ Retrieved {len(result)} file links for {file_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get file links for {file_uuid}: {e}")
            raise  # Re-raise for service layer to handle

        """Delete file link with business logic validation."""
        try:
            result = await self.supabase_adapter.delete_file_link(link_id)
            
            if result:
                self.logger.info(f"✅ File link deleted: {link_id}")
                
                # Record platform operation event
            else:
                self.logger.warning(f"⚠️ File link not found: {link_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete file link {link_id}: {e}")
            raise  # Re-raise for service layer to handle

        """Get lineage tree with business logic validation."""
        try:
            # Validate root file exists
            root_file = await self.get_file(root_uuid)
            if not root_file:
                self.logger.warning(f"⚠️ Root file not found: {root_uuid}")
            
            result = await self.supabase_adapter.get_lineage_tree(root_uuid)
            
            self.logger.debug(f"✅ Retrieved lineage tree with {len(result)} files for root {root_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get lineage tree for {root_uuid}: {e}")
            raise  # Re-raise for service layer to handle

        """Get file descendants with business logic validation."""
        try:
            # Validate root file exists
            root_file = await self.get_file(root_uuid)
            if not root_file:
                self.logger.warning(f"⚠️ Root file not found: {root_uuid}")
                return []
            
            result = await self.supabase_adapter.get_file_descendants(root_uuid)
            
            self.logger.debug(f"✅ Retrieved {len(result)} descendants for root {root_uuid}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get descendants for {root_uuid}: {e}")
            raise  # Re-raise for service layer to handle

        """Create child file with lineage tracking."""
        try:
            # Get parent file
            parent = await self.get_file(parent_uuid)
            if not parent:
                raise ValueError(f"Parent file not found: {parent_uuid}")
            
            # Calculate lineage metadata
            lineage_depth = parent.get("lineage_depth", 0) + 1
            generation = parent.get("generation", 0) + 1
            root_uuid = parent.get("root_file_uuid", parent_uuid)
            
            # Prepare child file data
            child_file_data = {
                **child_data,
                "parent_file_uuid": parent_uuid,
                "root_file_uuid": root_uuid,
                "lineage_depth": lineage_depth,
                "generation": generation,
                "lineage_path": f"{parent.get('lineage_path', '')}->{child_data.get('ui_name', '')}",
                "user_id": parent["user_id"],
                "tenant_id": parent.get("tenant_id"),
                "created_by": parent.get("created_by"),
                "access_level": parent.get("access_level", "open"),
                "data_classification": parent.get("data_classification", "public"),
                "pillar_origin": parent.get("pillar_origin", "content_pillar")
            }
            
            # Create child file
            child_result = await self.create_file(child_file_data)
            
            # Create file link
            await self.create_file_link(parent_uuid, child_result["uuid"], link_type)
            
            self.logger.info(f"✅ Child file created: {child_result['uuid']} from parent {parent_uuid}")
            
            return child_result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create child file: {e}")
            raise
    
    # ============================================================================
    # SEARCH AND STATISTICS OPERATIONS
    # ============================================================================
    
            raise  # Re-raise for service layer to handle
    
    async def search_files(self, user_id: str, search_term: str, 
                          content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search files with business logic validation."""
        try:
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
            result = await self.supabase_adapter.get_file_statistics(user_id, tenant_id)
            
            self.logger.debug(f"✅ Retrieved file statistics for user {user_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get file statistics: {e}")
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
            raise  # Re-raise for service layer to handle

        """Check health with business logic validation."""
        try:
            result = await self.supabase_adapter.health_check()
            
            # Add business logic health checks
            if result.get("status") == "healthy":
                # Test file operations
                test_stats = await self.get_file_statistics("test_user")
                result["business_logic"] = "operational"
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            raise  # Re-raise for service layer to handle
