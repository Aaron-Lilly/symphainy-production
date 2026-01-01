#!/usr/bin/env python3
"""
Agent Specialization Management Service

Provides agent specialization registration and management for the Curator Foundation.
Integrates with Specialization Registry to manage agent specializations dynamically.

WHAT (Curator Role): I provide agent specialization registration and management
HOW (Agent Specialization Management Service): I integrate with Specialization Registry and manage specializations dynamically
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
class AgentSpecialization:
    """Agent specialization definition."""
    agent_id: str
    agent_name: str
    specialization_id: str
    specialization_name: str
    pillar: str  # content, insights, operations, experience
    description: str
    capabilities: List[str]
    system_prompt_template: str
    expertise_level: str  # beginner, intermediate, advanced, expert
    version: str = "1.0.0"
    status: str = "active"  # active, deprecated, experimental
    registered_at: Optional[str] = None
    last_updated: Optional[str] = None
    usage_count: int = 0
    success_rate: float = 0.0


@dataclass
class SpecializationAnalytics:
    """Specialization analytics for Curator."""
    specialization_id: str
    specialization_name: str
    pillar: str
    total_agents: int
    active_agents: int
    deprecated_agents: int
    experimental_agents: int
    average_success_rate: float
    total_usage_count: int
    capabilities_count: int
    last_updated: str


class AgentSpecializationManagementService(FoundationServiceBase):
    """
    Agent Specialization Management Service for Curator Foundation.
    
    Provides agent specialization registration and management.
    Integrates with Specialization Registry to manage agent specializations dynamically.
    
    Features:
    - Agent specialization registration and validation
    - Specialization analytics and reporting
    - Pillar-based specialization organization
    - Capability mapping and management
    - Success rate tracking and optimization
    - Integration with Specialization Registry
    - Specialization health monitoring
    """
    
    def __init__(self, di_container, public_works_foundation=None):
        """Initialize Agent Specialization Management Service."""
        super().__init__("agent_specialization_management", di_container)
        
        # Store public works foundation reference
        self.public_works_foundation = public_works_foundation
        
        # Agent specialization storage
        self.agent_specializations: Dict[str, AgentSpecialization] = {}  # agent_id -> specialization
        self.specialization_index: Dict[str, List[str]] = {}  # specialization_id -> agent_ids
        self.pillar_specializations: Dict[str, List[str]] = {}  # pillar -> specialization_ids
        
        # Analytics and monitoring
        self.specialization_analytics: Dict[str, Dict[str, Any]] = {}
        self.usage_tracking: Dict[str, Dict[str, Any]] = {}
        
        # Integration points
        self.specialization_registry = None
        
        self.logger.info("Agent Specialization Management Service initialized")
    
    async def initialize(self):
        """Initialize the Agent Specialization Management Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agent_specialization_management_initialize_start", success=True)
            
            self.logger.info("🚀 Initializing Agent Specialization Management Service...")
            
            # Load existing specializations from storage
            await self._load_specializations_from_storage()
            
            # Initialize integration points
            await self._initialize_integrations()
            
            # Load specializations from Specialization Registry
            await self._load_specializations_from_registry()
            
            # Start analytics monitoring
            await self._start_analytics_monitoring()
            
            self.logger.info("✅ Agent Specialization Management Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("agent_specialization_management_initialized", 1.0, {"service": "agent_specialization_management"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agent_specialization_management_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agent_specialization_management_initialize")
            self.logger.error(f"❌ Failed to initialize Agent Specialization Management Service: {e}")
            raise
    
    async def _initialize_integrations(self):
        """Initialize integrations with other registries."""
        try:
            # Import and initialize Specialization Registry
            from foundations.agentic_foundation.specialization_registry import SpecializationRegistry
            self.specialization_registry = SpecializationRegistry()
            
            self.logger.info("✅ Specialization registry integration initialized")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to initialize specialization registry integration: {e}")
    
    async def _load_specializations_from_storage(self):
        """Load existing specializations from persistent storage."""
        try:
            # In a real implementation, this would load from a database
            # For now, we'll start with an empty registry
            self.logger.info("📚 Loaded specializations from storage")
            
        except Exception as e:
            self.logger.error(f"Failed to load specializations from storage: {e}")
            await self.handle_error_with_audit(e, "load_specializations_from_storage_failed")
    
    async def _load_specializations_from_registry(self):
        """Load specializations from Specialization Registry."""
        try:
            if not self.specialization_registry:
                return
            
            # Get all specializations from the registry
            specializations = self.specialization_registry.get_all_specializations()
            
            for spec_id, spec_data in specializations.items():
                # Update pillar index
                pillar = spec_data.get("pillar", "general")
                if pillar not in self.pillar_specializations:
                    self.pillar_specializations[pillar] = []
                if spec_id not in self.pillar_specializations[pillar]:
                    self.pillar_specializations[pillar].append(spec_id)
                
                # Update specialization index
                if spec_id not in self.specialization_index:
                    self.specialization_index[spec_id] = []
            
            self.logger.info(f"📋 Loaded {len(specializations)} specializations from registry")
            
        except Exception as e:
            self.logger.error(f"Failed to load specializations from registry: {e}")
            await self.handle_error_with_audit(e, "load_specializations_from_registry_failed")
    
    async def _start_analytics_monitoring(self):
        """Start analytics monitoring for specializations."""
        try:
            # Start periodic analytics update
            asyncio.create_task(self._periodic_analytics_update())
            
            self.logger.info("📊 Started analytics monitoring")
            
        except Exception as e:
            self.logger.error(f"Failed to start analytics monitoring: {e}")
            await self.handle_error_with_audit(e, "start_analytics_monitoring_failed")
    
    async def _periodic_analytics_update(self):
        """Periodically update specialization analytics."""
        try:
            while True:
                await self._update_specialization_analytics()
                await asyncio.sleep(300)  # Update every 5 minutes
                
        except asyncio.CancelledError:
            self.logger.info("Analytics monitoring stopped")
        except Exception as e:
            self.logger.error(f"Error in periodic analytics update: {e}")
            await self.handle_error_with_audit(e, "periodic_analytics_update_failed")
    
    async def _update_specialization_analytics(self):
        """Update specialization analytics."""
        try:
            for spec_id in self.specialization_index.keys():
                agent_ids = self.specialization_index[spec_id]
                
                if not agent_ids:
                    continue
                
                # Get specialization data
                spec_data = None
                if self.specialization_registry:
                    spec_data = self.specialization_registry.get_specialization(spec_id)
                
                if not spec_data:
                    continue
                
                # Calculate analytics
                total_agents = len(agent_ids)
                active_agents = 0
                deprecated_agents = 0
                experimental_agents = 0
                total_usage = 0
                total_success_rate = 0.0
                capabilities_count = len(spec_data.get("capabilities", []))
                
                for agent_id in agent_ids:
                    if agent_id in self.agent_specializations:
                        specialization = self.agent_specializations[agent_id]
                        
                        if specialization.status == "active":
                            active_agents += 1
                        elif specialization.status == "deprecated":
                            deprecated_agents += 1
                        elif specialization.status == "experimental":
                            experimental_agents += 1
                        
                        total_usage += specialization.usage_count
                        total_success_rate += specialization.success_rate
                
                average_success_rate = total_success_rate / total_agents if total_agents > 0 else 0.0
                
                self.specialization_analytics[spec_id] = {
                    "specialization_id": spec_id,
                    "specialization_name": spec_data.get("name", spec_id),
                    "pillar": spec_data.get("pillar", "general"),
                    "total_agents": total_agents,
                    "active_agents": active_agents,
                    "deprecated_agents": deprecated_agents,
                    "experimental_agents": experimental_agents,
                    "average_success_rate": average_success_rate,
                    "total_usage_count": total_usage,
                    "capabilities_count": capabilities_count,
                    "last_updated": datetime.now().isoformat()
                }
            
            self.logger.debug("📊 Updated specialization analytics")
            
        except Exception as e:
            self.logger.error(f"Failed to update specialization analytics: {e}")
            await self.handle_error_with_audit(e, "update_specialization_analytics_failed")
    
    # ============================================================================
    # PUBLIC API METHODS
    # ============================================================================
    
    async def register_agent_specialization(self, agent_id: str, agent_name: str, 
                                          specialization_config: Dict[str, Any], user_context: Dict[str, Any] = None) -> bool:
        """
        Register an agent with a specialization.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            specialization_config: Specialization configuration
            user_context: Optional user context for security and tenant validation
            
        Returns:
            bool: True if registration successful
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("register_agent_specialization_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_specialization", "write"):
                        await self.record_health_metric("register_agent_specialization_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("register_agent_specialization_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("register_agent_specialization_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("register_agent_specialization_complete", success=False)
                            return False
            
            specialization_id = specialization_config.get("id")
            if not specialization_id:
                self.logger.error(f"No specialization ID provided for agent {agent_name}")
                await self.record_health_metric("register_agent_specialization_error", 1.0, {"agent_id": agent_id, "error": "no_specialization_id"})
                await self.log_operation_with_telemetry("register_agent_specialization_complete", success=False)
                return False
            
            # Validate specialization exists in registry
            if self.specialization_registry:
                spec_data = self.specialization_registry.get_specialization(specialization_id)
                if not spec_data:
                    self.logger.error(f"Specialization {specialization_id} not found in registry")
                    await self.record_health_metric("register_agent_specialization_error", 1.0, {"agent_id": agent_id, "error": "specialization_not_found"})
                    await self.log_operation_with_telemetry("register_agent_specialization_complete", success=False)
                    return False
            
            # Create specialization record
            specialization = AgentSpecialization(
                agent_id=agent_id,
                agent_name=agent_name,
                specialization_id=specialization_id,
                specialization_name=specialization_config.get("name", specialization_id),
                pillar=specialization_config.get("pillar", "general"),
                description=specialization_config.get("description", ""),
                capabilities=specialization_config.get("capabilities", []),
                system_prompt_template=specialization_config.get("system_prompt_template", ""),
                expertise_level=specialization_config.get("expertise_level", "intermediate"),
                version=specialization_config.get("version", "1.0.0"),
                status=specialization_config.get("status", "active"),
                registered_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat()
            )
            
            # Store specialization
            self.agent_specializations[agent_id] = specialization
            
            # Update indexes
            if specialization_id not in self.specialization_index:
                self.specialization_index[specialization_id] = []
            if agent_id not in self.specialization_index[specialization_id]:
                self.specialization_index[specialization_id].append(agent_id)
            
            # Update pillar index
            pillar = specialization.pillar
            if pillar not in self.pillar_specializations:
                self.pillar_specializations[pillar] = []
            if specialization_id not in self.pillar_specializations[pillar]:
                self.pillar_specializations[pillar].append(specialization_id)
            
            # Initialize usage tracking
            self.usage_tracking[agent_id] = {
                "total_uses": 0,
                "successful_uses": 0,
                "failed_uses": 0,
                "last_used": None,
                "usage_by_capability": {}
            }
            
            self.logger.info(f"✅ Registered agent {agent_name} with specialization {specialization_id}")
            
            # Record health metric
            await self.record_health_metric("register_agent_specialization_success", 1.0, {"agent_id": agent_id, "specialization_id": specialization_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("register_agent_specialization_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "register_agent_specialization")
            self.logger.error(f"❌ Failed to register agent specialization: {e}")
            return False
    
    async def update_specialization_usage(self, agent_id: str, success: bool = True, 
                                        capability_used: str = None, user_context: Dict[str, Any] = None) -> bool:
        """
        Update specialization usage statistics.
        
        Args:
            agent_id: Agent identifier
            success: Whether the usage was successful
            capability_used: Specific capability that was used
            user_context: Optional user context for security and tenant validation
            
        Returns:
            bool: True if update successful
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("update_specialization_usage_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_specialization", "write"):
                        await self.record_health_metric("update_specialization_usage_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("update_specialization_usage_complete", success=False)
                        return False
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("update_specialization_usage_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("update_specialization_usage_complete", success=False)
                            return False
            
            if agent_id not in self.usage_tracking:
                self.logger.warning(f"No usage tracking found for agent {agent_id}")
                await self.record_health_metric("update_specialization_usage_error", 1.0, {"agent_id": agent_id, "error": "no_tracking"})
                await self.log_operation_with_telemetry("update_specialization_usage_complete", success=False)
                return False
            
            usage_stats = self.usage_tracking[agent_id]
            
            # Update usage statistics
            usage_stats["total_uses"] += 1
            usage_stats["last_used"] = datetime.now().isoformat()
            
            if success:
                usage_stats["successful_uses"] += 1
            else:
                usage_stats["failed_uses"] += 1
            
            # Update capability usage
            if capability_used:
                if capability_used not in usage_stats["usage_by_capability"]:
                    usage_stats["usage_by_capability"][capability_used] = 0
                usage_stats["usage_by_capability"][capability_used] += 1
            
            # Update agent specialization
            if agent_id in self.agent_specializations:
                specialization = self.agent_specializations[agent_id]
                specialization.usage_count += 1
                specialization.last_updated = datetime.now().isoformat()
                
                # Calculate success rate
                if usage_stats["total_uses"] > 0:
                    specialization.success_rate = usage_stats["successful_uses"] / usage_stats["total_uses"]
            
            # Record health metric
            await self.record_health_metric("update_specialization_usage_success", 1.0, {"agent_id": agent_id, "success": success})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("update_specialization_usage_complete", success=True)
            
            return True
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "update_specialization_usage")
            self.logger.error(f"Failed to update specialization usage for agent {agent_id}: {e}")
            return False
    
    async def get_agent_specialization(self, agent_id: str, user_context: Dict[str, Any] = None) -> Optional[AgentSpecialization]:
        """
        Get agent specialization information.
        
        Args:
            agent_id: Agent identifier
            user_context: Optional user context for security and tenant validation
            
        Returns:
            AgentSpecialization or None if not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agent_specialization_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_specialization", "read"):
                        await self.record_health_metric("get_agent_specialization_access_denied", 1.0, {"agent_id": agent_id})
                        await self.log_operation_with_telemetry("get_agent_specialization_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agent_specialization_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_agent_specialization_complete", success=False)
                            return None
            
            result = self.agent_specializations.get(agent_id)
            
            # Record health metric
            await self.record_health_metric("get_agent_specialization_success", 1.0, {"agent_id": agent_id, "found": result is not None})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agent_specialization_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agent_specialization")
            self.logger.error(f"Failed to get agent specialization for {agent_id}: {e}")
            return None
    
    async def get_specialization_analytics(self, specialization_id: str, user_context: Dict[str, Any] = None) -> Optional[SpecializationAnalytics]:
        """
        Get analytics for a specific specialization.
        
        Args:
            specialization_id: Specialization identifier
            user_context: Optional user context for security and tenant validation
            
        Returns:
            SpecializationAnalytics or None if not found
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_specialization_analytics_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_specialization", "read"):
                        await self.record_health_metric("get_specialization_analytics_access_denied", 1.0, {"specialization_id": specialization_id})
                        await self.log_operation_with_telemetry("get_specialization_analytics_complete", success=False)
                        return None
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_specialization_analytics_tenant_denied", 1.0, {"specialization_id": specialization_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_specialization_analytics_complete", success=False)
                            return None
            
            if specialization_id not in self.specialization_analytics:
                await self.record_health_metric("get_specialization_analytics_not_found", 1.0, {"specialization_id": specialization_id})
                await self.log_operation_with_telemetry("get_specialization_analytics_complete", success=True)
                return None
            
            analytics_data = self.specialization_analytics[specialization_id]
            
            result = SpecializationAnalytics(
                specialization_id=analytics_data["specialization_id"],
                specialization_name=analytics_data["specialization_name"],
                pillar=analytics_data["pillar"],
                total_agents=analytics_data["total_agents"],
                active_agents=analytics_data["active_agents"],
                deprecated_agents=analytics_data["deprecated_agents"],
                experimental_agents=analytics_data["experimental_agents"],
                average_success_rate=analytics_data["average_success_rate"],
                total_usage_count=analytics_data["total_usage_count"],
                capabilities_count=analytics_data["capabilities_count"],
                last_updated=analytics_data["last_updated"]
            )
            
            # Record health metric
            await self.record_health_metric("get_specialization_analytics_success", 1.0, {"specialization_id": specialization_id})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_specialization_analytics_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_specialization_analytics")
            self.logger.error(f"Failed to get specialization analytics for {specialization_id}: {e}")
            return None
    
    async def get_all_specialization_analytics(self, user_context: Dict[str, Any] = None) -> List[SpecializationAnalytics]:
        """Get analytics for all specializations."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_all_specialization_analytics_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_specialization", "read"):
                        await self.record_health_metric("get_all_specialization_analytics_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_all_specialization_analytics_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_all_specialization_analytics_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_all_specialization_analytics_complete", success=False)
                            return []
            
            analytics = []
            for spec_id in self.specialization_analytics.keys():
                spec_analytics = await self.get_specialization_analytics(spec_id, user_context)
                if spec_analytics:
                    analytics.append(spec_analytics)
            
            # Record health metric
            await self.record_health_metric("get_all_specialization_analytics_success", 1.0, {"count": len(analytics)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_all_specialization_analytics_complete", success=True)
            
            return analytics
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_all_specialization_analytics")
            self.logger.error(f"Failed to get all specialization analytics: {e}")
            return []
    
    async def get_pillar_specializations(self, pillar: str, user_context: Dict[str, Any] = None) -> List[str]:
        """
        Get all specializations for a specific pillar.
        
        Args:
            pillar: Business pillar (content, insights, operations, experience)
            user_context: Optional user context for security and tenant validation
            
        Returns:
            List of specialization IDs
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_pillar_specializations_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_specialization", "read"):
                        await self.record_health_metric("get_pillar_specializations_access_denied", 1.0, {"pillar": pillar})
                        await self.log_operation_with_telemetry("get_pillar_specializations_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_pillar_specializations_tenant_denied", 1.0, {"pillar": pillar, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_pillar_specializations_complete", success=False)
                            return []
            
            result = self.pillar_specializations.get(pillar, [])
            
            # Record health metric
            await self.record_health_metric("get_pillar_specializations_success", 1.0, {"pillar": pillar, "count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_pillar_specializations_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_pillar_specializations")
            self.logger.error(f"Failed to get pillar specializations for {pillar}: {e}")
            return []
    
    async def get_agents_by_specialization(self, specialization_id: str, user_context: Dict[str, Any] = None) -> List[str]:
        """
        Get all agents using a specific specialization.
        
        Args:
            specialization_id: Specialization identifier
            user_context: Optional user context for security and tenant validation
            
        Returns:
            List of agent IDs
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_agents_by_specialization_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "agent_specialization", "read"):
                        await self.record_health_metric("get_agents_by_specialization_access_denied", 1.0, {"specialization_id": specialization_id})
                        await self.log_operation_with_telemetry("get_agents_by_specialization_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_agents_by_specialization_tenant_denied", 1.0, {"specialization_id": specialization_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_agents_by_specialization_complete", success=False)
                            return []
            
            result = self.specialization_index.get(specialization_id, [])
            
            # Record health metric
            await self.record_health_metric("get_agents_by_specialization_success", 1.0, {"specialization_id": specialization_id, "count": len(result)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_agents_by_specialization_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_agents_by_specialization")
            self.logger.error(f"Failed to get agents by specialization {specialization_id}: {e}")
            return []
    
    async def get_specialization_health_report(self) -> Dict[str, Any]:
        """Get comprehensive specialization health report."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_specialization_health_report_start", success=True)
            
            total_specializations = len(self.specialization_index)
            total_agents = len(self.agent_specializations)
            
            # Health metrics
            healthy_specializations = 0
            degraded_specializations = 0
            unhealthy_specializations = 0
            
            for spec_id, analytics_data in self.specialization_analytics.items():
                success_rate = analytics_data.get("average_success_rate", 0.0)
                active_agents = analytics_data.get("active_agents", 0)
                total_agents_for_spec = analytics_data.get("total_agents", 0)
                
                if success_rate >= 0.8 and active_agents > 0:
                    healthy_specializations += 1
                elif success_rate >= 0.5 and active_agents > 0:
                    degraded_specializations += 1
                else:
                    unhealthy_specializations += 1
            
            # Pillar distribution
            pillar_distribution = {}
            for pillar, spec_ids in self.pillar_specializations.items():
                pillar_distribution[pillar] = len(spec_ids)
            
            result = {
                "total_specializations": total_specializations,
                "total_agents": total_agents,
                "health_summary": {
                    "healthy_specializations": healthy_specializations,
                    "degraded_specializations": degraded_specializations,
                    "unhealthy_specializations": unhealthy_specializations
                },
                "pillar_distribution": pillar_distribution,
                "top_performing_specializations": self._get_top_performing_specializations(),
                "generated_at": datetime.now().isoformat()
            }
            
            # Record health metric
            await self.record_health_metric("get_specialization_health_report_success", 1.0, {"total_specializations": total_specializations, "healthy_specializations": healthy_specializations})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_specialization_health_report_complete", success=True)
            
            return result
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_specialization_health_report")
            self.logger.error(f"Failed to generate specialization health report: {e}")
            return {}
    
    def _get_top_performing_specializations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing specializations by success rate."""
        try:
            performance_data = []
            
            for spec_id, analytics_data in self.specialization_analytics.items():
                if analytics_data.get("total_agents", 0) > 0:
                    performance_data.append({
                        "specialization_id": spec_id,
                        "specialization_name": analytics_data.get("specialization_name", spec_id),
                        "success_rate": analytics_data.get("average_success_rate", 0.0),
                        "total_agents": analytics_data.get("total_agents", 0),
                        "total_usage": analytics_data.get("total_usage_count", 0)
                    })
            
            # Sort by success rate and usage
            performance_data.sort(key=lambda x: (x["success_rate"], x["total_usage"]), reverse=True)
            
            return performance_data[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get top performing specializations: {e}")
            return []
    
    async def cleanup(self):
        """Cleanup the service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agent_specialization_management_cleanup_start", success=True)
            
            self.specialization_analytics.clear()
            self.usage_tracking.clear()
            
            self.logger.info("Agent Specialization Management Service cleaned up")
            
            # Record health metric
            await self.record_health_metric("agent_specialization_management_cleanup", 1.0, {"service": "agent_specialization_management"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agent_specialization_management_cleanup_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agent_specialization_management_cleanup")
            self.logger.error(f"Error during cleanup: {e}")

    async def shutdown(self):
        """Shutdown the Agent Specialization Management Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("agent_specialization_management_shutdown_start", success=True)
            
            self.logger.info("🛑 Shutting down Agent Specialization Management Service...")
            
            # Clear specializations registry
            self.agent_specializations.clear()
            self.analytics_data.clear()
            
            self.logger.info("✅ Agent Specialization Management Service shutdown complete")
            
            # Record health metric
            await self.record_health_metric("agent_specialization_management_shutdown", 1.0, {"service": "agent_specialization_management"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("agent_specialization_management_shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "agent_specialization_management_shutdown")
            self.logger.error(f"❌ Error during Agent Specialization Management Service shutdown: {e}")





