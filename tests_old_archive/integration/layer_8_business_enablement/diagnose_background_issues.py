#!/usr/bin/env python3
"""
Diagnose Background Issues

This script checks for background issues that might be affecting SSH or system resources:
- Docker container restart loops
- Resource consumption
- Hanging processes
- Environment variable issues
"""

import subprocess
import sys
import signal
import json
import os
from typing import Dict, Any, List
from datetime import datetime


def run_with_timeout(command: List[str], timeout: int = 5) -> tuple[str, int]:
    """Run a command with timeout."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds", 124
    except Exception as e:
        return f"Error: {e}", 1


def check_docker_containers() -> Dict[str, Any]:
    """Check Docker container status and restart counts."""
    print("\n🐳 Checking Docker Containers...")
    
    # Get all containers with restart counts
    stdout, code = run_with_timeout(
        ["docker", "ps", "-a", "--format", "{{.Names}}\t{{.Status}}\t{{.RestartCount}}"],
        timeout=5
    )
    
    if code != 0:
        return {"error": f"Failed to check containers: {stdout}"}
    
    containers = []
    restart_loops = []
    
    for line in stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 3:
            name = parts[0]
            status = parts[1]
            restart_count = int(parts[2]) if parts[2].isdigit() else 0
            
            containers.append({
                "name": name,
                "status": status,
                "restart_count": restart_count
            })
            
            # Flag containers with high restart counts (potential restart loop)
            if restart_count > 5:
                restart_loops.append({
                    "name": name,
                    "restart_count": restart_count,
                    "status": status
                })
    
    return {
        "total_containers": len(containers),
        "containers": containers,
        "restart_loops": restart_loops,
        "has_issues": len(restart_loops) > 0
    }


def check_system_resources() -> Dict[str, Any]:
    """Check system resource usage."""
    print("\n💻 Checking System Resources...")
    
    # Check memory usage
    mem_stdout, mem_code = run_with_timeout(
        ["free", "-h"],
        timeout=3
    )
    
    # Check disk usage
    disk_stdout, disk_code = run_with_timeout(
        ["df", "-h", "/"],
        timeout=3
    )
    
    # Check CPU load
    load_stdout, load_code = run_with_timeout(
        ["uptime"],
        timeout=3
    )
    
    return {
        "memory": mem_stdout if mem_code == 0 else "Failed to get memory info",
        "disk": disk_stdout if disk_code == 0 else "Failed to get disk info",
        "load": load_stdout if load_code == 0 else "Failed to get load info"
    }


def check_hanging_processes() -> Dict[str, Any]:
    """Check for processes that might be hanging."""
    print("\n🔍 Checking for Hanging Processes...")
    
    # Check for pytest processes
    pytest_stdout, pytest_code = run_with_timeout(
        ["ps", "aux"],
        timeout=3
    )
    
    hanging = []
    if pytest_code == 0:
        for line in pytest_stdout.split('\n'):
            if 'pytest' in line.lower() or 'python' in line.lower():
                parts = line.split()
                if len(parts) >= 11:
                    cpu = float(parts[2]) if parts[2].replace('.', '').isdigit() else 0
                    mem = float(parts[3]) if parts[3].replace('.', '').isdigit() else 0
                    # Flag processes with high CPU but no progress (potential hang)
                    if cpu > 50.0 or mem > 50.0:
                        hanging.append({
                            "pid": parts[1],
                            "cpu": cpu,
                            "mem": mem,
                            "command": ' '.join(parts[10:])
                        })
    
    return {
        "hanging_processes": hanging,
        "has_issues": len(hanging) > 0
    }


def check_environment_variables() -> Dict[str, Any]:
    """Check for problematic environment variables."""
    print("\n🔐 Checking Environment Variables...")
    
    issues = []
    
    # Check GOOGLE_APPLICATION_CREDENTIALS
    gac = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if gac:
        if not os.path.exists(gac):
            issues.append({
                "variable": "GOOGLE_APPLICATION_CREDENTIALS",
                "value": gac,
                "issue": "Path does not exist - could break SSH/GCP access"
            })
        else:
            # Check if it's readable
            if not os.access(gac, os.R_OK):
                issues.append({
                    "variable": "GOOGLE_APPLICATION_CREDENTIALS",
                    "value": gac,
                    "issue": "File exists but is not readable"
                })
    
    return {
        "GOOGLE_APPLICATION_CREDENTIALS": gac or "Not set",
        "issues": issues,
        "has_issues": len(issues) > 0
    }


def check_docker_health_status() -> Dict[str, Any]:
    """Check Docker container health status."""
    print("\n🏥 Checking Docker Container Health...")
    
    # Get containers with health checks
    stdout, code = run_with_timeout(
        ["docker", "ps", "--format", "{{.Names}}"],
        timeout=3
    )
    
    if code != 0:
        return {"error": "Failed to get container list"}
    
    health_status = {}
    unhealthy = []
    
    for container in stdout.strip().split('\n'):
        if not container.strip():
            continue
        
        # Check health status
        health_stdout, health_code = run_with_timeout(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}", container],
            timeout=2
        )
        
        if health_code == 0 and health_stdout.strip() and health_stdout.strip() != "none":
            status = health_stdout.strip()
            health_status[container] = status
            
            if status == "unhealthy":
                # Get failing streak
                streak_stdout, _ = run_with_timeout(
                    ["docker", "inspect", "--format", "{{.State.Health.FailingStreak}}", container],
                    timeout=2
                )
                failing_streak = int(streak_stdout.strip()) if streak_stdout.strip().isdigit() else 0
                
                unhealthy.append({
                    "container": container,
                    "status": status,
                    "failing_streak": failing_streak
                })
    
    return {
        "health_status": health_status,
        "unhealthy": unhealthy,
        "has_issues": len(unhealthy) > 0
    }


def main():
    """Main diagnostic function."""
    print("=" * 60)
    print("🔍 Background Issues Diagnostic")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "docker_containers": check_docker_containers(),
        "docker_health": check_docker_health_status(),
        "system_resources": check_system_resources(),
        "hanging_processes": check_hanging_processes(),
        "environment_variables": check_environment_variables()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    issues_found = False
    
    # Docker restart loops
    if results["docker_containers"].get("restart_loops"):
        print("\n⚠️  DOCKER RESTART LOOPS DETECTED:")
        for container in results["docker_containers"]["restart_loops"]:
            print(f"  - {container['name']}: {container['restart_count']} restarts ({container['status']})")
        issues_found = True
    
    # Unhealthy containers
    if results["docker_health"].get("unhealthy"):
        print("\n⚠️  UNHEALTHY DOCKER CONTAINERS:")
        for container in results["docker_health"]["unhealthy"]:
            print(f"  - {container['container']}: {container['status']} (failing streak: {container['failing_streak']})")
        issues_found = True
    
    # Hanging processes
    if results["hanging_processes"].get("hanging_processes"):
        print("\n⚠️  HIGH RESOURCE USAGE PROCESSES:")
        for proc in results["hanging_processes"]["hanging_processes"]:
            print(f"  - PID {proc['pid']}: {proc['cpu']}% CPU, {proc['mem']}% MEM")
            print(f"    Command: {proc['command'][:80]}...")
        issues_found = True
    
    # Environment variable issues
    if results["environment_variables"].get("issues"):
        print("\n⚠️  ENVIRONMENT VARIABLE ISSUES:")
        for issue in results["environment_variables"]["issues"]:
            print(f"  - {issue['variable']}: {issue['issue']}")
            print(f"    Value: {issue['value']}")
        issues_found = True
    
    if not issues_found:
        print("\n✅ No obvious issues detected")
        print("\nNote: SSH keepalive pings are normal and expected.")
        print("If you're experiencing SSH issues, check:")
        print("  1. Docker container restart loops (above)")
        print("  2. System resource exhaustion (check system_resources)")
        print("  3. Environment variable conflicts (above)")
    
    # Save full results
    output_file = f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Full diagnostic results saved to: {output_file}")
    
    return 0 if not issues_found else 1


if __name__ == "__main__":
    sys.exit(main())

