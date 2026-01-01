#!/usr/bin/env python3
"""
Tests for individual Curator Foundation services.

Tests the micro-services: CapabilityRegistryService, PatternValidationService,
AntiPatternDetectionService, and DocumentationGenerationService.
"""

import pytest
import pytest_asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from foundations.curator_foundation.services import (
    CapabilityRegistryService,
    PatternValidationService,
    AntiPatternDetectionService,
    DocumentationGenerationService
)
from foundations.curator_foundation.models import (
    CapabilityDefinition,
    PatternDefinition,
    AntiPatternViolation
)
from .test_base import CuratorFoundationTestBase


class TestCapabilityRegistryService(CuratorFoundationTestBase):
    """Test Capability Registry Service functionality."""
    
    @pytest.mark.asyncio
    async def test_capability_registry_initialization(self, mock_utility_foundation, mock_public_works_foundation):
        """Test capability registry service initialization."""
        service = CapabilityRegistryService(mock_utility_foundation, mock_public_works_foundation)
        
        assert service is not None
        assert service.service_name == "capability_registry"
        assert service.utility_foundation == mock_utility_foundation
        assert service.public_works_foundation == mock_public_works_foundation
        assert service.capability_registry is not None
        assert isinstance(service.capability_registry, dict)
    
    @pytest.mark.asyncio
    async def test_capability_registration(self, mock_utility_foundation, mock_public_works_foundation):
        """Test capability registration functionality."""
        service = CapabilityRegistryService(mock_utility_foundation, mock_public_works_foundation)
        
        # Create a test capability
        capability = CapabilityDefinition(
            name="test_capability",
            service_name="test_service",
            capability_type="data_processing",
            description="Test capability for data processing",
            version="1.0.0",
            endpoints=["/api/test"],
            dependencies=["database", "cache"],
            metadata={"test": True}
        )
        
        # Register the capability
        result = await service.register_capability(capability)
        
        assert result is not None
        assert "status" in result
        assert result["status"] == "success"
        assert "capability_id" in result
        
        # Verify capability is in registry
        assert capability.name in service.capability_registry
        registered_capability = service.capability_registry[capability.name]
        assert registered_capability.name == capability.name
        assert registered_capability.service_name == capability.service_name
    
    @pytest.mark.asyncio
    async def test_capability_discovery(self, mock_utility_foundation, mock_public_works_foundation):
        """Test capability discovery functionality."""
        service = CapabilityRegistryService(mock_utility_foundation, mock_public_works_foundation)
        
        # Register multiple capabilities
        capabilities = [
            CapabilityDefinition(
                name="capability_1",
                service_name="service_1",
                capability_type="data_processing",
                description="First capability",
                version="1.0.0",
                endpoints=["/api/cap1"],
                dependencies=[],
                metadata={}
            ),
            CapabilityDefinition(
                name="capability_2",
                service_name="service_2",
                capability_type="analytics",
                description="Second capability",
                version="1.0.0",
                endpoints=["/api/cap2"],
                dependencies=[],
                metadata={}
            )
        ]
        
        for capability in capabilities:
            await service.register_capability(capability)
        
        # Test discovery by type
        data_processing_caps = await service.discover_capabilities(capability_type="data_processing")
        assert len(data_processing_caps) == 1
        assert data_processing_caps[0].name == "capability_1"
        
        # Test discovery by service
        service_1_caps = await service.discover_capabilities(service_name="service_1")
        assert len(service_1_caps) == 1
        assert service_1_caps[0].name == "capability_1"
        
        # Test discovery all
        all_caps = await service.discover_capabilities()
        assert len(all_caps) == 2
    
    @pytest.mark.asyncio
    async def test_capability_validation(self, mock_utility_foundation, mock_public_works_foundation):
        """Test capability validation functionality."""
        service = CapabilityRegistryService(mock_utility_foundation, mock_public_works_foundation)
        
        # Test valid capability
        valid_capability = CapabilityDefinition(
            name="valid_capability",
            service_name="test_service",
            capability_type="data_processing",
            description="Valid capability",
            version="1.0.0",
            endpoints=["/api/valid"],
            dependencies=[],
            metadata={}
        )
        
        validation_result = await service.validate_capability(valid_capability)
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
        
        # Test invalid capability (missing required fields)
        invalid_capability = CapabilityDefinition(
            name="",  # Invalid: empty name
            service_name="test_service",
            capability_type="data_processing",
            description="Invalid capability",
            version="1.0.0",
            endpoints=[],  # Invalid: no endpoints
            dependencies=[],
            metadata={}
        )
        
        validation_result = await service.validate_capability(invalid_capability)
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) > 0


class TestPatternValidationService(CuratorFoundationTestBase):
    """Test Pattern Validation Service functionality."""
    
    @pytest.mark.asyncio
    async def test_pattern_validation_initialization(self, mock_utility_foundation):
        """Test pattern validation service initialization."""
        service = PatternValidationService(mock_utility_foundation)
        
        assert service is not None
        assert service.service_name == "pattern_validation"
        assert service.utility_foundation == mock_utility_foundation
        assert service.pattern_registry is not None
        assert isinstance(service.pattern_registry, dict)
    
    @pytest.mark.asyncio
    async def test_pattern_registration(self, mock_utility_foundation):
        """Test pattern registration functionality."""
        service = PatternValidationService(mock_utility_foundation)
        
        # Create a test pattern
        pattern = PatternDefinition(
            name="test_pattern",
            pattern_type="architectural",
            description="Test architectural pattern",
            rules=["rule1", "rule2"],
            validation_logic="def validate(): return True",
            metadata={"category": "design"}
        )
        
        # Register the pattern
        result = await service.register_pattern(pattern)
        
        assert result is not None
        assert "status" in result
        assert result["status"] == "success"
        
        # Verify pattern is in registry
        assert pattern.name in service.pattern_registry
        registered_pattern = service.pattern_registry[pattern.name]
        assert registered_pattern.name == pattern.name
        assert registered_pattern.pattern_type == pattern.pattern_type
    
    @pytest.mark.asyncio
    async def test_pattern_validation(self, mock_utility_foundation):
        """Test pattern validation functionality."""
        service = PatternValidationService(mock_utility_foundation)
        
        # Register a pattern
        pattern = PatternDefinition(
            name="naming_convention",
            pattern_type="coding",
            description="Naming convention pattern",
            rules=["snake_case", "descriptive_names"],
            validation_logic="def validate(code): return 'snake_case' in code",
            metadata={"severity": "warning"}
        )
        
        await service.register_pattern(pattern)
        
        # Test validation
        test_code = "def my_function(): pass"
        validation_result = await service.validate_against_pattern("naming_convention", test_code)
        
        assert validation_result is not None
        assert "valid" in validation_result
        assert "violations" in validation_result
        assert "pattern_name" in validation_result
    
    @pytest.mark.asyncio
    async def test_tenant_compliance_check(self, mock_utility_foundation):
        """Test tenant compliance checking."""
        service = PatternValidationService(mock_utility_foundation)
        
        # Mock tenant utility
        service.tenant_utility = Mock()
        service.tenant_utility.is_multi_tenant_enabled.return_value = True
        
        # Mock security service
        service.security_service = Mock()
        service.security_service.validate_user_context_with_security.return_value = True
        
        # Test compliance check
        result = await service.check_tenant_compliance("test_tenant", "test_user")
        
        assert result is not None
        assert "compliant" in result
        assert "tenant_id" in result
        assert "user_id" in result


class TestAntiPatternDetectionService(CuratorFoundationTestBase):
    """Test Anti-Pattern Detection Service functionality."""
    
    @pytest.mark.asyncio
    async def test_antipattern_detection_initialization(self, mock_utility_foundation):
        """Test anti-pattern detection service initialization."""
        service = AntiPatternDetectionService(mock_utility_foundation)
        
        assert service is not None
        assert service.service_name == "antipattern_detection"
        assert service.utility_foundation == mock_utility_foundation
        assert service.violation_registry is not None
        assert isinstance(service.violation_registry, list)
    
    @pytest.mark.asyncio
    async def test_code_scanning(self, mock_utility_foundation):
        """Test code scanning functionality."""
        service = AntiPatternDetectionService(mock_utility_foundation)
        
        # Test code with potential anti-patterns
        test_code = """
        def bad_function():
            # This function is too long and does too many things
            data = get_data()
            processed_data = process_data(data)
            result = analyze_data(processed_data)
            report = generate_report(result)
            send_report(report)
            return result
        """
        
        # Scan for anti-patterns
        scan_result = await service.scan_code_for_antipatterns(test_code, "test_file.py")
        
        assert scan_result is not None
        assert "violations" in scan_result
        assert "file_path" in scan_result
        assert "scan_timestamp" in scan_result
        assert isinstance(scan_result["violations"], list)
    
    @pytest.mark.asyncio
    async def test_violation_tracking(self, mock_utility_foundation):
        """Test violation tracking functionality."""
        service = AntiPatternDetectionService(mock_utility_foundation)
        
        # Create a test violation
        violation = AntiPatternViolation(
            violation_type="long_function",
            file_path="test_file.py",
            line_number=10,
            description="Function is too long",
            severity="warning",
            suggested_fix="Break into smaller functions",
            metadata={"function_name": "bad_function"}
        )
        
        # Track the violation
        result = await service.track_violation(violation)
        
        assert result is not None
        assert "status" in result
        assert result["status"] == "success"
        
        # Verify violation is tracked
        assert len(service.violation_registry) > 0
        tracked_violation = service.violation_registry[0]
        assert tracked_violation.violation_type == violation.violation_type
        assert tracked_violation.file_path == violation.file_path


class TestDocumentationGenerationService(CuratorFoundationTestBase):
    """Test Documentation Generation Service functionality."""
    
    @pytest.mark.asyncio
    async def test_documentation_generation_initialization(self, mock_utility_foundation):
        """Test documentation generation service initialization."""
        service = DocumentationGenerationService(mock_utility_foundation)
        
        assert service is not None
        assert service.service_name == "documentation_generation"
        assert service.utility_foundation == mock_utility_foundation
        assert service.generated_docs is not None
        assert isinstance(service.generated_docs, dict)
    
    @pytest.mark.asyncio
    async def test_openapi_generation(self, mock_utility_foundation):
        """Test OpenAPI documentation generation."""
        service = DocumentationGenerationService(mock_utility_foundation)
        
        # Mock service definitions
        service_definitions = {
            "test_service": {
                "name": "Test Service",
                "version": "1.0.0",
                "endpoints": [
                    {
                        "path": "/api/test",
                        "method": "GET",
                        "description": "Test endpoint",
                        "parameters": [],
                        "responses": {"200": {"description": "Success"}}
                    }
                ]
            }
        }
        
        # Generate OpenAPI spec
        openapi_spec = await service.generate_openapi_spec(service_definitions)
        
        assert openapi_spec is not None
        assert "openapi" in openapi_spec
        assert "info" in openapi_spec
        assert "paths" in openapi_spec
        assert openapi_spec["info"]["title"] == "SymphAIny Platform API"
        assert openapi_spec["info"]["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_markdown_documentation_generation(self, mock_utility_foundation):
        """Test Markdown documentation generation."""
        service = DocumentationGenerationService(mock_utility_foundation)
        
        # Mock service information
        service_info = {
            "name": "Test Service",
            "description": "A test service for documentation",
            "version": "1.0.0",
            "endpoints": [
                {
                    "path": "/api/test",
                    "method": "GET",
                    "description": "Test endpoint"
                }
            ]
        }
        
        # Generate Markdown documentation
        markdown_doc = await service.generate_markdown_docs(service_info)
        
        assert markdown_doc is not None
        assert isinstance(markdown_doc, str)
        assert "# Test Service" in markdown_doc
        assert "## API Endpoints" in markdown_doc
        assert "/api/test" in markdown_doc
