#!/usr/bin/env python3
"""
Data Steward Service - Multi-Tenant Production Implementation

Comprehensive data governance and file management service using GCS + Supabase pattern
with multi-tenant awareness and proper tenant isolation.

WHAT (Smart City Role): I manage data governance, lifecycle, and infrastructure across the platform with tenant awareness
HOW (Service Implementation): I use GCS for storage, Supabase for metadata, Redis for caching, and Security Guard for tenant validation
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List, Optional, BinaryIO
from datetime import datetime
from uuid import uuid4

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../'))

from bases.soa_service_base import SOAServiceBase
from backend.smart_city.protocols.soa_service_protocol import SOAServiceProtocol, SOAEndpoint, SOAServiceInfo
from foundations.utility_foundation.utility_foundation_service import UtilityFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from utilities import UserContext
from config.environment_loader import EnvironmentLoader
from config import Environment

# Import infrastructure abstractions
from foundations.infrastructure_foundation.abstractions.gcs_storage_abstraction import GCSStorageAbstraction
from foundations.infrastructure_foundation.abstractions.supabase_metadata_abstraction import SupabaseMetadataAbstraction
from foundations.infrastructure_foundation.abstractions.redis_cache_abstraction import RedisCacheAbstraction

# Import micro-modules
from .micro_modules.file_storage import FileStorageModule
from .micro_modules.metadata_management import MetadataManagementModule
from .micro_modules.data_governance import DataGovernanceModule
from .micro_modules.data_lifecycle import DataLifecycleModule
from .micro_modules.data_quality import DataQualityModule
from .micro_modules.access_control import AccessControlModule


class DataStewardService(SOAServiceBase):
    """
    Data Steward Service - Multi-Tenant Production Implementation
    
    Comprehensive data governance and file management service using the proven
    GCS + Supabase pattern with proper tenant isolation and security integration.
    
    WHAT (Smart City Role): I manage data governance, lifecycle, and infrastructure across the platform with tenant awareness
    HOW (Service Implementation): I use GCS for storage, Supabase for metadata, Redis for caching, and Security Guard for tenant validation
    """

    def __init__(self, utility_foundation: UtilityFoundationService, curator_foundation: CuratorFoundationService = None, 
                 public_works_foundation: PublicWorksFoundationService = None, environment: Optional[Environment] = None):
        """Initialize Data Steward Service with multi-tenant production infrastructure."""
        super().__init__("DataStewardService", utility_foundation, curator_foundation)
        
        self.public_works_foundation = public_works_foundation
        self.environment = environment or Environment.DEVELOPMENT
        
        # Initialize environment loader
        self.env_loader = EnvironmentLoader(environment)
        self.config = self.env_loader.get_all_config()
        
        # Multi-tenant coordination service
        self.multi_tenant_coordinator = None
        if self.public_works_foundation:
            self.multi_tenant_coordinator = self.public_works_foundation.multi_tenant_coordination_service
        
        # Smart city abstractions from public works
        self.smart_city_abstractions = {}
        
        # Initialize SOA protocol
        self.soa_protocol = DataStewardSOAProtocol("DataStewardService", self, curator_foundation), public_works_foundation
        
        # Initialize infrastructure abstractions
        self.gcs_abstraction = None
        self.supabase_abstraction = None
        self.redis_abstraction = None
        
        # Initialize micro-modules
        self.file_storage_module = None
        self.metadata_management_module = None
        self.data_governance_module = None
        self.data_lifecycle_module = None
        self.data_quality_module = None
        self.access_control_module = None
        
        # Service capabilities
        self.capabilities = [
            "file_storage",
            "metadata_management",
            "data_governance",
            "data_lifecycle",
            "data_quality",
            "access_control",
            "multi_tenant_data_governance"
        ]
        
        self.logger.info("📁 Data Steward Service initialized - Multi-Tenant Data Governance Hub")

    async def initialize(self):
        """Initialize the Data Steward service with multi-tenant capabilities."""
        try:
            await super().initialize()
            
            self.logger.info("🚀 Initializing Data Steward Service with multi-tenant capabilities...")

            # Initialize SOA protocol
            await self.soa_protocol.initialize()
            self.logger.info("✅ SOA Protocol initialized")

            # Initialize multi-tenant coordination
            if self.multi_tenant_coordinator:
                await self.multi_tenant_coordinator.initialize()
                self.logger.info("✅ Multi-tenant coordination initialized")
            
            # Load smart city abstractions from public works
            if self.public_works_foundation:
                await self.soa_protocol.load_smart_city_abstractions()
            self.smart_city_abstractions = self.soa_protocol.get_all_abstractions()
                self.logger.info(f"✅ Loaded {len(self.smart_city_abstractions)} smart city abstractions")

            # Initialize infrastructure abstractions
            await self._initialize_infrastructure_abstractions()
            
            # Initialize micro-modules
            await self._initialize_micro_modules()
            
            self.logger.info("✅ Data Steward Service initialized with multi-tenant capabilities")
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_initialize")
            raise

            self.logger.info("✅ Data Steward Service initialized successfully")

        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_service_initialization")
            self.service_health = "unhealthy"
            raise

    async def _initialize_infrastructure_abstractions(self):
        """Initialize infrastructure abstractions."""
        try:
            # Get GCS configuration from environment loader
            gcs_config = self.env_loader.get_gcs_config()
            
            if gcs_config["enabled"] and gcs_config["bucket_name"]:
                self.gcs_abstraction = GCSStorageAbstraction(
                    bucket_name=gcs_config["bucket_name"],
                    credentials_path=gcs_config["credentials_path"]
                )
                self.logger.info("✅ GCS Storage Abstraction initialized")
            else:
                self.logger.warning("⚠️ GCS not enabled or bucket not configured, file storage will be limited")

            # Get Supabase configuration from environment loader
            supabase_config = self.env_loader.get_supabase_config()
            
            if supabase_config["enabled"] and supabase_config["url"] and supabase_config["service_role_key"]:
                self.supabase_abstraction = SupabaseMetadataAbstraction(
                    supabase_url=supabase_config["url"],
                    supabase_key=supabase_config["service_role_key"]
                )
                self.logger.info("✅ Supabase Metadata Abstraction initialized")
            else:
                self.logger.warning("⚠️ Supabase not enabled or credentials not found, metadata operations will be limited")

            # Get Redis configuration from environment loader
            redis_config = self.env_loader.get_redis_config()
            
            if redis_config["url"]:
                # Parse Redis URL to extract connection details
                redis_url = redis_config["url"]
                if redis_url.startswith("redis://"):
                    # Simple parsing for redis://host:port/db format
                    parts = redis_url.replace("redis://", "").split("/")
                    host_port = parts[0].split(":")
                    host = host_port[0]
                    port = int(host_port[1]) if len(host_port) > 1 else 6379
                    db = int(parts[1]) if len(parts) > 1 else 0
                    
                    self.redis_abstraction = RedisCacheAbstraction(
                        host=host,
                        port=port,
                        password=redis_config.get("password"),
                        db=db
                    )
                    self.logger.info("✅ Redis Cache Abstraction initialized")
                else:
                    self.logger.warning("⚠️ Invalid Redis URL format, caching will be disabled")
            else:
                self.logger.warning("⚠️ Redis configuration not found, caching will be disabled")

        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_infrastructure_initialization")
            raise

    async def _initialize_micro_modules(self):
        """Initialize micro-modules."""
        try:
            # Initialize File Storage Module
            self.file_storage_module = FileStorageModule(
                logger=self.logger,
                env_loader=self.env_loader,
                gcs_abstraction=self.gcs_abstraction
            )
            await self.file_storage_module.initialize()

            # Initialize Metadata Management Module
            self.metadata_management_module = MetadataManagementModule(
                logger=self.logger,
                env_loader=self.env_loader,
                supabase_abstraction=self.supabase_abstraction
            )
            await self.metadata_management_module.initialize()

            # Initialize Data Governance Module
            self.data_governance_module = DataGovernanceModule(
                logger=self.logger,
                env_loader=self.env_loader
            )
            await self.data_governance_module.initialize()

            # Initialize Data Lifecycle Module
            self.data_lifecycle_module = DataLifecycleModule(
                logger=self.logger,
                env_loader=self.env_loader,
                gcs_abstraction=self.gcs_abstraction,
                supabase_abstraction=self.supabase_abstraction
            )
            await self.data_lifecycle_module.initialize()

            # Initialize Data Quality Module
            self.data_quality_module = DataQualityModule(
                logger=self.logger,
                env_loader=self.env_loader
            )
            await self.data_quality_module.initialize()

            # Initialize Access Control Module
            self.access_control_module = AccessControlModule(
                logger=self.logger,
                env_loader=self.env_loader
            )
            await self.access_control_module.initialize()

            self.logger.info("✅ All micro-modules initialized successfully")

        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_micro_modules_initialization")
            raise

    # File Storage Interface Implementation

    async def upload_file(self, file_data: BinaryIO, file_name: str, file_type: str, 
                         user_id: str, content_type: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None, 
                         user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Upload a file with governance and lifecycle management with tenant awareness."""
        try:
            # Validate tenant access
            if user_context and self.multi_tenant_coordinator:
                tenant_validation = await self.multi_tenant_coordinator.validate_tenant_feature_access(
                    user_context.tenant_id, "file_upload"
                )
                if not tenant_validation.get("allowed", False):
                    return {
                        "success": False,
                        "error": "Insufficient tenant permissions for file upload",
                        "file_uuid": None
                    }
            
            # Validate user permissions
            has_permission = await self.security_service.check_permissions(
                user_id, "file_upload", "write"
            )
            if not has_permission:
                return {
                    "success": False,
                    "error": "Insufficient permissions for file upload",
                    "file_uuid": None
                }
            # Generate file UUID
            file_uuid = str(uuid4())
            
            # Create file path in GCS
            file_path = f"content_files/{file_uuid}/{file_name}"
            
            # Upload file to GCS
            upload_result = await self.file_storage_module.upload_file(
                file_path=file_path,
                file_data=file_data,
                content_type=content_type,
                metadata=metadata
            )
            
            if not upload_result["success"]:
                return {
                    "success": False,
                    "error": upload_result["error"],
                    "file_uuid": None
                }
            
            # Create file metadata with tenant context
            file_metadata = {
                "uuid": file_uuid,
                "ui_name": file_name,
                "file_type": file_type,
                "mime_type": content_type,
                "original_path": upload_result["public_url"],
                "user_id": user_id,
                "status": "uploaded",
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "deleted": False
            }
            
            # Add tenant context to metadata
            if user_context and user_context.tenant_id:
                file_metadata["tenant_id"] = user_context.tenant_id
                file_metadata["uploaded_by"] = user_context.user_id
            
            # Store metadata in Supabase
            metadata_result = await self.metadata_management_module.create_file_metadata(file_metadata)
            
            if not metadata_result["success"]:
                # Clean up uploaded file if metadata storage fails
                await self.file_storage_module.delete_file(file_path)
                return {
                    "success": False,
                    "error": f"Metadata storage failed: {metadata_result['error']}",
                    "file_uuid": None
                }
            
            # Apply data governance policies
            governance_result = await self.data_governance_module.classify_file(file_metadata)
            
            # Apply data quality checks
            quality_result = await self.data_quality_module.validate_file(file_metadata)
            
            # Record telemetry for file upload with tenant context
            await self.telemetry_service.record_metric(
                "file_upload_count", 1,
                {
                    "file_type": file_type, 
                    "user_id": user_id,
                    "tenant_id": user_context.tenant_id if user_context else "system"
                }
            )
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "upload_file", "data_steward",
                    {
                        "file_uuid": file_uuid,
                        "file_name": file_name,
                        "file_type": file_type,
                        "governance_result": governance_result.get("success", False)
                    }
                )
            
            self.logger.info(f"✅ File uploaded successfully: {file_uuid}")
            
            return {
                "success": True,
                "file_uuid": file_uuid,
                "file_path": file_path,
                "public_url": upload_result["public_url"],
                "governance": governance_result,
                "quality": quality_result
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_file_upload")
            return {
                "success": False,
                "error": str(e),
                "file_uuid": None
            }

    async def download_file(self, file_uuid: str, user_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Download a file with access control and tenant awareness."""
        try:
            # Get file metadata first to check tenant access
            metadata_result = await self.metadata_management_module.get_file_metadata(file_uuid)
            if not metadata_result["success"]:
                return {
                    "success": False,
                    "error": metadata_result["error"],
                    "file_data": None
                }
            
            file_record = metadata_result["file_record"]
            
            # Check tenant access to file
            if user_context and user_context.tenant_id:
                if file_record.get("tenant_id") and file_record["tenant_id"] != user_context.tenant_id:
                    return {
                        "success": False,
                        "error": "Access denied: File belongs to different tenant",
                        "file_data": None
                    }
            
            # Check access permissions
            access_result = await self.access_control_module.check_file_access(file_uuid, user_id, "read")
            if not access_result["allowed"]:
                return {
                    "success": False,
                    "error": "Access denied",
                    "file_data": None
                }
            
            file_path = file_record["original_path"].replace(f"https://storage.googleapis.com/{self.gcs_abstraction.bucket_name}/", "")
            
            # Download file from GCS
            download_result = await self.file_storage_module.download_file(file_path)
            
            if not download_result["success"]:
                return {
                    "success": False,
                    "error": download_result["error"],
                    "file_data": None
                }
            
            # Log access for audit
            await self.access_control_module.log_file_access(file_uuid, user_id, "download")
            
            # Record telemetry for file download with tenant context
            await self.telemetry_service.record_metric(
                "file_download_count", 1,
                {
                    "file_uuid": file_uuid,
                    "user_id": user_id,
                    "tenant_id": user_context.tenant_id if user_context else "system"
                }
            )
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "download_file", "data_steward",
                    {
                        "file_uuid": file_uuid,
                        "file_name": file_record.get("ui_name", "unknown")
                    }
                )
            
            self.logger.info(f"✅ File downloaded successfully: {file_uuid}")
            
            return {
                "success": True,
                "file_data": download_result["file_data"],
                "file_name": file_record["ui_name"],
                "content_type": file_record["mime_type"],
                "size": download_result["size"]
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_file_download")
            return {
                "success": False,
                "error": str(e),
                "file_data": None
            }

    async def delete_file(self, file_uuid: str, user_id: str) -> Dict[str, Any]:
        """Delete a file with proper cleanup and governance."""
        try:
            # Check access permissions
            access_result = await self.access_control_module.check_file_access(file_uuid, user_id, "delete")
            if not access_result["allowed"]:
                return {
                    "success": False,
                    "error": "Access denied"
                }
            
            # Get file metadata
            metadata_result = await self.metadata_management_module.get_file_metadata(file_uuid)
            if not metadata_result["success"]:
                return {
                    "success": False,
                    "error": metadata_result["error"]
                }
            
            file_record = metadata_result["file_record"]
            file_path = file_record["original_path"].replace(f"https://storage.googleapis.com/{self.gcs_abstraction.bucket_name}/", "")
            
            # Apply data lifecycle policies
            lifecycle_result = await self.data_lifecycle_module.process_file_deletion(file_uuid, file_record)
            
            # Soft delete metadata
            delete_result = await self.metadata_management_module.delete_file(file_uuid)
            
            if not delete_result["success"]:
                return {
                    "success": False,
                    "error": delete_result["error"]
                }
            
            # Log deletion for audit
            await self.access_control_module.log_file_access(file_uuid, user_id, "delete")
            
            self.logger.info(f"✅ File deleted successfully: {file_uuid}")
            
            return {
                "success": True,
                "file_uuid": file_uuid,
                "lifecycle": lifecycle_result
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_file_deletion")
            return {
                "success": False,
                "error": str(e)
            }

    async def list_files(self, user_id: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """List files with filtering and access control."""
        try:
            # Apply access control filters
            access_filters = await self.access_control_module.get_user_file_filters(user_id)
            
            # Merge with provided filters
            if filters:
                access_filters.update(filters)
            
            # List files from metadata
            list_result = await self.metadata_management_module.list_files(
                user_id=user_id,
                **access_filters
            )
            
            if not list_result["success"]:
                return {
                    "success": False,
                    "error": list_result["error"],
                    "files": []
                }
            
            self.logger.info(f"✅ Listed {len(list_result['files'])} files for user {user_id}")
            
            return {
                "success": True,
                "files": list_result["files"],
                "total_count": list_result["total_count"]
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_file_listing")
            return {
                "success": False,
                "error": str(e),
                "files": []
            }

    async def get_file_metadata(self, file_uuid: str, user_id: str) -> Dict[str, Any]:
        """Get file metadata with access control."""
        try:
            # Check access permissions
            access_result = await self.access_control_module.check_file_access(file_uuid, user_id, "read")
            if not access_result["allowed"]:
                return {
                    "success": False,
                    "error": "Access denied"
                }
            
            # Get file metadata
            metadata_result = await self.metadata_management_module.get_file_metadata(file_uuid)
            
            if not metadata_result["success"]:
                return {
                    "success": False,
                    "error": metadata_result["error"]
                }
            
            # Log access for audit
            await self.access_control_module.log_file_access(file_uuid, user_id, "metadata_read")
            
            return {
                "success": True,
                "file_record": metadata_result["file_record"]
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_metadata_retrieval")
            return {
                "success": False,
                "error": str(e)
            }

    async def update_file_metadata(self, file_uuid: str, updates: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Update file metadata with access control and validation."""
        try:
            # Check access permissions
            access_result = await self.access_control_module.check_file_access(file_uuid, user_id, "write")
            if not access_result["allowed"]:
                return {
                    "success": False,
                    "error": "Access denied"
                }
            
            # Validate updates
            validation_result = await self.data_quality_module.validate_metadata_updates(updates)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": f"Validation failed: {validation_result['error']}"
                }
            
            # Update metadata
            update_result = await self.metadata_management_module.update_file_metadata(file_uuid, updates)
            
            if not update_result["success"]:
                return {
                    "success": False,
                    "error": update_result["error"]
                }
            
            # Log update for audit
            await self.access_control_module.log_file_access(file_uuid, user_id, "metadata_update")
            
            self.logger.info(f"✅ File metadata updated successfully: {file_uuid}")
            
            return {
                "success": True,
                "file_record": update_result["file_record"]
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_metadata_update")
            return {
                "success": False,
                "error": str(e)
            }

    # Data Governance Interface

    async def classify_file(self, file_uuid: str, user_id: str) -> Dict[str, Any]:
        """Classify a file based on governance policies."""
        try:
            # Get file metadata
            metadata_result = await self.metadata_management_module.get_file_metadata(file_uuid)
            if not metadata_result["success"]:
                return {
                    "success": False,
                    "error": metadata_result["error"]
                }
            
            # Apply classification
            classification_result = await self.data_governance_module.classify_file(metadata_result["file_record"])
            
            return {
                "success": True,
                "classification": classification_result
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_file_classification")
            return {
                "success": False,
                "error": str(e)
            }

    async def apply_retention_policy(self, file_uuid: str, user_id: str) -> Dict[str, Any]:
        """Apply data retention policies to a file."""
        try:
            # Get file metadata
            metadata_result = await self.metadata_management_module.get_file_metadata(file_uuid)
            if not metadata_result["success"]:
                return {
                    "success": False,
                    "error": metadata_result["error"]
                }
            
            # Apply retention policy
            retention_result = await self.data_lifecycle_module.apply_retention_policy(file_uuid, metadata_result["file_record"])
            
            return {
                "success": True,
                "retention": retention_result
            }
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="data_steward_retention_policy")
            return {
                "success": False,
                "error": str(e)
            }

    # Service Health and Status

    # Note: Using standard FoundationServiceBase health check pattern
    # Custom health logic should be implemented in micro-modules, not in service health check

    def get_service_status(self) -> Dict[str, Any]:
        """Get the status of the Data Steward Service."""
        try:
            return {
                "service_name": "data_steward",
                "service_type": "smart_city_service",
                "architecture": "gcs_supabase_redis",
                "environment": self.environment.value,
                "infrastructure": {
                    "gcs_bucket": self.gcs_abstraction.bucket_name if self.gcs_abstraction else None,
                    "supabase_connected": self.supabase_abstraction is not None,
                    "redis_connected": self.redis_abstraction is not None
                },
                "micro_modules": [
                    "file_storage", "metadata_management", "data_governance",
                    "data_lifecycle", "data_quality", "access_control"
                ],
                "initialized": self.is_initialized,
                "health": self.service_health
            }
            
        except Exception as e:
            return {
                "service_name": "data_steward",
                "service_type": "smart_city_service",
                "error": str(e),
                "initialized": False
            }
    
    # ============================================================================
    # MULTI-TENANT SPECIFIC METHODS
    # ============================================================================
    
    async def get_tenant_files(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get all files for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's files"}
            
            # Get tenant-specific files
            filters = {"tenant_id": tenant_id}
            result = await self.list_files("system", filters, user_context)
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_files", "data_steward",
                    {"tenant_id": tenant_id, "file_count": len(result.get("files", []))}
                )
            
            return result
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_files")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_storage_usage(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get storage usage for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's storage usage"}
            
            # Get tenant files
            tenant_files = await self.get_tenant_files(tenant_id, user_context)
            if not tenant_files.get("success"):
                return tenant_files
            
            # Calculate storage metrics
            files = tenant_files.get("files", [])
            total_size = sum(file.get("file_size", 0) for file in files)
            file_count = len(files)
            
            usage_metrics = {
                "tenant_id": tenant_id,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "average_file_size": round(total_size / file_count, 2) if file_count > 0 else 0
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_storage_usage", "data_steward",
                    {"tenant_id": tenant_id, "total_size_mb": usage_metrics["total_size_mb"]}
                )
            
            return {"success": True, "usage_metrics": usage_metrics}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_storage_usage")
            return {"success": False, "error": str(e)}
    
    async def get_tenant_data_governance_summary(self, tenant_id: str, user_context: Optional[UserContext] = None) -> Dict[str, Any]:
        """Get data governance summary for a specific tenant."""
        try:
            # Validate user access to tenant
            if user_context and user_context.tenant_id != tenant_id:
                return {"success": False, "error": "Access denied: Cannot access other tenant's governance summary"}
            
            # Get tenant files
            tenant_files = await self.get_tenant_files(tenant_id, user_context)
            if not tenant_files.get("success"):
                return tenant_files
            
            files = tenant_files.get("files", [])
            
            # Calculate governance metrics
            governance_summary = {
                "tenant_id": tenant_id,
                "total_files": len(files),
                "classified_files": len([f for f in files if f.get("classification")]),
                "governance_policies_applied": len([f for f in files if f.get("governance_policies")]),
                "retention_policies_active": len([f for f in files if f.get("retention_policy")]),
                "data_quality_score": self._calculate_data_quality_score(files)
            }
            
            # Audit the action
            if user_context:
                await self.security_service.audit_user_action(
                    user_context, "get_tenant_data_governance_summary", "data_steward",
                    {"tenant_id": tenant_id, "total_files": governance_summary["total_files"]}
                )
            
            return {"success": True, "governance_summary": governance_summary}
            
        except Exception as e:
            await self.error_handler.handle_error(e, context="get_tenant_data_governance_summary")
            return {"success": False, "error": str(e)}
    
    def _calculate_data_quality_score(self, files: List[Dict[str, Any]]) -> float:
        """Calculate data quality score based on file metadata."""
        if not files:
            return 100.0
        
        quality_indicators = []
        for file in files:
            score = 0
            if file.get("metadata"):
                score += 25
            if file.get("classification"):
                score += 25
            if file.get("governance_policies"):
                score += 25
            if file.get("retention_policy"):
                score += 25
            quality_indicators.append(score)
        
        return round(sum(quality_indicators) / len(quality_indicators), 2)


class DataStewardSOAProtocol(SOAServiceProtocol):
    """SOA Protocol implementation for Data Steward Service."""
    
    def __init__(self, service_name: str, service_instance, curator_foundation=None, public_works_foundation=None):
        """Initialize Data Steward SOA Protocol."""
        super().__init__(service_name, None, curator_foundation, public_works_foundation)
        self.service_instance = service_instance
        self.service_info = None
        
    async def initialize(self, user_context: UserContext = None):
        """Initialize the SOA service."""
        # Create service info with multi-tenant metadata
        self.service_info = SOAServiceInfo(
            service_name="DataStewardService",
            version="1.0.0",
            description="Data Steward Service - Multi-tenant data governance and file management",
            interface_name="IDataSteward",
            endpoints=self._create_all_endpoints(),
            tags=["data-governance", "file-management", "multi-tenant", "data-quality"],
            contact={"email": "datasteward@smartcity.com"},
            multi_tenant_enabled=True,
            tenant_isolation_level="strict"
        )
    
    def get_service_info(self) -> SOAServiceInfo:
        """Get service information for OpenAPI generation."""
        return self.service_info
    
    def get_openapi_spec(self) -> Dict[str, Any]:
        """Get OpenAPI 3.0 specification for this service."""
        if not self.service_info:
            return {"error": "Service not initialized"}
        
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.service_info.service_name,
                "version": self.service_info.version,
                "description": self.service_info.description,
                "contact": self.service_info.contact
            },
            "servers": [
                {"url": "https://api.smartcity.com/data-steward", "description": "Data Steward Service"}
            ],
            "paths": self._create_openapi_paths(),
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "security": [{"BearerAuth": []}]
        }
    
    def get_docs(self) -> Dict[str, Any]:
        """Get service documentation."""
        return {
            "service": self.service_info.service_name,
            "description": self.service_info.description,
            "version": self.service_info.version,
            "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
            "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
            "tenant_isolation_level": self.service_info.tenant_isolation_level
        }
    
    async def register_with_curator(self, user_context: UserContext = None) -> Dict[str, Any]:
        """Register this service with Curator Foundation Service."""
        if self.curator_foundation:
            capability = {
                "interface": self.service_info.interface_name,
                "endpoints": [endpoint.path for endpoint in self.service_info.endpoints],
                "tools": [],  # MCP tools handled separately
                "description": self.service_info.description,
                "realm": "smart_city",
                "multi_tenant_enabled": self.service_info.multi_tenant_enabled,
                "tenant_isolation_level": self.service_info.tenant_isolation_level
            }
            
            return await self.curator_foundation.register_capability(
                self.service_name, 
                capability, 
                user_context
            )
        else:
            return {"error": "Curator Foundation Service not available"}
    
    def _create_all_endpoints(self) -> List[SOAEndpoint]:
        """Create all endpoints for Data Steward Service."""
        endpoints = []
        
        # Standard endpoints
        endpoints.extend(self._create_standard_endpoints())
        endpoints.extend(self._create_health_endpoints())
        endpoints.extend(self._create_tenant_aware_endpoints())
        
        # Data Steward specific endpoints
        endpoints.extend([
            SOAEndpoint(
                path="/files",
                method="POST",
                summary="Upload File",
                description="Upload a file with tenant awareness",
                request_schema={
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                        "content_type": {"type": "string"},
                        "file_data": {"type": "string", "format": "binary"},
                        "metadata": {"type": "object"},
                        "classification": {"type": "string"}
                    },
                    "required": ["filename", "content_type", "file_data"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Files", "Upload"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/files/{file_id}",
                method="GET",
                summary="Download File",
                description="Download a file with tenant awareness",
                parameters=[
                    {
                        "name": "file_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "File ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string"},
                        "filename": {"type": "string"},
                        "content_type": {"type": "string"},
                        "file_data": {"type": "string", "format": "binary"}
                    }
                }),
                tags=["Files", "Download"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/files",
                method="GET",
                summary="List Files",
                description="List files for the current tenant",
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "files": {"type": "array", "items": {"type": "object"}},
                        "total_count": {"type": "integer"}
                    }
                }),
                tags=["Files", "Management"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/files/{file_id}/metadata",
                method="GET",
                summary="Get File Metadata",
                description="Get metadata for a specific file",
                parameters=[
                    {
                        "name": "file_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "File ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "file_id": {"type": "string"},
                        "metadata": {"type": "object"},
                        "classification": {"type": "string"}
                    }
                }),
                tags=["Files", "Metadata"],
                requires_tenant=True,
                tenant_scope="user"
            ),
            SOAEndpoint(
                path="/governance/policies",
                method="GET",
                summary="List Governance Policies",
                description="List data governance policies for the current tenant",
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "policies": {"type": "array", "items": {"type": "object"}},
                        "total_count": {"type": "integer"}
                    }
                }),
                tags=["Governance", "Policies"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/governance/policies",
                method="POST",
                summary="Create Governance Policy",
                description="Create a new data governance policy",
                request_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "rules": {"type": "array", "items": {"type": "object"}},
                        "classification": {"type": "string"}
                    },
                    "required": ["name", "description", "rules"]
                },
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "policy_id": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }),
                tags=["Governance", "Policies"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/file-summary",
                method="GET",
                summary="Get Tenant File Summary",
                description="Get file summary for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_files": {"type": "integer"},
                        "total_size_bytes": {"type": "number"},
                        "file_types": {"type": "object"}
                    }
                }),
                tags=["Tenant", "Files"],
                requires_tenant=True,
                tenant_scope="tenant"
            ),
            SOAEndpoint(
                path="/tenant/{tenant_id}/governance-summary",
                method="GET",
                summary="Get Tenant Governance Summary",
                description="Get data governance summary for a specific tenant",
                parameters=[
                    {
                        "name": "tenant_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                        "description": "Tenant ID"
                    }
                ],
                response_schema=self._create_success_response_schema({
                    "type": "object",
                    "properties": {
                        "tenant_id": {"type": "string"},
                        "total_policies": {"type": "integer"},
                        "data_quality_score": {"type": "number"},
                        "compliance_status": {"type": "string"}
                    }
                }),
                tags=["Tenant", "Governance"],
                requires_tenant=True,
                tenant_scope="tenant"
            )
        ])
        
        return endpoints
    
    def _create_openapi_paths(self) -> Dict[str, Any]:
        """Create OpenAPI paths for all endpoints."""
        paths = {}
        
        for endpoint in self.service_info.endpoints:
            path_item = {
                endpoint.method.lower(): {
                    "summary": endpoint.summary,
                    "description": endpoint.description,
                    "tags": endpoint.tags,
                    "security": [{"BearerAuth": []}] if endpoint.requires_tenant else []
                }
            }
            
            if endpoint.parameters:
                path_item[endpoint.method.lower()]["parameters"] = endpoint.parameters
            
            if endpoint.request_schema:
                path_item[endpoint.method.lower()]["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint.request_schema
                        }
                    }
                }
            
            if endpoint.response_schema:
                path_item[endpoint.method.lower()]["responses"] = {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": endpoint.response_schema
                            }
                        }
                    },
                    "400": {
                        "description": "Bad Request",
                        "content": {
                            "application/json": {
                                "schema": self._create_error_response_schema()
                            }
                        }
                    }
                }
            
            paths[endpoint.path] = path_item
        
        return paths