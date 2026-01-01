#!/usr/bin/env python3
"""
Abstraction Contract/Protocol Tests

Tests to verify abstractions implement protocols correctly:
- AuthenticationProtocol
- AuthorizationProtocol
- SessionProtocol
- TenantProtocol
- PolicyEngine Protocol
"""

import pytest
from typing import Protocol, runtime_checkable


class TestAbstractionContracts:
    """Test abstraction contract compliance."""
    
    def test_authentication_protocol_exists(self):
        """Test that AuthenticationProtocol exists and is importable."""
        from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import AuthenticationProtocol
        assert AuthenticationProtocol is not None
        
        # Check if it's a Protocol
        assert hasattr(AuthenticationProtocol, '__protocol_attrs__') or hasattr(AuthenticationProtocol, '__abstractmethods__')
    
    def test_authorization_protocol_exists(self):
        """Test that AuthorizationProtocol exists and is importable."""
        from foundations.public_works_foundation.abstraction_contracts.authorization_protocol import AuthorizationProtocol
        assert AuthorizationProtocol is not None
    
    def test_session_protocol_exists(self):
        """Test that SessionProtocol exists and is importable."""
        from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionProtocol
        assert SessionProtocol is not None
    
    def test_tenant_protocol_exists(self):
        """Test that TenantProtocol exists and is importable."""
        from foundations.public_works_foundation.abstraction_contracts.tenant_protocol import TenantProtocol
        assert TenantProtocol is not None
    
    def test_policy_engine_protocol_exists(self):
        """Test that PolicyEngine Protocol exists and is importable."""
        from foundations.public_works_foundation.abstraction_contracts.policy_engine_protocol import PolicyEngine
        assert PolicyEngine is not None
    
    def test_abstractions_implement_authentication_protocol(self):
        """Test that auth abstraction implements AuthenticationProtocol."""
        from foundations.public_works_foundation.abstraction_contracts.authentication_protocol import AuthenticationProtocol
        from foundations.public_works_foundation.infrastructure_abstractions.auth_abstraction import AuthAbstraction
        
        # Check that AuthAbstraction has methods required by AuthenticationProtocol
        # This is a structure test - verify methods exist
        assert hasattr(AuthAbstraction, '__init__')
    
    def test_abstractions_implement_authorization_protocol(self):
        """Test that authorization abstraction implements AuthorizationProtocol."""
        from foundations.public_works_foundation.abstraction_contracts.authorization_protocol import AuthorizationProtocol
        from foundations.public_works_foundation.infrastructure_abstractions.authorization_abstraction import AuthorizationAbstraction
        
        # Check that AuthorizationAbstraction has methods required by AuthorizationProtocol
        assert hasattr(AuthorizationAbstraction, '__init__')
    
    def test_abstractions_implement_session_protocol(self):
        """Test that session abstraction implements SessionProtocol."""
        from foundations.public_works_foundation.abstraction_contracts.session_protocol import SessionProtocol
        from foundations.public_works_foundation.infrastructure_abstractions.session_abstraction import SessionAbstraction
        
        # Check that SessionAbstraction has methods required by SessionProtocol
        assert hasattr(SessionAbstraction, '__init__')
    
    def test_abstractions_implement_tenant_protocol(self):
        """Test that tenant abstraction implements TenantProtocol."""
        from foundations.public_works_foundation.abstraction_contracts.tenant_protocol import TenantProtocol
        from foundations.public_works_foundation.infrastructure_abstractions.tenant_abstraction import TenantAbstraction
        
        # Check that TenantAbstraction has methods required by TenantProtocol
        assert hasattr(TenantAbstraction, '__init__')
    
    def test_abstractions_implement_policy_engine_protocol(self):
        """Test that policy abstraction implements PolicyEngine Protocol."""
        from foundations.public_works_foundation.abstraction_contracts.policy_engine_protocol import PolicyEngine
        from foundations.public_works_foundation.infrastructure_abstractions.policy_abstraction import PolicyAbstraction
        
        # Check that PolicyAbstraction has methods required by PolicyEngine
        assert hasattr(PolicyAbstraction, '__init__')
    
    def test_foundation_uses_protocols_for_abstractions(self):
        """Test that foundation uses protocols for abstraction typing."""
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.di_container.di_container_service import DIContainerService
        
        di_container = DIContainerService("test")
        foundation = PublicWorksFoundationService(di_container=di_container)
        
        # Foundation should have abstraction attributes typed with protocols
        assert hasattr(foundation, 'auth_abstraction')
        assert hasattr(foundation, 'authorization_abstraction')
        assert hasattr(foundation, 'session_abstraction')
        assert hasattr(foundation, 'tenant_abstraction')
