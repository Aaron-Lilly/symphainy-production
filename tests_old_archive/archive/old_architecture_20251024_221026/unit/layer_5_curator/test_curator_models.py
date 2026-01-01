#!/usr/bin/env python3
"""
Tests for Curator Foundation models.

Tests the data models: CapabilityDefinition, PatternDefinition, and AntiPatternViolation.
"""

import pytest
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import asdict

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from foundations.curator_foundation.models import (
    CapabilityDefinition,
    PatternDefinition,
    AntiPatternViolation
)


class TestCapabilityDefinition:
    """Test CapabilityDefinition model."""
    
    def test_capability_definition_creation(self):
        """Test creating a capability definition."""
        capability = CapabilityDefinition(
            service_name="test_service",
            interface_name="test_interface",
            endpoints=["/api/test"],
            tools=["test_tool"],
            description="Test capability for data processing",
            realm="smart_city",
            version="1.0.0"
        )
        
        assert capability.service_name == "test_service"
        assert capability.interface_name == "test_interface"
        assert capability.endpoints == ["/api/test"]
        assert capability.tools == ["test_tool"]
        assert capability.description == "Test capability for data processing"
        assert capability.realm == "smart_city"
        assert capability.version == "1.0.0"
        assert capability.registered_at is not None
    
    def test_capability_definition_defaults(self):
        """Test capability definition with default values."""
        capability = CapabilityDefinition(
            service_name="minimal_service",
            interface_name="minimal_interface",
            endpoints=[],
            tools=[],
            description="Minimal capability",
            realm="basic"
        )
        
        assert capability.service_name == "minimal_service"
        assert capability.interface_name == "minimal_interface"
        assert capability.endpoints == []
        assert capability.tools == []
        assert capability.description == "Minimal capability"
        assert capability.realm == "basic"
        assert capability.version == "1.0.0"  # Default value
        assert capability.registered_at is not None
    
    def test_capability_definition_serialization(self):
        """Test capability definition serialization."""
        capability = CapabilityDefinition(
            service_name="serializable_service",
            interface_name="serializable_interface",
            endpoints=["/api/serialize"],
            tools=["json_tool"],
            description="Test serialization",
            realm="serialization"
        )
        
        # Test dataclass serialization
        capability_dict = asdict(capability)
        
        assert isinstance(capability_dict, dict)
        assert capability_dict["service_name"] == "serializable_service"
        assert capability_dict["interface_name"] == "serializable_interface"
        assert capability_dict["description"] == "Test serialization"
        assert capability_dict["realm"] == "serialization"
        assert capability_dict["version"] == "1.0.0"
        assert capability_dict["endpoints"] == ["/api/serialize"]
        assert capability_dict["tools"] == ["json_tool"]
        assert "registered_at" in capability_dict


class TestPatternDefinition:
    """Test PatternDefinition model."""
    
    def test_pattern_definition_creation(self):
        """Test creating a pattern definition."""
        pattern = PatternDefinition(
            pattern_name="test_pattern",
            pattern_type="interface",
            description="Test architectural pattern",
            rules=["rule1", "rule2"],
            severity="error"
        )
        
        assert pattern.pattern_name == "test_pattern"
        assert pattern.pattern_type == "interface"
        assert pattern.description == "Test architectural pattern"
        assert pattern.rules == ["rule1", "rule2"]
        assert pattern.severity == "error"
        assert pattern.created_at is not None
    
    def test_pattern_definition_defaults(self):
        """Test pattern definition with default values."""
        pattern = PatternDefinition(
            pattern_name="minimal_pattern",
            pattern_type="service",
            description="Minimal pattern",
            rules=[]
        )
        
        assert pattern.pattern_name == "minimal_pattern"
        assert pattern.pattern_type == "service"
        assert pattern.description == "Minimal pattern"
        assert pattern.rules == []
        assert pattern.severity == "error"  # Default value
        assert pattern.created_at is not None
    
    def test_pattern_definition_serialization(self):
        """Test pattern definition serialization."""
        pattern = PatternDefinition(
            pattern_name="serializable_pattern",
            pattern_type="api",
            description="Test serialization",
            rules=["serialize", "deserialize"],
            severity="warning"
        )
        
        # Test dataclass serialization
        pattern_dict = asdict(pattern)
        
        assert isinstance(pattern_dict, dict)
        assert pattern_dict["pattern_name"] == "serializable_pattern"
        assert pattern_dict["pattern_type"] == "api"
        assert pattern_dict["description"] == "Test serialization"
        assert pattern_dict["rules"] == ["serialize", "deserialize"]
        assert pattern_dict["severity"] == "warning"
        assert "created_at" in pattern_dict


class TestAntiPatternViolation:
    """Test AntiPatternViolation model."""
    
    def test_antipattern_violation_creation(self):
        """Test creating an anti-pattern violation."""
        violation = AntiPatternViolation(
            violation_id="violation_001",
            pattern_name="long_function",
            file_path="test_file.py",
            line_number=10,
            code_snippet="def bad_function(): pass",
            severity="warning",
            description="Function is too long",
            suggested_fix="Break into smaller functions"
        )
        
        assert violation.violation_id == "violation_001"
        assert violation.pattern_name == "long_function"
        assert violation.file_path == "test_file.py"
        assert violation.line_number == 10
        assert violation.code_snippet == "def bad_function(): pass"
        assert violation.severity == "warning"
        assert violation.description == "Function is too long"
        assert violation.suggested_fix == "Break into smaller functions"
        assert violation.detected_at is not None
    
    def test_antipattern_violation_defaults(self):
        """Test anti-pattern violation with default values."""
        violation = AntiPatternViolation(
            violation_id="violation_002",
            pattern_name="basic_violation",
            file_path="basic_file.py",
            line_number=1,
            code_snippet="basic code",
            severity="info",
            description="Basic violation",
            suggested_fix="Fix the issue"
        )
        
        assert violation.violation_id == "violation_002"
        assert violation.pattern_name == "basic_violation"
        assert violation.file_path == "basic_file.py"
        assert violation.line_number == 1
        assert violation.code_snippet == "basic code"
        assert violation.severity == "info"
        assert violation.description == "Basic violation"
        assert violation.suggested_fix == "Fix the issue"
        assert violation.detected_at is not None
    
    def test_antipattern_violation_serialization(self):
        """Test anti-pattern violation serialization."""
        violation = AntiPatternViolation(
            violation_id="violation_003",
            pattern_name="serializable_violation",
            file_path="serializable_file.py",
            line_number=5,
            code_snippet="serializable code",
            severity="error",
            description="Test serialization",
            suggested_fix="Serialize properly"
        )
        
        # Test dataclass serialization
        violation_dict = asdict(violation)
        
        assert isinstance(violation_dict, dict)
        assert violation_dict["violation_id"] == "violation_003"
        assert violation_dict["pattern_name"] == "serializable_violation"
        assert violation_dict["file_path"] == "serializable_file.py"
        assert violation_dict["line_number"] == 5
        assert violation_dict["code_snippet"] == "serializable code"
        assert violation_dict["severity"] == "error"
        assert violation_dict["description"] == "Test serialization"
        assert violation_dict["suggested_fix"] == "Serialize properly"
        assert "detected_at" in violation_dict
    
    def test_antipattern_violation_severity_levels(self):
        """Test different severity levels."""
        severities = ["info", "warning", "error"]
        
        for i, severity in enumerate(severities):
            violation = AntiPatternViolation(
                violation_id=f"violation_{i}",
                pattern_name=f"test_{severity}",
                file_path="test_file.py",
                line_number=1,
                code_snippet="test code",
                severity=severity,
                description=f"Test {severity} violation",
                suggested_fix="Fix the issue"
            )
            
            assert violation.severity == severity
            assert violation.description == f"Test {severity} violation"