#!/usr/bin/env python3
"""
E2E Test Configuration

Configuration settings and utilities for E2E testing.
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TestConfig:
    """Configuration for E2E tests."""
    
    # Frontend URLs
    base_url: str = "http://localhost:3000"
    content_pillar_url: str = "http://localhost:3000/content"
    insights_pillar_url: str = "http://localhost:3000/insights"
    
    # Backend URLs
    backend_base_url: str = "http://localhost:8000"
    content_pillar_service_url: str = "http://localhost:8001"
    insights_pillar_service_url: str = "http://localhost:8002"
    experience_service_url: str = "http://localhost:8003"
    
    # Test data
    test_files_dir: str = "test_data"
    test_data_generated: bool = False
    
    # Test settings
    headless: bool = True
    slow_mo: int = 0
    timeout: int = 30000
    retry_count: int = 3
    
    # Browser settings
    browser_type: str = "chromium"
    viewport_width: int = 1280
    viewport_height: int = 720
    
    # API settings
    api_timeout: int = 10000
    api_retry_count: int = 3
    
    # Test data settings
    num_customers: int = 100
    num_payments: int = 200
    num_mainframe_records: int = 50
    
    # Environment settings
    environment: str = "test"
    debug_mode: bool = False
    verbose_logging: bool = False
    
    # Database settings (for backend testing)
    database_url: str = "sqlite:///test.db"
    test_database_url: str = "sqlite:///test_e2e.db"
    
    # Authentication settings
    test_user_email: str = "test@example.com"
    test_user_password: str = "testpassword123"
    
    # Feature flags
    enable_content_pillar: bool = True
    enable_insights_pillar: bool = True
    enable_operations_pillar: bool = False
    enable_business_outcomes_pillar: bool = False
    
    # Test execution settings
    parallel_workers: int = 1
    test_timeout: int = 300  # 5 minutes per test
    max_failures: int = 5
    
    # Reporting settings
    generate_html_report: bool = True
    generate_json_report: bool = True
    report_dir: str = "test_reports"
    
    # Screenshot settings
    take_screenshots: bool = True
    screenshot_dir: str = "test_screenshots"
    screenshot_on_failure: bool = True
    
    # Video settings
    record_video: bool = False
    video_dir: str = "test_videos"
    
    # Performance settings
    measure_performance: bool = True
    performance_threshold_ms: int = 5000
    
    # Accessibility settings
    check_accessibility: bool = True
    accessibility_standards: list = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.accessibility_standards is None:
            self.accessibility_standards = ["WCAG2AA"]
        
        # Ensure directories exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure required directories exist."""
        directories = [
            self.test_files_dir,
            self.report_dir,
            self.screenshot_dir,
            self.video_dir
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    @classmethod
    def from_file(cls, config_file: str) -> 'TestConfig':
        """Load configuration from file."""
        if not os.path.exists(config_file):
            return cls()
        
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        return cls(**config_data)
    
    def to_file(self, config_file: str):
        """Save configuration to file."""
        config_data = {
            'base_url': self.base_url,
            'content_pillar_url': self.content_pillar_url,
            'insights_pillar_url': self.insights_pillar_url,
            'backend_base_url': self.backend_base_url,
            'content_pillar_service_url': self.content_pillar_service_url,
            'insights_pillar_service_url': self.insights_pillar_service_url,
            'experience_service_url': self.experience_service_url,
            'test_files_dir': self.test_files_dir,
            'test_data_generated': self.test_data_generated,
            'headless': self.headless,
            'slow_mo': self.slow_mo,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'browser_type': self.browser_type,
            'viewport_width': self.viewport_width,
            'viewport_height': self.viewport_height,
            'api_timeout': self.api_timeout,
            'api_retry_count': self.api_retry_count,
            'num_customers': self.num_customers,
            'num_payments': self.num_payments,
            'num_mainframe_records': self.num_mainframe_records,
            'environment': self.environment,
            'debug_mode': self.debug_mode,
            'verbose_logging': self.verbose_logging,
            'database_url': self.database_url,
            'test_database_url': self.test_database_url,
            'test_user_email': self.test_user_email,
            'test_user_password': self.test_user_password,
            'enable_content_pillar': self.enable_content_pillar,
            'enable_insights_pillar': self.enable_insights_pillar,
            'enable_operations_pillar': self.enable_operations_pillar,
            'enable_business_outcomes_pillar': self.enable_business_outcomes_pillar,
            'parallel_workers': self.parallel_workers,
            'test_timeout': self.test_timeout,
            'max_failures': self.max_failures,
            'generate_html_report': self.generate_html_report,
            'generate_json_report': self.generate_json_report,
            'report_dir': self.report_dir,
            'take_screenshots': self.take_screenshots,
            'screenshot_dir': self.screenshot_dir,
            'screenshot_on_failure': self.screenshot_on_failure,
            'record_video': self.record_video,
            'video_dir': self.video_dir,
            'measure_performance': self.measure_performance,
            'performance_threshold_ms': self.performance_threshold_ms,
            'check_accessibility': self.check_accessibility,
            'accessibility_standards': self.accessibility_standards
        }
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def get_browser_context_options(self) -> Dict[str, Any]:
        """Get browser context options for Playwright."""
        return {
            'viewport': {
                'width': self.viewport_width,
                'height': self.viewport_height
            },
            'ignore_https_errors': True,
            'accept_downloads': True,
            'record_video_dir': self.video_dir if self.record_video else None,
            'record_video_size': {
                'width': self.viewport_width,
                'height': self.viewport_height
            } if self.record_video else None
        }
    
    def get_browser_launch_options(self) -> Dict[str, Any]:
        """Get browser launch options for Playwright."""
        options = {
            'headless': self.headless,
            'slow_mo': self.slow_mo,
            'timeout': self.timeout
        }
        
        if self.browser_type == "chromium":
            options['args'] = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        
        return options
    
    def get_test_timeout(self) -> int:
        """Get test timeout in milliseconds."""
        return self.test_timeout * 1000
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        feature_map = {
            'content_pillar': self.enable_content_pillar,
            'insights_pillar': self.enable_insights_pillar,
            'operations_pillar': self.enable_operations_pillar,
            'business_outcomes_pillar': self.enable_business_outcomes_pillar
        }
        
        return feature_map.get(feature, False)
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get environment variables for testing."""
        return {
            'TEST_ENVIRONMENT': self.environment,
            'TEST_DEBUG_MODE': str(self.debug_mode),
            'TEST_VERBOSE_LOGGING': str(self.verbose_logging),
            'TEST_DATABASE_URL': self.test_database_url,
            'TEST_USER_EMAIL': self.test_user_email,
            'TEST_USER_PASSWORD': self.test_user_password
        }
    
    def validate(self) -> bool:
        """Validate configuration."""
        errors = []
        
        # Check required URLs
        if not self.base_url:
            errors.append("base_url is required")
        
        if not self.content_pillar_url:
            errors.append("content_pillar_url is required")
        
        if not self.insights_pillar_url:
            errors.append("insights_pillar_url is required")
        
        # Check numeric values
        if self.timeout <= 0:
            errors.append("timeout must be positive")
        
        if self.retry_count < 0:
            errors.append("retry_count must be non-negative")
        
        if self.viewport_width <= 0 or self.viewport_height <= 0:
            errors.append("viewport dimensions must be positive")
        
        # Check feature flags
        if not any([self.enable_content_pillar, self.enable_insights_pillar, 
                   self.enable_operations_pillar, self.enable_business_outcomes_pillar]):
            errors.append("At least one pillar must be enabled")
        
        if errors:
            print("❌ Configuration validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        return True


# Default configuration instance
default_config = TestConfig()

# Environment-specific configurations
def get_config_for_environment(env: str = "test") -> TestConfig:
    """Get configuration for specific environment."""
    if env == "test":
        return TestConfig(
            environment="test",
            headless=True,
            debug_mode=False,
            verbose_logging=False
        )
    elif env == "development":
        return TestConfig(
            environment="development",
            headless=False,
            debug_mode=True,
            verbose_logging=True,
            slow_mo=100
        )
    elif env == "staging":
        return TestConfig(
            environment="staging",
            base_url="https://staging.symphainy.com",
            headless=True,
            debug_mode=False,
            verbose_logging=True
        )
    elif env == "production":
        return TestConfig(
            environment="production",
            base_url="https://symphainy.com",
            headless=True,
            debug_mode=False,
            verbose_logging=False,
            record_video=False,
            take_screenshots=False
        )
    else:
        return default_config


if __name__ == "__main__":
    # Generate default configuration file
    config = TestConfig()
    config.to_file("test_config.json")
    print("✅ Generated default test configuration: test_config.json")
    
    # Validate configuration
    if config.validate():
        print("✅ Configuration validation passed")
    else:
        print("❌ Configuration validation failed")





