#!/usr/bin/env python3
"""
Tool Discovery Service - Agentic Realm Business Service

Provides advanced tool discovery capabilities using Curator Foundation's service discovery.
Handles distributed tool discovery across realms and pillars.

WHAT (Agentic Role): I provide advanced tool discovery for agentic operations
HOW (Business Service): I orchestrate Curator Foundation service discovery for tools
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from foundations.public_works_foundation.abstraction_contracts.tool_storage_protocol import (
    ToolDefinition
)

# Import utility mixins
from bases.mixins.utility_access_mixin import UtilityAccessMixin
from bases.mixins.performance_monitoring_mixin import PerformanceMonitoringMixin


class ToolDiscoveryService(UtilityAccessMixin, PerformanceMonitoringMixin):
    """
    Tool Discovery Service - Agentic Realm Business Service
    
    Provides advanced tool discovery capabilities using Curator Foundation's service discovery.
    Handles distributed tool discovery across realms and pillars.
    
    This is a BUSINESS SERVICE that orchestrates Curator Foundation service discovery
    for distributed tool discovery across the platform.
    """
    
    def __init__(self, tool_registry_service=None, curator_foundation=None, di_container=None):
        """Initialize Tool Discovery Service with tool registry and Curator Foundation."""
        if not di_container:
            raise ValueError("DI Container is required for ToolDiscoveryService initialization")
        
        # Initialize utility mixins
        self._init_utility_access(di_container)
        self._init_performance_monitoring(di_container)
        
        self.tool_registry_service = tool_registry_service
        self.curator_foundation = curator_foundation
        
        # Business metrics
        self.business_metrics = {
            "total_discovery_requests": 0,
            "successful_discoveries": 0,
            "failed_discoveries": 0,
            "cross_realm_discoveries": 0,
            "curator_discoveries": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        self.logger.info("✅ Tool Discovery Service (Business Service) initialized")
    
    async def discover_tools_by_capability(self, capability_name: str,
                                         realm: str = None,
                                         pillar: str = None,
                                         tenant_context: Dict[str, Any] = None) -> List[ToolDefinition]:
        """
        Discover tools by capability using Curator Foundation service discovery.
        
        Args:
            capability_name: Name of the capability to discover
            realm: Specific realm to search (optional)
            pillar: Specific pillar to search (optional)
            tenant_context: Tenant context for multi-tenancy
            
        Returns:
            List of discovered tool definitions
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("discover_tools_by_capability_start", success=True, details={"capability_name": capability_name, "realm": realm, "pillar": pillar})
            
            # Security validation (zero-trust: secure by design)
            if tenant_context:
                security = self.get_security()
                if security:
                    user_context = {"tenant_id": tenant_context.get("tenant_id")} if tenant_context.get("tenant_id") else None
                    if user_context:
                        if not await security.check_permissions(user_context, "tool_discovery", "read"):
                            await self.record_health_metric("discover_tools_by_capability_access_denied", 1.0, {"capability_name": capability_name})
                            await self.log_operation_with_telemetry("discover_tools_by_capability_complete", success=False)
                            return []
            
            # Tenant validation (multi-tenant support)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_tools_by_capability_tenant_denied", 1.0, {"capability_name": capability_name, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_tools_by_capability_complete", success=False)
                            return []
            
            self.logger.info(f"🔍 Discovering tools by capability: {capability_name}")
            
            tools = []
            
            # First, try local tool registry
            if self.tool_registry_service:
                local_filters = {"tags": [capability_name]}
                if realm:
                    local_filters["realm"] = realm
                if pillar:
                    local_filters["pillar"] = pillar
                
                local_tools = await self.tool_registry_service.discover_tools(
                    filters=local_filters,
                    tenant_context=tenant_context
                )
                tools.extend(local_tools)
                self.logger.info(f"Found {len(local_tools)} tools in local registry")
            
            # Then, try Curator Foundation service discovery
            if self.curator_foundation:
                curator_tools = await self._discover_via_curator(
                    capability_name, realm, pillar, tenant_context
                )
                tools.extend(curator_tools)
                self.logger.info(f"Found {len(curator_tools)} tools via Curator discovery")
            
            # Update business metrics
            self.business_metrics["total_discovery_requests"] += 1
            self.business_metrics["successful_discoveries"] += len(tools)
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            
            # Record success metric
            await self.record_health_metric("discover_tools_by_capability_success", 1.0, {"capability_name": capability_name, "tools_count": len(tools)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("discover_tools_by_capability_complete", success=True, details={"capability_name": capability_name, "tools_count": len(tools)})
            
            self.logger.info(f"✅ Discovered {len(tools)} tools for capability: {capability_name}")
            return tools
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_tools_by_capability", details={"capability_name": capability_name})
            self.logger.error(f"❌ Failed to discover tools by capability {capability_name}: {e}")
            self.business_metrics["failed_discoveries"] += 1
            self.business_metrics["last_updated"] = datetime.now().isoformat()
            return []
    
    async def discover_tools_by_agent(self, agent_id: str,
                                    tenant_context: Dict[str, Any] = None) -> List[ToolDefinition]:
        """
        Discover tools owned by a specific agent.
        
        Args:
            agent_id: ID of the agent
            tenant_context: Tenant context for multi-tenancy
            
        Returns:
            List of tool definitions owned by the agent
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("discover_tools_by_agent_start", success=True, details={"agent_id": agent_id})
            
            # Security validation (zero-trust: secure by design)
            if tenant_context:
                security = self.get_security()
                if security:
                    user_context = {"tenant_id": tenant_context.get("tenant_id")} if tenant_context.get("tenant_id") else None
                    if user_context:
                        if not await security.check_permissions(user_context, "tool_discovery", "read"):
                            await self.record_health_metric("discover_tools_by_agent_access_denied", 1.0, {"agent_id": agent_id})
                            await self.log_operation_with_telemetry("discover_tools_by_agent_complete", success=False)
                            return []
            
            # Tenant validation (multi-tenant support)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_tools_by_agent_tenant_denied", 1.0, {"agent_id": agent_id, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_tools_by_agent_complete", success=False)
                            return []
            
            self.logger.info(f"🔍 Discovering tools by agent: {agent_id}")
            
            tools = []
            
            # Search local registry
            if self.tool_registry_service:
                local_filters = {"owner_agent": agent_id}
                local_tools = await self.tool_registry_service.discover_tools(
                    filters=local_filters,
                    tenant_context=tenant_context
                )
                tools.extend(local_tools)
            
            # Search via Curator Foundation
            if self.curator_foundation:
                curator_tools = await self._discover_agent_tools_via_curator(
                    agent_id, tenant_context
                )
                tools.extend(curator_tools)
            
            # Record success metric
            await self.record_health_metric("discover_tools_by_agent_success", 1.0, {"agent_id": agent_id, "tools_count": len(tools)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("discover_tools_by_agent_complete", success=True, details={"agent_id": agent_id, "tools_count": len(tools)})
            
            self.logger.info(f"✅ Found {len(tools)} tools for agent: {agent_id}")
            return tools
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_tools_by_agent", details={"agent_id": agent_id})
            self.logger.error(f"❌ Failed to discover tools for agent {agent_id}: {e}")
            return []
    
    async def discover_tools_by_tags(self, tags: List[str],
                                   realm: str = None,
                                   tenant_context: Dict[str, Any] = None) -> List[ToolDefinition]:
        """
        Discover tools by tags.
        
        Args:
            tags: List of tags to search for
            realm: Specific realm to search (optional)
            tenant_context: Tenant context for multi-tenancy
            
        Returns:
            List of tool definitions matching the tags
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("discover_tools_by_tags_start", success=True, details={"tags": tags, "realm": realm})
            
            # Security validation (zero-trust: secure by design)
            if tenant_context:
                security = self.get_security()
                if security:
                    user_context = {"tenant_id": tenant_context.get("tenant_id")} if tenant_context.get("tenant_id") else None
                    if user_context:
                        if not await security.check_permissions(user_context, "tool_discovery", "read"):
                            await self.record_health_metric("discover_tools_by_tags_access_denied", 1.0, {"tags": tags})
                            await self.log_operation_with_telemetry("discover_tools_by_tags_complete", success=False)
                            return []
            
            # Tenant validation (multi-tenant support)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_tools_by_tags_tenant_denied", 1.0, {"tags": tags, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_tools_by_tags_complete", success=False)
                            return []
            
            self.logger.info(f"🔍 Discovering tools by tags: {tags}")
            
            tools = []
            
            # Search local registry
            if self.tool_registry_service:
                local_filters = {"tags": tags}
                if realm:
                    local_filters["realm"] = realm
                
                local_tools = await self.tool_registry_service.discover_tools(
                    filters=local_filters,
                    tenant_context=tenant_context
                )
                tools.extend(local_tools)
            
            # Search via Curator Foundation
            if self.curator_foundation:
                curator_tools = await self._discover_tagged_tools_via_curator(
                    tags, realm, tenant_context
                )
                tools.extend(curator_tools)
            
            # Record success metric
            await self.record_health_metric("discover_tools_by_tags_success", 1.0, {"tags": tags, "tools_count": len(tools)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("discover_tools_by_tags_complete", success=True, details={"tags": tags, "tools_count": len(tools)})
            
            self.logger.info(f"✅ Found {len(tools)} tools for tags: {tags}")
            return tools
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_tools_by_tags", details={"tags": tags})
            self.logger.error(f"❌ Failed to discover tools by tags {tags}: {e}")
            return []
    
    async def discover_available_tools(self, tenant_context: Dict[str, Any] = None) -> Dict[str, List[ToolDefinition]]:
        """
        Discover all available tools organized by category.
        
        Args:
            tenant_context: Tenant context for multi-tenancy
            
        Returns:
            Dict organizing tools by category
        """
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("discover_available_tools_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if tenant_context:
                security = self.get_security()
                if security:
                    user_context = {"tenant_id": tenant_context.get("tenant_id")} if tenant_context.get("tenant_id") else None
                    if user_context:
                        if not await security.check_permissions(user_context, "tool_discovery", "read"):
                            await self.record_health_metric("discover_available_tools_access_denied", 1.0, {})
                            await self.log_operation_with_telemetry("discover_available_tools_complete", success=False)
                            return {}
            
            # Tenant validation (multi-tenant support)
            if tenant_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = tenant_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("discover_available_tools_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("discover_available_tools_complete", success=False)
                            return {}
            
            self.logger.info("🔍 Discovering all available tools")
            
            all_tools = []
            
            # Get tools from local registry
            if self.tool_registry_service:
                local_tools = await self.tool_registry_service.discover_tools(
                    tenant_context=tenant_context
                )
                all_tools.extend(local_tools)
            
            # Get tools via Curator Foundation
            if self.curator_foundation:
                curator_tools = await self._discover_all_tools_via_curator(tenant_context)
                all_tools.extend(curator_tools)
            
            # Organize by category
            organized_tools = {
                "by_realm": {},
                "by_pillar": {},
                "by_tags": {},
                "by_agent": {}
            }
            
            for tool in all_tools:
                # By realm
                realm = tool.realm or "unknown"
                if realm not in organized_tools["by_realm"]:
                    organized_tools["by_realm"][realm] = []
                organized_tools["by_realm"][realm].append(tool)
                
                # By pillar
                pillar = tool.pillar or "unknown"
                if pillar not in organized_tools["by_pillar"]:
                    organized_tools["by_pillar"][pillar] = []
                organized_tools["by_pillar"][pillar].append(tool)
                
                # By tags
                for tag in tool.tags:
                    if tag not in organized_tools["by_tags"]:
                        organized_tools["by_tags"][tag] = []
                    organized_tools["by_tags"][tag].append(tool)
                
                # By agent
                if tool.owner_agent:
                    if tool.owner_agent not in organized_tools["by_agent"]:
                        organized_tools["by_agent"][tool.owner_agent] = []
                    organized_tools["by_agent"][tool.owner_agent].append(tool)
            
            # Record success metric
            await self.record_health_metric("discover_available_tools_success", 1.0, {"total_tools": len(all_tools)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("discover_available_tools_complete", success=True, details={"total_tools": len(all_tools)})
            
            self.logger.info(f"✅ Organized {len(all_tools)} tools by category")
            return organized_tools
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "discover_available_tools")
            self.logger.error(f"❌ Failed to discover available tools: {e}")
            return {"by_realm": {}, "by_pillar": {}, "by_tags": {}, "by_agent": {}}
    
    async def _discover_via_curator(self, capability_name: str, realm: str = None,
                                  pillar: str = None,
                                  tenant_context: Dict[str, Any] = None) -> List[ToolDefinition]:
        """Discover tools via Curator Foundation service discovery."""
        try:
            if not self.curator_foundation:
                return []
            
            # Use Curator's capability registry to find services with the capability
            capabilities = await self.curator_foundation.capability_registry.get_capabilities_by_type(
                capability_type="tool",
                realm=realm,
                pillar=pillar
            )
            
            tools = []
            for capability in capabilities:
                if capability.get("tools"):
                    for tool_data in capability["tools"]:
                        if capability_name in tool_data.get("name", "").lower():
                            tool = ToolDefinition(
                                name=tool_data["name"],
                                description=tool_data.get("description", ""),
                                parameters=tool_data.get("parameters", {}),
                                returns=tool_data.get("returns"),
                                tags=[capability_name],
                                realm=capability.get("realm"),
                                pillar=capability.get("pillar"),
                                version=capability.get("version", "1.0.0")
                            )
                            tools.append(tool)
            
            self.business_metrics["curator_discoveries"] += 1
            return tools
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_discover_via_curator", details={"capability_name": capability_name})
            self.logger.error(f"❌ Failed to discover via Curator: {e}")
            return []
    
    async def _discover_agent_tools_via_curator(self, agent_id: str,
                                              tenant_context: Dict[str, Any] = None) -> List[ToolDefinition]:
        """Discover tools owned by agent via Curator Foundation."""
        try:
            if not self.curator_foundation:
                return []
            
            # This would need to be implemented based on how Curator tracks agent ownership
            # For now, return empty list
            return []
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_discover_agent_tools_via_curator", details={"agent_id": agent_id})
            self.logger.error(f"❌ Failed to discover agent tools via Curator: {e}")
            return []
    
    async def _discover_tagged_tools_via_curator(self, tags: List[str], realm: str = None,
                                               tenant_context: Dict[str, Any] = None) -> List[ToolDefinition]:
        """Discover tools by tags via Curator Foundation."""
        try:
            if not self.curator_foundation:
                return []
            
            # This would need to be implemented based on Curator's tagging system
            # For now, return empty list
            return []
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_discover_tagged_tools_via_curator", details={"tags": tags})
            self.logger.error(f"❌ Failed to discover tagged tools via Curator: {e}")
            return []
    
    async def _discover_all_tools_via_curator(self, tenant_context: Dict[str, Any] = None) -> List[ToolDefinition]:
        """Discover all tools via Curator Foundation."""
        try:
            if not self.curator_foundation:
                return []
            
            # Get all tool capabilities from Curator
            capabilities = await self.curator_foundation.capability_registry.get_all_capabilities()
            
            tools = []
            for capability in capabilities:
                if capability.get("tools"):
                    for tool_data in capability["tools"]:
                        tool = ToolDefinition(
                            name=tool_data["name"],
                            description=tool_data.get("description", ""),
                            parameters=tool_data.get("parameters", {}),
                            returns=tool_data.get("returns"),
                            tags=tool_data.get("tags", []),
                            realm=capability.get("realm"),
                            pillar=capability.get("pillar"),
                            version=capability.get("version", "1.0.0")
                        )
                        tools.append(tool)
            
            return tools
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "_discover_all_tools_via_curator")
            self.logger.error(f"❌ Failed to discover all tools via Curator: {e}")
            return []
    
    def get_business_metrics(self) -> Dict[str, Any]:
        """Get business metrics for tool discovery operations."""
        return self.business_metrics.copy()
    
    def get_discovery_health(self) -> Dict[str, Any]:
        """Get Tool Discovery Service health status."""
        return {
            "service_name": "ToolDiscoveryService",
            "service_type": "business_service",
            "realm": "agentic",
            "tool_registry_available": self.tool_registry_service is not None,
            "curator_foundation_available": self.curator_foundation is not None,
            "business_metrics": self.get_business_metrics(),
            "status": "healthy"
        }


