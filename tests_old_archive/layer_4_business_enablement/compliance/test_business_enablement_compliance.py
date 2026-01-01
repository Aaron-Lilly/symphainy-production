#!/usr/bin/env python3
"""
Business Enablement Compliance Tests

Validates that all Business Enablement components follow architectural patterns:
- DI Container usage (no direct imports)
- Utility usage (no direct logging, etc.)
- Foundation usage (Smart City SOA APIs, Platform Gateway)
- Base class compliance (RealmServiceBase, OrchestratorBase, AgentBase)

This test runs the validators and verifies no violations in active code.
"""

import pytest
from pathlib import Path

# Path is configured in pytest.ini - no manipulation needed
from tests.fixtures.di_container_usage_validator import DIContainerUsageValidator
from tests.fixtures.utility_usage_validator import UtilityUsageValidator
from tests.fixtures.foundation_usage_validator import FoundationUsageValidator
from tests.fixtures.smart_city_usage_validator import SmartCityUsageValidator


@pytest.mark.business_enablement
class TestBusinessEnablementCompliance:
    """Test Business Enablement components comply with architectural patterns."""
    
    # Use project_root_path fixture from conftest.py
    
    @pytest.fixture
    def business_enablement_path(self, project_root_path):
        """Get Business Enablement path."""
        return project_root_path / "backend" / "business_enablement"
    
    def test_di_container_compliance(self, project_root_path, business_enablement_path):
        """Test Business Enablement components use DI Container correctly."""
        validator = DIContainerUsageValidator(project_root_path)
        
        # Validate Business Enablement directory
        violations = validator.validate_directory(business_enablement_path)
        
        # Filter out archive violations
        active_violations = [v for v in violations if 'archive' not in v.get('file', '')]
        
        assert len(active_violations) == 0, \
            f"Found {len(active_violations)} DI Container violations in active code:\n" + \
            "\n".join([f"  {v.get('file')}:{v.get('line')} - {v.get('message')}" 
                      for v in active_violations[:10]])
    
    def test_utility_compliance(self, project_root_path, business_enablement_path):
        """Test Business Enablement components use utilities correctly."""
        validator = UtilityUsageValidator(project_root_path)
        
        # Validate Business Enablement directory
        violations = validator.validate_directory(business_enablement_path)
        
        # Filter out archive violations
        active_violations = [v for v in violations if 'archive' not in v.get('file', '')]
        
        assert len(active_violations) == 0, \
            f"Found {len(active_violations)} Utility violations in active code:\n" + \
            "\n".join([f"  {v.get('file')}:{v.get('line')} - {v.get('message')}" 
                      for v in active_violations[:10]])
    
    def test_foundation_compliance(self, project_root_path, business_enablement_path):
        """Test Business Enablement components use foundations correctly."""
        validator = FoundationUsageValidator(project_root_path)
        
        # Validate Business Enablement directory
        violations = validator.validate_directory(business_enablement_path)
        
        # Filter out archive violations
        active_violations = [v for v in violations if 'archive' not in v.get('file', '')]
        
        assert len(active_violations) == 0, \
            f"Found {len(active_violations)} Foundation violations in active code:\n" + \
            "\n".join([f"  {v.get('file')}:{v.get('line')} - {v.get('message')}" 
                      for v in active_violations[:10]])
    
    def test_smart_city_usage_compliance(self, project_root_path):
        """Test Business Enablement components use Smart City SOA APIs correctly."""
        validator = SmartCityUsageValidator(project_root_path)
        
        # Validate Business Enablement realm
        results = validator.validate_realm('business_enablement')
        
        # Filter out archive violations
        active_violations = [v for v in results.get('violations', []) 
                           if 'archive' not in v.get('file', '')]
        
        assert len(active_violations) == 0, \
            f"Found {len(active_violations)} Smart City Usage violations in active code:\n" + \
            "\n".join([f"  {v.get('file')}:{v.get('line')} - {v.get('type')}: {v.get('message')}" 
                      for v in active_violations[:10]])
    
    def test_all_compliance_validators_pass(self, project_root_path, business_enablement_path):
        """Test all compliance validators pass for Business Enablement."""
        # Run all validators
        di_validator = DIContainerUsageValidator(project_root_path)
        utility_validator = UtilityUsageValidator(project_root_path)
        foundation_validator = FoundationUsageValidator(project_root_path)
        smart_city_validator = SmartCityUsageValidator(project_root_path)
        
        # Collect all violations
        di_violations = [v for v in di_validator.validate_directory(business_enablement_path) 
                        if 'archive' not in v.get('file', '')]
        utility_violations = [v for v in utility_validator.validate_directory(business_enablement_path) 
                             if 'archive' not in v.get('file', '')]
        foundation_violations = [v for v in foundation_validator.validate_directory(business_enablement_path) 
                                if 'archive' not in v.get('file', '')]
        smart_city_results = smart_city_validator.validate_realm('business_enablement')
        smart_city_violations = [v for v in smart_city_results.get('violations', []) 
                                if 'archive' not in v.get('file', '')]
        
        # Report summary
        total_violations = len(di_violations) + len(utility_violations) + \
                          len(foundation_violations) + len(smart_city_violations)
        
        if total_violations > 0:
            print(f"\n📊 Compliance Summary:")
            print(f"  DI Container violations: {len(di_violations)}")
            print(f"  Utility violations: {len(utility_violations)}")
            print(f"  Foundation violations: {len(foundation_violations)}")
            print(f"  Smart City Usage violations: {len(smart_city_violations)}")
            print(f"  Total: {total_violations}")
        
        assert total_violations == 0, \
            f"Found {total_violations} total compliance violations in active code. " \
            f"See individual test failures for details."

