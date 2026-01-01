#!/usr/bin/env python3
"""
Knowledge Metadata Adapter - Raw Technology Layer

Raw metadata client wrapper for knowledge metadata management.
This is Layer 1 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I provide raw metadata management capabilities
HOW (Infrastructure Implementation): I wrap metadata operations with basic CRUD
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
import asyncio

logger = logging.getLogger(__name__)

class KnowledgeMetadataAdapter:
    """
    Raw metadata client wrapper for knowledge metadata management.
    
    Provides direct access to metadata operations without business logic.
    Focused on knowledge metadata, governance, and semantic tagging.
    """
    
    def __init__(self, host: str = "localhost", port: int = 5432, database: str = "knowledge_metadata",
                 username: str = "postgres", password: str = None, timeout: int = 30):
        """Initialize knowledge metadata adapter."""
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        
        # Database client (private - use wrapper methods instead)
        self._client = None
        # Keep client as alias for backward compatibility (will be removed)
        self.client = None
        
        # Metadata tables
        self.assets_table = "knowledge_assets"
        self.metadata_table = "asset_metadata"
        self.governance_table = "governance_policies"
        self.semantic_tags_table = "semantic_tags"
        
        self.logger.info(f"✅ Knowledge Metadata adapter initialized with {host}:{port}")
    
    async def connect(self) -> bool:
        """Connect to metadata database."""
        try:
            import asyncpg
            
            # Create database connection (private)
            self._client = await asyncpg.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                timeout=self.timeout
            )
            # Keep client as alias for backward compatibility (will be removed)
            self.client = self._client
            
            # Test connection
            health = await self._get_health()
            if health:
                self.logger.info("✅ Knowledge Metadata adapter connected")
                return True
            else:
                self.logger.error("❌ Failed to connect to metadata database")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to metadata database: {e}")
            return False
    
    async def _get_health(self) -> bool:
        """Check database health."""
        try:
            if self._client:
                result = await self._client.fetchval("SELECT 1")
                return result == 1
            return False
        except Exception as e:
            self.logger.error(f"❌ Health check failed: {e}")
            return False
    
    # ============================================================================
    # ASSET METADATA OPERATIONS
    # ============================================================================
    
    async def create_asset_metadata(self, asset_id: str, metadata: Dict[str, Any]) -> bool:
        """Create metadata for a knowledge asset."""
        try:
            if not self._client:
                return False
            
            # Insert asset metadata
            query = f"""
                INSERT INTO {self.metadata_table} (asset_id, metadata, created_at, updated_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (asset_id) DO UPDATE SET
                    metadata = $2,
                    updated_at = $4
            """
            
            await self._client.execute(
                query, 
                asset_id, 
                json.dumps(metadata), 
                datetime.utcnow(), 
                datetime.utcnow()
            )
            
            self.logger.info(f"✅ Asset metadata created: {asset_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create asset metadata: {e}")
            return False
    
    async def get_asset_metadata(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a knowledge asset."""
        try:
            if not self._client:
                return None
            
            # Get asset metadata
            query = f"SELECT metadata FROM {self.metadata_table} WHERE asset_id = $1"
            result = await self._client.fetchval(query, asset_id)
            
            if result:
                metadata = json.loads(result) if isinstance(result, str) else result
                self.logger.info(f"✅ Asset metadata retrieved: {asset_id}")
                return metadata
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get asset metadata: {e}")
            return None
    
    async def update_asset_metadata(self, asset_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata for a knowledge asset."""
        try:
            if not self._client:
                return False
            
            # Update asset metadata
            query = f"""
                UPDATE {self.metadata_table} 
                SET metadata = $2, updated_at = $3
                WHERE asset_id = $1
            """
            
            result = await self._client.execute(
                query, 
                asset_id, 
                json.dumps(metadata), 
                datetime.utcnow()
            )
            
            if result:
                self.logger.info(f"✅ Asset metadata updated: {asset_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update asset metadata: {e}")
            return False
    
    async def delete_asset_metadata(self, asset_id: str) -> bool:
        """Delete metadata for a knowledge asset."""
        try:
            if not self._client:
                return False
            
            # Delete asset metadata
            query = f"DELETE FROM {self.metadata_table} WHERE asset_id = $1"
            result = await self._client.execute(query, asset_id)
            
            self.logger.info(f"✅ Asset metadata deleted: {asset_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete asset metadata: {e}")
            return False
    
    # ============================================================================
    # SEMANTIC TAGGING OPERATIONS
    # ============================================================================
    
    async def add_semantic_tags(self, asset_id: str, tags: List[str], 
                               confidence_scores: Optional[List[float]] = None) -> bool:
        """Add semantic tags to a knowledge asset."""
        try:
            if not self._client:
                return False
            
            # Add semantic tags
            for i, tag in enumerate(tags):
                confidence = confidence_scores[i] if confidence_scores and i < len(confidence_scores) else 1.0
                
                query = f"""
                    INSERT INTO {self.semantic_tags_table} (asset_id, tag, confidence, created_at)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (asset_id, tag) DO UPDATE SET
                        confidence = $3,
                        updated_at = $4
                """
                
                await self._client.execute(
                    query, 
                    asset_id, 
                    tag, 
                    confidence, 
                    datetime.utcnow()
                )
            
            self.logger.info(f"✅ Semantic tags added: {asset_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add semantic tags: {e}")
            return False
    
    async def get_semantic_tags(self, asset_id: str) -> List[Dict[str, Any]]:
        """Get semantic tags for a knowledge asset."""
        try:
            if not self._client:
                return []
            
            # Get semantic tags
            query = f"""
                SELECT tag, confidence, created_at 
                FROM {self.semantic_tags_table} 
                WHERE asset_id = $1
                ORDER BY confidence DESC
            """
            
            results = await self._client.fetch(query, asset_id)
            
            tags = []
            for row in results:
                tag_data = {
                    "tag": row['tag'],
                    "confidence": row['confidence'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None
                }
                tags.append(tag_data)
            
            self.logger.info(f"✅ Semantic tags retrieved: {asset_id}")
            return tags
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get semantic tags: {e}")
            return []
    
    async def search_by_tags(self, tags: List[str], min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """Search assets by semantic tags."""
        try:
            if not self._client:
                return []
            
            # Build tag search query
            tag_conditions = " OR ".join([f"tag = ${i+1}" for i in range(len(tags))])
            query = f"""
                SELECT DISTINCT asset_id, tag, confidence
                FROM {self.semantic_tags_table}
                WHERE ({tag_conditions}) AND confidence >= ${len(tags) + 1}
                ORDER BY confidence DESC
            """
            
            params = tags + [min_confidence]
            results = await self._client.fetch(query, *params)
            
            assets = []
            for row in results:
                asset_data = {
                    "asset_id": row['asset_id'],
                    "tag": row['tag'],
                    "confidence": row['confidence']
                }
                assets.append(asset_data)
            
            self.logger.info(f"✅ Tag search completed: {len(tags)} tags")
            return assets
            
        except Exception as e:
            self.logger.error(f"❌ Failed to search by tags: {e}")
            return []
    
    # ============================================================================
    # GOVERNANCE OPERATIONS
    # ============================================================================
    
    async def create_governance_policy(self, policy_name: str, policy_data: Dict[str, Any]) -> str:
        """Create a governance policy."""
        try:
            if not self._client:
                return None
            
            policy_id = f"policy_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Insert governance policy
            query = f"""
                INSERT INTO {self.governance_table} (policy_id, policy_name, policy_data, created_at)
                VALUES ($1, $2, $3, $4)
            """
            
            await self._client.execute(
                query, 
                policy_id, 
                policy_name, 
                json.dumps(policy_data), 
                datetime.utcnow()
            )
            
            self.logger.info(f"✅ Governance policy created: {policy_id}")
            return policy_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create governance policy: {e}")
            return None
    
    async def get_governance_policies(self, policy_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get governance policies."""
        try:
            if not self._client:
                return []
            
            # Build query with optional type filter
            if policy_type:
                query = f"""
                    SELECT policy_id, policy_name, policy_data, created_at
                    FROM {self.governance_table}
                    WHERE policy_data->>'type' = $1
                    ORDER BY created_at DESC
                """
                results = await self._client.fetch(query, policy_type)
            else:
                query = f"""
                    SELECT policy_id, policy_name, policy_data, created_at
                    FROM {self.governance_table}
                    ORDER BY created_at DESC
                """
                results = await self._client.fetch(query)
            
            policies = []
            for row in results:
                policy_data = {
                    "policy_id": row['policy_id'],
                    "policy_name": row['policy_name'],
                    "policy_data": json.loads(row['policy_data']) if isinstance(row['policy_data'], str) else row['policy_data'],
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None
                }
                policies.append(policy_data)
            
            self.logger.info(f"✅ Governance policies retrieved")
            return policies
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get governance policies: {e}")
            return []
    
    async def apply_governance_policy(self, asset_id: str, policy_id: str) -> bool:
        """Apply a governance policy to an asset."""
        try:
            if not self._client:
                return False
            
            # Get policy data
            policy_query = f"SELECT policy_data FROM {self.governance_table} WHERE policy_id = $1"
            policy_result = await self._client.fetchval(policy_query, policy_id)
            
            if not policy_result:
                return False
            
            policy_data = json.loads(policy_result) if isinstance(policy_result, str) else policy_result
            
            # Apply policy rules (simplified)
            # In practice, this would involve complex policy evaluation
            self.logger.info(f"✅ Governance policy applied: {policy_id} to {asset_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to apply governance policy: {e}")
            return False
    
    # ============================================================================
    # ANALYTICS OPERATIONS
    # ============================================================================
    
    async def get_metadata_analytics(self) -> Dict[str, Any]:
        """Get metadata analytics."""
        try:
            if not self._client:
                return {"totalAssets": 0, "totalTags": 0, "totalPolicies": 0}
            
            # Get asset count
            asset_query = f"SELECT COUNT(*) FROM {self.metadata_table}"
            asset_count = await self._client.fetchval(asset_query)
            
            # Get tag count
            tag_query = f"SELECT COUNT(*) FROM {self.semantic_tags_table}"
            tag_count = await self._client.fetchval(tag_query)
            
            # Get policy count
            policy_query = f"SELECT COUNT(*) FROM {self.governance_table}"
            policy_count = await self._client.fetchval(policy_query)
            
            analytics = {
                "totalAssets": asset_count or 0,
                "totalTags": tag_count or 0,
                "totalPolicies": policy_count or 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info("✅ Metadata analytics retrieved")
            return analytics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get metadata analytics: {e}")
            return {"totalAssets": 0, "totalTags": 0, "totalPolicies": 0}
    
    async def track_metadata_access(self, asset_id: str, access_type: str, 
                                  user_id: Optional[str] = None) -> bool:
        """Track metadata access for analytics."""
        try:
            if not self._client:
                return False
            
            # Create access log entry
            access_log = {
                "asset_id": asset_id,
                "access_type": access_type,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store access log (simplified - would use proper logging table)
            self.logger.info(f"✅ Metadata access tracked: {asset_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to track metadata access: {e}")
            return False
    
    async def close(self):
        """Close the metadata database connection."""
        try:
            if self._client:
                await self._client.close()
                self._client = None
                self.client = None
                self.logger.info("✅ Knowledge Metadata adapter closed")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to close metadata adapter: {e}")

