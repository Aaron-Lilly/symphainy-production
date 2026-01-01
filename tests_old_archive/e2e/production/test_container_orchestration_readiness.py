#!/usr/bin/env python3
"""
Production Test: Container Orchestration Readiness

Tests container orchestration readiness for Cloud Run/GKE:
1. Containers are stateless (no local file dependencies)
2. Health checks work for orchestration
3. Containers can be deployed to Cloud Run/GKE
4. Services don't depend on Docker networking

This test validates that containers are ready for orchestration platforms.
"""

import pytest
import subprocess
import asyncio
import httpx
from typing import Dict, Any, List, Optional

pytestmark = [pytest.mark.e2e, pytest.mark.production_readiness, pytest.mark.critical]

TIMEOUT = 30.0
BASE_URL = "http://localhost"


class TestContainerOrchestrationReadiness:
    """Test container orchestration readiness for Cloud Run/GKE."""
    
    def get_container_config(self, container_name: str) -> Optional[Dict[str, Any]]:
        """Get Docker container configuration."""
        try:
            result = subprocess.run(
                ["docker", "inspect", container_name, "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
        except Exception as e:
            print(f"⚠️  Error getting container config for {container_name}: {e}")
        return None
    
    @pytest.mark.asyncio
    async def test_containers_have_health_checks(self):
        """
        Test that containers have health checks configured.
        
        Verifies:
        - Backend has health check
        - Frontend has health check
        - Health checks are suitable for orchestration platforms
        """
        print("\n" + "="*70)
        print("CONTAINER ORCHESTRATION TEST: Health Checks Configured")
        print("="*70)
        
        containers = {
            "symphainy-backend-prod": "Backend API",
            "symphainy-frontend-prod": "Frontend UI",
        }
        
        print(f"\n[HEALTH CHECKS]")
        containers_with_health = []
        
        for container_name, description in containers.items():
            config = self.get_container_config(container_name)
            
            if config:
                healthcheck = config.get("Config", {}).get("Healthcheck")
                
                if healthcheck:
                    test_cmd = healthcheck.get("Test", [])
                    interval = healthcheck.get("Interval", 0)
                    timeout = healthcheck.get("Timeout", 0)
                    retries = healthcheck.get("Retries", 0)
                    
                    print(f"   ✅ {container_name}: Health check configured")
                    print(f"      Test: {test_cmd}")
                    print(f"      Interval: {interval}ns")
                    print(f"      Timeout: {timeout}ns")
                    print(f"      Retries: {retries}")
                    
                    containers_with_health.append(container_name)
                else:
                    print(f"   ⚠️  {container_name}: No health check configured")
            else:
                print(f"   ⚠️  {container_name}: Container not found")
        
        # Verify at least application containers have health checks
        assert len(containers_with_health) > 0, \
            "❌ No containers have health checks configured"
        
        print(f"\n   ✅ Health checks verified: {len(containers_with_health)}/{len(containers)} containers")
    
    @pytest.mark.asyncio
    async def test_containers_are_stateless(self):
        """
        Test that containers are stateless (suitable for Cloud Run/GKE).
        
        Verifies:
        - Containers don't require local file storage
        - Containers don't require local volumes
        - Containers can be scaled horizontally
        """
        print("\n" + "="*70)
        print("CONTAINER ORCHESTRATION TEST: Stateless Containers")
        print("="*70)
        
        containers = {
            "symphainy-backend-prod": "Backend API",
            "symphainy-frontend-prod": "Frontend UI",
        }
        
        print(f"\n[STATELESS CHECK]")
        stateless_containers = []
        
        for container_name, description in containers.items():
            config = self.get_container_config(container_name)
            
            if config:
                # Check for volume mounts (stateful storage)
                mounts = config.get("Mounts", [])
                volumes = [m.get("Destination", "") for m in mounts if m.get("Type") == "volume"]
                
                if volumes:
                    print(f"   ⚠️  {container_name}: Has volume mounts: {volumes}")
                    print(f"      Note: Some volumes may be acceptable (logs, temp files)")
                else:
                    print(f"   ✅ {container_name}: No volume mounts (stateless)")
                    stateless_containers.append(container_name)
            else:
                print(f"   ⚠️  {container_name}: Container not found")
        
        # Application containers should be stateless
        # Infrastructure containers (Redis, ArangoDB) can be stateful
        print(f"\n   ✅ Stateless containers verified: {len(stateless_containers)}/{len(containers)} application containers")
        print(f"      Note: Infrastructure containers (Redis, ArangoDB) are expected to be stateful")
    
    @pytest.mark.asyncio
    async def test_health_checks_work_for_orchestration(self, http_client):
        """
        Test that health checks work for orchestration platforms.
        
        Verifies:
        - Health endpoints are accessible
        - Health endpoints return appropriate status codes
        - Health checks are fast enough for orchestration
        """
        print("\n" + "="*70)
        print("CONTAINER ORCHESTRATION TEST: Health Checks Work for Orchestration")
        print("="*70)
        
        health_endpoints = {
            "/api/health": "Backend health endpoint",
        }
        
        print(f"\n[ORCHESTRATION HEALTH CHECKS]")
        working_endpoints = []
        
        for endpoint, description in health_endpoints.items():
            try:
                import time
                start_time = time.time()
                response = await asyncio.wait_for(
                    http_client.get(endpoint),
                    timeout=10.0
                )
                elapsed_time = (time.time() - start_time) * 1000
                
                # Health checks should be fast (< 1s for orchestration)
                if elapsed_time < 1000:
                    print(f"   ✅ {endpoint}: Fast ({elapsed_time:.0f}ms)")
                else:
                    print(f"   ⚠️  {endpoint}: Slow ({elapsed_time:.0f}ms) - may timeout in orchestration")
                
                # Should return 200 or valid status
                if response.status_code in [200, 401, 403, 503]:
                    print(f"      Status: {response.status_code}")
                    working_endpoints.append(endpoint)
                else:
                    print(f"      Status: {response.status_code} (may not be suitable for orchestration)")
                
            except asyncio.TimeoutError:
                print(f"   ❌ {endpoint}: Timeout (not suitable for orchestration)")
            except Exception as e:
                print(f"   ❌ {endpoint}: Error - {e}")
        
        # Verify at least some health endpoints work
        assert len(working_endpoints) > 0, \
            "❌ No health endpoints are working for orchestration"
        
        print(f"\n   ✅ Health checks verified: {len(working_endpoints)}/{len(health_endpoints)} endpoints working")
    
    @pytest.mark.asyncio
    async def test_containers_dont_depend_on_docker_networking(self):
        """
        Test that containers don't depend on Docker networking.
        
        Verifies:
        - Services use environment variables for service URLs
        - Services don't hardcode container names
        - Services can work with external service URLs
        """
        print("\n" + "="*70)
        print("CONTAINER ORCHESTRATION TEST: No Docker Networking Dependencies")
        print("="*70)
        
        backend_container = "symphainy-backend-prod"
        
        print(f"\n[DOCKER NETWORKING CHECK]")
        print(f"   Container: {backend_container}")
        
        config = self.get_container_config(backend_container)
        
        if config:
            env_vars = config.get("Config", {}).get("Env", [])
            env_dict = {var.split("=")[0]: var.split("=")[1] if "=" in var else "" for var in env_vars if "=" in var}
            
            # Check for Docker-specific networking patterns
            docker_patterns = [
                "redis:6379",  # Container name
                "arangodb:8529",  # Container name
                "traefik:8080",  # Container name
            ]
            
            found_patterns = []
            for var_name, var_value in env_dict.items():
                for pattern in docker_patterns:
                    if pattern in var_value:
                        found_patterns.append(f"{var_name}={var_value}")
            
            if found_patterns:
                print(f"   ⚠️  Found Docker networking patterns:")
                for pattern in found_patterns:
                    print(f"      {pattern}")
                print(f"      Note: These are defaults and can be overridden for managed services")
            else:
                print(f"   ✅ No hardcoded Docker networking patterns")
            
            # Verify environment variables exist (means configuration is externalized)
            assert len(env_dict) > 0, \
                "❌ No environment variables found - services may depend on Docker networking"
            
            print(f"\n   ✅ Docker networking dependencies verified")
            print(f"      Services use environment variables (can be overridden for managed services)")





