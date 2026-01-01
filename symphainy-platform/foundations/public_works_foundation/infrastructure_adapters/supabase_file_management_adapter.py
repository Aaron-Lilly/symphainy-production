#!/usr/bin/env python3
"""
Supabase File Management Adapter - Raw Technology Client

Raw Supabase client wrapper for file management operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw Supabase operations for file management
HOW (Infrastructure Implementation): I use real Supabase client with no business logic
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

try:
    from supabase import create_client, Client
    # Note: Supabase client handles auth errors internally
    # We catch generic exceptions and identify auth errors by message/type
    class SupabaseAuthError(Exception):
        """Custom exception for Supabase authentication errors."""
        pass
except ImportError:
    class Client:
        def __init__(self): pass
    class SupabaseAuthError(Exception): pass
    def create_client(url, key): return Client()

logger = logging.getLogger(__name__)

class SupabaseFileManagementAdapter:
    """Raw Supabase client wrapper for file management operations - no business logic."""
    
    def __init__(self, url: str, service_key: str):
        """Initialize Supabase file management adapter with real credentials."""
        # Normalize URL - remove trailing slashes
        self.url = url.rstrip('/') if url else url
        self.service_key = service_key
        
        # Create Supabase client (private - use wrapper methods instead)
        self._client: Client = create_client(self.url, service_key)
        # Keep client as alias for backward compatibility (will be removed)
        self.client = self._client
        
        logger.info(f"✅ Supabase File Management adapter initialized with URL: {self.url}")
    
    async def connect(self) -> bool:
        """Connect to Supabase (already connected in __init__)."""
        try:
            # Test connection
            result = self._client.table("project_files").select("uuid").limit(1).execute()
            logger.info("✅ Supabase File Management adapter connected")
            return True
        except Exception as e:
            logger.error(f"❌ Supabase File Management adapter connection failed: {e}")
            return False
    
    # ============================================================================
    # RAW FILE OPERATIONS
    # ============================================================================
    
    async def create_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raw file creation - no business logic."""
        try:
            result = self._client.table("project_files").insert(file_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"❌ Failed to create file: {e}")
            raise
    
    async def get_file(self, file_uuid: str) -> Optional[Dict[str, Any]]:
        """Raw file retrieval - no business logic."""
        try:
            result = self._client.table("project_files").select("*").eq("uuid", file_uuid).eq("deleted", False).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Failed to get file {file_uuid}: {e}")
            return None
    
    async def update_file(self, file_uuid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Raw file update - no business logic."""
        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            result = self._client.table("project_files").update(updates).eq("uuid", file_uuid).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"❌ Failed to update file {file_uuid}: {e}")
            raise
    
    async def delete_file(self, file_uuid: str) -> bool:
        """Raw file deletion (soft delete) - no business logic."""
        try:
            result = self._client.table("project_files").update({
                "deleted": True,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("uuid", file_uuid).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ Failed to delete file {file_uuid}: {e}")
            return False
    
    async def list_files(self, user_id: str, tenant_id: Optional[str] = None, 
                        filters: Optional[Dict[str, Any]] = None, 
                        limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Raw file listing - no business logic."""
        try:
            query = self._client.table("project_files").select("*").eq("user_id", user_id).eq("deleted", False)
            
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.range(offset, offset + (limit or 10) - 1)
            
            result = query.order("created_at", desc=True).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Failed to list files: {e}")
            return []
    
    # ============================================================================
    # RAW FILE LINKING OPERATIONS
    # ============================================================================
    
    async def create_file_link(self, parent_uuid: str, child_uuid: str, link_type: str, 
                              generation_gap: int = 1, relationship_strength: str = "direct") -> Dict[str, Any]:
        """Raw file link creation - no business logic."""
        try:
            link_data = {
                "parent_uuid": parent_uuid,
                "child_uuid": child_uuid,
                "link_type": link_type,
                "generation_gap": generation_gap,
                "relationship_strength": relationship_strength
            }
            
            result = self._client.table("file_links").insert(link_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"❌ Failed to create file link: {e}")
            raise
    
    async def get_file_links(self, file_uuid: str, direction: str = "both") -> List[Dict[str, Any]]:
        """Raw file link retrieval - no business logic."""
        try:
            links = []
            
            if direction in ("parent", "both"):
                parent_result = self._client.table("file_links").select("*").eq("child_uuid", file_uuid).execute()
                links.extend(parent_result.data)
            
            if direction in ("child", "both"):
                child_result = self._client.table("file_links").select("*").eq("parent_uuid", file_uuid).execute()
                links.extend(child_result.data)
            
            return links
            
        except Exception as e:
            logger.error(f"❌ Failed to get file links for {file_uuid}: {e}")
            return []
    
    async def delete_file_link(self, link_id: str) -> bool:
        """Raw file link deletion - no business logic."""
        try:
            result = self._client.table("file_links").delete().eq("id", link_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ Failed to delete file link {link_id}: {e}")
            return False
    
    # ============================================================================
    # RAW LINEAGE OPERATIONS
    # ============================================================================
    
    async def get_lineage_tree(self, root_uuid: str) -> List[Dict[str, Any]]:
        """Raw lineage tree retrieval using SQL function - no business logic."""
        try:
            result = self._client.rpc("get_file_lineage_tree", {"root_uuid": root_uuid}).execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Failed to get lineage tree for {root_uuid}: {e}")
            return []
    
    async def get_file_descendants(self, root_uuid: str) -> List[Dict[str, Any]]:
        """Raw descendants retrieval using SQL function - no business logic."""
        try:
            result = self._client.rpc("get_file_descendants", {"root_uuid": root_uuid}).execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Failed to get descendants for {root_uuid}: {e}")
            return []
    
    # ============================================================================
    # RAW SEARCH OPERATIONS
    # ============================================================================
    
    async def search_files(self, user_id: str, search_term: str, 
                          content_type: Optional[str] = None,
                          file_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Raw file search - no business logic."""
        try:
            query = self._client.table("project_files").select("*").eq("user_id", user_id).eq("deleted", False)
            
            # Text search on ui_name
            query = query.ilike("ui_name", f"%{search_term}%")
            
            if content_type:
                query = query.eq("content_type", content_type)
            
            if file_type:
                query = query.eq("file_type", file_type)
            
            result = query.order("created_at", desc=True).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Failed to search files: {e}")
            return []
    
    # ============================================================================
    # RAW STATISTICS OPERATIONS
    # ============================================================================
    
    async def get_file_statistics(self, user_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """Raw file statistics - no business logic."""
        try:
            query = self._client.table("project_files").select("content_type, file_type, status").eq("user_id", user_id).eq("deleted", False)
            
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            
            result = query.execute()
            files = result.data
            
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
            
            return {
                "total_files": total_files,
                "content_types": content_types,
                "file_types": file_types,
                "statuses": statuses,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get file statistics: {e}")
            return {"total_files": 0, "content_types": {}, "file_types": {}, "statuses": {}}
    
    # ============================================================================
    # RAW HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """Raw health check - no business logic."""
        try:
            # Test basic connection
            result = self._client.table("project_files").select("uuid").limit(1).execute()
            
            return {
                "status": "healthy",
                "message": "Supabase File Management adapter is operational",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Supabase File Management adapter error: {e}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    # ============================================================================
    # RAW EMBEDDING FILES OPERATIONS
    # ============================================================================
    
    async def create_embedding_file(self, embedding_file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raw embedding file creation - no business logic."""
        try:
            result = self._client.table("embedding_files").insert(embedding_file_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"❌ Failed to create embedding file: {e}")
            raise
    
    async def get_embedding_file(self, embedding_file_uuid: str) -> Optional[Dict[str, Any]]:
        """Raw embedding file retrieval - no business logic."""
        try:
            result = self._client.table("embedding_files").select("*").eq("uuid", embedding_file_uuid).eq("status", "active").execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Failed to get embedding file {embedding_file_uuid}: {e}")
            return None
    
    async def update_embedding_file(self, embedding_file_uuid: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Raw embedding file update - no business logic."""
        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            result = self._client.table("embedding_files").update(updates).eq("uuid", embedding_file_uuid).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"❌ Failed to update embedding file {embedding_file_uuid}: {e}")
            raise
    
    async def delete_embedding_file(self, embedding_file_uuid: str) -> bool:
        """Raw embedding file deletion (soft delete) - no business logic."""
        try:
            result = self._client.table("embedding_files").update({
                "status": "deleted",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("uuid", embedding_file_uuid).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"❌ Failed to delete embedding file {embedding_file_uuid}: {e}")
            return False
    
    async def list_embedding_files(self, user_id: str, tenant_id: Optional[str] = None,
                                   parsed_file_id: Optional[str] = None,
                                   file_id: Optional[str] = None,
                                   filters: Optional[Dict[str, Any]] = None,
                                   limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Raw embedding file listing - no business logic."""
        try:
            query = self._client.table("embedding_files").select("*").eq("user_id", user_id).eq("status", "active")
            
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            
            if parsed_file_id:
                query = query.eq("parsed_file_id", parsed_file_id)
            
            if file_id:
                query = query.eq("file_id", file_id)
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.range(offset, offset + (limit or 10) - 1)
            
            result = query.order("created_at", desc=True).execute()
            return result.data
            
        except Exception as e:
            logger.error(f"❌ Failed to list embedding files: {e}")
            return []
    
    async def close(self):
        """Close the Supabase connection."""
        try:
            # Supabase client doesn't need explicit closing
            logger.info("✅ Supabase File Management adapter closed")
        except Exception as e:
            logger.error(f"❌ Error closing Supabase File Management adapter: {e}")




