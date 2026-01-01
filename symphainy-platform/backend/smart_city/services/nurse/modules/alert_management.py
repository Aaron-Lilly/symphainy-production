#!/usr/bin/env python3
"""
Nurse Service - Alert Management Module

Micro-module for alert threshold management using Alert Management Abstraction (Redis).
"""

from typing import Any, Dict

from foundations.public_works_foundation.abstraction_contracts.alerting_protocol import AlertRule, AlertSeverity


class AlertManagement:
    """Alert management module for Nurse service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def set_alert_threshold(self, service_name: str, metric_name: str, threshold: float) -> bool:
        """Set alert threshold using Alert Management Abstraction (Redis)."""
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Create alert rule for threshold
            alert_rule = AlertRule(
                name=f"{service_name}_{metric_name}_threshold",
                condition=f"{metric_name} > {threshold}",
                severity=AlertSeverity.MEDIUM,
                enabled=True,
                metadata={
                    "service_name": service_name,
                    "metric_name": metric_name,
                    "threshold": threshold
                }
            )
            
            rule_id = await self.service.alert_management_abstraction.create_alert_rule(alert_rule)
            success = rule_id is not None
            
            if success:
                # Update local thresholds (backward compatibility)
                if service_name not in self.service.alert_thresholds:
                    self.service.alert_thresholds[service_name] = {}
                
                self.service.alert_thresholds[service_name][metric_name] = threshold
                
                if self.service.logger:
                    self.service.logger.info(f"✅ Alert threshold set: {service_name}/{metric_name} = {threshold}")
                return True
            else:
                if self.service.logger:
                    self.service.logger.warning(f"⚠️ Failed to set alert threshold: {service_name}/{metric_name}")
                return False
                
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Error setting alert threshold: {str(e)}")
            return False






