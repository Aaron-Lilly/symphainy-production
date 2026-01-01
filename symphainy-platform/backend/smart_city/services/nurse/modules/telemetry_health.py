#!/usr/bin/env python3
"""
Nurse Service - Telemetry & Health Module

Micro-module for telemetry collection and health metrics using OpenTelemetry + Tempo + Health abstractions.
"""

import uuid
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.health_protocol import HealthType, HealthContext, HealthMetric
from foundations.public_works_foundation.abstraction_contracts.telemetry_protocol import TelemetryData, TelemetryType


class TelemetryHealth:
    """Telemetry and health monitoring module for Nurse service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def collect_telemetry(self, service_name: str, metric_name: str, metric_value: float, tags: Optional[Dict[str, Any]] = None) -> str:
        """
        Collect telemetry data using OpenTelemetry infrastructure.
        
        BOOTSTRAP PATTERN: This method PROVIDES telemetry, so we use direct telemetry abstraction access
        instead of log_operation_with_telemetry() to avoid circular dependency.
        """
        # Bootstrap Pattern: Direct telemetry abstraction access (Nurse PROVIDES telemetry)
        # ❌ DON'T USE: await self.service.log_operation_with_telemetry(...)
        # ✅ USE: Direct telemetry abstraction access for self-reporting
        telemetry_abstraction = self.service.get_telemetry_abstraction()
        
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            metric_id = str(uuid.uuid4())
            
            # Collect telemetry via OpenTelemetry using TelemetryData
            unit = "percent" if "usage" in metric_name else "count"
            telemetry_data = TelemetryData(
                name=metric_name,
                value=metric_value,
                type=TelemetryType.METRIC,
                timestamp=datetime.utcnow(),
                labels=tags or {},
                metadata={
                    "service_id": service_name,
                    "metric_id": metric_id,
                    "unit": unit  # Store unit in metadata
                }
            )
            
            success = await self.service.telemetry_abstraction.collect_metric(telemetry_data)
            
            if success:
                # Update local health metrics (backward compatibility)
                if service_name not in self.service.health_metrics:
                    self.service.health_metrics[service_name] = {}
                
                self.service.health_metrics[service_name][metric_name] = {
                    "value": metric_value,
                    "last_updated": datetime.utcnow().isoformat()
                }
                
                # Store health metrics using proper health abstraction
                health_context = HealthContext(
                    service_id=service_name,
                    metadata=tags or {}
                )
                
                health_metric = HealthMetric(
                    name=metric_name,
                    value=metric_value,
                    unit="percent" if "usage" in metric_name else "count",
                    timestamp=datetime.utcnow(),
                    labels=tags or {},
                    metadata={"service_id": service_name}
                )
                
                await self.service.health_abstraction.collect_metrics(
                    health_type=HealthType.SYSTEM,
                    context=health_context
                )
                
                # ✅ CAN USE: Health metrics utility (Nurse doesn't provide health metrics)
                await self.service.record_health_metric(
                    "telemetry_collected",
                    1.0,
                    {"service_name": service_name, "metric_name": metric_name}
                )
                
                # Bootstrap Pattern: Self-report using direct telemetry abstraction (if available)
                if telemetry_abstraction:
                    try:
                        # Record operation start/complete using direct abstraction
                        operation_telemetry = TelemetryData(
                            name="nurse_collect_telemetry",
                            value=1.0,
                            type=TelemetryType.METRIC,
                            timestamp=datetime.utcnow(),
                            labels={
                                "operation": "collect_telemetry",
                                "service_name": service_name,
                                "metric_name": metric_name,
                                "status": "success"
                            },
                            metadata={"metric_id": metric_id}
                        )
                        await telemetry_abstraction.collect_metric(operation_telemetry)
                    except Exception:
                        # Telemetry self-reporting is optional - don't fail if it doesn't work
                        pass
                
                return metric_id
            else:
                raise Exception("Failed to collect telemetry via OpenTelemetry")
                
        except Exception as e:
            # ✅ CAN USE: Error handling utility (Nurse doesn't provide error handling)
            await self.service.handle_error_with_audit(e, "collect_telemetry")
            
            # Bootstrap Pattern: Self-report failure using direct telemetry abstraction (if available)
            if telemetry_abstraction:
                try:
                    failure_telemetry = TelemetryData(
                        name="nurse_collect_telemetry",
                        value=0.0,
                        type=TelemetryType.METRIC,
                        timestamp=datetime.utcnow(),
                        labels={
                            "operation": "collect_telemetry",
                            "service_name": service_name,
                            "metric_name": metric_name,
                            "status": "error"
                        },
                        metadata={"error": str(e)}
                    )
                    await telemetry_abstraction.collect_metric(failure_telemetry)
                except Exception:
                    # Telemetry self-reporting is optional
                    pass
            
            raise
    
    async def get_health_metrics(self, service_name: str) -> Dict[str, Any]:
        """
        Get health metrics using Health Abstraction (OpenTelemetry + Simple Health).
        
        NORMAL PATTERN: This method USES health metrics (doesn't provide them), so we can use utilities normally.
        """
        # Start telemetry tracking (Nurse can use telemetry utilities for non-telemetry operations)
        await self.service.log_operation_with_telemetry(
            "get_health_metrics_start",
            success=True,
            details={"service_name": service_name}
        )
        
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get metrics from Health Abstraction
            metrics = await self.service.health_abstraction.get_health_metrics(service_name)
            
            if metrics:
                # Record health metric
                await self.service.record_health_metric(
                    "health_metrics_retrieved",
                    1.0,
                    {"service_name": service_name, "metric_count": len(metrics) if isinstance(metrics, dict) else 0}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_health_metrics_complete",
                    success=True,
                    details={"service_name": service_name, "metric_count": len(metrics) if isinstance(metrics, dict) else 0}
                )
                
                return {
                    "service_name": service_name,
                    "metrics": metrics,
                    "retrieved_at": datetime.utcnow().isoformat(),
                    "status": "success"
                }
            else:
                # Record health metric (no data)
                await self.service.record_health_metric(
                    "health_metrics_no_data",
                    1.0,
                    {"service_name": service_name}
                )
                
                # End telemetry tracking
                await self.service.log_operation_with_telemetry(
                    "get_health_metrics_complete",
                    success=True,
                    details={"service_name": service_name, "status": "no_data"}
                )
                
                return {
                    "service_name": service_name,
                    "metrics": {},
                    "retrieved_at": datetime.utcnow().isoformat(),
                    "status": "no_data"
                }
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.service.handle_error_with_audit(e, "get_health_metrics")
            
            # End telemetry tracking with failure
            await self.service.log_operation_with_telemetry(
                "get_health_metrics_complete",
                success=False,
                details={"service_name": service_name, "error": str(e)}
            )
            
            return {
                "service_name": service_name,
                "metrics": {},
                "error": str(e),
                "status": "error"
            }
    
    async def monitor_connection_pools(self) -> Dict[str, Any]:
        """
        Monitor connection pools for all infrastructure services.
        
        Collects metrics for:
        - ArangoDB connection pool
        - Redis connection pool
        - Database connection pools (if applicable)
        
        Uses existing telemetry infrastructure to collect and store metrics.
        """
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            pool_metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "pools": {},
                "overall_status": "healthy"
            }
            
            # Get platform gateway to access abstractions
            platform_gateway = None
            if hasattr(self.service, 'di_container'):
                platform_gateway = self.service.di_container.service_registry.get("PlatformInfrastructureGateway")
            
            if not platform_gateway:
                self.logger.warning("⚠️ Platform Gateway not available for connection pool monitoring")
                return {
                    "status": "error",
                    "error": "Platform Gateway not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Monitor ArangoDB connection pool
            try:
                arango_abstraction = platform_gateway.get_abstraction("database") or platform_gateway.get_abstraction("metadata")
                if arango_abstraction:
                    # Get ArangoDB adapter if available
                    if hasattr(arango_abstraction, 'adapter') and hasattr(arango_abstraction.adapter, '_is_connected'):
                        arango_connected = arango_abstraction.adapter._is_connected
                        arango_status = "connected" if arango_connected else "disconnected"
                        
                        # Collect connection pool metrics
                        await self.collect_telemetry(
                            "arangodb",
                            "connection_pool_status",
                            1.0 if arango_connected else 0.0,
                            {"status": arango_status, "pool_type": "arangodb"}
                        )
                        
                        pool_metrics["pools"]["arangodb"] = {
                            "status": arango_status,
                            "connected": arango_connected,
                            "monitored_at": datetime.utcnow().isoformat()
                        }
                        
                        if not arango_connected:
                            pool_metrics["overall_status"] = "degraded"
                            self.logger.warning("⚠️ ArangoDB connection pool: disconnected")
            except Exception as e:
                self.logger.error(f"❌ Failed to monitor ArangoDB connection pool: {e}")
                pool_metrics["pools"]["arangodb"] = {
                    "status": "error",
                    "error": str(e)
                }
                pool_metrics["overall_status"] = "degraded"
            
            # Monitor Redis connection pool
            try:
                redis_abstraction = platform_gateway.get_abstraction("cache") or platform_gateway.get_abstraction("session_management")
                if redis_abstraction:
                    # Test Redis connection
                    if hasattr(redis_abstraction, 'adapter') and hasattr(redis_abstraction.adapter, '_client'):
                        try:
                            # Simple ping test to check connection
                            redis_client = redis_abstraction.adapter._client
                            # Use asyncio to run synchronous ping in executor
                            loop = asyncio.get_event_loop()
                            await loop.run_in_executor(None, redis_client.ping)
                            redis_connected = True
                            redis_status = "connected"
                        except Exception:
                            redis_connected = False
                            redis_status = "disconnected"
                        
                        # Collect connection pool metrics
                        await self.collect_telemetry(
                            "redis",
                            "connection_pool_status",
                            1.0 if redis_connected else 0.0,
                            {"status": redis_status, "pool_type": "redis"}
                        )
                        
                        pool_metrics["pools"]["redis"] = {
                            "status": redis_status,
                            "connected": redis_connected,
                            "monitored_at": datetime.utcnow().isoformat()
                        }
                        
                        if not redis_connected:
                            pool_metrics["overall_status"] = "degraded"
                            self.logger.warning("⚠️ Redis connection pool: disconnected")
            except Exception as e:
                self.logger.error(f"❌ Failed to monitor Redis connection pool: {e}")
                pool_metrics["pools"]["redis"] = {
                    "status": "error",
                    "error": str(e)
                }
                pool_metrics["overall_status"] = "degraded"
            
            # Record overall pool health metric
            overall_health_value = 1.0 if pool_metrics["overall_status"] == "healthy" else 0.5 if pool_metrics["overall_status"] == "degraded" else 0.0
            await self.collect_telemetry(
                "connection_pools",
                "overall_health",
                overall_health_value,
                {
                    "status": pool_metrics["overall_status"],
                    "pools_monitored": len(pool_metrics["pools"])
                }
            )
            
            return {
                "status": "success",
                "metrics": pool_metrics,
                "monitored_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            await self.service.handle_error_with_audit(e, "monitor_connection_pools")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def monitor_log_aggregation(self) -> Dict[str, Any]:
        """
        Monitor log aggregation health and metrics.
        
        Collects metrics for:
        - Log volume
        - Log aggregation status
        - Query performance
        
        Uses existing telemetry infrastructure to collect and store metrics.
        """
        try:
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get platform gateway to access abstractions
            platform_gateway = None
            if hasattr(self.service, 'di_container'):
                platform_gateway = self.service.di_container.service_registry.get("PlatformInfrastructureGateway")
            
            if not platform_gateway:
                self.logger.warning("⚠️ Platform Gateway not available for log aggregation monitoring")
                return {
                    "status": "error",
                    "error": "Platform Gateway not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Get log aggregation abstraction
            log_abstraction = platform_gateway.get_abstraction("log_aggregation")
            if not log_abstraction:
                return {
                    "status": "error",
                    "error": "Log aggregation abstraction not available",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Get log metrics (last hour)
            from datetime import timedelta
            time_range = {"hours": 1}
            metrics = await log_abstraction.get_log_metrics(time_range)
            
            if metrics.get("status") == "success":
                # Collect telemetry
                await self.collect_telemetry(
                    "log_aggregation",
                    "log_volume",
                    float(metrics.get("volume", 0)),
                    {"status": "healthy", "time_range_hours": 1}
                )
                
                # Collect metrics by service
                for service, count in metrics.get("by_service", {}).items():
                    await self.collect_telemetry(
                        "log_aggregation",
                        "log_volume_by_service",
                        float(count),
                        {"service": service, "time_range_hours": 1}
                    )
                
                self.logger.info(f"✅ Log aggregation monitoring: {metrics.get('volume', 0)} logs in last hour")
                return {
                    "status": "success",
                    "metrics": metrics,
                    "monitored_at": datetime.utcnow().isoformat()
                }
            else:
                self.logger.warning(f"⚠️ Log aggregation monitoring issue: {metrics.get('error')}")
                return {
                    "status": "error",
                    "error": metrics.get("error"),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error monitoring log aggregation: {e}", exc_info=True)
            await self.collect_telemetry(
                "log_aggregation",
                "monitoring_error",
                1.0,
                {"error": str(e)}
            )
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

