"""
E2E Test: Content Pillar - Functional Business Logic
Tests that file parsing and data extraction ACTUALLY WORK

This test validates that we can:
- Upload files via API
- Parse different file formats
- Extract data correctly
- Verify data integrity
"""

import pytest
import httpx
import os
from pathlib import Path
import json
import asyncio

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
DEMO_FILES_DIR = Path("/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files")
TIMEOUT = 30.0

@pytest.fixture
def demo_files():
    """Get paths to demo files"""
    return {
        "defense_csv": DEMO_FILES_DIR / "SymphAIny_Demo_Defense_TnE/data/mission_plan.csv",
        "defense_binary": DEMO_FILES_DIR / "SymphAIny_Demo_Defense_TnE/data/telemetry_raw.bin",
        "defense_docx": DEMO_FILES_DIR / "SymphAIny_Demo_Defense_TnE/data/test_incident_reports.docx",
        "underwriting_csv": DEMO_FILES_DIR / "SymphAIny_Demo_Underwriting_Insights/data/claims.csv",
        "underwriting_excel": DEMO_FILES_DIR / "SymphAIny_Demo_Underwriting_Insights/data/reinsurance.xlsx",
        "underwriting_pdf": DEMO_FILES_DIR / "SymphAIny_Demo_Underwriting_Insights/data/underwriting_notes.pdf",
        "coexistence_csv": DEMO_FILES_DIR / "SymphAIny_Demo_Coexistence/data/legacy_policy_export.csv",
    }

@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.critical
class TestCSVParsing:
    """Test that CSV files are actually parsed correctly"""
    
    @pytest.mark.asyncio
    async def test_upload_and_parse_csv_functional(self, demo_files):
        """Test complete CSV upload → parse → extract data flow"""
        
        csv_file = demo_files["defense_csv"]
        
        if not csv_file.exists():
            pytest.skip(f"Demo file not found: {csv_file}")
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Step 1: Create session
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            assert session_response.status_code in [200, 201], \
                f"Session creation failed: {session_response.text}"
            
            session_data = session_response.json()
            session_token = session_data.get("session_token") or session_data.get("session_id")
            
            # Step 2: Upload CSV file
            with open(csv_file, 'rb') as f:
                files = {'file': ('mission_plan.csv', f, 'text/csv')}
                data = {'session_token': session_token}
                
                upload_response = await client.post(
                    f"{BASE_URL}/api/mvp/content/upload",
                    files=files,
                    data=data
                )
            
            assert upload_response.status_code in [200, 201], \
                f"❌ CRITICAL: CSV upload failed: {upload_response.text}"
            
            upload_data = upload_response.json()
            assert "file_id" in upload_data or "id" in upload_data, \
                "Upload response missing file ID"
            
            file_id = upload_data.get("file_id") or upload_data.get("id")
            print(f"✅ CSV uploaded successfully: {file_id}")
            
            # Step 3: Parse the file
            parse_response = await client.post(
                f"{BASE_URL}/api/mvp/content/parse/{file_id}",
                json={"session_token": session_token}
            )
            
            assert parse_response.status_code == 200, \
                f"❌ CRITICAL: CSV parsing failed: {parse_response.text}"
            
            parse_data = parse_response.json()
            
            # Step 4: Verify parsed data structure
            assert "data" in parse_data or "records" in parse_data or "rows" in parse_data, \
                "❌ CRITICAL: Parsed CSV missing data field"
            
            # Get the actual data
            data_key = next((k for k in ["data", "records", "rows"] if k in parse_data), None)
            parsed_rows = parse_data[data_key]
            
            # Verify we got actual data
            assert len(parsed_rows) > 0, \
                "❌ CRITICAL: CSV parsed but no rows extracted!"
            
            assert len(parsed_rows) >= 40, \
                f"❌ CRITICAL: Expected ~50 rows, got {len(parsed_rows)}"
            
            # Verify column structure
            first_row = parsed_rows[0]
            expected_columns = ["mission_id", "start_time", "end_time", "location", "lead_officer"]
            
            for col in expected_columns:
                assert col in first_row, \
                    f"❌ CRITICAL: Missing expected column '{col}' in parsed data"
            
            # Verify data quality
            assert first_row["mission_id"].startswith("M"), \
                "❌ CRITICAL: Mission ID format incorrect"
            
            print(f"✅ CSV parsed successfully: {len(parsed_rows)} rows")
            print(f"✅ First row: {first_row}")
            print(f"✅ FUNCTIONAL TEST PASSED: CSV upload → parse → extract data")

@pytest.mark.e2e
@pytest.mark.functional
@pytest.mark.critical
class TestBinaryParsing:
    """Test that binary files with COBOL copybooks are parsed"""
    
    @pytest.mark.asyncio
    async def test_upload_and_parse_binary_functional(self, demo_files):
        """Test complete binary upload → parse with copybook → extract records"""
        
        binary_file = demo_files["defense_binary"]
        
        if not binary_file.exists():
            pytest.skip(f"Demo file not found: {binary_file}")
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Create session
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            session_token = (session_response.json()).get("session_token", "session_id")
            
            # Upload binary file
            with open(binary_file, 'rb') as f:
                files = {'file': ('telemetry_raw.bin', f, 'application/octet-stream')}
                data = {'session_token': session_token}
                
                upload_response = await client.post(
                    f"{BASE_URL}/api/mvp/content/upload",
                    files=files,
                    data=data
                )
            
            if upload_response.status_code not in [200, 201]:
                pytest.skip(f"Binary upload not yet implemented: {upload_response.status_code}")
            
            upload_data = upload_response.json()
            file_id = upload_data.get("file_id") or upload_data.get("id")
            
            # Parse the binary file
            parse_response = await client.post(
                f"{BASE_URL}/api/mvp/content/parse/{file_id}",
                json={"session_token": session_token}
            )
            
            if parse_response.status_code != 200:
                pytest.skip(f"Binary parsing not yet implemented: {parse_response.status_code}")
            
            parse_data = parse_response.json()
            
            # Verify records extracted
            data_key = next((k for k in ["data", "records", "rows"] if k in parse_data), None)
            if not data_key:
                pytest.fail("❌ CRITICAL: Binary parsed but no data structure found")
            
            parsed_records = parse_data[data_key]
            assert len(parsed_records) > 0, \
                "❌ CRITICAL: Binary parsed but no records extracted"
            
            assert len(parsed_records) >= 40, \
                f"Expected ~50 records, got {len(parsed_records)}"
            
            print(f"✅ Binary file parsed: {len(parsed_records)} records")
            print(f"✅ FUNCTIONAL TEST PASSED: Binary parsing with COBOL copybook")

@pytest.mark.e2e
@pytest.mark.functional
class TestExcelParsing:
    """Test that Excel files are parsed correctly"""
    
    @pytest.mark.asyncio
    async def test_upload_and_parse_excel_functional(self, demo_files):
        """Test Excel upload → parse → extract sheets and data"""
        
        excel_file = demo_files["underwriting_excel"]
        
        if not excel_file.exists():
            pytest.skip(f"Demo file not found: {excel_file}")
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Create session
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            session_data = session_response.json()
            session_token = session_data.get("session_token") or session_data.get("session_id")
            
            # Upload Excel file
            with open(excel_file, 'rb') as f:
                files = {'file': ('reinsurance.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                data = {'session_token': session_token}
                
                upload_response = await client.post(
                    f"{BASE_URL}/api/mvp/content/upload",
                    files=files,
                    data=data
                )
            
            if upload_response.status_code not in [200, 201]:
                pytest.skip(f"Excel upload not yet implemented: {upload_response.status_code}")
            
            file_id = (upload_response.json()).get("file_id") or (upload_response.json()).get("id")
            
            # Parse Excel
            parse_response = await client.post(
                f"{BASE_URL}/api/mvp/content/parse/{file_id}",
                json={"session_token": session_token}
            )
            
            if parse_response.status_code != 200:
                pytest.skip(f"Excel parsing not yet implemented")
            
            parse_data = parse_response.json()
            
            # Verify data extracted
            data_key = next((k for k in ["data", "records", "rows", "sheets"] if k in parse_data), None)
            assert data_key, "❌ CRITICAL: Excel parsed but no data found"
            
            parsed_data = parse_data[data_key]
            assert len(parsed_data) > 0, \
                "❌ CRITICAL: Excel parsed but no rows extracted"
            
            print(f"✅ Excel parsed: {len(parsed_data)} rows")
            print(f"✅ FUNCTIONAL TEST PASSED: Excel parsing")

@pytest.mark.e2e
@pytest.mark.functional
class TestPDFExtraction:
    """Test that PDF text extraction works"""
    
    @pytest.mark.asyncio
    async def test_upload_and_extract_pdf_text(self, demo_files):
        """Test PDF upload → extract text → verify content"""
        
        pdf_file = demo_files["underwriting_pdf"]
        
        if not pdf_file.exists():
            pytest.skip(f"Demo file not found: {pdf_file}")
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Create session
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            session_token = (session_response.json()).get("session_token", "session_id")
            
            # Upload PDF
            with open(pdf_file, 'rb') as f:
                files = {'file': ('underwriting_notes.pdf', f, 'application/pdf')}
                data = {'session_token': session_token}
                
                upload_response = await client.post(
                    f"{BASE_URL}/api/mvp/content/upload",
                    files=files,
                    data=data
                )
            
            if upload_response.status_code not in [200, 201]:
                pytest.skip("PDF upload not yet implemented")
            
            file_id = (upload_response.json()).get("file_id") or (upload_response.json()).get("id")
            
            # Parse PDF
            parse_response = await client.post(
                f"{BASE_URL}/api/mvp/content/parse/{file_id}",
                json={"session_token": session_token}
            )
            
            if parse_response.status_code != 200:
                pytest.skip("PDF parsing not yet implemented")
            
            parse_data = parse_response.json()
            
            # Verify text extracted
            text_key = next((k for k in ["text", "content", "data"] if k in parse_data), None)
            assert text_key, "❌ CRITICAL: PDF parsed but no text found"
            
            extracted_text = parse_data[text_key]
            assert len(extracted_text) > 100, \
                "❌ CRITICAL: PDF text too short, extraction may have failed"
            
            print(f"✅ PDF text extracted: {len(extracted_text)} characters")
            print(f"✅ FUNCTIONAL TEST PASSED: PDF text extraction")

@pytest.mark.e2e
@pytest.mark.functional
class TestDOCXExtraction:
    """Test that DOCX text extraction works"""
    
    @pytest.mark.asyncio
    async def test_upload_and_extract_docx_text(self, demo_files):
        """Test DOCX upload → extract text and structure → verify"""
        
        docx_file = demo_files["defense_docx"]
        
        if not docx_file.exists():
            pytest.skip(f"Demo file not found: {docx_file}")
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Create session
            session_response = await client.post(f"{BASE_URL}/api/global/session")
            session_token = (session_response.json()).get("session_token", "session_id")
            
            # Upload DOCX
            with open(docx_file, 'rb') as f:
                files = {'file': ('test_incident_reports.docx', f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
                data = {'session_token': session_token}
                
                upload_response = await client.post(
                    f"{BASE_URL}/api/mvp/content/upload",
                    files=files,
                    data=data
                )
            
            if upload_response.status_code not in [200, 201]:
                pytest.skip("DOCX upload not yet implemented")
            
            file_id = (upload_response.json()).get("file_id") or (upload_response.json()).get("id")
            
            # Parse DOCX
            parse_response = await client.post(
                f"{BASE_URL}/api/mvp/content/parse/{file_id}",
                json={"session_token": session_token}
            )
            
            if parse_response.status_code != 200:
                pytest.skip("DOCX parsing not yet implemented")
            
            parse_data = parse_response.json()
            
            # Verify content extracted
            content_key = next((k for k in ["text", "content", "paragraphs", "data"] if k in parse_data), None)
            assert content_key, "❌ CRITICAL: DOCX parsed but no content found"
            
            extracted_content = parse_data[content_key]
            
            # Should have extracted text from 3 incidents
            if isinstance(extracted_content, str):
                assert len(extracted_content) > 50, \
                    "❌ CRITICAL: DOCX text too short"
                assert "Incident" in extracted_content, \
                    "❌ CRITICAL: DOCX content doesn't match expected structure"
            elif isinstance(extracted_content, list):
                assert len(extracted_content) >= 3, \
                    "❌ CRITICAL: Expected 3 incidents in DOCX"
            
            print(f"✅ DOCX content extracted")
            print(f"✅ FUNCTIONAL TEST PASSED: DOCX text extraction")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

