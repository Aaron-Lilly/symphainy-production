#!/usr/bin/env python3
"""
Safe Docker Operations - All operations have timeouts and error handling.

This module provides safe wrappers for Docker operations to prevent:
- Infinite loops
- Hanging operations
- Resource exhaustion
- SSH access issues
"""

import subprocess
import logging
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 10  # seconds


def run_docker_command(
    cmd: List[str],
    timeout: int = DEFAULT_TIMEOUT,
    capture_output: bool = True
) -> Tuple[bool, str, str]:
    """
    Run Docker command with timeout.
    
    Args:
        cmd: Docker command (without 'docker' prefix)
        timeout: Timeout in seconds
        capture_output: Whether to capture stdout/stderr
    
    Returns:
        (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ["docker"] + cmd,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        logger.error(f"Docker command timed out after {timeout} seconds: {' '.join(cmd)}")
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        logger.error(f"Docker command failed: {e}")
        return False, "", str(e)


def check_container_status(container_name: str) -> Dict[str, Any]:
    """
    Check Docker container status safely.
    
    Returns:
        Dict with status, health, restart_count, failing_streak, etc.
    """
    success, stdout, stderr = run_docker_command(
        ["inspect", "--format",
         "{{.State.Status}}|{{.State.Health.Status}}|{{.RestartCount}}|{{.State.Health.FailingStreak}}",
         container_name],
        timeout=5
    )
    
    if not success:
        return {
            "exists": False,
            "status": "not_found",
            "health": "unknown",
            "restart_count": 0,
            "failing_streak": 0,
            "error": stderr
        }
    
    parts = stdout.strip().split("|")
    return {
        "exists": True,
        "status": parts[0] if len(parts) > 0 else "unknown",
        "health": parts[1] if len(parts) > 1 else "unknown",
        "restart_count": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0,
        "failing_streak": int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0,
        "error": None
    }


def check_container_health(container_name: str) -> bool:
    """
    Check if container is healthy (quick check).
    
    Returns:
        True if healthy, False otherwise
    """
    status = check_container_status(container_name)
    if not status["exists"]:
        return False
    
    # Alert on restart loops
    if status["restart_count"] > 10:
        logger.warning(
            f"⚠️ {container_name}: restart_count={status['restart_count']} "
            f"(possible restart loop)"
        )
    
    if status["failing_streak"] > 10:
        logger.warning(
            f"⚠️ {container_name}: failing_streak={status['failing_streak']} "
            f"(health check failing)"
        )
    
    return (
        status["status"] == "running" and
        status["health"] in ["healthy", "none", "unknown"] and
        status["restart_count"] <= 10 and
        status["failing_streak"] <= 10
    )


def get_container_logs(
    container_name: str,
    tail: int = 50,
    timeout: int = 5
) -> Tuple[bool, str]:
    """
    Get container logs safely (with limits).
    
    Args:
        container_name: Container name
        tail: Number of lines to retrieve
        timeout: Timeout in seconds
    
    Returns:
        (success, logs)
    """
    success, stdout, stderr = run_docker_command(
        ["logs", "--tail", str(tail), container_name],
        timeout=timeout
    )
    
    if not success:
        return False, stderr
    
    return True, stdout


def check_all_containers_healthy() -> Dict[str, bool]:
    """
    Check health of all required containers.
    
    Returns:
        Dict mapping container names to health status
    """
    containers = [
        "symphainy-redis",
        "symphainy-arangodb",
        "symphainy-consul",
        "symphainy-celery-worker",
        "symphainy-celery-beat"
    ]
    
    results = {}
    for container in containers:
        results[container] = check_container_health(container)
    
    return results


def format_container_status(status: Dict[str, Any]) -> str:
    """Format container status for error messages."""
    if not status["exists"]:
        return f"Container not found: {status.get('error', 'unknown error')}"
    
    return (
        f"Status: {status['status']}, "
        f"Health: {status['health']}, "
        f"Restarts: {status['restart_count']}, "
        f"Failing streak: {status['failing_streak']}"
    )

