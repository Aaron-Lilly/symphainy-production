#!/usr/bin/env python3
"""
Curator Foundation Service

Platform-wide pattern enforcement and registry management service that provides
capability registration, pattern validation, anti-pattern detection, and OpenAPI
generation for all services across the platform.

WHAT (Foundation Role): I need to provide platform-wide pattern enforcement and registry management
HOW (Foundation Service): I maintain a central capability registry and validate architectural patterns
"""

import os
import sys
import json
import re
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from bases.foundation_service_base import FoundationServiceBase
from common.utilities import UserContext

# Import models from micro-modules
from .models import CapabilityDefinition, PatternDefinition, AntiPatternViolation


class CuratorFoundationService(FoundationServiceBase):
    """
    Curator Foundation Service - Platform-wide pattern enforcement and registry management
    
    Provides centralized capability registration, pattern validation, anti-pattern detection,
    and OpenAPI generation for all services across the platform.
    
    WHAT (Foundation Role): I need to provide platform-wide pattern enforcement and registry management
    HOW (Foundation Service): I maintain a central capability registry and validate architectural patterns
    """
    
    def __init__(self, utility_foundation, public_works_foundation=None):
        """Initialize Curator Foundation Service."""
        super().__init__("curator_foundation", utility_foundation)
        
        self.utility_foundation = utility_foundation
        self.public_works_foundation = public_works_foundation
        
        # Central registries
        self.capability_registry: Dict[str, CapabilityDefinition] = {}
        self.pattern_registry: Dict[str, PatternDefinition] = {}
        self.anti_pattern_violations: List[AntiPatternViolation] = []
        
        # Service discovery integration
        self.service_discovery_enabled = False
        self.consul_client = None
        
        # Initialize default patterns
        self._initialize_default_patterns()
        
        self.logger.info("🏛️ Curator Foundation Service initialized as Platform Registry Manager")
    
    def _initialize_default_patterns(self):
        """Initialize default architectural patterns."""
        default_patterns = [
        PatternDefinition(
                pattern_name="interface_naming",
                pattern_type="interface",
                rules=[
                    r"^I[A-Z][a-zA-Z0-9]*$",  # Interface names start with I
                    r"^[A-Z][a-zA-Z0-9]*Service$"  # Service names end with Service
                ],
                description="Interface and service naming conventions",
                severity="error"
        ),
        PatternDefinition(
                pattern_name="soa_endpoint_structure",
                pattern_type="api",
                rules=[
                    r"^/[a-z][a-z0-9_]*/[a-z][a-z0-9_]*$",  # RESTful endpoint structure
                    r"^/openapi\.json$",  # Required OpenAPI endpoint
                    r"^/docs$"  # Required docs endpoint
                ],
                description="SOA endpoint structure requirements",
                severity="error"
        ),
        PatternDefinition(
                pattern_name="mcp_tool_naming",
                pattern_type="mcp",
                rules=[
                    r"^[a-z][a-z0-9_]*$",  # MCP tool names are lowercase with underscores
                    r"^[a-z][a-z0-9_]*_tool$"  # MCP tool names should end with _tool
                ],
                description="MCP tool naming conventions",
                severity="warning"
        ),
        PatternDefinition(
                pattern_name="error_handling",
                pattern_type="service",
                rules=[
                    r"async def.*handle_error",  # Services should have error handling
                    r"try:\s*.*\s*except.*:",  # Proper try-except blocks
                    r"await.*error_handler"  # Use error handler service
                ],
                description="Error handling patterns",
                severity="error"
        ),
        PatternDefinition(
                pattern_name="logging_patterns",
                pattern_type="service",
                rules=[
                    r"self\.logger\.[a-z]+",  # Use logger service
                    r"await.*log_operation",  # Use structured logging
                    r"extra=.*log_data"  # Include structured data
                ],
                description="Logging pattern requirements",
                severity="warning"
        )
        ]
        
        for pattern in default_patterns:
        self.pattern_registry[pattern.pattern_name] = pattern
        
        self.logger.info(f"📋 Initialized {len(default_patterns)} default architectural patterns")
    
    async def initialize(self):
        """Initialize the Curator Foundation Service."""
        try:
            await super().initialize()
            self.logger.info("🚀 Initializing Curator Foundation Service...")
            
        # Initialize service discovery if available
        await self._initialize_service_discovery()
            
        # Register with Public Works Foundation if available
        if self.public_works_foundation:
                await self._register_with_public_works()
            
        self.logger.info("✅ Curator Foundation Service initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Curator Foundation Service: {e}")
            await self.error_handler.handle_error(e)
            raise
    
    async def _initialize_service_discovery(self):
        """Initialize service discovery integration."""
        try:
            # Check if Consul is available through Public Works Foundation
            if self.public_works_foundation:
                # Get service discovery abstraction
                service_discovery = self.public_works_foundation.get_service_discovery_abstraction()
                if service_discovery:
                    self.service_discovery_enabled = True
                    self.consul_client = service_discovery
                    self.logger.info("🔍 Service discovery integration enabled")
                else:
                    self.logger.info("ℹ️ Service discovery not available, using local registry only")
        else:
                self.logger.info("ℹ️ Public Works Foundation not available, using local registry only")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Service discovery initialization failed: {e}")
            self.service_discovery_enabled = False
    
    async def _register_with_public_works(self):
        """Register Curator Foundation Service with Public Works Foundation."""
        try:
            if self.public_works_foundation:
                # Register Curator as a foundation service
                await self.public_works_foundation.register_foundation_service(
                    "curator_foundation", 
                    self
                )
                self.logger.info("📝 Registered with Public Works Foundation")
            except Exception as e:
            self.logger.warning(f"⚠️ Failed to register with Public Works Foundation: {e}")
    
    # ============================================================================
    # CAPABILITY REGISTRATION
    
    async def register_capability(self, service_name: str, capability: Dict[str, Any]) -> Dict[str, Any]:
        """Register a service capability in the central registry."""
        try:
            await self.log_operation_with_telemetry("register_capability", details={
                "service_name": service_name,
                "capability": capability
            })
            
        # Validate capability structure
        if not self._validate_capability_structure(capability):
                raise ValueError(f"Invalid capability structure for {service_name}")
            
        # Create capability definition
        capability_def = CapabilityDefinition(
                service_name=service_name,
                interface_name=capability.get("interface", f"I{service_name.title()}"),
                endpoints=capability.get("endpoints", []),
                tools=capability.get("tools", []),
                description=capability.get("description", f"{service_name} service capability"),
                realm=capability.get("realm", "unknown")
        )
            
        # Register in local registry
        self.capability_registry[service_name] = capability_def
            
        # Register in service discovery if available
        if self.service_discovery_enabled and self.consul_client:
                await self._register_with_service_discovery(service_name, capability_def)
            
        # Validate patterns
        await self._validate_service_patterns(service_name, capability_def)
            
        result = {
                "success": True,
                "service_name": service_name,
                "capability": asdict(capability_def),
                "registered_at": capability_def.registered_at
        }
            
        self.logger.info(f"✅ Registered capability for {service_name}")
        return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to register capability for {service_name}: {e}")
            await self.handle_error(e, f"register_capability_{service_name}")
            raise
    
    def _validate_capability_structure(self, capability: Dict[str, Any]) -> bool:
        """Validate capability structure."""
        required_fields = ["interface", "endpoints", "tools"]
        return all(field in capability for field in required_fields)
    
    async def _register_with_service_discovery(self, service_name: str, capability: CapabilityDefinition):
        """Register capability with service discovery."""
        try:
            if self.consul_client:
                service_data = {
                    "service_name": service_name,
                    "interface": capability.interface_name,
                    "endpoints": capability.endpoints,
                    "tools": capability.tools,
                    "realm": capability.realm,
                    "version": capability.version,
                    "registered_at": capability.registered_at
                }
                
                await self.consul_client.register_service(service_name, service_data)
                self.logger.info(f"🔍 Registered {service_name} with service discovery")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to register {service_name} with service discovery: {e}")
    
    async def _validate_service_patterns(self, service_name: str, capability: CapabilityDefinition):
        """Validate service patterns for a registered capability."""
        try:
            # Validate interface naming
            interface_pattern = {
                "name": f"{service_name}_interface",
                "type": "interface",
                "value": capability.interface_name
            }
            interface_validation = await self.validate_pattern(interface_pattern)
            
        # Validate endpoint patterns
        endpoint_violations = []
        for endpoint in capability.endpoints:
                endpoint_pattern = {
                    "name": f"{service_name}_endpoint",
                    "type": "api",
                    "value": endpoint
                }
                endpoint_validation = await self.validate_pattern(endpoint_pattern)
                endpoint_violations.extend(endpoint_validation['violations'])
            
        # Log validation results
        total_violations = len(interface_validation['violations']) + len(endpoint_violations)
        if total_violations > 0:
                self.logger.warning(f"⚠️ Service {service_name} has {total_violations} pattern violations")
        else:
                self.logger.info(f"✅ Service {service_name} passed all pattern validations")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to validate patterns for {service_name}: {e}")
    
    async def get_capability(self, service_name: str) -> Optional[CapabilityDefinition]:
        """Get a registered capability."""
        try:
            capability = self.capability_registry.get(service_name)
            if capability:
                await self.log_operation_with_telemetry("get_capability", details={
                    "service_name": service_name,
                    "found": True
                })
            return capability
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get capability for {service_name}: {e}")
            return None
    
    async def list_capabilities(self, realm: str = None) -> List[CapabilityDefinition]:
        """List all registered capabilities, optionally filtered by realm."""
        try:
            capabilities = list(self.capability_registry.values())
            
        if realm:
                capabilities = [cap for cap in capabilities if cap.realm == realm]
            
        await self.log_operation_with_telemetry("list_capabilities", details={
                "realm": realm,
                "count": len(capabilities)
        })
            
        return capabilities
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list capabilities: {e}")
            return []
    
    # ============================================================================
    # PATTERN VALIDATION
    
    async def validate_pattern(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a pattern against architectural rules."""
        try:
            await self.log_operation_with_telemetry("validate_pattern", details={
                "pattern_name": pattern.get("name", "unknown")
            })
            
        pattern_name = pattern.get("name", "unknown")
        pattern_type = pattern.get("type", "unknown")
            
        # Get applicable patterns - only match exact type or specific patterns
        applicable_patterns = []
        if pattern_type == "interface":
                applicable_patterns = [p for p in self.pattern_registry.values() if p.pattern_name == "interface_naming"]
        elif pattern_type == "api":
                applicable_patterns = [p for p in self.pattern_registry.values() if p.pattern_name == "soa_endpoint_structure"]
        elif pattern_type == "mcp":
                applicable_patterns = [p for p in self.pattern_registry.values() if p.pattern_name == "mcp_tool_naming"]
        else:
                # For other types, only apply service-level patterns
                applicable_patterns = [p for p in self.pattern_registry.values() if p.pattern_type == "service"]
            
        violations = []
        for pattern_def in applicable_patterns:
                pattern_violations = await self._check_pattern_rules(pattern, pattern_def)
                violations.extend(pattern_violations)
            
        result = {
                "success": len(violations) == 0,
                "pattern_name": pattern_name,
                "violations": violations,
                "validated_at": datetime.utcnow().isoformat()
        }
            
        if violations:
                self.logger.warning(f"⚠️ Pattern validation failed for {pattern_name}: {len(violations)} violations")
        else:
                self.logger.info(f"✅ Pattern validation passed for {pattern_name}")
            
        return result
            
        except Exception as e:
            self.logger.error(f"❌ Failed to validate pattern: {e}")
            await self.handle_error(e, "validate_pattern")
            raise
    
    async def _check_pattern_rules(self, pattern: Dict[str, Any], pattern_def: PatternDefinition) -> List[Dict[str, Any]]:
        """Check pattern against specific pattern rules."""
        violations = []
        
        for rule in pattern_def.rules:
        if not self._check_rule(pattern, rule):
                violations.append({
                    "pattern_name": pattern_def.pattern_name,
                    "rule": rule,
                    "severity": pattern_def.severity,
                    "description": pattern_def.description
                })
        
        return violations
    
    def _check_rule(self, pattern: Dict[str, Any], rule: str) -> bool:
        """Check if pattern matches a specific rule."""
        try:
            # Handle different rule types
            if rule.startswith("^") and rule.endswith("$"):
                # Regex pattern matching
                pattern_value = pattern.get("value", "")
                return bool(re.match(rule, pattern_value))
            elif "async def" in rule:
                # Function definition pattern
                code = pattern.get("code", "")
                return bool(re.search(rule, code))
        else:
                # Simple string matching
                pattern_value = pattern.get("value", "")
                return rule in pattern_value
                
        except Exception as e:
            self.logger.warning(f"⚠️ Rule check failed for {rule}: {e}")
            return False
    
    # ============================================================================
    # ANTI-PATTERN DETECTION
    
    async def detect_anti_patterns(self, service_code: str, file_path: str = None) -> List[AntiPatternViolation]:
        """Detect anti-patterns in service code."""
        try:
            await self.log_operation_with_telemetry("detect_anti_patterns", details={
                "file_path": file_path,
                "code_length": len(service_code)
            })
            
        violations = []
        lines = service_code.split('\n')
            
        # Check each pattern
        for pattern_name, pattern_def in self.pattern_registry.items():
                pattern_violations = await self._scan_code_for_violations(
                    service_code, lines, pattern_def, file_path
                )
                violations.extend(pattern_violations)
            
        # Store violations
        self.anti_pattern_violations.extend(violations)
            
        if violations:
                self.logger.warning(f"⚠️ Detected {len(violations)} anti-pattern violations in {file_path or 'code'}")
        else:
                self.logger.info(f"✅ No anti-pattern violations detected in {file_path or 'code'}")
            
        return violations
            
        except Exception as e:
            self.logger.error(f"❌ Failed to detect anti-patterns: {e}")
            await self.handle_error(e, "detect_anti_patterns")
            return []
    
    async def _scan_code_for_violations(self, code: str, lines: List[str], 
                                      pattern_def: PatternDefinition, file_path: str) -> List[AntiPatternViolation]:
        """Scan code for specific pattern violations."""
        violations = []
        
        for i, line in enumerate(lines, 1):
        for rule in pattern_def.rules:
                if not self._check_rule({"code": line, "value": line.strip()}, rule):
                    # This is a violation
                    violation = AntiPatternViolation(
                        violation_id=f"{pattern_def.pattern_name}_{i}_{hash(line)}",
                        pattern_name=pattern_def.pattern_name,
                        file_path=file_path or "unknown",
                        line_number=i,
                        code_snippet=line.strip(),
                        severity=pattern_def.severity,
                        description=f"Violation of {pattern_def.pattern_name}: {pattern_def.description}",
                        suggested_fix=self._suggest_fix(pattern_def.pattern_name, rule, line)
                    )
                    violations.append(violation)
        
        return violations
    
    def _suggest_fix(self, pattern_name: str, rule: str, line: str) -> str:
        """Suggest a fix for a pattern violation."""
        suggestions = {
        "interface_naming": "Use PascalCase starting with 'I' for interfaces, 'Service' suffix for services",
        "soa_endpoint_structure": "Use lowercase with underscores for endpoints, include /openapi.json and /docs",
        "mcp_tool_naming": "Use lowercase with underscores, consider adding _tool suffix",
        "error_handling": "Add proper try-except blocks and use error_handler service",
        "logging_patterns": "Use self.logger methods and structured logging with extra data"
        }
        
        return suggestions.get(pattern_name, f"Follow the pattern: {rule}")
    
    # ============================================================================
    # OPENAPI GENERATION
    
    async def generate_openapi_spec(self, service_name: str) -> Dict[str, Any]:
        """Generate OpenAPI specification for a service."""
        try:
            capability = await self.get_capability(service_name)
            if not capability:
                raise ValueError(f"Service {service_name} not found in registry")
            
        await self.log_operation_with_telemetry("generate_openapi_spec", details={
                "service_name": service_name
        })
            
        # Generate OpenAPI spec
        openapi_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": f"{service_name.title()} Service",
                    "description": capability.description,
                    "version": capability.version
                },
                "servers": [
                    {
                        "url": f"http://localhost:8000/{service_name}",
                        "description": f"{service_name} service server"
                    }
                ],
                "paths": self._generate_paths_from_endpoints(capability.endpoints),
                "components": {
                    "schemas": self._generate_schemas_from_interface(capability.interface_name)
                }
        }
            
        self.logger.info(f"📄 Generated OpenAPI spec for {service_name}")
        return openapi_spec
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate OpenAPI spec for {service_name}: {e}")
            await self.handle_error(e, f"generate_openapi_spec_{service_name}")
            raise
    
    def _generate_paths_from_endpoints(self, endpoints: List[str]) -> Dict[str, Any]:
        """Generate OpenAPI paths from endpoint list."""
        paths = {}
        
        for endpoint in endpoints:
        # Simple path generation - can be enhanced
        path_item = {
                "get": {
                    "summary": f"Get {endpoint.replace('/', '').replace('_', ' ').title()}",
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object"
                                    }
                                }
                            }
                        }
                    }
                }
        }
        paths[endpoint] = path_item
        
        return paths
    
    def _generate_schemas_from_interface(self, interface_name: str) -> Dict[str, Any]:
        """Generate OpenAPI schemas from interface name."""
        # Simple schema generation - can be enhanced
        return {
        f"{interface_name}Request": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "object",
                        "description": "Request data"
                    }
                }
        },
        f"{interface_name}Response": {
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "description": "Operation success status"
                    },
                    "data": {
                        "type": "object",
                        "description": "Response data"
                    }
                }
        }
        }
    
    async def generate_docs(self, service_name: str) -> Dict[str, Any]:
        """Generate documentation for a service."""
        try:
            capability = await self.get_capability(service_name)
            if not capability:
                raise ValueError(f"Service {service_name} not found in registry")
            
        await self.log_operation_with_telemetry("generate_docs", details={
                "service_name": service_name
        })
            
        docs = {
                "service_name": service_name,
                "interface": capability.interface_name,
                "description": capability.description,
                "realm": capability.realm,
                "version": capability.version,
                "endpoints": capability.endpoints,
                "tools": capability.tools,
                "openapi_url": f"/{service_name}/openapi.json",
                "docs_url": f"/{service_name}/docs",
                "registered_at": capability.registered_at
        }
            
        self.logger.info(f"📚 Generated docs for {service_name}")
        return docs
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate docs for {service_name}: {e}")
            await self.handle_error(e, f"generate_docs_{service_name}")
            raise
    
    # ============================================================================
    # REGISTRY MANAGEMENT
    
    async def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status and statistics."""
        try:
            capabilities_by_realm = {}
            for capability in self.capability_registry.values():
                realm = capability.realm
                if realm not in capabilities_by_realm:
                    capabilities_by_realm[realm] = 0
                capabilities_by_realm[realm] += 1
            
        status = {
                "total_capabilities": len(self.capability_registry),
                "capabilities_by_realm": capabilities_by_realm,
                "total_patterns": len(self.pattern_registry),
                "total_violations": len(self.anti_pattern_violations),
                "service_discovery_enabled": self.service_discovery_enabled,
                "last_updated": datetime.utcnow().isoformat()
        }
            
        await self.log_operation_with_telemetry("get_registry_status", details=status)
        return status
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get registry status: {e}")
            return {"error": str(e)}
    
    async def clear_violations(self, pattern_name: str = None):
        """Clear anti-pattern violations."""
        try:
            if pattern_name:
                self.anti_pattern_violations = [
                    v for v in self.anti_pattern_violations 
                    if v.pattern_name != pattern_name
                ]
                self.logger.info(f"🧹 Cleared violations for pattern: {pattern_name}")
        else:
                self.anti_pattern_violations.clear()
                self.logger.info("🧹 Cleared all anti-pattern violations")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to clear violations: {e}")
    
    async def get_violations(self, pattern_name: str = None, severity: str = None) -> List[AntiPatternViolation]:
        """Get anti-pattern violations with optional filtering."""
        try:
            violations = self.anti_pattern_violations
            
        if pattern_name:
                violations = [v for v in violations if v.pattern_name == pattern_name]
            
        if severity:
                violations = [v for v in violations if v.severity == severity]
            
        return violations
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get violations: {e}")
            return []
