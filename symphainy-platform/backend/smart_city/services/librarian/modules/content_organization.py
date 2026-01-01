#!/usr/bin/env python3
"""
Librarian Service - Content Organization Module

Micro-module for content cataloging and schema management.
"""

import uuid
from typing import Any, Dict
from datetime import datetime


class ContentOrganization:
    """Content organization module for Librarian service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def catalog_content(self, content_data: Dict[str, Any]) -> str:
        """Catalog content using Knowledge Governance Abstraction."""
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            catalog_id = str(uuid.uuid4())
            catalog_entry = {
                "catalog_id": catalog_id,
                "content_type": content_data.get("content_type"),
                "title": content_data.get("title"),
                "description": content_data.get("description"),
                "category": content_data.get("category"),
                "tags": content_data.get("tags", []),
                "metadata": content_data.get("metadata", {}),
                "created_at": datetime.utcnow().isoformat(),
                "status": "cataloged"
            }
            
            # Store catalog entry via Knowledge Governance Abstraction
            metadata_result = await self.service.knowledge_governance_abstraction.create_asset_metadata(
                asset_id=catalog_id,
                metadata=catalog_entry
            )
            
            if not metadata_result:
                raise Exception("Failed to catalog content")
            
            # Cache catalog entry in Redis
            cache_key = f"catalog:{catalog_id}"
            await self.service.messaging_abstraction.set_value(
                key=cache_key,
                value=catalog_entry,
                ttl=1800  # 30 minutes
            )
            
            self.service.content_catalog[catalog_id] = catalog_entry
            
            if self.service.logger:
                self.service.logger.info(f"✅ Content cataloged: {catalog_id}")
            return catalog_id
            
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error cataloging content: {str(e)}")
            raise e
    
    async def manage_content_schema(self, schema_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage content schema using Knowledge Governance Abstraction."""
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            schema_id = schema_data.get("schema_id") or str(uuid.uuid4())
            schema_definition = {
                "schema_id": schema_id,
                "schema_name": schema_data.get("schema_name"),
                "schema_version": schema_data.get("schema_version", "1.0"),
                "fields": schema_data.get("fields", []),
                "validation_rules": schema_data.get("validation_rules", {}),
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Store schema via Knowledge Governance Abstraction
            metadata_result = await self.service.knowledge_governance_abstraction.create_asset_metadata(
                asset_id=schema_id,
                metadata=schema_definition
            )
            
            if metadata_result:
                if self.service.logger:
                    self.service.logger.info(f"✅ Content schema managed: {schema_id}")
                return {
                    "schema_id": schema_id,
                    "schema_definition": schema_definition,
                    "managed": True,
                    "status": "success"
                }
            else:
                return {
                    "schema_id": schema_id,
                    "managed": False,
                    "error": "Failed to manage content schema",
                    "status": "error"
                }
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error managing content schema: {str(e)}")
            return {
                "schema_id": schema_data.get("schema_id"),
                "managed": False,
                "error": str(e),
                "status": "error"
            }
    
    async def get_content_categories(self) -> Dict[str, Any]:
        """Get content categories using caching and abstractions."""
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Try Redis cache first
            cache_key = "content_categories"
            cached_categories = await self.service.messaging_abstraction.get_value(cache_key)
            if cached_categories:
                if self.service.logger:
                    self.service.logger.info("✅ Content categories retrieved from cache")
                return {
                    "categories": cached_categories,
                    "source": "cache",
                    "status": "success"
                }
            
            # Fallback to metadata query (simplified - categories could come from aggregation)
            # For now, return empty or use a default set
            categories = {
                "document": "Documents",
                "image": "Images",
                "video": "Videos",
                "audio": "Audio",
                "data": "Data Files"
            }
            
            # Cache for future requests
            await self.service.messaging_abstraction.set_value(
                key=cache_key,
                value=categories,
                ttl=3600  # 1 hour
            )
            
            if self.service.logger:
                self.service.logger.info("✅ Content categories retrieved")
            return {
                "categories": categories,
                "source": "default",
                "status": "success"
            }
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error getting content categories: {str(e)}")
            return {
                "categories": {},
                "error": str(e),
                "status": "error"
            }







