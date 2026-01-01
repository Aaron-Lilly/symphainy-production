#!/usr/bin/env python3
"""
Core 4 Utility Integration Pattern

This provides a custom utility integration pattern for Core 4 servers
(File Broker, Database Broker, Metadata Server, Context Broker) that are
deliberately abstracted and isolated from the main Smart City infrastructure.

Core 4 servers need utilities but in a different way than Smart City servers.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Import utilities (but don't require service_name for Core 4)
import sys
import os

# Using absolute imports from project root

from common.utilities.error import get_error_handler
from common.utilities.health import get_health_service, ServiceStatus
from common.utilities.logging.logging_service import get_logging_service
from common.utilities.telemetry import get_telemetry_service

class Core4UtilityIntegration:
    """
    Custom utility integration for Core 4 servers.
    
    Core 4 servers are deliberately abstracted/isolated, so they need
    a different utility integration pattern than Smart City servers.
    """
    
    def __init__(self, server_name: str):
        """
        Initialize Core 4 utility integration.
        
        Args:
            server_name: Name of the Core 4 server
        """
        self.server_name = server_name
        
        # Initialize utilities with minimal configuration
        # Core 4 servers don't need full service_name context
        self.logger = get_logging_service(f"core4_{server_name}")
        self.error_handler = get_error_handler(f"core4_{server_name}")
        self.health_service = get_health_service(f"core4_{server_name}")
        self.telemetry_service = get_telemetry_service(f"core4_{server_name}")
        
        # Core 4 specific state
        self.status = ServiceStatus.INITIALIZING
        self.start_time = datetime.utcnow()
        self.health_score = 1.0
        
        self.logger.info(f"Core 4 utility integration initialized for {server_name}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for Core 4 server."""
        try:
            health_data = {
                "server_name": self.server_name,
                "status": self.status.value,
                "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
                "health_score": self.health_score,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Log health check
            await self.telemetry_service.log_telemetry_data({
                "event": "core4_health_check",
                "server_name": self.server_name,
                "health_data": health_data
            })
            
            return health_data
            
        except Exception as e:
            self.logger.error(f"Health check failed for {self.server_name}: {e}")
            await self.error_handler.handle_error(e)
            return {
                "server_name": self.server_name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def log_operation(self, operation: str, details: Dict[str, Any] = None):
        """Log an operation for Core 4 server."""
        try:
            log_data = {
                "server_name": self.server_name,
                "operation": operation,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Core 4 operation: {operation}")
            
            # Log to telemetry
            await self.telemetry_service.log_telemetry_data({
                "event": "core4_operation",
                "server_name": self.server_name,
                "operation": operation,
                "details": details
            })
            
        except Exception as e:
            self.logger.error(f"Failed to log operation {operation}: {e}")
            await self.error_handler.handle_error(e)
    
    async def handle_error(self, error: Exception, context: str = ""):
        """Handle errors for Core 4 server."""
        try:
            error_data = {
                "server_name": self.server_name,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.error(f"Core 4 error in {context}: {error}")
            
            # Use error handler
            await self.error_handler.handle_error(error)
            
            # Log to telemetry
            await self.telemetry_service.log_telemetry_data({
                "event": "core4_error",
                "server_name": self.server_name,
                "error_data": error_data
            })
            
        except Exception as e:
            # Fallback logging if error handling fails
            self.logger.critical(f"Critical error in Core 4 error handling: {e}")
    
    def set_status(self, status: ServiceStatus):
        """Set the status of the Core 4 server."""
        self.status = status
        self.logger.info(f"Core 4 server {self.server_name} status: {status.value}")
    
    def update_health_score(self, score: float):
        """Update the health score of the Core 4 server."""
        self.health_score = max(0.0, min(1.0, score))
        self.logger.debug(f"Core 4 server {self.server_name} health score: {self.health_score}")

def create_core4_utility_integration(server_name: str) -> Core4UtilityIntegration:
    """
    Factory function to create Core 4 utility integration.
    
    Args:
        server_name: Name of the Core 4 server
        
    Returns:
        Core4UtilityIntegration instance
    """
    return Core4UtilityIntegration(server_name)
