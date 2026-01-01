"""
E2E tests for Insights Pillar validation.

Tests:
- Structured analysis workflow (EDA, VARK, business summary)
- Unstructured analysis workflow (with AAR support)
- Data mapping workflow (unstructured→structured, structured→structured)
- Data quality evaluation workflow
- Workflow ID propagation
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
@pytest.mark.insights
@pytest.mark.slow
@pytest.mark.critical
class TestInsightsPillarE2E:
    """Test suite for Insights Pillar E2E validation."""
    
    @pytest.fixture
    def api_base_url(self):
        """Get API base URL from environment."""
        import os
        # Use TEST_BACKEND_URL if available, otherwise TEST_API_URL, otherwise default to localhost
        return os.getenv("TEST_BACKEND_URL") or os.getenv("TEST_API_URL") or "http://localhost"
    
    @pytest.fixture
    def session_token(self):
        """Get session token for authenticated requests."""
        token = get_test_supabase_token()
        return token
    
    @pytest.fixture
    def test_csv_file(self):
        """Create a test CSV file for structured analysis."""
        import tempfile
        import os
        
        content = "name,age,city,department\nJohn,30,New York,Sales\nJane,25,Los Angeles,Marketing\nBob,35,Chicago,Engineering"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def test_text_file(self):
        """Create a test text file for unstructured analysis."""
        import tempfile
        import os
        
        content = """After Action Review - Project Alpha
        
        Executive Summary:
        Project Alpha was completed successfully with some challenges encountered during implementation.
        
        Lessons Learned:
        1. Early stakeholder engagement is critical for project success
        2. Regular communication prevents scope creep
        3. Automated testing reduces deployment risks
        
        Risks Identified:
        1. Resource constraints may impact future projects
        2. Technical debt needs to be addressed
        3. Documentation gaps could affect maintenance
        
        Recommendations:
        1. Implement continuous integration pipeline
        2. Establish regular review meetings
        3. Create comprehensive documentation
        
        Timeline:
        - Week 1: Project kickoff and planning
        - Week 2-4: Development phase
        - Week 5: Testing and deployment
        - Week 6: Post-deployment review"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.mark.asyncio
    async def test_structured_analysis_workflow(self, api_base_url, session_token, test_csv_file):
        """Test complete structured analysis workflow: upload → parse → analyze."""
        skip_if_missing_real_infrastructure(["supabase"])
        
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
            
            # Step 3: Create embeddings (required for EDA analysis)
            await asyncio.sleep(2.0)  # Wait for parsing to complete
            
            parsed_file_id = parse_result.get("parsed_file_id")
            if not parsed_file_id:
                pytest.skip("File parsing did not return parsed_file_id - cannot create embeddings")
            
            # ✅ Pass workflow_id from upload to maintain correlation
            embedding_headers = headers.copy()
            if workflow_id:
                embedding_headers["X-Workflow-Id"] = workflow_id
            
            # Create embeddings before analysis (DataAnalyzerService requires schema embeddings)
            create_embeddings_response = await client.post(
                f"{api_base_url}/api/v1/content-pillar/create-embeddings",
                json={
                    "parsed_file_id": parsed_file_id,
                    "file_id": file_id,
                    "workflow_id": workflow_id
                },
                headers=embedding_headers
            )
            
            assert create_embeddings_response.status_code in [200, 202]
            embeddings_result = create_embeddings_response.json()
            assert embeddings_result.get("success") is True, f"Embedding creation failed: {embeddings_result.get('error')}"
            
            # Get content_id from embeddings result (needed for EDA analysis)
            content_id = embeddings_result.get("content_id") or file_id
            
            # Step 4: Analyze structured data (EDA) - now that embeddings exist
            await asyncio.sleep(2.0)  # Wait for embeddings to be indexed
            
            # ✅ Pass workflow_id from upload to maintain correlation
            analysis_headers = headers.copy()
            if workflow_id:
                analysis_headers["X-Workflow-Id"] = workflow_id
            
            analysis_response = await client.post(
                f"{api_base_url}/api/v1/insights-solution/analyze",
                json={
                    "file_id": file_id,
                    "content_id": content_id,  # ✅ Pass content_id for EDA analysis
                    "analysis_type": "eda",
                    "options": {},
                    "workflow_id": workflow_id  # ✅ Also pass workflow_id in JSON body (FrontendGatewayService checks params first)
                },
                headers=analysis_headers
            )
            
            assert analysis_response.status_code in [200, 202]
            analysis_result = analysis_response.json()
            assert "success" in analysis_result
            assert analysis_result.get("success") is True
            assert "analysis_id" in analysis_result or "summary" in analysis_result
            
            # Verify workflow_id propagation
            assert analysis_result.get("workflow_id") == workflow_id, "workflow_id should be consistent"
    
    @pytest.mark.asyncio
    async def test_unstructured_analysis_workflow(self, api_base_url, session_token, test_text_file):
        """Test complete unstructured analysis workflow: upload → parse → analyze."""
        skip_if_missing_real_infrastructure(["supabase"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
            headers["X-Session-Token"] = session_token
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Upload file
            with open(test_text_file, 'rb') as f:
                files = {"file": (Path(test_text_file).name, f, "text/plain")}
                data = {
                    "file_type": "unstructured",
                    "parsing_type": "unstructured"
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
                json={"parsing_type": "unstructured"},
                headers=headers
            )
            
            assert parse_response.status_code in [200, 202]
            parse_result = parse_response.json()
            assert "parsed_file_id" in parse_result or "success" in parse_result
            
            # Step 3: Analyze unstructured data
            await asyncio.sleep(2.0)  # Wait for parsing to complete
            
            # ✅ Pass workflow_id from upload to maintain correlation
            analysis_headers = headers.copy()
            if workflow_id:
                analysis_headers["X-Workflow-Id"] = workflow_id
            
            analysis_response = await client.post(
                f"{api_base_url}/api/v1/insights-solution/analyze",
                json={
                    "file_id": file_id,
                    "analysis_type": "unstructured",
                    "options": {}
                },
                headers=analysis_headers
            )
            
            assert analysis_response.status_code in [200, 202]
            analysis_result = analysis_response.json()
            assert "success" in analysis_result
            assert analysis_result.get("success") is True
            assert "analysis_id" in analysis_result or "summary" in analysis_result
            
            # Verify workflow_id propagation
            assert analysis_result.get("workflow_id") == workflow_id, "workflow_id should be consistent"
    
    @pytest.mark.asyncio
    async def test_aar_analysis_workflow(self, api_base_url, session_token, test_text_file):
        """Test AAR (After Action Review) analysis workflow with agentic-forward pattern."""
        skip_if_missing_real_infrastructure(["supabase"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
            headers["X-Session-Token"] = session_token
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Upload AAR file
            with open(test_text_file, 'rb') as f:
                files = {"file": (Path(test_text_file).name, f, "text/plain")}
                data = {
                    "file_type": "unstructured",
                    "parsing_type": "unstructured"
                }
                
                upload_response = await client.post(
                    f"{api_base_url}/api/v1/content-pillar/upload-file",
                    files=files,
                    data=data,
                    headers=headers
                )
                
                assert upload_response.status_code in [200, 201, 202]
                upload_result = upload_response.json()
                file_id = upload_result.get("file_id")
                workflow_id = upload_result.get("workflow_id")
                
                if not file_id:
                    pytest.skip("File upload did not return file_id - cannot continue test")
            
            # Step 2: Parse file
            await asyncio.sleep(1.0)
            
            parse_response = await client.post(
                f"{api_base_url}/api/v1/content-pillar/process-file/{file_id}",
                json={"parsing_type": "unstructured"},
                headers=headers
            )
            
            assert parse_response.status_code in [200, 202]
            
            # Step 3: Analyze with AAR-specific analysis
            await asyncio.sleep(2.0)
            
            # ✅ Pass workflow_id from upload to maintain correlation
            analysis_headers = headers.copy()
            if workflow_id:
                analysis_headers["X-Workflow-Id"] = workflow_id
            
            analysis_response = await client.post(
                f"{api_base_url}/api/v1/insights-solution/analyze",
                json={
                    "file_id": file_id,
                    "analysis_type": "unstructured",
                    "options": {
                        "aar_specific_analysis": True  # ✅ Enable AAR analysis
                    }
                },
                headers=analysis_headers
            )
            
            assert analysis_response.status_code in [200, 202]
            analysis_result = analysis_response.json()
            assert "success" in analysis_result
            assert analysis_result.get("success") is True
            
            # Verify AAR analysis results
            aar_analysis = analysis_result.get("aar_analysis")
            if aar_analysis:
                assert "lessons_learned" in aar_analysis or isinstance(aar_analysis.get("lessons_learned"), list)
                assert "risks" in aar_analysis or isinstance(aar_analysis.get("risks"), list)
                assert "recommendations" in aar_analysis or isinstance(aar_analysis.get("recommendations"), list)
                assert "timeline" in aar_analysis or isinstance(aar_analysis.get("timeline"), list)
            
            # Verify workflow_id propagation
            assert analysis_result.get("workflow_id") == workflow_id, "workflow_id should be consistent"
    
    @pytest.mark.asyncio
    async def test_data_mapping_workflow(self, api_base_url, session_token, test_csv_file):
        """Test data mapping workflow: source file → target schema."""
        skip_if_missing_real_infrastructure(["supabase"])
        
        headers = {}
        if session_token:
            headers["Authorization"] = f"Bearer {session_token}"
            headers["X-Session-Token"] = session_token
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Upload source file
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
                source_file_id = upload_result.get("file_id")
                workflow_id = upload_response.json().get("workflow_id")
                
                if not source_file_id:
                    pytest.skip("File upload did not return file_id - cannot continue test")
            
            # Step 2: Parse source file
            await asyncio.sleep(1.0)
            
            parse_response = await client.post(
                f"{api_base_url}/api/v1/content-pillar/process-file/{source_file_id}",
                json={"parsing_type": "structured"},
                headers=headers
            )
            
            assert parse_response.status_code in [200, 202]
            
            # Step 3: Create target file (for structured→structured mapping)
            # For this test, we'll use the same file as target (simplified)
            target_file_id = source_file_id
            
            # Step 4: Execute data mapping
            await asyncio.sleep(2.0)
            
            # ✅ Pass workflow_id from upload to maintain correlation
            mapping_headers = headers.copy()
            if workflow_id:
                mapping_headers["X-Workflow-Id"] = workflow_id
            
            mapping_response = await client.post(
                f"{api_base_url}/api/v1/insights-solution/mapping",
                json={
                    "source_file_id": source_file_id,
                    "target_file_id": target_file_id,
                    "mapping_options": {}
                },
                headers=mapping_headers
            )
            
            assert mapping_response.status_code in [200, 202]
            mapping_result = mapping_response.json()
            assert "success" in mapping_result
            assert mapping_result.get("success") is True
            assert "mapping_id" in mapping_result or "mapping_rules" in mapping_result
            
            # Verify workflow_id propagation
            metadata = mapping_result.get("metadata", {})
            assert metadata.get("workflow_id") == workflow_id, "workflow_id should be consistent"
    
    @pytest.mark.asyncio
    async def test_data_quality_evaluation_workflow(self, api_base_url, session_token, test_csv_file):
        """Test data quality evaluation workflow."""
        skip_if_missing_real_infrastructure(["supabase"])
        
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
                file_id = upload_result.get("file_id")
                workflow_id = upload_result.get("workflow_id")
                
                if not file_id:
                    pytest.skip("File upload did not return file_id - cannot continue test")
            
            # Step 2: Parse file
            await asyncio.sleep(1.0)
            
            parse_response = await client.post(
                f"{api_base_url}/api/v1/content-pillar/process-file/{file_id}",
                json={"parsing_type": "structured"},
                headers=headers
            )
            
            assert parse_response.status_code in [200, 202]
            
            # Step 3: Evaluate data quality
            await asyncio.sleep(2.0)
            
            # ✅ Pass workflow_id from upload to maintain correlation
            quality_headers = headers.copy()
            if workflow_id:
                quality_headers["X-Workflow-Id"] = workflow_id
            
            quality_response = await client.post(
                f"{api_base_url}/api/v1/insights-solution/data-quality",
                json={
                    "file_id": file_id,
                    "options": {}
                },
                headers=quality_headers
            )
            
            assert quality_response.status_code in [200, 202]
            quality_result = quality_response.json()
            assert "success" in quality_result
            assert quality_result.get("success") is True
    
    @pytest.mark.asyncio
    async def test_workflow_id_propagation_e2e(self, api_base_url, session_token, test_csv_file):
        """Test workflow_id propagation through entire Insights Pillar workflow."""
        skip_if_missing_real_infrastructure(["supabase"])
        
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
                file_id = upload_result.get("file_id")
                workflow_id = upload_result.get("workflow_id")
                
                if not file_id or not workflow_id:
                    pytest.skip("File upload did not return file_id or workflow_id - cannot continue test")
            
            # Step 2: Parse file
            await asyncio.sleep(1.0)
            
            parse_headers = headers.copy()
            if workflow_id:
                parse_headers["X-Workflow-Id"] = workflow_id
            
            parse_response = await client.post(
                f"{api_base_url}/api/v1/content-pillar/process-file/{file_id}",
                json={"parsing_type": "structured"},
                headers=parse_headers
            )
            
            assert parse_response.status_code in [200, 202]
            
            # Step 3: Analyze (should propagate workflow_id)
            await asyncio.sleep(2.0)
            
            analysis_headers = headers.copy()
            if workflow_id:
                analysis_headers["X-Workflow-Id"] = workflow_id
            
            analysis_response = await client.post(
                f"{api_base_url}/api/v1/insights-solution/analyze",
                json={
                    "file_id": file_id,
                    "analysis_type": "eda",
                    "options": {}
                },
                headers=analysis_headers
            )
            
            assert analysis_response.status_code in [200, 202]
            analysis_result = analysis_response.json()
            
            # Verify workflow_id is consistent throughout
            assert analysis_result.get("workflow_id") == workflow_id, "workflow_id should be consistent across all operations"

