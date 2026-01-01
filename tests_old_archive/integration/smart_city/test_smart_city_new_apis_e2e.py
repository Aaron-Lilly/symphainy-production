#!/usr/bin/env python3
"""
End-to-End Integration Tests for Smart City New APIs

Tests the complete flow:
1. File Upload → Content Steward
2. File Parsing → Business Enablement
3. Store Parsed Files → Content Steward
4. Extract Content Metadata → Business Enablement (temporary inline)
5. Store Content Metadata → Librarian
6. Generate Embeddings → Business Enablement (temporary using existing agent)
7. Store Embeddings → Librarian
8. Query/Retrieve → Librarian

This test validates the new Smart City implementation end-to-end.
"""

import pytest
import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Test markers
pytestmark = [pytest.mark.integration, pytest.mark.smart_city, pytest.mark.e2e]


class TestSmartCityNewAPIsE2E:
    """End-to-end tests for new Smart City APIs."""
    
    @pytest.fixture
    async def test_file_data(self):
        """Create test file data (CSV for structured data)."""
        csv_content = """name,age,city
John Doe,30,New York
Jane Smith,25,San Francisco
Bob Johnson,35,Chicago"""
        return csv_content.encode('utf-8')
    
    @pytest.fixture
    async def user_context(self):
        """Create test user context."""
        return {
            "user_id": "test_user_123",
            "tenant_id": "test_tenant_456",
            "service_name": "test_service"
        }
    
    @pytest.mark.asyncio
    async def test_complete_flow_structured_data(
        self,
        content_steward_service,
        librarian_service,
        file_parser_service,
        hf_inference_agent,
        test_file_data,
        user_context
    ):
        """
        Test complete flow for structured data:
        Upload → Parse → Store Parsed → Extract Metadata → Store Metadata → Generate Embeddings → Store Embeddings
        """
        # Step 1: Upload file via Content Steward
        upload_result = await content_steward_service.process_upload(
            file_data=test_file_data,
            content_type="text/csv",
            metadata={
                "ui_name": "test_data.csv",
                "file_type": "csv",
                "original_filename": "test_data.csv"
            },
            user_context=user_context
        )
        
        assert upload_result is not None
        assert "uuid" in upload_result or "file_id" in upload_result
        file_id = upload_result.get("uuid") or upload_result.get("file_id")
        assert file_id is not None
        
        print(f"✅ Step 1: File uploaded - file_id: {file_id}")
        
        # Step 2: Parse file via FileParserService (Business Enablement)
        parse_result = await file_parser_service.parse_file(
            file_id=file_id,
            parse_options={"format": "csv"},
            user_context=user_context
        )
        
        assert parse_result is not None
        assert parse_result.get("success") is True
        assert "format_type" in parse_result or "structure" in parse_result
        
        format_type = parse_result.get("format_type", "parquet")
        content_type = parse_result.get("content_type", "structured")
        
        print(f"✅ Step 2: File parsed - format_type: {format_type}, content_type: {content_type}")
        
        # Step 3: Store parsed file via Content Steward
        # Note: We need to get the parsed file data from parse_result
        # For now, we'll create mock parsed file data
        parsed_file_data = b"mock_parquet_data"  # In real flow, this comes from parse_result
        
        store_parsed_result = await content_steward_service.store_parsed_file(
            file_id=file_id,
            parsed_file_data=parsed_file_data,
            format_type=format_type,
            content_type=content_type,
            parse_result=parse_result,
            user_context=user_context
        )
        
        assert store_parsed_result is not None
        assert store_parsed_result.get("success") is True
        assert "parsed_file_id" in store_parsed_result
        parsed_file_id = store_parsed_result["parsed_file_id"]
        
        print(f"✅ Step 3: Parsed file stored - parsed_file_id: {parsed_file_id}")
        
        # Step 4: Extract content metadata (TEMPORARY: inline until Business Enablement refactoring)
        # TODO: Move to ContentMetadataExtractionService during Business Enablement refactoring
        content_metadata = {
            "content_type": content_type,
            "structure_type": "structured",
            "schema": {
                "columns": ["name", "age", "city"],
                "data_types": {"name": "string", "age": "integer", "city": "string"}
            },
            "columns": ["name", "age", "city"],
            "data_types": {"name": "string", "age": "integer", "city": "string"},
            "row_count": 3,
            "column_count": 3,
            "parsing_method": "csv_parser",
            "parsing_confidence": 1.0
        }
        
        print(f"✅ Step 4: Content metadata extracted (temporary inline)")
        
        # Step 5: Store content metadata via Librarian
        store_metadata_result = await librarian_service.store_content_metadata(
            file_id=file_id,
            parsed_file_id=parsed_file_id,
            content_metadata=content_metadata,
            user_context=user_context
        )
        
        assert store_metadata_result is not None
        assert store_metadata_result.get("success") is True
        assert "content_id" in store_metadata_result
        content_id = store_metadata_result["content_id"]
        
        print(f"✅ Step 5: Content metadata stored - content_id: {content_id}")
        
        # Step 6: Generate embeddings (TEMPORARY: use existing StatelessHFInferenceAgent)
        # TODO: Move to EmbeddingService during Business Enablement refactoring
        embeddings = []
        for column in content_metadata["columns"]:
            # Generate embedding for column metadata
            embedding_text = f"Column: {column}, Type: {content_metadata['data_types'][column]}"
            embedding_result = await hf_inference_agent.generate_embedding(embedding_text)
            
            if embedding_result and "embedding" in embedding_result:
                embeddings.append({
                    "column_name": column,
                    "metadata_embedding": embedding_result["embedding"],
                    "meaning_embedding": embedding_result["embedding"],  # Simplified for test
                    "samples_embedding": embedding_result["embedding"],  # Simplified for test
                    "semantic_id": f"semantic_{column}_{uuid.uuid4().hex[:8]}"
                })
        
        print(f"✅ Step 6: Embeddings generated - count: {len(embeddings)}")
        
        # Step 7: Store embeddings via Librarian
        store_embeddings_result = await librarian_service.store_embeddings(
            content_id=content_id,
            file_id=file_id,
            embeddings=embeddings,
            user_context=user_context
        )
        
        assert store_embeddings_result is not None
        assert store_embeddings_result.get("success") is True
        assert "stored_count" in store_embeddings_result
        assert store_embeddings_result["stored_count"] == len(embeddings)
        
        print(f"✅ Step 7: Embeddings stored - stored_count: {store_embeddings_result['stored_count']}")
        
        # Step 8: Retrieve and verify
        # 8a: Get parsed file
        parsed_file = await content_steward_service.get_parsed_file(
            parsed_file_id=parsed_file_id,
            user_context=user_context
        )
        assert parsed_file is not None
        print(f"✅ Step 8a: Parsed file retrieved")
        
        # 8b: Get content metadata
        retrieved_metadata = await librarian_service.get_content_metadata(
            content_id=content_id,
            user_context=user_context
        )
        assert retrieved_metadata is not None
        assert retrieved_metadata.get("content_id") == content_id
        print(f"✅ Step 8b: Content metadata retrieved")
        
        # 8c: Get embeddings
        retrieved_embeddings = await librarian_service.get_embeddings(
            content_id=content_id,
            user_context=user_context
        )
        assert retrieved_embeddings is not None
        assert len(retrieved_embeddings) == len(embeddings)
        print(f"✅ Step 8c: Embeddings retrieved - count: {len(retrieved_embeddings)}")
        
        # Step 9: Test vector search
        if embeddings and len(embeddings) > 0:
            query_embedding = embeddings[0]["metadata_embedding"]
            search_results = await librarian_service.vector_search(
                query_embedding=query_embedding,
                limit=5,
                filters={"content_id": content_id},
                user_context=user_context
            )
            assert search_results is not None
            print(f"✅ Step 9: Vector search completed - results: {len(search_results)}")
        
        print(f"\n🎉 Complete E2E flow test PASSED!")
        print(f"   File ID: {file_id}")
        print(f"   Parsed File ID: {parsed_file_id}")
        print(f"   Content ID: {content_id}")
        print(f"   Embeddings Count: {len(embeddings)}")
    
    @pytest.mark.asyncio
    async def test_content_steward_parsed_file_apis(
        self,
        content_steward_service,
        test_file_data,
        user_context
    ):
        """Test Content Steward parsed file storage APIs."""
        # Upload file
        upload_result = await content_steward_service.process_upload(
            file_data=test_file_data,
            content_type="text/csv",
            metadata={"ui_name": "test.csv", "file_type": "csv"},
            user_context=user_context
        )
        file_id = upload_result.get("uuid") or upload_result.get("file_id")
        
        # Store parsed file
        parse_result = {
            "format_type": "parquet",
            "content_type": "structured",
            "row_count": 3,
            "column_count": 3,
            "columns": ["name", "age", "city"]
        }
        
        store_result = await content_steward_service.store_parsed_file(
            file_id=file_id,
            parsed_file_data=b"mock_parquet",
            format_type="parquet",
            content_type="structured",
            parse_result=parse_result,
            user_context=user_context
        )
        
        assert store_result.get("success") is True
        parsed_file_id = store_result["parsed_file_id"]
        
        # Get parsed file
        retrieved = await content_steward_service.get_parsed_file(
            parsed_file_id=parsed_file_id,
            user_context=user_context
        )
        assert retrieved is not None
        
        # List parsed files
        parsed_files = await content_steward_service.list_parsed_files(
            file_id=file_id,
            user_context=user_context
        )
        assert isinstance(parsed_files, list)
        assert len(parsed_files) > 0
        
        print(f"✅ Content Steward parsed file APIs test PASSED")
    
    @pytest.mark.asyncio
    async def test_librarian_content_metadata_apis(
        self,
        librarian_service,
        user_context
    ):
        """Test Librarian content metadata storage APIs."""
        file_id = str(uuid.uuid4())
        parsed_file_id = f"parsed_{uuid.uuid4()}"
        
        content_metadata = {
            "content_type": "structured",
            "structure_type": "table",
            "schema": {"columns": ["col1", "col2"]},
            "columns": ["col1", "col2"],
            "data_types": {"col1": "string", "col2": "integer"},
            "row_count": 10,
            "column_count": 2,
            "parsing_method": "test",
            "parsing_confidence": 1.0
        }
        
        # Store
        store_result = await librarian_service.store_content_metadata(
            file_id=file_id,
            parsed_file_id=parsed_file_id,
            content_metadata=content_metadata,
            user_context=user_context
        )
        
        assert store_result.get("success") is True
        content_id = store_result["content_id"]
        
        # Get
        retrieved = await librarian_service.get_content_metadata(
            content_id=content_id,
            user_context=user_context
        )
        assert retrieved is not None
        assert retrieved.get("content_id") == content_id
        
        # Update
        updates = {"row_count": 20}
        update_result = await librarian_service.update_content_metadata(
            content_id=content_id,
            updates=updates,
            user_context=user_context
        )
        assert update_result.get("success") is True
        
        print(f"✅ Librarian content metadata APIs test PASSED")
    
    @pytest.mark.asyncio
    async def test_librarian_embeddings_apis(
        self,
        librarian_service,
        hf_inference_agent,
        user_context
    ):
        """Test Librarian embeddings storage APIs."""
        file_id = str(uuid.uuid4())
        content_id = str(uuid.uuid4())
        
        # Generate test embeddings
        embeddings = []
        for i, column in enumerate(["col1", "col2"]):
            embedding_result = await hf_inference_agent.generate_embedding(f"Column {column}")
            if embedding_result and "embedding" in embedding_result:
                embeddings.append({
                    "column_name": column,
                    "metadata_embedding": embedding_result["embedding"],
                    "meaning_embedding": embedding_result["embedding"],
                    "samples_embedding": embedding_result["embedding"],
                    "semantic_id": f"semantic_{column}"
                })
        
        if not embeddings:
            pytest.skip("HF Inference Agent not available or embeddings not generated")
        
        # Store embeddings
        store_result = await librarian_service.store_embeddings(
            content_id=content_id,
            file_id=file_id,
            embeddings=embeddings,
            user_context=user_context
        )
        
        assert store_result.get("success") is True
        assert store_result.get("stored_count") == len(embeddings)
        
        # Get embeddings
        retrieved = await librarian_service.get_embeddings(
            content_id=content_id,
            user_context=user_context
        )
        assert retrieved is not None
        assert len(retrieved) == len(embeddings)
        
        # Vector search
        query_embedding = embeddings[0]["metadata_embedding"]
        search_results = await librarian_service.vector_search(
            query_embedding=query_embedding,
            limit=10,
            filters={"content_id": content_id},
            user_context=user_context
        )
        assert search_results is not None
        
        print(f"✅ Librarian embeddings APIs test PASSED")
    
    @pytest.mark.asyncio
    async def test_semantic_data_abstraction(
        self,
        semantic_data_abstraction,
        user_context
    ):
        """Test SemanticDataAbstraction directly."""
        content_id = str(uuid.uuid4())
        file_id = str(uuid.uuid4())
        
        # Test embeddings storage
        embeddings = [{
            "column_name": "test_col",
            "metadata_embedding": [0.1] * 384,  # Mock embedding vector
            "meaning_embedding": [0.2] * 384,
            "samples_embedding": [0.3] * 384,
            "semantic_id": "test_semantic_id"
        }]
        
        store_result = await semantic_data_abstraction.store_semantic_embeddings(
            content_id=content_id,
            file_id=file_id,
            embeddings=embeddings,
            user_context=user_context
        )
        
        assert store_result.get("success") is True
        
        # Test retrieval
        retrieved = await semantic_data_abstraction.get_semantic_embeddings(
            content_id=content_id,
            user_context=user_context
        )
        assert retrieved is not None
        assert len(retrieved) > 0
        
        print(f"✅ SemanticDataAbstraction test PASSED")
    
    @pytest.mark.asyncio
    async def test_observability_abstraction(
        self,
        observability_abstraction,
        user_context
    ):
        """Test ObservabilityAbstraction directly."""
        # Test log storage
        log_result = await observability_abstraction.record_platform_log(
            log_level="info",
            message="Test log message",
            service_name="test_service",
            trace_id="test_trace_123",
            user_context=user_context
        )
        
        assert log_result.get("success") is True
        
        # Test metric storage
        metric_result = await observability_abstraction.record_platform_metric(
            metric_name="test_metric",
            metric_value=42.0,
            service_name="test_service",
            trace_id="test_trace_123",
            user_context=user_context
        )
        
        assert metric_result.get("success") is True
        
        # Test trace storage
        trace_result = await observability_abstraction.record_platform_trace(
            trace_id="test_trace_123",
            span_name="test_span",
            service_name="test_service",
            start_time=datetime.utcnow(),
            duration_ms=100.0,
            status="ok",
            user_context=user_context
        )
        
        assert trace_result.get("success") is True
        
        # Test agent execution storage
        agent_result = await observability_abstraction.record_agent_execution(
            agent_id="test_agent_123",
            agent_name="TestAgent",
            prompt_hash="test_hash_123",
            response="Test response",
            trace_id="test_trace_123",
            execution_metadata={"tokens": 100, "latency_ms": 50},
            user_context=user_context
        )
        
        assert agent_result.get("success") is True
        
        # Test retrieval
        logs = await observability_abstraction.get_platform_logs(
            filters={"service_name": "test_service"},
            limit=10,
            user_context=user_context
        )
        assert logs is not None
        
        print(f"✅ ObservabilityAbstraction test PASSED")



