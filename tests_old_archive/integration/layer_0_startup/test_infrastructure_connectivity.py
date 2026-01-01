#!/usr/bin/env python3
"""
Layer 0: Infrastructure Connectivity Tests

Tests that verify infrastructure services are actually reachable (not just that containers exist).
These tests use environment variables with defaults to support hybrid cloud deployment (Option C).

CRITICAL: These tests FAIL (not skip) when infrastructure is unavailable, providing detailed diagnostics.
"""

import pytest
import asyncio
import os
from typing import Tuple
from tests.utils.safe_docker import check_container_status, format_container_status

pytestmark = [pytest.mark.integration, pytest.mark.critical_infrastructure]


async def check_service_reachable(host: str, port: int, timeout: float = 5.0) -> Tuple[bool, str]:
    """
    Check if service is reachable with timeout.
    
    Args:
        host: Service hostname
        port: Service port
        timeout: Connection timeout in seconds
    
    Returns:
        (success, error_message)
    """
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True, ""
    except asyncio.TimeoutError:
        return False, f"Connection timeout after {timeout} seconds"
    except Exception as e:
        return False, str(e)


class TestInfrastructureConnectivity:
    """Test that infrastructure services are actually reachable."""
    
    @pytest.mark.asyncio
    async def test_consul_is_reachable_with_timeout(self):
        """Verify Consul is reachable with 5-second timeout."""
        consul_host = os.getenv("CONSUL_HOST", "localhost")
        consul_port = int(os.getenv("CONSUL_PORT", "8500"))
        
        success, error = await check_service_reachable(consul_host, consul_port, timeout=5.0)
        
        if not success:
            container_status = check_container_status("symphainy-consul")
            pytest.fail(
                f"Consul is not reachable at {consul_host}:{consul_port}\n"
                f"Error: {error}\n\n"
                f"Container status: {format_container_status(container_status)}\n\n"
                f"Check: docker logs symphainy-consul\n"
                f"Check: docker ps --filter name=symphainy-consul\n"
                f"Verify: CONSUL_HOST={consul_host} CONSUL_PORT={consul_port} match your infrastructure"
            )
    
    @pytest.mark.asyncio
    async def test_arangodb_is_reachable_with_timeout(self):
        """Verify ArangoDB is reachable with 5-second timeout."""
        arango_host = os.getenv("ARANGO_HOST", "localhost")
        arango_port = int(os.getenv("ARANGO_PORT", "8529"))
        
        success, error = await check_service_reachable(arango_host, arango_port, timeout=5.0)
        
        if not success:
            container_status = check_container_status("symphainy-arangodb")
            pytest.fail(
                f"ArangoDB is not reachable at {arango_host}:{arango_port}\n"
                f"Error: {error}\n\n"
                f"Container status: {format_container_status(container_status)}\n\n"
                f"Check: docker logs symphainy-arangodb\n"
                f"Check: docker ps --filter name=symphainy-arangodb\n"
                f"Verify: ARANGO_HOST={arango_host} ARANGO_PORT={arango_port} match your infrastructure"
            )
    
    @pytest.mark.asyncio
    async def test_redis_is_reachable_with_timeout(self):
        """Verify Redis is reachable with 5-second timeout."""
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        
        success, error = await check_service_reachable(redis_host, redis_port, timeout=5.0)
        
        if not success:
            container_status = check_container_status("symphainy-redis")
            pytest.fail(
                f"Redis is not reachable at {redis_host}:{redis_port}\n"
                f"Error: {error}\n\n"
                f"Container status: {format_container_status(container_status)}\n\n"
                f"Check: docker logs symphainy-redis\n"
                f"Check: docker ps --filter name=symphainy-redis\n"
                f"Verify: REDIS_HOST={redis_host} REDIS_PORT={redis_port} match your infrastructure"
            )
    
    @pytest.mark.asyncio
    async def test_meilisearch_is_reachable_with_timeout(self):
        """Verify Meilisearch is reachable with 5-second timeout."""
        meili_host = os.getenv("MEILI_HOST", "localhost")
        meili_port = int(os.getenv("MEILI_PORT", "7700"))
        
        success, error = await check_service_reachable(meili_host, meili_port, timeout=5.0)
        
        if not success:
            container_status = check_container_status("symphainy-meilisearch")
            pytest.fail(
                f"Meilisearch is not reachable at {meili_host}:{meili_port}\n"
                f"Error: {error}\n\n"
                f"Container status: {format_container_status(container_status)}\n\n"
                f"Check: docker logs symphainy-meilisearch\n"
                f"Check: docker ps --filter name=symphainy-meilisearch\n"
                f"Verify: MEILI_HOST={meili_host} MEILI_PORT={meili_port} match your infrastructure"
            )
    
    @pytest.mark.asyncio
    async def test_all_critical_services_reachable(self):
        """Verify all critical infrastructure services are reachable."""
        services = [
            {
                "name": "Consul",
                "host_env": "CONSUL_HOST",
                "port_env": "CONSUL_PORT",
                "default_host": "localhost",
                "default_port": 8500,
                "container": "symphainy-consul"
            },
            {
                "name": "ArangoDB",
                "host_env": "ARANGO_HOST",
                "port_env": "ARANGO_PORT",
                "default_host": "localhost",
                "default_port": 8529,
                "container": "symphainy-arangodb"
            },
            {
                "name": "Redis",
                "host_env": "REDIS_HOST",
                "port_env": "REDIS_PORT",
                "default_host": "localhost",
                "default_port": 6379,
                "container": "symphainy-redis"
            },
            {
                "name": "Meilisearch",
                "host_env": "MEILI_HOST",
                "port_env": "MEILI_PORT",
                "default_host": "localhost",
                "default_port": 7700,
                "container": "symphainy-meilisearch"
            }
        ]
        
        failures = []
        
        for service in services:
            host = os.getenv(service["host_env"], service["default_host"])
            port = int(os.getenv(service["port_env"], str(service["default_port"])))
            
            success, error = await check_service_reachable(host, port, timeout=5.0)
            
            if not success:
                container_status = check_container_status(service["container"])
                failures.append({
                    "service": service["name"],
                    "host": host,
                    "port": port,
                    "error": error,
                    "container_status": container_status
                })
        
        if failures:
            error_msg = "Critical infrastructure services are not reachable:\n\n"
            for failure in failures:
                error_msg += (
                    f"❌ {failure['service']} ({failure['host']}:{failure['port']})\n"
                    f"   Error: {failure['error']}\n"
                    f"   Container: {format_container_status(failure['container_status'])}\n\n"
                )
            error_msg += (
                "Check Docker containers: docker ps --filter name=symphainy-\n"
                "Check logs: docker logs <container_name>\n"
                "Verify environment variables match your infrastructure configuration"
            )
            pytest.fail(error_msg)

