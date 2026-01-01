#!/usr/bin/env python3
"""
State Management Adapter - Infrastructure Adapter

Redis-based state management adapter harvested from working infrastructure foundation patterns.
This is Layer 1 of the 5-layer architecture for Traffic Cop state management.

WHAT (Infrastructure Role): I provide Redis-based state management operations
HOW (Infrastructure Implementation): I use real Redis patterns from infrastructure foundation
"""

import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

# Try to import Redis, fall back to mock if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    # Note: Using mock implementation when Redis is not available


class MockStateManagementClient:
    """Mock state management client for testing when Redis is not available."""
    
    def __init__(self):
        self.states = {}
        self.state_syncs = {}
        self.user_states = {}
        self.state_metrics = {
            "total_states": 0,
            "active_states": 0,
            "sync_operations": 0,
            "successful_syncs": 0,
            "failed_syncs": 0
        }
    
    async def sync_state(self, state_data: Dict[str, Any], tenant_id: str, state_type: str = "default") -> str:
        """Sync state."""
        state_id = f"state_{uuid.uuid4().hex[:8]}"
        self.states[state_id] = {
            "state_id": state_id,
            "tenant_id": tenant_id,
            "state_data": state_data,
            "state_type": state_type,
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "is_active": True
        }
        self.state_metrics["total_states"] += 1
        self.state_metrics["active_states"] += 1
        return state_id
    
    async def get_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """Get state by ID."""
        return self.states.get(state_id)
    
    async def update_state(self, state_id: str, state_data: Dict[str, Any]) -> bool:
        """Update state."""
        if state_id in self.states:
            self.states[state_id]["state_data"].update(state_data)
            self.states[state_id]["last_updated"] = datetime.utcnow().isoformat()
            return True
        return False
    
    async def delete_state(self, state_id: str) -> bool:
        """Delete state."""
        if state_id in self.states:
            self.states[state_id]["is_active"] = False
            return True
        return False
    
    async def get_user_states(self, user_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """Get user states."""
        user_states = []
        for state_id, state_data in self.states.items():
            if state_data.get("is_active", False):
                user_states.append(state_data)
        return user_states
    
    async def cleanup_expired_states(self) -> int:
        """Cleanup expired states."""
        cleaned_count = 0
        current_time = datetime.utcnow()
        
        for state_id, state_data in self.states.items():
            expires_at = datetime.fromisoformat(state_data.get("expires_at", current_time.isoformat()))
            if current_time > expires_at:
                state_data["is_active"] = False
                cleaned_count += 1
        
        return cleaned_count
    
    async def get_state_metrics(self) -> Dict[str, Any]:
        """Get state metrics."""
        return self.state_metrics.copy()


class StateManagementAdapter:
    """
    State Management Adapter - Infrastructure Adapter
    
    Redis-based state management adapter harvested from working infrastructure foundation patterns.
    This adapter provides state synchronization and management capabilities for Traffic Cop.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", di_container=None):
        """Initialize State Management Adapter."""
        if not di_container:
            raise ValueError("DI Container is required for StateManagementAdapter initialization")
        self.redis_url = redis_url
        self.redis_client = None
        self.is_connected = False
        self.di_container = di_container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger("StateManagementAdapter")
        
        # State management metrics
        self.metrics = {
            "total_states": 0,
            "active_states": 0,
            "sync_operations": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "average_sync_time": 0.0
        }
        
        self.logger.info("✅ State Management Adapter initialized")
    
    async def initialize(self) -> bool:
        """Initialize Redis connection."""
        try:
            if REDIS_AVAILABLE:
                # Real Redis connection
                self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
                
                # Test connection
                await self.redis_client.ping()
                self.is_connected = True
                self.logger.info("✅ Connected to Redis successfully for state management")
            else:
                # Mock Redis for development
                self.redis_client = MockStateManagementClient()
                self.is_connected = True
                self.logger.info("✅ Using mock Redis client for state management")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("initialize", {
                    "service": self.service_name,
                    "redis_available": REDIS_AVAILABLE,
                    "success": True
                })
            
            return True
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "initialize",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Failed to initialize Redis: {e}")
            # Fall back to mock
            self.redis_client = MockStateManagementClient()
            self.is_connected = True
            self.logger.warning("⚠️ Falling back to mock Redis client for state management")
            return True
    
    async def sync_state(self, state_data: Dict[str, Any], tenant_id: str, 
                        state_type: str = "default") -> str:
        """
        Sync state.
        
        Args:
            state_data: State data to sync
            tenant_id: Tenant identifier
            state_type: Type of state
            
        Returns:
            str: State ID
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            # Generate state ID
            state_id = f"state_{uuid.uuid4().hex[:8]}"
            
            # Prepare state data
            state_info = {
                "state_id": state_id,
                "tenant_id": tenant_id,
                "state_data": state_data,
                "state_type": state_type,
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "is_active": True
            }
            
            # Store state in Redis
            state_key = f"state:{state_id}"
            await self.redis_client.hset(state_key, {
                "data": json.dumps(state_info),
                "created_at": datetime.utcnow().isoformat(),
                "ttl": "3600"
            })
            
            # Set expiration
            await self.redis_client.expire(state_key, 3600)
            
            # Store tenant state mapping
            tenant_states_key = f"tenant_states:{tenant_id}"
            await self.redis_client.sadd(tenant_states_key, state_id)
            await self.redis_client.expire(tenant_states_key, 3600)
            
            # Update metrics
            self.metrics["total_states"] += 1
            self.metrics["active_states"] += 1
            self.metrics["sync_operations"] += 1
            self.metrics["successful_syncs"] += 1
            
            self.logger.info(f"✅ State synced: {state_id} for tenant {tenant_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("sync_state", {
                    "state_id": state_id,
                    "tenant_id": tenant_id,
                    "state_type": state_type,
                    "success": True
                })
            
            return state_id
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "sync_state",
                    "tenant_id": tenant_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error syncing state: {e}")
            self.metrics["failed_syncs"] += 1
            raise
    
    async def get_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Get state by ID.
        
        Args:
            state_id: State identifier
            
        Returns:
            Optional[Dict]: State data if found and active
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            state_key = f"state:{state_id}"
            state_data = await self.redis_client.hgetall(state_key)
            
            if state_data:
                state_info = json.loads(state_data.get("data", "{}"))
                
                # Check if state is active and not expired
                if state_info.get("is_active", False):
                    expires_at = datetime.fromisoformat(state_info.get("expires_at", datetime.utcnow().isoformat()))
                    if datetime.utcnow() < expires_at:
                        self.logger.debug(f"✅ State retrieved: {state_id}")
                        
                        # Record telemetry on success
                        telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                        if telemetry:
                            await telemetry.record_platform_operation_event("get_state", {
                                "state_id": state_id,
                                "found": True,
                                "success": True
                            })
                        
                        return state_info
            
            self.logger.warning(f"⚠️ State not found or expired: {state_id}")
            
            # Record telemetry for not found
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_state", {
                    "state_id": state_id,
                    "found": False,
                    "success": True
                })
            
            return None
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_state",
                    "state_id": state_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting state: {e}")
            return None
    
    async def update_state(self, state_id: str, state_data: Dict[str, Any]) -> bool:
        """
        Update state.
        
        Args:
            state_id: State identifier
            state_data: Updated state data
            
        Returns:
            bool: Success status
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            state_key = f"state:{state_id}"
            existing_data = await self.redis_client.hgetall(state_key)
            
            if existing_data:
                state_info = json.loads(existing_data.get("data", "{}"))
                
                # Update state data
                state_info["state_data"].update(state_data)
                state_info["last_updated"] = datetime.utcnow().isoformat()
                
                # Store updated state
                await self.redis_client.hset(state_key, "data", json.dumps(state_info))
                
                self.logger.debug(f"✅ State updated: {state_id}")
                
                # Record telemetry on success
                telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
                if telemetry:
                    await telemetry.record_platform_operation_event("update_state", {
                        "state_id": state_id,
                        "success": True
                    })
                
                return True
            
            self.logger.warning(f"⚠️ State not found for update: {state_id}")
            return False
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "update_state",
                    "state_id": state_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error updating state: {e}")
            return False
    
    async def delete_state(self, state_id: str) -> bool:
        """
        Delete state.
        
        Args:
            state_id: State identifier
            
        Returns:
            bool: Success status
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            state_key = f"state:{state_id}"
            
            # Get state data to find tenant_id
            state_data = await self.redis_client.hgetall(state_key)
            if state_data:
                state_info = json.loads(state_data.get("data", "{}"))
                tenant_id = state_info.get("tenant_id")
                
                # Remove from tenant states set
                if tenant_id:
                    tenant_states_key = f"tenant_states:{tenant_id}"
                    await self.redis_client.srem(tenant_states_key, state_id)
            
            # Mark state as inactive
            if state_data:
                state_info = json.loads(state_data.get("data", "{}"))
                state_info["is_active"] = False
                await self.redis_client.hset(state_key, "data", json.dumps(state_info))
            
            self.logger.info(f"✅ State deleted: {state_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("delete_state", {
                    "state_id": state_id,
                    "success": True
                })
            
            return True
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "delete_state",
                    "state_id": state_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error deleting state: {e}")
            return False
    
    async def get_user_states(self, user_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Get user states.
        
        Args:
            user_id: User identifier
            tenant_id: Tenant identifier
            
        Returns:
            List[Dict]: List of user states
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            # Get tenant states
            tenant_states_key = f"tenant_states:{tenant_id}"
            state_ids = await self.redis_client.smembers(tenant_states_key)
            
            user_states = []
            for state_id in state_ids:
                state_key = f"state:{state_id}"
                state_data = await self.redis_client.hgetall(state_key)
                
                if state_data:
                    state_info = json.loads(state_data.get("data", "{}"))
                    if state_info.get("is_active", False):
                        user_states.append(state_info)
            
            self.logger.debug(f"✅ Retrieved {len(user_states)} states for user {user_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_user_states", {
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "state_count": len(user_states),
                    "success": True
                })
            
            return user_states
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_user_states",
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting user states: {e}")
            return []
    
    async def cleanup_expired_states(self) -> int:
        """
        Cleanup expired states.
        
        Returns:
            int: Number of states cleaned up
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            # Get all state keys
            state_keys = await self.redis_client.keys("state:*")
            cleaned_count = 0
            current_time = datetime.utcnow()
            
            for state_key in state_keys:
                state_data = await self.redis_client.hgetall(state_key)
                if state_data:
                    state_info = json.loads(state_data.get("data", "{}"))
                    expires_at = datetime.fromisoformat(state_info.get("expires_at", current_time.isoformat()))
                    
                    if current_time > expires_at:
                        # Mark as inactive
                        state_info["is_active"] = False
                        await self.redis_client.hset(state_key, "data", json.dumps(state_info))
                        cleaned_count += 1
            
            self.logger.info(f"✅ Cleaned up {cleaned_count} expired states")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("cleanup_expired_states", {
                    "cleaned_count": cleaned_count,
                    "success": True
                })
            
            return cleaned_count
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "cleanup_expired_states",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error cleaning up expired states: {e}")
            return 0
    
    async def get_state_metrics(self) -> Dict[str, Any]:
        """
        Get state metrics.
        
        Returns:
            Dict: State metrics
        """
        try:
            # Update active states count
            if self.is_connected:
                active_states = await self.redis_client.keys("state:*")
                self.metrics["active_states"] = len(active_states)
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_state_metrics", {
                    "active_states": self.metrics.get("active_states", 0),
                    "success": True
                })
            
            return self.metrics.copy()
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_state_metrics",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error getting state metrics: {e}")
            return self.metrics.copy()
    
    async def sync_state_batch(self, states: List[Dict[str, Any]], tenant_id: str) -> List[str]:
        """
        Sync multiple states in batch.
        
        Args:
            states: List of state data
            tenant_id: Tenant identifier
            
        Returns:
            List[str]: List of state IDs
        """
        try:
            if not self.is_connected:
                raise RuntimeError("Redis not connected")
            
            state_ids = []
            for state_data in states:
                state_id = await self.sync_state(state_data, tenant_id)
                state_ids.append(state_id)
            
            self.logger.info(f"✅ Batch synced {len(state_ids)} states for tenant {tenant_id}")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("sync_state_batch", {
                    "tenant_id": tenant_id,
                    "state_count": len(state_ids),
                    "success": True
                })
            
            return state_ids
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "sync_state_batch",
                    "tenant_id": tenant_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error batch syncing states: {e}")
            return []
    
    async def close(self):
        """Close Redis connection."""
        try:
            if self.redis_client and hasattr(self.redis_client, 'close'):
                await self.redis_client.close()
            self.is_connected = False
            self.logger.info("✅ State Management Adapter connection closed")
            
            # Record telemetry on success
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("close", {
                    "service": self.service_name,
                    "success": True
                })
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "close",
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Error closing connection: {e}")



