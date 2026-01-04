#!/usr/bin/env python3
"""
Data Solution Orchestrator

WHAT: Orchestrates the complete data solution flow: Ingest → Parse → Embed → Expose
HOW: Direct SOA API calls to Smart City services, delegates to enabling services

This orchestrator is the foundation layer for all data operations in the platform.
It handles the end-to-end data lifecycle without touching raw client data after ingestion.

Architecture:
- Extends OrchestratorBase for Smart City access
- Uses direct SOA API calls (no SDK)
- Delegates to enabling services (FileParserService, EmbeddingService, etc.)
- Propagates workflow_id and correlation IDs throughout
"""

import os
import sys
import uuid
import json
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class DataSolutionOrchestrator(OrchestratorBase):
    """
    Data Solution Orchestrator - Foundation layer for data operations.
    
    Orchestrates the complete data solution flow:
    1. Ingest: File upload → Content Steward
    2. Parse: File parsing → Parsed file storage
    3. Embed: Representative sampling → Semantic embeddings
    4. Expose: Semantic layer exposure for other solutions
    
    Key Principles:
    - Direct SOA API calls to Smart City services (no SDK)
    - workflow_id propagation for end-to-end tracking
    - Correlation IDs (file_id, parsed_file_id, content_id) for data correlation
    - Lineage tracking for all operations
    - Observability recording for all operations
    """
    
    def __init__(self, delivery_manager):
        """
        Initialize Data Solution Orchestrator.
        
        Args:
            delivery_manager: Reference to DeliveryManagerService for service access
        """
        # Extract parameters from delivery_manager (which extends ManagerServiceBase)
        super().__init__(
            service_name="DataSolutionOrchestratorService",
            realm_name=delivery_manager.realm_name,
            platform_gateway=delivery_manager.platform_gateway,
            di_container=delivery_manager.di_container,
            business_orchestrator=delivery_manager  # Keep for backward compatibility
        )
        self.delivery_manager = delivery_manager
        self.orchestrator_name = "DataSolutionOrchestrator"
    
    async def initialize(self) -> bool:
        """
        Initialize Data Solution Orchestrator.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.logger.info(f"🚀 Initializing {self.orchestrator_name}...")
            
            # Call parent initialization
            result = await super().initialize()
            if not result:
                self.logger.warning("⚠️ Parent initialization failed, continuing anyway...")
            
            self.logger.info(f"✅ {self.orchestrator_name} initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.orchestrator_name}: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return False
    
    async def orchestrate_data_ingest(
        self,
        file_data: bytes,
        file_name: str,
        file_type: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate data ingestion.
        
        Flow:
        1. Upload file → Content Steward (direct SOA API)
        2. Track lineage → Data Steward (direct SOA API)
        3. Record observability → Nurse (direct SOA API)
        4. Return file_id and workflow_id
        
        Args:
            file_data: File data as bytes
            file_name: Name of the file
            file_type: MIME type or file extension
            user_context: Optional user context (includes workflow_id from Phase 0.5)
        
        Returns:
            Dict with success status, file_id, and workflow_id
        """
        try:
            # Get workflow_id from user_context (generated at gateway in Phase 0.5)
            # If not present, generate new one (fallback for direct calls)
            workflow_id = (
                user_context.get("workflow_id") if user_context else None
            ) or str(uuid.uuid4())
            
            self.logger.info(f"📥 Orchestrating data ingestion: {file_name} (workflow_id: {workflow_id})")
            
            # Upload via Content Steward (direct SOA API call - no SDK)
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "error": "Content Steward service not available",
                    "workflow_id": workflow_id
                }
            
            upload_result = await data_steward.process_upload(
                file_data=file_data,
                content_type=file_type,
                metadata={"ui_name": file_name},
                user_context=user_context,
                workflow_id=workflow_id
            )
            
            if not upload_result.get("success"):
                return {
                    "success": False,
                    "error": upload_result.get("error", "File upload failed"),
                    "workflow_id": workflow_id
                }
            
            file_id = upload_result.get("file_id")
            if not file_id:
                return {
                    "success": False,
                    "error": "File upload succeeded but file_id not returned",
                    "workflow_id": workflow_id
                }
            
            # Track lineage (direct SOA API call)
            data_steward = await self.get_data_steward_api()
            if data_steward:
                try:
                    await data_steward.track_lineage(
                        lineage_data={
                            "source_id": user_context.get("user_id") if user_context else "system",
                            "target_id": file_id,
                            "operation": "file_upload",
                            "operation_type": "file_storage",
                            "correlation_ids": {
                                "workflow_id": workflow_id,
                                "user_id": user_context.get("user_id") if user_context else None,
                                "session_id": user_context.get("session_id") if user_context else None,
                                "file_id": file_id  # ✅ Correlation: file_id included
                            }
                        },
                        workflow_id=workflow_id,
                        user_context=user_context
                    )
                except Exception as lineage_error:
                    self.logger.warning(f"⚠️ Lineage tracking failed: {lineage_error}")
            
            # Record observability (direct SOA API call)
            nurse = await self.get_nurse_api()
            if nurse:
                try:
                    await nurse.record_platform_event(
                        event_type="log",
                        event_data={
                            "level": "info",
                            "message": f"File uploaded: {file_name}",
                            "service_name": self.__class__.__name__,
                            "file_id": file_id
                        },
                        trace_id=workflow_id,
                        user_context=user_context
                    )
                except Exception as observability_error:
                    self.logger.warning(f"⚠️ Observability recording failed: {observability_error}")
            
            self.logger.info(f"✅ Data ingestion complete: file_id={file_id}, workflow_id={workflow_id}")
            
            return {
                "success": True,
                "file_id": file_id,
                "workflow_id": workflow_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Data ingestion failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id if 'workflow_id' in locals() else None
            }
    
    async def orchestrate_data_parse(
        self,
        file_id: str,
        parse_options: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate data parsing.
        
        Flow:
        1. Parse file → FileParserService (enabling service - will be created in Phase 1)
        2. Store parsed file → Content Steward (direct SOA API)
        3. Extract metadata → ContentMetadataExtractionService (will be created in Phase 1)
        4. Store metadata → Librarian (direct SOA API)
        5. Track lineage → Data Steward (direct SOA API)
        6. Return parse_result and metadata
        
        NOTE: FileParserService and ContentMetadataExtractionService don't exist yet.
        This will break until Phase 1. That's intentional - break then fix.
        
        Args:
            file_id: File identifier from ingestion
            parse_options: Optional parsing options
            user_context: Optional user context (includes workflow_id)
            workflow_id: Optional workflow_id (if not in user_context)
        
        Returns:
            Dict with success status, parse_result, parsed_file_id, content_metadata, workflow_id
        """
        try:
            # Get workflow_id from user_context or parameter
            if not workflow_id:
                workflow_id = (
                    user_context.get("workflow_id") if user_context else None
                ) or str(uuid.uuid4())
            
            self.logger.info(f"📝 Orchestrating data parsing: file_id={file_id} (workflow_id: {workflow_id})")
            
            # Get FileParserService (Content realm service)
            try:
                from backend.content.services.file_parser_service.file_parser_service import FileParserService
                file_parser = FileParserService(
                    service_name="FileParserService",
                    realm_name="content",  # ✅ Content realm service
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await file_parser.initialize()
            except Exception as e:
                raise ValueError(f"FileParserService not available: {e}")
            
            # Parse file
            parse_result = await file_parser.parse_file(
                file_id=file_id,
                parse_options=parse_options,
                user_context=user_context
            )
            
            if not parse_result.get("success"):
                return {
                    "success": False,
                    "error": parse_result.get("error", "File parsing failed"),
                    "workflow_id": workflow_id
                }
            
            # Store parsed file via Content Steward (direct SOA API)
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "error": "Content Steward service not available",
                    "workflow_id": workflow_id
                }
            
            # Convert parsed data to bytes
            parsed_data_bytes = json.dumps(parse_result.get("data", {})).encode('utf-8')
            
            # Determine format_type and content_type
            parsing_type = parse_result.get("parsing_type", "structured")
            format_type = "json_structured" if parsing_type == "structured" else "json_chunks"
            content_type = parsing_type
            
            store_result = await data_steward.store_parsed_file(
                file_id=file_id,
                parsed_file_data=parsed_data_bytes,
                format_type=format_type,
                content_type=content_type,
                parse_result=parse_result,
                workflow_id=workflow_id
            )
            
            if not store_result.get("success"):
                return {
                    "success": False,
                    "error": store_result.get("error", "Parsed file storage failed"),
                    "workflow_id": workflow_id
                }
            
            parsed_file_id = store_result.get("parsed_file_id")
            if not parsed_file_id:
                return {
                    "success": False,
                    "error": "Parsed file storage succeeded but parsed_file_id not returned",
                    "workflow_id": workflow_id
                }
            
            # Extract content metadata (Content realm service)
            try:
                from backend.content.services.content_metadata_extraction_service.content_metadata_extraction_service import ContentMetadataExtractionService
                metadata_extractor = ContentMetadataExtractionService(
                    service_name="ContentMetadataExtractionService",
                    realm_name="content",  # ✅ Content realm service
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await metadata_extractor.initialize()
            except Exception as e:
                raise ValueError(f"ContentMetadataExtractionService not available: {e}")
            
            content_metadata = await metadata_extractor.extract_and_store_metadata(
                file_id=file_id,
                parsed_file_id=parsed_file_id,
                parse_result=parse_result,
                workflow_id=workflow_id,
                user_context=user_context
            )
            
            # Track lineage
            data_steward = await self.get_data_steward_api()
            if data_steward:
                try:
                    await data_steward.track_lineage(
                        lineage_data={
                            "source_id": file_id,
                            "target_id": parsed_file_id,
                            "operation": "file_parsing",
                            "operation_type": "data_transformation",
                            "correlation_ids": {
                                "workflow_id": workflow_id,
                                "user_id": user_context.get("user_id") if user_context else None,
                                "session_id": user_context.get("session_id") if user_context else None,
                                "file_id": file_id,  # ✅ Correlation: file_id included
                                "parsed_file_id": parsed_file_id  # ✅ Correlation: parsed_file_id included
                            }
                        },
                        workflow_id=workflow_id,
                        user_context=user_context
                    )
                except Exception as lineage_error:
                    self.logger.warning(f"⚠️ Lineage tracking failed: {lineage_error}")
            
            self.logger.info(f"✅ Data parsing complete: parsed_file_id={parsed_file_id}, workflow_id={workflow_id}")
            
            return {
                "success": True,
                "parse_result": parse_result,
                "parsed_file_id": parsed_file_id,
                "content_metadata": content_metadata,
                "workflow_id": workflow_id
            }
            
        except ValueError as ve:
            # Expected error for missing enabling services (Phase 1)
            self.logger.warning(f"⚠️ {str(ve)}")
            return {
                "success": False,
                "error": str(ve),
                "workflow_id": workflow_id if 'workflow_id' in locals() else None
            }
        except Exception as e:
            self.logger.error(f"❌ Data parsing failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id if 'workflow_id' in locals() else None
            }
    
    async def orchestrate_data_embed(
        self,
        file_id: str,
        parsed_file_id: str,
        content_metadata: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate semantic embedding creation.
        
        Flow:
        1. Create representative embeddings → EmbeddingService (will be created in Phase 1)
        2. Store embeddings → Librarian (direct SOA API)
        3. Track lineage → Data Steward (direct SOA API)
        4. Return embeddings_result
        
        NOTE: EmbeddingService doesn't exist yet.
        This will break until Phase 1. That's intentional - break then fix.
        
        Args:
            file_id: File identifier
            parsed_file_id: Parsed file identifier
            content_metadata: Content metadata from parsing
            user_context: Optional user context (includes workflow_id)
            workflow_id: Optional workflow_id (if not in user_context)
        
        Returns:
            Dict with success status, embeddings_count, content_id, workflow_id
        """
        try:
            # Get workflow_id from user_context or parameter
            if not workflow_id:
                workflow_id = (
                    user_context.get("workflow_id") if user_context else None
                ) or str(uuid.uuid4())
            
            self.logger.info(f"🧬 Orchestrating data embedding: file_id={file_id}, parsed_file_id={parsed_file_id} (workflow_id: {workflow_id})")
            
            # Get EmbeddingService (Content realm service)
            try:
                from backend.content.services.embedding_service.embedding_service import EmbeddingService
                embedding_service = EmbeddingService(
                    service_name="EmbeddingService",
                    realm_name="content",  # ✅ Content realm service
                    platform_gateway=self.delivery_manager.platform_gateway,
                    di_container=self.delivery_manager.di_container
                )
                await embedding_service.initialize()
            except Exception as e:
                raise ValueError(f"EmbeddingService not available: {e}")
            
            # Create embeddings using representative sampling (every 10th row)
            embeddings_result = await embedding_service.create_representative_embeddings(
                parsed_file_id=parsed_file_id,
                content_metadata=content_metadata,
                sampling_strategy="every_nth",
                n=10,  # Every 10th row
                user_context=user_context
            )
            
            if not embeddings_result.get("embeddings"):
                return {
                    "success": False,
                    "message": "No embeddings created",
                    "workflow_id": workflow_id
                }
            
            # Store via Librarian (direct SOA API)
            librarian = await self.get_librarian_api()
            if not librarian:
                return {
                    "success": False,
                    "error": "Librarian service not available",
                    "workflow_id": workflow_id
                }
            
            content_id = content_metadata.get("content_id")
            if not content_id:
                return {
                    "success": False,
                    "message": "content_id not found in content_metadata",
                    "workflow_id": workflow_id
                }
            
            await librarian.store_semantic_embeddings(
                content_id=content_id,
                file_id=file_id,
                embeddings=embeddings_result["embeddings"],
                workflow_id=workflow_id,
                user_context=user_context
            )
            
            # Track lineage
            data_steward = await self.get_data_steward_api()
            if data_steward:
                try:
                    await data_steward.track_lineage(
                        lineage_data={
                            "source_id": parsed_file_id,
                            "target_id": content_id,
                            "operation": "embedding_creation",
                            "operation_type": "semantic_processing",
                            "correlation_ids": {
                                "workflow_id": workflow_id,
                                "user_id": user_context.get("user_id") if user_context else None,
                                "session_id": user_context.get("session_id") if user_context else None,
                                "file_id": file_id,  # ✅ Correlation: file_id included
                                "parsed_file_id": parsed_file_id,  # ✅ Correlation: parsed_file_id included
                                "content_id": content_id  # ✅ Correlation: content_id included
                            }
                        },
                        workflow_id=workflow_id,
                        user_context=user_context
                    )
                except Exception as lineage_error:
                    self.logger.warning(f"⚠️ Lineage tracking failed: {lineage_error}")
            
            embeddings_count = len(embeddings_result.get("embeddings", []))
            self.logger.info(f"✅ Data embedding complete: embeddings_count={embeddings_count}, content_id={content_id}, workflow_id={workflow_id}")
            
            return {
                "success": True,
                "embeddings_count": embeddings_count,
                "content_id": content_id,
                "workflow_id": workflow_id
            }
            
        except ValueError as ve:
            # Expected error for missing enabling services (Phase 1)
            self.logger.warning(f"⚠️ {str(ve)}")
            return {
                "success": False,
                "error": str(ve),
                "workflow_id": workflow_id if 'workflow_id' in locals() else None
            }
        except Exception as e:
            self.logger.error(f"❌ Data embedding failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id if 'workflow_id' in locals() else None
            }
    
    async def orchestrate_data_expose(
        self,
        file_id: str,
        parsed_file_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate data exposure for other solutions.
        
        Flow:
        1. Get parsed file → Content Steward (direct SOA API)
        2. Get content metadata → Librarian (direct SOA API)
        3. Get semantic embeddings → Librarian (direct SOA API)
        4. Return exposed data (semantic view)
        
        This enables Operations/Business Outcomes to access parsed files
        without touching raw client data.
        
        Args:
            file_id: File identifier
            parsed_file_id: Optional parsed file identifier (if not provided, gets first one)
            user_context: Optional user context
        
        Returns:
            Dict with success status, parsed_data, content_metadata, embeddings info
        """
        try:
            self.logger.info(f"📤 Orchestrating data exposure: file_id={file_id}")
            
            # Get parsed file
            data_steward = await self.get_data_steward_api()
            if not data_steward:
                return {
                    "success": False,
                    "error": "Content Steward service not available"
                }
            
            # If parsed_file_id not provided, get it from file_id
            if not parsed_file_id:
                # Get parsed files for this file_id
                parsed_files = await data_steward.list_parsed_files(
                    file_id=file_id,
                    user_context=user_context
                )
                if parsed_files and len(parsed_files) > 0:
                    parsed_file_id = parsed_files[0].get("parsed_file_id")
            
            if not parsed_file_id:
                return {
                    "success": False,
                    "message": f"No parsed file found for file_id: {file_id}"
                }
            
            parsed_file = await data_steward.get_parsed_file(
                parsed_file_id=parsed_file_id,
                user_context=user_context
            )
            
            if not parsed_file:
                return {
                    "success": False,
                    "error": f"Parsed file not found: {parsed_file_id}"
                }
            
            # Get content metadata
            librarian = await self.get_librarian_api()
            content_metadata = None
            embeddings = []
            
            if librarian:
                try:
                    content_metadata = await librarian.get_content_metadata(
                        file_id=file_id,
                        user_context=user_context
                    )
                    
                    # Get semantic embeddings (optional - may not exist yet)
                    if content_metadata and content_metadata.get("content_id"):
                        try:
                            embeddings = await librarian.get_semantic_embeddings(
                                content_id=content_metadata["content_id"],
                                user_context=user_context
                            )
                        except Exception as e:
                            # Embeddings may not exist yet - that's OK
                            self.logger.debug(f"Embeddings not available: {e}")
                except Exception as metadata_error:
                    self.logger.warning(f"⚠️ Content metadata retrieval failed: {metadata_error}")
            
            self.logger.info(f"✅ Data exposure complete: file_id={file_id}, parsed_file_id={parsed_file_id}, embeddings_available={len(embeddings) > 0}")
            
            # Return exposed data (semantic view)
            return {
                "success": True,
                "parsed_data": parsed_file.get("data") if parsed_file else None,
                "content_metadata": content_metadata,
                "embeddings_available": len(embeddings) > 0,
                "embeddings_count": len(embeddings),
                "exposed_via": "semantic_layer",
                "raw_client_data": False  # Not touching raw client data
            }
            
        except Exception as e:
            self.logger.error(f"❌ Data exposure failed: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }


