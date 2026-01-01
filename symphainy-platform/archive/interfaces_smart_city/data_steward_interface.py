#!/usr/bin/env python3
"""
Data Steward Interface

Defines the contracts for Data Steward service operations.
This interface matches the existing DataStewardService APIs.

WHAT (Interface Role): I define the contracts for data governance and lifecycle management
HOW (Interface Implementation): I provide clear, typed interfaces for consumers
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class DataStatus(str, Enum):
    """Data status levels."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    PENDING = "pending"
    PROCESSING = "processing"


class DataPolicyType(str, Enum):
    """Data policy type levels."""
    RETENTION = "retention"
    ACCESS = "access"
    PRIVACY = "privacy"
    QUALITY = "quality"
    COMPLIANCE = "compliance"


class DataLineageType(str, Enum):
    """Data lineage type levels."""
    SOURCE = "source"
    TRANSFORMATION = "transformation"
    DESTINATION = "destination"
    DEPENDENCY = "dependency"


# Request Models
class RegisterDatasetRequest(BaseModel):
    """Request to register a new dataset."""
    dataset_id: str = Field(..., description="Unique identifier for the dataset")
    dataset_name: str = Field(..., description="Name of the dataset")
    dataset_type: str = Field(..., description="Type of the dataset")
    description: Optional[str] = Field(None, description="Description of the dataset")
    schema: Optional[Dict[str, Any]] = Field(None, description="Dataset schema")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Dataset metadata")
    owner: Optional[str] = Field(None, description="Dataset owner")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant datasets")


class GetDataLineageRequest(BaseModel):
    """Request to get data lineage."""
    data_id: str = Field(..., description="ID of the data item")
    lineage_type: Optional[DataLineageType] = Field(None, description="Type of lineage to retrieve")
    depth: Optional[int] = Field(1, description="Depth of lineage traversal")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


class ApplyDataPolicyRequest(BaseModel):
    """Request to apply data governance policy."""
    dataset_id: str = Field(..., description="ID of the dataset")
    policy_type: DataPolicyType = Field(..., description="Type of policy to apply")
    policy_config: Dict[str, Any] = Field(..., description="Policy configuration")
    effective_date: Optional[str] = Field(None, description="When the policy becomes effective")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant policies")


class GetStorageMetricsRequest(BaseModel):
    """Request to get storage and data metrics."""
    dataset_ids: Optional[List[str]] = Field(None, description="Specific dataset IDs (all if None)")
    include_lineage: Optional[bool] = Field(False, description="Include lineage metrics")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant access")


class ArchiveDatasetRequest(BaseModel):
    """Request to archive a dataset."""
    data_id: str = Field(..., description="ID of the dataset to archive")
    archive_reason: Optional[str] = Field("routine_archival", description="Reason for archiving")
    retention_period_days: Optional[int] = Field(365, description="Retention period in days")
    tenant_id: Optional[str] = Field(None, description="Tenant ID for multi-tenant archiving")


# Response Models
class RegisterDatasetResponse(BaseModel):
    """Response for dataset registration."""
    success: bool = Field(..., description="Dataset registration success status")
    dataset_id: Optional[str] = Field(None, description="Registered dataset ID")
    dataset_name: Optional[str] = Field(None, description="Dataset name")
    dataset_status: Optional[DataStatus] = Field(None, description="Initial dataset status")
    registered_at: Optional[str] = Field(None, description="Registration timestamp")
    message: str = Field(..., description="Response message")


class GetDataLineageResponse(BaseModel):
    """Response for data lineage retrieval."""
    success: bool = Field(..., description="Lineage retrieval success status")
    data_id: Optional[str] = Field(None, description="Data item ID")
    lineage_type: Optional[DataLineageType] = Field(None, description="Type of lineage retrieved")
    lineage_chain: Optional[List[Dict[str, Any]]] = Field(None, description="Lineage chain")
    lineage_depth: Optional[int] = Field(None, description="Depth of lineage retrieved")
    retrieved_at: Optional[str] = Field(None, description="Retrieval timestamp")
    message: str = Field(..., description="Response message")


class ApplyDataPolicyResponse(BaseModel):
    """Response for data policy application."""
    success: bool = Field(..., description="Policy application success status")
    dataset_id: Optional[str] = Field(None, description="Dataset ID")
    policy_type: Optional[DataPolicyType] = Field(None, description="Applied policy type")
    policy_id: Optional[str] = Field(None, description="Applied policy ID")
    effective_date: Optional[str] = Field(None, description="Policy effective date")
    applied_at: Optional[str] = Field(None, description="Application timestamp")
    message: str = Field(..., description="Response message")


class GetStorageMetricsResponse(BaseModel):
    """Response for storage metrics."""
    success: bool = Field(..., description="Metrics retrieval success status")
    total_files: Optional[int] = Field(None, description="Total number of files")
    total_size_bytes: Optional[int] = Field(None, description="Total storage size in bytes")
    active_datasets: Optional[int] = Field(None, description="Number of active datasets")
    archived_datasets: Optional[int] = Field(None, description="Number of archived datasets")
    lineage_metrics: Optional[Dict[str, Any]] = Field(None, description="Lineage metrics if requested")
    retrieved_at: Optional[str] = Field(None, description="Retrieval timestamp")
    message: str = Field(..., description="Response message")


class ArchiveDatasetResponse(BaseModel):
    """Response for dataset archiving."""
    success: bool = Field(..., description="Dataset archiving success status")
    data_id: Optional[str] = Field(None, description="Archived dataset ID")
    archive_id: Optional[str] = Field(None, description="Archive operation ID")
    archive_reason: Optional[str] = Field(None, description="Archive reason")
    retention_period_days: Optional[int] = Field(None, description="Retention period")
    archived_at: Optional[str] = Field(None, description="Archiving timestamp")
    message: str = Field(..., description="Response message")


# Interface Definition
class IDataSteward:
    """
    Data Steward Interface

    Defines the contracts for Data Steward service operations.
    This interface matches the existing DataStewardService APIs.
    """

    # Data Catalog Management
    async def register_dataset(self, request: RegisterDatasetRequest) -> RegisterDatasetResponse:
        """Register a new dataset in the catalog."""
        pass

    # Data Lineage
    async def get_data_lineage(self, request: GetDataLineageRequest) -> GetDataLineageResponse:
        """Get data lineage for a dataset."""
        pass

    # Data Governance
    async def apply_data_policy(self, request: ApplyDataPolicyRequest) -> ApplyDataPolicyResponse:
        """Apply data governance policy."""
        pass

    # Storage Management
    async def get_storage_metrics(self, request: GetStorageMetricsRequest) -> GetStorageMetricsResponse:
        """Get storage and data metrics."""
        pass

    # Data Lifecycle
    async def archive_dataset(self, request: ArchiveDatasetRequest) -> ArchiveDatasetResponse:
        """Archive a dataset."""
        pass























