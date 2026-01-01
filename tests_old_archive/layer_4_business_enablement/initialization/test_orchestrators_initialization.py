#!/usr/bin/env python3
"""
Business Enablement Orchestrators Initialization Tests

Validates that all orchestrators can be initialized correctly.
Tests that orchestrators:
- Can be instantiated with DI Container
- Have required attributes
- Can coordinate agents and services
- Follow OrchestratorBase patterns
"""

import pytest

import os
from unittest.mock import Mock, MagicMock

from foundations.di_container.di_container_service import DIContainerService

# Orchestrators to test
ORCHESTRATORS = [
    ("ContentAnalysisOrchestrator", "backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.content_analysis_orchestrator.content_analysis_orchestrator"),
    ("InsightsOrchestrator", "backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.insights_orchestrator.insights_orchestrator"),
    ("OperationsOrchestrator", "backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.operations_orchestrator.operations_orchestrator"),
    ("BusinessOutcomesOrchestrator", "backend.business_enablement.delivery_manager.mvp_pillar_orchestrators.business_outcomes_orchestrator.business_outcomes_orchestrator"),
]

@pytest.mark.business_enablement
class TestOrchestratorsInitialization:
    """Test all orchestrators can be initialized."""
    
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
    
    @pytest.mark.parametrize("orchestrator_name,module_path", ORCHESTRATORS)
    def test_orchestrator_can_be_instantiated(self, orchestrator_name, module_path, mock_di_container, mock_platform_gateway):
        """Test that orchestrator can be instantiated."""
        try:
            # Create mock delivery manager (orchestrators require delivery_manager)
            mock_delivery_manager = Mock()
            mock_delivery_manager.realm_name = "business_enablement"
            mock_delivery_manager.platform_gateway = mock_platform_gateway
            mock_delivery_manager.di_container = mock_di_container
            mock_delivery_manager.logger = Mock()
            
            module = __import__(module_path, fromlist=[orchestrator_name])
            orchestrator_class = getattr(module, orchestrator_name)
            orchestrator = orchestrator_class(
                delivery_manager=mock_delivery_manager
            )
            assert orchestrator is not None, f"{orchestrator_name} should be instantiated"
        except ImportError as e:
            pytest.skip(f"Could not import {orchestrator_name}: {e}")
        except Exception as e:
            pytest.fail(f"{orchestrator_name} failed to instantiate: {e}")
    
    @pytest.mark.parametrize("orchestrator_name,module_path", ORCHESTRATORS)
    def test_orchestrator_has_di_container(self, orchestrator_name, module_path, mock_di_container, mock_platform_gateway):
        """Test that orchestrator has di_container attribute."""
        try:
            # Create mock delivery manager
            mock_delivery_manager = Mock()
            mock_delivery_manager.realm_name = "business_enablement"
            mock_delivery_manager.platform_gateway = mock_platform_gateway
            mock_delivery_manager.di_container = mock_di_container
            mock_delivery_manager.logger = Mock()
            
            module = __import__(module_path, fromlist=[orchestrator_name])
            orchestrator_class = getattr(module, orchestrator_name)
            orchestrator = orchestrator_class(
                delivery_manager=mock_delivery_manager
            )
            assert hasattr(orchestrator, 'di_container'), \
                f"{orchestrator_name} should have di_container attribute"
        except ImportError:
            pytest.skip(f"Could not import {orchestrator_name}")
        except Exception as e:
            pytest.fail(f"{orchestrator_name} failed: {e}")
    
    @pytest.mark.parametrize("orchestrator_name,module_path", ORCHESTRATORS)
    def test_orchestrator_extends_orchestrator_base(self, orchestrator_name, module_path, mock_di_container, mock_platform_gateway):
        """Test that orchestrator extends OrchestratorBase."""
        try:
            from bases.orchestrator_base import OrchestratorBase
            # Create mock delivery manager
            mock_delivery_manager = Mock()
            mock_delivery_manager.realm_name = "business_enablement"
            mock_delivery_manager.platform_gateway = mock_platform_gateway
            mock_delivery_manager.di_container = mock_di_container
            mock_delivery_manager.logger = Mock()
            
            module = __import__(module_path, fromlist=[orchestrator_name])
            orchestrator_class = getattr(module, orchestrator_name)
            orchestrator = orchestrator_class(
                delivery_manager=mock_delivery_manager
            )
            assert isinstance(orchestrator, OrchestratorBase), \
                f"{orchestrator_name} should extend OrchestratorBase"
        except ImportError:
            pytest.skip(f"Could not import {orchestrator_name}")
        except Exception as e:
            pytest.fail(f"{orchestrator_name} failed: {e}")
    
    def test_all_orchestrators_initialized(self, mock_di_container, mock_platform_gateway):
        """Test that all orchestrators can be initialized together."""
        orchestrators = []
        errors = []
        
        # Create mock delivery manager
        mock_delivery_manager = Mock()
        mock_delivery_manager.realm_name = "business_enablement"
        mock_delivery_manager.platform_gateway = mock_platform_gateway
        mock_delivery_manager.di_container = mock_di_container
        mock_delivery_manager.logger = Mock()
        
        for orchestrator_name, module_path in ORCHESTRATORS:
            try:
                module = __import__(module_path, fromlist=[orchestrator_name])
                orchestrator_class = getattr(module, orchestrator_name)
                orchestrator = orchestrator_class(
                    delivery_manager=mock_delivery_manager
                )
                orchestrators.append((orchestrator_name, orchestrator))
            except Exception as e:
                errors.append((orchestrator_name, str(e)))
        
        # Report results
        print(f"\n✅ Successfully initialized: {len(orchestrators)}/{len(ORCHESTRATORS)} orchestrators")
        for name, orchestrator in orchestrators:
            print(f"   - {name}: OK")
        
        if errors:
            print(f"\n❌ Failed to initialize: {len(errors)} orchestrators")
            for name, error in errors:
                print(f"   - {name}: {error}")
        
        assert len(orchestrators) == len(ORCHESTRATORS), \
            f"All orchestrators should initialize: {len(errors)} failed"

