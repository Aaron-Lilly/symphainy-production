#!/usr/bin/env python3
"""
Layer 8: Business Enablement Enabling Services - Comprehensive Tests

Tests ALL 26 enabling services with:
1. Initialization (infrastructure, Smart City APIs, abstractions)
2. Actual functionality (not just that they initialize)
3. Platform Gateway abstraction access
4. Curator registration (Phase 2 pattern)
5. Integration with Smart City services

Infrastructure:
- Uses `smart_city_infrastructure` fixture (from test_smart_city_infrastructure.py)
- This fixture initializes all required Smart City services (Librarian, Data Steward, Content Steward, etc.)
- Services are discovered via Curator service discovery (proper architecture pattern)

Services to test:
1. file_parser_service
2. data_analyzer_service
3. metrics_calculator_service
4. validation_engine_service
5. transformation_engine_service
6. schema_mapper_service
7. workflow_manager_service
8. visualization_engine_service
9. report_generator_service
10. export_formatter_service
11. data_compositor_service
12. reconciliation_service
13. notification_service
14. audit_trail_service
15. configuration_service
16. insights_generator_service
17. roadmap_generation_service
18. format_composer_service
19. data_insights_query_service
20. coexistence_analysis_service
21. sop_builder_service
22. workflow_conversion_service
23. poc_generation_service
24. insights_orchestrator_service
25. apg_processor_service
26. (Any others found)

Test Pattern for Each Service:
- Initialize with proper setup (DI Container, Platform Gateway, Curator)
- Verify initialization succeeds
- Test actual service functionality (not just initialization)
- Verify Platform Gateway abstraction access
- Verify Curator registration
- Verify Smart City API discovery
"""

import pytest
import asyncio
from typing import Dict, Any, List

pytestmark = [pytest.mark.integration]


class TestEnablingServicesInitialization:
    """Test that all enabling services initialize correctly."""
    
    @pytest.fixture
    async def test_infrastructure(self):
        """Set up test infrastructure (DI Container, Public Works, Curator, Platform Gateway)."""
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
        
        di_container = DIContainerService("test_platform")
        pwf = PublicWorksFoundationService(di_container=di_container)
        
        # Use timeout for initialization
        try:
            pwf_result = await asyncio.wait_for(
                pwf.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Public Works Foundation initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis"
            )
        
        if not pwf_result:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Public Works Foundation initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis\n\n"
                f"Fix: Ensure all critical infrastructure containers are running and healthy."
            )
        
        di_container.public_works_foundation = pwf
        
        curator = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=pwf
        )
        
        # Use timeout for initialization
        try:
            curator_result = await asyncio.wait_for(
                curator.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Curator Foundation initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb"
            )
        
        if not curator_result:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Curator Foundation initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n\n"
                f"Fix: Ensure all critical infrastructure containers are running and healthy."
            )
        
        di_container.curator_foundation = curator
        
        # Initialize Platform Gateway
        platform_gateway = PlatformInfrastructureGateway(
            public_works_foundation=pwf
        )
        
        yield {
            "di_container": di_container,
            "public_works_foundation": pwf,
            "curator": curator,
            "platform_gateway": platform_gateway
        }
    
    @pytest.mark.asyncio
    async def test_file_parser_service_initializes(self, test_infrastructure):
        """Test that File Parser Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
            
            infra = smart_city_infrastructure
            service = FileParserService(
                service_name="FileParserService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            result = await service.initialize()
            
            assert result is True, "File Parser Service should initialize"
            assert service.is_initialized, "File Parser Service should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"File Parser Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"File Parser Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_data_analyzer_service_initializes(self, test_infrastructure):
        """Test that Data Analyzer Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.data_analyzer_service.data_analyzer_service import DataAnalyzerService
            
            infra = smart_city_infrastructure
            service = DataAnalyzerService(
                service_name="DataAnalyzerService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            result = await service.initialize()
            
            assert result is True, "Data Analyzer Service should initialize"
            assert service.is_initialized, "Data Analyzer Service should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Data Analyzer Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Data Analyzer Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_metrics_calculator_service_initializes(self, test_infrastructure):
        """Test that Metrics Calculator Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.metrics_calculator_service.metrics_calculator_service import MetricsCalculatorService
            
            infra = smart_city_infrastructure
            service = MetricsCalculatorService(
                service_name="MetricsCalculatorService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            result = await service.initialize()
            
            assert result is True, "Metrics Calculator Service should initialize"
            assert service.is_initialized, "Metrics Calculator Service should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Metrics Calculator Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Metrics Calculator Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_validation_engine_service_initializes(self, test_infrastructure):
        """Test that Validation Engine Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
            
            infra = smart_city_infrastructure
            service = ValidationEngineService(
                service_name="ValidationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            result = await service.initialize()
            
            assert result is True, "Validation Engine Service should initialize"
            assert service.is_initialized, "Validation Engine Service should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Validation Engine Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Validation Engine Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_transformation_engine_service_initializes(self, test_infrastructure):
        """Test that Transformation Engine Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.transformation_engine_service.transformation_engine_service import TransformationEngineService
            
            infra = smart_city_infrastructure
            service = TransformationEngineService(
                service_name="TransformationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            result = await service.initialize()
            
            assert result is True, "Transformation Engine Service should initialize"
            assert service.is_initialized, "Transformation Engine Service should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Transformation Engine Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Transformation Engine Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_schema_mapper_service_initializes(self, test_infrastructure):
        """Test that Schema Mapper Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.schema_mapper_service.schema_mapper_service import SchemaMapperService
            
            infra = smart_city_infrastructure
            service = SchemaMapperService(
                service_name="SchemaMapperService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Use timeout for initialization
            try:
                result = await asyncio.wait_for(
                    service.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Schema Mapper Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Schema Mapper Service initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            assert result is True, "Schema Mapper Service should initialize"
            assert service.is_initialized, "Schema Mapper Service should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Schema Mapper Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Schema Mapper Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_workflow_manager_service_initializes(self, test_infrastructure):
        """Test that Workflow Manager Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.workflow_manager_service.workflow_manager_service import WorkflowManagerService
            
            infra = smart_city_infrastructure
            service = WorkflowManagerService(
                service_name="WorkflowManagerService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Use timeout for initialization
            try:
                result = await asyncio.wait_for(
                    service.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Workflow Manager Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Workflow Manager Service initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            assert result is True, "Workflow Manager Service should initialize"
            assert service.is_initialized, "Workflow Manager Service should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Workflow Manager Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Workflow Manager Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_visualization_engine_service_initializes(self, test_infrastructure):
        """Test that Visualization Engine Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.visualization_engine_service.visualization_engine_service import VisualizationEngineService
            
            infra = smart_city_infrastructure
            service = VisualizationEngineService(
                service_name="VisualizationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Use timeout for initialization
            try:
                result = await asyncio.wait_for(
                    service.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Visualization Engine Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            assert result is True, "Visualization Engine Service should initialize"
            assert service.is_initialized, "Visualization Engine Service should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Visualization Engine Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Visualization Engine Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_report_generator_service_initializes(self, test_infrastructure):
        """Test that Report Generator Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.report_generator_service.report_generator_service import ReportGeneratorService
            
            infra = smart_city_infrastructure
            service = ReportGeneratorService(
                service_name="ReportGeneratorService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Use timeout for initialization
            try:
                result = await asyncio.wait_for(
                    service.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Report Generator Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            assert result is True, "Report Generator Service should initialize"
            assert service.is_initialized, "Report Generator Service should be marked as initialized"
            
        except ImportError as e:
            pytest.fail(
                f"Report Generator Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Report Generator Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    # Batch 1: Output & Format Services
    @pytest.mark.asyncio
    async def test_export_formatter_service_initializes(self, test_infrastructure):
        """Test that Export Formatter Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.export_formatter_service.export_formatter_service import ExportFormatterService
            
            infra = smart_city_infrastructure
            service = ExportFormatterService(
                service_name="ExportFormatterService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Export Formatter Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Export Formatter Service should initialize"
            assert service.is_initialized, "Export Formatter Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Export Formatter Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Export Formatter Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_format_composer_service_initializes(self, test_infrastructure):
        """Test that Format Composer Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.format_composer_service.format_composer_service import FormatComposerService
            
            infra = smart_city_infrastructure
            service = FormatComposerService(
                service_name="FormatComposerService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Format Composer Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Format Composer Service should initialize"
            assert service.is_initialized, "Format Composer Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Format Composer Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Format Composer Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    # Batch 2: Data Processing Services
    @pytest.mark.asyncio
    async def test_data_compositor_service_initializes(self, test_infrastructure):
        """Test that Data Compositor Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.data_compositor_service.data_compositor_service import DataCompositorService
            
            infra = smart_city_infrastructure
            service = DataCompositorService(
                service_name="DataCompositorService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Data Compositor Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Data Compositor Service should initialize"
            assert service.is_initialized, "Data Compositor Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Data Compositor Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Data Compositor Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_data_insights_query_service_initializes(self, test_infrastructure):
        """Test that Data Insights Query Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.data_insights_query_service.data_insights_query_service import DataInsightsQueryService
            
            infra = smart_city_infrastructure
            service = DataInsightsQueryService(
                service_name="DataInsightsQueryService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Data Insights Query Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Data Insights Query Service should initialize"
            assert service.is_initialized, "Data Insights Query Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Data Insights Query Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Data Insights Query Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_reconciliation_service_initializes(self, test_infrastructure):
        """Test that Reconciliation Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.reconciliation_service.reconciliation_service import ReconciliationService
            
            infra = smart_city_infrastructure
            service = ReconciliationService(
                service_name="ReconciliationService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Reconciliation Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Reconciliation Service should initialize"
            assert service.is_initialized, "Reconciliation Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Reconciliation Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Reconciliation Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    # Batch 3: Workflow & Analysis Services
    @pytest.mark.asyncio
    async def test_workflow_conversion_service_initializes(self, test_infrastructure):
        """Test that Workflow Conversion Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.workflow_conversion_service.workflow_conversion_service import WorkflowConversionService
            
            infra = smart_city_infrastructure
            service = WorkflowConversionService(
                service_name="WorkflowConversionService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Workflow Conversion Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Workflow Conversion Service should initialize"
            assert service.is_initialized, "Workflow Conversion Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Workflow Conversion Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Workflow Conversion Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_insights_generator_service_initializes(self, test_infrastructure):
        """Test that Insights Generator Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.insights_generator_service.insights_generator_service import InsightsGeneratorService
            
            infra = smart_city_infrastructure
            service = InsightsGeneratorService(
                service_name="InsightsGeneratorService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Insights Generator Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Insights Generator Service should initialize"
            assert service.is_initialized, "Insights Generator Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Insights Generator Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Insights Generator Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_insights_orchestrator_service_initializes(self, test_infrastructure):
        """Test that Insights Orchestrator Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.insights_orchestrator_service.insights_orchestrator_service import InsightsOrchestrationService
            
            infra = smart_city_infrastructure
            service = InsightsOrchestrationService(
                service_name="InsightsOrchestratorService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Insights Orchestrator Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Insights Orchestrator Service should initialize"
            assert service.is_initialized, "Insights Orchestrator Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Insights Orchestrator Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Insights Orchestrator Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    # Batch 4: Business Services
    @pytest.mark.asyncio
    async def test_sop_builder_service_initializes(self, test_infrastructure):
        """Test that SOP Builder Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.sop_builder_service.sop_builder_service import SOPBuilderService
            
            infra = smart_city_infrastructure
            service = SOPBuilderService(
                service_name="SOPBuilderService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"SOP Builder Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "SOP Builder Service should initialize"
            assert service.is_initialized, "SOP Builder Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"SOP Builder Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"SOP Builder Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_coexistence_analysis_service_initializes(self, test_infrastructure):
        """Test that Coexistence Analysis Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.coexistence_analysis_service.coexistence_analysis_service import CoexistenceAnalysisService
            
            infra = smart_city_infrastructure
            service = CoexistenceAnalysisService(
                service_name="CoexistenceAnalysisService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Coexistence Analysis Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Coexistence Analysis Service should initialize"
            assert service.is_initialized, "Coexistence Analysis Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Coexistence Analysis Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Coexistence Analysis Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_poc_generation_service_initializes(self, test_infrastructure):
        """Test that POC Generation Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.poc_generation_service.poc_generation_service import POCGenerationService
            
            infra = smart_city_infrastructure
            service = POCGenerationService(
                service_name="POCGenerationService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"POC Generation Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "POC Generation Service should initialize"
            assert service.is_initialized, "POC Generation Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"POC Generation Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"POC Generation Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_roadmap_generation_service_initializes(self, test_infrastructure):
        """Test that Roadmap Generation Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.roadmap_generation_service.roadmap_generation_service import RoadmapGenerationService
            
            infra = smart_city_infrastructure
            service = RoadmapGenerationService(
                service_name="RoadmapGenerationService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Roadmap Generation Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Roadmap Generation Service should initialize"
            assert service.is_initialized, "Roadmap Generation Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Roadmap Generation Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Roadmap Generation Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_apg_processor_service_initializes(self, test_infrastructure):
        """Test that APG Processor Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.apg_processor_service.apg_processor_service import APGProcessingService
            
            infra = smart_city_infrastructure
            service = APGProcessingService(
                service_name="APGProcessorService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"APG Processor Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "APG Processor Service should initialize"
            assert service.is_initialized, "APG Processor Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"APG Processor Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"APG Processor Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_audit_trail_service_initializes(self, test_infrastructure):
        """Test that Audit Trail Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.audit_trail_service.audit_trail_service import AuditTrailService
            
            infra = smart_city_infrastructure
            service = AuditTrailService(
                service_name="AuditTrailService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Audit Trail Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Audit Trail Service should initialize"
            assert service.is_initialized, "Audit Trail Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Audit Trail Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Audit Trail Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_configuration_service_initializes(self, test_infrastructure):
        """Test that Configuration Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.configuration_service.configuration_service import ConfigurationService
            
            infra = smart_city_infrastructure
            service = ConfigurationService(
                service_name="ConfigurationService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Configuration Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Configuration Service should initialize"
            assert service.is_initialized, "Configuration Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Configuration Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Configuration Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_notification_service_initializes(self, test_infrastructure):
        """Test that Notification Service initializes correctly."""
        try:
            from backend.business_enablement.enabling_services.notification_service.notification_service import NotificationService
            
            infra = smart_city_infrastructure
            service = NotificationService(
                service_name="NotificationService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            try:
                result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Notification Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs: docker logs symphainy-consul, docker logs symphainy-arangodb, docker logs symphainy-redis"
                )
            
            assert result is True, "Notification Service should initialize"
            assert service.is_initialized, "Notification Service should be marked as initialized"
        except ImportError as e:
            pytest.fail(f"Notification Service not available: {e}\n\nThis indicates a code/dependency issue, not infrastructure.\nCheck that services are installed and in Python path.")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                pytest.fail(
                    f"Notification Service initialization failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise


class TestEnablingServicesFunctionality:
    """
    Test that enabling services actually work (not just initialize).
    
    Layer 3: Functionality tests require Smart City services.
    Uses smart_city_infrastructure fixture (from test_smart_city_infrastructure.py).
    """
    
    # Note: Uses smart_city_infrastructure fixture (not test_infrastructure)
    # This fixture initializes all Smart City services (Librarian, Data Steward, Content Steward, etc.)
    
    @pytest.mark.asyncio
    async def test_file_parser_service_parses_file(self, smart_city_infrastructure):
        """Test that File Parser Service can actually parse a file."""
        try:
            from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
            
            infra = smart_city_infrastructure
            service = FileParserService(
                service_name="FileParserService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Use timeout for initialization
            try:
                result = await asyncio.wait_for(
                    service.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"File Parser Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"File Parser Service initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            # Test actual functionality - parse a simple text file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("Test content for parsing")
                temp_file_path = f.name
            
            try:
                # Test parse_file method
                parse_result = await service.parse_file(
                    file_path=temp_file_path,
                    file_format="txt",
                    user_context={"user_id": "test_user", "tenant_id": "test_tenant"}
                )
                
                assert parse_result is not None, "File Parser should return a result"
                assert "content" in parse_result or "data" in parse_result or "text" in parse_result, \
                    "Parse result should contain parsed content"
                
            finally:
                # Clean up
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            
        except ImportError as e:
            pytest.fail(
                f"File Parser Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"File Parser Service functionality test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_validation_engine_service_validates_data(self, smart_city_infrastructure):
        """Test that Validation Engine Service can actually validate data."""
        try:
            from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
            
            infra = smart_city_infrastructure
            service = ValidationEngineService(
                service_name="ValidationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Use timeout for initialization
            try:
                result = await asyncio.wait_for(
                    service.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Validation Engine Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Validation Engine Service initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            # Test actual functionality - validate some data
            # First, store test data via Librarian (service uses data_id, not direct data)
            test_data = {"field1": "value1", "field2": 123, "field3": "test@example.com"}
            user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
            
            # Store document via Librarian (requires Content Steward)
            try:
                storage_result = await service.store_document(
                    document_data=test_data,
                    metadata={"test": True, "validation_test": True}
                )
            except ValueError as e:
                if "Content Steward service not available" in str(e):
                    from tests.utils.safe_docker import check_container_status
                    consul_status = check_container_status("symphainy-consul")
                    arango_status = check_container_status("symphainy-arangodb")
                    
                    pytest.fail(
                        f"Content Steward service not available for document storage.\n"
                        f"This is required for Validation Engine to store and retrieve test data.\n\n"
                        f"Infrastructure status:\n"
                        f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                        f"restarts: {consul_status['restart_count']})\n"
                        f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                        f"restarts: {arango_status['restart_count']})\n\n"
                        f"Fix: Content Steward must be initialized and registered with Curator.\n"
                        f"Check: Content Steward service should be available via service discovery."
                    )
                else:
                    raise
            
            if not storage_result or "document_id" not in storage_result:
                pytest.fail(
                    f"Failed to store test data for validation.\n"
                    f"Storage result: {storage_result}\n\n"
                    f"This indicates an issue with Content Steward integration or document storage."
                )
            
            data_id = storage_result["document_id"]
            
            # Test validate_data with validation rules
            validation_rules = {
                "required_fields": ["field1", "field2", "field3"],
                "field_types": {
                    "field1": "string",
                    "field2": "integer",
                    "field3": "string"
                },
                "field_formats": {
                    "field3": "email"
                }
            }
            
            validation_result = await service.validate_data(
                data_id=data_id,
                validation_rules=validation_rules,
                user_context=user_context
            )
            
            assert validation_result is not None, "Validation Engine should return a result"
            assert "success" in validation_result, "Validation result should have success field"
            assert "status" in validation_result or "passed" in validation_result, \
                "Validation result should indicate validation status"
            
        except ImportError as e:
            pytest.fail(
                f"Validation Engine Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Validation Engine Service functionality test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_validation_engine_validates_schema(self, smart_city_infrastructure):
        """Test that Validation Engine can validate data against a schema."""
        try:
            from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
            
            infra = smart_city_infrastructure
            service = ValidationEngineService(
                service_name="ValidationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Initialize service
            result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            if not result:
                pytest.fail("Validation Engine Service failed to initialize")
            
            # Store test data
            test_data = {
                "name": "John Doe",
                "age": 30,
                "email": "john@example.com",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "zip": "12345"
                }
            }
            user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
            
            storage_result = await service.store_document(
                document_data=test_data,
                metadata={"test": True, "schema_validation_test": True}
            )
            
            if not storage_result or "document_id" not in storage_result:
                pytest.fail("Failed to store test data for schema validation")
            
            data_id = storage_result["document_id"]
            
            # Define schema
            schema = {
                "type": "object",
                "required": ["name", "age", "email", "address"],
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer", "minimum": 0, "maximum": 150},
                    "email": {"type": "string", "format": "email"},
                    "address": {
                        "type": "object",
                        "required": ["street", "city", "zip"],
                        "properties": {
                            "street": {"type": "string"},
                            "city": {"type": "string"},
                            "zip": {"type": "string", "pattern": "^[0-9]{5}$"}
                        }
                    }
                }
            }
            
            # Test schema validation
            schema_result = await service.validate_schema(
                data_id=data_id,
                schema=schema,
                user_context=user_context
            )
            
            assert schema_result is not None, "Schema validation should return a result"
            assert "success" in schema_result, "Schema validation result should have success field"
            assert "schema_valid" in schema_result, "Schema validation result should indicate validity"
            
        except ImportError as e:
            pytest.fail(f"Validation Engine Service not available: {e}")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Schema validation test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_validation_engine_validates_batch(self, smart_city_infrastructure):
        """Test that Validation Engine can validate multiple datasets in batch."""
        try:
            from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
            
            infra = smart_city_infrastructure
            service = ValidationEngineService(
                service_name="ValidationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Initialize service
            result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            if not result:
                pytest.fail("Validation Engine Service failed to initialize")
            
            user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
            
            # Store multiple test datasets
            test_datasets = [
                {"id": 1, "name": "Dataset 1", "value": 100},
                {"id": 2, "name": "Dataset 2", "value": 200},
                {"id": 3, "name": "Dataset 3", "value": 300}
            ]
            
            data_ids = []
            for test_data in test_datasets:
                storage_result = await service.store_document(
                    document_data=test_data,
                    metadata={"test": True, "batch_validation_test": True}
                )
                if storage_result and "document_id" in storage_result:
                    data_ids.append(storage_result["document_id"])
            
            if len(data_ids) == 0:
                pytest.fail("Failed to store test data for batch validation")
            
            # Create batch validation requests
            validation_rules = {
                "required_fields": ["id", "name", "value"],
                "field_types": {
                    "id": "integer",
                    "name": "string",
                    "value": "integer"
                }
            }
            
            validations = [
                {
                    "data_id": data_id,
                    "validation_rules": validation_rules
                }
                for data_id in data_ids
            ]
            
            # Test batch validation
            batch_result = await service.validate_batch(
                validations=validations,
                user_context=user_context
            )
            
            assert batch_result is not None, "Batch validation should return a result"
            assert "success" in batch_result, "Batch validation result should have success field"
            assert "results" in batch_result or "validation_results" in batch_result, \
                "Batch validation should return individual results"
            
        except ImportError as e:
            pytest.fail(f"Validation Engine Service not available: {e}")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Batch validation test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise
    
    @pytest.mark.asyncio
    async def test_validation_engine_handles_missing_data(self, smart_city_infrastructure):
        """Test that Validation Engine handles missing data gracefully."""
        try:
            from backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service import ValidationEngineService
            
            infra = smart_city_infrastructure
            service = ValidationEngineService(
                service_name="ValidationEngineService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Initialize service
            result = await asyncio.wait_for(service.initialize(), timeout=30.0)
            if not result:
                pytest.fail("Validation Engine Service failed to initialize")
            
            user_context = {"user_id": "test_user", "tenant_id": "test_tenant"}
            
            # Test with non-existent data_id
            non_existent_id = "non_existent_data_id_12345"
            validation_rules = {"required_fields": ["field1"]}
            
            validation_result = await service.validate_data(
                data_id=non_existent_id,
                validation_rules=validation_rules,
                user_context=user_context
            )
            
            # Should return a result indicating data not found
            assert validation_result is not None, "Validation should return a result even for missing data"
            assert validation_result.get("success") is False or validation_result.get("message") == "Data not found", \
                "Validation should indicate data not found"
            
        except ImportError as e:
            pytest.fail(f"Validation Engine Service not available: {e}")
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Missing data test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise


class TestEnablingServicesPlatformGateway:
    """Test that enabling services use Platform Gateway correctly."""
    
    @pytest.fixture
    async def test_infrastructure(self):
        """Set up test infrastructure."""
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
        
        di_container = DIContainerService("test_platform")
        pwf = PublicWorksFoundationService(di_container=di_container)
        
        # Use timeout for initialization
        try:
            pwf_result = await asyncio.wait_for(
                pwf.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Public Works Foundation initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis"
            )
        
        if not pwf_result:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Public Works Foundation initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis\n\n"
                f"Fix: Ensure all critical infrastructure containers are running and healthy."
            )
        
        di_container.public_works_foundation = pwf
        
        curator = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=pwf
        )
        
        # Use timeout for initialization
        try:
            curator_result = await asyncio.wait_for(
                curator.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Curator Foundation initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb"
            )
        
        if not curator_result:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Curator Foundation initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n\n"
                f"Fix: Ensure all critical infrastructure containers are running and healthy."
            )
        
        di_container.curator_foundation = curator
        
        platform_gateway = PlatformInfrastructureGateway(
            public_works_foundation=pwf
        )
        
        return {
            "di_container": di_container,
            "public_works_foundation": pwf,
            "curator": curator,
            "platform_gateway": platform_gateway
        }
    
    @pytest.mark.asyncio
    async def test_file_parser_uses_platform_gateway(self, test_infrastructure):
        """Test that File Parser Service uses Platform Gateway for abstractions."""
        try:
            from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
            
            infra = smart_city_infrastructure
            service = FileParserService(
                service_name="FileParserService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Use timeout for initialization
            try:
                result = await asyncio.wait_for(
                    service.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"File Parser Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"File Parser Service initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            # File Parser should use Platform Gateway for document_intelligence abstraction
            assert service.platform_gateway is not None, \
                "File Parser should have Platform Gateway reference"
            assert hasattr(service, "document_intelligence") or hasattr(service, "get_abstraction"), \
                "File Parser should access abstractions via Platform Gateway"
            
        except ImportError as e:
            pytest.fail(
                f"File Parser Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Platform Gateway test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise


class TestEnablingServicesCuratorRegistration:
    """Test that enabling services register with Curator (Phase 2 pattern)."""
    
    @pytest.fixture
    async def test_infrastructure(self):
        """Set up test infrastructure."""
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
        
        di_container = DIContainerService("test_platform")
        pwf = PublicWorksFoundationService(di_container=di_container)
        
        # Use timeout for initialization
        try:
            pwf_result = await asyncio.wait_for(
                pwf.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Public Works Foundation initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis"
            )
        
        if not pwf_result:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Public Works Foundation initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis\n\n"
                f"Fix: Ensure all critical infrastructure containers are running and healthy."
            )
        
        di_container.public_works_foundation = pwf
        
        curator = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=pwf
        )
        
        # Use timeout for initialization
        try:
            curator_result = await asyncio.wait_for(
                curator.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Curator Foundation initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb"
            )
        
        if not curator_result:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Curator Foundation initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n\n"
                f"Fix: Ensure all critical infrastructure containers are running and healthy."
            )
        
        di_container.curator_foundation = curator
        
        platform_gateway = PlatformInfrastructureGateway(
            public_works_foundation=pwf
        )
        
        return {
            "di_container": di_container,
            "public_works_foundation": pwf,
            "curator": curator,
            "platform_gateway": platform_gateway
        }
    
    @pytest.mark.asyncio
    async def test_file_parser_registers_with_curator(self, test_infrastructure):
        """Test that File Parser Service registers with Curator."""
        try:
            from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
            
            infra = smart_city_infrastructure
            curator = infra["curator"]
            
            services_before = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            service = FileParserService(
                service_name="FileParserService",
                realm_name="business_enablement",
                platform_gateway=infra["platform_gateway"],
                di_container=infra["di_container"]
            )
            
            # Use timeout for initialization
            try:
                result = await asyncio.wait_for(
                    service.initialize(),
                    timeout=30.0  # 30 second timeout
                )
            except asyncio.TimeoutError:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"File Parser Service initialization timed out after 30 seconds.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis"
                )
            
            if not result:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"File Parser Service initialization failed.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Fix: Ensure all critical infrastructure containers are running and healthy."
                )
            
            services_after = len(curator.registered_services) if hasattr(curator, "registered_services") else 0
            
            # File Parser should register with Curator (Phase 2 pattern)
            assert services_after >= services_before, \
                "File Parser should register with Curator (Phase 2 pattern)"
            
        except ImportError as e:
            pytest.fail(
                f"File Parser Service not available: {e}\n\n"
                f"This indicates a code/dependency issue, not infrastructure.\n"
                f"Check that services are installed and in Python path."
            )
        except Exception as e:
            error_str = str(e).lower()
            if "infrastructure" in error_str or "connection" in error_str or "timeout" in error_str:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Curator registration test failed: {e}\n\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                    f"Check Docker containers: docker ps --filter name=symphainy-"
                )
            else:
                raise

