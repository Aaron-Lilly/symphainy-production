#!/usr/bin/env python3
"""
Composition Service Initialization Tests

Tests to verify key composition services initialize correctly:
- SecurityCompositionService
- SessionCompositionService
- StateCompositionService
- PostOfficeCompositionService
- ConductorCompositionService
- PolicyCompositionService
"""

import pytest
import inspect
from foundations.public_works_foundation.composition_services.security_composition_service import SecurityCompositionService
from foundations.public_works_foundation.composition_services.session_composition_service import SessionCompositionService
from foundations.public_works_foundation.composition_services.state_composition_service import StateCompositionService
from foundations.public_works_foundation.composition_services.post_office_composition_service import PostOfficeCompositionService
from foundations.public_works_foundation.composition_services.conductor_composition_service import ConductorCompositionService
from foundations.public_works_foundation.composition_services.policy_composition_service import PolicyCompositionService


class TestCompositionServiceInitialization:
    """Test composition service initialization."""
    
    def test_security_composition_service_initializes(self):
        """Test that SecurityCompositionService initializes successfully."""
        service = SecurityCompositionService()
        assert service is not None
        assert hasattr(service, 'service_name')
        assert hasattr(service, 'is_initialized')
        assert hasattr(service, 'initialize')
        assert callable(service.initialize)
    
    def test_session_composition_service_initializes(self):
        """Test that SessionCompositionService initializes successfully."""
        # SessionCompositionService requires session_abstraction parameter
        class MockSessionAbstraction:
            pass
        service = SessionCompositionService(session_abstraction=MockSessionAbstraction())
        assert service is not None
        assert hasattr(service, 'service_name')
        assert hasattr(service, 'logger')
    
    def test_state_composition_service_initializes(self):
        """Test that StateCompositionService initializes successfully."""
        # StateCompositionService requires state_management parameter
        class MockStateManagement:
            pass
        service = StateCompositionService(state_management=MockStateManagement())
        assert service is not None
        assert hasattr(service, 'state_management')
        assert hasattr(service, 'logger')
    
    def test_post_office_composition_service_initializes(self):
        """Test that PostOfficeCompositionService initializes successfully."""
        # PostOfficeCompositionService requires event_management and messaging parameters
        class MockEventManagement:
            pass
        class MockMessaging:
            pass
        service = PostOfficeCompositionService(
            event_management=MockEventManagement(),
            messaging=MockMessaging()
        )
        assert service is not None
        assert hasattr(service, 'event_management')
        assert hasattr(service, 'messaging')
        assert hasattr(service, 'logger')
    
    def test_conductor_composition_service_initializes(self):
        """Test that ConductorCompositionService initializes successfully."""
        # ConductorCompositionService requires multiple abstraction parameters
        class MockTaskManagement:
            pass
        class MockWorkflowOrchestration:
            pass
        class MockResourceAllocation:
            pass
        service = ConductorCompositionService(
            task_management_abstraction=MockTaskManagement(),
            workflow_orchestration_abstraction=MockWorkflowOrchestration(),
            resource_allocation_abstraction=MockResourceAllocation()
        )
        assert service is not None
        assert hasattr(service, 'is_initialized')
        assert hasattr(service, 'logger')
    
    def test_policy_composition_service_initializes(self):
        """Test that PolicyCompositionService initializes successfully."""
        # PolicyCompositionService requires policy_abstraction parameter
        class MockPolicyAbstraction:
            pass
        service = PolicyCompositionService(policy_abstraction=MockPolicyAbstraction())
        assert service is not None
        assert hasattr(service, 'service_name')
        assert hasattr(service, 'logger')
    
    def test_composition_services_receive_required_abstractions(self):
        """Test that composition services have methods to receive abstractions."""
        # SecurityCompositionService requires auth, authorization, session, tenant, policy
        security_service = SecurityCompositionService()
        assert hasattr(security_service, 'initialize')
        # The initialize method should accept abstractions as parameters
        sig = inspect.signature(security_service.initialize)
        assert len(sig.parameters) > 0  # Should accept abstraction parameters
    
    def test_composition_services_are_accessible_via_foundation(self):
        """Test that composition services can be accessed via foundation structure."""
        # This is a structure test - verify foundation has composition service attributes
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.di_container.di_container_service import DIContainerService
        
        di_container = DIContainerService("test")
        foundation = PublicWorksFoundationService(di_container=di_container)
        
        # Foundation should have composition service attributes
        assert hasattr(foundation, 'composition_service') or hasattr(foundation, 'security_composition_service')
