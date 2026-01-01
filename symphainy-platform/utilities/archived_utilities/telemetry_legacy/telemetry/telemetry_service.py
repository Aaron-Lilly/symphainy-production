"""
Simple Telemetry Service for MCP Servers

This service provides simple telemetry capabilities by calling the Nurse MCP Server's
telemetry tools. No complex dependencies - just simple tool calls.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json

class TelemetryService:
    """Simple telemetry service that calls Nurse MCP Server tools."""

    def __init__(self, service_name: str, nurse_client=None):
        """Initialize telemetry service."""
        self.service_name = service_name
        self.nurse_client = nurse_client

    async def log_telemetry_data(self, telemetry_data: Dict[str, Any], 
                                telemetry_type: str = "general") -> Dict[str, Any]:
        """Log telemetry data by calling Nurse's collect_telemetry_data tool."""
        if not self.nurse_client:
            return {"status": "error", "error": "Nurse client not available"}
        
        try:
            # Prepare telemetry data for Nurse
            nurse_input = {
                "service_name": self.service_name,
                "telemetry_type": telemetry_type,
                "telemetry_data": telemetry_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Call Nurse's collect_telemetry_data tool
            result = await self.nurse_client.call_tool(
                "collect_telemetry_data",
                input_data=json.dumps(nurse_input)
            )
            
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def log_health_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Log health metrics by calling Nurse's monitor_system_health tool."""
        if not self.nurse_client:
            return {"status": "error", "error": "Nurse client not available"}
        
        try:
            # Prepare health data for Nurse
            health_input = {
                "service_name": self.service_name,
                "health_metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Call Nurse's monitor_system_health tool
            result = await self.nurse_client.call_tool(
                "monitor_system_health",
                input_data=json.dumps(health_input)
            )
            
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def log_anomaly(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log anomaly by calling Nurse's detect_anomalies tool."""
        if not self.nurse_client:
            return {"status": "error", "error": "Nurse client not available"}
        
        try:
            # Prepare anomaly data for Nurse
            anomaly_input = {
                "service_name": self.service_name,
                "anomaly_data": anomaly_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Call Nurse's detect_anomalies tool
            result = await self.nurse_client.call_tool(
                "detect_anomalies",
                input_data=json.dumps(anomaly_input)
            )
            
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def set_nurse_client(self, nurse_client):
        """Set the Nurse client for telemetry calls."""
        self.nurse_client = nurse_client
    
    async def record_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a telemetry metric."""
        try:
            metric_data = {
                "metric_name": metric_name,
                "value": value,
                "tags": tags or {},
                "timestamp": datetime.utcnow().isoformat(),
                "service": self.service_name
            }
            
            # Log the metric
            await self.log_telemetry_data(metric_data, "metric")
            
        except Exception as e:
            self.logger.error(f"Failed to record metric {metric_name}: {e}")

# Global telemetry service factory
def get_telemetry_service(service_name: str, nurse_client=None, config=None) -> TelemetryService:
    """Get a telemetry service instance."""
    return TelemetryService(service_name, nurse_client)