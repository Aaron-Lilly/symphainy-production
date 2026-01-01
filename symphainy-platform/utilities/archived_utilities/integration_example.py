"""
Integration Example: How to Add Utilities to Existing MCP Servers

This shows how to integrate the utilities into existing MCP servers
without breaking existing functionality.
"""

# Example 1: Simple import and use in existing server
"""
# In your existing MCP server file (e.g., data_steward_server.py):

from common.utilities import (
    get_logging_service, 
    get_error_handler, 
    get_health_service,
    get_telemetry_service
)

class DataStewardMCPServer(SmartCityBase):
    def __init__(self):
        super().__init__("data_steward", "DataStewardMCP")
        
        # Add utilities
        self.logger = get_logging_service("data_steward")
        self.error_handler = get_error_handler("data_steward") 
        self.health_service = get_health_service("data_steward")
        self.telemetry_service = get_telemetry_service("data_steward")
        
        # Rest of existing initialization...
"""

# Example 2: Using telemetry in tool implementations
"""
# In your tool implementations (e.g., tool_implementations.py):

from common.utilities import get_telemetry_service

class DataStewardToolImplementations:
    def __init__(self, server_instance):
        self.server = server_instance
        self.telemetry_service = get_telemetry_service("data_steward")
    
    async def assess_data_quality(self, data_source: str, quality_rules: List[str]):
        try:
            # Your existing tool logic...
            result = {"status": "success", "quality_score": 0.95}
            
            # Log telemetry to Nurse
            await self.telemetry_service.log_telemetry_data({
                "tool": "assess_data_quality",
                "data_source": data_source,
                "quality_score": result["quality_score"],
                "execution_time": 0.25
            }, "data_quality")
            
            return result
        except Exception as e:
            # Log error
            self.server.error_handler.handle_error(e, {"tool": "assess_data_quality"})
            raise
"""

# Example 3: Adding health check endpoint
"""
# In your server setup:

async def health_check(self):
    # Use the health service
    return await self.health_service.health_check()
"""

# Example 4: Setting up Nurse client for telemetry
"""
# When you have access to the Nurse MCP Server client:

def set_nurse_client(self, nurse_client):
    self.telemetry_service.set_nurse_client(nurse_client)
    self.logger.info("Nurse client set for telemetry")
"""












