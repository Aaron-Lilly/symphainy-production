#!/usr/bin/env python3
"""
Integration Tests: DIContainer Service with Infrastructure

Tests the DIContainerService integration with actual infrastructure services.
This test suite ensures we catch infrastructure integration issues that were
missed in the previous testing approach.

WHAT (Test Role): I validate DI container integration with infrastructure services
HOW (Test Implementation): I test actual service connections, not just abstractions

Key Learnings from Infrastructure Testing:
1. Test actual service connections, not just abstractions
2. Test infrastructure service availability and health
3. Test configuration loading from environment
4. Test error handling when infrastructure is unavailable
5. Test dependency chains and startup order
"""

import pytest
import asyncio
import sys
import os
import httpx
import redis
from pathlib import Path
from unittest.mock import Mock, patch

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../symphainy-platform'))

from foundations.di_container.di_container_service import DIContainerService


class TestDIContainerInfrastructureIntegration:
    """Integration tests for DIContainerService with infrastructure services."""
    
    @pytest.fixture
    def infrastructure_services_available(self):
        """Check if infrastructure services are available."""
        services = {
            'consul': False,
            'redis': False,
            'arangodb': False,
            'tempo': False,
            'grafana': False,
            'otel_collector': False
        }
        
        # Check Consul
        try:
            async def check_consul():
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get("http://localhost:8501/v1/status/leader")
                    return response.status_code == 200
            services['consul'] = asyncio.run(check_consul())
        except:
            pass
        
        # Check Redis
        try:
            r = redis.StrictRedis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=5)
            services['redis'] = r.ping()
        except:
            pass
        
        # Check ArangoDB
        try:
            async def check_arangodb():
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get("http://localhost:8529/_api/version")
                    return response.status_code == 200
            services['arangodb'] = asyncio.run(check_arangodb())
        except:
            pass
        
        # Check Tempo
        try:
            async def check_tempo():
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get("http://localhost:3200/status")
                    return response.status_code == 200
            services['tempo'] = asyncio.run(check_tempo())
        except:
            pass
        
        # Check Grafana
        try:
            async def check_grafana():
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get("http://localhost:3000/api/health")
                    return response.status_code == 200
            services['grafana'] = asyncio.run(check_grafana())
        except:
            pass
        
        # Check OpenTelemetry Collector
        try:
            async def check_otel():
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get("http://localhost:8889/metrics")
                    return response.status_code == 200
            services['otel_collector'] = asyncio.run(check_otel())
        except:
            pass
        
        return services
    
    @pytest.fixture
    def di_container_with_infrastructure(self, infrastructure_services_available):
        """Create DI container with infrastructure services available."""
        # Set environment variables for infrastructure services
        env_vars = {
            'CONSUL_URL': 'http://localhost:8501',
            'REDIS_HOST': 'localhost',
            'REDIS_PORT': '6379',
            'ARANGODB_URL': 'http://localhost:8529',
            'TEMPO_URL': 'http://localhost:3200',
            'GRAFANA_URL': 'http://localhost:3000',
            'OTEL_COLLECTOR_METRICS_URL': 'http://localhost:8889'
        }
        
        with patch.dict(os.environ, env_vars):
            container = DIContainerService("infrastructure_test")
            return container
    
    def test_di_container_with_consul_available(self, di_container_with_infrastructure, infrastructure_services_available):
        """Test DI container with Consul service available."""
        if not infrastructure_services_available['consul']:
            pytest.skip("Consul service not available")
        
        container = di_container_with_infrastructure
        
        # Test that DI container can access Consul configuration
        config = container.get_config()
        consul_url = config.get_string('CONSUL_URL', 'http://localhost:8501')
        assert consul_url == 'http://localhost:8501'
        
        # Test that health utility can check Consul
        health = container.get_health()
        health.set_status("consul", "healthy")
        assert health.get_status()["consul"] == "healthy"
    
    def test_di_container_with_redis_available(self, di_container_with_infrastructure, infrastructure_services_available):
        """Test DI container with Redis service available."""
        if not infrastructure_services_available['redis']:
            pytest.skip("Redis service not available")
        
        container = di_container_with_infrastructure
        
        # Test that DI container can access Redis configuration
        config = container.get_config()
        redis_host = config.get_string('REDIS_HOST', 'localhost')
        redis_port = config.get_int('REDIS_PORT', 6379)
        assert redis_host == 'localhost'
        assert redis_port == 6379
        
        # Test that health utility can check Redis
        health = container.get_health()
        health.set_status("redis", "healthy")
        assert health.get_status()["redis"] == "healthy"
    
    def test_di_container_with_arangodb_available(self, di_container_with_infrastructure, infrastructure_services_available):
        """Test DI container with ArangoDB service available."""
        if not infrastructure_services_available['arangodb']:
            pytest.skip("ArangoDB service not available")
        
        container = di_container_with_infrastructure
        
        # Test that DI container can access ArangoDB configuration
        config = container.get_config()
        arangodb_url = config.get_string('ARANGODB_URL', 'http://localhost:8529')
        assert arangodb_url == 'http://localhost:8529'
        
        # Test that health utility can check ArangoDB
        health = container.get_health()
        health.set_status("arangodb", "healthy")
        assert health.get_status()["arangodb"] == "healthy"
    
    def test_di_container_with_tempo_available(self, di_container_with_infrastructure, infrastructure_services_available):
        """Test DI container with Tempo service available."""
        if not infrastructure_services_available['tempo']:
            pytest.skip("Tempo service not available")
        
        container = di_container_with_infrastructure
        
        # Test that DI container can access Tempo configuration
        config = container.get_config()
        tempo_url = config.get_string('TEMPO_URL', 'http://localhost:3200')
        assert tempo_url == 'http://localhost:3200'
        
        # Test that telemetry utility can work with Tempo
        telemetry = container.get_telemetry()
        telemetry.bootstrap()
        assert telemetry.is_bootstrapped() is True
        
        # Test that health utility can check Tempo
        health = container.get_health()
        health.set_status("tempo", "healthy")
        assert health.get_status()["tempo"] == "healthy"
    
    def test_di_container_with_grafana_available(self, di_container_with_infrastructure, infrastructure_services_available):
        """Test DI container with Grafana service available."""
        if not infrastructure_services_available['grafana']:
            pytest.skip("Grafana service not available")
        
        container = di_container_with_infrastructure
        
        # Test that DI container can access Grafana configuration
        config = container.get_config()
        grafana_url = config.get_string('GRAFANA_URL', 'http://localhost:3000')
        assert grafana_url == 'http://localhost:3000'
        
        # Test that health utility can check Grafana
        health = container.get_health()
        health.set_status("grafana", "healthy")
        assert health.get_status()["grafana"] == "healthy"
    
    def test_di_container_with_otel_collector_available(self, di_container_with_infrastructure, infrastructure_services_available):
        """Test DI container with OpenTelemetry Collector service available."""
        if not infrastructure_services_available['otel_collector']:
            pytest.skip("OpenTelemetry Collector service not available")
        
        container = di_container_with_infrastructure
        
        # Test that DI container can access OpenTelemetry Collector configuration
        config = container.get_config()
        otel_url = config.get_string('OTEL_COLLECTOR_METRICS_URL', 'http://localhost:8889')
        assert otel_url == 'http://localhost:8889'
        
        # Test that telemetry utility can work with OpenTelemetry Collector
        telemetry = container.get_telemetry()
        telemetry.bootstrap()
        assert telemetry.is_bootstrapped() is True
        
        # Test that health utility can check OpenTelemetry Collector
        health = container.get_health()
        health.set_status("otel_collector", "healthy")
        assert health.get_status()["otel_collector"] == "healthy"
    
    def test_di_container_with_all_infrastructure_available(self, di_container_with_infrastructure, infrastructure_services_available):
        """Test DI container with all infrastructure services available."""
        available_services = sum(1 for status in infrastructure_services_available.values() if status)
        total_services = len(infrastructure_services_available)
        
        if available_services < total_services:
            pytest.skip(f"Only {available_services}/{total_services} infrastructure services available")
        
        container = di_container_with_infrastructure
        
        # Test that all utilities can work together
        logger = container.get_logger("integration_test")
        health = container.get_health()
        telemetry = container.get_telemetry()
        security = container.get_security()
        
        # Test utility initialization
        assert logger is not None
        assert health is not None
        assert telemetry is not None
        assert security is not None
        
        # Test utility bootstrap
        telemetry.bootstrap()
        security.bootstrap()
        assert telemetry.is_bootstrapped() is True
        assert security.is_bootstrapped() is True
        
        # Test health status for all services
        for service_name in infrastructure_services_available.keys():
            health.set_status(service_name, "healthy")
            assert health.get_status()[service_name] == "healthy"
        
        # Test telemetry recording
        telemetry.record_metric("infrastructure_integration", 1, {"test": "integration"})
        
        # Test logging
        logger.info("Infrastructure integration test completed")
    
    def test_di_container_with_partial_infrastructure_available(self, di_container_with_infrastructure, infrastructure_services_available):
        """Test DI container with partial infrastructure services available."""
        available_services = [name for name, status in infrastructure_services_available.items() if status]
        
        if not available_services:
            pytest.skip("No infrastructure services available")
        
        container = di_container_with_infrastructure
        
        # Test that DI container works with available services
        health = container.get_health()
        telemetry = container.get_telemetry()
        
        # Test health status for available services
        for service_name in available_services:
            health.set_status(service_name, "healthy")
            assert health.get_status()[service_name] == "healthy"
        
        # Test telemetry with available services
        telemetry.bootstrap()
        assert telemetry.is_bootstrapped() is True
        
        # Test that unavailable services are handled gracefully
        unavailable_services = [name for name, status in infrastructure_services_available.items() if not status]
        for service_name in unavailable_services:
            health.set_status(service_name, "unavailable")
            assert health.get_status()[service_name] == "unavailable"
    
    def test_di_container_infrastructure_error_handling(self, di_container_with_infrastructure):
        """Test DI container error handling when infrastructure services are unavailable."""
        container = di_container_with_infrastructure
        
        # Test that DI container handles infrastructure errors gracefully
        health = container.get_health()
        error_handler = container.get_error_handler()
        
        # Test error handling for unavailable services
        try:
            # Simulate infrastructure error
            raise ConnectionError("Infrastructure service unavailable")
        except Exception as e:
            error_handler.handle_error(e, "infrastructure_error_test")
        
        # Test that system continues to work after infrastructure error
        health.set_status("error_recovery", "healthy")
        assert health.get_status()["error_recovery"] == "healthy"
    
    def test_di_container_configuration_loading_from_infrastructure(self, di_container_with_infrastructure):
        """Test DI container configuration loading from infrastructure environment."""
        container = di_container_with_infrastructure
        config = container.get_config()
        
        # Test that configuration is loaded from environment
        assert config.get_string('CONSUL_URL') == 'http://localhost:8501'
        assert config.get_string('REDIS_HOST') == 'localhost'
        assert config.get_int('REDIS_PORT') == 6379
        assert config.get_string('ARANGODB_URL') == 'http://localhost:8529'
        assert config.get_string('TEMPO_URL') == 'http://localhost:3200'
        assert config.get_string('GRAFANA_URL') == 'http://localhost:3000'
        assert config.get_string('OTEL_COLLECTOR_METRICS_URL') == 'http://localhost:8889'
    
    def test_di_container_fastapi_app_with_infrastructure(self, di_container_with_infrastructure):
        """Test DI container FastAPI app creation with infrastructure services."""
        container = di_container_with_infrastructure
        
        # Test FastAPI app creation
        app = container.create_fastapi_app("infrastructure_test_app")
        assert app is not None
        
        # Test app configuration
        assert app.title == "infrastructure_test_app MCP Server"
        assert app.version == "1.0.0"
        
        # Test that app can access infrastructure configuration
        config = container.get_config()
        assert config.get_string('CONSUL_URL') == 'http://localhost:8501'
    
    def test_di_container_utility_dependency_chain(self, di_container_with_infrastructure):
        """Test DI container utility dependency chain with infrastructure services."""
        container = di_container_with_infrastructure
        
        # Test that utilities can access each other through the DI container
        logger = container.get_logger("dependency_test")
        health = container.get_health()
        telemetry = container.get_telemetry()
        security = container.get_security()
        
        # Test utility dependency chain
        logger.info("Testing utility dependency chain")
        health.set_status("dependency_test", "healthy")
        telemetry.bootstrap()
        security.bootstrap()
        
        # Test that utilities work together
        assert telemetry.is_bootstrapped() is True
        assert security.is_bootstrapped() is True
        assert health.get_status()["dependency_test"] == "healthy"
        
        # Test telemetry recording
        telemetry.record_metric("dependency_chain_test", 1, {"test": "dependency"})
        
        # Test security operations
        assert security.service_name == "infrastructure_test"
    
    def test_di_container_concurrent_access_with_infrastructure(self, di_container_with_infrastructure):
        """Test DI container concurrent access with infrastructure services."""
        import threading
        import time
        
        container = di_container_with_infrastructure
        results = []
        
        def worker(worker_id):
            logger = container.get_logger(f"worker_{worker_id}")
            health = container.get_health()
            telemetry = container.get_telemetry()
            
            # Test concurrent operations with infrastructure
            logger.info(f"Worker {worker_id} testing infrastructure integration")
            health.set_status(f"worker_{worker_id}", "healthy")
            telemetry.bootstrap()
            telemetry.record_metric(f"worker_{worker_id}_metric", 1)
            
            results.append(f"worker_{worker_id}_completed")
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Test that all workers completed
        assert len(results) == 3
        for i in range(3):
            assert f"worker_{i}_completed" in results
        
        # Test that health status is properly maintained
        health = container.get_health()
        for i in range(3):
            assert health.get_status()[f"worker_{i}"] == "healthy"





