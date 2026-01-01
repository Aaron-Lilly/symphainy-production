"""
Test Infrastructure Health Checks

Validates that infrastructure services are accessible and healthy.
This is useful for validating Phase 3 infrastructure dependency handling.
"""

import pytest
import os

import socket
from typing import Dict, Any

# Add symphainy-platform to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../symphainy-platform"))

@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.medium_priority
class TestInfrastructureHealth:
    """Test infrastructure service health."""
    
    def check_port_open(self, host: str, port: int, timeout: float = 2.0) -> bool:
        """Check if a port is open."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    @pytest.mark.asyncio
    async def test_redis_accessible(self):
        """Test that Redis is accessible."""
        is_open = self.check_port_open("localhost", 6379)
        if not is_open:
            pytest.skip("Redis not running on localhost:6379 (start with docker-compose)")
        assert is_open, "Redis should be accessible on localhost:6379"
    
    @pytest.mark.asyncio
    async def test_arangodb_accessible(self):
        """Test that ArangoDB is accessible."""
        is_open = self.check_port_open("localhost", 8529)
        if not is_open:
            pytest.skip("ArangoDB not running on localhost:8529 (start with docker-compose)")
        assert is_open, "ArangoDB should be accessible on localhost:8529"
    
    @pytest.mark.asyncio
    async def test_meilisearch_accessible(self):
        """Test that Meilisearch is accessible."""
        is_open = self.check_port_open("localhost", 7700)
        if not is_open:
            pytest.skip("Meilisearch not running on localhost:7700 (start with docker-compose)")
        assert is_open, "Meilisearch should be accessible on localhost:7700"
    
    @pytest.mark.asyncio
    async def test_consul_accessible(self):
        """Test that Consul is accessible."""
        is_open = self.check_port_open("localhost", 8500)
        if not is_open:
            pytest.skip("Consul not running on localhost:8500 (start with docker-compose)")
        assert is_open, "Consul should be accessible on localhost:8500"
    
    @pytest.mark.asyncio
    async def test_all_critical_services_accessible(self):
        """Test that all critical services are accessible."""
        critical_services = [
            ("Redis", "localhost", 6379),
            ("ArangoDB", "localhost", 8529),
            ("Meilisearch", "localhost", 7700),
            ("Consul", "localhost", 8500),
        ]
        
        unavailable_services = []
        for service_name, host, port in critical_services:
            if not self.check_port_open(host, port):
                unavailable_services.append(f"{service_name} ({host}:{port})")
        
        if unavailable_services:
            pytest.skip(
                f"Some critical services are not accessible: {', '.join(unavailable_services)}. "
                "Start with: docker-compose -f tests/docker-compose.test.yml up -d"
            )
        
        # All services are accessible
        assert len(unavailable_services) == 0,             f"All critical services should be accessible, but {unavailable_services} are not"
