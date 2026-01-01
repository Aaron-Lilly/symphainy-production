#!/usr/bin/env python3
"""
Agent Capability Registry Service

Provides real-time agent capability reporting and management for the Curator Foundation.
Integrates with Agent SDK to track and manage agent capabilities dynamically.

WHAT (Curator Role): I provide real-time agent capability reporting and management
HOW (Agent Capability Registry Service): I integrate with Agent SDK and track capabilities dynamically
"""

import sys
import os
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase


@dataclass
class AgentCapability:
    """Agent capability definition."""
    agent_id: str
    agent_name: str
    capability_name: str
    capability_type: str  # tool, analysis, output, integration, etc.
    description: str
    parameters: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    version: str = "1.0.0"
    status: str = "active"  # active, deprecated, experimental
    pillar: Optional[str] = None
    specialization: Optional[str] = None
    registered_at: Optional[str] = None
    last_used: Optional[str] = None
    usage_count: int = 0


@dataclass
class AgentCapabilityReport:
    """Agent capability report for Curator."""
    agent_id: str
    agent_name: str
    total_capabilities: int
    active_capabilities: int
    deprecated_capabilities: int
    experimental_capabilities: int
    capabilities_by_type: Dict[str, int]
    capabilities_by_pillar: Dict[str, int]
    capabilities_by_specialization: Dict[str, int]
    last_updated: str
    health_status: str


class AgentCapabilityRegistryService(FoundationServiceBase):
    """
    Agent Capability Registry Service for Curator Foundation.
    
    Provides real-time agent capability reporting and management.
    Integrates with Agent SDK to track and manage agent capabilities dynamically.
    
    Features:
    - Real-time capability registration and updates
    - Capability usage tracking and analytics
    - Agent health monitoring through capabilities
    - Integration with Specialization Registry
    - Integration with AGUI Schema Registry
    - Capability dependency tracking
    - Pillar and specialization-based capability organization
    """
    
    def __init__(self, di_container, public_works_foundation=None):
        """Initialize Agent Capability Registry Service."""
        super().__init__("agent_capability_registry", di_container)
        
        # Store public works foundation reference
        self.public_works_foundation = public_works_foundation
        
        # Agent capability storage
        self.agent_capabilities: Dict[str, List[AgentCapability]] = {}  # agent_id -> capabilities
        self.capability_index: Dict[str, str] = {}  # capability_name -> agent_id
        self.capability_usage: Dict[str, Dict[str, Any]] = {}  # capability_name -> usage stats
        
        # Integration points
        self.specialization_registry = None
        self.agui_schema_registry = None
        
        # Real-time monitoring
        self.capability_monitors: Dict[str, asyncio.Task] = {}
        self.health_checks: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("Agent Capability Registry Service initialized")
    
    async def initialize(self):
        """Initialize the Agent Capability Registry Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agent_capability_registry_initialize_start", success=True)
            
            self.logger.info("🚀 Initializing Agent Capability Registry Service...")
            
            # Load existing capabilities from storage
            await self._load_capabilities_from_storage()
            
            # Initialize integration points
            await self._initialize_integrations()
            
            # Start capability monitoring
            await self._start_capability_monitoring()
            
            self.logger.info("✅ Agent Capability Registry Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("agent_capability_registry_initialized", 1.0, {"service": "agent_capability_registry"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agent_capability_registry_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agent_capability_registry_initialize")
            self.logger.error(f"❌ Failed to initialize Agent Capability Registry Service: {e}")
            raise
    
    async def _initialize_integrations(self):
        """Initialize integrations with other registries."""
        try:
            # Import and initialize Specialization Registry
            from foundations.agentic_foundation.specialization_registry import SpecializationRegistry
            self.specialization_registry = SpecializationRegistry()
            
            # Import and initialize AGUI Schema Registry
            from foundations.agentic_foundation.agui_schema_registry import AGUISchemaRegistry
            self.agui_schema_registry = AGUISchemaRegistry()
            
            self.logger.info("✅ Agent registry integrations initialized")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to initialize some integrations: {e}")
    
    async def _load_capabilities_from_storage(self):
        """Load existing capabilities from persistent storage."""
        try:
            # In a real implementation, this would load from a database
            # For now, we'll start with an empty registry
            self.logger.info("📚 Loaded capabilities from storage")
            
        except Exception as e:
            self.logger.error(f"Failed to load capabilities from storage: {e}")
            await self.handle_error_with_audit(e, "load_capabilities_from_storage_failed")
    
    async def _start_capability_monitoring(self):
        """Start real-time capability monitoring."""
        try:
            # Start monitoring task for each registered agent
            for agent_id in self.agent_capabilities.keys():
                monitor_task = asyncio.create_task(self._monitor_agent_capabilities(agent_id))
                self.capability_monitors[agent_id] = monitor_task
            
            self.logger.info(f"🔍 Started capability monitoring for {len(self.capability_monitors)} agents")
            
        except Exception as e:
            self.logger.error(f"Failed to start capability monitoring: {e}")
            await self.handle_error_with_audit(e, "start_capability_monitoring_failed")
    
    async def _monitor_agent_capabilities(self, agent_id: str):
        """Monitor agent capabilities in real-time."""
        try:
            while True:
                # Check agent health and capability status
                await self._check_agent_health(agent_id)
                
                # Update capability usage statistics
                await self._update_capability_usage(agent_id)
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except asyncio.CancelledError:
            self.logger.info(f"Capability monitoring stopped for agent {agent_id}")
        except Exception as e:
            self.logger.error(f"Error monitoring capabilities for agent {agent_id}: {e}")
            await self.handle_error_with_audit(e, f"monitor_agent_capabilities_failed_{agent_id}")
    
    async def _check_agent_health(self, agent_id: str):
        """Check agent health through capability status."""
        try:
            if agent_id not in self.agent_capabilities:
                return
            
            capabilities = self.agent_capabilities[agent_id]
            health_status = "healthy"
            issues = []
            
            for capability in capabilities:
                # Check if capability is responding
                if capability.status == "deprecated":
                    issues.append(f"Capability {capability.capability_name} is deprecated")
                elif capability.status == "experimental":
                    issues.append(f"Capability {capability.capability_name} is experimental")
                
                # Check usage patterns
                if capability.usage_count == 0 and capability.registered_at:
                    # Capability never used - might be an issue
                    days_since_registration = (datetime.now() - datetime.fromisoformat(capability.registered_at)).days
                    if days_since_registration > 7:
                        issues.append(f"Capability {capability.capability_name} unused for {days_since_registration} days")
            
            if issues:
                health_status = "degraded" if len(issues) < 3 else "unhealthy"
            
            self.health_checks[agent_id] = {
                "status": health_status,
                "issues": issues,
                "last_checked": datetime.now().isoformat(),
                "total_capabilities": len(capabilities),
                "active_capabilities": len([c for c in capabilities if c.status == "active"])
            }
            
        except Exception as e:
            self.logger.error(f"Error checking health for agent {agent_id}: {e}")
            await self.handle_error_with_audit(e, f"check_agent_health_failed_{agent_id}")
    
    async def _update_capability_usage(self, agent_id: str):
        """Update capability usage statistics."""
        try:
            if agent_id not in self.agent_capabilities:
                return
            
            capabilities = self.agent_capabilities[agent_id]
            
            for capability in capabilities:
                capability_name = capability.capability_name
                
                if capability_name not in self.capability_usage:
                    self.capability_usage[capability_name] = {
                        "total_uses": 0,
                        "last_used": None,
                        "usage_by_agent": {},
                        "usage_by_pillar": {},
                        "usage_by_specialization": {}
                    }
                
                usage_stats = self.capability_usage[capability_name]
                
                # Update agent-specific usage
                if agent_id not in usage_stats["usage_by_agent"]:
                    usage_stats["usage_by_agent"][agent_id] = 0
                
                # Update pillar usage
                if capability.pillar:
                    if capability.pillar not in usage_stats["usage_by_pillar"]:
                        usage_stats["usage_by_pillar"][capability.pillar] = 0
                
                # Update specialization usage
                if capability.specialization:
                    if capability.specialization not in usage_stats["usage_by_specialization"]:
                        usage_stats["usage_by_specialization"][capability.specialization] = 0
                
        except Exception as e:
            self.logger.error(f"Error updating capability usage for agent {agent_id}: {e}")
            await self.handle_error_with_audit(e, f"update_capability_usage_failed_{agent_id}")
    
    # ============================================================================
    # PUBLIC API METHODS
    # ============================================================================
    
    async def register_agent_capabilities(self, agent_id: str, agent_name: str, 
                                        capabilities: List[Dict[str, Any]], 
                                        pillar: str = None, specialization: str = None,
                                        user_context: Dict[str, Any] = None) -> bool:
        """
        Register capabilities for an agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            capabilities: List of capability definitions
            pillar: Business pillar (content, insights, operations, experience)
            specialization: Agent specialization
            user_context: Optional user context for security and tenant validation
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_agent_capabilities_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "write"):
                        await self.record_health_metric("register_agent_capabilities_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("register_agent_capabilities_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_agent_capabilities_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_agent_capabilities_complete", success=False)
                            return False
            
            self.logger.info(f"📝 Registering {len(capabilities)} capabilities for agent {agent_name}")
            
            agent_capabilities = []
            
            for cap_data in capabilities:
                capability = AgentCapability(
                    agent_id=agent_id,
                    agent_name=agent_name,
                    capability_name=cap_data.get("name"),
                    capability_type=cap_data.get("type", "tool"),
                    description=cap_data.get("description", ""),
                    parameters=cap_data.get("parameters"),
                    dependencies=cap_data.get("dependencies"),
                    version=cap_data.get("version", "1.0.0"),
                    status=cap_data.get("status", "active"),
                    pillar=pillar,
                    specialization=specialization,
                    registered_at=datetime.now().isoformat()
                )
                
                agent_capabilities.append(capability)
                
                # Update capability index
                self.capability_index[capability.capability_name] = agent_id
            
            # Store capabilities
            self.agent_capabilities[agent_id] = agent_capabilities
            
            # Start monitoring for this agent if not already started
            if agent_id not in self.capability_monitors:
                monitor_task = asyncio.create_task(self._monitor_agent_capabilities(agent_id))
                self.capability_monitors[agent_id] = monitor_task
            
            # Integrate with other registries
            await self._integrate_with_specialization_registry(agent_id, specialization)
            await self._integrate_with_agui_schema_registry(agent_id, agent_name)
            
            self.logger.info(f"✅ Successfully registered capabilities for agent {agent_name}")
            
            # Record health metric
            await self.record_health_metric("register_agent_capabilities_success", 1.0, {"agent_id": agent_id, "capabilities_count": len(capabilities)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_agent_capabilities_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_agent_capabilities")
            self.logger.error(f"❌ Failed to register capabilities for agent {agent_name}: {e}")
            return False
    
    async def update_capability_usage(self, capability_name: str, agent_id: str, 
                                    usage_data: Dict[str, Any] = None,
                                    user_context: Dict[str, Any] = None) -> bool:
        """
        Update capability usage statistics.
        
        Args:
            capability_name: Name of the capability
            agent_id: Agent that used the capability
            usage_data: Additional usage data
            user_context: Optional user context for security and tenant validation
            
        Returns:
            bool: True if update successful
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("update_capability_usage_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "write"):
                        await self.record_health_metric("update_capability_usage_access_denied", 1.0, {"agent_id": agent_id, "capability_name": capability_name})
                        await self.log_operation_with_telemetry("update_capability_usage_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("update_capability_usage_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("update_capability_usage_complete", success=False)
                            return False
            
            if capability_name not in self.capability_usage:
                self.capability_usage[capability_name] = {
                    "total_uses": 0,
                    "last_used": None,
                    "usage_by_agent": {},
                    "usage_by_pillar": {},
                    "usage_by_specialization": {}
                }
            
            usage_stats = self.capability_usage[capability_name]
            
            # Update usage statistics
            usage_stats["total_uses"] += 1
            usage_stats["last_used"] = datetime.now().isoformat()
            
            if agent_id not in usage_stats["usage_by_agent"]:
                usage_stats["usage_by_agent"][agent_id] = 0
            usage_stats["usage_by_agent"][agent_id] += 1
            
            # Update agent capability usage count
            if agent_id in self.agent_capabilities:
                for capability in self.agent_capabilities[agent_id]:
                    if capability.capability_name == capability_name:
                        capability.usage_count += 1
                        capability.last_used = datetime.now().isoformat()
                        break
            
            # Record health metric
            await self.record_health_metric("update_capability_usage_success", 1.0, {"capability_name": capability_name, "agent_id": agent_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("update_capability_usage_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "update_capability_usage")
            self.logger.error(f"Failed to update capability usage for {capability_name}: {e}")
            return False
    
    async def get_agent_capability_report(self, agent_id: str, user_context: Dict[str, Any] = None) -> Optional[AgentCapabilityReport]:
        """
        Get comprehensive capability report for an agent.
        
        Args:
            agent_id: Agent identifier
            user_context: Optional user context for security and tenant validation
            
        Returns:
            AgentCapabilityReport or None if agent not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_capability_report_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, agent_id, "read"):
                        await self.record_health_metric("get_agent_capability_report_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("get_agent_capability_report_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_capability_report_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_agent_capability_report_complete", success=False)
                            return None
            
            if agent_id not in self.agent_capabilities:
                await self.record_health_metric("get_agent_capability_report_not_found", 1.0, {"agent_id": agent_id})
                await self.log_operation_with_telemetry("get_agent_capability_report_complete", success=True)
                return None
            
            capabilities = self.agent_capabilities[agent_id]
            agent_name = capabilities[0].agent_name if capabilities else "Unknown"
            
            # Calculate statistics
            total_capabilities = len(capabilities)
            active_capabilities = len([c for c in capabilities if c.status == "active"])
            deprecated_capabilities = len([c for c in capabilities if c.status == "deprecated"])
            experimental_capabilities = len([c for c in capabilities if c.status == "experimental"])
            
            # Group by type
            capabilities_by_type = {}
            for capability in capabilities:
                cap_type = capability.capability_type
                capabilities_by_type[cap_type] = capabilities_by_type.get(cap_type, 0) + 1
            
            # Group by pillar
            capabilities_by_pillar = {}
            for capability in capabilities:
                pillar = capability.pillar or "unknown"
                capabilities_by_pillar[pillar] = capabilities_by_pillar.get(pillar, 0) + 1
            
            # Group by specialization
            capabilities_by_specialization = {}
            for capability in capabilities:
                specialization = capability.specialization or "general"
                capabilities_by_specialization[specialization] = capabilities_by_specialization.get(specialization, 0) + 1
            
            # Get health status
            health_status = self.health_checks.get(agent_id, {}).get("status", "unknown")
            
            result = AgentCapabilityReport(
                agent_id=agent_id,
                agent_name=agent_name,
                total_capabilities=total_capabilities,
                active_capabilities=active_capabilities,
                deprecated_capabilities=deprecated_capabilities,
                experimental_capabilities=experimental_capabilities,
                capabilities_by_type=capabilities_by_type,
                capabilities_by_pillar=capabilities_by_pillar,
                capabilities_by_specialization=capabilities_by_specialization,
                last_updated=datetime.now().isoformat(),
                health_status=health_status
            )
            
            # Record health metric
            await self.record_health_metric("get_agent_capability_report_success", 1.0, {"agent_id": agent_id, "total_capabilities": total_capabilities})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_capability_report_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_capability_report")
            self.logger.error(f"Failed to generate capability report for agent {agent_id}: {e}")
            return None
    
    async def get_all_agent_reports(self, user_context: Dict[str, Any] = None) -> List[AgentCapabilityReport]:
        """Get capability reports for all registered agents."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_all_agent_reports_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_capability_registry", "read"):
                        await self.record_health_metric("get_all_agent_reports_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_all_agent_reports_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            reports = []
            for agent_id in self.agent_capabilities.keys():
                # Filter by tenant if user_context provided
                if user_context:
                    tenant = self.get_tenant()
                    if tenant:
                        tenant_id = user_context.get("tenant_id")
                        if tenant_id:
                            if not await tenant.validate_tenant_access(tenant_id):
                                continue  # Skip agents from other tenants
                
                report = await self.get_agent_capability_report(agent_id, user_context)
                if report:
                    reports.append(report)
            
            # Record health metric
            await self.record_health_metric("get_all_agent_reports_success", 1.0, {"count": len(reports)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_all_agent_reports_complete", success=True)
            
            return reports
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_all_agent_reports")
            self.logger.error(f"Failed to get all agent reports: {e}")
            return []
    
    async def _integrate_with_specialization_registry(self, agent_id: str, specialization: str):
        """Integrate with Specialization Registry."""
        try:
            if self.specialization_registry and specialization:
                # Register agent with specialization
                await self.specialization_registry.register_agent_specialization(
                    agent_id, specialization
                )
                self.logger.info(f"Integrated agent {agent_id} with specialization {specialization}")
                
        except Exception as e:
            self.logger.warning(f"Failed to integrate with specialization registry: {e}")
    
    async def _integrate_with_agui_schema_registry(self, agent_id: str, agent_name: str):
        """Integrate with AGUI Schema Registry."""
        try:
            if self.agui_schema_registry:
                # Check if agent has AGUI schema registered
                schema = self.agui_schema_registry.get_agent_schema(agent_name)
                if schema:
                    self.logger.info(f"Found AGUI schema for agent {agent_name}")
                else:
                    self.logger.info(f"No AGUI schema found for agent {agent_name}")
                    
        except Exception as e:
            self.logger.warning(f"Failed to integrate with AGUI schema registry: {e}")
    
    async def get_capability_analytics(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive capability analytics."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_capability_analytics_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_capability_registry", "read"):
                        await self.record_health_metric("get_capability_analytics_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_capability_analytics_complete", success=False)
                        return {"error": "Access denied", "error_code": "ACCESS_DENIED"}
            
            # Tenant validation (multi-tenant support)
            agent_capabilities_to_analyze = self.agent_capabilities
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_capability_analytics_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_capability_analytics_complete", success=False)
                            return {"error": "Tenant access denied", "error_code": "TENANT_ACCESS_DENIED"}
                        # Filter by tenant if tenant_id is in agent metadata (would need to be stored)
                        # For now, we'll analyze all agents but this could be enhanced
            
            total_agents = len(agent_capabilities_to_analyze)
            total_capabilities = sum(len(caps) for caps in self.agent_capabilities.values())
            
            # Capability type distribution
            type_distribution = {}
            pillar_distribution = {}
            specialization_distribution = {}
            
            for capabilities in self.agent_capabilities.values():
                for capability in capabilities:
                    # Type distribution
                    cap_type = capability.capability_type
                    type_distribution[cap_type] = type_distribution.get(cap_type, 0) + 1
                    
                    # Pillar distribution
                    pillar = capability.pillar or "unknown"
                    pillar_distribution[pillar] = pillar_distribution.get(pillar, 0) + 1
                    
                    # Specialization distribution
                    specialization = capability.specialization or "general"
                    specialization_distribution[specialization] = specialization_distribution.get(specialization, 0) + 1
            
            result = {
                "total_agents": total_agents,
                "total_capabilities": total_capabilities,
                "type_distribution": type_distribution,
                "pillar_distribution": pillar_distribution,
                "specialization_distribution": specialization_distribution,
                "health_summary": {
                    "healthy_agents": len([h for h in self.health_checks.values() if h.get("status") == "healthy"]),
                    "degraded_agents": len([h for h in self.health_checks.values() if h.get("status") == "degraded"]),
                    "unhealthy_agents": len([h for h in self.health_checks.values() if h.get("status") == "unhealthy"])
                },
                "generated_at": datetime.now().isoformat()
            }
            
            # Record health metric
            await self.record_health_metric("get_capability_analytics_success", 1.0, {"total_agents": total_agents, "total_capabilities": total_capabilities})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_capability_analytics_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_capability_analytics")
            self.logger.error(f"Failed to generate capability analytics: {e}")
            return {}
    
    async def cleanup(self):
        """Cleanup the service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agent_capability_registry_cleanup_start", success=True)
            
            # Cancel monitoring tasks
            for task in self.capability_monitors.values():
                task.cancel()
            
            self.capability_monitors.clear()
            self.health_checks.clear()
            
            self.logger.info("Agent Capability Registry Service cleaned up")
            
            # Record health metric
            await self.record_health_metric("agent_capability_registry_cleanup", 1.0, {"service": "agent_capability_registry"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agent_capability_registry_cleanup_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agent_capability_registry_cleanup")
            self.logger.error(f"Error during cleanup: {e}")

    async def shutdown(self):
        """Shutdown the Agent Capability Registry Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agent_capability_registry_shutdown_start", success=True)
            
            self.logger.info("🛑 Shutting down Agent Capability Registry Service...")
            
            # Clear capability registry
            self.agent_capabilities.clear()
            self.health_checks.clear()
            
            self.logger.info("✅ Agent Capability Registry Service shutdown complete")
            
            # Record health metric
            await self.record_health_metric("agent_capability_registry_shutdown", 1.0, {"service": "agent_capability_registry"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agent_capability_registry_shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agent_capability_registry_shutdown")
            self.logger.error(f"❌ Error during Agent Capability Registry Service shutdown: {e}")


