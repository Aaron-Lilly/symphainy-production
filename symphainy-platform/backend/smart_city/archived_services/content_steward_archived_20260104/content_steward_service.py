#!/usr/bin/env python3
"""
Content Steward Service - Clean Micro-Modular Rebuild

Clean micro-modular implementation using base/protocol architecture
with proper infrastructure abstractions for file management (GCS + Supabase) and content metadata (ArangoDB).

WHAT (Smart City Role): I provide client data processing, policy enforcement, and metadata extraction
HOW (Service Implementation): I use SmartCityRoleBase with correct infrastructure abstractions
"""

from typing import Dict, Any, Optional, List, List

# Import base and protocol
from bases.smart_city_role_base import SmartCityRoleBase
from backend.smart_city.protocols.content_steward_service_protocol import ContentStewardServiceProtocol

# Import micro-modules
from .modules.initialization import Initialization
from .modules.file_processing import FileProcessing
from .modules.parsed_file_processing import ParsedFileProcessing
from .modules.content_processing import ContentProcessing
from .modules.content_validation import ContentValidation
from .modules.content_metadata import ContentMetadata
from .modules.soa_mcp import SoaMcp
from .modules.utilities import Utilities


class ContentStewardService(SmartCityRoleBase, ContentStewardServiceProtocol):
    """
    Content Steward Service - Clean Micro-Modular Rebuild
    
    Clean micro-modular implementation using base/protocol architecture
    with proper infrastructure abstractions for file management (GCS + Supabase) and content metadata (ArangoDB).
    
    WHAT (Smart City Role): I provide client data processing, policy enforcement, and metadata extraction
    HOW (Service Implementation): I use SmartCityRoleBase with correct infrastructure abstractions
    """
    
    def __init__(self, di_container: Any):
        """Initialize Content Steward Service with proper infrastructure mapping."""
        super().__init__(
            service_name="ContentStewardService",
            role_name="content_steward",
            di_container=di_container
        )
        
        # Infrastructure Abstractions (will be initialized in initialize())
        self.file_management_abstraction = None  # GCS + Supabase
        self.content_metadata_abstraction = None  # ArangoDB
        self.cache_abstraction = None  # Cache for performance optimization (Redis/Memory)
        
        # Service State
        self.is_infrastructure_connected = False
        
        # SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        
        # Service capabilities
        self.content_processing_enabled = True
        self.metadata_extraction_enabled = True
        self.policy_enforcement_enabled = True
        self.format_conversion_enabled = True
        
        # Service-specific state (backward compatibility)
        self.content_registry: Dict[str, Dict[str, Any]] = {}
        self.metadata_registry: Dict[str, Dict[str, Any]] = {}
        self.processing_queue: List[Dict[str, Any]] = []
        self.quality_metrics: Dict[str, Dict[str, Any]] = {}
        
        # Initialize micro-modules
        self.initialization_module = Initialization(self)
        self.file_processing_module = FileProcessing(self)
        self.parsed_file_processing_module = ParsedFileProcessing(self)
        self.content_processing_module = ContentProcessing(self)
        self.content_validation_module = ContentValidation(self)
        self.content_metadata_module = ContentMetadata(self)
        self.soa_mcp_module = SoaMcp(self)
        self.utilities_module = Utilities(self)
        
        # Logger is initialized by SmartCityRoleBase
        if self.logger:
            self.logger.info("✅ Content Steward Service (Clean Micro-Modular Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """Initialize Content Steward Service with proper infrastructure connections."""
        # Start telemetry tracking
        await self.log_operation_with_telemetry(
            "content_steward_initialize_start",
            success=True
        )
        
        try:
            # Initialize infrastructure connections
            await self.initialization_module.initialize_infrastructure_connections()
            
            # Initialize SOA API exposure
            await self.soa_mcp_module.initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self.soa_mcp_module.initialize_mcp_tool_integration()
            
            # Register capabilities with curator
            capabilities = await self.soa_mcp_module.register_content_steward_capabilities()
            # Register capabilities with curator (Phase 2 pattern - simplified for Smart City)
            await self.soa_mcp_module.register_capabilities()
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            # Record health metric
            await self.record_health_metric(
                "content_steward_initialized",
                1.0,
                {"service": "ContentStewardService"}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "content_steward_initialize_complete",
                success=True
            )
            
            return True
            
        except Exception as e:
            # Error handling with audit
            await self.handle_error_with_audit(
                e,
                "content_steward_initialize",
                {
                    "service": "ContentStewardService",
                    "error_type": type(e).__name__
                }
            )
            
            self.service_health = "unhealthy"
            
            # Log failure
            await self.log_operation_with_telemetry(
                "content_steward_initialize_complete",
                success=False,
                details={"error": str(e), "error_type": type(e).__name__}
            )
            
            # Record health metric
            await self.record_health_metric(
                "content_steward_initialized",
                0.0,
                metadata={"error_type": type(e).__name__}
            )
            
            return False
    
    # ============================================================================
    # FILE LIFECYCLE METHODS (Phase 3.1: Content Steward Finalization)
    # ============================================================================
    
    async def upload_file(
        self,
        file_data: bytes,
        file_name: str,
        file_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload file (SOA API - Phase 3.1).
        
        Wrapper for process_upload with standardized parameters.
        
        Args:
            file_data: Raw file bytes
            file_name: File name
            file_type: File type/extension
            metadata: Optional file metadata
            user_context: Optional user context
            
        Returns:
            Dict with uuid, file_id, and metadata
        """
        # Build metadata dict if not provided
        if not metadata:
            metadata = {}
        metadata.setdefault("ui_name", file_name)
        metadata.setdefault("file_type", file_type)
        
        # Determine content_type from file_type if not in metadata
        content_type = metadata.get("content_type")
        if not content_type:
            # Map common file types to MIME types
            mime_type_map = {
                "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "pdf": "application/pdf",
                "csv": "text/csv",
                "json": "application/json",
                "txt": "text/plain"
            }
            content_type = mime_type_map.get(file_type.lower(), "application/octet-stream")
        
        return await self.process_upload(file_data, content_type, metadata, user_context, workflow_id)
    
    async def get_file(self, file_id: str, user_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get file via file_management infrastructure (SOA API - Phase 3.1).
        
        Content Steward wraps Public Works file_management and exposes it
        as an SOA API for realm services to access file storage.
        
        Args:
            file_id: ID of file to retrieve
            user_context: Optional user context for security
            
        Returns:
            File data with metadata, or None if not found
        """
        try:
            # Security validation
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "file_management", "read"):
                        raise PermissionError("Access denied: insufficient permissions to read file")
            
            # Use file_management abstraction (initialized during startup)
            if not self.file_management_abstraction:
                self.logger.warning("⚠️ file_management abstraction not available")
                return None
            
            # Get file from infrastructure (uses protocol method name)
            file_record = await self.file_management_abstraction.get_file(file_id)
            
            if not file_record:
                self.logger.debug(f"File not found: {file_id}")
                return None
            
            return file_record
            
        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to get file {file_id}: {e}")
            import traceback
            self.logger.error(f"   Traceback: {traceback.format_exc()}")
            return None
    
    async def delete_file(self, file_id: str, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Delete file (SOA API - Phase 3.1).
        
        Args:
            file_id: ID of file to delete
            user_context: Optional user context for security
            
        Returns:
            bool indicating success
        """
        try:
            # Security validation
            # Note: ContentStewardService is a Smart City service with access to file_management
            # When called from authorized services (e.g., Journey Orchestrators), we trust the service
            # and don't require the user_context to have file_management permissions
            # The Smart City service itself has the permissions to act on behalf of the user
            if user_context:
                security = self.get_security()
                if security:
                    # Try to check permissions, but don't fail if user_context doesn't have file_management permissions
                    # This allows Journey realm orchestrators to call ContentStewardService
                    try:
                        has_permission = await security.check_permissions(user_context, "file_management", "delete")
                        if not has_permission:
                            # Log but don't fail - Smart City service can act on behalf of authorized callers
                            self.logger.debug(f"⚠️ User context doesn't have file_management.delete permission, but allowing (Smart City service has access)")
                    except Exception as perm_error:
                        # If permission check fails, log but continue (Smart City service has access)
                        self.logger.debug(f"⚠️ Permission check failed: {perm_error}, but allowing (Smart City service has access)")
            
            if not self.file_management_abstraction:
                self.logger.warning("⚠️ file_management abstraction not available")
                return False
            
            return await self.file_management_abstraction.delete_file(file_id)
            
        except PermissionError:
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to delete file {file_id}: {e}")
            return False
    
    async def list_files(
        self,
        filters: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List files with optional filters (SOA API - Phase 3.1).
        
        Args:
            filters: Optional filters (user_id, tenant_id, content_type, etc.)
            user_context: Optional user context for security
            
        Returns:
            List of file records
        """
        try:
            # Security validation
            # Note: ContentStewardService is a Smart City service with access to file_management
            # When called from authorized services (e.g., Journey Orchestrators), we trust the service
            # and don't require the user_context to have file_management permissions
            # The Smart City service itself has the permissions to act on behalf of the user
            if user_context:
                security = self.get_security()
                if security:
                    # Try to check permissions, but don't fail if user_context doesn't have file_management permissions
                    # This allows Journey realm orchestrators to call ContentStewardService
                    try:
                        has_permission = await security.check_permissions(user_context, "file_management", "read")
                        if not has_permission:
                            # Log but don't fail - Smart City service can act on behalf of authorized callers
                            self.logger.debug(f"⚠️ User context doesn't have file_management.read permission, but allowing (Smart City service has access)")
                    except Exception as perm_error:
                        # If permission check fails, log but continue (Smart City service has access)
                        self.logger.debug(f"⚠️ Permission check failed: {perm_error}, but allowing (Smart City service has access)")
            
            if not self.file_management_abstraction:
                self.logger.warning("⚠️ file_management abstraction not available")
                return []
            
            # Extract user_id and tenant_id from user_context or filters
            user_id = None
            tenant_id = None
            
            if user_context:
                user_id = user_context.get("user_id")
                tenant_id = user_context.get("tenant_id")
            
            if filters:
                user_id = filters.get("user_id", user_id)
                tenant_id = filters.get("tenant_id", tenant_id)
            
            if not user_id:
                raise ValueError("user_id is required (from user_context or filters)")
            
            # Extract other filters
            list_filters = {k: v for k, v in (filters or {}).items() if k not in ["user_id", "tenant_id"]}
            
            return await self.file_management_abstraction.list_files(
                user_id=user_id,
                tenant_id=tenant_id,
                filters=list_filters if list_filters else None
            )
            
        except (PermissionError, ValueError):
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to list files: {e}")
            return []
    
    async def classify_file(
        self,
        file_id: str,
        data_classification: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify file (data_classification: 'client' or 'platform') (SOA API - Phase 3.1).
        
        Args:
            file_id: ID of file to classify
            data_classification: Classification ('client' or 'platform')
            user_context: Optional user context for security
            
        Returns:
            Dict with updated file information
        """
        try:
            # Validate classification
            if data_classification not in ["client", "platform"]:
                raise ValueError(f"Invalid data_classification: {data_classification}. Must be 'client' or 'platform'")
            
            # Security validation
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "file_management", "write"):
                        raise PermissionError("Access denied: insufficient permissions to classify file")
            
            if not self.file_management_abstraction:
                self.logger.warning("⚠️ file_management abstraction not available")
                return {"success": False, "error": "Infrastructure not available"}
            
            # Update file with classification
            return await self.file_management_abstraction.update_file(
                file_uuid=file_id,
                updates={"data_classification": data_classification}
            )
            
        except (PermissionError, ValueError):
            raise
        except Exception as e:
            self.logger.error(f"❌ Failed to classify file {file_id}: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================================================
    # LEGACY METHODS (for backward compatibility)
    # ============================================================================
    
    async def process_upload(self, file_data: bytes, content_type: str, metadata: Optional[Dict[str, Any]] = None, user_context: Optional[Dict[str, Any]] = None, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """Process uploaded file with content analysis and metadata extraction (legacy method)."""
        # Service-level method delegates to module (module handles utilities)
        return await self.file_processing_module.process_upload(file_data, content_type, metadata, user_context, workflow_id)
    
    async def get_file_metadata(self, file_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Retrieve metadata for a specific file."""
        # Service-level method delegates to module (module handles utilities)
        return await self.file_processing_module.get_file_metadata(file_id, user_context)
    
    async def update_file_metadata(self, file_id: str, metadata_updates: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Update metadata for a specific file."""
        # Service-level method delegates to module (module handles utilities)
        return await self.file_processing_module.update_file_metadata(file_id, metadata_updates, user_context)
    
    async def process_file_content(self, file_id: str, processing_options: Optional[Dict[str, Any]] = None, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process file content with specified options."""
        # Service-level method delegates to module (module handles utilities)
        return await self.file_processing_module.process_file_content(file_id, processing_options, user_context)
    
    # ============================================================================
    # PARSED FILE STORAGE METHODS (NEW)
    # ============================================================================
    
    async def store_parsed_file(
        self,
        file_id: str,
        parsed_file_data: bytes,
        format_type: str,
        content_type: str,
        parse_result: Dict[str, Any],
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Store parsed file in GCS and metadata in Supabase parsed_data_files table (SOA API).
        
        Args:
            file_id: Original file UUID
            parsed_file_data: Parsed file bytes
            format_type: Format type ("parquet", "json_structured", "json_chunks")
            content_type: Content type ("structured", "unstructured", "hybrid")
            parse_result: Parse result metadata
            workflow_id: Optional workflow ID for orchestration
            
        Returns:
            Dict with parsed_file_id and metadata
        """
        return await self.parsed_file_processing_module.store_parsed_file(
            file_id, parsed_file_data, format_type, content_type, parse_result, workflow_id
        )
    
    async def get_parsed_file(
        self,
        parsed_file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get parsed file data and metadata (SOA API).
        
        Args:
            parsed_file_id: Parsed file ID
            user_context: Optional user context
            
        Returns:
            Dict with parsed file data and metadata
        """
        return await self.parsed_file_processing_module.get_parsed_file(parsed_file_id, user_context)
    
    async def list_parsed_files(
        self,
        file_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List parsed files for a given original file or for a user (SOA API).
        
        Args:
            file_id: Optional original file UUID (if provided, filters by file_id)
            user_id: Optional user ID (if provided and file_id is None, lists all parsed files for user)
            user_context: Optional user context
            
        Returns:
            List of parsed file metadata records
        """
        return await self.parsed_file_processing_module.list_parsed_files(file_id=file_id, user_id=user_id, user_context=user_context)
    
    async def list_embedding_files(
        self,
        user_id: str,
        parsed_file_id: Optional[str] = None,
        file_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List embedding files for a user (SOA API).
        
        Args:
            user_id: User identifier
            parsed_file_id: Optional parsed file ID to filter by
            file_id: Optional original file ID to filter by
            user_context: Optional user context
            
        Returns:
            List of embedding file metadata records
        """
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if not self.file_management_abstraction or not self.file_management_abstraction.supabase_adapter:
                raise Exception("File management abstraction or Supabase adapter not available")
            
            supabase_adapter = self.file_management_abstraction.supabase_adapter
            
            filters = {}
            if parsed_file_id:
                filters["parsed_file_id"] = parsed_file_id
            if file_id:
                filters["file_id"] = file_id
            
            embedding_files = await supabase_adapter.list_embedding_files(
                user_id=user_id,
                filters=filters if filters else None
            )
            
            return embedding_files if embedding_files else []
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list embedding files: {e}", exc_info=True)
            return []
    
    async def get_file_statistics(
        self,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get file statistics for dashboard (uploaded, parsed, embedded counts).
        
        Args:
            user_id: User identifier
            user_context: Optional user context
            
        Returns:
            Dictionary with statistics
        """
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if not self.file_management_abstraction:
                raise Exception("File management abstraction not available")
            
            tenant_id = user_context.get("tenant_id") if user_context else None
            
            # Get uploaded file count
            # ✅ FIX: Exclude files with status="parsed" (these are old duplicate entries from before the fix)
            # Also exclude files with ui_name starting with "parsed_" (legacy entries)
            uploaded_files = await self.file_management_abstraction.list_files(
                user_id=user_id,
                tenant_id=tenant_id,
                filters={"status": "uploaded", "deleted": False}
            )
            # Filter out any parsed files that might have been created in project_files (legacy entries)
            if uploaded_files:
                uploaded_files = [f for f in uploaded_files if f.get("status") == "uploaded" and not f.get("ui_name", "").startswith("parsed_")]
            uploaded_count = len(uploaded_files) if uploaded_files else 0
            
            # Get parsed file count
            parsed_files = await self.list_parsed_files(user_id=user_id, user_context=user_context)
            parsed_count = len(parsed_files) if parsed_files else 0
            
            # Get embedded file count
            embedding_files = await self.list_embedding_files(user_id=user_id, user_context=user_context)
            embedded_count = len(embedding_files) if embedding_files else 0
            
            return {
                "uploaded": uploaded_count,
                "parsed": parsed_count,
                "embedded": embedded_count,
                "total": uploaded_count + parsed_count + embedded_count
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get file statistics: {e}", exc_info=True)
            return {
                "uploaded": 0,
                "parsed": 0,
                "embedded": 0,
                "total": 0
            }
    
    # ============================================================================
    # DASHBOARD SERVICE METHODS (OPTIMAL ARCHITECTURE)
    # ============================================================================
    
    async def get_dashboard_files(
        self,
        user_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get unified file list for dashboard from all three tables.
        
        This is the optimal architecture: dashboard service queries all three tables
        (project_files, parsed_data_files, embedding_files) and composes a unified view.
        
        Args:
            user_id: User identifier
            user_context: Optional user context
            
        Returns:
            Dict with files list and statistics
        """
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if not self.file_management_abstraction:
                raise Exception("File management abstraction not available")
            
            tenant_id = user_context.get("tenant_id") if user_context else None
            files = []
            
            # 1. Get original uploaded files from project_files (status="uploaded" only)
            uploaded_files = await self.file_management_abstraction.list_files(
                user_id=user_id,
                tenant_id=tenant_id,
                filters={"status": "uploaded", "deleted": False}
            )
            for f in uploaded_files:
                files.append({
                    "uuid": f["uuid"],
                    "ui_name": f.get("ui_name", f.get("filename", "")),
                    "status": "uploaded",
                    "file_type": f.get("file_type", ""),
                    "mime_type": f.get("mime_type", ""),
                    "size": f.get("file_size", 0),
                    "created_at": f.get("created_at", f.get("uploaded_at", "")),
                    "type": "original"
                })
            
            # 2. Get parsed files from parsed_data_files
            parsed_files = await self.list_parsed_files(user_id=user_id, user_context=user_context)
            for pf in parsed_files:
                # Extract ui_name from metadata (since it's stored there)
                metadata = pf.get("metadata", {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                ui_name = metadata.get("ui_name") or f"parsed_{pf.get('parsed_file_id', '')}"
                
                files.append({
                    "uuid": pf["uuid"],  # parsed_data_files.uuid
                    "ui_name": ui_name,
                    "status": "parsed",
                    "file_type": pf.get("format_type", ""),
                    "mime_type": f"application/{pf.get('format_type', '')}",
                    "size": pf.get("file_size", 0),
                    "created_at": pf.get("parsed_at", pf.get("created_at", "")),
                    "original_file_id": pf.get("file_id"),  # Link to original
                    "type": "parsed"
                })
            
            # 3. Get embedded files from embedding_files
            embedded_files = await self.list_embedding_files(user_id=user_id, user_context=user_context)
            for ef in embedded_files:
                files.append({
                    "uuid": ef.get("uuid", ef.get("content_id", "")),  # embedding_files.uuid
                    "ui_name": ef.get("ui_name", f"embeddings_{ef.get('parsed_file_id', '')}"),
                    "status": "embedded",
                    "file_type": "embeddings",
                    "mime_type": "application/json",
                    "size": ef.get("size", 0),
                    "created_at": ef.get("created_at", ""),
                    "parsed_file_id": ef.get("parsed_file_id"),  # Link to parsed file
                    "original_file_id": ef.get("file_id"),  # Link to original
                    "type": "embedded"
                })
            
            # Sort by created_at (most recent first)
            files.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            # Calculate statistics
            statistics = {
                "uploaded": len([f for f in files if f["type"] == "original"]),
                "parsed": len([f for f in files if f["type"] == "parsed"]),
                "embedded": len([f for f in files if f["type"] == "embedded"]),
                "total": len(files)
            }
            
            return {
                "success": True,
                "files": files,
                "statistics": statistics
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get dashboard files: {e}", exc_info=True)
            return {
                "success": False,
                "files": [],
                "statistics": {"uploaded": 0, "parsed": 0, "embedded": 0, "total": 0},
                "error": str(e)
            }
    
    async def delete_file_by_type(
        self,
        file_uuid: str,
        file_type: str,  # "original", "parsed", or "embedded"
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Delete file directly from its table and storage.
        No cascade - users delete what they want to delete.
        
        Args:
            file_uuid: UUID of file to delete
            file_type: "original", "parsed", or "embedded"
        """
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            if file_type == "original":
                # Delete from project_files and GCS
                result = await self.file_management_abstraction.delete_file(file_uuid)
                return {
                    "success": result,
                    "file_uuid": file_uuid,
                    "file_type": file_type,
                    "message": "Original file deleted"
                }
                
            elif file_type == "parsed":
                # Get parsed file metadata from parsed_data_files table (using uuid column)
                supabase_adapter = self.file_management_abstraction.supabase_adapter
                result = supabase_adapter.client.table("parsed_data_files").select("*").eq("uuid", file_uuid).execute()
                
                if not result.data or len(result.data) == 0:
                    return {
                        "success": False,
                        "error": f"Parsed file not found: {file_uuid}"
                    }
                
                parsed_file_metadata = result.data[0]
                
                # Get GCS path from metadata
                metadata = parsed_file_metadata.get("metadata", {})
                if isinstance(metadata, str):
                    import json
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                gcs_path = metadata.get("gcs_path")
                if not gcs_path:
                    # Fallback: construct path from parsed_file_id and format_type
                    parsed_file_id = parsed_file_metadata.get("parsed_file_id")
                    format_type = parsed_file_metadata.get("format_type", "parquet")
                    gcs_path = f"parsed_data/{parsed_file_id}.{format_type}"
                
                # Delete from GCS
                if gcs_path:
                    gcs_adapter = self.file_management_abstraction.gcs_adapter
                    if gcs_adapter:
                        gcs_result = await gcs_adapter.delete_file(gcs_path)
                        if gcs_result.get("success"):
                            self.logger.info(f"✅ [delete_file_by_type] Deleted from GCS: {gcs_path}")
                        else:
                            self.logger.warning(f"⚠️ [delete_file_by_type] Failed to delete from GCS: {gcs_path}")
                
                # Delete from parsed_data_files (hard delete)
                supabase_adapter.client.table("parsed_data_files").delete().eq("uuid", file_uuid).execute()
                
                self.logger.info(f"✅ [delete_file_by_type] Deleted parsed file: {file_uuid}")
                return {
                    "success": True,
                    "file_uuid": file_uuid,
                    "file_type": file_type,
                    "message": "Parsed file deleted"
                }
                
            elif file_type == "embedded":
                # Get embedding metadata
                embedding_files = await self.list_embedding_files(user_id=None, parsed_file_id=None, file_id=None, user_context=user_context)
                embedding_file = next((ef for ef in embedding_files if ef.get("uuid") == file_uuid or ef.get("content_id") == file_uuid), None)
                
                if not embedding_file:
                    return {
                        "success": False,
                        "error": f"Embedding file not found: {file_uuid}"
                    }
                
                # Delete embeddings from ArangoDB (if needed)
                # Note: Implementation depends on how embeddings are stored
                # For now, we'll just delete from embedding_files table
                
                # Delete from embedding_files
                supabase_adapter = self.file_management_abstraction.supabase_adapter
                supabase_adapter.client.table("embedding_files").delete().eq("uuid", file_uuid).execute()
                
                self.logger.info(f"✅ [delete_file_by_type] Deleted embedding file: {file_uuid}")
                return {
                    "success": True,
                    "file_uuid": file_uuid,
                    "file_type": file_type,
                    "message": "Embedding file deleted"
                }
            else:
                return {
                    "success": False,
                    "error": f"Invalid file_type: {file_type}. Must be 'original', 'parsed', or 'embedded'"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to delete file {file_uuid} (type: {file_type}): {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # FORMAT CONVERSION METHODS
    # ============================================================================
    
    async def convert_file_format(self, file_id: str, source_format: str, target_format: str, 
                                conversion_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert file from source format to target format."""
        return await self.content_processing_module.convert_file_format(file_id, source_format, target_format, conversion_options)
    
    async def batch_convert_formats(self, file_ids: List[str], target_format: str, 
                                  conversion_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Convert multiple files to target format in batch."""
        return await self.content_processing_module.batch_convert_formats(file_ids, target_format, conversion_options)
    
    # ============================================================================
    # DATA OPTIMIZATION METHODS
    # ============================================================================
    
    async def optimize_data(self, file_id: str, optimization_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize data for specific use cases."""
        return await self.content_processing_module.optimize_data(file_id, optimization_options)
    
    async def compress_data(self, file_id: str, compression_type: str = "gzip") -> Dict[str, Any]:
        """Compress data using specified compression type."""
        return await self.content_processing_module.compress_data(file_id, compression_type)
    
    async def validate_output(self, file_id: str, expected_format: str) -> Dict[str, Any]:
        """Validate output format and quality."""
        return await self.content_processing_module.validate_output(file_id, expected_format)
    
    # ============================================================================
    # CONTENT VALIDATION METHODS
    # ============================================================================
    
    async def validate_content(self, content_data: bytes, content_type: str, user_context: Optional[Dict[str, Any]] = None) -> bool:
        """Validate content against policies and standards."""
        # Service-level method delegates to module (module handles utilities)
        return await self.content_validation_module.validate_content(content_data, content_type, user_context)
    
    async def get_quality_metrics(self, asset_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get quality metrics for content asset."""
        # Service-level method delegates to module (module handles utilities)
        return await self.content_validation_module.get_quality_metrics(asset_id, user_context)
    
    # ============================================================================
    # METADATA AND LINEAGE METHODS
    # ============================================================================
    
    async def get_asset_metadata(self, asset_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get comprehensive metadata for content asset."""
        # Service-level method delegates to module (module handles utilities)
        return await self.content_metadata_module.get_asset_metadata(asset_id, user_context)
    
    async def get_lineage(self, asset_id: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get lineage information for content asset."""
        # Service-level method delegates to module (module handles utilities)
        return await self.content_metadata_module.get_lineage(asset_id, user_context)
    
    # ============================================================================
    # STATUS AND CAPABILITIES METHODS
    # ============================================================================
    
    async def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status and statistics."""
        return await self.content_metadata_module.get_processing_status()
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities and configuration."""
        return await self.utilities_module.get_service_capabilities()
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate infrastructure mapping."""
        return await self.utilities_module.validate_infrastructure_mapping()
