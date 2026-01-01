#!/usr/bin/env python3
"""
Service Mesh Metadata Reporter Service

Reports and aggregates service mesh policies from domains.
Domains OWN policies (load balancing, timeouts, circuit breakers), Curator REPORTS/aggregates.

WHAT (Service Role): I need to report and aggregate service mesh policies from domains
HOW (Service Implementation): I maintain a policy registry that aggregates domain-provided policies
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase

# Import utilities directly
from utilities import (
    ValidationUtility, SerializationUtility, ConfigurationUtility,
    HealthManagementUtility
)


class ServiceMeshMetadataReporterService(FoundationServiceBase):
    """
    Service Mesh Metadata Reporter Service - Policy reporting and aggregation
    
    Reports and aggregates service mesh policies from domains. Domains own
    policies (load balancing, timeouts, circuit breakers), Curator reports/aggregates.
    
    WHAT (Service Role): I need to report and aggregate service mesh policies from domains
    HOW (Service Implementation): I maintain a policy registry that aggregates domain-provided policies
    """
    
    def __init__(self, di_container, public_works_foundation=None):
        """Initialize Service Mesh Metadata Reporter Service."""
        super().__init__("service_mesh_metadata_reporter", di_container)
        
        # Store public works foundation reference
        self.public_works_foundation = public_works_foundation
        
        # Policy registry: service_name -> [policy_reports]
        # Each policy report includes source (domain) and policies
        self.policy_registry: Dict[str, List[Dict[str, Any]]] = {}
        
        self.logger.info("📋 Service Mesh Metadata Reporter Service initialized")
    
    async def initialize(self):
        """Initialize the Service Mesh Metadata Reporter Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("service_mesh_metadata_reporter_initialize_start", success=True)
            
            await super().initialize()
            self.logger.info("🚀 Initializing Service Mesh Metadata Reporter Service...")
            
            self.logger.info("✅ Service Mesh Metadata Reporter Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("service_mesh_metadata_reporter_initialized", 1.0, {"service": "service_mesh_metadata_reporter"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("service_mesh_metadata_reporter_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "service_mesh_metadata_reporter_initialize")
            raise
    
    async def report_service_mesh_policies(
        self,
        service_name: str,
        policies: Dict[str, Any],
        user_context: Dict[str, Any] = None
    ) -> bool:
        """
        Report service mesh policies (domain owns, Curator reports).
        
        Domains own their service mesh policies (load balancing, timeouts,
        circuit breakers). Curator aggregates and reports these policies
        for service mesh evolution (Consul Connect).
        
        Args:
            service_name: Name of the service
            policies: Policy metadata dictionary (domain-provided)
            user_context: Optional user context for security and tenant validation
        
        Policies format (domain-provided):
        {
            "source": "business_enablement_realm",  # Domain that owns this
            "reported_at": "...",
            "policies": {
                "load_balancing": "round_robin",  # Owned by domain
                "timeout": "30s",  # Owned by domain
                "circuit_breakers": {...},  # Owned by domain
                "traffic_splitting": [...],  # Owned by domain
                "intentions": [...]  # Owned by domain
            }
        }
        
        Returns:
            True if reporting successful, False otherwise
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "report_service_mesh_policies_start",
                success=True,
                details={"service_name": service_name}
            )
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "service_mesh_policies", "write"):
                        await self.record_health_metric("report_service_mesh_policies_access_denied", 1.0, {"service_name": service_name})
                        await self.log_operation_with_telemetry("report_service_mesh_policies_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("report_service_mesh_policies_tenant_denied", 1.0, {"service_name": service_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("report_service_mesh_policies_complete", success=False)
                            return False
            
            # Validate inputs
            if not service_name:
                raise ValueError("service_name is required")
            
            if not policies or not isinstance(policies, dict):
                raise ValueError("policies must be a dictionary")
            
            # Ensure source is set (domain attribution)
            if "source" not in policies:
                policies["source"] = "unknown_domain"
            
            # Add reporting timestamp
            policies["reported_at"] = datetime.utcnow().isoformat()
            policies["user_context"] = user_context
            
            # Initialize service entry if needed
            if service_name not in self.policy_registry:
                self.policy_registry[service_name] = []
            
            # Store policy report (domain owns, Curator reports)
            self.policy_registry[service_name].append(policies)
            
            self.logger.info(f"✅ Service mesh policies reported: {service_name} (source: {policies.get('source')})")
            
            # Record health metric
            await self.record_health_metric(
                "service_mesh_policies_reported",
                1.0,
                {"service_name": service_name, "source": policies.get("source")}
            )
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "report_service_mesh_policies_complete",
                success=True,
                details={"service_name": service_name}
            )
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(
                e,
                "report_service_mesh_policies",
                details={"service_name": service_name, "policies": policies}
            )
            return False
    
    async def get_service_mesh_policy_report(
        self,
        service_name: str
    ) -> Dict[str, Any]:
        """
        Aggregate service mesh policies from domains and report.
        
        Aggregates all policy reports for a service and returns a unified view.
        Used for service mesh configuration (Consul Connect).
        
        Args:
            service_name: Name of the service
        
        Returns:
            Aggregated policy report:
            {
                "service": service_name,
                "policies": {
                    "source": "domain_reported",
                    "aggregated_at": "...",
                    "load_balancing": "...",
                    "timeout": "...",
                    "circuit_breakers": [...],
                    "traffic_splitting": [...]
                }
            }
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry(
                "get_service_mesh_policy_report_start",
                success=True,
                details={"service_name": service_name}
            )
            
            if service_name not in self.policy_registry:
                return {
                    "service": service_name,
                    "policies": {
                        "source": "no_policies_reported",
                        "aggregated_at": datetime.utcnow().isoformat()
                    }
                }
            
            # Aggregate policies from all domain reports
            policy_reports = self.policy_registry[service_name]
            
            # Merge policies (latest wins for conflicts)
            aggregated_policies = {
                "source": "domain_reported",
                "aggregated_at": datetime.utcnow().isoformat(),
                "report_count": len(policy_reports)
            }
            
            # Aggregate each policy type
            for report in policy_reports:
                report_policies = report.get("policies", {})
                for policy_type, policy_value in report_policies.items():
                    # For now, use latest value (could be more sophisticated)
                    aggregated_policies[policy_type] = policy_value
            
            result = {
                "service": service_name,
                "policies": aggregated_policies
            }
            
            # Record success metric
            await self.record_health_metric("get_service_mesh_policy_report_success", 1.0, {"service_name": service_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry(
                "get_service_mesh_policy_report_complete",
                success=True,
                details={"service_name": service_name}
            )
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(
                e,
                "get_service_mesh_policy_report",
                details={"service_name": service_name}
            )
            return {
                "service": service_name,
                "policies": {
                    "source": "error",
                    "error": str(e)
                }
            }

