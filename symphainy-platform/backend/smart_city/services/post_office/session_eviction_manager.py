#!/usr/bin/env python3
"""
Session Eviction Manager - Stale Connection Cleanup

Manages session eviction for WebSocket connections.
Implements heartbeat-based connection management with automatic cleanup.

WHAT: I clean up stale WebSocket connections
HOW: I use heartbeat monitoring and automatic eviction
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SessionEvictionManager:
    """
    Manages session eviction for WebSocket connections.
    
    Implements heartbeat-based connection management with automatic
    cleanup of stale connections.
    """
    
    def __init__(
        self,
        connection_registry: Any,
        heartbeat_interval: int = 30,
        max_idle_time: int = 300,
        eviction_check_interval: int = 60
    ):
        """
        Initialize Session Eviction Manager.
        
        Args:
            connection_registry: ConnectionRegistry instance
            heartbeat_interval: Seconds between heartbeat checks
            max_idle_time: Maximum idle time before eviction (seconds)
            eviction_check_interval: Interval for eviction checks (seconds)
        """
        self.connection_registry = connection_registry
        self.heartbeat_interval = heartbeat_interval
        self.max_idle_time = max_idle_time
        self.eviction_check_interval = eviction_check_interval
        self.logger = logger
        
        # Active heartbeat monitors
        self.heartbeat_monitors: Dict[str, asyncio.Task] = {}
        
        # Eviction task
        self.eviction_task: Optional[asyncio.Task] = None
        
        self.logger.info("✅ Session Eviction Manager initialized")
    
    async def start_heartbeat_monitor(
        self,
        connection_id: str,
        websocket: Any,
        local_connections: Dict[str, Any]
    ):
        """
        Start heartbeat monitoring for connection.
        
        Args:
            connection_id: Connection ID
            websocket: WebSocket connection
            local_connections: Dict of local connections (for cleanup)
        """
        try:
            # Check if monitor already exists
            if connection_id in self.heartbeat_monitors:
                self.logger.debug(f"Heartbeat monitor already exists for {connection_id}")
                return
            
            # Create heartbeat monitor task
            task = asyncio.create_task(
                self._heartbeat_loop(connection_id, websocket, local_connections)
            )
            self.heartbeat_monitors[connection_id] = task
            
            self.logger.debug(f"✅ Started heartbeat monitor for {connection_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start heartbeat monitor for {connection_id}: {e}")
    
    async def _heartbeat_loop(
        self,
        connection_id: str,
        websocket: Any,
        local_connections: Dict[str, Any]
    ):
        """Background task for heartbeat monitoring."""
        try:
            while True:
                await asyncio.sleep(self.heartbeat_interval)
                
                try:
                    # Send ping
                    await websocket.send_json({
                        "type": "ping",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
                    # Update last heartbeat in Redis
                    await self.connection_registry.update_connection_heartbeat(connection_id)
                    
                    self.logger.debug(f"💓 Heartbeat sent to {connection_id}")
                    
                except Exception as e:
                    # Connection likely dead, stop monitoring
                    self.logger.warning(f"⚠️ Heartbeat failed for {connection_id}: {e}")
                    await self._evict_connection(connection_id, local_connections)
                    break
                    
        except asyncio.CancelledError:
            self.logger.debug(f"Heartbeat monitor cancelled for {connection_id}")
        except Exception as e:
            self.logger.error(f"❌ Error in heartbeat loop for {connection_id}: {e}")
            await self._evict_connection(connection_id, local_connections)
    
    async def start_eviction_monitor(self, local_connections: Dict[str, Any]):
        """Start background eviction monitor."""
        if self.eviction_task and not self.eviction_task.done():
            self.logger.warning("Eviction monitor already running")
            return
        
        self.eviction_task = asyncio.create_task(
            self._eviction_loop(local_connections)
        )
        self.logger.info("✅ Started eviction monitor")
    
    async def _eviction_loop(self, local_connections: Dict[str, Any]):
        """Background task to check for stale connections."""
        try:
            while True:
                await asyncio.sleep(self.eviction_check_interval)
                
                try:
                    # Get all connections from registry
                    # Note: This is expensive, in production use Redis SCAN with cursor
                    # For now, we'll check connections that are in local_connections
                    
                    stale_connections = []
                    now = datetime.utcnow()
                    
                    for connection_id in list(local_connections.keys()):
                        try:
                            # Get connection from registry
                            conn = await self.connection_registry.get_connection(connection_id)
                            if not conn:
                                # Connection not in registry, mark as stale
                                stale_connections.append(connection_id)
                                continue
                            
                            # Check last heartbeat
                            last_heartbeat_str = conn.get("last_heartbeat")
                            if last_heartbeat_str:
                                try:
                                    last_heartbeat = datetime.fromisoformat(last_heartbeat_str.replace('Z', '+00:00'))
                                    idle_time = (now - last_heartbeat).total_seconds()
                                    
                                    if idle_time > self.max_idle_time:
                                        self.logger.warning(
                                            f"⚠️ Connection {connection_id} idle for {idle_time}s, evicting"
                                        )
                                        stale_connections.append(connection_id)
                                except Exception as e:
                                    self.logger.warning(f"⚠️ Error parsing heartbeat for {connection_id}: {e}")
                                    stale_connections.append(connection_id)
                            else:
                                # No heartbeat, check last activity
                                last_activity_str = conn.get("last_activity")
                                if last_activity_str:
                                    try:
                                        last_activity = datetime.fromisoformat(last_activity_str.replace('Z', '+00:00'))
                                        idle_time = (now - last_activity).total_seconds()
                                        
                                        if idle_time > self.max_idle_time:
                                            self.logger.warning(
                                                f"⚠️ Connection {connection_id} inactive for {idle_time}s, evicting"
                                            )
                                            stale_connections.append(connection_id)
                                    except Exception as e:
                                        self.logger.warning(f"⚠️ Error parsing activity for {connection_id}: {e}")
                                        stale_connections.append(connection_id)
                                else:
                                    # No activity or heartbeat, evict
                                    self.logger.warning(f"⚠️ Connection {connection_id} has no activity/heartbeat, evicting")
                                    stale_connections.append(connection_id)
                                    
                        except Exception as e:
                            self.logger.error(f"❌ Error checking connection {connection_id}: {e}")
                            stale_connections.append(connection_id)
                    
                    # Evict stale connections
                    for connection_id in stale_connections:
                        await self._evict_connection(connection_id, local_connections)
                    
                    if stale_connections:
                        self.logger.info(f"🧹 Evicted {len(stale_connections)} stale connections")
                        
                except Exception as e:
                    self.logger.error(f"❌ Error in eviction loop: {e}")
                    
        except asyncio.CancelledError:
            self.logger.debug("Eviction monitor cancelled")
        except Exception as e:
            self.logger.error(f"❌ Error in eviction monitor: {e}")
    
    async def _evict_connection(self, connection_id: str, local_connections: Dict[str, Any]):
        """Evict a connection."""
        try:
            # Stop heartbeat monitor
            if connection_id in self.heartbeat_monitors:
                task = self.heartbeat_monitors[connection_id]
                task.cancel()
                del self.heartbeat_monitors[connection_id]
            
            # Close WebSocket if still open
            websocket = local_connections.get(connection_id)
            if websocket:
                try:
                    await websocket.close(code=1008, reason="Connection evicted (stale)")
                except:
                    pass  # Connection might already be closed
                del local_connections[connection_id]
            
            # Unregister from Redis
            await self.connection_registry.unregister_connection(connection_id)
            
            self.logger.info(f"✅ Evicted connection {connection_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Error evicting connection {connection_id}: {e}")
    
    async def stop_heartbeat_monitor(self, connection_id: str):
        """Stop heartbeat monitor for connection."""
        try:
            if connection_id in self.heartbeat_monitors:
                task = self.heartbeat_monitors[connection_id]
                task.cancel()
                del self.heartbeat_monitors[connection_id]
                self.logger.debug(f"✅ Stopped heartbeat monitor for {connection_id}")
        except Exception as e:
            self.logger.error(f"❌ Error stopping heartbeat monitor for {connection_id}: {e}")
    
    async def shutdown(self, local_connections: Dict[str, Any]):
        """Shutdown eviction manager and clean up."""
        try:
            # Cancel all heartbeat monitors
            for connection_id in list(self.heartbeat_monitors.keys()):
                await self.stop_heartbeat_monitor(connection_id)
            
            # Cancel eviction task
            if self.eviction_task and not self.eviction_task.done():
                self.eviction_task.cancel()
                try:
                    await self.eviction_task
                except asyncio.CancelledError:
                    pass
            
            # Evict all remaining connections
            for connection_id in list(local_connections.keys()):
                await self._evict_connection(connection_id, local_connections)
            
            self.logger.info("✅ Session Eviction Manager shut down")
            
        except Exception as e:
            self.logger.error(f"❌ Error shutting down Session Eviction Manager: {e}")

