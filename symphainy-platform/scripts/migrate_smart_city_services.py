#!/usr/bin/env python3
"""
Migration Script for Smart City Services

This script helps migrate Smart City services to the new Phase 2 registration pattern.
Run this to see the migration pattern for each service.

Note: This is a helper script - actual migrations should be done manually using search_replace
to ensure proper code review and testing.
"""

# Service mappings: (service_name, interface_name, endpoint_prefix)
SERVICES = [
    ("DataStewardService", "IDataStewardService", "data-steward"),
    ("ConductorService", "IConductorService", "conductor"),
    ("PostOfficeService", "IPostOfficeService", "post-office"),
    ("SecurityGuardService", "ISecurityGuardService", "security"),
    ("TrafficCopService", "ITrafficCopService", "traffic-cop"),
]

MIGRATION_TEMPLATE = """
    async def register_capabilities(self) -> Dict[str, Any]:
        \"\"\"Register {service_display} capabilities with Curator using new Phase 2 pattern.\"\"\"
        try:
            # Get Curator Foundation via PlatformCapabilitiesMixin
            curator_foundation = self.service.get_curator()
            if not curator_foundation:
                if self.service.logger:
                    self.service.logger.warning("⚠️ Curator Foundation not available, skipping registration")
                return await self._get_{service_snake}_capabilities_dict()
            
            # Import CapabilityDefinition for new pattern
            from foundations.curator_foundation.models.capability_definition import CapabilityDefinition
            
            # Build capabilities list from SOA APIs and MCP tools
            capabilities = []
            
            # Convert SOA APIs to capabilities with contracts
            for api_name, api_config in self.service.soa_apis.items():
                endpoint = api_config.get("endpoint", f"/api/v1/{endpoint_prefix}/{api_name}")
                handler = getattr(self.service, api_name, None) or getattr(self, api_name, None)
                
                capability = CapabilityDefinition(
                    service_name=self.service.service_name,
                    interface_name="{interface_name}",
                    endpoints=[endpoint],
                    tools=[],
                    description=api_config.get("description", f"{service_display} {{api_name}} API"),
                    realm="smart_city",
                    version="1.0.0",
                    semantic_mapping=None,  # Can be added later if semantic API mapping exists
                    contracts={{
                        "soa_api": {{
                            "api_name": api_name,
                            "endpoint": endpoint,
                            "method": api_config.get("method", "POST"),
                            "handler": handler,
                            "metadata": {{
                                "method": api_config.get("method", "POST"),
                                "description": api_config.get("description", f"{service_display} {{api_name}} API"),
                                "parameters": api_config.get("parameters", [])
                            }}
                        }}
                    }}
                )
                capabilities.append(capability)
            
            # Convert MCP tools to capabilities with contracts
            for tool_name, tool_config in self.service.mcp_tools.items():
                handler = getattr(self, f"_mcp_{{tool_name}}", None)
                endpoint = tool_config.get("endpoint", f"/mcp/{{tool_name}}")
                
                capability = CapabilityDefinition(
                    service_name=self.service.service_name,
                    interface_name="{interface_name}",
                    endpoints=[endpoint],
                    tools=[tool_name],
                    description=tool_config.get("description", f"{service_display} {{tool_name}} tool"),
                    realm="smart_city",
                    version="1.0.0",
                    semantic_mapping=None,  # Can be added later if semantic API mapping exists
                    contracts={{
                        "mcp_tool": {{
                            "tool_name": tool_name,
                            "tool_definition": {{
                                "name": tool_config.get("name", tool_name),
                                "description": tool_config.get("description", f"{service_display} {{tool_name}} tool"),
                                "endpoint": endpoint,
                                "handler": handler,
                                "input_schema": tool_config.get("input_schema", {{}})
                            }},
                            "metadata": {{
                                "service_name": self.service.service_name,
                                "tool_name": tool_name
                            }}
                        }}
                    }}
                )
                capabilities.append(capability)
            
            # Register all capabilities using new pattern
            for capability in capabilities:
                success = await curator_foundation.register_domain_capability(capability)
                if not success:
                    if self.service.logger:
                        self.service.logger.warning(f"⚠️ Failed to register capability: {{capability.description}}")
            
            if self.service.logger:
                self.service.logger.info(f"✅ {service_display} capabilities registered with Curator (Phase 2 pattern): {{len(capabilities)}} capabilities")
        except Exception as e:
            if self.service.logger:
                self.service.logger.error(f"❌ Failed to register {service_display} capabilities: {{e}}")
                import traceback
                self.service.logger.error(f"Traceback: {{traceback.format_exc()}}")
            # Don't raise - return capabilities dict anyway
        
        # Return capabilities metadata
        return await self._get_{service_snake}_capabilities_dict()
"""

def generate_migration_code(service_name, interface_name, endpoint_prefix):
    """Generate migration code for a service."""
    # Convert service name to display name and snake case
    service_display = service_name.replace("Service", "").replace("_", " ")
    service_snake = service_name.lower().replace("service", "").replace("_", "_")
    
    return MIGRATION_TEMPLATE.format(
        service_display=service_display,
        service_snake=service_snake,
        interface_name=interface_name,
        endpoint_prefix=endpoint_prefix
    )

if __name__ == "__main__":
    print("Smart City Services Migration Helper")
    print("=" * 50)
    print("\nThis script shows the migration pattern for each service.")
    print("Use search_replace to apply these changes manually.\n")
    
    for service_name, interface_name, endpoint_prefix in SERVICES:
        print(f"\n{'='*50}")
        print(f"Service: {service_name}")
        print(f"Interface: {interface_name}")
        print(f"Endpoint Prefix: {endpoint_prefix}")
        print(f"{'='*50}")
        print(generate_migration_code(service_name, interface_name, endpoint_prefix))







