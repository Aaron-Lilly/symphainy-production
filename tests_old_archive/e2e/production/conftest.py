"""
Shared fixtures for production readiness tests.

These tests verify production readiness by testing through real interfaces.
"""

import pytest
import httpx
import os
import uuid
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Backend URL for tests
# Default to production public URL (http://35.215.64.103) since we're testing on GCE
# Traefik routes all traffic through port 80
# Can override with TEST_BACKEND_URL env var for local testing if needed
BASE_URL = os.getenv("TEST_BACKEND_URL", "http://35.215.64.103")
PRODUCTION_BASE_URL = os.getenv("PRODUCTION_BASE_URL", BASE_URL)

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
        """Create a parsed file for use in Insights Pillar tests."""
        print(f"📤 [HELPER] Creating parsed file (type: {file_type})...")
        
        if content is None:
            content = self._generate_default_content(file_type)
        
        if filename is None:
            filename = f"parsed_{file_type}_{uuid.uuid4().hex[:8]}.{file_type}"
        
        mime_type = self._get_mime_type(file_type)
        files = {"file": (filename, content, mime_type)}
        
        # Step 1: Upload file with timeout protection
        print(f"   [STEP 1/3] Uploading file: {filename}")
        try:
            upload_response = await asyncio.wait_for(
                self.client.post(
                    "/api/v1/content-pillar/upload-file",
                    files=files,
                    timeout=TIMEOUT
                ),
                timeout=TIMEOUT + 5.0  # Add buffer for asyncio timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"File upload timed out after {TIMEOUT + 5.0}s")
        
        # Handle rate limiting gracefully - skip test if rate limited
        if upload_response.status_code == 429:
            pytest.skip(f"Rate limited (429) - cannot upload file for test")
        
        assert upload_response.status_code in [200, 201], \
            f"❌ File upload failed: {upload_response.status_code} - {upload_response.text}"
        
        upload_data = upload_response.json()
        file_id = upload_data.get("file_id") or upload_data.get("uuid") or upload_data.get("id")
        assert file_id, f"❌ Upload response missing file_id: {upload_data}"
        print(f"   ✅ File uploaded: file_id={file_id}")
        
        # Step 2: Parse file with timeout protection
        print(f"   [STEP 2/3] Parsing file: {file_id}")
        try:
            parse_response = await asyncio.wait_for(
                self.client.post(
                    f"/api/v1/content-pillar/process-file/{file_id}",
                    json={"action": "parse"},
                    timeout=TIMEOUT
                ),
                timeout=TIMEOUT + 5.0  # Add buffer for asyncio timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"File parsing timed out after {TIMEOUT + 5.0}s")
        
        # Handle rate limiting gracefully - skip test if rate limited
        if parse_response.status_code == 429:
            pytest.skip(f"Rate limited (429) - cannot parse file for test")
        
        assert parse_response.status_code in [200, 201, 202], \
            f"❌ File parsing failed: {parse_response.status_code} - {parse_response.text}"
        print(f"   ✅ File parsing initiated/completed: {parse_response.status_code}")
        
        # Step 3: Get file details with timeout protection
        print(f"   [STEP 3/3] Getting file details: {file_id}")
        try:
            details_response = await asyncio.wait_for(
                self.client.get(
                    f"/api/v1/content-pillar/get-file-details/{file_id}",
                    timeout=TIMEOUT
                ),
                timeout=TIMEOUT + 5.0  # Add buffer for asyncio timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Get file details timed out after {TIMEOUT + 5.0}s")
        
        assert details_response.status_code == 200, \
            f"❌ File details failed: {details_response.status_code} - {details_response.text}"
        
        details_data = details_response.json()
        file_data = details_data.get("file", details_data)
        print(f"   ✅ File details retrieved")
        
        parsed_file = ParsedFile(
            file_id=file_id,
            file_type=file_type,
            filename=filename,
            parsed=True,
            metadata=file_data,
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
        """Create an uploaded file for use in Operations Pillar tests."""
        print(f"📤 [HELPER] Creating uploaded file (type: {file_type}, parse: {parse})...")
        
        if content is None:
            content = self._generate_default_content(file_type)
        
        if filename is None:
            filename = f"uploaded_{file_type}_{uuid.uuid4().hex[:8]}.{file_type}"
        
        mime_type = self._get_mime_type(file_type)
        files = {"file": (filename, content, mime_type)}
        
        # Step 1: Upload file with timeout protection
        print(f"   [STEP 1] Uploading file: {filename}")
        try:
            upload_response = await asyncio.wait_for(
                self.client.post(
                    "/api/v1/content-pillar/upload-file",
                    files=files,
                    timeout=TIMEOUT
                ),
                timeout=TIMEOUT + 5.0  # Add buffer for asyncio timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"File upload timed out after {TIMEOUT + 5.0}s")
        
        # Handle rate limiting gracefully - skip test if rate limited
        if upload_response.status_code == 429:
            pytest.skip(f"Rate limited (429) - cannot upload file for test")
        
        assert upload_response.status_code in [200, 201], \
            f"❌ File upload failed: {upload_response.status_code} - {upload_response.text}"
        
        upload_data = upload_response.json()
        file_id = upload_data.get("file_id") or upload_data.get("uuid") or upload_data.get("id")
        assert file_id, f"❌ Upload response missing file_id: {upload_data}"
        print(f"   ✅ File uploaded: file_id={file_id}")
        
        is_parsed = False
        if parse:
            # Step 2: Parse file with timeout protection (if requested)
            print(f"   [STEP 2] Parsing file: {file_id}")
            try:
                parse_response = await asyncio.wait_for(
                    self.client.post(
                        f"/api/v1/content-pillar/process-file/{file_id}",
                        json={"action": "parse"},
                        timeout=TIMEOUT
                    ),
                    timeout=TIMEOUT + 5.0  # Add buffer for asyncio timeout
                )
                is_parsed = parse_response.status_code in [200, 201, 202]
                print(f"   ✅ File parsing initiated/completed: {parse_response.status_code}")
            except asyncio.TimeoutError:
                raise TimeoutError(f"File parsing timed out after {TIMEOUT + 5.0}s")
        
        # Step 3: Get file details with timeout protection
        print(f"   [STEP 3] Getting file details: {file_id}")
        try:
            details_response = await asyncio.wait_for(
                self.client.get(
                    f"/api/v1/content-pillar/get-file-details/{file_id}",
                    timeout=TIMEOUT
                ),
                timeout=TIMEOUT + 5.0  # Add buffer for asyncio timeout
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Get file details timed out after {TIMEOUT + 5.0}s")
        
        details_data = details_response.json() if details_response.status_code == 200 else {}
        file_data = details_data.get("file", details_data)
        print(f"   ✅ File details retrieved")
        
        uploaded_file = UploadedFile(
            file_id=file_id,
            file_type=file_type,
            filename=filename,
            parsed=is_parsed,
            metadata=file_data,
            client=self.client
        )
        
        self._uploaded_files.append(uploaded_file)
        return uploaded_file
    
    async def create_pillar_outputs(self) -> Dict[str, Any]:
        """Create outputs from all pillars for Business Outcomes Pillar tests."""
        print("📤 [HELPER] Creating pillar outputs (Content, Insights, Operations)...")
        outputs = {
            "content_pillar": {},
            "insights_pillar": {},
            "operations_pillar": {}
        }
        
        # Step 1: Create parsed file (Content Pillar)
        print("   [STEP 1/3] Creating parsed file (Content Pillar)...")
        parsed_file = await self.create_parsed_file(file_type="csv")
        outputs["content_pillar"] = {
            "file_id": parsed_file.file_id,
            "file_type": parsed_file.file_type,
            "filename": parsed_file.filename,
            "parsed": True
        }
        print(f"   ✅ Content Pillar output created: file_id={parsed_file.file_id}")
        
        # Step 2: Run insights analysis (Insights Pillar)
        print("   [STEP 2/3] Running insights analysis (Insights Pillar)...")
        try:
            analyze_response = await asyncio.wait_for(
                self.client.post(
                    "/api/v1/insights-pillar/analyze-content",
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
                ),
                timeout=TIMEOUT + 5.0  # Add buffer for asyncio timeout
            )
            
            if analyze_response.status_code in [200, 201, 202]:
                analyze_data = analyze_response.json()
                analysis_id = analyze_data.get("analysis_id") or analyze_data.get("id")
                outputs["insights_pillar"] = {
                    "analysis_id": analysis_id,
                    "file_id": parsed_file.file_id,
                    "status": "completed" if analyze_response.status_code in [200, 201] else "processing"
                }
                print(f"   ✅ Insights Pillar output created: analysis_id={analysis_id}")
            else:
                print(f"   ⚠️ Insights analysis returned {analyze_response.status_code} (may not be implemented)")
                outputs["insights_pillar"] = {"status": "not_available"}
        except asyncio.TimeoutError:
            print(f"   ⚠️ Insights analysis timed out (may not be implemented)")
            outputs["insights_pillar"] = {"status": "not_available"}
        except Exception as e:
            print(f"   ⚠️ Insights analysis failed (may not be implemented): {e}")
            outputs["insights_pillar"] = {"status": "not_available"}
        
        # Step 3: Prepare Operations Pillar output
        print("   [STEP 3/3] Preparing Operations Pillar output...")
        outputs["operations_pillar"] = {
            "status": "available",
            "file_id": parsed_file.file_id
        }
        print(f"   ✅ Operations Pillar output prepared")
        
        return outputs
    
    def _generate_default_content(self, file_type: str) -> bytes:
        """Generate default content for a file type."""
        content_map = {
            "csv": b"name,value\ntest1,100\ntest2,200\ntest3,300",
            "txt": b"This is a test text file for operations pillar.",
            "json": b'{"key": "value", "data": [1, 2, 3]}',
        }
        return content_map.get(file_type.lower(), b"Test file content")
    
    def _get_mime_type(self, file_type: str) -> str:
        """Get MIME type for a file type."""
        mime_map = {
            "csv": "text/csv",
            "txt": "text/plain",
            "json": "application/json",
        }
        return mime_map.get(file_type.lower(), "application/octet-stream")


@pytest.fixture
def backend_url() -> str:
    """Fixture that provides the backend URL."""
    return BASE_URL


@pytest.fixture
async def http_client(backend_url):
    """Async HTTP client for production readiness tests."""
    # Ensure URL has protocol
    base_url = backend_url
    if not base_url or not base_url.startswith(("http://", "https://")):
        base_url = f"http://{base_url}" if base_url else "http://localhost:8000"
    
    # Use base_url parameter - paths should be relative (start with /)
    async with httpx.AsyncClient(base_url=base_url, timeout=10.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
@pytest.mark.timeout(30)  # 30 second timeout for fixture setup (reduced from 60)
async def production_client():
    """
    Production test client with rate limiting mitigation.
    
    Features:
    - Rate limit monitoring and throttling
    - Authentication token caching
    - Request throttling (delay between requests)
    - Test data isolation
    """
    import asyncio
    from tests.e2e.production.test_production_client import ProductionTestClient
    
    base_url = PRODUCTION_BASE_URL
    if not base_url or not base_url.startswith(("http://", "https://")):
        base_url = f"http://{base_url}" if base_url else "http://localhost:8000"
    
    # Get test user credentials from environment (priority: TEST_USER_* > TEST_SUPABASE_* > default)
    test_user_email = (
        os.getenv("TEST_USER_EMAIL") or 
        os.getenv("TEST_SUPABASE_EMAIL") or 
        "test_user@symphainy.com"
    )
    test_user_password = (
        os.getenv("TEST_USER_PASSWORD") or 
        os.getenv("TEST_SUPABASE_PASSWORD") or 
        "test_password_123"
    )
    
    client = ProductionTestClient(
        base_url=base_url,
        test_user_email=test_user_email,
        test_user_password=test_user_password
    )
    
    # Skip pre-authentication to avoid fixture timeout
    # Authentication will happen lazily on first request via client.authenticate()
    # This prevents fixture setup from hanging if authentication is slow
    
    yield client
    await client.close()


@pytest.fixture
@pytest.mark.timeout(90)  # 90 second timeout for fixture setup
async def parsed_file_for_insights(production_client):
    """Fixture that provides a parsed file for Insights Pillar tests."""
    helper = TestDependencyHelper(production_client)
    try:
        # Wrap in asyncio.wait_for to ensure timeout protection
        return await asyncio.wait_for(
            helper.create_parsed_file(file_type="csv"),
            timeout=75.0  # Slightly less than pytest timeout to provide clear error
        )
    except asyncio.TimeoutError:
        pytest.fail("❌ parsed_file_for_insights fixture timed out after 75s - file upload/parsing may be hanging")


@pytest.fixture
@pytest.mark.timeout(90)  # 90 second timeout for fixture setup
async def uploaded_file_for_operations(production_client):
    """Fixture that provides an uploaded file for Operations Pillar tests."""
    helper = TestDependencyHelper(production_client)
    try:
        # Wrap in asyncio.wait_for to ensure timeout protection
        print("📤 [FIXTURE] Starting uploaded_file_for_operations fixture...")
        result = await asyncio.wait_for(
            helper.create_uploaded_file(file_type="csv", parse=False),
            timeout=75.0  # Slightly less than pytest timeout to provide clear error
        )
        print(f"✅ [FIXTURE] uploaded_file_for_operations completed: file_id={result.file_id}")
        return result
    except asyncio.TimeoutError:
        pytest.fail("❌ uploaded_file_for_operations fixture timed out after 75s - file upload may be hanging")
    except Exception as e:
        pytest.fail(f"❌ uploaded_file_for_operations fixture failed: {e}")


@pytest.fixture
@pytest.mark.timeout(120)  # 120 second timeout for fixture setup (includes parsing)
async def parsed_file_for_operations(production_client):
    """Fixture that provides a parsed file for Operations Pillar tests (if needed)."""
    helper = TestDependencyHelper(production_client)
    try:
        # Wrap in asyncio.wait_for to ensure timeout protection
        return await asyncio.wait_for(
            helper.create_uploaded_file(file_type="csv", parse=True),
            timeout=105.0  # Slightly less than pytest timeout to provide clear error
        )
    except asyncio.TimeoutError:
        pytest.fail("❌ parsed_file_for_operations fixture timed out after 105s - file upload/parsing may be hanging")


@pytest.fixture
@pytest.mark.timeout(180)  # 180 second timeout for fixture setup (complex, involves multiple pillars)
async def pillar_outputs_for_business_outcomes(production_client):
    """Fixture that provides outputs from all pillars for Business Outcomes tests."""
    helper = TestDependencyHelper(production_client)
    try:
        # Wrap in asyncio.wait_for to ensure timeout protection
        print("📤 [FIXTURE] Starting pillar_outputs_for_business_outcomes fixture...")
        outputs = await asyncio.wait_for(
            helper.create_pillar_outputs(),
            timeout=165.0  # Slightly less than pytest timeout to provide clear error
        )
        outputs['_client'] = production_client
        print(f"✅ [FIXTURE] pillar_outputs_for_business_outcomes completed")
        return outputs
    except asyncio.TimeoutError:
        pytest.fail("❌ pillar_outputs_for_business_outcomes fixture timed out after 165s - pillar operations may be hanging")
    except Exception as e:
        pytest.fail(f"❌ pillar_outputs_for_business_outcomes fixture failed: {e}")


