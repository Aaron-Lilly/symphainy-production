#!/usr/bin/env python3
"""
E2E Test Runner

Main test runner for Content Pillar E2E tests.
"""

import os
import sys
import asyncio
import argparse
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from playwright.async_api import async_playwright
from test_config import TestConfig, get_config_for_environment
from test_utilities import (
    create_test_logger, create_test_screenshot, create_test_performance,
    create_test_data_manager, create_test_assertions, create_test_helpers,
    create_test_report_generator
)
from test_data_generator import TestDataGenerator
# Add current directory to path to avoid conflict with root file
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from test_content_pillar_e2e import ContentPillarE2ETestSuite


class E2ETestRunner:
    """Main E2E test runner."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.logger = create_test_logger("E2E_TestRunner")
        self.screenshot = create_test_screenshot(config.screenshot_dir)
        self.performance = create_test_performance()
        self.data_manager = create_test_data_manager(config.test_files_dir)
        self.report_generator = create_test_report_generator(config.report_dir)
        
        self.test_results = []
        self.browser = None
        self.context = None
        self.page = None
    
    async def setup(self):
        """Set up test environment."""
        self.logger.info("🔧 Setting up E2E test environment...")
        
        # Generate test data if needed
        if not self.config.test_data_generated:
            self.logger.info("📊 Generating test data...")
            generator = TestDataGenerator(self.config.test_files_dir)
            generator.generate_all_test_files()
            self.config.test_data_generated = True
        
        # Launch browser
        self.logger.info("🌐 Launching browser...")
        playwright = await async_playwright().start()
        
        browser_type = getattr(playwright, self.config.browser_type)
        self.browser = await browser_type.launch(
            **self.config.get_browser_launch_options()
        )
        
        # Create browser context
        self.context = await self.browser.new_context(
            **self.config.get_browser_context_options()
        )
        
        # Create page
        self.page = await self.context.new_page()
        
        # Set up page event handlers
        self.page.on("pageerror", self._handle_page_error)
        self.page.on("requestfailed", self._handle_request_failed)
        
        self.logger.info("✅ Test environment setup complete")
    
    async def teardown(self):
        """Tear down test environment."""
        self.logger.info("🧹 Tearing down E2E test environment...")
        
        if self.page:
            await self.page.close()
        
        if self.context:
            await self.context.close()
        
        if self.browser:
            await self.browser.close()
        
        self.logger.info("✅ Test environment teardown complete")
    
    async def _handle_page_error(self, error):
        """Handle page errors."""
        self.logger.error(f"Page error: {error}")
    
    async def _handle_request_failed(self, request):
        """Handle failed requests."""
        self.logger.warning(f"Request failed: {request.url} - {request.failure}")
    
    async def run_test_suite(self, test_suite_class, test_suite_name: str):
        """Run a test suite."""
        self.logger.info(f"🧪 Running test suite: {test_suite_name}")
        
        # Create test suite instance
        test_suite = test_suite_class(
            page=self.page,
            config=self.config,
            logger=self.logger,
            screenshot=self.screenshot,
            performance=self.performance,
            data_manager=self.data_manager
        )
        
        # Get test methods
        test_methods = [method for method in dir(test_suite) if method.startswith('test_')]
        
        self.logger.info(f"Found {len(test_methods)} test methods")
        
        # Run each test method
        for test_method_name in test_methods:
            await self._run_single_test(test_suite, test_method_name)
        
        self.logger.info(f"✅ Test suite {test_suite_name} completed")
    
    async def _run_single_test(self, test_suite, test_method_name: str):
        """Run a single test method."""
        test_start_time = datetime.now()
        self.logger.test_start(test_method_name)
        
        try:
            # Start performance timer
            self.performance.start_timer(test_method_name)
            
            # Run the test
            test_method = getattr(test_suite, test_method_name)
            await test_method()
            
            # End performance timer
            duration = self.performance.end_timer(test_method_name)
            
            # Record success
            test_result = {
                'name': test_method_name,
                'status': 'passed',
                'duration': duration,
                'start_time': test_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'error': None
            }
            
            self.test_results.append(test_result)
            self.logger.test_end(test_method_name, success=True)
            
        except Exception as e:
            # End performance timer
            duration = self.performance.end_timer(test_method_name)
            
            # Record failure
            test_result = {
                'name': test_method_name,
                'status': 'failed',
                'duration': duration,
                'start_time': test_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'error': str(e)
            }
            
            self.test_results.append(test_result)
            self.logger.test_end(test_method_name, success=False)
            self.logger.error(f"Test {test_method_name} failed: {e}")
            
            # Take screenshot on failure
            if self.config.screenshot_on_failure:
                await self.screenshot.take_screenshot(
                    self.page, 
                    f"failure_{test_method_name}",
                    full_page=True
                )
    
    async def run_all_tests(self):
        """Run all test suites."""
        self.logger.info("🚀 Starting E2E test execution...")
        
        try:
            # Set up test environment
            await self.setup()
            
            # Run Content Pillar tests
            if self.config.is_feature_enabled('content_pillar'):
                await self.run_test_suite(ContentPillarE2ETestSuite, "Content Pillar")
            
            # Add other test suites here as they are implemented
            # if self.config.is_feature_enabled('insights_pillar'):
            #     await self.run_test_suite(InsightsPillarE2ETestSuite, "Insights Pillar")
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            raise
        
        finally:
            # Tear down test environment
            await self.teardown()
            
            # Generate reports
            await self._generate_reports()
    
    async def _generate_reports(self):
        """Generate test reports."""
        self.logger.info("📊 Generating test reports...")
        
        # Generate HTML report
        if self.config.generate_html_report:
            html_report_path = self.report_generator.generate_html_report(self.test_results)
            self.logger.info(f"HTML report generated: {html_report_path}")
        
        # Generate JSON report
        if self.config.generate_json_report:
            json_report_path = self.report_generator.generate_json_report(self.test_results)
            self.logger.info(f"JSON report generated: {json_report_path}")
        
        # Print summary
        self._print_test_summary()
    
    def _print_test_summary(self):
        """Print test execution summary."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['status'] == 'passed')
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("📊 E2E TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print("="*60)
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'failed':
                    print(f"   - {result['name']}: {result['error']}")
        
        print("\n🎯 PERFORMANCE METRICS:")
        performance_metrics = self.performance.get_metrics()
        for test_name, duration in performance_metrics.items():
            print(f"   - {test_name}: {duration:.2f}s")
        
        print("="*60)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run E2E tests for Symphainy Platform")
    parser.add_argument("--environment", "-e", default="test", 
                       choices=["test", "development", "staging", "production"],
                       help="Test environment")
    parser.add_argument("--config", "-c", type=str, help="Configuration file path")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--screenshot", action="store_true", help="Take screenshots")
    parser.add_argument("--video", action="store_true", help="Record video")
    parser.add_argument("--report-dir", type=str, help="Report directory")
    parser.add_argument("--test-files-dir", type=str, help="Test files directory")
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        config = TestConfig.from_file(args.config)
    else:
        config = get_config_for_environment(args.environment)
    
    # Override configuration with command line arguments
    if args.headless is not None:
        config.headless = args.headless
    if args.debug is not None:
        config.debug_mode = args.debug
    if args.verbose is not None:
        config.verbose_logging = args.verbose
    if args.screenshot is not None:
        config.take_screenshots = args.screenshot
    if args.video is not None:
        config.record_video = args.video
    if args.report_dir:
        config.report_dir = args.report_dir
    if args.test_files_dir:
        config.test_files_dir = args.test_files_dir
    
    # Validate configuration
    if not config.validate():
        print("❌ Configuration validation failed")
        sys.exit(1)
    
    # Create and run test runner
    runner = E2ETestRunner(config)
    
    try:
        await runner.run_all_tests()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
