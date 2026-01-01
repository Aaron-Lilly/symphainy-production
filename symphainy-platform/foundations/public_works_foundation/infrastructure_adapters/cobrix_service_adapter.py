#!/usr/bin/env python3
"""
Cobrix Service Adapter - Layer 4 (Infrastructure Adapter)

Calls containerized Cobrix service for COBOL/mainframe file parsing.
Replaces MainframeProcessingAdapter with industry-standard Cobrix implementation.

WHAT (Infrastructure): I provide COBOL processing capabilities via Cobrix service
HOW (Adapter): I call containerized Cobrix service via docker exec (MVP) or HTTP (Phase 2)
"""

import logging
import asyncio
import subprocess
import json
import os
import tempfile
import io
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import httpx
    HTTP_CLIENT_AVAILABLE = True
    HTTP_CLIENT_TYPE = "httpx"
except ImportError:
    try:
        import aiohttp
        HTTP_CLIENT_AVAILABLE = True
        HTTP_CLIENT_TYPE = "aiohttp"
    except ImportError:
        HTTP_CLIENT_AVAILABLE = False
        HTTP_CLIENT_TYPE = None

logger = logging.getLogger(__name__)

class CobrixServiceAdapter:
    """
    Cobrix Service Adapter - Calls containerized Cobrix service.
    
    Replaces MainframeProcessingAdapter with industry-standard Cobrix.
    Uses docker exec for MVP (Phase 1), can be upgraded to HTTP API (Phase 2).
    """
    
    def __init__(self, service_discovery_abstraction=None, di_container=None, cobrix_container_name: str = "symphainy-cobrix-parser"):
        """
        Initialize Cobrix Service Adapter.
        
        Args:
            service_discovery_abstraction: Service discovery abstraction (for future HTTP API)
            di_container: Dependency injection container
            cobrix_container_name: Docker container name for Cobrix service
        """
        self.service_discovery = service_discovery_abstraction
        self.di_container = di_container
        self.cobrix_container_name = cobrix_container_name
        
        # Get logger from DI Container if available
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger("cobrix_service_adapter")
        else:
            self.logger = logging.getLogger("CobrixServiceAdapter")
        
        self.cobrix_service_url = None  # For future HTTP API (Phase 2)
        self.logger.info(f"✅ Cobrix Service Adapter initialized (container: {cobrix_container_name})")
    
    async def _discover_cobrix_service(self) -> bool:
        """
        Discover Cobrix service via service discovery (for Phase 2 HTTP API).
        
        Returns:
            bool: True if service discovered
        """
        if not self.service_discovery:
            return False
        
        try:
            services = await self.service_discovery.discover_service("cobrix-parser")
            if services and len(services) > 0:
                service = services[0]
                self.cobrix_service_url = f"http://{service.address}:{service.port}"
                self.logger.info(f"✅ Discovered Cobrix service at {self.cobrix_service_url}")
                return True
        except Exception as e:
            self.logger.warning(f"⚠️ Service discovery failed: {e}")
        
        return False
    
    async def _check_container_available(self) -> bool:
        """
        Check if Cobrix container is available via HTTP health check.
        
        Returns:
            bool: True if container is reachable via HTTP
        """
        # Use HTTP health check instead of docker ps (which doesn't work from inside containers)
        cobrix_url = f"http://{self.cobrix_container_name}:8080"
        try:
            if HTTP_CLIENT_TYPE == "httpx":
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{cobrix_url}/health")
                    return response.status_code == 200
            else:
                # Fallback: assume available if we can't check (will fail on actual request if not)
                return True
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to check Cobrix service health: {e}")
            # Don't fail - let the actual parse request handle the error
            return True
    
    async def parse_file(self, file_data: bytes, filename: str, copybook_data: bytes = None) -> Dict[str, Any]:
        """
        Parse mainframe file using Cobrix service via HTTP API.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            copybook_data: Copybook content (bytes)
        
        Returns:
            Dict with parsed records, tables, metadata
        """
        if not copybook_data:
            return {
                "success": False,
                "error": "Copybook data is required for Cobrix parsing",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Get Cobrix service URL (from service discovery or default)
        # Use container name directly (Docker network DNS resolution)
        cobrix_url = self.cobrix_service_url
        if not cobrix_url:
            # Try service discovery first (for future use)
            if self.service_discovery:
                discovered = await self._discover_cobrix_service()
                if discovered:
                    cobrix_url = self.cobrix_service_url
        
        # Fallback to container name (Docker network DNS)
        # Docker Compose creates DNS entries for container names
        if not cobrix_url:
            cobrix_url = f"http://{self.cobrix_container_name}:8080"
        
        self.logger.info(f"🔄 Using Cobrix service at: {cobrix_url}")
        
        # Call HTTP API
        if not HTTP_CLIENT_AVAILABLE:
            return {
                "success": False,
                "error": "HTTP client library (httpx or aiohttp) not available.",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        try:
            self.logger.info(f"🔄 Calling Cobrix HTTP API at {cobrix_url}/parse/cobol for file: {filename}")
            
            # Use httpx if available (preferred), otherwise aiohttp
            if HTTP_CLIENT_TYPE == "httpx":
                async with httpx.AsyncClient(timeout=300.0) as client:
                    files = {
                        'file': (filename or "data.bin", file_data, 'application/octet-stream'),
                        'copybook': ("copybook.cpy", copybook_data, 'text/plain')
                    }
                    response = await client.post(
                        f"{cobrix_url}/parse/cobol",
                        files=files
                    )
                    response.raise_for_status()
                    result = response.json()
            else:  # aiohttp
                data = aiohttp.FormData()
                data.add_field('file', 
                              io.BytesIO(file_data),
                              filename=filename or "data.bin",
                              content_type='application/octet-stream')
                data.add_field('copybook',
                              io.BytesIO(copybook_data),
                              filename="copybook.cpy",
                              content_type='text/plain')
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{cobrix_url}/parse/cobol",
                        data=data,
                        timeout=aiohttp.ClientTimeout(total=300.0)
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            error_msg = f"Cobrix API returned {response.status}: {error_text}"
                            self.logger.error(f"❌ {error_msg}")
                            return {
                                "success": False,
                                "error": error_msg,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        result = await response.json()
            
            # Convert to expected format
            if result.get("success"):
                return {
                    "success": True,
                    "records": result.get("records", []),
                    "tables": result.get("tables", []),
                    "metadata": result.get("metadata", {}),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result.get("detail", "Unknown error"),
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        except (httpx.HTTPError if HTTP_CLIENT_TYPE == "httpx" else aiohttp.ClientError) as e:
            error_msg = f"Failed to connect to Cobrix service at {cobrix_url}: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            error_msg = f"Cobrix parsing failed: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.utcnow().isoformat()
            }

