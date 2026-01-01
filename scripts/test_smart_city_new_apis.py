#!/usr/bin/env python3
"""
End-to-End Test Script for Smart City New APIs

This script tests the new Smart City APIs end-to-end:
1. Content Steward parsed file storage
2. Librarian content metadata storage
3. Librarian embeddings storage
4. SemanticDataAbstraction
5. ObservabilityAbstraction

Usage:
    python scripts/test_smart_city_new_apis.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Set TEST_MODE to make Traefik optional
os.environ["TEST_MODE"] = "true"

# Add project root to path
project_root = Path(__file__).parent.parent / "symphainy-platform"
sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
import uuid
from datetime import datetime


async def test_semantic_data_abstraction():
    """Test SemanticDataAbstraction."""
    print("\n" + "="*80)
    print("TEST 1: SemanticDataAbstraction")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService("test_platform")
        
        # Initialize Public Works Foundation
        pwf = PublicWorksFoundationService(di_container=di_container)
        await pwf.initialize_foundation()
        
        # Register in DI Container (required for Smart City services to access it)
        di_container.public_works_foundation = pwf
        
        # Get semantic data abstraction
        semantic_data_abstraction = pwf.get_abstraction("semantic_data")
        
        if not semantic_data_abstraction:
            print("❌ SemanticDataAbstraction not found")
            return False
        
        print("✅ SemanticDataAbstraction retrieved")
        
        # Test data
        content_id = str(uuid.uuid4())
        file_id = str(uuid.uuid4())
        user_context = {"tenant_id": "test_tenant", "user_id": "test_user", "permissions": ["write", "read", "execute"]}
        
        # Test embeddings storage
        embeddings = [{
            "column_name": "test_column",
            "metadata_embedding": [0.1] * 384,  # Mock embedding
            "meaning_embedding": [0.2] * 384,
            "samples_embedding": [0.3] * 384,
            "semantic_id": f"semantic_{uuid.uuid4().hex[:8]}"
        }]
        
        print(f"   Storing embeddings for content_id: {content_id}")
        store_result = await semantic_data_abstraction.store_semantic_embeddings(
            content_id=content_id,
            file_id=file_id,
            embeddings=embeddings,
            user_context=user_context
        )
        
        if not store_result.get("success"):
            print(f"❌ Failed to store embeddings: {store_result}")
            return False
        
        print(f"✅ Embeddings stored: {store_result.get('stored_count')} embeddings")
        
        # Test retrieval
        print(f"   Retrieving embeddings for content_id: {content_id}")
        retrieved = await semantic_data_abstraction.get_semantic_embeddings(
            content_id=content_id,
            user_context=user_context
        )
        
        if not retrieved or len(retrieved) == 0:
            print("❌ Failed to retrieve embeddings")
            return False
        
        print(f"✅ Embeddings retrieved: {len(retrieved)} embeddings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing SemanticDataAbstraction: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_observability_abstraction():
    """Test ObservabilityAbstraction."""
    print("\n" + "="*80)
    print("TEST 2: ObservabilityAbstraction")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        # Initialize DI Container
        di_container = DIContainerService("test_platform")
        
        # Initialize Public Works Foundation
        pwf = PublicWorksFoundationService(di_container=di_container)
        await pwf.initialize_foundation()
        
        # Register in DI Container (required for Smart City services to access it)
        di_container.public_works_foundation = pwf
        
        # Get observability abstraction
        observability_abstraction = pwf.get_abstraction("observability")
        
        if not observability_abstraction:
            print("❌ ObservabilityAbstraction not found")
            return False
        
        print("✅ ObservabilityAbstraction retrieved")
        
        user_context = {"tenant_id": "test_tenant", "user_id": "test_user", "permissions": ["write", "read", "execute"]}
        trace_id = f"trace_{uuid.uuid4().hex[:8]}"
        
        # Test log storage
        print("   Recording platform log")
        log_result = await observability_abstraction.record_platform_log(
            log_level="info",
            message="Test log message from E2E test",
            service_name="test_service",
            trace_id=trace_id,
            user_context=user_context
        )
        
        if not log_result.get("success"):
            print(f"❌ Failed to record log: {log_result}")
            return False
        
        print(f"✅ Platform log recorded: {log_result.get('log_id')}")
        
        # Test metric storage
        print("   Recording platform metric")
        metric_result = await observability_abstraction.record_platform_metric(
            metric_name="test_metric",
            metric_value=42.0,
            service_name="test_service",
            trace_id=trace_id,
            user_context=user_context
        )
        
        if not metric_result.get("success"):
            print(f"❌ Failed to record metric: {metric_result}")
            return False
        
        print(f"✅ Platform metric recorded: {metric_result.get('metric_id')}")
        
        # Test trace storage
        print("   Recording platform trace")
        from datetime import datetime
        start_time = datetime.utcnow()
        trace_result = await observability_abstraction.record_platform_trace(
            trace_id=trace_id,
            span_name="test_operation",
            service_name="test_service",
            start_time=start_time,
            duration_ms=100.0,
            status="ok",
            user_context=user_context
        )
        
        if not trace_result.get("success"):
            print(f"❌ Failed to record trace: {trace_result}")
            return False
        
        print(f"✅ Platform trace recorded: {trace_result.get('trace_id')}")
        
        # Test agent execution storage
        print("   Recording agent execution")
        agent_result = await observability_abstraction.record_agent_execution(
            agent_id=f"agent_{uuid.uuid4().hex[:8]}",
            agent_name="TestAgent",
            prompt_hash="test_hash_123",
            response="Test response",
            trace_id=trace_id,
            execution_metadata={"tokens": 100, "latency_ms": 50},
            user_context=user_context
        )
        
        if not agent_result.get("success"):
            print(f"❌ Failed to record agent execution: {agent_result}")
            return False
        
        print(f"✅ Agent execution recorded: {agent_result.get('execution_id')}")
        
        # Test retrieval
        print("   Retrieving platform logs")
        logs = await observability_abstraction.get_platform_logs(
            filters={"service_name": "test_service"},
            limit=10,
            user_context=user_context
        )
        
        if logs is None:
            print("❌ Failed to retrieve logs")
            return False
        
        print(f"✅ Platform logs retrieved: {len(logs)} logs")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing ObservabilityAbstraction: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_content_steward_parsed_file_apis():
    """Test Content Steward parsed file APIs."""
    print("\n" + "="*80)
    print("TEST 3: Content Steward Parsed File APIs")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService
        
        # Initialize DI Container
        di_container = DIContainerService("test_platform")
        
        # Initialize Public Works Foundation
        pwf = PublicWorksFoundationService(di_container=di_container)
        await pwf.initialize_foundation()
        
        # Register in DI Container (required for Smart City services to access it)
        di_container.public_works_foundation = pwf
        
        # Initialize Content Steward
        # Note: Smart City services access Public Works directly (no Platform Gateway needed)
        content_steward = ContentStewardService(
            di_container=di_container
        )
        await content_steward.initialize()
        
        print("✅ Content Steward initialized")
        
        # Test data
        user_context = {"tenant_id": "test_tenant", "user_id": "test_user", "permissions": ["write", "read", "execute", "admin"]}
        
        # First, upload a file to get a valid file_id
        print("   Uploading test file...")
        upload_result = await content_steward.process_upload(
            file_data=b"test file content",
            content_type="text/plain",
            metadata={"ui_name": "test_file.txt", "file_type": "txt"},
            user_context=user_context
        )
        
        if not upload_result or "uuid" not in upload_result:
            print(f"❌ Failed to upload test file: {upload_result}")
            return False
        
        file_id = upload_result["uuid"]
        print(f"✅ Test file uploaded: {file_id}")
        
        # Mock parse result
        parse_result = {
            "format_type": "parquet",
            "content_type": "structured",
            "row_count": 3,
            "column_count": 3,
            "columns": ["name", "age", "city"],
            "data_types": {"name": "string", "age": "integer", "city": "string"}
        }
        
        # Test store_parsed_file
        print(f"   Storing parsed file for file_id: {file_id}")
        store_result = await content_steward.store_parsed_file(
            file_id=file_id,
            parsed_file_data=b"mock_parquet_data",
            format_type="parquet",
            content_type="structured",
            parse_result=parse_result,
            user_context=user_context
        )
        
        if not store_result.get("success"):
            print(f"❌ Failed to store parsed file: {store_result}")
            return False
        
        parsed_file_id = store_result.get("parsed_file_id")
        print(f"✅ Parsed file stored: {parsed_file_id}")
        
        # Test get_parsed_file
        print(f"   Retrieving parsed file: {parsed_file_id}")
        retrieved = await content_steward.get_parsed_file(
            parsed_file_id=parsed_file_id,
            user_context=user_context
        )
        
        if not retrieved:
            print("❌ Failed to retrieve parsed file")
            return False
        
        print(f"✅ Parsed file retrieved")
        
        # Test list_parsed_files
        print(f"   Listing parsed files for file_id: {file_id}")
        parsed_files = await content_steward.list_parsed_files(
            file_id=file_id,
            user_context=user_context
        )
        
        if not isinstance(parsed_files, list):
            print("❌ Failed to list parsed files")
            return False
        
        print(f"✅ Parsed files listed: {len(parsed_files)} files")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Content Steward APIs: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_librarian_apis():
    """Test Librarian content metadata and embeddings APIs."""
    print("\n" + "="*80)
    print("TEST 4: Librarian Content Metadata & Embeddings APIs")
    print("="*80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from backend.smart_city.services.librarian.librarian_service import LibrarianService
        
        # Initialize DI Container
        di_container = DIContainerService("test_platform")
        
        # Initialize Public Works Foundation
        pwf = PublicWorksFoundationService(di_container=di_container)
        await pwf.initialize_foundation()
        
        # Register in DI Container (required for Smart City services to access it)
        di_container.public_works_foundation = pwf
        
        # Initialize Librarian
        # Note: Smart City services access Public Works directly (no Platform Gateway needed)
        librarian = LibrarianService(
            di_container=di_container
        )
        await librarian.initialize()
        
        print("✅ Librarian initialized")
        
        # Test data
        file_id = str(uuid.uuid4())
        parsed_file_id = f"parsed_{uuid.uuid4()}"
        user_context = {"tenant_id": "test_tenant", "user_id": "test_user", "permissions": ["write", "read", "execute"]}
        
        # Test content metadata storage
        content_metadata = {
            "content_type": "structured",
            "structure_type": "table",
            "schema": {
                "columns": ["col1", "col2"],
                "data_types": {"col1": "string", "col2": "integer"}
            },
            "columns": ["col1", "col2"],
            "data_types": {"col1": "string", "col2": "integer"},
            "row_count": 10,
            "column_count": 2,
            "parsing_method": "test",
            "parsing_confidence": 1.0
        }
        
        print(f"   Storing content metadata")
        store_metadata_result = await librarian.store_content_metadata(
            file_id=file_id,
            parsed_file_id=parsed_file_id,
            content_metadata=content_metadata,
            user_context=user_context
        )
        
        if not store_metadata_result.get("success"):
            print(f"❌ Failed to store content metadata: {store_metadata_result}")
            return False
        
        content_id = store_metadata_result.get("content_id")
        print(f"✅ Content metadata stored: {content_id}")
        
        # Test retrieval
        print(f"   Retrieving content metadata: {content_id}")
        retrieved_metadata = await librarian.get_content_metadata(
            content_id=content_id,
            user_context=user_context
        )
        
        if not retrieved_metadata:
            print("❌ Failed to retrieve content metadata")
            return False
        
        print(f"✅ Content metadata retrieved")
        
        # Test embeddings storage (mock embeddings)
        embeddings = [{
            "column_name": "col1",
            "metadata_embedding": [0.1] * 384,
            "meaning_embedding": [0.2] * 384,
            "samples_embedding": [0.3] * 384,
            "semantic_id": f"semantic_col1_{uuid.uuid4().hex[:8]}"
        }]
        
        print(f"   Storing embeddings")
        store_embeddings_result = await librarian.store_embeddings(
            content_id=content_id,
            file_id=file_id,
            embeddings=embeddings,
            user_context=user_context
        )
        
        if not store_embeddings_result.get("success"):
            print(f"❌ Failed to store embeddings: {store_embeddings_result}")
            return False
        
        print(f"✅ Embeddings stored: {store_embeddings_result.get('stored_count')} embeddings")
        
        # Test retrieval
        print(f"   Retrieving embeddings")
        retrieved_embeddings = await librarian.get_embeddings(
            content_id=content_id,
            user_context=user_context
        )
        
        if not retrieved_embeddings or len(retrieved_embeddings) == 0:
            print("❌ Failed to retrieve embeddings")
            return False
        
        print(f"✅ Embeddings retrieved: {len(retrieved_embeddings)} embeddings")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Librarian APIs: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("SMART CITY NEW APIS - END-TO-END TEST SUITE")
    print("="*80)
    
    results = {}
    
    # Run tests
    results["semantic_data_abstraction"] = await test_semantic_data_abstraction()
    results["observability_abstraction"] = await test_observability_abstraction()
    results["content_steward_apis"] = await test_content_steward_parsed_file_apis()
    results["librarian_apis"] = await test_librarian_apis()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

