#!/usr/bin/env python3
"""
Unit Tests: Public Works Foundation

Tests the new Public Works Foundation Service with proper DI container integration.
Validates business abstraction creation, mapping, and access.

WHAT (Test Role): I validate the Public Works Foundation Service
HOW (Test Implementation): I test business abstraction instantiation, dimension mapping, and access methods
"""

import pytest
import asyncio
import sys
import os
from pathlib import Path

# Add the platform directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../symphainy-platform'))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService


class TestPublicWorksFoundationService:
    """Test Public Works Foundation Service functionality."""
    
    @pytest.fixture
    def di_container(self):
        """Create a DI container for testing."""
        return DIContainerService("test_public_works")
    
    @pytest.fixture
    def public_works_service(self, di_container):
        """Create a Public Works Foundation Service for testing."""
        return PublicWorksFoundationService(di_container)
    
    def test_service_initialization(self, public_works_service):
        """Test service initializes correctly."""
        assert public_works_service is not None
        assert hasattr(public_works_service, 'di_container')
        assert hasattr(public_works_service, 'business_abstractions')
        assert hasattr(public_works_service, 'smart_city_abstractions')
        assert hasattr(public_works_service, 'business_enablement_abstractions')
        assert hasattr(public_works_service, 'experience_abstractions')
        assert hasattr(public_works_service, 'agentic_abstractions')
    
    def test_business_abstractions_created(self, public_works_service):
        """Test that business abstractions are created."""
        abstractions = public_works_service.business_abstractions
        assert len(abstractions) > 0
        
        # Check for core abstractions
        expected_abstractions = [
            'multi_tenancy', 'authentication', 'authorization',
            'content_processing', 'analytics', 'visualization',
            'agui', 'llm', 'event_routing', 'session_management',
            'security', 'business_intelligence', 'strategic_planning',
            'business_outcomes', 'cross_dimensional_orchestration',
            'platform_coordination'
        ]
        
        for abstraction_name in expected_abstractions:
            assert abstraction_name in abstractions, f"Missing abstraction: {abstraction_name}"
            assert abstractions[abstraction_name] is not None
    
    def test_mvp_abstractions_created(self, public_works_service):
        """Test that MVP business abstractions are created."""
        abstractions = public_works_service.business_abstractions
        
        # Check for MVP abstractions
        mvp_abstractions = [
            'cobol_processing', 'sop_processing', 
            'poc_generation', 'roadmap_generation',
            'coexistence_evaluation'
        ]
        
        for abstraction_name in mvp_abstractions:
            assert abstraction_name in abstractions, f"Missing MVP abstraction: {abstraction_name}"
            assert abstractions[abstraction_name] is not None
    
    def test_dimension_mappings(self, public_works_service):
        """Test dimension mappings are correct."""
        # Smart City should have all abstractions
        smart_city_abstractions = public_works_service.smart_city_abstractions
        assert len(smart_city_abstractions) > 0
        
        # Business Enablement should have pillar-specific abstractions
        business_enablement_abstractions = public_works_service.business_enablement_abstractions
        assert len(business_enablement_abstractions) > 0
        
        # Experience should have experience-specific abstractions
        experience_abstractions = public_works_service.experience_abstractions
        assert len(experience_abstractions) > 0
        
        # Agentic should have agentic abstractions + MVP abstractions
        agentic_abstractions = public_works_service.agentic_abstractions
        assert len(agentic_abstractions) > 0
        
        # Check that MVP abstractions are in agentic dimension
        mvp_in_agentic = [
            'cobol_processing', 'sop_processing', 
            'poc_generation', 'roadmap_generation',
            'coexistence_evaluation'
        ]
        for abstraction_name in mvp_in_agentic:
            assert abstraction_name in agentic_abstractions, f"MVP abstraction {abstraction_name} not in agentic dimension"
    
    def test_get_abstractions_for_dimension(self, public_works_service):
        """Test getting abstractions for specific dimensions."""
        # Test Smart City dimension
        smart_city = public_works_service.get_abstractions_for_dimension("smart_city")
        assert isinstance(smart_city, dict)
        assert len(smart_city) > 0
        
        # Test Business Enablement dimension
        business_enablement = public_works_service.get_abstractions_for_dimension("business_enablement")
        assert isinstance(business_enablement, dict)
        assert len(business_enablement) > 0
        
        # Test Experience dimension
        experience = public_works_service.get_abstractions_for_dimension("experience")
        assert isinstance(experience, dict)
        assert len(experience) > 0
        
        # Test Agentic dimension
        agentic = public_works_service.get_abstractions_for_dimension("agentic")
        assert isinstance(agentic, dict)
        assert len(agentic) > 0
    
    def test_get_agentic_abstractions(self, public_works_service):
        """Test getting agentic abstractions."""
        agentic_abstractions = public_works_service.get_agentic_abstractions()
        assert isinstance(agentic_abstractions, dict)
        assert len(agentic_abstractions) > 0
        
        # Should include core agentic abstractions
        core_agentic = ['mcp_client', 'mcp_protocol', 'tool_registry', 'agui', 'llm']
        for abstraction_name in core_agentic:
            assert abstraction_name in agentic_abstractions, f"Missing core agentic abstraction: {abstraction_name}"
        
        # Should include MVP abstractions
        mvp_abstractions = ['cobol_processing', 'sop_processing', 'poc_generation', 'roadmap_generation', 'coexistence_evaluation']
        for abstraction_name in mvp_abstractions:
            assert abstraction_name in agentic_abstractions, f"Missing MVP abstraction in agentic: {abstraction_name}"
    
    def test_get_health_status(self, public_works_service):
        """Test getting service health status."""
        health_status = public_works_service.get_health_status()
        assert isinstance(health_status, dict)
        assert 'status' in health_status
        assert 'service_name' in health_status
        assert 'initialization_time' in health_status
        assert 'business_abstractions_created' in health_status
