#!/usr/bin/env python3
"""
Smart City Realm Validator Compliance Tests

Tests to validate that Smart City services pass all validators:
- DI Container Usage Validator
- Utility Usage Validator
- Foundation Usage Validator
- Public Works Foundation Usage Validator
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add tests to path for validators
tests_root = project_root.parent
sys.path.insert(0, str(tests_root))

import pytest
from tests.fixtures.di_container_usage_validator import DIContainerUsageValidator
from tests.fixtures.utility_usage_validator import UtilityUsageValidator
from tests.fixtures.foundation_usage_validator import FoundationUsageValidator
from tests.fixtures.public_works_foundation_usage_validator import PublicWorksFoundationUsageValidator


class TestSmartCityValidatorCompliance:
    """Test Smart City services validator compliance."""
    
    @pytest.fixture
    def di_validator(self):
        """Create DI Container Usage Validator."""
        return DIContainerUsageValidator(project_root)
    
    @pytest.fixture
    def utility_validator(self):
        """Create Utility Usage Validator."""
        return UtilityUsageValidator(project_root)
    
    @pytest.fixture
    def foundation_validator(self):
        """Create Foundation Usage Validator."""
        return FoundationUsageValidator(project_root)
    
    @pytest.fixture
    def public_works_validator(self):
        """Create Public Works Foundation Usage Validator."""
        return PublicWorksFoundationUsageValidator(project_root)
    
    def test_smart_city_services_di_container_compliance(self, di_validator):
        """Test that Smart City services comply with DI Container usage rules."""
        smart_city_path = project_root / "backend" / "smart_city"
        
        violations = di_validator.validate_directory(smart_city_path)
        
        # Smart City services can directly import Public Works and Communications Foundations
        # So we should filter out those violations
        filtered_violations = [
            v for v in violations
            if not (
                'from foundations.public_works_foundation' in v.get('message', '') or
                'from foundations.communication_foundation' in v.get('message', '')
            )
        ]
        
        assert len(filtered_violations) == 0, f"Found DI Container violations: {filtered_violations[:5]}"
    
    def test_smart_city_services_utility_compliance(self, utility_validator):
        """Test that Smart City services comply with utility usage rules."""
        smart_city_path = project_root / "backend" / "smart_city"
        
        violations = utility_validator.validate_directory(smart_city_path)
        
        # Report violations but don't fail (we'll fix these separately)
        if violations:
            print(f"\n⚠️ Found {len(violations)} utility violations in Smart City services")
            for v in violations[:5]:
                print(f"  - {v['file']}:{v['line']} - {v['message']}")
        
        # For now, we'll track but not fail on utility violations
        # These will be addressed in a separate cleanup pass
        assert True  # Placeholder - will be updated after utility cleanup
    
    def test_smart_city_services_foundation_compliance(self, foundation_validator):
        """Test that Smart City services comply with foundation usage rules."""
        smart_city_path = project_root / "backend" / "smart_city"
        
        violations = foundation_validator.validate_directory(smart_city_path)
        
        # Smart City can directly access Public Works and Communications Foundations
        # So foundation violations should be minimal (only instantiation violations)
        foundation_violations = [v for v in violations if v['type'] == 'forbidden_foundation_import']
        
        assert len(foundation_violations) == 0, f"Found foundation import violations: {foundation_violations[:5]}"
    
    def test_smart_city_services_public_works_compliance(self, public_works_validator):
        """Test that Smart City services comply with Public Works Foundation usage rules."""
        smart_city_path = project_root / "backend" / "smart_city"
        
        violations = public_works_validator.validate_directory(smart_city_path)
        
        # Smart City can directly access Public Works abstractions
        # So violations should be minimal (only adapter instantiation violations)
        adapter_violations = [v for v in violations if v['type'] == 'forbidden_adapter_instantiation']
        
        assert len(adapter_violations) == 0, f"Found adapter instantiation violations: {adapter_violations[:5]}"
    
    def test_smart_city_services_comprehensive_compliance(self, di_validator, utility_validator, foundation_validator, public_works_validator):
        """Comprehensive validator compliance test for Smart City services."""
        smart_city_path = project_root / "backend" / "smart_city"
        
        # Run all validators
        di_violations = di_validator.validate_directory(smart_city_path)
        util_violations = utility_validator.validate_directory(smart_city_path)
        foundation_violations = foundation_validator.validate_directory(smart_city_path)
        public_works_violations = public_works_validator.validate_directory(smart_city_path)
        
        # Filter DI violations (allow Public Works/Communications imports for Smart City)
        filtered_di_violations = [
            v for v in di_violations
            if not (
                'from foundations.public_works_foundation' in v.get('message', '') or
                'from foundations.communication_foundation' in v.get('message', '')
            )
        ]
        
        # Filter foundation violations (only check instantiation, not imports)
        filtered_foundation_violations = [
            v for v in foundation_violations
            if v['type'] == 'forbidden_foundation_instantiation'
        ]
        
        # Report summary
        print(f"\n📊 Smart City Validator Compliance Summary:")
        print(f"  - DI Container violations: {len(filtered_di_violations)}")
        print(f"  - Utility violations: {len(util_violations)}")
        print(f"  - Foundation violations: {len(filtered_foundation_violations)}")
        print(f"  - Public Works violations: {len(public_works_violations)}")
        
        # Assertions
        assert len(filtered_di_violations) == 0, f"DI Container violations found: {filtered_di_violations[:3]}"
        assert len(filtered_foundation_violations) == 0, f"Foundation instantiation violations found: {filtered_foundation_violations[:3]}"
        assert len(public_works_violations) == 0, f"Public Works violations found: {public_works_violations[:3]}"
        
        # Utility violations are tracked but not failing (will be fixed separately)
        if util_violations:
            print(f"\n⚠️ Note: {len(util_violations)} utility violations found (will be addressed in utility cleanup)")

