#!/usr/bin/env python3
"""
Pattern Initialization Micro-Module

Handles initialization of default architectural patterns for the Pattern Validation Service.

WHAT (Module Role): I need to initialize default architectural patterns
HOW (Module Implementation): I create and register default pattern definitions
"""

from typing import Dict, Any
from ...models import PatternDefinition


class PatternInitializationModule:
    """Handles initialization of default architectural patterns."""
    
    def __init__(self, logger):
        """Initialize the Pattern Initialization Module."""
        self.logger = logger
        self.service_name = "pattern_initialization"
    
    def initialize_default_patterns(self) -> Dict[str, PatternDefinition]:
        """Initialize default architectural patterns."""
        default_patterns = [
            PatternDefinition(
                pattern_name="interface_naming",
                pattern_type="interface",
                rules=[
                    "Interface names must start with 'I'",
                    "Interface names must be PascalCase",
                    "Interface names must end with descriptive noun"
                ],
                description="Interface naming pattern requirements",
                severity="error"
            ),
            PatternDefinition(
                pattern_name="soa_endpoint_structure",
                pattern_type="api",
                rules=[
                    "Endpoints must follow RESTful conventions",
                    "Endpoints must use proper HTTP methods",
                    "Endpoints must have consistent path structure"
                ],
                description="SOA endpoint structure requirements",
                severity="error"
            ),
            PatternDefinition(
                pattern_name="mcp_tool_naming",
                pattern_type="mcp",
                rules=[
                    "Tool names must be snake_case",
                    "Tool names must be descriptive",
                    "Tool names must not conflict with existing tools"
                ],
                description="MCP tool naming requirements",
                severity="warning"
            ),
            PatternDefinition(
                pattern_name="service_initialization",
                pattern_type="service",
                rules=[
                    "Services must call super().initialize()",
                    "Services must handle initialization errors",
                    "Services must log initialization status"
                ],
                description="Service initialization pattern requirements",
                severity="error"
            ),
            PatternDefinition(
                pattern_name="error_handling",
                pattern_type="service",
                rules=[
                    "All async methods must have try-except blocks",
                    "Errors must be logged with context",
                    "Errors must be handled gracefully"
                ],
                description="Error handling pattern requirements",
                severity="error"
            ),
            PatternDefinition(
                pattern_name="logging_pattern",
                pattern_type="service",
                rules=[
                    "All operations must be logged",
                    "Log messages must include emojis for clarity",
                    "Log levels must be appropriate"
                ],
                description="Logging pattern requirements",
                severity="warning"
            )
        ]
        
        # Convert to dictionary for easy access
        pattern_registry = {}
        for pattern in default_patterns:
            pattern_registry[pattern.pattern_name] = pattern
        
        self.logger.info(f"📋 Initialized {len(default_patterns)} default architectural patterns")
        return pattern_registry
