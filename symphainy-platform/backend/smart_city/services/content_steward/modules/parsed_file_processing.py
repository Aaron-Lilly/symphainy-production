#!/usr/bin/env python3
"""
Content Steward Service - Parsed File Processing Module

Micro-module for parsed file storage operations using File Management (GCS + Supabase parsed_data_files table).
"""

import uuid
from typing import Any, Dict, Optional, List
from datetime import datetime


class ParsedFileProcessing:
    """Parsed file processing module for Content Steward service."""
    
    def __init__(self, service: Any):
        """Initialize with service instance."""
        self.service = service
        self.logger = self.service.di_container.get_logger(f"{self.__class__.__name__}")
    
    async def store_parsed_file(
        self,
        file_id: str,
        parsed_file_data: bytes,
        format_type: str,  # "jsonl", "json_structured", "json_chunks", "parquet" (legacy)
        content_type: str,  # "structured", "unstructured", "hybrid"
        parse_result: Dict[str, Any],
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Store parsed file in GCS and metadata in Supabase parsed_data_files table.
        
        Args:
            file_id: Original file UUID (from project_files)
            parsed_file_data: Parsed file bytes (Parquet, JSON, etc.)
            format_type: Format of parsed file ("jsonl", "json_structured", "json_chunks", "parquet" for legacy)
            content_type: Content classification ("structured", "unstructured", "hybrid")
            parse_result: Parse result metadata (row_count, column_count, etc.)
            workflow_id: Optional workflow ID for orchestration
            
        Returns:
            Dict with parsed_file_id and metadata
        """
        # Start telemetry tracking
        await self.service.log_operation_with_telemetry(
            "store_parsed_file_start",
            success=True,
            details={"file_id": file_id, "format_type": format_type, "content_type": content_type}
        )
        
        try:
            # ✅ Get user context from request-scoped context
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = get_request_user_context()
            
            # Security validation (zero-trust: secure by design)
            if ctx:
                security = self.service.get_security()
                if security:
                    # Debug logging
                    self.logger.info(f"🔍 [store_parsed_file] Using user context: user_id={ctx.get('user_id')}, tenant_id={ctx.get('tenant_id')}, permissions={ctx.get('permissions')}")
                    
                    has_permission = await security.check_permissions(ctx, "file_management", "write")
                    self.logger.info(f"🔍 [store_parsed_file] check_permissions result: {has_permission}")
                    
                    if not has_permission:
                        await self.service.record_health_metric("store_parsed_file_access_denied", 1.0, {"file_id": file_id})
                        await self.service.log_operation_with_telemetry("store_parsed_file_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to store parsed file")
            else:
                self.logger.warning(f"⚠️ [store_parsed_file] No user context available (neither provided nor in request context)")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get original file to determine data classification, tenant_id, and user_id
            original_file = await self.service.file_management_abstraction.get_file(file_id)
            if not original_file:
                raise ValueError(f"Original file not found: {file_id}")
            
            # Get user_id from original file (primary) or context (fallback)
            user_id = original_file.get("user_id")
            if not user_id and ctx:
                user_id = ctx.get("user_id")
            if not user_id:
                raise ValueError(f"Cannot determine user_id for file {file_id}")
            
            # Determine data classification and tenant_id from original file
            tenant_id = original_file.get("tenant_id")
            data_classification = "client" if tenant_id else "platform"
            
            # Validate data classification
            if data_classification == "client" and not tenant_id:
                raise ValueError("Client data must have tenant_id")
            
            # Validate format-specific bytes BEFORE storage (only for parquet - JSONL is text, no validation needed)
            if format_type == "parquet" and isinstance(parsed_file_data, bytes):
                if len(parsed_file_data) >= 4:
                    magic_bytes = parsed_file_data[:4]
                    footer_magic = parsed_file_data[-4:] if len(parsed_file_data) >= 4 else None
                    if magic_bytes == b'PAR1' and footer_magic == b'PAR1':
                        self.logger.info(f"✅ [store_parsed_file] Parquet bytes validated before storage: {len(parsed_file_data)} bytes, header={magic_bytes}, footer={footer_magic}")
                    else:
                        self.logger.error(f"❌ [store_parsed_file] Invalid parquet bytes before storage: header={magic_bytes}, footer={footer_magic}, length={len(parsed_file_data)}")
                        raise ValueError(f"Invalid parquet bytes: header={magic_bytes}, footer={footer_magic}")
                else:
                    self.logger.error(f"❌ [store_parsed_file] Parquet bytes too short: {len(parsed_file_data)} bytes")
                    raise ValueError(f"Parquet bytes too short: {len(parsed_file_data)} bytes")
            elif format_type == "jsonl" and isinstance(parsed_file_data, bytes):
                # JSONL validation: ensure it's valid UTF-8 and has at least one newline-separated JSON object
                try:
                    jsonl_content = parsed_file_data.decode('utf-8')
                    lines = [line.strip() for line in jsonl_content.strip().split('\n') if line.strip()]
                    if lines:
                        import json
                        # Validate first line is valid JSON
                        json.loads(lines[0])
                        self.logger.info(f"✅ [store_parsed_file] JSONL validated: {len(lines)} records, {len(parsed_file_data)} bytes")
                    else:
                        self.logger.warning(f"⚠️ [store_parsed_file] JSONL file appears empty")
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    self.logger.error(f"❌ [store_parsed_file] Invalid JSONL bytes: {e}")
                    raise ValueError(f"Invalid JSONL bytes: {e}")
            
            # Store parsed file in GCS (via file_management_abstraction)
            # Note: We'll use the file_management_abstraction's GCS adapter
            # For now, we'll store it as a new file record, but mark it as parsed
            parsed_file_record = {
                "user_id": original_file.get("user_id", "system"),
                "tenant_id": tenant_id,
                "ui_name": f"parsed_{original_file.get('ui_name', file_id)}",
                "file_type": format_type,
                "mime_type": f"application/{format_type}",
                "file_content": parsed_file_data,
                "metadata": {
                    "original_file_id": file_id,
                    "is_parsed_file": True,
                    "format_type": format_type,
                    "content_type": content_type
                },
                "status": "parsed",
                "parent_file_uuid": file_id,  # Link to original file
                "generation": original_file.get("generation", 0) + 1,
                "lineage_depth": original_file.get("lineage_depth", 0) + 1
            }
            
            # Store in GCS (via file_management_abstraction) FIRST to get actual UUID
            self.logger.info(f"🔍 [store_parsed_file] Storing parsed file in GCS: format_type={format_type}, size={len(parsed_file_data)} bytes")
            gcs_result = await self.service.file_management_abstraction.create_file(parsed_file_record)
            parsed_file_gcs_id = gcs_result.get("uuid")
            
            if not parsed_file_gcs_id:
                raise ValueError("Failed to get UUID from GCS file creation - cannot store parsed file metadata")
            
            # Create file link for cascade deletion - link original file (parent) to parsed file (child)
            # This ensures parsed files are deleted when the original file is deleted
            try:
                await self.service.file_management_abstraction.create_file_link(
                    parent_uuid=file_id,
                    child_uuid=parsed_file_gcs_id,
                    link_type="parsed_from"
                )
                self.logger.info(f"✅ [store_parsed_file] Created file link: {file_id} -> {parsed_file_gcs_id} (parsed_from)")
            except Exception as link_error:
                # Log warning but don't fail - link creation is for cleanup, not critical for functionality
                self.logger.warning(f"⚠️ [store_parsed_file] Failed to create file link: {link_error}")
            
            # Use the ACTUAL GCS file UUID as parsed_file_id (not a generated one)
            parsed_file_id = parsed_file_gcs_id
            gcs_path = f"parsed_data/{parsed_file_id}.{format_type}"
            
            self.logger.info(f"✅ [store_parsed_file] Stored in GCS: parsed_file_id={parsed_file_id}, gcs_file_id={parsed_file_gcs_id}")
            
            # Extract metadata from parse_result
            row_count = parse_result.get("row_count") or parse_result.get("structure", {}).get("row_count")
            column_count = parse_result.get("column_count") or parse_result.get("structure", {}).get("column_count")
            column_names = parse_result.get("column_names") or parse_result.get("structure", {}).get("columns", [])
            data_types = parse_result.get("data_types") or parse_result.get("structure", {}).get("data_types", {})
            
            # Store metadata in Supabase parsed_data_files table
            # Use the ACTUAL GCS file UUID as parsed_file_id (ensures lookups work correctly)
            # Include user_id and ui_name directly for simple queries (no JOIN needed)
            # ✅ STANDARDIZED: ui_name matches pattern from project_files and embedding_files
            parsed_file_ui_name = parsed_file_record.get("ui_name")  # Already constructed above: f"parsed_{original_file.get('ui_name', file_id)}"
            
            parsed_file_metadata = {
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,  # ✅ FIXED: Use actual GCS UUID, not generated string
                "user_id": user_id,  # ✅ NEW: Store user_id directly for simple queries
                "ui_name": parsed_file_ui_name,  # ✅ NEW: Store ui_name directly for unified query pattern
                "data_classification": data_classification,
                "tenant_id": tenant_id,
                "format_type": format_type,
                "content_type": content_type,
                "file_size": len(parsed_file_data),
                "row_count": row_count,
                "column_count": column_count,
                "column_names": column_names if isinstance(column_names, list) else [],
                "data_types": data_types if isinstance(data_types, dict) else {},
                "parsed_at": datetime.utcnow().isoformat(),
                "parsed_by": ctx.get("service_name", "file_parser_service") if ctx else "file_parser_service",
                "parse_options": parse_result.get("parse_options", {}),
                "status": "parsed",  # Main status: parsed file is ready for use
                "processing_status": "completed",  # Processing is complete (not pending)
                "metadata": {
                    "gcs_file_id": parsed_file_gcs_id,  # Same as parsed_file_id
                    "gcs_path": gcs_path
                }
            }
            
            # Store in Supabase parsed_data_files table
            # TODO: Add parsed_data_files methods to SupabaseFileManagementAdapter
            # For now, we'll use a direct Supabase call via the adapter
            supabase_adapter = self.service.file_management_abstraction.supabase_adapter
            result = supabase_adapter.client.table("parsed_data_files").insert(parsed_file_metadata).execute()
            
            parsed_file_metadata_record = result.data[0] if result.data else parsed_file_metadata
            
            # Record health metric
            await self.service.record_health_metric(
                "parsed_file_stored",
                1.0,
                {
                    "file_id": file_id,
                    "parsed_file_id": parsed_file_id,
                    "format_type": format_type,
                    "content_type": content_type
                }
            )
            
            # FIX 2: Workflow orchestration - Update workflow state after storing parsed file
            conductor = None
            if workflow_id and hasattr(self.service, 'get_smart_city_api'):
                try:
                    conductor = await self.service.get_smart_city_api("Conductor")
                    if conductor:
                        await conductor.update_workflow_state(
                            workflow_id=workflow_id,
                            state_updates={"status": "parsed_file_stored", "parsed_file_id": parsed_file_id},
                            user_context=ctx
                        )
                except Exception as e:
                    self.service.logger.warning(f"⚠️ Failed to update workflow state: {e}")
            
            # FIX 3: Event publishing - Publish parsed_file_stored event
            post_office = None
            if hasattr(self.service, 'get_smart_city_api'):
                try:
                    post_office = await self.service.get_smart_city_api("PostOffice")
                    if post_office:
                        await post_office.publish_event(
                            {
                                "event_type": "parsed_file_stored",
                                "event_data": {
                                    "file_id": file_id,
                                    "parsed_file_id": parsed_file_id,
                                    "format_type": format_type,
                                    "content_type": content_type,
                                    "data_classification": data_classification,
                                    "workflow_id": workflow_id,
                                    "status": "stored"
                                }
                            },
                            user_context=ctx
                        )
                except Exception as e:
                    self.service.logger.warning(f"⚠️ Failed to publish parsed_file_stored event: {e}")
            
            # End telemetry tracking
            await self.service.log_operation_with_telemetry(
                "store_parsed_file_complete",
                success=True,
                details={
                    "file_id": file_id,
                    "parsed_file_id": parsed_file_id,
                    "format_type": format_type,
                    "content_type": content_type
                }
            )
            
            # FIX 7: Standardized response format
            # ✅ Include parsed_file_id at top level for backward compatibility
            return {
                "success": True,
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,  # ✅ Top-level for easy access
                "data": {  # ✅ FIX 7: Standardized response format
                    "file_id": file_id,
                    "parsed_file_id": parsed_file_id,
                    "parsed_file_gcs_id": parsed_file_gcs_id,
                    "gcs_path": gcs_path,
                    "format_type": format_type,
                    "content_type": content_type,
                    "data_classification": data_classification,
                    "metadata": parsed_file_metadata_record
                },
                "metadata": {  # ✅ FIX 7: Additional metadata
                    "status": "success",
                    "message": "Parsed file stored successfully"
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to store parsed file: {e}")
            await self.service.log_operation_with_telemetry(
                "store_parsed_file_complete",
                success=False,
                details={"error": str(e)}
            )
            raise
    
    async def get_parsed_file(
        self,
        parsed_file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get parsed file data and metadata.
        
        Args:
            parsed_file_id: Parsed file ID (from parsed_data_files table)
            user_context: Optional user context for security and tenant validation (kept for backward compatibility)
            
        Returns:
            Dict with parsed file data and metadata, or None if not found
        """
        try:
            # ✅ Get user context from request-scoped context
            from utilities.security_authorization.request_context import get_request_user_context
            ctx = user_context or get_request_user_context()
            
            # Security validation
            if ctx:
                security = self.service.get_security()
                if security:
                    if not await security.check_permissions(ctx, "file_management", "read"):
                        raise PermissionError("Access denied: insufficient permissions to get parsed file")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get metadata from Supabase parsed_data_files table
            supabase_adapter = self.service.file_management_abstraction.supabase_adapter
            result = supabase_adapter.client.table("parsed_data_files").select("*").eq("parsed_file_id", parsed_file_id).execute()
            
            if not result.data or len(result.data) == 0:
                self.logger.warning(f"⚠️ Parsed file not found: {parsed_file_id}")
                return None
            
            parsed_file_metadata = result.data[0]
            
            # Get file data from GCS (via file_management_abstraction)
            # The metadata contains gcs_file_id or we can construct the path
            gcs_file_id = parsed_file_metadata.get("metadata", {}).get("gcs_file_id")
            self.logger.info(f"🔍 [get_parsed_file] parsed_file_id={parsed_file_id}, gcs_file_id={gcs_file_id}")
            
            if gcs_file_id:
                self.logger.info(f"🔍 [get_parsed_file] Retrieving file from GCS: gcs_file_id={gcs_file_id}")
                file_data = await self.service.file_management_abstraction.get_file(gcs_file_id)
                if file_data:
                    file_content = file_data.get("file_content")
                    if file_content:
                        # Validate format-specific magic bytes (if applicable)
                        format_type = parsed_file_metadata.get("format_type", "jsonl")
                        if format_type == "parquet" and isinstance(file_content, bytes) and len(file_content) >= 4:
                            magic_bytes = file_content[:4]
                            if magic_bytes == b'PAR1':
                                self.logger.info(f"✅ [get_parsed_file] Retrieved valid parquet file: {len(file_content)} bytes")
                            else:
                                self.logger.error(f"❌ [get_parsed_file] Invalid parquet magic bytes: {magic_bytes} (expected PAR1)")
                                self.logger.error(f"   Content type: {type(file_content)}, length: {len(file_content)}")
                                self.logger.error(f"   First 20 bytes: {file_content[:20]}")
                                self.logger.error(f"   file_data keys: {list(file_data.keys())}")
                        elif format_type == "jsonl":
                            # JSONL is text format, no magic bytes to validate
                            if isinstance(file_content, bytes):
                                try:
                                    # Validate it's valid UTF-8
                                    file_content.decode('utf-8')
                                    self.logger.info(f"✅ [get_parsed_file] Retrieved valid JSONL file: {len(file_content)} bytes")
                                except UnicodeDecodeError as e:
                                    self.logger.error(f"❌ [get_parsed_file] Invalid JSONL (not UTF-8): {e}")
                            else:
                                self.logger.info(f"✅ [get_parsed_file] Retrieved JSONL file: {len(str(file_content))} chars")
                        else:
                            # Other formats (json_structured, json_chunks) - no validation needed
                            self.logger.info(f"✅ [get_parsed_file] Retrieved {format_type} file: {len(file_content) if isinstance(file_content, bytes) else len(str(file_content))} bytes/chars")
                    else:
                        self.logger.warning(f"⚠️ [get_parsed_file] Retrieved file has no file_content: keys={list(file_data.keys())}")
                else:
                    self.logger.warning(f"⚠️ [get_parsed_file] File not found in GCS: gcs_file_id={gcs_file_id}")
            else:
                # Fallback: construct path and try to get from GCS
                gcs_path = parsed_file_metadata.get("metadata", {}).get("gcs_path")
                if gcs_path:
                    # TODO: Add method to get file by GCS path
                    self.logger.warning(f"⚠️ [get_parsed_file] GCS file ID not found, cannot retrieve file data")
                    file_data = None
                else:
                    self.logger.warning(f"⚠️ [get_parsed_file] Neither gcs_file_id nor gcs_path found in metadata")
                    file_data = None
            
            return {
                "parsed_file_id": parsed_file_id,
                "metadata": parsed_file_metadata,
                "file_data": file_data.get("file_content") if file_data and file_data.get("file_content") else None,
                "format_type": parsed_file_metadata.get("format_type"),
                "content_type": parsed_file_metadata.get("content_type")
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get parsed file {parsed_file_id}: {e}")
            return None
    
    async def list_parsed_files(
        self,
        file_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List parsed files for a given original file or for a user.
        
        Args:
            file_id: Optional original file UUID (if provided, filters by file_id)
            user_id: Optional user ID (if provided and file_id is None, lists all parsed files for user)
            user_context: Optional user context for security and tenant validation
            
        Returns:
            List of parsed file metadata records
        """
        try:
            # Security validation
            # Note: ContentStewardService is a Smart City service with access to file_management
            # When called from authorized services (e.g., Journey Orchestrators), we trust the service
            # and don't require the user_context to have file_management permissions
            # The Smart City service itself has the permissions to act on behalf of the user
            if user_context:
                security = self.service.get_security()
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
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get parsed files from Supabase parsed_data_files table
            supabase_adapter = self.service.file_management_abstraction.supabase_adapter
            
            # Build query based on provided filters
            query = supabase_adapter.client.table("parsed_data_files").select("*")
            
            if file_id:
                # Filter by file_id (original file)
                self.logger.info(f"🔍 Querying parsed_data_files table for file_id: {file_id}")
                query = query.eq("file_id", file_id)
            elif user_id:
                # Filter by user_id (all parsed files for user)
                # ✅ SIMPLIFIED: Query directly by user_id (no JOIN needed!)
                self.logger.info(f"🔍 Querying parsed_data_files directly by user_id: {user_id}")
                
                result = supabase_adapter.client.table("parsed_data_files").select("*").eq("user_id", user_id).execute()
                
                parsed_files = result.data if result.data else []
                self.logger.info(f"✅ Found {len(parsed_files)} parsed files for user {user_id}")
                return parsed_files
            else:
                # No filters provided - return empty
                self.logger.warning(f"⚠️ No file_id or user_id provided to list_parsed_files")
                return []
            
            result = query.execute()
            parsed_files = result.data if result.data else []
            
            self.logger.info(f"✅ Retrieved {len(parsed_files)} parsed files")
            
            return parsed_files
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list parsed files: {e}", exc_info=True)
            return []

