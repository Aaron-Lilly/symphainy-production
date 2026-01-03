#!/usr/bin/env python3
"""
Redis Alerting Infrastructure Adapter

Raw Redis bindings for alert management and notifications.
Thin wrapper around Redis with no business logic.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import uuid

try:
    import redis
    from redis import Redis
except ImportError:
    redis = None
    Redis = None


class RedisAlertingAdapter:
    """Raw Redis alerting adapter for alert management integration."""
    
    def __init__(self, redis_url: str = None, config_adapter=None, **kwargs):
        """
        Initialize Redis alerting adapter.
        
        Args:
            redis_url: Redis server URL (optional - will use config_adapter if not provided)
            config_adapter: ConfigAdapter for reading configuration (optional)
        """
        # Get Redis URL from config_adapter if not provided
        if not redis_url:
            if config_adapter:
                redis_url = config_adapter.get("REDIS_URL", "redis://symphainy-redis:6379")
            else:
                # Default to container name in Docker environment
                redis_url = "redis://symphainy-redis:6379"
        
        self.redis_url = redis_url
        self.logger = logging.getLogger("RedisAlertingAdapter")
        
        # Redis client (private - use wrapper methods instead)
        self._client = None
        
        # Alert storage keys
        self.alerts_key = "alerts"
        self.alert_rules_key = "alert_rules"
        self.notifications_key = "notifications"
        
        # Initialize Redis
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis client."""
        if not redis or not Redis:
            self.logger.warning("Redis not installed, alerting will be disabled")
            return
        
        try:
            # Create Redis client (private)
            self._client = Redis.from_url(self.redis_url, decode_responses=True)
            # Test connection
            self._client.ping()
            # Keep client as alias for backward compatibility (will be removed)
            self.client = self._client
            self.logger.info("✅ Redis alerting adapter initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis client: {e}")
            self._client = None
            self.client = None
    
    async def create_alert(self, alert: Dict[str, Any]) -> str:
        """Create alert in Redis."""
        if not self._client:
            return str(uuid.uuid4())  # Return mock alert ID if Redis not available
        
        try:
            alert_id = str(uuid.uuid4())
            alert_data = {
                "id": alert_id,
                "title": alert.get("title", ""),
                "message": alert.get("message", ""),
                "severity": alert.get("severity", "medium"),
                "status": alert.get("status", "active"),
                "source": alert.get("source", "unknown"),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "metadata": alert.get("metadata", {})
            }
            
            # Store alert in Redis
            self._client.hset(self.alerts_key, alert_id, json.dumps(alert_data))
            
            self.logger.debug(f"Alert created: {alert_id}")
            return alert_id
        except Exception as e:
            self.logger.error(f"Failed to create alert: {e}")
            return str(uuid.uuid4())
    
    async def update_alert(self, alert_id: str, updates: Dict[str, Any]) -> bool:
        """Update alert in Redis."""
        if not self._client:
            return True  # Return success if Redis not available
        
        try:
            # Get existing alert
            alert_data = self._client.hget(self.alerts_key, alert_id)
            if not alert_data:
                return False
            
            # Parse and update
            alert = json.loads(alert_data)
            alert.update(updates)
            alert["updated_at"] = datetime.utcnow().isoformat()
            
            # Store updated alert
            self._client.hset(self.alerts_key, alert_id, json.dumps(alert))
            
            self.logger.debug(f"Alert updated: {alert_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update alert {alert_id}: {e}")
            return False
    
    async def get_alert(self, alert_id: str) -> Optional[Dict[str, Any]]:
        """Get alert from Redis."""
        if not self._client:
            return None
        
        try:
            alert_data = self._client.hget(self.alerts_key, alert_id)
            if alert_data:
                return json.loads(alert_data)
            return None
        except Exception as e:
            self.logger.error(f"Failed to get alert {alert_id}: {e}")
            return None
    
    async def list_alerts(self, filters: Dict[str, Any] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List alerts from Redis."""
        if not self._client:
            return []
        
        try:
            # Get all alerts
            alerts_data = self._client.hgetall(self.alerts_key)
            alerts = []
            
            for alert_id, alert_json in alerts_data.items():
                alert = json.loads(alert_json)
                
                # Apply filters if provided
                if filters:
                    match = True
                    for key, value in filters.items():
                        if alert.get(key) != value:
                            match = False
                            break
                    if not match:
                        continue
                
                alerts.append(alert)
                
                # Apply limit
                if len(alerts) >= limit:
                    break
            
            return alerts
        except Exception as e:
            self.logger.error(f"Failed to list alerts: {e}")
            return []
    
    async def create_alert_rule(self, rule: Dict[str, Any]) -> str:
        """Create alert rule in Redis."""
        if not self._client:
            return str(uuid.uuid4())  # Return mock rule ID if Redis not available
        
        try:
            rule_id = str(uuid.uuid4())
            rule_data = {
                "id": rule_id,
                "name": rule.get("name", ""),
                "condition": rule.get("condition", ""),
                "severity": rule.get("severity", "medium"),
                "enabled": rule.get("enabled", True),
                "created_at": datetime.utcnow().isoformat(),
                "metadata": rule.get("metadata", {})
            }
            
            # Store rule in Redis
            self._client.hset(self.alert_rules_key, rule_id, json.dumps(rule_data))
            
            self.logger.debug(f"Alert rule created: {rule_id}")
            return rule_id
        except Exception as e:
            self.logger.error(f"Failed to create alert rule: {e}")
            return str(uuid.uuid4())
    
    async def evaluate_alert_rules(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate alert rules against data."""
        if not self._client:
            return []
        
        try:
            # Get all enabled rules
            rules_data = self._client.hgetall(self.alert_rules_key)
            alerts = []
            
            for rule_id, rule_json in rules_data.items():
                rule = json.loads(rule_json)
                
                if not rule.get("enabled", True):
                    continue
                
                # Simple condition evaluation (in real implementation, use proper expression evaluator)
                condition = rule.get("condition", "")
                if self._evaluate_condition(condition, data):
                    # Create alert
                    alert = {
                        "title": f"Rule triggered: {rule['name']}",
                        "message": f"Condition '{condition}' was met",
                        "severity": rule.get("severity", "medium"),
                        "status": "active",
                        "source": f"rule:{rule_id}",
                        "metadata": {
                            "rule_id": rule_id,
                            "rule_name": rule["name"],
                            "condition": condition,
                            "data": data
                        }
                    }
                    alerts.append(alert)
            
            return alerts
        except Exception as e:
            self.logger.error(f"Failed to evaluate alert rules: {e}")
            return []
    
    async def send_notification(self, alert: Dict[str, Any], channel: Dict[str, Any]) -> bool:
        """Send notification via Redis."""
        if not self._client:
            return True  # Return success if Redis not available
        
        try:
            notification_data = {
                "id": str(uuid.uuid4()),
                "alert_id": alert.get("id"),
                "channel_type": channel.get("type", "email"),
                "channel_config": channel.get("config", {}),
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store notification in Redis
            self._client.hset(self.notifications_key, notification_data["id"], json.dumps(notification_data))
            
            self.logger.debug(f"Notification queued: {notification_data['id']}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send notification: {e}")
            return False
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge alert."""
        return await self.update_alert(alert_id, {
            "status": "acknowledged",
            "acknowledged_by": user_id,
            "acknowledged_at": datetime.utcnow().isoformat()
        })
    
    async def resolve_alert(self, alert_id: str, user_id: str) -> bool:
        """Resolve alert."""
        return await self.update_alert(alert_id, {
            "status": "resolved",
            "resolved_by": user_id,
            "resolved_at": datetime.utcnow().isoformat()
        })
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis alerting adapter health."""
        try:
            if not self._client:
                return {
                    "status": "unhealthy",
                    "reason": "redis_not_available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Test connection
            self._client.ping()
            
            # Get basic stats
            info = self._client.info()
            
            return {
                "status": "healthy",
                "redis_url": self.redis_url,
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "reason": "health_check_failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _evaluate_condition(self, condition: str, data: Dict[str, Any]) -> bool:
        """Simple condition evaluation (placeholder for proper expression evaluator)."""
        try:
            # This is a very basic implementation
            # In production, use a proper expression evaluator like `asteval` or `simpleeval`
            if "cpu_usage" in condition and "cpu_usage" in data:
                # Example: "cpu_usage > 80"
                if ">" in condition:
                    threshold = float(condition.split(">")[1].strip())
                    return data["cpu_usage"] > threshold
            return False
        except Exception:
            return False







