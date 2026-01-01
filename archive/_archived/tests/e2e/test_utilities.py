#!/usr/bin/env python3
"""
E2E Test Utilities

Utility functions and helpers for E2E testing.
"""

import os
import time
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from playwright.async_api import Page, Browser, BrowserContext, expect
from playwright.sync_api import sync_playwright


class TestLogger:
    """Enhanced logging for E2E tests."""
    
    def __init__(self, name: str = "E2E_Test", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Create file handler
        file_handler = logging.FileHandler('e2e_test.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def test_start(self, test_name: str):
        """Log test start."""
        self.logger.info(f"🧪 Starting test: {test_name}")
    
    def test_end(self, test_name: str, success: bool = True):
        """Log test end."""
        status = "✅ PASSED" if success else "❌ FAILED"
        self.logger.info(f"{status}: {test_name}")


class TestScreenshot:
    """Screenshot utilities for E2E tests."""
    
    def __init__(self, screenshot_dir: str = "test_screenshots"):
        self.screenshot_dir = screenshot_dir
        self.ensure_directory()
    
    def ensure_directory(self):
        """Ensure screenshot directory exists."""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    async def take_screenshot(self, page: Page, name: str, full_page: bool = True):
        """Take a screenshot of the current page."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        await page.screenshot(
            path=filepath,
            full_page=full_page
        )
        
        return filepath
    
    async def take_element_screenshot(self, page: Page, selector: str, name: str):
        """Take a screenshot of a specific element."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        element = await page.query_selector(selector)
        if element:
            await element.screenshot(path=filepath)
            return filepath
        
        return None


class TestPerformance:
    """Performance measurement utilities for E2E tests."""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, name: str):
        """Start a performance timer."""
        self.start_times[name] = time.time()
    
    def end_timer(self, name: str) -> float:
        """End a performance timer and return duration."""
        if name not in self.start_times:
            return 0.0
        
        duration = time.time() - self.start_times[name]
        self.metrics[name] = duration
        del self.start_times[name]
        return duration
    
    def get_metrics(self) -> Dict[str, float]:
        """Get all performance metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all performance metrics."""
        self.metrics.clear()
        self.start_times.clear()


class TestDataManager:
    """Test data management utilities."""
    
    def __init__(self, test_data_dir: str = "test_data"):
        self.test_data_dir = test_data_dir
        self.ensure_directory()
    
    def ensure_directory(self):
        """Ensure test data directory exists."""
        if not os.path.exists(self.test_data_dir):
            os.makedirs(self.test_data_dir)
    
    def load_test_data(self, filename: str) -> Dict[str, Any]:
        """Load test data from JSON file."""
        filepath = os.path.join(self.test_data_dir, filename)
        
        if not os.path.exists(filepath):
            return {}
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def save_test_data(self, filename: str, data: Dict[str, Any]):
        """Save test data to JSON file."""
        filepath = os.path.join(self.test_data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def cleanup_test_data(self):
        """Clean up test data files."""
        if os.path.exists(self.test_data_dir):
            for filename in os.listdir(self.test_data_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.test_data_dir, filename))


class TestAssertions:
    """Enhanced assertions for E2E tests."""
    
    def __init__(self, page: Page):
        self.page = page
    
    async def assert_element_visible(self, selector: str, timeout: int = 5000):
        """Assert that an element is visible."""
        await expect(self.page.locator(selector)).to_be_visible(timeout=timeout)
    
    async def assert_element_hidden(self, selector: str, timeout: int = 5000):
        """Assert that an element is hidden."""
        await expect(self.page.locator(selector)).to_be_hidden(timeout=timeout)
    
    async def assert_text_content(self, selector: str, expected_text: str, timeout: int = 5000):
        """Assert that an element contains expected text."""
        await expect(self.page.locator(selector)).to_contain_text(expected_text, timeout=timeout)
    
    async def assert_url_contains(self, expected_url: str, timeout: int = 5000):
        """Assert that the current URL contains expected text."""
        await expect(self.page).to_have_url(expected_url, timeout=timeout)
    
    async def assert_element_count(self, selector: str, expected_count: int, timeout: int = 5000):
        """Assert that the number of elements matches expected count."""
        elements = await self.page.query_selector_all(selector)
        assert len(elements) == expected_count, f"Expected {expected_count} elements, found {len(elements)}"
    
    async def assert_file_downloaded(self, filename: str, timeout: int = 10000):
        """Assert that a file was downloaded."""
        # This would need to be implemented based on the download mechanism
        # For now, we'll just check if the file exists in the downloads directory
        downloads_dir = os.path.expanduser("~/Downloads")
        filepath = os.path.join(downloads_dir, filename)
        
        # Wait for file to appear
        start_time = time.time()
        while time.time() - start_time < timeout / 1000:
            if os.path.exists(filepath):
                return True
            await asyncio.sleep(0.1)
        
        assert False, f"File {filename} was not downloaded within {timeout}ms"


class TestHelpers:
    """General test helper functions."""
    
    def __init__(self, page: Page):
        self.page = page
    
    async def wait_for_page_load(self, timeout: int = 30000):
        """Wait for page to fully load."""
        await self.page.wait_for_load_state('networkidle', timeout=timeout)
    
    async def wait_for_element(self, selector: str, timeout: int = 5000):
        """Wait for an element to appear."""
        await self.page.wait_for_selector(selector, timeout=timeout)
    
    async def wait_for_text(self, text: str, timeout: int = 5000):
        """Wait for text to appear on the page."""
        await self.page.wait_for_selector(f"text={text}", timeout=timeout)
    
    async def scroll_to_element(self, selector: str):
        """Scroll to an element."""
        element = await self.page.query_selector(selector)
        if element:
            await element.scroll_into_view_if_needed()
    
    async def click_and_wait(self, selector: str, wait_selector: str = None, timeout: int = 5000):
        """Click an element and wait for a response."""
        await self.page.click(selector)
        
        if wait_selector:
            await self.page.wait_for_selector(wait_selector, timeout=timeout)
        else:
            await self.page.wait_for_load_state('networkidle', timeout=timeout)
    
    async def fill_and_submit_form(self, form_data: Dict[str, str]):
        """Fill and submit a form with provided data."""
        for field, value in form_data.items():
            await self.page.fill(f"input[name='{field}']", value)
        
        await self.page.click("button[type='submit']")
        await self.page.wait_for_load_state('networkidle')
    
    async def upload_file(self, file_input_selector: str, file_path: str):
        """Upload a file using the file input."""
        await self.page.set_input_files(file_input_selector, file_path)
        await self.page.wait_for_load_state('networkidle')
    
    async def select_dropdown_option(self, select_selector: str, option_value: str):
        """Select an option from a dropdown."""
        await self.page.select_option(select_selector, option_value)
        await self.page.wait_for_load_state('networkidle')
    
    async def check_checkbox(self, checkbox_selector: str):
        """Check a checkbox."""
        await self.page.check(checkbox_selector)
        await self.page.wait_for_load_state('networkidle')
    
    async def uncheck_checkbox(self, checkbox_selector: str):
        """Uncheck a checkbox."""
        await self.page.uncheck(checkbox_selector)
        await self.page.wait_for_load_state('networkidle')
    
    async def hover_element(self, selector: str):
        """Hover over an element."""
        await self.page.hover(selector)
    
    async def double_click_element(self, selector: str):
        """Double-click an element."""
        await self.page.dblclick(selector)
    
    async def right_click_element(self, selector: str):
        """Right-click an element."""
        await self.page.click(selector, button='right')
    
    async def press_key(self, key: str):
        """Press a key."""
        await self.page.keyboard.press(key)
    
    async def type_text(self, text: str):
        """Type text."""
        await self.page.keyboard.type(text)
    
    async def clear_input(self, selector: str):
        """Clear an input field."""
        await self.page.fill(selector, "")
    
    async def get_element_text(self, selector: str) -> str:
        """Get text content of an element."""
        element = await self.page.query_selector(selector)
        if element:
            return await element.text_content()
        return ""
    
    async def get_element_attribute(self, selector: str, attribute: str) -> str:
        """Get attribute value of an element."""
        element = await self.page.query_selector(selector)
        if element:
            return await element.get_attribute(attribute)
        return ""
    
    async def is_element_visible(self, selector: str) -> bool:
        """Check if an element is visible."""
        try:
            await self.page.wait_for_selector(selector, timeout=1000)
            return True
        except:
            return False
    
    async def is_element_enabled(self, selector: str) -> bool:
        """Check if an element is enabled."""
        element = await self.page.query_selector(selector)
        if element:
            return await element.is_enabled()
        return False
    
    async def get_page_title(self) -> str:
        """Get the page title."""
        return await self.page.title()
    
    async def get_current_url(self) -> str:
        """Get the current URL."""
        return self.page.url
    
    async def navigate_back(self):
        """Navigate back in browser history."""
        await self.page.go_back()
        await self.page.wait_for_load_state('networkidle')
    
    async def navigate_forward(self):
        """Navigate forward in browser history."""
        await self.page.go_forward()
        await self.page.wait_for_load_state('networkidle')
    
    async def refresh_page(self):
        """Refresh the current page."""
        await self.page.reload()
        await self.page.wait_for_load_state('networkidle')


class TestReportGenerator:
    """Generate test reports."""
    
    def __init__(self, report_dir: str = "test_reports"):
        self.report_dir = report_dir
        self.ensure_directory()
    
    def ensure_directory(self):
        """Ensure report directory exists."""
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
    
    def generate_html_report(self, test_results: List[Dict[str, Any]], filename: str = None):
        """Generate HTML test report."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.html"
        
        filepath = os.path.join(self.report_dir, filename)
        
        # Generate HTML content
        html_content = self._generate_html_content(test_results)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return filepath
    
    def generate_json_report(self, test_results: List[Dict[str, Any]], filename: str = None):
        """Generate JSON test report."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.json"
        
        filepath = os.path.join(self.report_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        return filepath
    
    def _generate_html_content(self, test_results: List[Dict[str, Any]]) -> str:
        """Generate HTML content for test report."""
        total_tests = len(test_results)
        passed_tests = sum(1 for result in test_results if result.get('status') == 'passed')
        failed_tests = total_tests - passed_tests
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>E2E Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                .test-result {{ margin: 10px 0; padding: 10px; border-radius: 5px; }}
                .passed {{ background-color: #d4edda; border: 1px solid #c3e6cb; }}
                .failed {{ background-color: #f8d7da; border: 1px solid #f5c6cb; }}
                .test-name {{ font-weight: bold; }}
                .test-duration {{ color: #666; font-size: 0.9em; }}
                .test-error {{ color: #721c24; font-size: 0.9em; margin-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>E2E Test Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Tests: {total_tests}</p>
                <p>Passed: {passed_tests}</p>
                <p>Failed: {failed_tests}</p>
                <p>Success Rate: {(passed_tests/total_tests*100):.1f}%</p>
            </div>
            
            <div class="test-results">
                <h2>Test Results</h2>
        """
        
        for result in test_results:
            status = result.get('status', 'unknown')
            test_name = result.get('name', 'Unknown Test')
            duration = result.get('duration', 0)
            error = result.get('error', '')
            
            status_class = 'passed' if status == 'passed' else 'failed'
            
            html += f"""
                <div class="test-result {status_class}">
                    <div class="test-name">{test_name}</div>
                    <div class="test-duration">Duration: {duration:.2f}s</div>
                    {f'<div class="test-error">Error: {error}</div>' if error else ''}
                </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html


# Utility functions
def create_test_logger(name: str = "E2E_Test") -> TestLogger:
    """Create a test logger."""
    return TestLogger(name)

def create_test_screenshot(screenshot_dir: str = "test_screenshots") -> TestScreenshot:
    """Create a test screenshot utility."""
    return TestScreenshot(screenshot_dir)

def create_test_performance() -> TestPerformance:
    """Create a test performance utility."""
    return TestPerformance()

def create_test_data_manager(test_data_dir: str = "test_data") -> TestDataManager:
    """Create a test data manager."""
    return TestDataManager(test_data_dir)

def create_test_assertions(page: Page) -> TestAssertions:
    """Create test assertions utility."""
    return TestAssertions(page)

def create_test_helpers(page: Page) -> TestHelpers:
    """Create test helpers utility."""
    return TestHelpers(page)

def create_test_report_generator(report_dir: str = "test_reports") -> TestReportGenerator:
    """Create a test report generator."""
    return TestReportGenerator(report_dir)





