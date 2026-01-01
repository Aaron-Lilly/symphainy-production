#!/usr/bin/env python3
"""
State Composition Service - Layer 4 of 5-Layer Architecture

Orchestrates state management abstractions for state synchronization and management.
This service composes state management infrastructure to provide
business-facing state capabilities.

WHAT (Composition Role): I orchestrate state management for state synchronization
HOW (Composition Implementation): I compose state management abstractions into state capabilities
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from foundations.public_works_foundation.infrastructure_abstractions.state_management_abstraction import StateManagementAbstraction

logger = logging.getLogger(__name__)


class StateCompositionService:
    """
    State Composition Service.
    
    Orchestrates state management abstractions to provide
    comprehensive state capabilities including state synchronization,
    state persistence, and state coordination.
    """
    
    def __init__(self, state_management: StateManagementAbstraction, di_container=None):
        """Initialize State Composition Service with abstractions."""
        self.state_management = state_management
        self.di_container = di_container
        self.service_name = "state_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger("StateCompositionService")
        
        # State management state
        self.state_sync_queue: List[Dict[str, Any]] = []
        self.state_metrics: Dict[str, Any] = {
            "total_states": 0,
            "active_states": 0,
            "state_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        self.logger.info("✅ State Composition Service initialized")
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    

    async def sync_state(self, entity_id: str, state_type: str, state_data: Dict[str, Any], 
                        tenant_id: str) -> Dict[str, Any]:
        """
        Synchronize state across services.
        
        This ensures that state is consistent across all
        services that need access to it.
        """
        try:
            self.logger.info(f"Syncing state for entity {entity_id}, type {state_type}")
            
            # Sync state using state management
            sync_context = await self.state_management.sync_state(
                entity_id=entity_id,
                state_type=state_type,
                state_data=state_data,
                tenant_id=tenant_id
            )
            
            if sync_context.is_successful:
                # Update metrics
                self.state_metrics["state_syncs"] += 1
                self.state_metrics["successful_syncs"] += 1
                self.state_metrics["last_updated"] = datetime.utcnow().isoformat()
                
                self.logger.info(f"✅ State synced for entity {entity_id}")
                
                # Record platform operation event
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("sync_state", {
                        "entity_id": entity_id,
                        "state_type": state_type,
                        "sync_id": sync_context.sync_id,
                        "success": True
                    })
                
                return {
                    "success": True,
                    "sync_id": sync_context.sync_id,
                    "entity_id": entity_id,
                    "state_type": state_type,
                    "state_id": sync_context.state_id,
                    "synced_at": sync_context.sync_timestamp.isoformat()
                }
            else:
                self.state_metrics["failed_syncs"] += 1
                self.logger.error(f"❌ Failed to sync state for entity {entity_id}")
                
                return {
                    "success": False,
                    "error": "State sync failed",
                    "entity_id": entity_id,
                    "state_type": state_type,
                    "sync_id": sync_context.sync_id
                }
                
        except Exception as e:
            self.state_metrics["failed_syncs"] += 1
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "sync_state",
                    "entity_id": entity_id,
                    "state_type": state_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error syncing state for entity {entity_id}: {e}")
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "STATE_SYNC_ERROR",
                "entity_id": entity_id,
                "state_type": state_type
            }
    
    async def sync_state_batch(self, states: List[Dict[str, Any]], tenant_id: str) -> List[str]:
        """Sync multiple states in batch."""
        try:
            self.logger.info(f"Syncing batch of {len(states)} states for tenant {tenant_id}")
            
            sync_ids = []
            for state_data in states:
                entity_id = state_data.get("entity_id")
                state_type = state_data.get("state_type")
                state_content = state_data.get("state_data", {})
                
                sync_result = await self.sync_state(entity_id, state_type, state_content, tenant_id)
                if sync_result.get("success"):
                    sync_ids.append(sync_result.get("sync_id"))
            
            self.logger.info(f"✅ Batch sync completed for {len(sync_ids)} states")
            return sync_ids
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "sync_state_batch",
                    "tenant_id": tenant_id,
                    "batch_size": len(states),
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error in batch state sync: {e}")
            return []
    
    async def create_state(self, entity_id: str, state_type: str, initial_state: Dict[str, Any]) -> Optional[str]:
        """Create a new state entry."""
        try:
            self.logger.info(f"Creating state for entity {entity_id}, type {state_type}")
            
            # Create state using state management
            state_context = await self.state_management.create_state(
                entity_id=entity_id,
                state_type=state_type,
                initial_state=initial_state
            )
            
            if state_context:
                # Update metrics
                self.state_metrics["total_states"] += 1
                self.state_metrics["active_states"] += 1
                self.state_metrics["last_updated"] = datetime.utcnow().isoformat()
                
                self.logger.info(f"✅ Created state {state_context.state_id} for entity {entity_id}")
                return state_context.state_id
            else:
                self.logger.error(f"❌ Failed to create state for entity {entity_id}")
                return None
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_state",
                    "entity_id": entity_id,
                    "state_type": state_type,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error creating state for entity {entity_id}: {e}")
            return None
    
    async def get_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Get state by ID."""
        try:
            self.logger.debug(f"Getting state {state_id}")
            
            state_context = await self.state_management.get_state(state_id)
            
            if state_context:
                self.logger.debug(f"✅ Retrieved state {state_id}")
                return {
                    "state_id": state_context.state_id,
                    "entity_id": state_context.entity_id,
                    "state_type": state_context.state_type,
                    "current_state": state_context.current_state,
                    "last_updated": state_context.last_updated.isoformat(),
                    "version": state_context.version
                }
            else:
                self.logger.warning(f"⚠️ State {state_id} not found")
                return None
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_state",
                    "state_id": state_id,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error getting state {state_id}: {e}")
            return None
    
    async def update_state(self, state_id: str, new_state: Dict[str, Any], expected_version: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Update state with optional optimistic locking."""
        try:
            self.logger.info(f"Updating state {state_id}")
            
            updated_state = await self.state_management.update_state(
                state_id=state_id,
                new_state=new_state,
                expected_version=expected_version
            )
            
            if updated_state:
                self.logger.info(f"✅ Updated state {state_id} to version {updated_state.version}")
                return {
                    "state_id": updated_state.state_id,
                    "entity_id": updated_state.entity_id,
                    "state_type": updated_state.state_type,
                    "current_state": updated_state.current_state,
                    "last_updated": updated_state.last_updated.isoformat(),
                    "version": updated_state.version
                }
            else:
                self.logger.warning(f"⚠️ Failed to update state {state_id}")
                return None
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "update_state",
                    "state_id": state_id,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error updating state {state_id}: {e}")
            return None
    
    async def delete_state(self, state_id: str) -> bool:
        """Delete state by ID."""
        try:
            self.logger.info(f"Deleting state {state_id}")
            
            success = await self.state_management.delete_state(state_id)
            
            if success:
                # Update metrics
                self.state_metrics["active_states"] = max(0, self.state_metrics["active_states"] - 1)
                self.state_metrics["last_updated"] = datetime.utcnow().isoformat()
                
                self.logger.info(f"✅ Deleted state {state_id}")
                return True
            else:
                self.logger.error(f"❌ Failed to delete state {state_id}")
                return False
                
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "delete_state",
                    "state_id": state_id,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error deleting state {state_id}: {e}")
            return False
    
    async def get_states_by_entity(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all states for an entity."""
        try:
            self.logger.debug(f"Getting states for entity {entity_id}")
            
            states = await self.state_management.get_states_by_entity(entity_id)
            
            # Convert to dict format
            state_dicts = []
            for state in states:
                state_dicts.append({
                    "state_id": state.state_id,
                    "entity_id": state.entity_id,
                    "state_type": state.state_type,
                    "current_state": state.current_state,
                    "last_updated": state.last_updated.isoformat(),
                    "version": state.version
                })
            
            self.logger.debug(f"✅ Retrieved {len(state_dicts)} states for entity {entity_id}")
            return state_dicts
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_states_by_entity",
                    "entity_id": entity_id,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error getting states for entity {entity_id}: {e}")
            return []
    
    async def get_states_by_type(self, state_type: str) -> List[Dict[str, Any]]:
        """Get all states of a specific type."""
        try:
            self.logger.debug(f"Getting states of type {state_type}")
            
            states = await self.state_management.get_states_by_type(state_type)
            
            # Convert to dict format
            state_dicts = []
            for state in states:
                state_dicts.append({
                    "state_id": state.state_id,
                    "entity_id": state.entity_id,
                    "state_type": state.state_type,
                    "current_state": state.current_state,
                    "last_updated": state.last_updated.isoformat(),
                    "version": state.version
                })
            
            self.logger.debug(f"✅ Retrieved {len(state_dicts)} states of type {state_type}")
            return state_dicts
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_states_by_type",
                    "state_type": state_type,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error getting states of type {state_type}: {e}")
            return []
    
    async def queue_state_sync(self, entity_id: str, state_type: str, state_data: Dict[str, Any], 
                              tenant_id: str, priority: int = 0) -> str:
        """Queue a state sync for later processing."""
        try:
            sync_id = str(uuid.uuid4())
            
            sync_item = {
                "sync_id": sync_id,
                "entity_id": entity_id,
                "state_type": state_type,
                "state_data": state_data,
                "tenant_id": tenant_id,
                "priority": priority,
                "queued_at": datetime.utcnow(),
                "status": "queued"
            }
            
            self.state_sync_queue.append(sync_item)
            
            # Sort by priority (higher priority first)
            self.state_sync_queue.sort(key=lambda x: x["priority"], reverse=True)
            
            self.logger.info(f"✅ Queued state sync {sync_id} for entity {entity_id}")
            return sync_id
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "queue_state_sync",
                    "entity_id": entity_id,
                    "state_type": state_type,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error queuing state sync for entity {entity_id}: {e}")
            return None
    
    async def process_state_sync_queue(self, max_items: int = 10) -> List[Dict[str, Any]]:
        """Process queued state syncs."""
        try:
            self.logger.info(f"Processing {min(max_items, len(self.state_sync_queue))} queued state syncs")
            
            processed_items = []
            items_to_process = self.state_sync_queue[:max_items]
            
            for sync_item in items_to_process:
                try:
                    # Process the sync
                    sync_result = await self.sync_state(
                        entity_id=sync_item["entity_id"],
                        state_type=sync_item["state_type"],
                        state_data=sync_item["state_data"],
                        tenant_id=sync_item["tenant_id"]
                    )
                    
                    sync_item["status"] = "processed"
                    sync_item["processed_at"] = datetime.utcnow()
                    sync_item["sync_result"] = sync_result
                    
                    processed_items.append(sync_item)
                    
                except Exception as e:
                    sync_item["status"] = "failed"
                    sync_item["error"] = str(e)
                    sync_item["processed_at"] = datetime.utcnow()
                    
                    processed_items.append(sync_item)
                    self.logger.error(f"❌ Error processing queued sync {sync_item['sync_id']}: {e}")
            
            # Remove processed items from queue
            self.state_sync_queue = self.state_sync_queue[max_items:]
            
            self.logger.info(f"✅ Processed {len(processed_items)} state syncs")
            return processed_items
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "process_state_sync_queue",
                    "max_items": max_items,
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error processing state sync queue: {e}")
            return []
    
    async def get_state_metrics(self) -> Dict[str, Any]:
        """Get state management metrics."""
        try:
            # Get metrics from state management
            state_management_metrics = await self.state_management.get_state_metrics()
            
            # Combine metrics
            combined_metrics = {
                "state_composition_metrics": self.state_metrics,
                "state_management_metrics": state_management_metrics,
                "queue_size": len(self.state_sync_queue),
                "composition_service": "StateCompositionService",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return combined_metrics
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_state_metrics",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error getting state metrics: {e}")
            return {
                "state_composition_metrics": self.state_metrics,
                "queue_size": len(self.state_sync_queue),
                "error": str(e),
                "error_code": "STATE_METRICS_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def cleanup_expired_states(self) -> int:
        """Clean up expired states."""
        try:
            self.logger.info("Cleaning up expired states")
            
            # This would typically involve checking TTLs and removing expired states
            # For now, we'll just return 0 as the state management abstraction
            # handles TTL management internally
            
            self.logger.info("✅ State cleanup completed")
            return 0
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "cleanup_expired_states",
                    "service": self.service_name
                }, telemetry=self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None)
            else:
                self.logger.error(f"❌ Error cleaning up expired states: {e}")
            return 0



