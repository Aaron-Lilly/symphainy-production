#!/usr/bin/env python3
"""
Pattern Validation Engine Micro-Module

Handles core pattern validation logic and rule checking coordination.

WHAT (Module Role): I need to coordinate pattern validation and rule checking
HOW (Module Implementation): I orchestrate validation against pattern definitions
"""

from typing import Dict, Any, List
from datetime import datetime
from ...models import PatternDefinition
from .pattern_rule_checker import PatternRuleCheckerModule


class PatternValidationEngineModule:
    """Handles core pattern validation logic and rule checking coordination."""
    
    def __init__(self, logger):
        """Initialize the Pattern Validation Engine Module."""
        self.logger = logger
        self.service_name = "pattern_validation_engine"
        self.rule_checker = PatternRuleCheckerModule(logger)
    
    async def validate_pattern(self, pattern: Dict[str, Any], pattern_registry: Dict[str, PatternDefinition]) -> Dict[str, Any]:
        """Validate a pattern against architectural rules."""
        try:
            pattern_name = pattern.get("name", "unknown")
            pattern_type = pattern.get("type", "unknown")
            
            # Get applicable patterns - only match exact type or specific patterns
            applicable_patterns = []
            if pattern_type == "interface":
                applicable_patterns = [p for p in pattern_registry.values() if p.pattern_name == "interface_naming"]
            elif pattern_type == "api":
                applicable_patterns = [p for p in pattern_registry.values() if p.pattern_name == "soa_endpoint_structure"]
            elif pattern_type == "mcp":
                applicable_patterns = [p for p in pattern_registry.values() if p.pattern_name == "mcp_tool_naming"]
            else:
                # For other types, only apply service-level patterns
                applicable_patterns = [p for p in pattern_registry.values() if p.pattern_type == "service"]
            
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
            self.logger.error(f"❌ Error validating pattern: {e}")
            return {
                "success": False,
                "pattern_name": pattern.get("name", "unknown"),
                "violations": [{"error": str(e)}],
                "validated_at": datetime.utcnow().isoformat()
            }
    
    async def _check_pattern_rules(self, pattern: Dict[str, Any], pattern_def: PatternDefinition) -> List[Dict[str, Any]]:
        """Check pattern against specific pattern rules."""
        violations = []
        
        for rule in pattern_def.rules:
            if not self.rule_checker.check_rule(pattern, rule):
                violations.append({
                    "pattern_name": pattern_def.pattern_name,
                    "rule": rule,
                    "severity": pattern_def.severity,
                    "description": pattern_def.description
                })
        
        return violations
