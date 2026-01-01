#!/usr/bin/env python3
"""
Mock File Management Adapter - For Testing

In-memory file management adapter that mimics Supabase behavior.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide mock file management operations
HOW (Infrastructure Implementation): I use in-memory storage for testing
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class MockFileManagementAdapter:
    """In-memory file management adapter for testing - no business logic."""
    
    def __init__(self):
        """Initialize mock file management adapter."""
        self._files: Dict[str, Dict[str, Any]] = {}
        self._links: Dict[str, Dict[str, Any]] = {}
        logger.info("✅ Mock File Management adapter initialized (in-memory)")
    
    async def connect(self) -> bool:
        """Connect to mock storage (always succeeds)."""
        logger.info("✅ Mock File Management adapter connected")
        return True
    
    # ============================================================================
    # FILE OPERATIONS
    # ============================================================================
    
    async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock file creation - stores in memory."""
        try:
            # Generate UUID if not provided
            file_uuid = file_data.get("uuid", str(uuid.uuid4()))
            file_data["uuid"] = file_uuid
            
            # Add timestamps
            now = datetime.utcnow().isoformat()
            file_data["created_at"] = file_data.get("created_at", now)
            file_data["updated_at"] = now
            file_data["deleted"] = False
            
            # Store in memory
            self._files[file_uuid] = file_data
            
            logger.info(f"✅ Mock: Created file {file_uuid}")
            return file_data
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to create file: {e}")
            raise
    
    async def get_file(self, file_uuid: str) -> Optional[Dict[str, Any]]:
        """Mock file retrieval - gets from memory."""
        try:
            file_data = self._files.get(file_uuid)
            
            if file_data and not file_data.get("deleted", False):
                logger.info(f"✅ Mock: Retrieved file {file_uuid}")
                return file_data
            
            logger.warning(f"⚠️ Mock: File {file_uuid} not found or deleted")
            return None
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to get file {file_uuid}: {e}")
            return None
    
    async def update_file(self, file_uuid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Mock file update - updates in memory."""
        try:
            if file_uuid not in self._files:
                raise ValueError(f"File {file_uuid} not found")
            
            # Add updated_at timestamp
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            # Update file data
            self._files[file_uuid].update(updates)
            
            logger.info(f"✅ Mock: Updated file {file_uuid}")
            return self._files[file_uuid]
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to update file {file_uuid}: {e}")
            raise
    
    async def delete_file(self, file_uuid: str) -> bool:
        """Mock file deletion (soft delete) - marks as deleted in memory."""
        try:
            if file_uuid not in self._files:
                logger.warning(f"⚠️ Mock: File {file_uuid} not found for deletion")
                return False
            
            # Soft delete
            self._files[file_uuid]["deleted"] = True
            self._files[file_uuid]["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"✅ Mock: Deleted file {file_uuid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to delete file {file_uuid}: {e}")
            return False
    
    async def list_files(self, user_id: str, tenant_id: Optional[str] = None, 
                        filters: Optional[Dict[str, Any]] = None, 
                        limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Mock file listing - filters in-memory files."""
        try:
            # Filter files by user_id and not deleted
            results = [
                f for f in self._files.values()
                if f.get("user_id") == user_id and not f.get("deleted", False)
            ]
            
            # Apply tenant_id filter
            if tenant_id:
                results = [f for f in results if f.get("tenant_id") == tenant_id]
            
            # Apply custom filters
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        results = [f for f in results if f.get(key) in value]
                    else:
                        results = [f for f in results if f.get(key) == value]
            
            # Sort by created_at (newest first)
            results.sort(key=lambda f: f.get("created_at", ""), reverse=True)
            
            # Apply pagination
            if offset:
                results = results[offset:]
            if limit:
                results = results[:limit]
            
            logger.info(f"✅ Mock: Listed {len(results)} files for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to list files: {e}")
            return []
    
    # ============================================================================
    # FILE LINKING OPERATIONS
    # ============================================================================
    
    async def create_file_link(self, parent_uuid: str, child_uuid: str, link_type: str, 
                              generation_gap: int = 1, relationship_strength: str = "direct") -> Dict[str, Any]:
        """Mock file link creation - stores in memory."""
        try:
            link_id = str(uuid.uuid4())
            link_data = {
                "id": link_id,
                "parent_uuid": parent_uuid,
                "child_uuid": child_uuid,
                "link_type": link_type,
                "generation_gap": generation_gap,
                "relationship_strength": relationship_strength,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self._links[link_id] = link_data
            
            logger.info(f"✅ Mock: Created file link {link_id}")
            return link_data
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to create file link: {e}")
            raise
    
    async def get_file_links(self, file_uuid: str, direction: str = "both") -> List[Dict[str, Any]]:
        """Mock file link retrieval - gets from memory."""
        try:
            links = []
            
            for link in self._links.values():
                if direction in ("parent", "both") and link.get("child_uuid") == file_uuid:
                    links.append(link)
                if direction in ("child", "both") and link.get("parent_uuid") == file_uuid:
                    links.append(link)
            
            logger.info(f"✅ Mock: Retrieved {len(links)} links for file {file_uuid}")
            return links
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to get file links: {e}")
            return []
    
    async def delete_file_link(self, link_id: str) -> bool:
        """Mock file link deletion - removes from memory."""
        try:
            if link_id in self._links:
                del self._links[link_id]
                logger.info(f"✅ Mock: Deleted file link {link_id}")
                return True
            
            logger.warning(f"⚠️ Mock: Link {link_id} not found for deletion")
            return False
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to delete file link: {e}")
            return False
    
    # ============================================================================
    # LINEAGE OPERATIONS
    # ============================================================================
    
    async def get_lineage_tree(self, root_uuid: str) -> List[Dict[str, Any]]:
        """Mock lineage tree retrieval - simple recursive traversal."""
        try:
            # For mock implementation, return a simple list
            lineage = []
            
            # Get root file
            root_file = await self.get_file(root_uuid)
            if root_file:
                lineage.append({
                    "uuid": root_file["uuid"],
                    "ui_name": root_file.get("ui_name", "unknown"),
                    "file_type": root_file.get("file_type", "unknown"),
                    "content_type": root_file.get("content_type"),
                    "generation": root_file.get("generation", 0),
                    "lineage_depth": root_file.get("lineage_depth", 0),
                    "lineage_path": root_file.get("lineage_path", root_uuid),
                    "level": 0
                })
            
            logger.info(f"✅ Mock: Retrieved lineage tree for {root_uuid}")
            return lineage
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to get lineage tree: {e}")
            return []
    
    async def get_file_descendants(self, root_uuid: str) -> List[Dict[str, Any]]:
        """Mock descendants retrieval - simple link traversal."""
        try:
            descendants = []
            
            # Get root file
            root_file = await self.get_file(root_uuid)
            if root_file:
                descendants.append({
                    "uuid": root_file["uuid"],
                    "ui_name": root_file.get("ui_name", "unknown"),
                    "file_type": root_file.get("file_type", "unknown"),
                    "content_type": root_file.get("content_type"),
                    "generation": root_file.get("generation", 0),
                    "lineage_depth": root_file.get("lineage_depth", 0)
                })
            
            logger.info(f"✅ Mock: Retrieved {len(descendants)} descendants for {root_uuid}")
            return descendants
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to get descendants: {e}")
            return []
    
    # ============================================================================
    # SEARCH OPERATIONS
    # ============================================================================
    
    async def search_files(self, user_id: str, search_term: str, 
                          content_type: Optional[str] = None,
                          file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Mock file search - simple string matching."""
        try:
            results = [
                f for f in self._files.values()
                if f.get("user_id") == user_id 
                and not f.get("deleted", False)
                and search_term.lower() in f.get("ui_name", "").lower()
            ]
            
            if content_type:
                results = [f for f in results if f.get("content_type") == content_type]
            
            if file_type:
                results = [f for f in results if f.get("file_type") == file_type]
            
            results.sort(key=lambda f: f.get("created_at", ""), reverse=True)
            
            logger.info(f"✅ Mock: Found {len(results)} files matching '{search_term}'")
            return results
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to search files: {e}")
            return []
    
    # ============================================================================
    # STATISTICS OPERATIONS
    # ============================================================================
    
    async def get_file_statistics(self, user_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Mock file statistics - simple counting."""
        try:
            files = [
                f for f in self._files.values()
                if f.get("user_id") == user_id and not f.get("deleted", False)
            ]
            
            if tenant_id:
                files = [f for f in files if f.get("tenant_id") == tenant_id]
            
            # Calculate statistics
            total_files = len(files)
            content_types = {}
            file_types = {}
            statuses = {}
            
            for file in files:
                content_type = file.get("content_type", "unknown")
                file_type = file.get("file_type", "unknown")
                status = file.get("status", "unknown")
                
                content_types[content_type] = content_types.get(content_type, 0) + 1
                file_types[file_type] = file_types.get(file_type, 0) + 1
                statuses[status] = statuses.get(status, 0) + 1
            
            logger.info(f"✅ Mock: Retrieved statistics for user {user_id}")
            return {
                "total_files": total_files,
                "content_types": content_types,
                "file_types": file_types,
                "statuses": statuses,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Mock: Failed to get statistics: {e}")
            return {"total_files": 0, "content_types": {}, "file_types": {}, "statuses": {}}
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check - always healthy."""
        return {
            "status": "healthy",
            "message": "Mock File Management adapter is operational",
            "files_count": len([f for f in self._files.values() if not f.get("deleted", False)]),
            "links_count": len(self._links),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def close(self):
        """Close the mock adapter (cleanup)."""
        logger.info(f"✅ Mock File Management adapter closed ({len(self._files)} files, {len(self._links)} links)")





