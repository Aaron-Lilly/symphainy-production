#!/usr/bin/env python3
"""
Data Steward Service - Parsed File Processing Module

Micro-module for parsed file storage operations using File Management (GCS + Supabase parsed_data_files table).
Consolidated from Content Steward as part of Phase 0.1.

WHAT: I manage parsed file storage and retrieval
HOW: I use File Management Abstraction (GCS + Supabase) for parsed file operations
"""

import uuid
from typing import Any, Dict, Optional, List
from datetime import datetime


class ParsedFileProcessing:
    """Parsed file processing module for Data Steward service."""
    
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
                    has_permission = await security.check_permissions(ctx, "file_management", "write")
                    if not has_permission:
                        await self.service.record_health_metric("store_parsed_file_access_denied", 1.0, {"file_id": file_id})
                        await self.service.log_operation_with_telemetry("store_parsed_file_complete", success=False)
                        raise PermissionError("Access denied: insufficient permissions to store parsed file")
            
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
            
            # Validate format-specific bytes BEFORE storage
            if format_type == "parquet" and isinstance(parsed_file_data, bytes):
                if len(parsed_file_data) >= 4:
                    magic_bytes = parsed_file_data[:4]
                    footer_magic = parsed_file_data[-4:] if len(parsed_file_data) >= 4 else None
                    if magic_bytes != b'PAR1' or footer_magic != b'PAR1':
                        raise ValueError(f"Invalid parquet bytes: header={magic_bytes}, footer={footer_magic}")
                else:
                    raise ValueError(f"Parquet bytes too short: {len(parsed_file_data)} bytes")
            elif format_type == "jsonl" and isinstance(parsed_file_data, bytes):
                # JSONL validation: ensure it's valid UTF-8 and has at least one newline-separated JSON object
                try:
                    jsonl_content = parsed_file_data.decode('utf-8')
                    lines = [line.strip() for line in jsonl_content.strip().split('\n') if line.strip()]
                    if lines:
                        import json
                        json.loads(lines[0])  # Validate first line is valid JSON
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    raise ValueError(f"Invalid JSONL bytes: {e}")
            
            # Generate UUID for parsed file
            parsed_file_gcs_id = str(uuid.uuid4())
            gcs_path = f"parsed_data/{parsed_file_gcs_id}.{format_type}"
            
            # Determine content type for GCS
            content_type_map = {
                "parquet": "application/parquet",
                "jsonl": "application/x-ndjson",
                "json_structured": "application/json",
                "json_chunks": "application/json"
            }
            gcs_content_type = content_type_map.get(format_type, "application/octet-stream")
            
            # Store parsed file binary in GCS
            gcs_adapter = self.service.file_management_abstraction.gcs_adapter
            if not gcs_adapter:
                raise ValueError("GCS adapter not available - cannot store parsed file")
            
            gcs_success = await gcs_adapter.upload_file(
                blob_name=gcs_path,
                file_data=parsed_file_data,
                content_type=gcs_content_type,
                metadata={
                    "original_file_id": file_id,
                    "user_id": user_id,
                    "format_type": format_type,
                    "content_type": content_type,
                    "is_parsed_file": "true"
                }
            )
            
            if not gcs_success:
                raise ValueError(f"Failed to upload parsed file to GCS: {gcs_path}")
            
            # Use the GCS file UUID as parsed_file_id
            parsed_file_id = parsed_file_gcs_id
            
            # Extract metadata from parse_result
            row_count = parse_result.get("row_count") or parse_result.get("structure", {}).get("row_count")
            column_count = parse_result.get("column_count") or parse_result.get("structure", {}).get("column_count")
            column_names = parse_result.get("column_names") or parse_result.get("structure", {}).get("columns", [])
            data_types = parse_result.get("data_types") or parse_result.get("structure", {}).get("data_types", {})
            
            # Store metadata in Supabase parsed_data_files table
            original_ui_name = original_file.get("ui_name", file_id)
            parsed_file_ui_name = f"parsed_{original_ui_name}"
            
            parsed_file_metadata = {
                "file_id": file_id,  # Link back to original uploaded file
                "parsed_file_id": parsed_file_id,  # GCS UUID for retrieving the binary
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
                "status": "parsed",
                "processing_status": "completed",
                "metadata": {
                    "gcs_file_id": parsed_file_gcs_id,
                    "gcs_path": gcs_path,
                    "user_id": user_id,
                    "ui_name": parsed_file_ui_name
                }
            }
            
            # Store in Supabase parsed_data_files table
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
            
            return {
                "success": True,
                "file_id": file_id,
                "parsed_file_id": parsed_file_id,
                "data": {
                    "file_id": file_id,
                    "parsed_file_id": parsed_file_id,
                    "parsed_file_gcs_id": parsed_file_gcs_id,
                    "gcs_path": gcs_path,
                    "format_type": format_type,
                    "content_type": content_type,
                    "data_classification": data_classification,
                    "metadata": parsed_file_metadata_record
                },
                "metadata": {
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
            user_context: Optional user context for security and tenant validation
            
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
            
            # Tenant validation (multi-tenant support)
            tenant_id = None
            if ctx:
                tenant = self.service.get_tenant()
                if tenant:
                    tenant_id = ctx.get("tenant_id")
                    if tenant_id:
                        # Validate tenant access
                        try:
                            import inspect
                            if inspect.iscoroutinefunction(tenant.validate_tenant_access):
                                is_valid = await tenant.validate_tenant_access(tenant_id, tenant_id)
                            else:
                                is_valid = tenant.validate_tenant_access(tenant_id, tenant_id)
                            
                            if not is_valid:
                                raise PermissionError(f"Tenant access denied: {tenant_id}")
                        except PermissionError:
                            raise
                        except Exception as e:
                            self.logger.warning(f"⚠️ Tenant validation failed: {e}")
                            # Continue with query - RLS will enforce isolation if configured
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get metadata from Supabase parsed_data_files table
            supabase_adapter = self.service.file_management_abstraction.supabase_adapter
            
            # Build query with tenant filter if available
            # Note: Supabase RLS should also enforce tenant isolation at database level
            query = supabase_adapter.client.table("parsed_data_files").select("*")
            
            # Try querying by uuid first (what dashboard returns)
            query = query.eq("uuid", parsed_file_id)
            
            # Add tenant filter if available (defense in depth - RLS also enforces)
            if tenant_id:
                query = query.eq("tenant_id", tenant_id)
            
            result = query.execute()
            
            # If not found by uuid, try by parsed_file_id (GCS identifier)
            if not result.data or len(result.data) == 0:
                query = supabase_adapter.client.table("parsed_data_files").select("*").eq("parsed_file_id", parsed_file_id)
                if tenant_id:
                    query = query.eq("tenant_id", tenant_id)
                result = query.execute()
            
            if not result.data or len(result.data) == 0:
                self.logger.warning(f"⚠️ Parsed file not found: {parsed_file_id}")
                return None
            
            parsed_file_metadata = result.data[0]
            
            # Additional tenant validation after retrieval (defense in depth)
            if tenant_id and parsed_file_metadata.get("tenant_id"):
                if parsed_file_metadata.get("tenant_id") != tenant_id:
                    self.logger.warning(f"⚠️ Tenant isolation violation: User tenant {tenant_id} tried to access file from tenant {parsed_file_metadata.get('tenant_id')}")
                    raise PermissionError("Tenant isolation violation: Cannot access parsed file from different tenant")
            
            # Get file data directly from GCS
            gcs_path = parsed_file_metadata.get("metadata", {}).get("gcs_path")
            if not gcs_path:
                format_type = parsed_file_metadata.get("format_type", "parquet")
                gcs_path = f"parsed_data/{parsed_file_id}.{format_type}"
            
            gcs_adapter = self.service.file_management_abstraction.gcs_adapter
            if not gcs_adapter:
                raise ValueError("GCS adapter not available - cannot retrieve parsed file")
            
            file_content = await gcs_adapter.download_file(gcs_path)
            
            return {
                "parsed_file_id": parsed_file_id,
                "metadata": parsed_file_metadata,
                "file_data": file_content,
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
            if user_context:
                security = self.service.get_security()
                if security:
                    try:
                        has_permission = await security.check_permissions(user_context, "file_management", "read")
                        if not has_permission:
                            self.logger.debug(f"⚠️ User context doesn't have file_management.read permission, but allowing (Smart City service has access)")
                    except Exception as perm_error:
                        self.logger.debug(f"⚠️ Permission check failed: {perm_error}, but allowing (Smart City service has access)")
            
            if not self.service.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Get parsed files from Supabase parsed_data_files table
            supabase_adapter = self.service.file_management_abstraction.supabase_adapter
            
            # Build query based on provided filters
            query = supabase_adapter.client.table("parsed_data_files").select("*")
            
            if file_id:
                query = query.eq("file_id", file_id)
            elif user_id:
                # Query all parsed files and filter by metadata->user_id (since user_id is in metadata JSONB)
                result = supabase_adapter.client.table("parsed_data_files").select("*").execute()
                parsed_files = []
                if result.data:
                    for pf in result.data:
                        metadata = pf.get("metadata", {})
                        if isinstance(metadata, str):
                            import json
                            try:
                                metadata = json.loads(metadata)
                            except:
                                metadata = {}
                        if metadata.get("user_id") == user_id:
                            parsed_files.append(pf)
                return parsed_files
            else:
                return []
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list parsed files: {e}", exc_info=True)
            return []


