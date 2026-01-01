#!/usr/bin/env python3
"""
Knowledge Governance Protocol - Abstraction Contract Layer

Protocol defining knowledge governance and metadata management operations.
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define the contract for knowledge governance operations
HOW (Infrastructure Implementation): I specify the interface for governance and metadata management
"""

from typing import Dict, Any, List, Optional, Protocol, Union
from datetime import datetime
from enum import Enum

class GovernanceLevel(Enum):
    """Governance level enumeration."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

class MetadataStatus(Enum):
    """Metadata status enumeration."""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"

class PolicyType(Enum):
    """Policy type enumeration."""
    ACCESS_CONTROL = "access_control"
    DATA_QUALITY = "data_quality"
    RETENTION = "retention"
    CLASSIFICATION = "classification"
    COMPLIANCE = "compliance"

class KnowledgeGovernanceProtocol(Protocol):
    """
    Protocol for knowledge governance operations.
    
    Defines the interface for governance policies, metadata management,
    and compliance operations across knowledge assets.
    """
    
    # ============================================================================
    # POLICY MANAGEMENT
    # ============================================================================
    
    async def create_governance_policy(self, 
                                     policy_name: str,
                                     policy_type: PolicyType,
                                     policy_data: Dict[str, Any],
                                     description: Optional[str] = None) -> str:
        """
        Create a governance policy.
        
        Args:
            policy_name: Name of the policy
            policy_type: Type of policy
            policy_data: Policy configuration data
            description: Optional policy description
            
        Returns:
            Policy ID
        """
        ...
    
    async def update_governance_policy(self, 
                                     policy_id: str,
                                     policy_data: Dict[str, Any]) -> bool:
        """
        Update a governance policy.
        
        Args:
            policy_id: ID of the policy to update
            policy_data: Updated policy data
            
        Returns:
            Success status
        """
        ...
    
    async def delete_governance_policy(self, 
                                     policy_id: str) -> bool:
        """
        Delete a governance policy.
        
        Args:
            policy_id: ID of the policy to delete
            
        Returns:
            Success status
        """
        ...
    
    async def get_governance_policies(self, 
                                    policy_type: Optional[PolicyType] = None,
                                    status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get governance policies.
        
        Args:
            policy_type: Optional policy type filter
            status: Optional status filter
            
        Returns:
            List of governance policies
        """
        ...
    
    # ============================================================================
    # POLICY APPLICATION
    # ============================================================================
    
    async def apply_policy_to_asset(self, 
                                  asset_id: str,
                                  policy_id: str,
                                  effective_date: Optional[datetime] = None) -> bool:
        """
        Apply a governance policy to a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            policy_id: ID of the governance policy
            effective_date: Optional effective date
            
        Returns:
            Success status
        """
        ...
    
    async def remove_policy_from_asset(self, 
                                     asset_id: str,
                                     policy_id: str) -> bool:
        """
        Remove a governance policy from a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            policy_id: ID of the governance policy
            
        Returns:
            Success status
        """
        ...
    
    async def get_asset_policies(self, 
                               asset_id: str) -> List[Dict[str, Any]]:
        """
        Get policies applied to a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            
        Returns:
            List of applied policies
        """
        ...
    
    # ============================================================================
    # METADATA MANAGEMENT
    # ============================================================================
    
    async def create_asset_metadata(self, 
                                  asset_id: str,
                                  metadata: Dict[str, Any],
                                  governance_level: GovernanceLevel = GovernanceLevel.INTERNAL) -> bool:
        """
        Create metadata for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            metadata: Metadata to create
            governance_level: Governance level for the asset
            
        Returns:
            Success status
        """
        ...
    
    async def update_asset_metadata(self, 
                                   asset_id: str,
                                   metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            metadata: Updated metadata
            
        Returns:
            Success status
        """
        ...
    
    async def get_asset_metadata(self, 
                               asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            
        Returns:
            Asset metadata or None
        """
        ...
    
    async def delete_asset_metadata(self, 
                                   asset_id: str) -> bool:
        """
        Delete metadata for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            
        Returns:
            Success status
        """
        ...
    
    # ============================================================================
    # SEMANTIC TAGGING
    # ============================================================================
    
    async def add_semantic_tags(self, 
                              asset_id: str,
                              tags: List[str],
                              confidence_scores: Optional[List[float]] = None,
                              tag_source: Optional[str] = None) -> bool:
        """
        Add semantic tags to a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            tags: List of semantic tags
            confidence_scores: Confidence scores for tags
            tag_source: Source of the tags (manual, ai, system)
            
        Returns:
            Success status
        """
        ...
    
    async def update_semantic_tags(self, 
                                 asset_id: str,
                                 tags: List[str],
                                 confidence_scores: Optional[List[float]] = None) -> bool:
        """
        Update semantic tags for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            tags: Updated list of semantic tags
            confidence_scores: Updated confidence scores
            
        Returns:
            Success status
        """
        ...
    
    async def get_semantic_tags(self, 
                              asset_id: str) -> List[Dict[str, Any]]:
        """
        Get semantic tags for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            
        Returns:
            List of semantic tags with metadata
        """
        ...
    
    async def search_by_semantic_tags(self, 
                                    tags: List[str],
                                    min_confidence: float = 0.5,
                                    tag_operator: str = "AND") -> List[Dict[str, Any]]:
        """
        Search knowledge assets by semantic tags.
        
        Args:
            tags: List of semantic tags to search
            min_confidence: Minimum confidence threshold
            tag_operator: Operator for tag combination (AND, OR)
            
        Returns:
            List of matching knowledge assets
        """
        ...
    
    # ============================================================================
    # CLASSIFICATION AND LABELING
    # ============================================================================
    
    async def classify_asset(self, 
                           asset_id: str,
                           classification: str,
                           confidence: float = 1.0,
                           classifier: Optional[str] = None) -> bool:
        """
        Classify a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            classification: Classification label
            confidence: Classification confidence
            classifier: Source of the classification
            
        Returns:
            Success status
        """
        ...
    
    async def get_asset_classification(self, 
                                     asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get classification for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            
        Returns:
            Asset classification or None
        """
        ...
    
    async def update_governance_level(self, 
                                    asset_id: str,
                                    governance_level: GovernanceLevel,
                                    reason: Optional[str] = None) -> bool:
        """
        Update governance level for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            governance_level: New governance level
            reason: Reason for the change
            
        Returns:
            Success status
        """
        ...
    
    # ============================================================================
    # COMPLIANCE AND AUDIT
    # ============================================================================
    
    async def check_compliance(self, 
                             asset_id: str,
                             compliance_rules: List[str]) -> Dict[str, Any]:
        """
        Check compliance for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            compliance_rules: List of compliance rules to check
            
        Returns:
            Compliance check results
        """
        ...
    
    async def get_compliance_report(self, 
                                   asset_ids: Optional[List[str]] = None,
                                   compliance_rules: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate compliance report for knowledge assets.
        
        Args:
            asset_ids: Optional list of asset IDs to check
            compliance_rules: Optional list of compliance rules
            
        Returns:
            Compliance report
        """
        ...
    
    async def audit_asset_access(self, 
                               asset_id: str,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Audit access to a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            start_date: Optional start date for audit
            end_date: Optional end date for audit
            
        Returns:
            List of access audit records
        """
        ...
    
    # ============================================================================
    # DATA QUALITY
    # ============================================================================
    
    async def assess_data_quality(self, 
                                asset_id: str,
                                quality_metrics: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Assess data quality for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            quality_metrics: Optional list of quality metrics to assess
            
        Returns:
            Data quality assessment results
        """
        ...
    
    async def get_quality_metrics(self, 
                                asset_id: str) -> Dict[str, Any]:
        """
        Get quality metrics for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            
        Returns:
            Quality metrics
        """
        ...
    
    async def update_quality_metrics(self, 
                                   asset_id: str,
                                   metrics: Dict[str, Any]) -> bool:
        """
        Update quality metrics for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            metrics: Quality metrics to update
            
        Returns:
            Success status
        """
        ...
    
    # ============================================================================
    # RETENTION AND LIFECYCLE
    # ============================================================================
    
    async def set_retention_policy(self, 
                                 asset_id: str,
                                 retention_period: int,
                                 retention_unit: str = "days",
                                 auto_archive: bool = True) -> bool:
        """
        Set retention policy for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            retention_period: Retention period
            retention_unit: Unit of retention period
            auto_archive: Whether to auto-archive after retention
            
        Returns:
            Success status
        """
        ...
    
    async def get_retention_status(self, 
                                 asset_id: str) -> Optional[Dict[str, Any]]:
        """
        Get retention status for a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            
        Returns:
            Retention status or None
        """
        ...
    
    async def archive_asset(self, 
                          asset_id: str,
                          archive_reason: Optional[str] = None) -> bool:
        """
        Archive a knowledge asset.
        
        Args:
            asset_id: ID of the knowledge asset
            archive_reason: Reason for archiving
            
        Returns:
            Success status
        """
        ...
    
    # ============================================================================
    # ANALYTICS AND REPORTING
    # ============================================================================
    
    async def get_governance_analytics(self, 
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get governance analytics.
        
        Args:
            start_date: Optional start date for analytics
            end_date: Optional end date for analytics
            
        Returns:
            Governance analytics
        """
        ...
    
    async def get_metadata_statistics(self) -> Dict[str, Any]:
        """
        Get metadata statistics.
        
        Returns:
            Metadata statistics
        """
        ...
    
    async def generate_governance_report(self, 
                                       report_type: str,
                                       parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate governance report.
        
        Args:
            report_type: Type of report to generate
            parameters: Optional report parameters
            
        Returns:
            Governance report
        """
        ...
    
    # ============================================================================
    # UTILITY OPERATIONS
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on governance services.
        
        Returns:
            Dict containing health status
        """
        ...
    
    async def get_governance_statistics(self) -> Dict[str, Any]:
        """
        Get governance statistics.
        
        Returns:
            Dict containing governance statistics
        """
        ...

