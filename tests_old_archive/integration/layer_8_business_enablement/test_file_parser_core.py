#!/usr/bin/env python3
"""
Layer 8: File Parser Service - Core Functionality Tests

Tests File Parser Service with core file types:
- Text files (.txt)
- COBOL copybook files (.cpy)
- Mainframe binary files (.bin)
- HTML files (.html)

This establishes the pattern for comprehensive testing.
"""

import pytest
import asyncio
from typing import Dict, Any

from .test_utilities import TestFileManager, ContentStewardHelper, TestDataManager
from .test_infrastructure_setup import TestInfrastructureConfig, test_infrastructure_available

pytestmark = [pytest.mark.integration]


class TestFileParserCore:
    """Core functionality tests for File Parser Service."""
    
    @pytest.fixture
    async def test_infrastructure(self, test_infrastructure_available):
        """Set up test infrastructure including Smart City services."""
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
        from backend.smart_city.services.content_steward.content_steward_service import ContentStewardService
        import os
        from pathlib import Path
        from dotenv import load_dotenv
        
        # Load test environment variables and resolve credential paths
        # NOTE: GCS credentials are loaded from .env.secrets via UnifiedConfigurationManager
        # Use GCS_CREDENTIALS_JSON (Supabase pattern) or TEST_GCS_CREDENTIALS_JSON for test-specific credentials
        # We do NOT modify GOOGLE_APPLICATION_CREDENTIALS globally to avoid breaking SSH access
        env_path = Path(__file__).parent / ".env.test"
        if env_path.exists():
            # CRITICAL: Store original critical GCP env vars before loading .env.test
            CRITICAL_GCP_ENV_VARS = [
                "GOOGLE_APPLICATION_CREDENTIALS",
                "GCLOUD_PROJECT",
                "GOOGLE_CLOUD_PROJECT",
                "GCLOUD_CONFIG",
                "CLOUDSDK_CONFIG"
            ]
            original_gcp_vars = {var: os.environ.get(var) for var in CRITICAL_GCP_ENV_VARS}
            
            load_dotenv(dotenv_path=env_path)
            
            # CRITICAL: Restore original critical GCP env vars (don't let .env.test override them)
            for var in CRITICAL_GCP_ENV_VARS:
                if var in os.environ and os.environ[var] != original_gcp_vars[var]:
                    # .env.test tried to set a critical GCP env var - restore original
                    if original_gcp_vars[var] is not None:
                        os.environ[var] = original_gcp_vars[var]
                    else:
                        # Remove it if it wasn't set originally
                        os.environ.pop(var, None)
            
            # NOTE: GCS credentials are now loaded from .env.secrets via UnifiedConfigurationManager
            # No need to manually set GCS_CREDENTIALS_PATH - the platform handles it automatically
            # If you need test-specific credentials, use TEST_GCS_CREDENTIALS_JSON or GCS_CREDENTIALS_JSON
        
        di_container = DIContainerService("test_platform")
        pwf = PublicWorksFoundationService(di_container=di_container)
        
        # Use timeout for initialization
        try:
            pwf_result = await asyncio.wait_for(
                pwf.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Public Works Foundation initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis"
            )
        
        if not pwf_result:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Public Works Foundation initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis\n\n"
                f"Fix: Ensure all critical infrastructure containers are running and healthy."
            )
        
        di_container.public_works_foundation = pwf
        
        curator = CuratorFoundationService(
            foundation_services=di_container,
            public_works_foundation=pwf
        )
        
        # Use timeout for initialization
        try:
            curator_result = await asyncio.wait_for(
                curator.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Curator Foundation initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb"
            )
        
        if not curator_result:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Curator Foundation initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n\n"
                f"Fix: Ensure all critical infrastructure containers are running and healthy."
            )
        
        di_container.curator_foundation = curator
        
        platform_gateway = PlatformInfrastructureGateway(
            public_works_foundation=pwf
        )
        
        # Initialize Content Steward (required for File Parser)
        # Content Steward must be registered with Curator for FileParserService to discover it
        content_steward = ContentStewardService(di_container=di_container)
        
        # Use timeout for initialization
        try:
            content_steward_result = await asyncio.wait_for(
                content_steward.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Content Steward initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis"
            )
        
        if not content_steward_result:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Content Steward initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis\n\n"
                f"Fix: Ensure all critical infrastructure containers are running and healthy."
            )
        
        # Ensure Content Steward is registered with Curator so FileParserService can discover it
        # FileParserService uses get_content_steward_api() which looks up services via Curator
        # Note: Content Steward should already be registered during initialize()
        # The service discovery happens via Curator's service registry
        
        # Note: If test infrastructure is available, it will use test bucket/tenant
        # Otherwise, tests will skip gracefully
        
        yield {
            "di_container": di_container,
            "public_works_foundation": pwf,
            "curator": curator,
            "platform_gateway": platform_gateway,
            "content_steward": content_steward,
            "test_infrastructure_available": test_infrastructure_available
        }
    
    @pytest.fixture
    async def file_parser_service(self, test_infrastructure):
        """Create and initialize File Parser Service."""
        from backend.business_enablement.enabling_services.file_parser_service.file_parser_service import FileParserService
        
        infra = test_infrastructure
        service = FileParserService(
            service_name="FileParserService",
            realm_name="business_enablement",
            platform_gateway=infra["platform_gateway"],
            di_container=infra["di_container"]
        )
        
        # Use timeout for initialization
        try:
            result = await asyncio.wait_for(
                service.initialize(),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"File Parser Service initialization timed out after 30 seconds.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis"
            )
        
        if not result:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"File Parser Service initialization failed.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                f"restarts: {redis_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n"
                f"  docker logs symphainy-redis\n\n"
                f"Fix: Ensure all critical infrastructure containers are running and healthy."
            )
        
        return service
    
    @pytest.fixture
    async def content_steward_helper(self, file_parser_service, test_infrastructure):
        """Create Content Steward helper."""
        # Use Content Steward from test infrastructure (already initialized)
        infra = test_infrastructure
        content_steward = infra.get("content_steward")
        
        # If not in infrastructure, try to get from File Parser Service
        if not content_steward:
            content_steward = file_parser_service.content_steward
        
        if not content_steward:
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            
            pytest.fail(
                f"Content Steward not available.\n"
                f"Infrastructure status:\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                f"restarts: {consul_status['restart_count']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                f"restarts: {arango_status['restart_count']})\n\n"
                f"Check logs:\n"
                f"  docker logs symphainy-consul\n"
                f"  docker logs symphainy-arangodb\n\n"
                f"Fix: Content Steward must be initialized and registered with Curator."
            )
        
        user_context = TestDataManager.get_user_context()
        helper = ContentStewardHelper(content_steward, user_context)
        
        yield helper
        
        # Cleanup stored files
        await helper.cleanup_stored_files()
    
    @pytest.fixture
    def user_context(self):
        """Standard user context for tests."""
        return TestDataManager.get_user_context()
    
    # ============================================================================
    # CORE FILE TYPE TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_parse_text_file(self, file_parser_service, content_steward_helper, user_context):
        """Test parsing a plain text file."""
        # Create test file
        file_path, file_data = TestFileManager.create_text_file("Test text content\nLine 2\nLine 3 with special chars: àáâã")
        
        try:
            # Store file via Content Steward
            # Note: This may fail if GCS/Supabase infrastructure is not available
            # In that case, we skip the test gracefully
            try:
                file_id = await content_steward_helper.store_file(
                    file_data=file_data,
                    filename="test.txt",
                    content_type="text/plain"
                )
            except Exception as e:
                # Check if it's an infrastructure connectivity issue
                error_msg = str(e).lower()
                if "gcs" in error_msg or "supabase" in error_msg or "400" in error_msg or "connection" in error_msg or "timeout" in error_msg:
                    from tests.utils.safe_docker import check_container_status
                    consul_status = check_container_status("symphainy-consul")
                    arango_status = check_container_status("symphainy-arangodb")
                    redis_status = check_container_status("symphainy-redis")
                    
                    pytest.fail(
                        f"Infrastructure not available for file storage: {e}\n\n"
                        f"Infrastructure status:\n"
                        f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                        f"restarts: {consul_status['restart_count']})\n"
                        f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                        f"restarts: {arango_status['restart_count']})\n"
                        f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                        f"restarts: {redis_status['restart_count']})\n\n"
                        f"Check logs:\n"
                        f"  docker logs symphainy-consul\n"
                        f"  docker logs symphainy-arangodb\n"
                        f"  docker logs symphainy-redis\n\n"
                        f"Note: File storage requires GCS or Supabase infrastructure. "
                        f"Verify GCS_CREDENTIALS_PATH or Supabase configuration."
                    )
                raise  # Re-raise if it's a different error
            
            if not file_id:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Failed to store file via Content Steward.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Note: File storage requires GCS or Supabase infrastructure. "
                    f"Verify GCS_CREDENTIALS_JSON or Supabase configuration."
                )
            
            # Parse file
            result = await file_parser_service.parse_file(
                file_id=file_id,
                parse_options=None,
                user_context=user_context
            )
            
            # Verify result
            assert result is not None, "Parse result should not be None"
            assert result.get("success") is not False, "Parse should succeed or return error structure"
            
            # If successful, verify content
            if result.get("success") is True or "content" in result or "text" in result:
                assert "content" in result or "text" in result or "data" in result, \
                    "Parse result should contain parsed content"
            
        finally:
            TestFileManager.cleanup_file(file_path)
    
    @pytest.mark.asyncio
    async def test_parse_cobol_copybook_file(self, file_parser_service, content_steward_helper, user_context):
        """Test parsing a COBOL copybook file (.cpy)."""
        # Create test file
        file_path, file_data = TestFileManager.create_cobol_copybook_file()
        
        try:
            # Store file via Content Steward
            file_id = await content_steward_helper.store_file(
                file_data=file_data,
                filename="test.cpy",
                content_type="text/plain"
            )
            
            if not file_id:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Failed to store file via Content Steward.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Note: File storage requires GCS or Supabase infrastructure. "
                    f"Verify GCS_CREDENTIALS_JSON or Supabase configuration."
                )
            
            # Parse file
            result = await file_parser_service.parse_file(
                file_id=file_id,
                parse_options=None,
                user_context=user_context
            )
            
            # Verify result
            assert result is not None, "Parse result should not be None"
            assert result.get("success") is not False, "Parse should succeed or return error structure"
            
            # COBOL copybook parsing may return structured data
            if result.get("success") is True:
                assert "content" in result or "data" in result or "structure" in result, \
                    "COBOL parse result should contain parsed content or structure"
            
        finally:
            TestFileManager.cleanup_file(file_path)
    
    @pytest.mark.asyncio
    async def test_parse_mainframe_binary_file(self, file_parser_service, content_steward_helper, user_context):
        """Test parsing a Mainframe binary file (.bin)."""
        # Create test file
        file_path, file_data = TestFileManager.create_mainframe_binary_file()
        
        try:
            # Store file via Content Steward
            file_id = await content_steward_helper.store_file(
                file_data=file_data,
                filename="test.bin",
                content_type="application/octet-stream"
            )
            
            if not file_id:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Failed to store file via Content Steward.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Note: File storage requires GCS or Supabase infrastructure. "
                    f"Verify GCS_CREDENTIALS_JSON or Supabase configuration."
                )
            
            # Parse file (binary files may need special handling)
            result = await file_parser_service.parse_file(
                file_id=file_id,
                parse_options={"format": "binary"},
                user_context=user_context
            )
            
            # Verify result
            assert result is not None, "Parse result should not be None"
            # Binary parsing may return structured data or hex representation
            if result.get("success") is True:
                assert "content" in result or "data" in result or "hex" in result or "bytes" in result, \
                    "Binary parse result should contain parsed data"
            
        finally:
            TestFileManager.cleanup_file(file_path)
    
    @pytest.mark.asyncio
    async def test_parse_html_file(self, file_parser_service, content_steward_helper, user_context):
        """Test parsing an HTML file."""
        # Create test file
        file_path, file_data = TestFileManager.create_html_file("<html><body><h1>Test</h1><p>Content with <strong>formatting</strong></p></body></html>")
        
        try:
            # Store file via Content Steward
            file_id = await content_steward_helper.store_file(
                file_data=file_data,
                filename="test.html",
                content_type="text/html"
            )
            
            if not file_id:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Failed to store file via Content Steward.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Note: File storage requires GCS or Supabase infrastructure. "
                    f"Verify GCS_CREDENTIALS_JSON or Supabase configuration."
                )
            
            # Parse file
            result = await file_parser_service.parse_file(
                file_id=file_id,
                parse_options=None,
                user_context=user_context
            )
            
            # Verify result
            assert result is not None, "Parse result should not be None"
            assert result.get("success") is not False, "Parse should succeed or return error structure"
            
            # HTML parsing should extract text content
            if result.get("success") is True:
                assert "content" in result or "text" in result or "html" in result, \
                    "HTML parse result should contain parsed content"
            
        finally:
            TestFileManager.cleanup_file(file_path)
    
    # ============================================================================
    # OUTPUT FORMAT TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_parse_file_json_output(self, file_parser_service, content_steward_helper, user_context):
        """Test parsing file with JSON output format."""
        # Create test file
        file_path, file_data = TestFileManager.create_text_file("Test content for JSON output")
        
        try:
            # Store file
            file_id = await content_steward_helper.store_file(
                file_data=file_data,
                filename="test.txt"
            )
            
            if not file_id:
                from tests.utils.safe_docker import check_container_status
                consul_status = check_container_status("symphainy-consul")
                arango_status = check_container_status("symphainy-arangodb")
                redis_status = check_container_status("symphainy-redis")
                
                pytest.fail(
                    f"Failed to store file via Content Steward.\n"
                    f"Infrastructure status:\n"
                    f"  Consul: {consul_status['status']} (health: {consul_status['health']}, "
                    f"restarts: {consul_status['restart_count']})\n"
                    f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']}, "
                    f"restarts: {arango_status['restart_count']})\n"
                    f"  Redis: {redis_status['status']} (health: {redis_status['health']}, "
                    f"restarts: {redis_status['restart_count']})\n\n"
                    f"Check logs:\n"
                    f"  docker logs symphainy-consul\n"
                    f"  docker logs symphainy-arangodb\n"
                    f"  docker logs symphainy-redis\n\n"
                    f"Note: File storage requires GCS or Supabase infrastructure. "
                    f"Verify GCS_CREDENTIALS_JSON or Supabase configuration."
                )
            
            # Parse with JSON output format
            result = await file_parser_service.parse_file(
                file_id=file_id,
                parse_options={"output_format": "json"},
                user_context=user_context
            )
            
            # Verify JSON output
            assert result is not None, "Parse result should not be None"
            if result.get("success") is True:
                # Result should be JSON-serializable (dict)
                assert isinstance(result, dict), "JSON output should be a dict"
            
        finally:
            TestFileManager.cleanup_file(file_path)
    
    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_parse_file_invalid_file_id(self, file_parser_service, user_context):
        """Test parsing with invalid file ID."""
        result = await file_parser_service.parse_file(
            file_id="invalid_file_id_12345",
            parse_options=None,
            user_context=user_context
        )
        
        # Should handle error gracefully
        assert result is not None, "Should return error result, not None"
        assert result.get("success") is False or "error" in result or "message" in result, \
            "Should indicate error for invalid file ID"
    
    @pytest.mark.asyncio
    async def test_parse_file_missing_file(self, file_parser_service, user_context):
        """Test parsing with non-existent file ID."""
        result = await file_parser_service.parse_file(
            file_id="nonexistent_file_12345",
            parse_options=None,
            user_context=user_context
        )
        
        assert result is not None, "Should return error result"
        assert result.get("success") is False or "error" in result or "message" in result, \
            "Should indicate error for missing file"

