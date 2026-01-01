#!/usr/bin/env python3
"""
Supabase Metadata Adapter - Raw Technology Client (Compact)

Raw Supabase client wrapper for metadata operations.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw Supabase operations for file metadata
HOW (Infrastructure Implementation): I use real Supabase client with no business logic
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from supabase import create_client, Client
    from gotrue.errors import AuthError as SupabaseAuthError
except ImportError:
    class Client:
        def __init__(self): pass
    class SupabaseAuthError(Exception): pass
    def create_client(url, key): return Client()

logger = logging.getLogger(__name__)

class SupabaseMetadataAdapter:
    """Raw Supabase client wrapper for metadata operations - no business logic."""
    
    def __init__(self, url: str, anon_key: str, service_key: str = None):
        """Initialize Supabase metadata adapter with real credentials."""
        self.url = url
        self.anon_key = anon_key
        self.service_key = service_key
        
        self.anon_client: Client = create_client(url, anon_key)
        self.service_client: Client = create_client(url, service_key) if service_key else self.anon_client
        
        logger.info(f"✅ Supabase Metadata adapter initialized with URL: {url}")
    
    # ============================================================================
    # RAW METADATA OPERATIONS
    # ============================================================================
    
    async def create_metadata(self, table: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Raw metadata creation - no business logic."""
        try:
            result = self.service_client.table(table).insert(metadata).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"❌ Failed to create metadata in {table}: {e}")
            raise
    
    async def get_metadata(self, table: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Raw metadata retrieval - no business logic."""
        try:
            result = self.service_client.table(table).select("*").eq("id", record_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Failed to get metadata from {table}: {e}")
            return None
    
    async def update_metadata(self, table: str, record_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Raw metadata update - no business logic."""
        try:
            result = self.service_client.table(table).update(updates).eq("id", record_id).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"❌ Failed to update metadata in {table}: {e}")
            raise
    
    async def delete_metadata(self, table: str, record_id: str) -> bool:
        """Raw metadata deletion - no business logic."""
        try:
            self.service_client.table(table).delete().eq("id", record_id).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete metadata from {table}: {e}")
            return False
    
    # ============================================================================
    # RAW METADATA QUERY OPERATIONS
    # ============================================================================
    
    async def query_metadata(self, table: str, filters: Dict[str, Any] = None,
                           order_by: str = None, limit: int = None, offset: int = None) -> List[Dict[str, Any]]:
        """Raw metadata query - no business logic."""
        try:
            query = self.service_client.table(table).select("*")
            
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            if order_by:
                query = query.order(order_by)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.range(offset, offset + (limit or 1000) - 1)
            
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Failed to query metadata from {table}: {e}")
            return []
    
    async def search_metadata(self, table: str, search_column: str, search_term: str,
                            limit: int = None) -> List[Dict[str, Any]]:
        """Raw metadata search - no business logic."""
        try:
            query = self.service_client.table(table).select("*").ilike(search_column, f"%{search_term}%")
            if limit:
                query = query.limit(limit)
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Failed to search metadata in {table}: {e}")
            return []
    
    # ============================================================================
    # RAW FILE METADATA OPERATIONS
    # ============================================================================
    
    async def create_file_metadata(self, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Raw file metadata creation - no business logic."""
        try:
            result = self.service_client.table("file_metadata").insert(file_metadata).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"❌ Failed to create file metadata: {e}")
            raise
    
    async def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Raw file metadata retrieval - no business logic."""
        try:
            result = self.service_client.table("file_metadata").select("*").eq("id", file_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Failed to get file metadata: {e}")
            return None
    
    async def update_file_metadata(self, file_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Raw file metadata update - no business logic."""
        try:
            result = self.service_client.table("file_metadata").update(updates).eq("id", file_id).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"❌ Failed to update file metadata: {e}")
            raise
    
    async def get_files_by_user(self, user_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Raw files by user query - no business logic."""
        try:
            query = self.service_client.table("file_metadata").select("*").eq("user_id", user_id)
            if limit:
                query = query.limit(limit)
            result = query.execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Failed to get files by user: {e}")
            return []
    
    # ============================================================================
    # RAW LINEAGE OPERATIONS
    # ============================================================================
    
    async def create_lineage_record(self, lineage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raw lineage record creation - no business logic."""
        try:
            result = self.service_client.table("data_lineage").insert(lineage_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"❌ Failed to create lineage record: {e}")
            raise
    
    async def get_lineage_by_asset(self, asset_id: str) -> List[Dict[str, Any]]:
        """Raw lineage by asset query - no business logic."""
        try:
            result = self.service_client.table("data_lineage").select("*").eq("asset_id", asset_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Failed to get lineage by asset: {e}")
            return []
    
    async def get_lineage_by_source(self, source_id: str) -> List[Dict[str, Any]]:
        """Raw lineage by source query - no business logic."""
        try:
            result = self.service_client.table("data_lineage").select("*").eq("source_id", source_id).execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Failed to get lineage by source: {e}")
            return []
    
    # ============================================================================
    # RAW POLICY OPERATIONS
    # ============================================================================
    
    async def create_policy(self, policy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Raw policy creation - no business logic."""
        try:
            result = self.service_client.table("policies").insert(policy_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            logger.error(f"❌ Failed to create policy: {e}")
            raise
    
    async def get_policy(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Raw policy retrieval - no business logic."""
        try:
            result = self.service_client.table("policies").select("*").eq("id", policy_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Failed to get policy: {e}")
            return None
    
    async def get_policies_by_type(self, policy_type: str) -> List[Dict[str, Any]]:
        """Raw policies by type query - no business logic."""
        try:
            result = self.service_client.table("policies").select("*").eq("type", policy_type).execute()
            return result.data
        except Exception as e:
            logger.error(f"❌ Failed to get policies by type: {e}")
            return []
    
    # ============================================================================
    # RAW AUTHENTICATION OPERATIONS
    # ============================================================================
    
    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Raw user authentication - no business logic."""
        try:
            response = self.anon_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if response.user:
                return {
                    "user": response.user,
                    "session": response.session
                }
            return None
        except SupabaseAuthError as e:
            logger.error(f"❌ Authentication error: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Failed to authenticate user: {e}")
            return None
    
    async def get_user_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Raw user context retrieval - no business logic."""
        try:
            result = self.service_client.table("user_context").select("*").eq("user_id", user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"❌ Failed to get user context: {e}")
            return None
    
    # ============================================================================
    # RAW CONNECTION OPERATIONS
    # ============================================================================
    
    async def test_connection(self) -> bool:
        """Raw connection test - no business logic."""
        try:
            self.service_client.table("file_metadata").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """Raw connection info - no business logic."""
        try:
            return {
                "url": self.url,
                "has_service_key": bool(self.service_key),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Failed to get connection info: {e}")
            return {}

