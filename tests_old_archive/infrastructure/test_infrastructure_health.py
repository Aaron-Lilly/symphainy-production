#!/usr/bin/env python3
"""
Infrastructure Health Check Tests

Tests that production infrastructure is healthy and accessible.
Catches infrastructure issues before deployment.

Run: pytest tests/infrastructure/test_infrastructure_health.py -v
"""

import pytest
import asyncio
import httpx
import subprocess
from typing import List, Dict, Optional
import json


def check_container_health(container_name: str) -> bool:
    """
    Check if a Docker container is healthy.
    
    Args:
        container_name: Name of the container to check
        
    Returns:
        True if container is running and healthy, False otherwise
    """
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", container_name],
            capture_output=True,
            text=True,
            timeout=5.0
        )
        
        if result.returncode != 0:
            return False
        
        status = result.stdout.strip()
        return status == "running"
    except Exception as e:
        print(f"⚠️ Error checking container {container_name}: {e}")
        return False


def get_container_health_status(container_name: str) -> Optional[str]:
    """
    Get the health status of a Docker container.
    
    Returns:
        "healthy", "unhealthy", "starting", or None if no health check
    """
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_name],
            capture_output=True,
            text=True,
            timeout=5.0
        )
        
        if result.returncode != 0:
            return None
        
        status = result.stdout.strip()
        return status if status else None
    except Exception:
        return None


@pytest.mark.e2e
@pytest.mark.infrastructure
@pytest.mark.production_readiness
class TestInfrastructureHealth:
    """Tests for infrastructure health and accessibility."""
    
    @pytest.mark.asyncio
    async def test_core_containers_running(self):
        """Test that core infrastructure containers are running."""
        # Core services required for platform operation
        core_containers = [
            "symphainy-consul",      # Service discovery
            "symphainy-arangodb",    # Metadata storage
            "symphainy-redis",       # Cache and sessions
        ]
        
        failed = []
        for container in core_containers:
            try:
                is_running = await asyncio.to_thread(check_container_health, container)
                if not is_running:
                    failed.append(f"{container} (not running)")
                else:
                    health_status = await asyncio.to_thread(get_container_health_status, container)
                    if health_status:
                        print(f"✅ {container} is running (health: {health_status})")
                    else:
                        print(f"✅ {container} is running (no health check)")
            except Exception as e:
                failed.append(f"{container} (error: {e})")
        
        assert not failed, \
            f"❌ Core containers not running: {failed}\n" \
            f"   These containers are required for the platform to function"
    
    @pytest.mark.asyncio
    async def test_consul_accessible(self):
        """Test that Consul service discovery is accessible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                    # Test Consul leader endpoint
                    response = await client.get("http://localhost:8500/v1/status/leader")
                    assert response.status_code == 200, \
                        f"Consul leader endpoint returned {response.status_code}"
                    
                    # Test Consul health endpoint
                    response = await client.get("http://localhost:8500/v1/health/node/consul")
                    assert response.status_code in [200, 404], \
                        f"Consul health endpoint returned {response.status_code}"
                    
                    print(f"✅ Consul is accessible on port 8500")
        except (asyncio.TimeoutError, httpx.TimeoutException):
            pytest.fail("❌ Consul health check timed out (service not accessible)")
        except httpx.ConnectError:
            pytest.fail("❌ Consul not accessible on port 8500 (connection refused)")
        except Exception as e:
            pytest.fail(f"❌ Consul health check failed: {e}")
    
    @pytest.mark.asyncio
    async def test_redis_accessible(self):
        """Test that Redis is accessible."""
        try:
            import redis.asyncio as redis
            # Connect to Redis with timeout
            r = redis.Redis(
                host='localhost', 
                port=6379, 
                db=0, 
                decode_responses=True,
                socket_connect_timeout=5.0
            )
            try:
                # Test connection with PING
                pong = await r.ping()
                assert pong, "Redis PING failed"
                
                # Test basic operation
                await r.set("test_key", "test_value", ex=1)
                value = await r.get("test_key")
                assert value == "test_value", "Redis GET failed"
                await r.delete("test_key")
                
                print(f"✅ Redis is accessible on port 6379")
            finally:
                await r.close()
        except (asyncio.TimeoutError, redis.exceptions.TimeoutError, redis.exceptions.ConnectionError):
            pytest.fail("❌ Redis health check timed out or connection failed (service not accessible)")
        except Exception as e:
            pytest.fail(f"❌ Redis not accessible on port 6379: {e}")
    
    @pytest.mark.asyncio
    async def test_arangodb_accessible(self):
        """Test that ArangoDB is accessible."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                    # Test ArangoDB version endpoint
                    response = await client.get("http://localhost:8529/_api/version")
                    assert response.status_code == 200, \
                        f"ArangoDB version endpoint returned {response.status_code}"
                    
                    # Verify response is JSON
                    data = response.json()
                    assert "version" in data or "server" in data, \
                        "ArangoDB response missing version information"
                    
                    print(f"✅ ArangoDB is accessible on port 8529")
        except (asyncio.TimeoutError, httpx.TimeoutException):
            pytest.fail("❌ ArangoDB health check timed out (service not accessible)")
        except httpx.ConnectError:
            pytest.fail("❌ ArangoDB not accessible on port 8529 (connection refused)")
        except Exception as e:
            pytest.fail(f"❌ ArangoDB health check failed: {e}")
    
    @pytest.mark.asyncio
    async def test_backend_container_healthy(self):
        """Test that backend container is running and healthy."""
        # Check for test container first, then production container
        container_name = "symphainy-backend-test"
        if not await asyncio.to_thread(check_container_health, container_name):
            container_name = "symphainy-backend-prod"  # Fallback to prod container
        
        try:
            is_running = await asyncio.to_thread(check_container_health, container_name)
            assert is_running, f"Backend container {container_name} is not running"
            
            health_status = await asyncio.to_thread(get_container_health_status, container_name)
            if health_status:
                # Prefer healthy, but starting is acceptable (might be initializing)
                assert health_status in ["healthy", "starting"], \
                    f"Backend container health status: {health_status}"
                print(f"✅ Backend container is running (health: {health_status})")
            else:
                print(f"✅ Backend container is running (no health check)")
        except Exception as e:
            pytest.fail(f"❌ Backend container check failed: {e}")
    
    @pytest.mark.asyncio
    async def test_backend_health_endpoint(self):
        """Test that backend health endpoint is accessible."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get("http://localhost:8000/health")
                    assert response.status_code == 200, \
                        f"Backend health endpoint returned {response.status_code}"
                    
                    # Verify response structure (health endpoint returns detailed status)
                    data = response.json()
                    # Check for any health-related fields (flexible structure)
                    has_health_info = (
                        "status" in data or 
                        "health" in data or 
                        "ok" in data or
                        "health_validation" in data or
                        "foundation_services" in data or
                        "infrastructure_services" in data
                    )
                    assert has_health_info, \
                        "Backend health response missing status information"
                    
                    print(f"✅ Backend health endpoint is accessible")
        except (asyncio.TimeoutError, httpx.TimeoutException):
            pytest.fail("❌ Backend health check timed out")
        except httpx.ConnectError:
            pytest.fail("❌ Backend not accessible on port 8000 (connection refused)")
        except Exception as e:
            pytest.fail(f"❌ Backend health check failed: {e}")
    
    @pytest.mark.asyncio
    async def test_observability_services_running(self):
        """Test that observability services are running (optional but recommended)."""
        # Observability services (nice to have, but not critical for basic operation)
        observability_containers = [
            "symphainy-tempo",           # Distributed tracing
            "symphainy-otel-collector", # Telemetry collection
        ]
        
        failed = []
        for container in observability_containers:
            try:
                is_running = await asyncio.to_thread(check_container_health, container)
                if not is_running:
                    failed.append(container)
                else:
                    health_status = await asyncio.to_thread(get_container_health_status, container)
                    if health_status:
                        print(f"✅ {container} is running (health: {health_status})")
                    else:
                        print(f"✅ {container} is running (no health check)")
            except Exception as e:
                failed.append(f"{container} (error: {e})")
        
        if failed:
            print(f"⚠️ Some observability services not running: {failed}")
            print(f"   (These are optional but recommended for production)")
        else:
            print(f"✅ All observability services are running")
    
    @pytest.mark.asyncio
    async def test_optional_services_status(self):
        """Test status of optional services (informational)."""
        # Optional services that enhance functionality
        optional_containers = {
            "symphainy-meilisearch": "Search engine",
            "symphainy-opa": "Policy engine",
            "symphainy-grafana": "Visualization",
            "symphainy-celery-worker": "Background tasks",
            "symphainy-celery-beat": "Task scheduler",
        }
        
        status_report = []
        for container, purpose in optional_containers.items():
            try:
                is_running = await asyncio.to_thread(check_container_health, container)
                if is_running:
                    health_status = await asyncio.to_thread(get_container_health_status, container)
                    status = health_status if health_status else "running"
                    status_report.append(f"✅ {container} ({purpose}): {status}")
                else:
                    status_report.append(f"⚠️ {container} ({purpose}): not running")
            except Exception:
                status_report.append(f"❓ {container} ({purpose}): unknown")
        
        # Print status report (informational, don't fail)
        print("\n📊 Optional Services Status:")
        for status in status_report:
            print(f"   {status}")

