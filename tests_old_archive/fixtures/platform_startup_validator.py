#!/usr/bin/env python3
"""
Platform Startup Validator

Validates that platform startup worked correctly and everything is healthy.
This is Layer 0 - the foundational verifier that ensures the platform can start.

WHAT: Validate platform startup and health
HOW: Check platform status, health endpoints, foundation initialization

This validator is used AFTER platform startup to verify:
1. Platform started successfully
2. All foundations initialized
3. Health checks work
4. Platform is ready for use
"""

import asyncio
import httpx
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys
import os
from datetime import datetime


class PlatformStartupValidator:
    """
    Validates that platform startup worked correctly and everything is healthy.
    
    This is the foundational verifier (Layer 0) that ensures:
    1. Platform can start successfully
    2. All foundations initialize correctly
    3. Health endpoints work
    4. Platform is ready for use
    
    Anti-patterns to catch:
    1. Platform fails to start
    2. Foundations don't initialize
    3. Health endpoints don't work
    4. Platform not ready for use
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize validator.
        
        Args:
            base_url: Base URL of the platform
            timeout: Timeout for HTTP requests in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.violations: List[Dict[str, Any]] = []
    
    async def validate_platform_startup(self) -> Dict[str, Any]:
        """
        Validate that platform started successfully.
        
        Checks:
        1. Platform responds to health endpoint
        2. Platform status is operational
        3. All foundations initialized
        4. Health checks work
        
        Returns validation results.
        """
        violations = []
        checks = {
            'health_endpoint_responds': False,
            'platform_status_operational': False,
            'foundations_initialized': False,
            'health_checks_work': False,
            'api_routers_registered': False,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Check 1: Health endpoint responds
                try:
                    health_response = await client.get(f"{self.base_url}/health")
                    if health_response.status_code == 200:
                        checks['health_endpoint_responds'] = True
                        health_data = health_response.json()
                        
                        # Check 2: Platform status is operational
                        platform_status = health_data.get('platform_status', 'unknown')
                        if platform_status == 'operational':
                            checks['platform_status_operational'] = True
                        else:
                            violations.append({
                                'type': 'platform_not_operational',
                                'message': f"Platform status is '{platform_status}', expected 'operational'",
                                'recommendation': 'Check platform startup logs for errors'
                            })
                        
                        # Check 3: Foundations initialized
                        startup_status = health_data.get('startup_status', {})
                        foundation_status = startup_status.get('foundation', 'unknown')
                        if foundation_status == 'completed':
                            checks['foundations_initialized'] = True
                        else:
                            violations.append({
                                'type': 'foundations_not_initialized',
                                'message': f"Foundation status is '{foundation_status}', expected 'completed'",
                                'recommendation': 'Check foundation initialization logs'
                            })
                        
                        # Check 4: Health checks work
                        foundation_services = health_data.get('foundation_services', {})
                        if foundation_services:
                            all_healthy = all(
                                status == 'healthy' 
                                for status in foundation_services.values()
                            )
                            if all_healthy:
                                checks['health_checks_work'] = True
                            else:
                                violations.append({
                                    'type': 'unhealthy_foundations',
                                    'message': f"Some foundations are unhealthy: {foundation_services}",
                                    'recommendation': 'Check foundation health status'
                                })
                        
                    else:
                        violations.append({
                            'type': 'health_endpoint_failed',
                            'message': f"Health endpoint returned status {health_response.status_code}",
                            'recommendation': 'Check platform startup logs'
                        })
                
                except httpx.TimeoutException:
                    violations.append({
                        'type': 'health_endpoint_timeout',
                        'message': f"Health endpoint timed out after {self.timeout} seconds",
                        'recommendation': 'Check if platform is running and accessible'
                    })
                
                except httpx.ConnectError:
                    violations.append({
                        'type': 'platform_not_accessible',
                        'message': f"Could not connect to platform at {self.base_url}",
                        'recommendation': 'Ensure platform is running and accessible'
                    })
                
                # Check 5: API routers registered (check if platform/status endpoint works)
                try:
                    status_response = await client.get(f"{self.base_url}/platform/status")
                    if status_response.status_code == 200:
                        checks['api_routers_registered'] = True
                    else:
                        violations.append({
                            'type': 'api_routers_not_registered',
                            'message': f"Platform status endpoint returned status {status_response.status_code}",
                            'recommendation': 'Check API router registration in startup'
                        })
                except Exception as e:
                    violations.append({
                        'type': 'api_routers_check_failed',
                        'message': f"Failed to check API routers: {e}",
                        'recommendation': 'Check platform startup logs'
                    })
        
        except Exception as e:
            violations.append({
                'type': 'validation_error',
                'message': f"Failed to validate platform startup: {e}",
                'recommendation': 'Check platform startup logs and network connectivity'
            })
        
        all_checks_passed = all(checks.values())
        
        return {
            'is_valid': all_checks_passed and len(violations) == 0,
            'checks': checks,
            'violations': violations,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def validate_foundation_health(self, foundation_name: str) -> Dict[str, Any]:
        """
        Validate that a specific foundation is healthy.
        
        Args:
            foundation_name: Name of the foundation to check
        
        Returns validation results.
        """
        violations = []
        checks = {
            'foundation_exists': False,
            'foundation_healthy': False,
            'foundation_accessible': False,
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Check foundation services endpoint
                try:
                    response = await client.get(f"{self.base_url}/foundation/services")
                    if response.status_code == 200:
                        data = response.json()
                        foundation_services = data.get('foundation_services', [])
                        
                        if foundation_name in foundation_services:
                            checks['foundation_exists'] = True
                            checks['foundation_accessible'] = True
                            
                            # Check health
                            health_response = await client.get(f"{self.base_url}/health")
                            if health_response.status_code == 200:
                                health_data = health_response.json()
                                foundation_services_health = health_data.get('foundation_services', {})
                                
                                if foundation_name in foundation_services_health:
                                    health_status = foundation_services_health[foundation_name]
                                    if health_status == 'healthy':
                                        checks['foundation_healthy'] = True
                                    else:
                                        violations.append({
                                            'type': 'foundation_unhealthy',
                                            'message': f"Foundation '{foundation_name}' is unhealthy: {health_status}",
                                            'recommendation': f'Check {foundation_name} initialization logs'
                                        })
                        else:
                            violations.append({
                                'type': 'foundation_not_found',
                                'message': f"Foundation '{foundation_name}' not found in foundation services",
                                'recommendation': f'Check if {foundation_name} is initialized during startup'
                            })
                    else:
                        violations.append({
                            'type': 'foundation_services_endpoint_failed',
                            'message': f"Foundation services endpoint returned status {response.status_code}",
                            'recommendation': 'Check platform startup logs'
                        })
                
                except Exception as e:
                    violations.append({
                        'type': 'foundation_health_check_failed',
                        'message': f"Failed to check foundation health: {e}",
                        'recommendation': 'Check platform startup logs and network connectivity'
                    })
        
        except Exception as e:
            violations.append({
                'type': 'validation_error',
                'message': f"Failed to validate foundation health: {e}",
                'recommendation': 'Check platform startup logs and network connectivity'
            })
        
        all_checks_passed = all(checks.values())
        
        return {
            'foundation_name': foundation_name,
            'is_valid': all_checks_passed and len(violations) == 0,
            'checks': checks,
            'violations': violations,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def validate_all_foundations(self) -> Dict[str, Any]:
        """
        Validate that all foundations are healthy.
        
        Expected foundations:
        - public_works_foundation
        - curator_foundation
        - communication_foundation
        - agentic_foundation
        
        Returns validation results for all foundations.
        """
        expected_foundations = [
            'public_works_foundation',
            'curator_foundation',
            'communication_foundation',
            'agentic_foundation',
        ]
        
        results = {}
        all_valid = True
        
        for foundation_name in expected_foundations:
            result = await self.validate_foundation_health(foundation_name)
            results[foundation_name] = result
            if not result['is_valid']:
                all_valid = False
        
        return {
            'is_valid': all_valid,
            'foundations': results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def validate_platform_readiness(self) -> Dict[str, Any]:
        """
        Comprehensive validation: Check platform startup, health, and all foundations.
        
        This is the main validation method that should be called after platform startup.
        
        Returns comprehensive validation results.
        """
        # Validate platform startup
        startup_validation = await self.validate_platform_startup()
        
        # Validate all foundations
        foundations_validation = await self.validate_all_foundations()
        
        # Combine results
        all_valid = startup_validation['is_valid'] and foundations_validation['is_valid']
        all_violations = startup_validation['violations'] + [
            v for f in foundations_validation['foundations'].values() 
            for v in f.get('violations', [])
        ]
        
        return {
            'is_valid': all_valid,
            'startup_validation': startup_validation,
            'foundations_validation': foundations_validation,
            'all_violations': all_violations,
            'violation_count': len(all_violations),
            'timestamp': datetime.utcnow().isoformat()
        }


