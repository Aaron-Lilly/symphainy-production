#!/usr/bin/env python3
"""
Backpressure Manager - Rate Limiting and Queue Management

Manages backpressure for WebSocket message flow to prevent overload.
Implements circuit breakers and message queuing for graceful degradation.

WHAT: I manage message flow to prevent system overload
HOW: I use circuit breakers and queues to handle backpressure
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Simple circuit breaker implementation for channel protection."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        """
        Initialize Circuit Breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half_open
        self.success_count = 0  # For half-open state
    
    def is_open(self) -> bool:
        """Check if circuit is open."""
        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = "half_open"
                    self.success_count = 0
                    return False
            return True
        return False
    
    def record_success(self):
        """Record successful operation."""
        if self.state == "half_open":
            self.success_count += 1
            # Require 2 successes to close circuit
            if self.success_count >= 2:
                self.state = "closed"
                self.failure_count = 0
        else:
            self.failure_count = 0
    
    def record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            self.success_count = 0


class BackpressureManager:
    """
    Manages backpressure for WebSocket message flow.
    
    Implements circuit breakers and message queuing to handle
    overload scenarios gracefully.
    """
    
    def __init__(self, messaging_abstraction: Any, max_queue_size: int = 1000):
        """
        Initialize Backpressure Manager.
        
        Args:
            messaging_abstraction: Redis messaging abstraction
            max_queue_size: Maximum queue size per channel
        """
        self.messaging_abstraction = messaging_abstraction
        self.max_queue_size = max_queue_size
        self.logger = logger
        
        # Circuit breakers per channel
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Message queues per channel
        self.message_queues: Dict[str, asyncio.Queue] = {}
        
        # Queue drain tasks
        self.drain_tasks: Dict[str, asyncio.Task] = {}
        
        self.logger.info("✅ Backpressure Manager initialized")
    
    async def publish_with_backpressure(
        self,
        channel: str,
        message: Dict[str, Any],
        max_queue_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Publish message with backpressure handling.
        
        Args:
            channel: Channel name
            message: Message to publish
            max_queue_size: Override default max queue size
            
        Returns:
            Dict with publish status
        """
        try:
            # Get or create circuit breaker for channel
            circuit_breaker = self.circuit_breakers.get(channel)
            if not circuit_breaker:
                circuit_breaker = CircuitBreaker(
                    failure_threshold=5,
                    recovery_timeout=30
                )
                self.circuit_breakers[channel] = circuit_breaker
            
            # Check circuit breaker state
            if circuit_breaker.is_open():
                # Circuit is open, queue message instead
                self.logger.warning(f"⚠️ Circuit open for {channel}, queuing message")
                return await self._queue_message(channel, message, max_queue_size)
            
            try:
                # Try to publish
                redis_channel = f"websocket:{channel}"
                
                # Check subscriber count (if available)
                subscribers = 0
                if hasattr(self.messaging_abstraction, 'pubsub_numsub'):
                    subscribers = await self.messaging_abstraction.pubsub_numsub(redis_channel)
                elif hasattr(self.messaging_abstraction, 'get_subscriber_count'):
                    subscribers = await self.messaging_abstraction.get_subscriber_count(redis_channel)
                
                if subscribers == 0:
                    # No subscribers, queue message
                    self.logger.debug(f"No subscribers for {channel}, queuing message")
                    return await self._queue_message(channel, message, max_queue_size)
                
                # Publish to Redis
                if hasattr(self.messaging_abstraction, 'publish'):
                    await self.messaging_abstraction.publish(
                        redis_channel,
                        json.dumps(message)
                    )
                elif hasattr(self.messaging_abstraction, 'send_message'):
                    await self.messaging_abstraction.send_message(redis_channel, message)
                
                circuit_breaker.record_success()
                
                return {
                    "status": "published",
                    "queued": False,
                    "subscribers": subscribers
                }
                
            except Exception as e:
                circuit_breaker.record_failure()
                self.logger.warning(f"⚠️ Publish failed for {channel}: {e}, queuing message")
                # Queue message on failure
                return await self._queue_message(channel, message, max_queue_size)
                
        except Exception as e:
            self.logger.error(f"❌ Error in publish_with_backpressure for {channel}: {e}")
            return {
                "status": "error",
                "queued": False,
                "error": str(e)
            }
    
    async def _queue_message(
        self,
        channel: str,
        message: Dict[str, Any],
        max_queue_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Queue message when backpressure is detected."""
        try:
            queue_size = max_queue_size or self.max_queue_size
            
            queue = self.message_queues.get(channel)
            if not queue:
                queue = asyncio.Queue(maxsize=queue_size)
                self.message_queues[channel] = queue
                # Start background worker to drain queue
                task = asyncio.create_task(self._drain_queue(channel))
                self.drain_tasks[channel] = task
            
            try:
                queue.put_nowait(message)
                return {
                    "status": "queued",
                    "queued": True,
                    "queue_size": queue.qsize()
                }
            except asyncio.QueueFull:
                # Queue is full, reject message
                self.logger.warning(f"⚠️ Queue full for channel {channel}, rejecting message")
                return {
                    "status": "rejected",
                    "queued": False,
                    "reason": "queue_full",
                    "queue_size": queue.qsize()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error queuing message for {channel}: {e}")
            return {
                "status": "error",
                "queued": False,
                "error": str(e)
            }
    
    async def _drain_queue(self, channel: str):
        """Background worker to drain message queue."""
        queue = self.message_queues.get(channel)
        if not queue:
            return
        
        redis_channel = f"websocket:{channel}"
        circuit_breaker = self.circuit_breakers.get(channel)
        
        self.logger.info(f"🔄 Starting queue drain worker for {channel}")
        
        while True:
            try:
                # Wait for message with timeout
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    # No messages, check if we should continue
                    if queue.empty():
                        await asyncio.sleep(1)
                    continue
                
                # Check circuit breaker
                if circuit_breaker and circuit_breaker.is_open():
                    # Circuit still open, put message back
                    try:
                        queue.put_nowait(message)
                    except asyncio.QueueFull:
                        # Queue full, drop message
                        self.logger.warning(f"⚠️ Dropping message from {channel} queue (circuit open, queue full)")
                    await asyncio.sleep(5)  # Wait before retry
                    continue
                
                # Try to publish
                try:
                    if hasattr(self.messaging_abstraction, 'publish'):
                        await self.messaging_abstraction.publish(
                            redis_channel,
                            json.dumps(message)
                        )
                    elif hasattr(self.messaging_abstraction, 'send_message'):
                        await self.messaging_abstraction.send_message(redis_channel, message)
                    
                    if circuit_breaker:
                        circuit_breaker.record_success()
                    
                    queue.task_done()
                    self.logger.debug(f"✅ Drained message from {channel} queue")
                    
                except Exception as e:
                    if circuit_breaker:
                        circuit_breaker.record_failure()
                    self.logger.warning(f"⚠️ Error draining queue for {channel}: {e}")
                    # Put message back at front of queue
                    try:
                        queue.put_nowait(message)
                    except asyncio.QueueFull:
                        # Queue full, drop message
                        self.logger.warning(f"⚠️ Dropping message from {channel} queue (publish failed, queue full)")
                    await asyncio.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"❌ Error in queue drain worker for {channel}: {e}")
                await asyncio.sleep(1)
    
    def get_queue_status(self, channel: Optional[str] = None) -> Dict[str, Any]:
        """Get queue status for channel(s)."""
        if channel:
            queue = self.message_queues.get(channel)
            circuit_breaker = self.circuit_breakers.get(channel)
            return {
                "channel": channel,
                "queue_size": queue.qsize() if queue else 0,
                "queue_max": self.max_queue_size,
                "circuit_state": circuit_breaker.state if circuit_breaker else "closed",
                "failure_count": circuit_breaker.failure_count if circuit_breaker else 0
            }
        else:
            return {
                "channels": {
                    ch: {
                        "queue_size": queue.qsize(),
                        "queue_max": self.max_queue_size,
                        "circuit_state": self.circuit_breakers.get(ch, CircuitBreaker()).state
                    }
                    for ch, queue in self.message_queues.items()
                }
            }
    
    async def shutdown(self):
        """Shutdown backpressure manager and clean up."""
        try:
            # Cancel all drain tasks
            for task in self.drain_tasks.values():
                task.cancel()
            
            self.logger.info("✅ Backpressure Manager shut down")
            
        except Exception as e:
            self.logger.error(f"❌ Error shutting down Backpressure Manager: {e}")

