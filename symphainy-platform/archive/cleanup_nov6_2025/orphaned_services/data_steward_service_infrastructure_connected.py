#!/usr/bin/env python3
"""
Data Steward Service - Infrastructure-Connected Clean Rebuild

Updated clean rebuild that properly uses infrastructure abstractions:
- File metadata and files stored in Supabase
- Content metadata stored in ArangoDB
- Proper infrastructure mapping validation

WHAT (Smart City Role): I provide platform data governance with proper infrastructure integration
HOW (Service Implementation): I use SmartCityRoleBase with infrastructure abstractions
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

# Import ONLY our new base and protocol
from bases.smart_city_role_base import SmartCityRoleBase


class DataStewardServiceProtocol:
    """
    Protocol for Data Steward services with infrastructure integration.
    Defines the contract for data governance, policy management, and lineage tracking.
    """
    
    # Data Governance Methods
    async def create_content_policy(self, data_type: str, rules: Dict[str, Any]) -> str:
        """Create content policy for data type."""
        ...
    
    async def get_policy_for_content(self, content_type: str) -> Dict[str, Any]:
        """Get policy for content type."""
        ...
    
    # Lineage Tracking Methods
    async def record_lineage(self, lineage_data: Dict[str, Any]) -> str:
        """Record data lineage."""
        ...
    
    async def get_lineage(self, asset_id: str) -> Dict[str, Any]:
        """Get lineage for asset."""
        ...
    
    # Data Quality Methods
    async def validate_schema(self, schema_data: Dict[str, Any]) -> bool:
        """Validate data schema."""
        ...
    
    async def get_quality_metrics(self, asset_id: str) -> Dict[str, Any]:
        """Get quality metrics for asset."""
        ...
    
    # Compliance Methods
    async def enforce_compliance(self, asset_id: str, compliance_rules: List[str]) -> bool:
        """Enforce compliance rules for asset."""
        ...


class DataStewardService(SmartCityRoleBase, DataStewardServiceProtocol):
    """
    Data Steward Service - Infrastructure-Connected Clean Rebuild
    
    Clean implementation using ONLY our new base and protocol construct
    with proper infrastructure abstractions for Supabase and ArangoDB.
    
    WHAT (Smart City Role): I provide platform data governance with proper infrastructure integration
    HOW (Service Implementation): I use SmartCityRoleBase with infrastructure abstractions
    """
    
    def __init__(self, di_container: Any):
        """Initialize Data Steward Service with infrastructure integration."""
        super().__init__(
            service_name="DataStewardService",
            role_name="data_steward",
            di_container=di_container
        )
        
        # Infrastructure Abstractions (will be initialized in initialize())
        self.file_management_abstraction = None
        self.metadata_management_abstraction = None
        self.content_metadata_abstraction = None
        
        # Service State
        self.is_infrastructure_connected = False
        
        # Week 3 Enhancement: SOA API and MCP Integration
        self.soa_apis: Dict[str, Dict[str, Any]] = {}
        self.mcp_tools: Dict[str, Dict[str, Any]] = {}
        self.mcp_server_enabled = False
        
        # Logger is initialized by SmartCityRoleBase
        if self.logger:
            self.logger.info("✅ Data Steward Service (Infrastructure-Connected Clean Rebuild) initialized")
    
    async def initialize(self) -> bool:
        """Initialize Data Steward Service with infrastructure connections."""
        try:
            if self.logger:
                self.logger.info("🚀 Initializing Data Steward Service with infrastructure connections...")
            
            # Initialize infrastructure abstractions
            await self._initialize_infrastructure_connections()
            
            # Initialize SOA API exposure
            await self._initialize_soa_api_exposure()
            
            # Initialize MCP tool integration
            await self._initialize_mcp_tool_integration()
            
            # Register capabilities with curator
            capabilities = await self._register_data_steward_capabilities()
            await self.register_capability("DataStewardService", capabilities)
            
            self.is_initialized = True
            self.service_health = "healthy"
            
            if self.logger:
                self.logger.info("✅ Data Steward Service (Infrastructure-Connected) initialized successfully")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to initialize Data Steward Service: {str(e)}")
            self.service_health = "unhealthy"
            return False
    
    async def _initialize_infrastructure_connections(self):
        """Initialize connections to infrastructure abstractions."""
        try:
            if self.logger:
                self.logger.info("🔌 Connecting to infrastructure abstractions...")
            
            # Get Public Works Foundation
            public_works_foundation = self.get_public_works_foundation()
            if not public_works_foundation:
                raise Exception("Public Works Foundation not available")
            
            # Get File Management Abstraction (Supabase)
            self.file_management_abstraction = await public_works_foundation.get_abstraction("file_management")
            if not self.file_management_abstraction:
                raise Exception("File Management Abstraction not available")
            
            # Get Metadata Management Abstraction (Supabase)
            self.metadata_management_abstraction = await public_works_foundation.get_abstraction("metadata_management")
            if not self.metadata_management_abstraction:
                raise Exception("Metadata Management Abstraction not available")
            
            # Get Content Metadata Abstraction (ArangoDB)
            self.content_metadata_abstraction = await public_works_foundation.get_abstraction("content_metadata")
            if not self.content_metadata_abstraction:
                raise Exception("Content Metadata Abstraction not available")
            
            self.is_infrastructure_connected = True
            
            if self.logger:
                self.logger.info("✅ Infrastructure connections established:")
                self.logger.info("  - File Management (Supabase): ✅")
                self.logger.info("  - Metadata Management (Supabase): ✅")
                self.logger.info("  - Content Metadata (ArangoDB): ✅")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Failed to connect to infrastructure: {str(e)}")
            raise e
    
    async def _initialize_soa_api_exposure(self):
        """Initialize SOA API exposure for Smart City capabilities."""
        self.soa_apis = {
            "create_content_policy": {
                "endpoint": "/api/data-steward/policies",
                "method": "POST",
                "description": "Create content policy for data type",
                "parameters": ["data_type", "rules"]
            },
            "get_policy_for_content": {
                "endpoint": "/api/data-steward/policies/{content_type}",
                "method": "GET",
                "description": "Get policy for content type",
                "parameters": ["content_type"]
            },
            "record_lineage": {
                "endpoint": "/api/data-steward/lineage",
                "method": "POST",
                "description": "Record data lineage",
                "parameters": ["lineage_data"]
            },
            "get_lineage": {
                "endpoint": "/api/data-steward/lineage/{asset_id}",
                "method": "GET",
                "description": "Get lineage for asset",
                "parameters": ["asset_id"]
            },
            "validate_schema": {
                "endpoint": "/api/data-steward/validate-schema",
                "method": "POST",
                "description": "Validate data schema",
                "parameters": ["schema_data"]
            },
            "get_quality_metrics": {
                "endpoint": "/api/data-steward/quality/{asset_id}",
                "method": "GET",
                "description": "Get quality metrics for asset",
                "parameters": ["asset_id"]
            },
            "enforce_compliance": {
                "endpoint": "/api/data-steward/compliance/{asset_id}",
                "method": "POST",
                "description": "Enforce compliance rules for asset",
                "parameters": ["asset_id", "compliance_rules"]
            }
        }
    
    async def _initialize_mcp_tool_integration(self):
        """Initialize MCP tool integration for data governance."""
        self.mcp_tools = {
            "policy_manager": {
                "name": "policy_manager",
                "description": "Manage content policies and governance rules",
                "parameters": ["data_type", "rules", "action"]
            },
            "lineage_tracker": {
                "name": "lineage_tracker",
                "description": "Track and query data lineage",
                "parameters": ["asset_id", "lineage_data", "query_type"]
            },
            "schema_validator": {
                "name": "schema_validator",
                "description": "Validate data schemas and structures",
                "parameters": ["schema_data", "validation_rules"]
            },
            "compliance_enforcer": {
                "name": "compliance_enforcer",
                "description": "Enforce compliance rules and policies",
                "parameters": ["asset_id", "compliance_rules", "enforcement_level"]
            }
        }
    
    async def _register_data_steward_capabilities(self) -> Dict[str, Any]:
        """Register Data Steward Service capabilities."""
        return {
            "service_name": "DataStewardService",
            "service_type": "data_governance",
            "realm": "smart_city",
            "capabilities": [
                "content_policy_management",
                "data_lineage_tracking",
                "schema_validation",
                "quality_metrics",
                "compliance_enforcement",
                "infrastructure_integration"
            ],
            "infrastructure_connections": {
                "file_management": "Supabase",
                "metadata_management": "Supabase", 
                "content_metadata": "ArangoDB"
            },
            "soa_apis": self.soa_apis,
            "mcp_tools": self.mcp_tools,
            "status": "active",
            "infrastructure_connected": self.is_infrastructure_connected,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    # ============================================================================
    # DATA GOVERNANCE METHODS WITH INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def create_content_policy(self, data_type: str, rules: Dict[str, Any]) -> str:
        """Create content policy for data type using Supabase."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            policy_id = str(uuid.uuid4())
            policy_data = {
                "policy_id": policy_id,
                "data_type": data_type,
                "rules": rules,
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Store policy in Supabase via Metadata Management Abstraction
            success = await self.metadata_management_abstraction.create_metadata(
                metadata_id=policy_id,
                metadata=policy_data,
                metadata_type="content_policy"
            )
            
            if success:
                if self.logger:
                    self.logger.info(f"✅ Content policy created: {policy_id} for data_type: {data_type}")
                return policy_id
            else:
                raise Exception("Failed to create policy in Supabase")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error creating content policy: {str(e)}")
            raise e
    
    async def get_policy_for_content(self, content_type: str) -> Dict[str, Any]:
        """Get policy for content type from Supabase."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Query policy from Supabase via Metadata Management Abstraction
            policies = await self.metadata_management_abstraction.query_metadata(
                filters={"data_type": content_type, "metadata_type": "content_policy"},
                limit=1
            )
            
            if policies and len(policies) > 0:
                policy = policies[0]
                if self.logger:
                    self.logger.info(f"✅ Policy retrieved for content_type: {content_type}")
                return {
                    "policy_id": policy.get("policy_id"),
                    "data_type": policy.get("data_type"),
                    "rules": policy.get("rules"),
                    "created_at": policy.get("created_at"),
                    "status": policy.get("status")
                }
            else:
                return {
                    "policy_id": None,
                    "data_type": content_type,
                    "rules": {},
                    "message": "No policy found for content type"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting policy for content: {str(e)}")
            return {
                "policy_id": None,
                "data_type": content_type,
                "rules": {},
                "error": str(e)
            }
    
    # ============================================================================
    # LINEAGE TRACKING METHODS WITH INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def record_lineage(self, lineage_data: Dict[str, Any]) -> str:
        """Record data lineage using Supabase."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            lineage_id = str(uuid.uuid4())
            lineage_record = {
                "lineage_id": lineage_id,
                "asset_id": lineage_data.get("asset_id"),
                "source_asset_id": lineage_data.get("source_asset_id"),
                "transformation_type": lineage_data.get("transformation_type"),
                "transformation_details": lineage_data.get("transformation_details"),
                "created_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Store lineage in Supabase via Metadata Management Abstraction
            success = await self.metadata_management_abstraction.create_metadata(
                metadata_id=lineage_id,
                metadata=lineage_record,
                metadata_type="data_lineage"
            )
            
            if success:
                if self.logger:
                    self.logger.info(f"✅ Data lineage recorded: {lineage_id}")
                return lineage_id
            else:
                raise Exception("Failed to record lineage in Supabase")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error recording lineage: {str(e)}")
            raise e
    
    async def get_lineage(self, asset_id: str) -> Dict[str, Any]:
        """Get lineage for asset from Supabase."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Query lineage from Supabase via Metadata Management Abstraction
            lineage_records = await self.metadata_management_abstraction.query_metadata(
                filters={"asset_id": asset_id, "metadata_type": "data_lineage"},
                limit=100
            )
            
            if lineage_records:
                if self.logger:
                    self.logger.info(f"✅ Lineage retrieved for asset: {asset_id}")
                return {
                    "asset_id": asset_id,
                    "lineage_records": lineage_records,
                    "total_records": len(lineage_records),
                    "status": "success"
                }
            else:
                return {
                    "asset_id": asset_id,
                    "lineage_records": [],
                    "total_records": 0,
                    "message": "No lineage records found"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting lineage: {str(e)}")
            return {
                "asset_id": asset_id,
                "lineage_records": [],
                "total_records": 0,
                "error": str(e)
            }
    
    # ============================================================================
    # DATA QUALITY METHODS WITH INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def validate_schema(self, schema_data: Dict[str, Any]) -> bool:
        """Validate data schema using ArangoDB."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Store schema validation in ArangoDB via Content Metadata Abstraction
            validation_result = await self.content_metadata_abstraction.validate_content_schema(
                schema_data=schema_data
            )
            
            if validation_result.get("valid", False):
                if self.logger:
                    self.logger.info("✅ Schema validation passed")
                return True
            else:
                if self.logger:
                    self.logger.warning(f"⚠️ Schema validation failed: {validation_result.get('errors', [])}")
                return False
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error validating schema: {str(e)}")
            return False
    
    async def get_quality_metrics(self, asset_id: str) -> Dict[str, Any]:
        """Get quality metrics for asset from ArangoDB."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            # Query quality metrics from ArangoDB via Content Metadata Abstraction
            metrics = await self.content_metadata_abstraction.get_content_quality_metrics(
                content_id=asset_id
            )
            
            if metrics:
                if self.logger:
                    self.logger.info(f"✅ Quality metrics retrieved for asset: {asset_id}")
                return {
                    "asset_id": asset_id,
                    "quality_metrics": metrics,
                    "status": "success"
                }
            else:
                return {
                    "asset_id": asset_id,
                    "quality_metrics": {},
                    "message": "No quality metrics found"
                }
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting quality metrics: {str(e)}")
            return {
                "asset_id": asset_id,
                "quality_metrics": {},
                "error": str(e)
            }
    
    # ============================================================================
    # COMPLIANCE METHODS WITH INFRASTRUCTURE INTEGRATION
    # ============================================================================
    
    async def enforce_compliance(self, asset_id: str, compliance_rules: List[str]) -> bool:
        """Enforce compliance rules for asset using both Supabase and ArangoDB."""
        try:
            if not self.is_infrastructure_connected:
                raise Exception("Infrastructure not connected")
            
            compliance_results = []
            
            # Check compliance against policies in Supabase
            for rule in compliance_rules:
                # Get policy for the rule
                policy = await self.get_policy_for_content(rule)
                
                if policy.get("policy_id"):
                    # Check asset against policy
                    compliance_check = await self._check_asset_compliance(asset_id, policy)
                    compliance_results.append({
                        "rule": rule,
                        "compliant": compliance_check,
                        "policy_id": policy.get("policy_id")
                    })
                else:
                    compliance_results.append({
                        "rule": rule,
                        "compliant": False,
                        "error": "No policy found for rule"
                    })
            
            # Overall compliance status
            all_compliant = all(result.get("compliant", False) for result in compliance_results)
            
            if self.logger:
                self.logger.info(f"✅ Compliance check completed for asset: {asset_id}")
                self.logger.info(f"  - Rules checked: {len(compliance_rules)}")
                self.logger.info(f"  - All compliant: {all_compliant}")
            
            return all_compliant
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error enforcing compliance: {str(e)}")
            return False
    
    async def _check_asset_compliance(self, asset_id: str, policy: Dict[str, Any]) -> bool:
        """Check asset compliance against specific policy."""
        try:
            # This would involve checking the asset against the policy rules
            # For now, we'll simulate compliance checking
            rules = policy.get("rules", {})
            
            # Basic compliance check (placeholder logic)
            if rules.get("required_fields"):
                # Check if asset has required fields
                pass
            
            if rules.get("data_quality_threshold"):
                # Check data quality metrics
                pass
            
            # Return True for now (placeholder)
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error checking asset compliance: {str(e)}")
            return False
    
    # ============================================================================
    # INFRASTRUCTURE VALIDATION METHODS
    # ============================================================================
    
    async def validate_infrastructure_mapping(self) -> Dict[str, Any]:
        """Validate that infrastructure mapping is working correctly."""
        try:
            validation_results = {
                "file_management_supabase": False,
                "metadata_management_supabase": False,
                "content_metadata_arango": False,
                "overall_status": False
            }
            
            # Test File Management (Supabase)
            try:
                if self.file_management_abstraction:
                    # Test basic file operation
                    test_result = await self.file_management_abstraction.list_files({"limit": 1})
                    validation_results["file_management_supabase"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ File Management (Supabase) test failed: {str(e)}")
            
            # Test Metadata Management (Supabase)
            try:
                if self.metadata_management_abstraction:
                    # Test basic metadata operation
                    test_result = await self.metadata_management_abstraction.query_metadata({"limit": 1})
                    validation_results["metadata_management_supabase"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Metadata Management (Supabase) test failed: {str(e)}")
            
            # Test Content Metadata (ArangoDB)
            try:
                if self.content_metadata_abstraction:
                    # Test basic content metadata operation
                    test_result = await self.content_metadata_abstraction.list_content_metadata({"limit": 1})
                    validation_results["content_metadata_arango"] = True
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"⚠️ Content Metadata (ArangoDB) test failed: {str(e)}")
            
            # Overall status
            validation_results["overall_status"] = all([
                validation_results["file_management_supabase"],
                validation_results["metadata_management_supabase"],
                validation_results["content_metadata_arango"]
            ])
            
            if self.logger:
                self.logger.info("🔍 Infrastructure mapping validation completed:")
                self.logger.info(f"  - File Management (Supabase): {'✅' if validation_results['file_management_supabase'] else '❌'}")
                self.logger.info(f"  - Metadata Management (Supabase): {'✅' if validation_results['metadata_management_supabase'] else '❌'}")
                self.logger.info(f"  - Content Metadata (ArangoDB): {'✅' if validation_results['content_metadata_arango'] else '❌'}")
                self.logger.info(f"  - Overall Status: {'✅' if validation_results['overall_status'] else '❌'}")
            
            return validation_results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error validating infrastructure mapping: {str(e)}")
            return {
                "file_management_supabase": False,
                "metadata_management_supabase": False,
                "content_metadata_arango": False,
                "overall_status": False,
                "error": str(e)
            }
    
    async def get_service_capabilities(self) -> Dict[str, Any]:
        """Get service capabilities with infrastructure status."""
        try:
            return {
                "service_name": "DataStewardService",
                "service_type": "data_governance",
                "realm": "smart_city",
                "capabilities": [
                    "content_policy_management",
                    "data_lineage_tracking",
                    "schema_validation",
                    "quality_metrics",
                    "compliance_enforcement",
                    "infrastructure_integration"
                ],
                "infrastructure_connections": {
                    "file_management": "Supabase",
                    "metadata_management": "Supabase",
                    "content_metadata": "ArangoDB"
                },
                "infrastructure_status": {
                    "connected": self.is_infrastructure_connected,
                    "file_management_available": self.file_management_abstraction is not None,
                    "metadata_management_available": self.metadata_management_abstraction is not None,
                    "content_metadata_available": self.content_metadata_abstraction is not None
                },
                "soa_apis": self.soa_apis,
                "mcp_tools": self.mcp_tools,
                "status": "active",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error getting service capabilities: {str(e)}")
            return {
                "service_name": "DataStewardService",
                "error": str(e),
                "status": "error"
            }
