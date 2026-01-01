#!/usr/bin/env python3
"""
Test Dependencies Helper

Provides shared fixtures and helpers for cross-pillar test dependencies:
- Parsed files for Insights Pillar
- Uploaded files for Operations Pillar
- Pillar outputs for Business Outcomes Pillar
"""

import pytest
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

TIMEOUT = 60.0


@dataclass
class ParsedFile:
    """Represents a parsed file ready for use in tests."""
    file_id: str
    file_type: str
    filename: str
    parsed: bool = True
    metadata: Optional[Dict[str, Any]] = None
    client: Any = None  # ProductionTestClient instance


@dataclass
class UploadedFile:
    """Represents an uploaded file (may or may not be parsed)."""
    file_id: str
    file_type: str
    filename: str
    parsed: bool = False
    metadata: Optional[Dict[str, Any]] = None
    client: Any = None  # ProductionTestClient instance


class TestDependencyHelper:
    """Helper class for managing test dependencies across pillars."""
    
    def __init__(self, production_client):
        self.client = production_client
        self._parsed_files: List[ParsedFile] = []
        self._uploaded_files: List[UploadedFile] = []
    
    async def create_parsed_file(
        self,
        file_type: str = "csv",
        content: Optional[bytes] = None,
        filename: Optional[str] = None
    ) -> ParsedFile:
        """
        Create a parsed file for use in Insights Pillar tests.
        
        Args:
            file_type: File type (csv, xlsx, pdf, docx, etc.)
            content: File content (if None, generates default content)
            filename: Filename (if None, generates unique filename)
        
        Returns:
            ParsedFile object with file_id and metadata
        """
        # Generate default content if not provided
        if content is None:
            content = self._generate_default_content(file_type)
        
        if filename is None:
            filename = f"parsed_{file_type}_{uuid.uuid4().hex[:8]}.{file_type}"
        
        # Step 1: Upload file
        mime_type = self._get_mime_type(file_type)
        files = {"file": (filename, content, mime_type)}
        
        upload_response = await self.client.post(
            "/api/v1/content-pillar/upload-file",
            files=files,
            timeout=TIMEOUT
        )
        
        assert upload_response.status_code in [200, 201], \
            f"❌ File upload failed: {upload_response.status_code} - {upload_response.text}"
        
        upload_data = upload_response.json()
        file_id = upload_data.get("file_id") or upload_data.get("uuid") or upload_data.get("id")
        assert file_id, f"❌ Upload response missing file_id: {upload_data}"
        
        # Step 2: Parse file
        parse_response = await self.client.post(
            f"/api/v1/content-pillar/process-file/{file_id}",
            json={"action": "parse"},
            timeout=TIMEOUT
        )
        
        assert parse_response.status_code in [200, 201, 202], \
            f"❌ File parsing failed: {parse_response.status_code} - {parse_response.text}"
        
        # Step 3: Verify file is parsed (get file details)
        details_response = await self.client.get(
            f"/api/v1/content-pillar/get-file-details/{file_id}",
            timeout=TIMEOUT
        )
        
        assert details_response.status_code == 200, \
            f"❌ File details failed: {details_response.status_code} - {details_response.text}"
        
        details_data = details_response.json()
        
        # Create ParsedFile object
        parsed_file = ParsedFile(
            file_id=file_id,
            file_type=file_type,
            filename=filename,
            parsed=True,
            metadata=details_data,
            client=self.client
        )
        
        self._parsed_files.append(parsed_file)
        return parsed_file
    
    async def create_uploaded_file(
        self,
        file_type: str = "csv",
        content: Optional[bytes] = None,
        filename: Optional[str] = None,
        parse: bool = False
    ) -> UploadedFile:
        """
        Create an uploaded file for use in Operations Pillar tests.
        
        Args:
            file_type: File type (csv, docx, pdf, etc.)
            content: File content (if None, generates default content)
            filename: Filename (if None, generates unique filename)
            parse: Whether to parse the file after upload
        
        Returns:
            UploadedFile object with file_id and metadata
        """
        # Generate default content if not provided
        if content is None:
            content = self._generate_default_content(file_type)
        
        if filename is None:
            filename = f"uploaded_{file_type}_{uuid.uuid4().hex[:8]}.{file_type}"
        
        # Upload file
        mime_type = self._get_mime_type(file_type)
        files = {"file": (filename, content, mime_type)}
        
        upload_response = await self.client.post(
            "/api/v1/content-pillar/upload-file",
            files=files,
            timeout=TIMEOUT
        )
        
        assert upload_response.status_code in [200, 201], \
            f"❌ File upload failed: {upload_response.status_code} - {upload_response.text}"
        
        upload_data = upload_response.json()
        file_id = upload_data.get("file_id") or upload_data.get("uuid") or upload_data.get("id")
        assert file_id, f"❌ Upload response missing file_id: {upload_data}"
        
        # Optionally parse file
        is_parsed = False
        if parse:
            parse_response = await self.client.post(
                f"/api/v1/content-pillar/process-file/{file_id}",
                json={"action": "parse"},
                timeout=TIMEOUT
            )
            is_parsed = parse_response.status_code in [200, 201, 202]
        
        # Get file details
        details_response = await self.client.get(
            f"/api/v1/content-pillar/get-file-details/{file_id}",
            timeout=TIMEOUT
        )
        
        details_data = details_response.json() if details_response.status_code == 200 else {}
        
        # Create UploadedFile object
        uploaded_file = UploadedFile(
            file_id=file_id,
            file_type=file_type,
            filename=filename,
            parsed=is_parsed,
            metadata=details_data,
            client=self.client
        )
        
        self._uploaded_files.append(uploaded_file)
        return uploaded_file
    
    async def create_pillar_outputs(self) -> Dict[str, Any]:
        """
        Create outputs from all pillars for Business Outcomes Pillar tests.
        
        Returns:
            Dictionary with outputs from Content, Insights, and Operations pillars
        """
        outputs = {
            "content_pillar": {},
            "insights_pillar": {},
            "operations_pillar": {}
        }
        
        # Content Pillar: Create parsed file
        parsed_file = await self.create_parsed_file(file_type="csv")
        outputs["content_pillar"] = {
            "file_id": parsed_file.file_id,
            "file_type": parsed_file.file_type,
            "filename": parsed_file.filename,
            "parsed": True
        }
        
        # Insights Pillar: Analyze the parsed file
        try:
            analyze_response = await self.client.post(
                "/api/v1/insights-pillar/analyze-content-for-insights",
                json={
                    "source_type": "file",
                    "file_id": parsed_file.file_id,
                    "content_type": "structured",
                    "analysis_options": {
                        "include_visualizations": True,
                        "include_tabular_summary": True
                    }
                },
                timeout=TIMEOUT
            )
            
            if analyze_response.status_code in [200, 201, 202]:
                analyze_data = analyze_response.json()
                analysis_id = analyze_data.get("analysis_id") or analyze_data.get("id")
                outputs["insights_pillar"] = {
                    "analysis_id": analysis_id,
                    "file_id": parsed_file.file_id,
                    "status": "completed" if analyze_response.status_code in [200, 201] else "processing"
                }
        except Exception as e:
            print(f"⚠️ Insights analysis failed (may not be implemented): {e}")
            outputs["insights_pillar"] = {"status": "not_available"}
        
        # Operations Pillar: Create SOP or workflow (if file is suitable)
        # For now, just mark as available
        outputs["operations_pillar"] = {
            "status": "available",
            "file_id": parsed_file.file_id
        }
        
        return outputs
    
    def _generate_default_content(self, file_type: str) -> bytes:
        """Generate default content for a file type."""
        content_map = {
            "csv": b"name,value\ntest1,100\ntest2,200\ntest3,300",
            "txt": b"This is a test text file for operations pillar.",
            "json": b'{"key": "value", "data": [1, 2, 3]}',
            "pdf": b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\nxref\n0 1\ntrailer\n<< /Size 1 >>\nstartxref\n9\n%%EOF",  # Minimal PDF
            "docx": b"PK\x03\x04",  # Minimal DOCX (ZIP header)
        }
        return content_map.get(file_type.lower(), b"Test file content")
    
    def _get_mime_type(self, file_type: str) -> str:
        """Get MIME type for a file type."""
        mime_map = {
            "csv": "text/csv",
            "txt": "text/plain",
            "json": "application/json",
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "bin": "application/octet-stream",
        }
        return mime_map.get(file_type.lower(), "application/octet-stream")


@pytest.fixture
def dependency_helper(production_client):
    """Fixture that provides TestDependencyHelper for cross-pillar dependencies."""
    return TestDependencyHelper(production_client)


@pytest.fixture
async def parsed_file_for_insights(production_client):
    """Fixture that provides a parsed file for Insights Pillar tests."""
    helper = TestDependencyHelper(production_client)
    return await helper.create_parsed_file(file_type="csv")


@pytest.fixture
async def uploaded_file_for_operations(production_client):
    """Fixture that provides an uploaded file for Operations Pillar tests."""
    helper = TestDependencyHelper(production_client)
    return await helper.create_uploaded_file(file_type="csv", parse=False)


@pytest.fixture
async def parsed_file_for_operations(production_client):
    """Fixture that provides a parsed file for Operations Pillar tests (if needed)."""
    helper = TestDependencyHelper(production_client)
    return await helper.create_uploaded_file(file_type="csv", parse=True)


@pytest.fixture
async def pillar_outputs_for_business_outcomes(production_client):
    """Fixture that provides outputs from all pillars for Business Outcomes tests."""
    helper = TestDependencyHelper(production_client)
    outputs = await helper.create_pillar_outputs()
    # Add client reference for convenience
    outputs['_client'] = production_client
    return outputs

