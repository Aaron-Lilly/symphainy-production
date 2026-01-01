#!/usr/bin/env python3
"""
Librarian Service - Knowledge Management Module

Micro-module for knowledge item management operations.
"""

import uuid
from typing import Any, Dict, Optional
from datetime import datetime


class KnowledgeManagement:
    """Knowledge management module for Librarian service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def store_knowledge(self, knowledge_data: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> str:
        """Store knowledge item using knowledge abstractions."""
        title = knowledge_data.get("title", "unknown")
        
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "store_knowledge_start",
            success=True,
            details={"title": title}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "write"):
                        await self.service.record_health_metric("store_knowledge_access_denied", 1.0, {"title": title})
                        await self.service.log_operation_with_telemetry("store_knowledge_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to store knowledge")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("store_knowledge_tenant_denied", 1.0, {"title": title, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("store_knowledge_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            item_id = str(uuid.uuid4())
            knowledge_item = {
                "item_id": item_id,
                "title": title,
                "content": knowledge_data.get("content"),
                "category": knowledge_data.get("category"),
                "tags": knowledge_data.get("tags", []),
                "metadata": knowledge_data.get("metadata", {}),
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Store metadata via Knowledge Governance Abstraction
            metadata_result = await self.service.knowledge_governance_abstraction.create_asset_metadata(
                asset_id=item_id,
                metadata=knowledge_item
            )
            
            if not metadata_result:
                raise Exception("Failed to store knowledge item metadata")
            
            # Index via Knowledge Discovery Abstraction (for search)
            # The abstraction handles Meilisearch indexing internally
            
            # Cache in Redis via Cache Abstraction
            cache_key = f"knowledge:{item_id}"
            cache_abstraction = self.service.get_cache_abstraction()
            if cache_abstraction:
                await cache_abstraction.set_value(
                    key=cache_key,
                    value=knowledge_item,
                    ttl=3600  # 1 hour
                )
            
            self.service.knowledge_base[item_id] = knowledge_item
            
            # Record health metric
            await self.service.record_health_metric(
                "knowledge_stored",
                1.0,
                {"item_id": item_id, "title": title}
            )
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "store_knowledge_complete",
                success=True,
                details={"item_id": item_id, "title": title}
            )
            
            return item_id
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "store_knowledge")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "store_knowledge_complete",
                success=False,
                details={"title": title, "error": str(e)}
            )
            raise
    
    async def get_knowledge_item(self, item_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve knowledge item using caching and abstractions."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "get_knowledge_item_start",
            success=True,
            details={"item_id": item_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "read"):
                        await self.service.record_health_metric("get_knowledge_item_access_denied", 1.0, {"item_id": item_id})
                        await self.service.log_operation_with_telemetry("get_knowledge_item_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to read knowledge item")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("get_knowledge_item_tenant_denied", 1.0, {"item_id": item_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("get_knowledge_item_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Try Redis cache first
            cache_key = f"knowledge:{item_id}"
            cache_abstraction = self.service.get_cache_abstraction()
            cached_item = None
            if cache_abstraction:
                cached_item = await cache_abstraction.get(cache_key)
                # Cache returns dict, extract value if wrapped
                if cached_item and isinstance(cached_item, dict):
                    if "value" in cached_item:
                        cached_item = cached_item["value"]
            
            if cached_item:
                # Record health metric
                await self.service.record_health_metric(
                    "knowledge_item_retrieved",
                    1.0,
                    {"item_id": item_id, "source": "cache"}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_knowledge_item_complete",
                    success=True,
                    details={"item_id": item_id, "source": "cache"}
                )
                
                return {
                    "item_id": item_id,
                    "item": cached_item,
                    "source": "cache",
                    "status": "success"
                }
            
            # Fallback to Knowledge Governance Abstraction
            metadata = await self.service.knowledge_governance_abstraction.get_asset_metadata(asset_id=item_id)
            if metadata:
                # Cache for future requests
                if cache_abstraction:
                    await cache_abstraction.set_value(
                        key=cache_key,
                        value=metadata,
                        ttl=3600
                    )
                
                # Record health metric
                await self.service.record_health_metric(
                    "knowledge_item_retrieved",
                    1.0,
                    {"item_id": item_id, "source": "database"}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_knowledge_item_complete",
                    success=True,
                    details={"item_id": item_id, "source": "database"}
                )
                
                return {
                    "item_id": item_id,
                    "item": metadata,
                    "source": "database",
                    "status": "success"
                }
            else:
                await self.service.record_health_metric("knowledge_item_not_found", 1.0, {"item_id": item_id})
                await self.service.log_operation_with_telemetry("get_knowledge_item_complete", success=False, details={"item_id": item_id, "reason": "not_found"})
                return {
                    "item_id": item_id,
                    "item": None,
                    "error": "Knowledge item not found",
                    "status": "error"
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_knowledge_item")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_knowledge_item_complete",
                success=False,
                details={"item_id": item_id, "error": str(e)}
            )
            return {
                "item_id": item_id,
                "item": None,
                "error": str(e),
                "status": "error"
            }
    
    async def update_knowledge_item(self, item_id: str, updates: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update knowledge item using abstractions."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "update_knowledge_item_start",
            success=True,
            details={"item_id": item_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "write"):
                        await self.service.record_health_metric("update_knowledge_item_access_denied", 1.0, {"item_id": item_id})
                        await self.service.log_operation_with_telemetry("update_knowledge_item_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to update knowledge item")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("update_knowledge_item_tenant_denied", 1.0, {"item_id": item_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("update_knowledge_item_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Update via Knowledge Governance Abstraction
            success = await self.service.knowledge_governance_abstraction.update_asset_metadata(
                asset_id=item_id,
                metadata=updates
            )
            
            if success:
                # Invalidate cache
                cache_key = f"knowledge:{item_id}"
                cache_abstraction = self.service.get_cache_abstraction()
                if cache_abstraction:
                    await cache_abstraction.delete(cache_key)
                
                # Record health metric
                await self.service.record_health_metric(
                    "knowledge_item_updated",
                    1.0,
                    {"item_id": item_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "update_knowledge_item_complete",
                    success=True,
                    details={"item_id": item_id}
                )
                
                return {
                    "item_id": item_id,
                    "updated": True,
                    "updates": updates,
                    "status": "success"
                }
            else:
                await self.service.record_health_metric("knowledge_item_update_failed", 1.0, {"item_id": item_id})
                await self.service.log_operation_with_telemetry("update_knowledge_item_complete", success=False, details={"item_id": item_id, "error": "Failed to update"})
                return {
                    "item_id": item_id,
                    "updated": False,
                    "error": "Failed to update knowledge item",
                    "status": "error"
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "update_knowledge_item")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "update_knowledge_item_complete",
                success=False,
                details={"item_id": item_id, "error": str(e)}
            )
            return {
                "item_id": item_id,
                "updated": False,
                "error": str(e),
                "status": "error"
            }
    
    async def delete_knowledge_item(self, item_id: str, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Delete knowledge item using abstractions."""
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "delete_knowledge_item_start",
            success=True,
            details={"item_id": item_id}
        )
        
        try:
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(user_context, "knowledge_management", "write"):
                        await self.service.record_health_metric("delete_knowledge_item_access_denied", 1.0, {"item_id": item_id})
                        await self.service.log_operation_with_telemetry("delete_knowledge_item_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to delete knowledge item")
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.service.record_health_metric("delete_knowledge_item_tenant_denied", 1.0, {"item_id": item_id, "tenant_id": tenant_id})
                            await self.service.log_operation_with_telemetry("delete_knowledge_item_complete", success=False)
                            raise PermissionError(f"Tenant access denied: {tenant_id}")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Delete via Knowledge Governance Abstraction
            success = await self.service.knowledge_governance_abstraction.delete_asset_metadata(asset_id=item_id)
            
            if success:
                # Remove from cache
                cache_key = f"knowledge:{item_id}"
                cache_abstraction = self.service.get_cache_abstraction()
                if cache_abstraction:
                    await cache_abstraction.delete(cache_key)
                
                # Remove from local state
                if item_id in self.service.knowledge_base:
                    del self.service.knowledge_base[item_id]
                
                # Record health metric
                await self.service.record_health_metric(
                    "knowledge_item_deleted",
                    1.0,
                    {"item_id": item_id}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "delete_knowledge_item_complete",
                    success=True,
                    details={"item_id": item_id}
                )
                
                return True
            else:
                await self.service.record_health_metric("knowledge_item_delete_failed", 1.0, {"item_id": item_id})
                await self.service.log_operation_with_telemetry("delete_knowledge_item_complete", success=False, details={"item_id": item_id})
                return False
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "delete_knowledge_item")
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "delete_knowledge_item_complete",
                success=False,
                details={"item_id": item_id, "error": str(e)}
            )
            return False







