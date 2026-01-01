#!/usr/bin/env python3
"""
Layer 0: Infrastructure Pre-Flight Checks

CRITICAL: These tests run BEFORE all other tests to verify infrastructure is ready.
If these tests fail, all other tests will fail, so we catch infrastructure issues early.

These tests FAIL (not skip) when infrastructure is unavailable, providing detailed diagnostics.
"""

import pytest
import subprocess
import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "symphainy-platform"))

pytestmark = [pytest.mark.integration, pytest.mark.critical_infrastructure]


def run_docker_command(cmd: list, timeout: int = 10) -> Tuple[bool, str, str]:
    """Run Docker command with timeout. Returns (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, "", str(e)


def check_container_status(container_name: str) -> Dict[str, any]:
    """Check Docker container status. Returns dict with status info."""
    success, stdout, stderr = run_docker_command(
        ["docker", "inspect", "--format", "{{.State.Status}}|{{.State.Health.Status}}|{{.RestartCount}}", container_name]
    )
    
    if not success:
        return {
            "exists": False,
            "status": "not_found",
            "health": "unknown",
            "restart_count": 0,
            "error": stderr
        }
    
    parts = stdout.strip().split("|")
    status = parts[0] if len(parts) > 0 else "unknown"
    health = parts[1] if len(parts) > 1 else "unknown"
    restart_count = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
    
    return {
        "exists": True,
        "status": status,
        "health": health,
        "restart_count": restart_count,
        "error": None
    }


async def check_service_reachable(host: str, port: int, timeout: float = 5.0) -> Tuple[bool, str]:
    """Check if service is reachable with timeout. Returns (success, error_message)."""
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


class TestInfrastructurePreflight:
    """Pre-flight checks: Verify infrastructure is ready before running tests."""
    
    @pytest.mark.asyncio
    async def test_docker_containers_are_running(self):
        """Verify all required Docker containers are running."""
        required_containers = [
            "symphainy-redis",
            "symphainy-arangodb",
            "symphainy-consul",
            "symphainy-celery-worker",
            "symphainy-celery-beat"
        ]
        
        failed_containers = []
        container_statuses = {}
        
        for container in required_containers:
            status = check_container_status(container)
            container_statuses[container] = status
            
            if not status["exists"]:
                failed_containers.append(f"{container}: not found")
            elif status["status"] != "running":
                failed_containers.append(f"{container}: status={status['status']}")
        
        if failed_containers:
            details = "\n".join([f"  - {c}" for c in failed_containers])
            pytest.fail(
                f"Required Docker containers are not running:\n{details}\n\n"
                f"Full status:\n{self._format_container_statuses(container_statuses)}\n\n"
                f"Start containers with: docker-compose -f docker-compose.infrastructure.yml up -d"
            )
    
    @pytest.mark.asyncio
    async def test_docker_containers_are_healthy(self):
        """Verify all Docker containers are healthy (not restarting)."""
        containers_with_health = [
            "symphainy-redis",
            "symphainy-arangodb",
            "symphainy-consul",
            "symphainy-celery-worker",
            "symphainy-celery-beat"
        ]
        
        unhealthy_containers = []
        container_statuses = {}
        
        for container in containers_with_health:
            status = check_container_status(container)
            container_statuses[container] = status
            
            if not status["exists"]:
                unhealthy_containers.append(f"{container}: not found")
            elif status["status"] != "running":
                unhealthy_containers.append(f"{container}: status={status['status']}")
            elif status["health"] not in ["healthy", "none", "unknown"]:
                # "none" means no health check configured (OK for some containers)
                unhealthy_containers.append(f"{container}: health={status['health']}")
            elif status["restart_count"] > 5:
                unhealthy_containers.append(f"{container}: restart_count={status['restart_count']} (possible restart loop)")
        
        if unhealthy_containers:
            details = "\n".join([f"  - {c}" for c in unhealthy_containers])
            pytest.fail(
                f"Docker containers are unhealthy:\n{details}\n\n"
                f"Full status:\n{self._format_container_statuses(container_statuses)}\n\n"
                f"Check logs with: docker logs <container_name>"
            )
    
    @pytest.mark.asyncio
    async def test_no_container_restart_loops(self):
        """Verify no containers are in restart loops."""
        all_containers = [
            "symphainy-redis",
            "symphainy-arangodb",
            "symphainy-consul",
            "symphainy-tempo",
            "symphainy-opa",
            "symphainy-celery-worker",
            "symphainy-celery-beat"
        ]
        
        restarting_containers = []
        
        for container in all_containers:
            status = check_container_status(container)
            if status["exists"] and status["restart_count"] > 10:
                restarting_containers.append(
                    f"{container}: restart_count={status['restart_count']} (possible infinite restart loop)"
                )
        
        if restarting_containers:
            details = "\n".join([f"  - {c}" for c in restarting_containers])
            pytest.fail(
                f"Containers in restart loops detected:\n{details}\n\n"
                f"Check logs with: docker logs <container_name>\n"
                f"Check health checks in docker-compose.infrastructure.yml"
            )
    
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
                f"Container status: {self._format_container_status(container_status)}\n\n"
                f"Check: docker logs symphainy-consul"
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
                f"Container status: {self._format_container_status(container_status)}\n\n"
                f"Check: docker logs symphainy-arangodb"
            )
    
    @pytest.mark.asyncio
    async def test_redis_is_reachable(self):
        """Verify Redis is reachable."""
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        
        success, error = await check_service_reachable(redis_host, redis_port, timeout=5.0)
        
        if not success:
            container_status = check_container_status("symphainy-redis")
            pytest.fail(
                f"Redis is not reachable at {redis_host}:{redis_port}\n"
                f"Error: {error}\n\n"
                f"Container status: {self._format_container_status(container_status)}\n\n"
                f"Check: docker logs symphainy-redis"
            )
    
    @pytest.mark.asyncio
    async def test_celery_workers_are_running(self):
        """Verify Celery workers are running."""
        worker_status = check_container_status("symphainy-celery-worker")
        beat_status = check_container_status("symphainy-celery-beat")
        
        failures = []
        if not worker_status["exists"] or worker_status["status"] != "running":
            failures.append(f"celery-worker: {worker_status.get('status', 'unknown')}")
        if not beat_status["exists"] or beat_status["status"] != "running":
            failures.append(f"celery-beat: {beat_status.get('status', 'unknown')}")
        
        if failures:
            details = "\n".join([f"  - {f}" for f in failures])
            pytest.fail(
                f"Celery workers are not running:\n{details}\n\n"
                f"Worker status: {self._format_container_status(worker_status)}\n"
                f"Beat status: {self._format_container_status(beat_status)}\n\n"
                f"Check: docker logs symphainy-celery-worker"
            )
    
    @pytest.mark.asyncio
    async def test_configuration_ports_match_docker(self):
        """Verify configuration port values match Docker container ports."""
        # Get expected ports from environment or defaults
        consul_port = int(os.getenv("CONSUL_PORT", "8500"))
        arango_port = int(os.getenv("ARANGO_PORT", "8529"))
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        
        # Check Docker container port mappings
        consul_success, consul_stdout, _ = run_docker_command(
            ["docker", "port", "symphainy-consul", "8500/tcp"]
        )
        arango_success, arango_stdout, _ = run_docker_command(
            ["docker", "port", "symphainy-arangodb", "8529/tcp"]
        )
        redis_success, redis_stdout, _ = run_docker_command(
            ["docker", "port", "symphainy-redis", "6379/tcp"]
        )
        
        mismatches = []
        
        if consul_success:
            # Parse port from output (format: "0.0.0.0:8500")
            mapped_port = consul_stdout.strip().split(":")[-1] if ":" in consul_stdout else None
            if mapped_port and int(mapped_port) != consul_port:
                mismatches.append(f"Consul: config={consul_port}, docker={mapped_port}")
        
        if arango_success:
            mapped_port = arango_stdout.strip().split(":")[-1] if ":" in arango_stdout else None
            if mapped_port and int(mapped_port) != arango_port:
                mismatches.append(f"ArangoDB: config={arango_port}, docker={mapped_port}")
        
        if redis_success:
            mapped_port = redis_stdout.strip().split(":")[-1] if ":" in redis_stdout else None
            if mapped_port and int(mapped_port) != redis_port:
                mismatches.append(f"Redis: config={redis_port}, docker={mapped_port}")
        
        if mismatches:
            details = "\n".join([f"  - {m}" for m in mismatches])
            pytest.fail(
                f"Configuration port mismatches detected:\n{details}\n\n"
                f"Update environment variables or docker-compose.infrastructure.yml to match"
            )
    
    @pytest.mark.asyncio
    async def test_required_environment_variables_are_set(self):
        """Verify required environment variables are set."""
        required_vars = [
            "SECRET_KEY",
            "JWT_SECRET"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            details = "\n".join([f"  - {v}" for v in missing_vars])
            pytest.fail(
                f"Required environment variables are not set:\n{details}\n\n"
                f"Set these in your environment or .env file"
            )
    
    @pytest.mark.asyncio
    async def test_celery_app_module_exists(self):
        """Verify Celery app module exists and is importable."""
        try:
            # Try to import celery_app module
            import celery_app
            assert hasattr(celery_app, 'celery'), "celery_app module should have 'celery' attribute"
            assert celery_app.celery is not None, "Celery app should be initialized"
        except ImportError as e:
            pytest.fail(
                f"Celery app module (celery_app.py) not found or not importable: {e}\n\n"
                f"Expected location: symphainy-platform/celery_app.py\n"
                f"Check that celery_app.py exists and is in the Python path"
            )
        except AttributeError as e:
            pytest.fail(
                f"Celery app module missing 'celery' attribute: {e}\n\n"
                f"Check that celery_app.py defines 'celery = Celery(...)'"
            )
    
    def _format_container_status(self, status: Dict) -> str:
        """Format container status for error messages."""
        if not status["exists"]:
            return f"Container not found: {status.get('error', 'unknown error')}"
        return (
            f"Status: {status['status']}, "
            f"Health: {status['health']}, "
            f"Restart count: {status['restart_count']}"
        )
    
    def _format_container_statuses(self, statuses: Dict[str, Dict]) -> str:
        """Format multiple container statuses for error messages."""
        lines = []
        for container, status in statuses.items():
            lines.append(f"  {container}: {self._format_container_status(status)}")
        return "\n".join(lines)

