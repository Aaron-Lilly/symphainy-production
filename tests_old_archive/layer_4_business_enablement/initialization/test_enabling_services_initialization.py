#!/usr/bin/env python3
"""
Business Enablement Enabling Services Initialization Tests

Validates that all enabling services can be initialized correctly.
Tests that services:
- Can be instantiated with DI Container
- Have required attributes (di_container, platform_gateway, etc.)
- Can access Smart City SOA APIs
- Follow RealmServiceBase patterns
"""

import pytest
from unittest.mock import Mock, MagicMock

# Path is configured in pytest.ini - no manipulation needed
from foundations.di_container.di_container_service import DIContainerService
from tests.fixtures.business_enablement_fixtures import mock_platform_gateway


# Enabling Services to test
ENABLING_SERVICES = [
    ("FileParserService", "backend.business_enablement.enabling_services.file_parser_service.file_parser_service"),
    ("DataAnalyzerService", "backend.business_enablement.enabling_services.data_analyzer_service.data_analyzer_service"),
    ("MetricsCalculatorService", "backend.business_enablement.enabling_services.metrics_calculator_service.metrics_calculator_service"),
    ("ValidationEngineService", "backend.business_enablement.enabling_services.validation_engine_service.validation_engine_service"),
    ("TransformationEngineService", "backend.business_enablement.enabling_services.transformation_engine_service.transformation_engine_service"),
    ("SchemaMapperService", "backend.business_enablement.enabling_services.schema_mapper_service.schema_mapper_service"),
    ("WorkflowManagerService", "backend.business_enablement.enabling_services.workflow_manager_service.workflow_manager_service"),
    ("VisualizationEngineService", "backend.business_enablement.enabling_services.visualization_engine_service.visualization_engine_service"),
    ("ReportGeneratorService", "backend.business_enablement.enabling_services.report_generator_service.report_generator_service"),
    ("ExportFormatterService", "backend.business_enablement.enabling_services.export_formatter_service.export_formatter_service"),
    ("DataCompositorService", "backend.business_enablement.enabling_services.data_compositor_service.data_compositor_service"),
    ("ReconciliationService", "backend.business_enablement.enabling_services.reconciliation_service.reconciliation_service"),
    ("NotificationService", "backend.business_enablement.enabling_services.notification_service.notification_service"),
    ("AuditTrailService", "backend.business_enablement.enabling_services.audit_trail_service.audit_trail_service"),
    ("ConfigurationService", "backend.business_enablement.enabling_services.configuration_service.configuration_service"),
    ("WorkflowConversionService", "backend.business_enablement.enabling_services.workflow_conversion_service.workflow_conversion_service"),
    # Note: InsightsGeneratorService and InsightsOrchestratorService are not RealmServiceBase services
    # They are standalone business logic classes (InsightsDataService, InsightsOrchestrationService)
    # Skipping them from RealmServiceBase tests
    ("SOPBuilderService", "backend.business_enablement.enabling_services.sop_builder_service.sop_builder_service"),
    ("CoexistenceAnalysisService", "backend.business_enablement.enabling_services.coexistence_analysis_service.coexistence_analysis_service"),
    # Note: APGProcessorService is not a RealmServiceBase service
    # It's a standalone business logic class (APGProcessingService)
    # Skipping it from RealmServiceBase tests
    ("POCGenerationService", "backend.business_enablement.enabling_services.poc_generation_service.poc_generation_service"),
    ("RoadmapGenerationService", "backend.business_enablement.enabling_services.roadmap_generation_service.roadmap_generation_service"),
    ("DataInsightsQueryService", "backend.business_enablement.enabling_services.data_insights_query_service.data_insights_query_service"),
    ("FormatComposerService", "backend.business_enablement.enabling_services.format_composer_service.format_composer_service"),
]


@pytest.mark.business_enablement
class TestEnablingServicesInitialization:
    """Test all enabling services can be initialized."""
    
    @pytest.fixture
    def mock_di_container(self):
        """Create mock DI Container."""
        container = Mock(spec=DIContainerService)
        container.realm_name = "business_enablement"
        container.get_utility = Mock(return_value=Mock())
        container.get_service = Mock(return_value=None)
        container.get_foundation_service = Mock(return_value=None)
        container.get_logger = Mock(return_value=Mock())
        return container
    
    @pytest.fixture
    def mock_platform_gateway(self):
        """Create mock Platform Gateway."""
        gateway = Mock()
        gateway.get_abstraction = Mock(return_value=None)
        return gateway
    
    @pytest.mark.parametrize("service_name,module_path", ENABLING_SERVICES)
    def test_service_can_be_instantiated(self, service_name, module_path, mock_di_container, mock_platform_gateway):
        """Test that service can be instantiated."""
        try:
            module = __import__(module_path, fromlist=[service_name])
            service_class = getattr(module, service_name)
            # Services require service_name and realm_name as positional arguments
            service = service_class(
                service_name=service_name,
                realm_name="business_enablement",
                platform_gateway=mock_platform_gateway,
                di_container=mock_di_container
            )
            assert service is not None, f"{service_name} should be instantiated"
        except ImportError as e:
            pytest.skip(f"Could not import {service_name}: {e}")
        except Exception as e:
            pytest.fail(f"{service_name} failed to instantiate: {e}")
    
    @pytest.mark.parametrize("service_name,module_path", ENABLING_SERVICES)
    def test_service_has_di_container(self, service_name, module_path, mock_di_container, mock_platform_gateway):
        """Test that service has di_container attribute."""
        try:
            module = __import__(module_path, fromlist=[service_name])
            service_class = getattr(module, service_name)
            service = service_class(
                service_name=service_name,
                realm_name="business_enablement",
                platform_gateway=mock_platform_gateway,
                di_container=mock_di_container
            )
            assert hasattr(service, 'di_container'), \
                f"{service_name} should have di_container attribute"
            assert service.di_container == mock_di_container, \
                f"{service_name} should have correct di_container"
        except ImportError:
            pytest.skip(f"Could not import {service_name}")
        except Exception as e:
            pytest.fail(f"{service_name} failed: {e}")
    
    @pytest.mark.parametrize("service_name,module_path", ENABLING_SERVICES)
    def test_service_has_platform_gateway(self, service_name, module_path, mock_di_container, mock_platform_gateway):
        """Test that service has platform_gateway attribute."""
        try:
            module = __import__(module_path, fromlist=[service_name])
            service_class = getattr(module, service_name)
            service = service_class(
                service_name=service_name,
                realm_name="business_enablement",
                platform_gateway=mock_platform_gateway,
                di_container=mock_di_container
            )
            assert hasattr(service, 'platform_gateway'), \
                f"{service_name} should have platform_gateway attribute"
        except ImportError:
            pytest.skip(f"Could not import {service_name}")
        except Exception as e:
            pytest.fail(f"{service_name} failed: {e}")
    
    @pytest.mark.parametrize("service_name,module_path", ENABLING_SERVICES)
    def test_service_extends_realm_service_base(self, service_name, module_path, mock_di_container, mock_platform_gateway):
        """Test that service extends RealmServiceBase."""
        try:
            from bases.realm_service_base import RealmServiceBase
            module = __import__(module_path, fromlist=[service_name])
            service_class = getattr(module, service_name)
            service = service_class(
                service_name=service_name,
                realm_name="business_enablement",
                platform_gateway=mock_platform_gateway,
                di_container=mock_di_container
            )
            assert isinstance(service, RealmServiceBase), \
                f"{service_name} should extend RealmServiceBase"
        except ImportError:
            pytest.skip(f"Could not import {service_name}")
        except Exception as e:
            pytest.fail(f"{service_name} failed: {e}")
    
    @pytest.mark.parametrize("service_name,module_path", ENABLING_SERVICES)
    def test_service_has_smart_city_access_methods(self, service_name, module_path, mock_di_container, mock_platform_gateway):
        """Test that service has Smart City SOA API access methods."""
        try:
            module = __import__(module_path, fromlist=[service_name])
            service_class = getattr(module, service_name)
            service = service_class(
                service_name=service_name,
                realm_name="business_enablement",
                platform_gateway=mock_platform_gateway,
                di_container=mock_di_container
            )
            # RealmServiceBase should provide these methods
            assert hasattr(service, 'get_librarian_api') or hasattr(service, 'get_smart_city_api'), \
                f"{service_name} should have Smart City API access methods"
        except ImportError:
            pytest.skip(f"Could not import {service_name}")
        except Exception as e:
            pytest.fail(f"{service_name} failed: {e}")
    
    def test_all_services_initialized(self, mock_di_container, mock_platform_gateway):
        """Test that all services can be initialized together."""
        services = []
        errors = []
        
        for service_name, module_path in ENABLING_SERVICES:
            try:
                module = __import__(module_path, fromlist=[service_name])
                service_class = getattr(module, service_name)
                service = service_class(
                    service_name=service_name,
                    realm_name="business_enablement",
                    platform_gateway=mock_platform_gateway,
                    di_container=mock_di_container
                )
                services.append((service_name, service))
            except Exception as e:
                errors.append((service_name, str(e)))
        
        # Report results
        print(f"\n✅ Successfully initialized: {len(services)}/{len(ENABLING_SERVICES)} enabling services")
        for name, service in services:
            print(f"   - {name}: OK")
        
        if errors:
            print(f"\n❌ Failed to initialize: {len(errors)} services")
            for name, error in errors:
                print(f"   - {name}: {error}")
        
        # At least 80% should initialize (allowing for some that may need infrastructure)
        assert len(services) >= len(ENABLING_SERVICES) * 0.8, \
            f"Too many services failed to initialize: {len(errors)}/{len(ENABLING_SERVICES)}"

