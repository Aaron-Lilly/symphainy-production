#!/usr/bin/env python3
"""
E2E Test Setup Validation

Validate that the E2E test setup is working correctly.
"""

import os
import sys
import asyncio
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from test_config import TestConfig, get_config_for_environment
from test_data_generator import TestDataGenerator
from test_utilities import create_test_logger


class E2ESetupValidator:
    """Validate E2E test setup."""
    
    def __init__(self):
        self.logger = create_test_logger("E2E_SetupValidator")
        self.validation_results = []
    
    def validate_configuration(self) -> bool:
        """Validate test configuration."""
        self.logger.info("🔧 Validating test configuration...")
        
        try:
            # Test default configuration
            config = TestConfig()
            if not config.validate():
                self.validation_results.append({
                    'component': 'Configuration',
                    'status': 'failed',
                    'message': 'Default configuration validation failed'
                })
                return False
            
            # Test environment-specific configurations
            environments = ['test', 'development', 'staging', 'production']
            for env in environments:
                env_config = get_config_for_environment(env)
                if not env_config.validate():
                    self.validation_results.append({
                        'component': f'Configuration ({env})',
                        'status': 'failed',
                        'message': f'{env} configuration validation failed'
                    })
                    return False
            
            self.validation_results.append({
                'component': 'Configuration',
                'status': 'passed',
                'message': 'All configurations validated successfully'
            })
            
            self.logger.info("✅ Configuration validation passed")
            return True
            
        except Exception as e:
            self.validation_results.append({
                'component': 'Configuration',
                'status': 'failed',
                'message': f'Configuration validation error: {e}'
            })
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def validate_test_data_generation(self) -> bool:
        """Validate test data generation."""
        self.logger.info("📊 Validating test data generation...")
        
        try:
            # Create test data generator
            generator = TestDataGenerator("test_validation_data")
            
            # Generate test data
            generator.generate_all_test_files()
            
            # Verify files were created
            expected_files = [
                "test_customers.csv",
                "test_customers.json",
                "test_payments.csv",
                "test_payments.json",
                "test_mainframe.dat",
                "test_copybook.cpy",
                "invalid_file.txt",
                "corrupted.csv"
            ]
            
            missing_files = []
            for filename in expected_files:
                filepath = os.path.join("test_validation_data", filename)
                if not os.path.exists(filepath):
                    missing_files.append(filename)
            
            if missing_files:
                self.validation_results.append({
                    'component': 'Test Data Generation',
                    'status': 'failed',
                    'message': f'Missing files: {", ".join(missing_files)}'
                })
                return False
            
            # Verify file contents
            csv_file = os.path.join("test_validation_data", "test_customers.csv")
            with open(csv_file, 'r') as f:
                csv_content = f.read()
                if "customer_id" not in csv_content:
                    self.validation_results.append({
                        'component': 'Test Data Generation',
                        'status': 'failed',
                        'message': 'CSV file content validation failed'
                    })
                    return False
            
            self.validation_results.append({
                'component': 'Test Data Generation',
                'status': 'passed',
                'message': 'Test data generation successful'
            })
            
            self.logger.info("✅ Test data generation validation passed")
            return True
            
        except Exception as e:
            self.validation_results.append({
                'component': 'Test Data Generation',
                'status': 'failed',
                'message': f'Test data generation error: {e}'
            })
            self.logger.error(f"Test data generation validation failed: {e}")
            return False
    
    def validate_dependencies(self) -> bool:
        """Validate required dependencies."""
        self.logger.info("📦 Validating dependencies...")
        
        try:
            # Check Playwright
            try:
                from playwright.async_api import async_playwright
                self.logger.info("✅ Playwright available")
            except ImportError:
                self.validation_results.append({
                    'component': 'Dependencies',
                    'status': 'failed',
                    'message': 'Playwright not installed'
                })
                return False
            
            # Check other dependencies
            dependencies = [
                'pytest',
                'asyncio',
                'json',
                'datetime',
                'typing'
            ]
            
            missing_deps = []
            for dep in dependencies:
                try:
                    __import__(dep)
                except ImportError:
                    missing_deps.append(dep)
            
            if missing_deps:
                self.validation_results.append({
                    'component': 'Dependencies',
                    'status': 'failed',
                    'message': f'Missing dependencies: {", ".join(missing_deps)}'
                })
                return False
            
            self.validation_results.append({
                'component': 'Dependencies',
                'status': 'passed',
                'message': 'All dependencies available'
            })
            
            self.logger.info("✅ Dependencies validation passed")
            return True
            
        except Exception as e:
            self.validation_results.append({
                'component': 'Dependencies',
                'status': 'failed',
                'message': f'Dependencies validation error: {e}'
            })
            self.logger.error(f"Dependencies validation failed: {e}")
            return False
    
    def validate_test_structure(self) -> bool:
        """Validate test file structure."""
        self.logger.info("📁 Validating test structure...")
        
        try:
            # Check required test files
            required_files = [
                "test_content_pillar_e2e.py",
                "test_content_pillar_test_cases.py",
                "test_data_generator.py",
                "test_config.py",
                "test_utilities.py",
                "run_e2e_tests.py"
            ]
            
            missing_files = []
            for filename in required_files:
                filepath = os.path.join(os.path.dirname(__file__), filename)
                if not os.path.exists(filepath):
                    missing_files.append(filename)
            
            if missing_files:
                self.validation_results.append({
                    'component': 'Test Structure',
                    'status': 'failed',
                    'message': f'Missing test files: {", ".join(missing_files)}'
                })
                return False
            
            # Check test directories
            required_dirs = [
                "test_data",
                "test_reports",
                "test_screenshots"
            ]
            
            missing_dirs = []
            for dirname in required_dirs:
                if not os.path.exists(dirname):
                    missing_dirs.append(dirname)
            
            if missing_dirs:
                self.validation_results.append({
                    'component': 'Test Structure',
                    'status': 'failed',
                    'message': f'Missing test directories: {", ".join(missing_dirs)}'
                })
                return False
            
            self.validation_results.append({
                'component': 'Test Structure',
                'status': 'passed',
                'message': 'Test structure validation successful'
            })
            
            self.logger.info("✅ Test structure validation passed")
            return True
            
        except Exception as e:
            self.validation_results.append({
                'component': 'Test Structure',
                'status': 'failed',
                'message': f'Test structure validation error: {e}'
            })
            self.logger.error(f"Test structure validation failed: {e}")
            return False
    
    def validate_imports(self) -> bool:
        """Validate that all imports work correctly."""
        self.logger.info("🔗 Validating imports...")
        
        try:
            # Test main test suite import (use relative import to avoid conflict with root file)
            import sys
            import os
            sys.path.insert(0, os.path.dirname(__file__))
            from test_content_pillar_e2e import ContentPillarE2ETestSuite
            self.logger.info("✅ ContentPillarE2ETestSuite import successful")
            
            # Test test cases import
            from test_content_pillar_test_cases import ContentPillarTestCases
            self.logger.info("✅ ContentPillarTestCases import successful")
            
            # Test utilities import
            from test_utilities import create_test_logger
            self.logger.info("✅ Test utilities import successful")
            
            # Test config import
            from test_config import TestConfig
            self.logger.info("✅ Test config import successful")
            
            self.validation_results.append({
                'component': 'Imports',
                'status': 'passed',
                'message': 'All imports successful'
            })
            
            self.logger.info("✅ Imports validation passed")
            return True
            
        except Exception as e:
            self.validation_results.append({
                'component': 'Imports',
                'status': 'failed',
                'message': f'Import validation error: {e}'
            })
            self.logger.error(f"Imports validation failed: {e}")
            return False
    
    def run_validation(self) -> bool:
        """Run all validations."""
        self.logger.info("🚀 Starting E2E test setup validation...")
        
        validations = [
            self.validate_dependencies,
            self.validate_test_structure,
            self.validate_imports,
            self.validate_configuration,
            self.validate_test_data_generation
        ]
        
        all_passed = True
        for validation in validations:
            if not validation():
                all_passed = False
        
        self.print_validation_results()
        return all_passed
    
    def print_validation_results(self):
        """Print validation results."""
        print("\n" + "="*60)
        print("📊 E2E TEST SETUP VALIDATION RESULTS")
        print("="*60)
        
        for result in self.validation_results:
            status_icon = "✅" if result['status'] == 'passed' else "❌"
            print(f"{status_icon} {result['component']}: {result['message']}")
        
        print("="*60)
        
        passed_count = sum(1 for r in self.validation_results if r['status'] == 'passed')
        total_count = len(self.validation_results)
        
        print(f"\n📈 Summary: {passed_count}/{total_count} validations passed")
        
        if passed_count == total_count:
            print("🎉 All validations passed! E2E test setup is ready.")
        else:
            print("⚠️  Some validations failed. Please fix the issues before running tests.")


def main():
    """Main entry point."""
    validator = E2ESetupValidator()
    
    if validator.run_validation():
        print("\n✅ E2E test setup validation completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ E2E test setup validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
