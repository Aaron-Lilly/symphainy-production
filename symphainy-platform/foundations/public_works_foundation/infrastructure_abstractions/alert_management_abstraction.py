#!/usr/bin/env python3
"""
Alert Management Abstraction - Infrastructure abstraction for alert management

Coordinates alert adapters and handles infrastructure-level concerns like
error handling, retries, logging, and adapter selection for Redis-based alert management.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.alerting_protocol import (
    AlertingProtocol, Alert, AlertRule,
    AlertSeverity, AlertStatus
)

class AlertManagementAbstraction:
    """
    Alert Management Abstraction - Infrastructure abstraction for alert management
    
    Coordinates different alert adapters and handles infrastructure-level concerns.
    This layer provides swappable alert management engines and infrastructure coordination.
    
    NOTE: This abstraction accepts an alert adapter via dependency injection.
          All adapter creation happens in Public Works Foundation Service.
    """
    
    def __init__(self,
                 alert_adapter: AlertingProtocol,  # Required: Accept adapter via DI
                 config_adapter=None,
                 service_name: str = "alert_management_abstraction",
                 di_container=None):
        """
        Initialize Alert Management Abstraction.
        
        Args:
            alert_adapter: Alert adapter implementing AlertingProtocol (required)
            config_adapter: Configuration adapter (optional)
            service_name: Service name for logging (optional)
            di_container: DI Container for logging (required)
        """
        if not alert_adapter:
            raise ValueError("AlertManagementAbstraction requires alert_adapter via dependency injection")
        if not di_container:
            raise ValueError("DI Container is required for AlertManagementAbstraction initialization")
        
        self.service_name = service_name
        self.di_container = di_container
        
        # Get logger from DI Container
        if not hasattr(di_container, 'get_logger'):
            raise RuntimeError("DI Container does not have get_logger method")
        self.logger = di_container.get_logger(service_name)
        self.config_adapter = config_adapter
        
        # Use injected adapter
        self.adapter = alert_adapter
        self.adapter_type = getattr(alert_adapter, 'adapter_type', 'unknown')
        
        # Infrastructure-level configuration
        self.max_retries = 3
        self.retry_delay = 0.1
        self.timeout = 30
        
        self.logger.info(f"Initialized Alert Management Abstraction with {self.adapter_type} adapter")
    
    async def create_alert(self, 
                         alert: Alert) -> str:
        """Create alert with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Creating alert '{alert.title}' with {self.adapter_type}")
            
            # Create alert with retry logic
            alert_id = await self._execute_with_retry(
                self.adapter.create_alert,
                alert
            )
            
            self.logger.info(f"✅ Alert created: {alert.title} ({alert_id})")
            
            return alert_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create alert '{alert.title}': {e}")
            raise  # Re-raise for service layer to handle
    
    async def update_alert(self, alert_id: str, updates: Dict[str, Any]) -> bool:
        """Update alert with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Updating alert {alert_id} with {self.adapter_type}")
            
            # Update alert with retry logic
            success = await self._execute_with_retry(
                self.adapter.update_alert,
                alert_id,
                updates
            )
            
            if success:
                self.logger.debug(f"✅ Alert updated: {alert_id}")
            else:
                self.logger.warning(f"⚠️ Failed to update alert: {alert_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update alert {alert_id}: {e}")
            raise  # Re-raise for service layer to handle

        """Get alert with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Getting alert {alert_id} with {self.adapter_type}")
            
            # Get alert with retry logic
            alert = await self._execute_with_retry(
                self.adapter.get_alert,
                alert_id
            )
            
            if alert:
                self.logger.debug(f"✅ Alert retrieved: {alert_id}")
            else:
                self.logger.warning(f"⚠️ Alert not found: {alert_id}")
            
            return alert
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get alert {alert_id}: {e}")
            raise  # Re-raise for service layer to handle

        """List alerts with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Listing alerts with filters using {self.adapter_type}")
            
            # List alerts with retry logic
            alerts = await self._execute_with_retry(
                self.adapter.list_alerts,
                filters,
                limit
            )
            
            self.logger.debug(f"✅ Retrieved {len(alerts)} alerts")
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list alerts: {e}")
            raise  # Re-raise for service layer to handle

        """Create alert rule with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Creating alert rule '{rule.name}' with {self.adapter_type}")
            
            # Create rule with retry logic
            rule_id = await self._execute_with_retry(
                self.adapter.create_alert_rule,
                rule
            )
            
            self.logger.info(f"✅ Alert rule created: {rule.name} ({rule_id})")
            
            return rule_id
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create alert rule '{rule.name}': {e}")
            raise e
    
            raise  # Re-raise for service layer to handle
    async def evaluate_alert_rules(self, 
                                 data: Dict[str, Any]) -> List[Alert]:
        """Evaluate alert rules with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Evaluating alert rules with {self.adapter_type}")
            
            # Evaluate rules with retry logic
            alerts = await self._execute_with_retry(
                self.adapter.evaluate_alert_rules,
                data
            )
            
            self.logger.debug(f"✅ Generated {len(alerts)} alerts from rules")
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"❌ Failed to evaluate alert rules: {e}")
            raise  # Re-raise for service layer to handle
    
    async def send_notification(self, alert_id: str, notification: Dict[str, Any]) -> bool:
        """
        Send notification with infrastructure-level coordination.
        
        Matches the AlertingProtocol signature.
        """
        try:
            self.logger.debug(f"Sending notification for alert {alert_id} via channels: {channels}")
            
            # Send notification with retry logic
            # Adapter may have different signature, so we handle both cases
            success = await self._execute_with_retry(
                self.adapter.send_notification,
                alert_id,
                channels
            )
            
            if success:
                self.logger.debug(f"✅ Notification sent for alert {alert_id}")
            else:
                self.logger.warning(f"⚠️ Failed to send notification for alert {alert_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send notification for alert {alert_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge alert with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Acknowledging alert {alert_id} by user {user_id}")
            
            # Acknowledge alert with retry logic
            success = await self._execute_with_retry(
                self.adapter.acknowledge_alert,
                alert_id,
                user_id
            )
            
            if success:
                self.logger.info(f"✅ Alert acknowledged: {alert_id}")
            else:
                self.logger.warning(f"⚠️ Failed to acknowledge alert: {alert_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to acknowledge alert {alert_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def resolve_alert(self, alert_id: str, resolution: Dict[str, Any]) -> bool:
        """Resolve alert with infrastructure-level coordination."""
        try:
            self.logger.debug(f"Resolving alert {alert_id} by user {user_id}")
            
            # Resolve alert with retry logic
            success = await self._execute_with_retry(
                self.adapter.resolve_alert,
                alert_id,
                user_id
            )
            
            if success:
                self.logger.info(f"✅ Alert resolved: {alert_id}")
            else:
                self.logger.warning(f"⚠️ Failed to resolve alert: {alert_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to resolve alert {alert_id}: {e}")
            raise  # Re-raise for service layer to handle

        """Check alert management infrastructure health."""
        try:
            self.logger.debug("Checking alert management infrastructure health")
            
            # Check adapter health
            adapter_health = await self.adapter.health_check()
            
            # Add abstraction-level health info
            return {
                "status": "healthy" if adapter_health.get("status") == "healthy" else "unhealthy",
                "abstraction_layer": "alert_management_abstraction",
                "adapter_type": self.adapter_type,
                "adapter_health": adapter_health,
                "infrastructure_metrics": {
                    "max_retries": self.max_retries,
                    "retry_delay": self.retry_delay,
                    "timeout": self.timeout
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"❌ Alert management infrastructure health check failed: {e}")
    
    # ============================================================================
    # IMPLEMENT MISSING ABSTRACT METHODS FROM AlertingProtocol
    # ============================================================================
    
            raise  # Re-raise for service layer to handle

        """Get active alerts (abstract method implementation)."""
        try:
            filters = {"status": AlertStatus.ACTIVE}
            if severity:
                filters["severity"] = severity
            result = await self.list_alerts(filters=filters)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get active alerts: {e}")
            raise  # Re-raise for service layer to handle

        """Update alert status (abstract method implementation)."""
        try:
            result = await self.update_alert(alert_id, {"status": status})
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update alert status: {e}")
            raise  # Re-raise for service layer to handle

        """Execute function with retry logic."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                self.logger.error(f"All {self.max_retries + 1} attempts failed")
        
                raise  # Re-raise for service layer to handle

