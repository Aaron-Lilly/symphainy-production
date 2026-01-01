#!/usr/bin/env python3
"""
Content Pillar E2E Test Cases - Individual Test Methods

Individual test case methods for Content Pillar E2E testing.
These methods are imported by the main test suite.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime


class ContentPillarTestCases:
    """Individual test case methods for Content Pillar E2E testing."""
    
    def __init__(self, test_suite):
        self.test_suite = test_suite
        self.page = test_suite.page
    
    async def test_landing_page_guide_agent_interaction(self):
        """
        Test Case 1: Landing Page GuideAgent Interaction
        
        Requirements:
        - Landing page welcomes user and introduces key elements
        - GuideAgent prompts user to understand their goals
        - GuideAgent suggests specific data to share
        - GuideAgent directs user to Content Pillar
        """
        print("\n🧪 Test Case 1: Landing Page GuideAgent Interaction")
        
        # Navigate to landing page
        await self.page.goto(self.test_suite.base_url)
        await self.page.wait_for_load_state('networkidle')
        
        # Verify landing page elements
        assert await self.page.is_visible("text=Welcome to Symphainy MVP"), "Landing page welcome message not found"
        assert await self.page.is_visible("text=GuideAgent"), "GuideAgent not found on landing page"
        assert await self.page.is_visible("text=Content Pillar"), "Content Pillar navigation not found"
        
        # Test GuideAgent interaction
        guide_agent_input = await self.page.query_selector("input[placeholder*='Ask the GuideAgent']")
        assert guide_agent_input, "GuideAgent input not found"
        
        # Simulate user goal input
        await guide_agent_input.fill("I want to analyze my customer data to understand payment patterns")
        await guide_agent_input.press("Enter")
        
        # Wait for GuideAgent response
        await self.page.wait_for_selector(".guide-agent-response", timeout=10000)
        
        # Verify GuideAgent suggests data sharing
        response_text = await self.page.text_content(".guide-agent-response")
        assert "customer data" in response_text.lower(), "GuideAgent should suggest customer data"
        assert "volumetric data" in response_text.lower() or "financial reports" in response_text.lower(), "GuideAgent should suggest specific data types"
        
        # Verify GuideAgent directs to Content Pillar
        assert "content pillar" in response_text.lower(), "GuideAgent should direct to Content Pillar"
        
        print("✅ Landing page GuideAgent interaction successful")
    
    async def test_content_pillar_dashboard_view(self):
        """
        Test Case 2: Content Pillar Dashboard View
        
        Requirements:
        - Dashboard view of available files
        - File uploader supporting multiple file types
        - Navigation to Content Pillar
        """
        print("\n🧪 Test Case 2: Content Pillar Dashboard View")
        
        # Navigate to Content Pillar
        await self.page.goto(self.test_suite.content_pillar_url)
        await self.page.wait_for_load_state('networkidle')
        
        # Verify dashboard elements
        assert await self.page.is_visible("text=Content Pillar Dashboard"), "Dashboard title not found"
        assert await self.page.is_visible("text=Available Files"), "Available files section not found"
        assert await self.page.is_visible("text=Upload Files"), "File uploader not found"
        
        # Verify file uploader supports multiple types
        file_input = await self.page.query_selector("input[type='file']")
        assert file_input, "File input not found"
        
        # Check accepted file types
        accept_attr = await file_input.get_attribute("accept")
        assert accept_attr, "File input should have accept attribute"
        assert ".csv" in accept_attr, "CSV files should be supported"
        assert ".json" in accept_attr, "JSON files should be supported"
        assert ".dat" in accept_attr, "Mainframe binary files should be supported"
        assert ".cpy" in accept_attr, "Copybook files should be supported"
        
        print("✅ Content Pillar dashboard view successful")
    
    async def test_file_upload_csv(self):
        """
        Test Case 3: CSV File Upload and Parsing
        
        Requirements:
        - Upload CSV file
        - Parse to AI-friendly format (parquet)
        - Preview data functionality
        """
        print("\n🧪 Test Case 3: CSV File Upload and Parsing")
        
        # Upload CSV file
        file_input = await self.page.query_selector("input[type='file']")
        await file_input.set_input_files(f"{self.test_suite.test_files_dir}/test_customers.csv")
        
        # Wait for upload processing
        await self.page.wait_for_selector(".upload-progress", timeout=10000)
        await self.page.wait_for_selector(".upload-complete", timeout=15000)
        
        # Verify file appears in dashboard
        assert await self.page.is_visible("text=test_customers.csv"), "Uploaded file not found in dashboard"
        
        # Test data preview
        preview_button = await self.page.query_selector("button[data-testid='preview-file']")
        assert preview_button, "Preview button not found"
        await preview_button.click()
        
        # Wait for preview modal
        await self.page.wait_for_selector(".data-preview-modal", timeout=5000)
        
        # Verify preview shows data
        preview_content = await self.page.text_content(".data-preview-modal")
        assert "customer_id" in preview_content, "Preview should show column headers"
        assert "Customer_1" in preview_content, "Preview should show sample data"
        
        # Verify parsing format selection
        format_selector = await self.page.query_selector("select[name='parsing-format']")
        assert format_selector, "Parsing format selector not found"
        
        # Select parquet format
        await format_selector.select_option("parquet")
        
        # Confirm parsing
        parse_button = await self.page.query_selector("button[data-testid='parse-file']")
        assert parse_button, "Parse button not found"
        await parse_button.click()
        
        # Wait for parsing completion
        await self.page.wait_for_selector(".parsing-complete", timeout=15000)
        
        # Verify parsed file status
        assert await self.page.is_visible("text=test_customers.parquet"), "Parsed file not found"
        assert await self.page.is_visible("text=Ready for Insights"), "File should be ready for Insights Pillar"
        
        print("✅ CSV file upload and parsing successful")
    
    async def test_file_upload_json(self):
        """
        Test Case 4: JSON File Upload and Parsing
        
        Requirements:
        - Upload JSON file
        - Parse to AI-friendly format (JSON Structured)
        - Preview data functionality
        """
        print("\n🧪 Test Case 4: JSON File Upload and Parsing")
        
        # Upload JSON file
        file_input = await self.page.query_selector("input[type='file']")
        await file_input.set_input_files(f"{self.test_suite.test_files_dir}/test_customers.json")
        
        # Wait for upload processing
        await self.page.wait_for_selector(".upload-progress", timeout=10000)
        await self.page.wait_for_selector(".upload-complete", timeout=15000)
        
        # Verify file appears in dashboard
        assert await self.page.is_visible("text=test_customers.json"), "Uploaded JSON file not found in dashboard"
        
        # Test data preview
        preview_button = await self.page.query_selector("button[data-testid='preview-file']")
        await preview_button.click()
        
        # Wait for preview modal
        await self.page.wait_for_selector(".data-preview-modal", timeout=5000)
        
        # Verify JSON preview shows structured data
        preview_content = await self.page.text_content(".data-preview-modal")
        assert "customers" in preview_content, "Preview should show JSON structure"
        assert "id" in preview_content, "Preview should show JSON fields"
        
        # Select JSON Structured format
        format_selector = await self.page.query_selector("select[name='parsing-format']")
        await format_selector.select_option("json_structured")
        
        # Confirm parsing
        parse_button = await self.page.query_selector("button[data-testid='parse-file']")
        await parse_button.click()
        
        # Wait for parsing completion
        await self.page.wait_for_selector(".parsing-complete", timeout=15000)
        
        # Verify parsed file status
        assert await self.page.is_visible("text=test_customers_structured.json"), "Parsed JSON file not found"
        assert await self.page.is_visible("text=Ready for Insights"), "File should be ready for Insights Pillar"
        
        print("✅ JSON file upload and parsing successful")
    
    async def test_mainframe_binary_file_upload(self):
        """
        Test Case 5: Mainframe Binary File Upload with Copybook
        
        Requirements:
        - Upload mainframe binary file (.dat)
        - Upload corresponding copybook (.cpy)
        - Parse using COBOL2CSV conversion
        - Preview converted data
        """
        print("\n🧪 Test Case 5: Mainframe Binary File Upload with Copybook")
        
        # Upload mainframe binary file
        file_input = await self.page.query_selector("input[type='file']")
        await file_input.set_input_files(f"{self.test_suite.test_files_dir}/test_mainframe.dat")
        
        # Wait for upload processing
        await self.page.wait_for_selector(".upload-progress", timeout=10000)
        await self.page.wait_for_selector(".upload-complete", timeout=15000)
        
        # Verify mainframe file detection
        assert await self.page.is_visible("text=Mainframe Binary File Detected"), "Mainframe file detection not found"
        assert await self.page.is_visible("text=Copybook Required"), "Copybook requirement not found"
        
        # Upload copybook file
        copybook_input = await self.page.query_selector("input[type='file'][accept*='.cpy']")
        assert copybook_input, "Copybook file input not found"
        await copybook_input.set_input_files(f"{self.test_suite.test_files_dir}/test_copybook.cpy")
        
        # Wait for copybook processing
        await self.page.wait_for_selector(".copybook-processed", timeout=10000)
        
        # Verify copybook parsing
        assert await self.page.is_visible("text=Copybook Parsed Successfully"), "Copybook parsing not found"
        assert await self.page.is_visible("text=CUSTOMER-RECORD"), "Copybook structure not found"
        
        # Test COBOL2CSV conversion
        convert_button = await self.page.query_selector("button[data-testid='convert-cobol']")
        assert convert_button, "COBOL conversion button not found"
        await convert_button.click()
        
        # Wait for conversion completion
        await self.page.wait_for_selector(".conversion-complete", timeout=20000)
        
        # Verify converted data preview
        preview_button = await self.page.query_selector("button[data-testid='preview-converted']")
        await preview_button.click()
        
        # Wait for preview modal
        await self.page.wait_for_selector(".data-preview-modal", timeout=5000)
        
        # Verify converted data structure
        preview_content = await self.page.text_content(".data-preview-modal")
        assert "CUSTOMER_ID" in preview_content, "Converted data should show COBOL fields"
        assert "CUSTOMER_NAME" in preview_content, "Converted data should show COBOL fields"
        
        # Verify final parsed file
        assert await self.page.is_visible("text=test_mainframe_converted.csv"), "Converted file not found"
        assert await self.page.is_visible("text=Ready for Insights"), "File should be ready for Insights Pillar"
        
        print("✅ Mainframe binary file upload and conversion successful")
    
    async def test_content_liaison_agent_interaction(self):
        """
        Test Case 6: ContentLiaisonAgent Interaction
        
        Requirements:
        - ContentLiaisonAgent allows interaction with parsed files
        - Agent can answer questions about uploaded data
        - Agent provides guidance on data preparation
        """
        print("\n🧪 Test Case 6: ContentLiaisonAgent Interaction")
        
        # Ensure we have a parsed file available
        if not await self.page.is_visible("text=Ready for Insights"):
            # Upload and parse a file first
            await self.test_file_upload_csv()
        
        # Open ContentLiaisonAgent chat
        liaison_chat_button = await self.page.query_selector("button[data-testid='open-liaison-chat']")
        assert liaison_chat_button, "ContentLiaisonAgent chat button not found"
        await liaison_chat_button.click()
        
        # Wait for chat panel to open
        await self.page.wait_for_selector(".liaison-chat-panel", timeout=5000)
        
        # Test agent interaction
        chat_input = await self.page.query_selector("input[placeholder*='Ask about your files']")
        assert chat_input, "Liaison chat input not found"
        
        # Ask about uploaded data
        await chat_input.fill("What files do I have uploaded and what can I do with them?")
        await chat_input.press("Enter")
        
        # Wait for agent response
        await self.page.wait_for_selector(".liaison-response", timeout=10000)
        
        # Verify agent response
        response_text = await self.page.text_content(".liaison-response")
        assert "test_customers" in response_text, "Agent should mention uploaded files"
        assert "insights" in response_text.lower(), "Agent should mention next steps"
        
        # Test specific data question
        await chat_input.fill("Can you tell me about the structure of my customer data?")
        await chat_input.press("Enter")
        
        # Wait for agent response
        await self.page.wait_for_selector(".liaison-response", timeout=10000)
        
        # Verify agent provides data structure information
        response_text = await self.page.text_content(".liaison-response")
        assert "customer_id" in response_text or "columns" in response_text.lower(), "Agent should describe data structure"
        
        print("✅ ContentLiaisonAgent interaction successful")
    
    async def test_data_preparation_for_insights_pillar(self):
        """
        Test Case 7: Data Preparation for Insights Pillar
        
        Requirements:
        - Files are properly prepared for Insights Pillar
        - Data is in correct format (parquet, JSON Structured, JSON Chunks)
        - User can proceed to Insights Pillar
        """
        print("\n🧪 Test Case 7: Data Preparation for Insights Pillar")
        
        # Ensure we have parsed files ready
        if not await self.page.is_visible("text=Ready for Insights"):
            await self.test_file_upload_csv()
        
        # Verify files are ready for Insights Pillar
        ready_files = await self.page.query_selector_all(".file-ready-for-insights")
        assert len(ready_files) > 0, "No files ready for Insights Pillar"
        
        # Test file format verification
        for file_element in ready_files:
            file_name = await file_element.text_content()
            assert any(ext in file_name for ext in ['.parquet', '.json', '.csv']), f"File {file_name} should be in correct format"
        
        # Test navigation to Insights Pillar
        insights_button = await self.page.query_selector("button[data-testid='go-to-insights']")
        assert insights_button, "Go to Insights Pillar button not found"
        
        # Verify button is enabled
        is_enabled = await insights_button.is_enabled()
        assert is_enabled, "Insights Pillar button should be enabled"
        
        # Click to navigate to Insights Pillar
        await insights_button.click()
        
        # Wait for navigation
        await self.page.wait_for_load_state('networkidle')
        
        # Verify we're on Insights Pillar page
        current_url = self.page.url
        assert "insights" in current_url.lower(), "Should navigate to Insights Pillar"
        
        # Verify files are available in Insights Pillar
        assert await self.page.is_visible("text=test_customers"), "Uploaded files should be available in Insights Pillar"
        
        print("✅ Data preparation for Insights Pillar successful")
    
    async def test_error_handling_and_validation(self):
        """
        Test Case 8: Error Handling and Validation
        
        Requirements:
        - Proper error handling for invalid files
        - Validation of file types and formats
        - User-friendly error messages
        """
        print("\n🧪 Test Case 8: Error Handling and Validation")
        
        # Test invalid file type upload
        invalid_file_path = f"{self.test_suite.test_files_dir}/invalid_file.txt"
        with open(invalid_file_path, 'w') as f:
            f.write("This is not a valid data file")
        
        file_input = await self.page.query_selector("input[type='file']")
        await file_input.set_input_files(invalid_file_path)
        
        # Wait for error handling
        await self.page.wait_for_selector(".upload-error", timeout=10000)
        
        # Verify error message
        error_message = await self.page.text_content(".upload-error")
        assert "unsupported file type" in error_message.lower() or "invalid file" in error_message.lower(), "Should show appropriate error message"
        
        # Test corrupted file upload
        corrupted_file_path = f"{self.test_suite.test_files_dir}/corrupted.csv"
        with open(corrupted_file_path, 'w') as f:
            f.write("This is not a valid CSV file\nwith,invalid,structure")
        
        await file_input.set_input_files(corrupted_file_path)
        
        # Wait for processing error
        await self.page.wait_for_selector(".processing-error", timeout=10000)
        
        # Verify error message
        error_message = await self.page.text_content(".processing-error")
        assert "error" in error_message.lower() or "invalid" in error_message.lower(), "Should show processing error message"
        
        print("✅ Error handling and validation successful")
    
    async def test_file_management_operations(self):
        """
        Test Case 9: File Management Operations
        
        Requirements:
        - Delete uploaded files
        - Rename files
        - View file details
        - Re-parse files with different formats
        """
        print("\n🧪 Test Case 9: File Management Operations")
        
        # Ensure we have files to manage
        if not await self.page.is_visible("text=test_customers"):
            await self.test_file_upload_csv()
        
        # Test file details view
        details_button = await self.page.query_selector("button[data-testid='view-file-details']")
        assert details_button, "File details button not found"
        await details_button.click()
        
        # Wait for details modal
        await self.page.wait_for_selector(".file-details-modal", timeout=5000)
        
        # Verify details content
        details_content = await self.page.text_content(".file-details-modal")
        assert "test_customers" in details_content, "File details should show file name"
        assert "rows" in details_content.lower() or "columns" in details_content.lower(), "File details should show data info"
        
        # Close details modal
        close_button = await self.page.query_selector("button[data-testid='close-details']")
        await close_button.click()
        
        # Test file rename
        rename_button = await self.page.query_selector("button[data-testid='rename-file']")
        assert rename_button, "Rename button not found"
        await rename_button.click()
        
        # Wait for rename input
        await self.page.wait_for_selector("input[data-testid='rename-input']", timeout=5000)
        
        # Enter new name
        rename_input = await self.page.query_selector("input[data-testid='rename-input']")
        await rename_input.fill("renamed_customers")
        await rename_input.press("Enter")
        
        # Verify rename
        await self.page.wait_for_selector("text=renamed_customers", timeout=5000)
        
        # Test file deletion
        delete_button = await self.page.query_selector("button[data-testid='delete-file']")
        assert delete_button, "Delete button not found"
        await delete_button.click()
        
        # Confirm deletion
        confirm_button = await self.page.query_selector("button[data-testid='confirm-delete']")
        await confirm_button.click()
        
        # Verify file is deleted
        await self.page.wait_for_selector("text=renamed_customers", state="hidden", timeout=5000)
        
        print("✅ File management operations successful")





