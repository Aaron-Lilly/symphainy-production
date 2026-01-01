#!/usr/bin/env python3
"""
Pattern Rule Checker Micro-Module

Handles individual rule checking logic for pattern validation.

WHAT (Module Role): I need to check individual rules against patterns
HOW (Module Implementation): I implement specific rule validation logic
"""

import re
from typing import Dict, Any, List
from ...models import PatternDefinition


class PatternRuleCheckerModule:
    """Handles individual rule checking logic for pattern validation."""
    
    def __init__(self, logger):
        """Initialize the Pattern Rule Checker Module."""
        self.logger = logger
        self.service_name = "pattern_rule_checker"
    
    def check_rule(self, pattern: Dict[str, Any], rule: str) -> bool:
        """Check a specific rule against a pattern."""
        try:
            if "interface" in rule.lower():
                return self._check_interface_rule(pattern, rule)
            elif "endpoint" in rule.lower() or "api" in rule.lower():
                return self._check_endpoint_rule(pattern, rule)
            elif "tool" in rule.lower() or "mcp" in rule.lower():
                return self._check_tool_rule(pattern, rule)
            elif "service" in rule.lower():
                return self._check_service_rule(pattern, rule)
            elif "error" in rule.lower():
                return self._check_error_handling_rule(pattern, rule)
            elif "log" in rule.lower():
                return self._check_logging_rule(pattern, rule)
            else:
                # Generic rule checking
                return self._check_generic_rule(pattern, rule)
        except Exception as e:
            self.logger.error(f"❌ Error checking rule '{rule}': {e}")
            return False
    
    def _check_interface_rule(self, pattern: Dict[str, Any], rule: str) -> bool:
        """Check interface-specific rules."""
        interface_name = pattern.get("name", "")
        
        if "start with 'I'" in rule:
            return interface_name.startswith("I")
        elif "PascalCase" in rule:
            return self._is_pascal_case(interface_name)
        elif "descriptive noun" in rule:
            return len(interface_name) > 2 and interface_name[1:].isalpha()
        
        return True
    
    def _check_endpoint_rule(self, pattern: Dict[str, Any], rule: str) -> bool:
        """Check endpoint-specific rules."""
        endpoints = pattern.get("endpoints", [])
        
        if "RESTful conventions" in rule:
            return self._check_restful_conventions(endpoints)
        elif "HTTP methods" in rule:
            return self._check_http_methods(endpoints)
        elif "path structure" in rule:
            return self._check_path_structure(endpoints)
        
        return True
    
    def _check_tool_rule(self, pattern: Dict[str, Any], rule: str) -> bool:
        """Check tool-specific rules."""
        tools = pattern.get("tools", [])
        
        if "snake_case" in rule:
            return all(self._is_snake_case(tool.get("name", "")) for tool in tools)
        elif "descriptive" in rule:
            return all(len(tool.get("name", "")) > 3 for tool in tools)
        elif "not conflict" in rule:
            # This would need to check against existing tools
            return True
        
        return True
    
    def _check_service_rule(self, pattern: Dict[str, Any], rule: str) -> bool:
        """Check service-specific rules."""
        # These would typically be checked against actual service code
        # For now, we'll return True as a placeholder
        return True
    
    def _check_error_handling_rule(self, pattern: Dict[str, Any], rule: str) -> bool:
        """Check error handling rules."""
        # These would typically be checked against actual service code
        # For now, we'll return True as a placeholder
        return True
    
    def _check_logging_rule(self, pattern: Dict[str, Any], rule: str) -> bool:
        """Check logging rules."""
        # These would typically be checked against actual service code
        # For now, we'll return True as a placeholder
        return True
    
    def _check_generic_rule(self, pattern: Dict[str, Any], rule: str) -> bool:
        """Check generic rules."""
        # Generic rule checking logic
        return True
    
    def _is_pascal_case(self, text: str) -> bool:
        """Check if text is in PascalCase."""
        if not text:
            return False
        return text[0].isupper() and text[1:].islower() and text.isalpha()
    
    def _is_snake_case(self, text: str) -> bool:
        """Check if text is in snake_case."""
        if not text:
            return False
        return text.islower() and "_" in text and text.replace("_", "").isalpha()
    
    def _check_restful_conventions(self, endpoints: List[Dict[str, Any]]) -> bool:
        """Check if endpoints follow RESTful conventions."""
        for endpoint in endpoints:
            path = endpoint.get("path", "")
            method = endpoint.get("method", "")
            
            # Basic RESTful checks
            if not path.startswith("/"):
                return False
            if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                return False
        
        return True
    
    def _check_http_methods(self, endpoints: List[Dict[str, Any]]) -> bool:
        """Check if endpoints use proper HTTP methods."""
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        
        for endpoint in endpoints:
            method = endpoint.get("method", "")
            if method not in valid_methods:
                return False
        
        return True
    
    def _check_path_structure(self, endpoints: List[Dict[str, Any]]) -> bool:
        """Check if endpoints have consistent path structure."""
        for endpoint in endpoints:
            path = endpoint.get("path", "")
            
            # Basic path structure checks
            if not path.startswith("/"):
                return False
            if "//" in path:
                return False
        
        return True
