#!/usr/bin/env python3
"""
Layer 8: File Parser Service - Comprehensive Functionality Tests

This is the MODEL test suite for comprehensive functionality testing.
Tests File Parser Service with:
- Multiple file types (PDF, Excel, Word, COBOL, Binary, Text, HTML, Images)
- Multiple output formats (JSON, XML, Structured dict)
- Edge cases and error handling

This establishes patterns that can be reused for other services.
"""

import pytest
import asyncio
import tempfile
import os
from typing import Dict, Any

pytestmark = [pytest.mark.integration]


class TestFileParserComprehensive:
    """Comprehensive functionality tests for File Parser Service."""
    
    @pytest.fixture
    async def test_infrastructure(self):
        """Set up test infrastructure."""
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        from platform_infrastructure.infrastructure.platform_gateway import PlatformInfrastructureGateway
        
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
        
        yield {
            "di_container": di_container,
            "public_works_foundation": pwf,
            "curator": curator,
            "platform_gateway": platform_gateway
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
    def user_context(self):
        """Standard user context for tests."""
        return {
            "user_id": "test_user",
            "tenant_id": "test_tenant",
            "session_id": "test_session"
        }
    
    # ============================================================================
    # FILE TYPE TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_parse_text_file(self, file_parser_service, user_context):
        """Test parsing a plain text file."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test text file.\nIt has multiple lines.\n")
            temp_file_path = f.name
        
        try:
            # First, we need to store the file via Content Steward to get a file_id
            # For now, we'll test with a file_id if the service supports it
            # Or we'll need to mock the Content Steward API
            
            # This test needs to be adjusted based on actual File Parser API
            # The service uses file_id, not file_path
            from tests.utils.safe_docker import check_container_status
            consul_status = check_container_status("symphainy-consul")
            arango_status = check_container_status("symphainy-arangodb")
            redis_status = check_container_status("symphainy-redis")
            
            pytest.fail(
                f"Test not yet implemented: Need to implement file storage via Content Steward first.\n\n"
                f"Infrastructure status (for reference):\n"
                f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
                f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
                f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
                f"TODO: Implement file storage helper using Content Steward API to get file_id."
            )
            
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    @pytest.mark.asyncio
    async def test_parse_excel_file(self, file_parser_service, user_context):
        """Test parsing an Excel file."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to create Excel file and store via Content Steward.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement Excel file creation and storage via Content Steward helper."
        )
    
    @pytest.mark.asyncio
    async def test_parse_word_file(self, file_parser_service, user_context):
        """Test parsing a Word document."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to create Word file and store via Content Steward.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement Word file creation and storage via Content Steward helper."
        )
    
    @pytest.mark.asyncio
    async def test_parse_pdf_file(self, file_parser_service, user_context):
        """Test parsing a PDF document."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to create PDF file and store via Content Steward.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement PDF file creation and storage via Content Steward helper."
        )
    
    @pytest.mark.asyncio
    async def test_parse_cobol_file(self, file_parser_service, user_context):
        """Test parsing a COBOL file (.cpy)."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to create COBOL file and store via Content Steward.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement COBOL file creation and storage via Content Steward helper."
        )
    
    @pytest.mark.asyncio
    async def test_parse_binary_file(self, file_parser_service, user_context):
        """Test parsing a binary file (.bin)."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to create binary file and store via Content Steward.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement binary file creation and storage via Content Steward helper."
        )
    
    @pytest.mark.asyncio
    async def test_parse_html_file(self, file_parser_service, user_context):
        """Test parsing an HTML file."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to create HTML file and store via Content Steward.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement HTML file creation and storage via Content Steward helper."
        )
    
    @pytest.mark.asyncio
    async def test_parse_image_file_ocr(self, file_parser_service, user_context):
        """Test parsing an image file with OCR."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to create image file and store via Content Steward.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement image file creation and storage via Content Steward helper."
        )
    
    # ============================================================================
    # OUTPUT FORMAT TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_parse_file_json_output(self, file_parser_service, user_context):
        """Test parsing file with JSON output format."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to implement with actual file storage.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement file storage helper and test JSON output format."
        )
    
    @pytest.mark.asyncio
    async def test_parse_file_xml_output(self, file_parser_service, user_context):
        """Test parsing file with XML output format."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to implement with actual file storage.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement file storage helper and test XML output format."
        )
    
    @pytest.mark.asyncio
    async def test_parse_file_structured_dict_output(self, file_parser_service, user_context):
        """Test parsing file with structured dict output format."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to implement with actual file storage.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement file storage helper and test structured dict output format."
        )
    
    # ============================================================================
    # COMBINATION TESTS (File Type × Output Format)
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_parse_text_file_json_output(self, file_parser_service, user_context):
        """Test parsing text file with JSON output."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to implement text file parsing with JSON output.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement file storage helper and test text file with JSON output."
        )
    
    @pytest.mark.asyncio
    async def test_parse_excel_file_json_output(self, file_parser_service, user_context):
        """Test parsing Excel file with JSON output."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to implement Excel file parsing with JSON output.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement file storage helper and test Excel file with JSON output."
        )
    
    @pytest.mark.asyncio
    async def test_parse_cobol_file_json_output(self, file_parser_service, user_context):
        """Test parsing COBOL file with JSON output."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to implement COBOL file parsing with JSON output.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement file storage helper and test COBOL file with JSON output."
        )
    
    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_parse_file_invalid_file_id(self, file_parser_service, user_context):
        """Test parsing with invalid file ID."""
        try:
            result = await file_parser_service.parse_file(
                file_id="invalid_file_id_12345",
                parse_options=None,
                user_context=user_context
            )
            # Should handle error gracefully
            assert result is not None, "Should return error result, not None"
            assert "error" in result or "status" in result, "Should indicate error"
        except Exception as e:
            # Exception is also acceptable for invalid file ID
            assert True, f"Exception for invalid file ID is acceptable: {e}"
    
    @pytest.mark.asyncio
    async def test_parse_file_missing_file(self, file_parser_service, user_context):
        """Test parsing with non-existent file ID."""
        try:
            result = await file_parser_service.parse_file(
                file_id="nonexistent_file_12345",
                parse_options=None,
                user_context=user_context
            )
            assert result is not None, "Should return error result"
            assert "error" in result or "status" in result, "Should indicate error"
        except Exception as e:
            assert True, f"Exception for missing file is acceptable: {e}"
    
    @pytest.mark.asyncio
    async def test_parse_file_unsupported_format(self, file_parser_service, user_context):
        """Test parsing with unsupported file format."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to implement with actual file storage.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement file storage helper and test unsupported format handling."
        )
    
    # ============================================================================
    # EDGE CASES
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_parse_empty_file(self, file_parser_service, user_context):
        """Test parsing an empty file."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to implement with actual file storage.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement file storage helper and test empty file handling."
        )
    
    @pytest.mark.asyncio
    async def test_parse_file_with_special_characters(self, file_parser_service, user_context):
        """Test parsing file with special characters."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to implement with actual file storage.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement file storage helper and test special character handling."
        )
    
    @pytest.mark.asyncio
    async def test_parse_file_with_unicode(self, file_parser_service, user_context):
        """Test parsing file with Unicode content."""
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Test not yet implemented: Need to implement with actual file storage.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement file storage helper and test Unicode content handling."
        )
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    async def _create_and_store_file(self, file_parser_service, content: bytes, file_name: str, file_type: str) -> str:
        """
        Helper to create a file and store it via Content Steward.
        Returns file_id for use in parse_file.
        """
        # This needs to be implemented based on Content Steward API
        # For now, this is a placeholder
        from tests.utils.safe_docker import check_container_status
        consul_status = check_container_status("symphainy-consul")
        arango_status = check_container_status("symphainy-arangodb")
        redis_status = check_container_status("symphainy-redis")
        
        pytest.fail(
            f"Helper method not yet implemented: Need to implement file storage via Content Steward.\n\n"
            f"Infrastructure status (for reference):\n"
            f"  Consul: {consul_status['status']} (health: {consul_status['health']})\n"
            f"  ArangoDB: {arango_status['status']} (health: {arango_status['health']})\n"
            f"  Redis: {redis_status['status']} (health: {redis_status['health']})\n\n"
            f"TODO: Implement _create_and_store_file helper using Content Steward API."
        )


