#!/usr/bin/env python3
"""
Initialization Module - File Parser Service

Handles service initialization, infrastructure setup, and Curator registration.
REUSED from existing implementation with workflow_id support added.
"""

from typing import Dict, Any


class Initialization:
    """Initialization module for File Parser Service."""
    
    def __init__(self, service_instance):
        """Initialize with service instance."""
        self.service = service_instance
    
    async def initialize(self) -> bool:
        """
        Initialize File Parser Service with full utility usage.
        
        Uses standard utility pattern:
        - Telemetry tracking (start/complete)
        - Error handling with audit
        - Health metrics
        - Smart City service discovery
        - Curator registration
        """
        await self.service.log_operation_with_telemetry("file_parser_initialize_start", success=True)
        
        try:
            # 1. Discover Smart City services (via Curator)
            # Business Enablement uses Smart City SOA APIs, not direct infrastructure access
            self.service.librarian = await self.service.get_librarian_api()
            self.service.content_steward = await self.service.get_content_steward_api()
            self.service.data_steward = await self.service.get_data_steward_api()
            self.service.nurse = await self.service.get_nurse_api()  # ✅ Added for observability
            
            # Log discovery results for debugging
            if not self.service.content_steward:
                self.service.logger.warning("⚠️ Content Steward API not discovered via Curator - file retrieval may fail")
            else:
                self.service.logger.info(f"✅ Content Steward API discovered: {type(self.service.content_steward).__name__}")
            
            # 2. Verify file parsing abstractions are available via Platform Gateway
            # File parsing now uses individual file type abstractions (excel_processing, pdf_processing, etc.)
            # following the 5-layer architecture pattern. We don't need document_intelligence anymore.
            # Test that we can access at least one file parsing abstraction to verify Platform Gateway is working
            try:
                test_abstraction = self.service.platform_gateway.get_abstraction(
                    realm_name=self.service.realm_name,
                    abstraction_name="excel_processing"
                )
                if test_abstraction:
                    self.service.logger.info("✅ File parsing abstractions accessible via Platform Gateway")
                else:
                    self.service.logger.warning("⚠️ File parsing abstractions may not be fully initialized")
            except Exception as e:
                self.service.logger.warning(f"⚠️ Could not verify file parsing abstractions: {e}")
                # Don't fail initialization - abstractions may be lazy-loaded
            
            # 3. Register with Curator (Phase 2 pattern with CapabilityDefinition structure)
            # Note: Enabling services provide SOA APIs only (no MCP tools)
            # MCP servers are at the orchestrator level for use case-level tools
            await self.service.register_with_curator(
                capabilities=[
                    {
                        "name": "file_parsing",
                        "protocol": "FileParserServiceProtocol",
                        "description": "Parse files into structured formats",
                        "contracts": {
                            "soa_api": {
                                "api_name": "parse_file",
                                "endpoint": "/api/v1/file-parser/parse",
                                "method": "POST",
                                "handler": self.service.parse_file,
                                "metadata": {
                                    "description": "Parse file into structured format",
                                    "parameters": ["file_id", "parse_options"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "content.parse_file",
                            "semantic_api": "/api/v1/content-pillar/parse-file"
                        }
                    },
                    {
                        "name": "format_detection",
                        "protocol": "FileParserServiceProtocol",
                        "description": "Detect file type and format",
                        "contracts": {
                            "soa_api": {
                                "api_name": "detect_file_type",
                                "endpoint": "/api/v1/file-parser/detect-type",
                                "method": "POST",
                                "handler": self.service.detect_file_type,
                                "metadata": {
                                    "description": "Detect file type",
                                    "parameters": ["file_id"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "content.detect_file_type",
                            "semantic_api": "/api/v1/content-pillar/detect-file-type"
                        }
                    },
                    {
                        "name": "content_extraction",
                        "protocol": "FileParserServiceProtocol",
                        "description": "Extract plain text content from files",
                        "contracts": {
                            "soa_api": {
                                "api_name": "extract_content",
                                "endpoint": "/api/v1/file-parser/extract-content",
                                "method": "POST",
                                "handler": self.service.extract_content,
                                "metadata": {
                                    "description": "Extract plain text content",
                                    "parameters": ["file_id"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "content.extract_content",
                            "semantic_api": "/api/v1/content-pillar/extract-content"
                        }
                    },
                    {
                        "name": "metadata_extraction",
                        "protocol": "FileParserServiceProtocol",
                        "description": "Extract metadata from files",
                        "contracts": {
                            "soa_api": {
                                "api_name": "extract_metadata",
                                "endpoint": "/api/v1/file-parser/extract-metadata",
                                "method": "POST",
                                "handler": self.service.extract_metadata,
                                "metadata": {
                                    "description": "Extract file metadata",
                                    "parameters": ["file_id"]
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "content.extract_metadata",
                            "semantic_api": "/api/v1/content-pillar/extract-metadata"
                        }
                    }
                ]
            )
            
            self.service.logger.info("✅ File Parser Service registered with Curator")
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry("file_parser_initialize_complete", success=True)
            
            return True
            
        except Exception as e:
            self.service.logger.error(f"❌ File Parser Service initialization failed: {e}")
            import traceback
            self.service.logger.error(f"   Traceback: {traceback.format_exc()}")
            await self.service.handle_error_with_audit(e, "file_parser_initialize")
            await self.service.log_operation_with_telemetry("file_parser_initialize_complete", success=False, details={"error": str(e)})
            return False



