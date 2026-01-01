#!/usr/bin/env python3
"""
Pattern Management Micro-Module

Handles CRUD operations for pattern definitions.

WHAT (Module Role): I need to manage pattern definitions (add, remove, get, list)
HOW (Module Implementation): I provide CRUD operations for pattern registry
"""

from typing import Dict, Any, List, Optional
from ...models import PatternDefinition


class PatternManagementModule:
    """Handles CRUD operations for pattern definitions."""
    
    def __init__(self, logger):
        """Initialize the Pattern Management Module."""
        self.logger = logger
        self.service_name = "pattern_management"
    
    async def add_pattern(self, pattern: PatternDefinition, pattern_registry: Dict[str, PatternDefinition]) -> bool:
        """Add a new pattern to the registry."""
        try:
            if pattern.pattern_name in pattern_registry:
                self.logger.warning(f"⚠️ Pattern {pattern.pattern_name} already exists, updating...")
            
            pattern_registry[pattern.pattern_name] = pattern
            self.logger.info(f"✅ Added pattern: {pattern.pattern_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error adding pattern {pattern.pattern_name}: {e}")
            return False
    
    async def remove_pattern(self, pattern_name: str, pattern_registry: Dict[str, PatternDefinition]) -> bool:
        """Remove a pattern from the registry."""
        try:
            if pattern_name not in pattern_registry:
                self.logger.warning(f"⚠️ Pattern {pattern_name} not found in registry")
                return False
            
            del pattern_registry[pattern_name]
            self.logger.info(f"🗑️ Removed pattern: {pattern_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error removing pattern {pattern_name}: {e}")
            return False
    
    async def get_pattern(self, pattern_name: str, pattern_registry: Dict[str, PatternDefinition]) -> Optional[PatternDefinition]:
        """Get a specific pattern from the registry."""
        try:
            pattern = pattern_registry.get(pattern_name)
            if pattern:
                self.logger.info(f"📋 Retrieved pattern: {pattern_name}")
            else:
                self.logger.warning(f"⚠️ Pattern {pattern_name} not found")
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"❌ Error getting pattern {pattern_name}: {e}")
            return None
    
    async def list_patterns(self, pattern_type: str = None, pattern_registry: Dict[str, PatternDefinition] = None) -> List[PatternDefinition]:
        """List all patterns, optionally filtered by type."""
        try:
            if pattern_registry is None:
                return []
            
            patterns = list(pattern_registry.values())
            
            if pattern_type:
                patterns = [p for p in patterns if p.pattern_type == pattern_type]
            
            self.logger.info(f"📋 Listed {len(patterns)} patterns" + (f" of type {pattern_type}" if pattern_type else ""))
            return patterns
            
        except Exception as e:
            self.logger.error(f"❌ Error listing patterns: {e}")
            return []
    
    async def get_pattern_status(self, pattern_registry: Dict[str, PatternDefinition]) -> Dict[str, Any]:
        """Get pattern registry status and statistics."""
        try:
            patterns_by_type = {}
            for pattern in pattern_registry.values():
                pattern_type = pattern.pattern_type
                if pattern_type not in patterns_by_type:
                    patterns_by_type[pattern_type] = 0
                patterns_by_type[pattern_type] += 1
            
            status = {
                "total_patterns": len(pattern_registry),
                "patterns_by_type": patterns_by_type,
                "last_updated": "2024-01-01T00:00:00Z"  # Placeholder
            }
            
            self.logger.info(f"📊 Pattern registry status: {len(pattern_registry)} total patterns")
            return status
            
        except Exception as e:
            self.logger.error(f"❌ Error getting pattern status: {e}")
            return {"error": str(e)}
