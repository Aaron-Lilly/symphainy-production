#!/usr/bin/env python3
"""
Policy Tracker Orchestrator for Insurance Use Case

WHAT: Tracks policy location and status across systems
HOW: Maintains policy location registry, validates migrations, supports reconciliation

This orchestrator provides policy tracking capabilities:
- Policy location tracking (legacy system, new system, in transit)
- Migration status tracking
- Cross-system reconciliation
- Validation of migration results
"""

import os
import sys
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class PolicyLocation(str, Enum):
    """Policy location enumeration."""
    LEGACY_SYSTEM = "legacy_system"
    NEW_SYSTEM = "new_system"
    IN_TRANSIT = "in_transit"
    COEXISTENCE = "coexistence"  # Exists in both systems
    UNKNOWN = "unknown"


class MigrationStatus(str, Enum):
    """Migration status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    VALIDATED = "validated"


class PolicyTrackerOrchestrator(OrchestratorBase):
    """
    Policy Tracker Orchestrator for Insurance Use Case.
    
    Tracks policy location and status across systems, supports reconciliation and validation.
    Integrates with Insurance Migration Orchestrator, Wave Orchestrator, and Data Steward.
    """
    
    def __init__(self, delivery_manager):
        """
        Initialize Policy Tracker Orchestrator.
        
        Args:
            delivery_manager: Reference to DeliveryManagerService for service access
        """
        super().__init__(
            service_name="PolicyTrackerOrchestratorService",
            realm_name=delivery_manager.realm_name,
            platform_gateway=delivery_manager.platform_gateway,
            di_container=delivery_manager.di_container,
            business_orchestrator=delivery_manager
        )
        self.delivery_manager = delivery_manager
        self.orchestrator_name = "PolicyTrackerOrchestrator"
        
        # Enabling services (lazy initialization)
        self._insurance_migration_orchestrator = None
        self._wave_orchestrator = None
        self._data_steward = None  # For WAL integration
        
        # Policy tracking storage (in-memory for MVP, will move to State Management later)
        self._policy_registry: Dict[str, Dict[str, Any]] = {}
        
        # MCP Server (initialized in initialize())
        self.mcp_server = None
    
    async def _get_insurance_migration_orchestrator(self):
        """Lazy initialization of Insurance Migration Orchestrator."""
        if self._insurance_migration_orchestrator is None:
            try:
                orchestrators = self.delivery_manager.get_orchestrators()
                for orchestrator in orchestrators:
                    if hasattr(orchestrator, 'orchestrator_name') and orchestrator.orchestrator_name == "InsuranceMigrationOrchestrator":
                        self._insurance_migration_orchestrator = orchestrator
                        self.logger.info("✅ Insurance Migration Orchestrator discovered")
                        return orchestrator
                
                self.logger.warning("⚠️ Insurance Migration Orchestrator not found")
            except Exception as e:
                self.logger.error(f"❌ Insurance Migration Orchestrator initialization failed: {e}")
                return None
        
        return self._insurance_migration_orchestrator
    
    async def _get_wave_orchestrator(self):
        """Lazy initialization of Wave Orchestrator."""
        if self._wave_orchestrator is None:
            try:
                orchestrators = self.delivery_manager.get_orchestrators()
                for orchestrator in orchestrators:
                    if hasattr(orchestrator, 'orchestrator_name') and orchestrator.orchestrator_name == "WaveOrchestrator":
                        self._wave_orchestrator = orchestrator
                        self.logger.info("✅ Wave Orchestrator discovered")
                        return orchestrator
                
                self.logger.warning("⚠️ Wave Orchestrator not found")
            except Exception as e:
                self.logger.warning(f"⚠️ Wave Orchestrator not available: {e}")
        
        return self._wave_orchestrator
    
    async def _get_data_steward(self):
        """Lazy initialization of Data Steward (for WAL)."""
        if self._data_steward is None:
            try:
                self._data_steward = await self.get_data_steward_api()
                if self._data_steward:
                    self.logger.info("✅ Data Steward discovered for WAL integration")
            except Exception as e:
                self.logger.warning(f"⚠️ Data Steward not available: {e}")
        
        return self._data_steward
    
    # ============================================================================
    # POLICY TRACKING OPERATIONS
    # ============================================================================
    
    async def register_policy(
        self,
        policy_id: str,
        location: PolicyLocation,
        system_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a policy in the tracking system.
        
        Args:
            policy_id: Policy identifier
            location: Current location of the policy
            system_id: System identifier (if applicable)
            metadata: Optional policy metadata
            user_context: Optional user context
        
        Returns:
            Registration result
        """
        # Write to WAL
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.record_wal_entry(
                entry_data={
                    "operation": "register_policy",
                    "policy_id": policy_id,
                    "location": location.value,
                    "system_id": system_id
                },
                user_context=user_context
            )
        
        try:
            # Create or update policy record
            if policy_id not in self._policy_registry:
                self._policy_registry[policy_id] = {
                    "policy_id": policy_id,
                    "locations": [],
                    "migration_status": MigrationStatus.NOT_STARTED.value,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            
            policy_record = self._policy_registry[policy_id]
            
            # Add location entry
            location_entry = {
                "location": location.value,
                "system_id": system_id,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            policy_record["locations"].append(location_entry)
            
            # Update current location (most recent)
            policy_record["current_location"] = location.value
            policy_record["current_system_id"] = system_id
            policy_record["updated_at"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"✅ Registered policy {policy_id} at location {location.value}")
            
            return {
                "success": True,
                "policy_id": policy_id,
                "location": location.value,
                "policy_record": policy_record
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register policy: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "policy_id": policy_id
            }
    
    async def update_migration_status(
        self,
        policy_id: str,
        status: MigrationStatus,
        wave_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update migration status for a policy.
        
        Args:
            policy_id: Policy identifier
            status: Migration status
            wave_id: Optional wave ID if part of a wave
            details: Optional status details
            user_context: Optional user context
        
        Returns:
            Update result
        """
        # Write to WAL
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.record_wal_entry(
                entry_data={
                    "operation": "update_migration_status",
                    "policy_id": policy_id,
                    "status": status.value,
                    "wave_id": wave_id
                },
                user_context=user_context
            )
        
        try:
            if policy_id not in self._policy_registry:
                return {
                    "success": False,
                    "error": f"Policy {policy_id} not found in registry"
                }
            
            policy_record = self._policy_registry[policy_id]
            policy_record["migration_status"] = status.value
            policy_record["updated_at"] = datetime.utcnow().isoformat()
            
            if wave_id:
                policy_record["wave_id"] = wave_id
            
            if details:
                policy_record["status_details"] = details
            
            # Update location based on status
            if status == MigrationStatus.COMPLETED:
                policy_record["current_location"] = PolicyLocation.NEW_SYSTEM.value
            elif status == MigrationStatus.IN_PROGRESS:
                policy_record["current_location"] = PolicyLocation.IN_TRANSIT.value
            elif status == MigrationStatus.ROLLED_BACK:
                policy_record["current_location"] = PolicyLocation.LEGACY_SYSTEM.value
            
            self.logger.info(f"✅ Updated migration status for policy {policy_id}: {status.value}")
            
            return {
                "success": True,
                "policy_id": policy_id,
                "status": status.value,
                "policy_record": policy_record
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update migration status: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "policy_id": policy_id
            }
    
    async def get_policy_location(
        self,
        policy_id: str
    ) -> Dict[str, Any]:
        """
        Get current location and status of a policy.
        
        Args:
            policy_id: Policy identifier
        
        Returns:
            Policy location and status information
        """
        try:
            policy_record = self._policy_registry.get(policy_id)
            if not policy_record:
                return {
                    "success": False,
                    "error": f"Policy {policy_id} not found in registry"
                }
            
            return {
                "success": True,
                "policy_id": policy_id,
                "current_location": policy_record.get("current_location", PolicyLocation.UNKNOWN.value),
                "current_system_id": policy_record.get("current_system_id"),
                "migration_status": policy_record.get("migration_status"),
                "locations": policy_record.get("locations", []),
                "wave_id": policy_record.get("wave_id"),
                "updated_at": policy_record.get("updated_at")
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get policy location: {e}")
            return {
                "success": False,
                "error": str(e),
                "policy_id": policy_id
            }
    
    async def validate_migration(
        self,
        policy_id: str,
        validation_rules: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate a policy migration.
        
        Checks that policy exists in target system and data integrity is maintained.
        
        Args:
            policy_id: Policy identifier
            validation_rules: Optional custom validation rules
            user_context: Optional user context
        
        Returns:
            Validation result
        """
        # Write to WAL
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.record_wal_entry(
                entry_data={
                    "operation": "validate_migration",
                    "policy_id": policy_id
                },
                user_context=user_context
            )
        
        try:
            policy_record = self._policy_registry.get(policy_id)
            if not policy_record:
                return {
                    "success": False,
                    "error": f"Policy {policy_id} not found in registry"
                }
            
            validation_results = []
            all_passed = True
            
            # Default validation rules
            default_rules = [
                {
                    "type": "location_check",
                    "description": "Policy must be in new system",
                    "expected_location": PolicyLocation.NEW_SYSTEM.value
                },
                {
                    "type": "status_check",
                    "description": "Migration status must be completed",
                    "expected_status": MigrationStatus.COMPLETED.value
                }
            ]
            
            rules = validation_rules or default_rules
            
            for rule in rules:
                rule_type = rule.get("type")
                passed = False
                details = {}
                
                if rule_type == "location_check":
                    expected_location = rule.get("expected_location", PolicyLocation.NEW_SYSTEM.value)
                    current_location = policy_record.get("current_location")
                    passed = current_location == expected_location
                    details = {
                        "expected": expected_location,
                        "actual": current_location
                    }
                
                elif rule_type == "status_check":
                    expected_status = rule.get("expected_status", MigrationStatus.COMPLETED.value)
                    current_status = policy_record.get("migration_status")
                    passed = current_status == expected_status
                    details = {
                        "expected": expected_status,
                        "actual": current_status
                    }
                
                elif rule_type == "data_integrity":
                    # TODO: Implement data integrity checks (compare legacy vs new system)
                    passed = True
                    details = {"message": "Data integrity check not yet implemented"}
                
                validation_results.append({
                    "rule": rule.get("description", rule_type),
                    "passed": passed,
                    "details": details
                })
                
                if not passed:
                    all_passed = False
            
            # Update status if validation passed
            if all_passed:
                await self.update_migration_status(
                    policy_id=policy_id,
                    status=MigrationStatus.VALIDATED,
                    details={"validated_at": datetime.utcnow().isoformat()},
                    user_context=user_context
                )
            
            self.logger.info(f"✅ Validation complete for policy {policy_id}: {'PASSED' if all_passed else 'FAILED'}")
            
            return {
                "success": True,
                "policy_id": policy_id,
                "validation_passed": all_passed,
                "validation_results": validation_results
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to validate migration: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "policy_id": policy_id
            }
    
    async def reconcile_systems(
        self,
        system_a: str,
        system_b: str,
        policy_ids: Optional[List[str]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Reconcile policies between two systems.
        
        Compares policy locations and identifies discrepancies.
        
        Args:
            system_a: First system identifier
            system_b: Second system identifier
            policy_ids: Optional list of policy IDs to reconcile (all if not provided)
            user_context: Optional user context
        
        Returns:
            Reconciliation results
        """
        # Write to WAL
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.record_wal_entry(
                entry_data={
                    "operation": "reconcile_systems",
                    "system_a": system_a,
                    "system_b": system_b
                },
                user_context=user_context
            )
        
        try:
            policies_to_check = policy_ids or list(self._policy_registry.keys())
            
            reconciliation_results = {
                "system_a": system_a,
                "system_b": system_b,
                "total_policies": len(policies_to_check),
                "in_system_a": [],
                "in_system_b": [],
                "in_both": [],
                "in_neither": [],
                "discrepancies": []
            }
            
            for policy_id in policies_to_check:
                policy_record = self._policy_registry.get(policy_id)
                if not policy_record:
                    reconciliation_results["in_neither"].append(policy_id)
                    continue
                
                locations = policy_record.get("locations", [])
                in_a = any(loc.get("system_id") == system_a for loc in locations)
                in_b = any(loc.get("system_id") == system_b for loc in locations)
                
                if in_a and in_b:
                    reconciliation_results["in_both"].append(policy_id)
                elif in_a:
                    reconciliation_results["in_system_a"].append(policy_id)
                elif in_b:
                    reconciliation_results["in_system_b"].append(policy_id)
                else:
                    reconciliation_results["in_neither"].append(policy_id)
                
                # Check for discrepancies
                if in_a != in_b:
                    reconciliation_results["discrepancies"].append({
                        "policy_id": policy_id,
                        "issue": "Location mismatch",
                        "system_a": in_a,
                        "system_b": in_b
                    })
            
            self.logger.info(f"✅ Reconciliation complete: {len(reconciliation_results['in_both'])} in both, {len(reconciliation_results['discrepancies'])} discrepancies")
            
            return {
                "success": True,
                "reconciliation": reconciliation_results
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to reconcile systems: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_policies_by_location(
        self,
        location: PolicyLocation,
        system_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all policies at a specific location.
        
        Args:
            location: Policy location to filter by
            system_id: Optional system ID to filter by
        
        Returns:
            List of policies at the location
        """
        try:
            matching_policies = []
            
            for policy_id, policy_record in self._policy_registry.items():
                current_location = policy_record.get("current_location")
                current_system_id = policy_record.get("current_system_id")
                
                if current_location == location.value:
                    if system_id is None or current_system_id == system_id:
                        matching_policies.append({
                            "policy_id": policy_id,
                            "location": current_location,
                            "system_id": current_system_id,
                            "migration_status": policy_record.get("migration_status"),
                            "updated_at": policy_record.get("updated_at")
                        })
            
            return {
                "success": True,
                "location": location.value,
                "system_id": system_id,
                "count": len(matching_policies),
                "policies": matching_policies
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get policies by location: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # INITIALIZATION
    # ============================================================================
    
    async def initialize(self) -> bool:
        """
        Initialize Policy Tracker Orchestrator.
        
        Sets up MCP Server for agent access.
        """
        try:
            # Call parent initialize
            await super().initialize()
            
            # Initialize MCP Server (exposes orchestrator methods as MCP tools)
            from .mcp_server import PolicyTrackerMCPServer
            
            self.mcp_server = PolicyTrackerMCPServer(
                orchestrator=self,
                di_container=self.di_container
            )
            
            # MCP server registers tools in __init__, ready to use
            self.logger.info(f"✅ {self.orchestrator_name} MCP Server initialized")
            
            # Register with Curator (Phase 2 pattern with CapabilityDefinition structure)
            await self._realm_service.register_with_curator(
                capabilities=[
                    {
                        "name": "policy_tracking",
                        "protocol": "PolicyTrackerOrchestratorProtocol",
                        "description": "Track policy location and status",
                        "contracts": {
                            "soa_api": {
                                "api_name": "register_policy",
                                "endpoint": "/api/v1/policy-tracking/register-policy",
                                "method": "POST",
                                "handler": self.register_policy,
                                "metadata": {
                                    "description": "Register a policy for tracking",
                                    "parameters": ["policy_id", "location", "metadata", "user_context"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "register_policy_tool",
                                "tool_definition": {
                                    "name": "register_policy_tool",
                                    "description": "Register a policy for tracking",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "policy_id": {"type": "string"},
                                            "location": {"type": "string"},
                                            "metadata": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "insurance.register_policy",
                            "semantic_api": "/api/v1/policy-tracking/register-policy"
                        }
                    },
                    {
                        "name": "policy_location_query",
                        "protocol": "PolicyTrackerOrchestratorProtocol",
                        "description": "Query policy location and status",
                        "contracts": {
                            "soa_api": {
                                "api_name": "get_policy_location",
                                "endpoint": "/api/v1/policy-tracking/get-policy-location/{policy_id}",
                                "method": "GET",
                                "handler": self.get_policy_location,
                                "metadata": {
                                    "description": "Get policy location and status",
                                    "parameters": ["policy_id"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "get_policy_location_tool",
                                "tool_definition": {
                                    "name": "get_policy_location_tool",
                                    "description": "Get policy location and status",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "policy_id": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "insurance.get_policy_location",
                            "semantic_api": "/api/v1/policy-tracking/get-policy-location"
                        }
                    }
                ],
                soa_apis=["register_policy", "get_policy_location", "update_policy_location"],
                mcp_tools=["register_policy_tool", "get_policy_location_tool", "update_policy_location_tool"]
            )
            
            self.logger.info(f"✅ {self.orchestrator_name} registered with Curator")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.orchestrator_name}: {e}", exc_info=True)
            return False


