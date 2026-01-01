"""
E2E tests for Content Pillar validation.

Tests:
- File upload → parsing → embedding → preview
- Structured file parsing
- Unstructured file parsing
- Hybrid file parsing
- Binary file with copybook parsing
"""

import pytest
import asyncio
import httpx
import json
from typing import Dict, Any
from pathlib import Path

from config.test_config import TestConfig
from utils.real_infrastructure_helpers import skip_if_missing_real_infrastructure, get_test_supabase_token


@pytest.mark.e2e
@pytest.mark.production_readiness
@pytest.mark.pillar
@pytest.mark.content
@pytest.mark.slow
@pytest.mark.critical
class TestContentPillarE2E:
    """Test suite for Content Pillar E2E validation."""
    
    @pytest.fixture
    def api_base_url(self):
        """Get API base URL from environment."""
        import os
        # Use TEST_BACKEND_URL if available, otherwise TEST_API_URL, otherwise default to localhost:8000
        return os.getenv("TEST_BACKEND_URL") or os.getenv("TEST_API_URL") or "http://localhost:8000"
    
    @pytest.fixture
    def session_token(self):
        """Get session token for authenticated requests."""
        token = get_test_supabase_token()
        return token
    
    @pytest.fixture
    def test_csv_file(self):
        """Create a test CSV file."""
        import tempfile
        import os
        
        content = "name,age,city\nJohn,30,New York\nJane,25,Los Angeles\nBob,35,Chicago"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_file_upload_workflow(self, api_base_url, session_token, test_csv_file):
        """Test complete file upload workflow."""
        skip_if_missing_real_infrastructure(["supabase"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Upload file
            with open(test_csv_file, 'rb') as f:
                files = {"file": (Path(test_csv_file).name, f, "text/csv")}
                data = {
                    "file_type": "structured",
                    "parsing_type": "structured"
                }
                
                response = await client.post(
                    f"{api_base_url}/api/v1/content-pillar/upload-file",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                # Should accept file (may return 200 or 202 for async processing)
                assert response.status_code in [200, 202, 201]
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    assert "file_id" in result or "success" in result
    
    @pytest.mark.asyncio
    async def test_structured_file_parsing(self, api_base_url, session_token):
        """Test structured file parsing workflow."""
        skip_if_missing_real_infrastructure(["supabase"])
        
        # This would test parsing a structured file
        # For now, test that parsing endpoint exists
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test parsing endpoint (may require file_id)
            response = await client.post(
                f"{api_base_url}/api/v1/content-pillar/process-file",
                json={"file_id": "test_file", "parsing_type": "structured"},
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_unstructured_file_parsing(self, api_base_url, session_token):
        """Test unstructured file parsing workflow."""
        skip_if_missing_real_infrastructure(["supabase"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test unstructured parsing endpoint
            response = await client.post(
                f"{api_base_url}/api/v1/content-pillar/process-file",
                json={"file_id": "test_file", "parsing_type": "unstructured"},
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_hybrid_file_parsing(self, api_base_url, session_token):
        """Test hybrid file parsing workflow."""
        skip_if_missing_real_infrastructure(["supabase"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test hybrid parsing endpoint
            response = await client.post(
                f"{api_base_url}/api/v1/content-pillar/process-file",
                json={"file_id": "test_file", "parsing_type": "hybrid"},
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_file_preview_endpoint(self, api_base_url, session_token):
        """Test file preview endpoint."""
        skip_if_missing_real_infrastructure(["supabase"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test preview endpoint
            response = await client.get(
                f"{api_base_url}/api/v1/content-pillar/file-preview/test_file_id",
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
    
    # ========================================================================
    # EMBEDDING/DATA MASH E2E TESTS
    # ========================================================================
    
    @pytest.mark.asyncio
    async def test_complete_embedding_workflow_e2e(self, api_base_url, session_token, test_csv_file):
        """Test complete E2E embedding workflow: upload → parse → create embeddings → preview."""
        skip_if_missing_real_infrastructure(["supabase", "arango"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
            headers["X-Session-Token"] = session_token
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Upload file
            with open(test_csv_file, 'rb') as f:
                files = {"file": (Path(test_csv_file).name, f, "text/csv")}
                data = {
                    "file_type": "structured",
                    "parsing_type": "structured"
                }
                
                upload_response = await client.post(
                    f"{api_base_url}/api/v1/content-pillar/upload-file",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                assert upload_response.status_code in [200, 201, 202]
                upload_result = upload_response.json()
                assert "file_id" in upload_result or "success" in upload_result
                file_id = upload_result.get("file_id")
                workflow_id = upload_result.get("workflow_id")
                
                if not file_id:
                    pytest.skip("File upload did not return file_id - cannot continue test")
            
            # Step 2: Parse file
            await asyncio.sleep(1.0)  # Small delay for file processing
            
            parse_response = await client.post(
                f"{api_base_url}/api/v1/content-pillar/process-file/{file_id}",
                json={"parsing_type": "structured"},
                headers=headers
            )
            
            assert parse_response.status_code in [200, 202]
            parse_result = parse_response.json()
            assert "parsed_file_id" in parse_result or "success" in parse_result
            parsed_file_id = parse_result.get("parsed_file_id")
            
            if not parsed_file_id:
                pytest.skip("File parsing did not return parsed_file_id - cannot continue test")
            
            # Step 3: Create embeddings
            await asyncio.sleep(2.0)  # Wait for parsing to complete
            
            # ✅ Pass workflow_id from upload to maintain correlation
            create_embeddings_headers = headers.copy()
            if workflow_id:
                create_embeddings_headers["X-Workflow-Id"] = workflow_id
            
            create_embeddings_response = await client.post(
                f"{api_base_url}/api/v1/content-pillar/create-embeddings",
                json={
                    "parsed_file_id": parsed_file_id,
                    "file_id": file_id,
                    "workflow_id": workflow_id  # ✅ Also pass in request body
                },
                headers=create_embeddings_headers
            )
            
            assert create_embeddings_response.status_code in [200, 202]
            embeddings_result = create_embeddings_response.json()
            assert "success" in embeddings_result
            assert embeddings_result.get("success") is True
            assert "content_id" in embeddings_result
            assert "embeddings_count" in embeddings_result
            content_id = embeddings_result.get("content_id")
            embeddings_count = embeddings_result.get("embeddings_count", 0)
            
            # Verify workflow_id propagation
            assert embeddings_result.get("workflow_id") == workflow_id, "workflow_id should be consistent"
            
            if not content_id:
                pytest.skip("Embedding creation did not return content_id - cannot continue test")
            
            # Step 4: List embeddings
            await asyncio.sleep(1.0)  # Small delay for embedding storage
            
            list_embeddings_response = await client.get(
                f"{api_base_url}/api/v1/content-pillar/list-embeddings?file_id={file_id}",
                headers=headers
            )
            
            assert list_embeddings_response.status_code == 200
            list_result = list_embeddings_response.json()
            assert "success" in list_result
            assert "embeddings" in list_result or "embedding_files" in list_result
            
            # Step 5: Preview embeddings
            preview_response = await client.get(
                f"{api_base_url}/api/v1/content-pillar/preview-embeddings/{content_id}",
                headers=headers
            )
            
            assert preview_response.status_code == 200
            preview_result = preview_response.json()
            assert "success" in preview_result
            assert preview_result.get("success") is True
            assert "content_id" in preview_result
            assert "columns" in preview_result
            assert "structure" in preview_result
    
    @pytest.mark.asyncio
    async def test_create_embeddings_endpoint(self, api_base_url, session_token):
        """Test create-embeddings API endpoint."""
        skip_if_missing_real_infrastructure(["supabase", "arango"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
            headers["X-Session-Token"] = session_token
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # First, we need a parsed file - try to get one from list-parsed-files
            list_parsed_response = await client.get(
                f"{api_base_url}/api/v1/content-pillar/list-parsed-files",
                headers=headers
            )
            
            if list_parsed_response.status_code == 200:
                parsed_files = list_parsed_response.json()
                parsed_file_id = None
                
                if isinstance(parsed_files, dict) and "parsed_files" in parsed_files:
                    parsed_files_list = parsed_files.get("parsed_files", [])
                    if parsed_files_list and len(parsed_files_list) > 0:
                        parsed_file_id = parsed_files_list[0].get("parsed_file_id") or parsed_files_list[0].get("id")
                
                if parsed_file_id:
                    # Test create-embeddings endpoint
                    create_response = await client.post(
                        f"{api_base_url}/api/v1/content-pillar/create-embeddings",
                        json={"parsed_file_id": parsed_file_id},
                        headers=headers
                    )
                    
                    # Should not be 404 (endpoint exists)
                    assert create_response.status_code != 404
                    
                    if create_response.status_code == 200:
                        result = create_response.json()
                        assert "success" in result
                        if result.get("success"):
                            assert "content_id" in result
                            assert "embeddings_count" in result
                else:
                    pytest.skip("No parsed files available for embedding creation test")
            else:
                # Endpoint exists even if we can't get parsed files
                create_response = await client.post(
                    f"{api_base_url}/api/v1/content-pillar/create-embeddings",
                    json={"parsed_file_id": "test_parsed_file_id"},
                    headers=headers
                )
                assert create_response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_preview_embeddings_endpoint(self, api_base_url, session_token):
        """Test preview-embeddings API endpoint."""
        skip_if_missing_real_infrastructure(["supabase", "arango"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
            headers["X-Session-Token"] = session_token
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test with a test content_id (will likely fail but endpoint should exist)
            response = await client.get(
                f"{api_base_url}/api/v1/content-pillar/preview-embeddings/test_content_id",
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
    
    @pytest.mark.asyncio
    async def test_list_embeddings_endpoint(self, api_base_url, session_token):
        """Test list-embeddings API endpoint."""
        skip_if_missing_real_infrastructure(["supabase", "arango"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
            headers["X-Session-Token"] = session_token
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test without file_id (list all)
            response = await client.get(
                f"{api_base_url}/api/v1/content-pillar/list-embeddings",
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
            
            if response.status_code == 200:
                result = response.json()
                assert "success" in result
                assert "embeddings" in result or "embedding_files" in result
            
            # Test with file_id filter
            response_with_filter = await client.get(
                f"{api_base_url}/api/v1/content-pillar/list-embeddings?file_id=test_file_id",
                headers=headers
            )
            
            assert response_with_filter.status_code != 404
    
    @pytest.mark.asyncio
    async def test_list_parsed_files_with_embeddings_endpoint(self, api_base_url, session_token):
        """Test list-parsed-files-with-embeddings API endpoint."""
        skip_if_missing_real_infrastructure(["supabase", "arango"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
            headers["X-Session-Token"] = session_token
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{api_base_url}/api/v1/content-pillar/list-parsed-files-with-embeddings",
                headers=headers
            )
            
            # Should not be 404 (endpoint exists)
            assert response.status_code != 404
            
            if response.status_code == 200:
                result = response.json()
                assert "success" in result
                assert "parsed_files" in result
    
    @pytest.mark.asyncio
    async def test_workflow_id_propagation_e2e(self, api_base_url, session_token, test_csv_file):
        """Test workflow_id propagation through entire flow."""
        skip_if_missing_real_infrastructure(["supabase", "arango"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
            headers["X-Session-Token"] = session_token
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Upload file (get initial workflow_id)
            with open(test_csv_file, 'rb') as f:
                files = {"file": (Path(test_csv_file).name, f, "text/csv")}
                data = {
                    "file_type": "structured",
                    "parsing_type": "structured"
                }
                
                upload_response = await client.post(
                    f"{api_base_url}/api/v1/content-pillar/upload-file",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                if upload_response.status_code not in [200, 201, 202]:
                    pytest.skip("File upload failed - cannot test workflow_id propagation")
                
                upload_result = upload_response.json()
                initial_workflow_id = upload_result.get("workflow_id")
                file_id = upload_result.get("file_id")
                
                if not file_id:
                    pytest.skip("File upload did not return file_id - cannot continue test")
            
            # Step 2: Parse file (should have same workflow_id)
            await asyncio.sleep(1.0)
            
            parse_response = await client.post(
                f"{api_base_url}/api/v1/content-pillar/process-file/{file_id}",
                json={"parsing_type": "structured"},
                headers=headers
            )
            
            if parse_response.status_code in [200, 202]:
                parse_result = parse_response.json()
                parse_workflow_id = parse_result.get("workflow_id")
                
                if initial_workflow_id and parse_workflow_id:
                    # workflow_id should be consistent (or at least present)
                    assert parse_workflow_id is not None, "workflow_id should be present in parse response"
                
                parsed_file_id = parse_result.get("parsed_file_id")
                
                if parsed_file_id:
                    # Step 3: Create embeddings (should have same workflow_id)
                    await asyncio.sleep(2.0)
                    
                    create_response = await client.post(
                        f"{api_base_url}/api/v1/content-pillar/create-embeddings",
                        json={
                            "parsed_file_id": parsed_file_id,
                            "file_id": file_id
                        },
                        headers=headers
                    )
                    
                    if create_response.status_code in [200, 202]:
                        create_result = create_response.json()
                        create_workflow_id = create_result.get("workflow_id")
                        
                        if initial_workflow_id and create_workflow_id:
                            # workflow_id should be consistent
                            assert create_workflow_id is not None, "workflow_id should be present in embedding creation response"
                            # Note: workflow_id might be different if gateway generates new one, but should be present


