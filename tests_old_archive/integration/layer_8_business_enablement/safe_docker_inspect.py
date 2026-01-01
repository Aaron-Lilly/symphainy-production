#!/usr/bin/env python3
"""
Safe Docker Container Inspection Script

This script safely checks Docker container status and logs with timeouts
to prevent infinite loops that could lock out VM sessions.

Usage:
    python3 safe_docker_inspect.py [container_name]
    python3 safe_docker_inspect.py --all
    python3 safe_docker_inspect.py --health
"""

import subprocess
import sys
import signal
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


class TimeoutError(Exception):
    """Custom timeout error."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutError("Operation timed out")


def run_with_timeout(command: List[str], timeout: int = 5) -> tuple[str, int]:
    """
    Run a command with a timeout to prevent hanging.
    
    Args:
        command: Command to run as list
        timeout: Timeout in seconds (default: 5)
        
    Returns:
        Tuple of (stdout, return_code)
    """
    try:
        # Set up signal handler for timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            signal.alarm(0)  # Cancel alarm
            return result.stdout, result.returncode
        except subprocess.TimeoutExpired:
            signal.alarm(0)
            return f"Command timed out after {timeout} seconds", 124
        except TimeoutError:
            signal.alarm(0)
            return f"Command timed out after {timeout} seconds", 124
    except Exception as e:
        signal.alarm(0)
        return f"Error running command: {e}", 1


def check_container_status(container_name: str) -> Dict[str, Any]:
    """Check container status with timeout."""
    print(f"\n📊 Checking status for: {container_name}")
    
    # Check if container exists
    stdout, code = run_with_timeout(
        ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}\t{{.Status}}\t{{.State}}"],
        timeout=3
    )
    
    if code != 0:
        return {"error": f"Failed to check container: {stdout}", "exists": False}
    
    if not stdout.strip():
        return {"exists": False, "message": f"Container '{container_name}' not found"}
    
    # Parse status
    parts = stdout.strip().split('\t')
    if len(parts) >= 3:
        return {
            "exists": True,
            "name": parts[0],
            "status": parts[1],
            "state": parts[2]
        }
    
    return {"exists": True, "raw_status": stdout.strip()}


def get_container_logs(container_name: str, lines: int = 50) -> Dict[str, Any]:
    """Get container logs with timeout."""
    print(f"📋 Getting last {lines} lines of logs for: {container_name}")
    
    stdout, code = run_with_timeout(
        ["docker", "logs", "--tail", str(lines), container_name],
        timeout=5
    )
    
    if code != 0:
        return {"error": f"Failed to get logs: {stdout}", "logs": ""}
    
    return {"logs": stdout, "lines": lines}


def check_container_health(container_name: str) -> Dict[str, Any]:
    """Check container health status with timeout."""
    print(f"🏥 Checking health for: {container_name}")
    
    # Get health status from inspect
    stdout, code = run_with_timeout(
        ["docker", "inspect", "--format", "{{json .State.Health}}", container_name],
        timeout=3
    )
    
    if code != 0:
        return {"error": f"Failed to check health: {stdout}", "has_healthcheck": False}
    
    if not stdout.strip() or stdout.strip() == "null":
        return {"has_healthcheck": False, "message": "No health check configured"}
    
    try:
        health_data = json.loads(stdout)
        return {
            "has_healthcheck": True,
            "status": health_data.get("Status", "unknown"),
            "failing_streak": health_data.get("FailingStreak", 0),
            "log": health_data.get("Log", [])
        }
    except json.JSONDecodeError:
        return {"has_healthcheck": True, "raw_data": stdout}


def check_container_ports(container_name: str) -> Dict[str, Any]:
    """Check container port mappings with timeout."""
    print(f"🔌 Checking ports for: {container_name}")
    
    stdout, code = run_with_timeout(
        ["docker", "port", container_name],
        timeout=3
    )
    
    if code != 0:
        return {"error": f"Failed to check ports: {stdout}", "ports": []}
    
    ports = []
    for line in stdout.strip().split('\n'):
        if line.strip():
            ports.append(line.strip())
    
    return {"ports": ports}


def get_all_containers() -> List[str]:
    """Get list of all SymphAIny containers."""
    stdout, code = run_with_timeout(
        ["docker", "ps", "-a", "--filter", "name=symphainy-", "--format", "{{.Names}}"],
        timeout=3
    )
    
    if code != 0:
        return []
    
    return [name.strip() for name in stdout.strip().split('\n') if name.strip()]


def inspect_container(container_name: str, include_logs: bool = True, include_health: bool = True) -> Dict[str, Any]:
    """Comprehensive container inspection."""
    result = {
        "container": container_name,
        "timestamp": datetime.now().isoformat(),
        "status": check_container_status(container_name),
    }
    
    if result["status"].get("exists"):
        if include_health:
            result["health"] = check_container_health(container_name)
        
        result["ports"] = check_container_ports(container_name)
        
        if include_logs:
            result["logs"] = get_container_logs(container_name, lines=30)
    
    return result


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Safely inspect Docker containers with timeouts")
    parser.add_argument("container", nargs="?", help="Container name to inspect")
    parser.add_argument("--all", action="store_true", help="Inspect all SymphAIny containers")
    parser.add_argument("--health", action="store_true", help="Only check health status")
    parser.add_argument("--no-logs", action="store_true", help="Skip log retrieval")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds (default: 5)")
    
    args = parser.parse_args()
    
    print("🔍 Safe Docker Container Inspector")
    print("=" * 50)
    print(f"Timeout: {args.timeout} seconds per operation")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    if args.all:
        containers = get_all_containers()
        if not containers:
            print("\n❌ No SymphAIny containers found")
            sys.exit(1)
        
        print(f"\n📦 Found {len(containers)} containers:")
        for container in containers:
            print(f"  - {container}")
        
        results = {}
        for container in containers:
            results[container] = inspect_container(
                container,
                include_logs=not args.no_logs,
                include_health=args.health or True
            )
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("=" * 50)
        for container, data in results.items():
            status = data.get("status", {})
            if status.get("exists"):
                state = status.get("state", "unknown")
                health = data.get("health", {})
                health_status = health.get("status", "N/A") if health.get("has_healthcheck") else "No healthcheck"
                print(f"\n{container}:")
                print(f"  State: {state}")
                print(f"  Health: {health_status}")
                if health.get("failing_streak", 0) > 0:
                    print(f"  ⚠️  Failing streak: {health['failing_streak']}")
            else:
                print(f"\n{container}: Not found")
        
        # Optionally save to file
        output_file = f"docker_inspect_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Full results saved to: {output_file}")
        
    elif args.container:
        result = inspect_container(
            args.container,
            include_logs=not args.no_logs,
            include_health=args.health or True
        )
        
        # Print formatted output
        print("\n" + "=" * 50)
        print(f"📦 Container: {args.container}")
        print("=" * 50)
        print(json.dumps(result, indent=2))
        
    else:
        # Default: Check critical containers
        critical_containers = ["symphainy-consul", "symphainy-arangodb", "symphainy-redis"]
        print("\n🔍 Checking critical containers...")
        
        for container in critical_containers:
            result = inspect_container(container, include_logs=False, include_health=True)
            status = result.get("status", {})
            if status.get("exists"):
                state = status.get("state", "unknown")
                health = result.get("health", {})
                health_status = health.get("status", "N/A") if health.get("has_healthcheck") else "No healthcheck"
                print(f"\n{container}:")
                print(f"  State: {state}")
                print(f"  Health: {health_status}")
                if health.get("failing_streak", 0) > 0:
                    print(f"  ⚠️  Failing streak: {health['failing_streak']}")
            else:
                print(f"\n{container}: Not found")


if __name__ == "__main__":
    main()

