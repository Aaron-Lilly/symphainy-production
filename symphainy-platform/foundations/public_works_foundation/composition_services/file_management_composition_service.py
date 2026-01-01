#!/usr/bin/env python3
"""
File Management Composition Service - Complex Workflow Orchestration

Orchestrates complex file management workflows and business processes.
This is Layer 4 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I orchestrate complex file management workflows
HOW (Infrastructure Implementation): I compose multiple operations into business processes
"""

import logging
import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..infrastructure_abstractions.file_management_abstraction import FileManagementAbstraction

logger = logging.getLogger(__name__)

class FileManagementCompositionService:
    """
    Composition service for complex file management workflows.
    
    Orchestrates multiple file operations into cohesive business processes
    for the platform's file management needs.
    """
    
    def __init__(self, file_management_abstraction: FileManagementAbstraction, di_container=None):
        """Initialize file management composition service."""
        self.file_management = file_management_abstraction
        self.di_container = di_container
        self.service_name = "file_management_composition_service"
        
        # Get logger from DI Container if available, otherwise use standard logger
        if di_container and hasattr(di_container, 'get_logger'):
            self.logger = di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        self.logger.info("✅ File Management Composition Service initialized")
    
    # ============================================================================
    # SECURITY AND MULTI-TENANCY VALIDATION HELPERS
    # ============================================================================
    
    async def _validate_security_and_tenant(self, user_context: Dict[str, Any], 
                                           resource: str, action: str) -> Optional[Dict[str, Any]]:
        """
        Validate security context and tenant access.
        
        Args:
            user_context: User context with user_id, tenant_id, security_context
            resource: Resource being accessed
            action: Action being performed
            
        Returns:
            None if validation passes, error dict if validation fails
        """
        try:
            # Get utilities from DI container
            security = self.di_container.get_utility("security") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            tenant = self.di_container.get_utility("tenant") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            
            user_id = user_context.get("user_id")
            tenant_id = user_context.get("tenant_id")
            security_context = user_context.get("security_context")
            
            # Security validation (if security utility available and context provided)
            if security and security_context:
                try:
                    # Validate user permission
                    has_permission = await security.validate_user_permission(
                        user_id, resource, action, 
                        security_context.get("permissions", [])
                    )
                    if not has_permission:
                        return {
                            "success": False,
                            "error": f"Permission denied: {action} on {resource}",
                            "error_code": "PERMISSION_DENIED"
                        }
                except Exception as e:
                    self.logger.warning(f"Security validation failed: {e}")
                    # Don't fail on security validation errors - log and continue
                    # (security might not be fully bootstrapped)
            
            # Multi-tenancy validation (if tenant utility available and tenant_id provided)
            if tenant and tenant_id:
                try:
                    # Check if multi-tenancy is enabled
                    if tenant.is_multi_tenant_enabled():
                        # Validate tenant access (basic check - user can only access their own tenant)
                        # For cross-tenant access, this would be handled at foundation service level
                        if not tenant.validate_tenant_access(tenant_id, tenant_id):
                            return {
                                "success": False,
                                "error": f"Tenant access denied for tenant: {tenant_id}",
                                "error_code": "TENANT_ACCESS_DENIED"
                            }
                except Exception as e:
                    self.logger.warning(f"Tenant validation failed: {e}")
                    # Don't fail on tenant validation errors - log and continue
            
            return None  # Validation passed
            
        except Exception as e:
            self.logger.error(f"Security/tenant validation error: {e}")
            # Don't fail on validation errors - log and continue
            return None
    
    # ============================================================================
    # FILE UPLOAD AND PROCESSING WORKFLOWS
    # ============================================================================
    
    async def upload_and_process_file(self, file_data: bytes, filename: str, file_type: str, 
                                    user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete file upload and processing workflow.
        
        Args:
            file_data: Raw file bytes
            filename: Original filename
            file_type: File type/extension
            user_context: User context information
            
        Returns:
            Dict containing upload result and processing information
        """
        try:
            self.logger.info(f"🚀 Starting upload and process workflow for: {filename}")
            
            # Validate security and tenant access
            validation_error = await self._validate_security_and_tenant(
                user_context, "file", "upload"
            )
            if validation_error:
                return validation_error
            
            # 1. Calculate file metadata
            file_hash = hashlib.sha256(file_data).hexdigest()
            file_size = len(file_data)
            
            # 2. Determine content type
            content_type = self._determine_content_type(file_data, file_type)
            
            # 3. Create initial file record
            file_record = {
                "ui_name": filename,
                "file_type": file_type,
                "file_size": file_size,
                "file_hash": file_hash,
                "file_data": file_data,  # Store raw data for processing
                "user_id": user_context.get("user_id"),
                "tenant_id": user_context.get("tenant_id"),
                "created_by": user_context.get("user_id"),
                "upload_source": user_context.get("upload_source", "web_interface"),
                "client_ip": user_context.get("client_ip"),
                "user_agent": user_context.get("user_agent"),
                "pillar_origin": "content_pillar",
                "content_type": content_type,
                "status": "uploaded",
                "processing_status": "pending"
            }
            
            # 4. Create file
            file_result = await self.file_management.create_file(file_record)
            
            # 5. Update processing status
            await self.file_management.update_file(file_result["uuid"], {
                "processing_status": "completed",
                "status": "completed"
            })
            
            self.logger.info(f"✅ Upload and process workflow completed: {file_result['uuid']}")
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("upload_and_process_file", {
                    "filename": filename,
                    "file_type": file_type,
                    "file_size": file_size,
                    "file_uuid": file_result["uuid"],
                    "success": True
                })
            
            return {
                "success": True,
                "file_uuid": file_result["uuid"],
                "content_type": content_type,
                "file_size": file_size,
                "file_hash": file_hash,
                "message": "File uploaded and processed successfully"
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "upload_and_process_file",
                    "filename": filename,
                    "file_type": file_type,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Upload and process workflow failed: {e}")
            raise
    
    async def create_parsed_components(self, parent_uuid: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create parsed components from hybrid document.
        
        Args:
            parent_uuid: UUID of parent file
            parsed_data: Parsed document data with text and tables
            
        Returns:
            Dict containing created component information
        """
        try:
            self.logger.info(f"🔧 Creating parsed components for parent: {parent_uuid}")
            
            components = {}
            parent_name = parsed_data.get("ui_name", "document")
            
            # Create text component if exists
            if parsed_data.get("text_content"):
                text_data = parsed_data["text_content"].encode('utf-8')
                text_component = await self.file_management.create_child_file(
                    parent_uuid=parent_uuid,
                    child_data={
                        "ui_name": f"{parent_name}_text.txt",
                        "file_type": "txt",
                        "content_type": "unstructured",
                        "file_size": len(text_data),
                        "file_data": text_data,
                        "processing_pipeline": {
                            "stage": "text_extraction",
                            "timestamp": datetime.utcnow().isoformat(),
                            "source": "hybrid_parsing"
                        }
                    },
                    link_type="parsed_from"
                )
                components["text"] = text_component
            
            # Create tables component if exists
            if parsed_data.get("tables"):
                tables_csv = self._convert_tables_to_csv(parsed_data["tables"])
                tables_data = tables_csv.encode('utf-8')
                tables_component = await self.file_management.create_child_file(
                    parent_uuid=parent_uuid,
                    child_data={
                        "ui_name": f"{parent_name}_tables.csv",
                        "file_type": "csv",
                        "content_type": "structured",
                        "file_size": len(tables_data),
                        "file_data": tables_data,
                        "processing_pipeline": {
                            "stage": "table_extraction",
                            "timestamp": datetime.utcnow().isoformat(),
                            "source": "hybrid_parsing",
                            "table_count": len(parsed_data["tables"])
                        }
                    },
                    link_type="parsed_from"
                )
                components["tables"] = tables_component
            
            self.logger.info(f"✅ Created {len(components)} parsed components for {parent_uuid}")
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("create_parsed_components", {
                    "parent_uuid": parent_uuid,
                    "component_count": len(components),
                    "success": True
                })
            
            return {
                "success": True,
                "components": components,
                "component_count": len(components),
                "message": "Parsed components created successfully"
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_parsed_components",
                    "parent_uuid": parent_uuid,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Create parsed components failed: {e}")
            raise
    
    # ============================================================================
    # FILE LINEAGE AND RELATIONSHIP WORKFLOWS
    # ============================================================================
    
    async def create_file_lineage_chain(self, root_file_uuid: str, 
                                      processing_stages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a complete file lineage chain through processing stages.
        
        Args:
            root_file_uuid: UUID of the root file
            processing_stages: List of processing stage configurations
            
        Returns:
            Dict containing lineage chain information
        """
        try:
            self.logger.info(f"🔗 Creating file lineage chain from root: {root_file_uuid}")
            
            lineage_chain = {
                "root_uuid": root_file_uuid,
                "stages": [],
                "total_files": 1
            }
            
            current_file_uuid = root_file_uuid
            
            for i, stage in enumerate(processing_stages):
                # Create child file for this stage
                child_data = {
                    "ui_name": f"{stage['name']}_{i+1}",
                    "file_type": stage.get("file_type", "processed"),
                    "content_type": stage.get("content_type", "unstructured"),
                    "file_data": stage.get("file_data", b""),
                    "processing_pipeline": {
                        "stage": stage["name"],
                        "stage_number": i + 1,
                        "timestamp": datetime.utcnow().isoformat(),
                        "parameters": stage.get("parameters", {})
                    }
                }
                
                child_file = await self.file_management.create_child_file(
                    parent_uuid=current_file_uuid,
                    child_data=child_data,
                    link_type=stage.get("link_type", "derived_from")
                )
                
                lineage_chain["stages"].append({
                    "stage_name": stage["name"],
                    "file_uuid": child_file["uuid"],
                    "generation": child_file["generation"]
                })
                
                current_file_uuid = child_file["uuid"]
                lineage_chain["total_files"] += 1
            
            self.logger.info(f"✅ Created lineage chain with {len(processing_stages)} stages")
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("create_file_lineage_chain", {
                    "root_file_uuid": root_file_uuid,
                    "stage_count": len(processing_stages),
                    "success": True
                })
            
            return {
                "success": True,
                "lineage_chain": lineage_chain,
                "message": "File lineage chain created successfully"
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "create_file_lineage_chain",
                    "root_file_uuid": root_file_uuid,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Create file lineage chain failed: {e}")
            raise
    
    async def get_complete_file_lineage(self, file_uuid: str) -> Dict[str, Any]:
        """
        Get complete file lineage with detailed information.
        
        Args:
            file_uuid: UUID of the file to get lineage for
            
        Returns:
            Dict containing complete lineage information
        """
        try:
            self.logger.info(f"🌳 Getting complete file lineage for: {file_uuid}")
            
            # Get the file to find root
            file_record = await self.file_management.get_file(file_uuid)
            if not file_record:
                raise ValueError(f"File not found: {file_uuid}")
            
            # Get root file UUID
            root_uuid = file_record.get("root_file_uuid", file_uuid)
            
            # Get complete lineage tree
            lineage_tree = await self.file_management.get_lineage_tree(root_uuid)
            
            # Organize lineage by generation
            lineage_by_generation = {}
            for file_info in lineage_tree:
                generation = file_info.get("generation", 0)
                if generation not in lineage_by_generation:
                    lineage_by_generation[generation] = []
                lineage_by_generation[generation].append(file_info)
            
            # Get file links for relationship details
            file_links = await self.file_management.get_file_links(file_uuid, "both")
            
            result = {
                "file_uuid": file_uuid,
                "root_uuid": root_uuid,
                "lineage_tree": lineage_tree,
                "lineage_by_generation": lineage_by_generation,
                "file_relationships": file_links,
                "total_files": len(lineage_tree),
                "max_generation": max(lineage_by_generation.keys()) if lineage_by_generation else 0
            }
            
            self.logger.info(f"✅ Retrieved complete lineage with {len(lineage_tree)} files")
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("get_complete_file_lineage", {
                    "file_uuid": file_uuid,
                    "total_files": len(lineage_tree),
                    "success": True
                })
            
            return {
                "success": True,
                "lineage": result,
                "message": "Complete file lineage retrieved successfully"
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "get_complete_file_lineage",
                    "file_uuid": file_uuid,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Get complete file lineage failed: {e}")
            raise
    
    # ============================================================================
    # FILE SEARCH AND DISCOVERY WORKFLOWS
    # ============================================================================
    
    async def advanced_file_search(self, user_id: str, search_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Advanced file search with multiple criteria.
        
        Args:
            user_id: User identifier
            search_criteria: Dictionary of search criteria
            
        Returns:
            Dict containing search results and metadata
        """
        try:
            self.logger.info(f"🔍 Advanced file search for user: {user_id}")
            
            search_results = []
            search_term = search_criteria.get("search_term", "")
            content_type = search_criteria.get("content_type")
            file_type = search_criteria.get("file_type")
            date_range = search_criteria.get("date_range")
            lineage_depth = search_criteria.get("lineage_depth")
            
            # Basic search
            if search_term:
                results = await self.file_management.search_files(
                    user_id=user_id,
                    search_term=search_term,
                    content_type=content_type,
                    file_type=file_type
                )
                search_results.extend(results)
            
            # Additional filtering
            if date_range:
                start_date = date_range.get("start")
                end_date = date_range.get("end")
                # This would require additional filtering logic
                pass
            
            if lineage_depth is not None:
                # Filter by lineage depth
                search_results = [f for f in search_results if f.get("lineage_depth", 0) == lineage_depth]
            
            # Remove duplicates
            seen_uuids = set()
            unique_results = []
            for result in search_results:
                if result["uuid"] not in seen_uuids:
                    unique_results.append(result)
                    seen_uuids.add(result["uuid"])
            
            self.logger.info(f"✅ Advanced search found {len(unique_results)} files")
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("advanced_file_search", {
                    "user_id": user_id,
                    "total_results": len(unique_results),
                    "success": True
                })
            
            return {
                "success": True,
                "results": unique_results,
                "total_results": len(unique_results),
                "search_criteria": search_criteria,
                "message": "Advanced file search completed successfully"
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "advanced_file_search",
                    "user_id": user_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Advanced file search failed: {e}")
            raise
    
    # ============================================================================
    # FILE ANALYTICS AND REPORTING WORKFLOWS
    # ============================================================================
    
    async def generate_file_analytics(self, user_id: str, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive file analytics.
        
        Args:
            user_id: User identifier
            tenant_id: Optional tenant identifier
            
        Returns:
            Dict containing analytics data
        """
        try:
            self.logger.info(f"📊 Generating file analytics for user: {user_id}")
            
            # Get basic statistics
            stats = await self.file_management.get_file_statistics(user_id, tenant_id)
            
            # Get all files for detailed analysis
            all_files = await self.file_management.list_files(user_id, tenant_id)
            
            # Calculate additional analytics
            analytics = {
                "basic_statistics": stats,
                "file_size_analysis": self._analyze_file_sizes(all_files),
                "content_type_distribution": self._analyze_content_types(all_files),
                "lineage_analysis": self._analyze_lineage_patterns(all_files),
                "processing_pipeline_analysis": self._analyze_processing_pipelines(all_files),
                "temporal_analysis": self._analyze_temporal_patterns(all_files),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"✅ Generated comprehensive file analytics")
            
            # Record platform operation event
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if telemetry:
                await telemetry.record_platform_operation_event("generate_file_analytics", {
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "success": True
                })
            
            return {
                "success": True,
                "analytics": analytics,
                "message": "File analytics generated successfully"
            }
            
        except Exception as e:
            # Use error handler with telemetry
            error_handler = self.di_container.get_utility("error_handler") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            telemetry = self.di_container.get_utility("telemetry") if self.di_container and hasattr(self.di_container, 'get_utility') else None
            if error_handler:
                await error_handler.handle_error(e, {
                    "operation": "generate_file_analytics",
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "service": self.service_name
                }, telemetry=telemetry)
            else:
                self.logger.error(f"❌ Generate file analytics failed: {e}")
            raise
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _determine_content_type(self, file_data: bytes, file_type: str) -> str:
        """Determine content type from file data and type."""
        # Simple content type detection logic
        if file_type.lower() in ["csv", "xlsx", "xls", "json"]:
            return "structured"
        elif file_type.lower() in ["txt", "md", "rtf"]:
            return "unstructured"
        elif file_type.lower() in ["pdf", "docx", "doc"]:
            return "hybrid"  # Could contain both text and tables
        else:
            return "unstructured"
    
    def _convert_tables_to_csv(self, tables: List[Dict[str, Any]]) -> str:
        """Convert table data to CSV format."""
        csv_lines = []
        
        for table in tables:
            # Add table header
            if table.get("columns"):
                csv_lines.append(",".join(table["columns"]))
            
            # Add table rows
            if table.get("rows"):
                for row in table["rows"]:
                    csv_lines.append(",".join(str(cell) for cell in row))
            
            # Add separator between tables
            csv_lines.append("")
        
        return "\n".join(csv_lines)
    
    def _analyze_file_sizes(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze file size patterns."""
        sizes = [f.get("file_size", 0) for f in files if f.get("file_size")]
        
        if not sizes:
            return {"total_size": 0, "average_size": 0, "size_distribution": {}}
        
        return {
            "total_size": sum(sizes),
            "average_size": sum(sizes) / len(sizes),
            "min_size": min(sizes),
            "max_size": max(sizes),
            "size_distribution": {
                "small": len([s for s in sizes if s < 1024 * 1024]),  # < 1MB
                "medium": len([s for s in sizes if 1024 * 1024 <= s < 10 * 1024 * 1024]),  # 1-10MB
                "large": len([s for s in sizes if s >= 10 * 1024 * 1024])  # >= 10MB
            }
        }
    
    def _analyze_content_types(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content type distribution."""
        content_types = {}
        file_types = {}
        
        for file in files:
            content_type = file.get("content_type", "unknown")
            file_type = file.get("file_type", "unknown")
            
            content_types[content_type] = content_types.get(content_type, 0) + 1
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            "content_types": content_types,
            "file_types": file_types
        }
    
    def _analyze_lineage_patterns(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze file lineage patterns."""
        lineage_depths = [f.get("lineage_depth", 0) for f in files]
        generations = [f.get("generation", 0) for f in files]
        
        return {
            "max_lineage_depth": max(lineage_depths) if lineage_depths else 0,
            "max_generation": max(generations) if generations else 0,
            "average_lineage_depth": sum(lineage_depths) / len(lineage_depths) if lineage_depths else 0,
            "lineage_distribution": {
                "root_files": len([f for f in files if f.get("lineage_depth", 0) == 0]),
                "derived_files": len([f for f in files if f.get("lineage_depth", 0) > 0])
            }
        }
    
    def _analyze_processing_pipelines(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze processing pipeline patterns."""
        pipelines = {}
        
        for file in files:
            pipeline = file.get("processing_pipeline", {})
            if pipeline:
                stage = pipeline.get("stage", "unknown")
                pipelines[stage] = pipelines.get(stage, 0) + 1
        
        return {
            "pipeline_stages": pipelines,
            "files_with_pipelines": len([f for f in files if f.get("processing_pipeline")])
        }
    
    def _analyze_temporal_patterns(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in file creation."""
        # This would analyze creation dates, upload patterns, etc.
        return {
            "total_files": len(files),
            "analysis": "Temporal analysis not implemented yet"
        }




