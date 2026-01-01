#!/usr/bin/env python3
"""
Anti-Pattern Detection Service

Handles anti-pattern scanning and violation tracking for service code
across the platform.

WHAT (Service Role): I need to detect anti-patterns and track violations
HOW (Service Implementation): I scan code for violations and maintain violation history
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../'))

from bases.foundation_service_base import FoundationServiceBase

# Direct library usage - no abstractions needed for standard libraries
import json
import re
import ast
import os
from pathlib import Path
from ..models import AntiPatternViolation, PatternDefinition


class AntiPatternDetectionService(FoundationServiceBase):
    """
    Anti-Pattern Detection Service - Code scanning and violation tracking
    
    Scans service code for anti-pattern violations and maintains violation history
    for platform-wide quality assurance.
    
    WHAT (Service Role): I need to detect anti-patterns and track violations
    HOW (Service Implementation): I scan code for violations and maintain violation history
    """
    
    def __init__(self, di_container, pattern_validation_service=None):
        """Initialize Anti-Pattern Detection Service."""
        super().__init__("antipattern_detection", di_container)
        self.pattern_validation_service = pattern_validation_service
        
        # Violation tracking
        self.anti_pattern_violations: List[AntiPatternViolation] = []
        
        self.logger.info("🔍 Anti-Pattern Detection Service initialized")
    
    async def initialize(self):
        """Initialize the Anti-Pattern Detection Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("antipattern_detection_initialize_start", success=True)
            
            await super().initialize()
            self.logger.info("🚀 Initializing Anti-Pattern Detection Service...")
            
            self.logger.info("✅ Anti-Pattern Detection Service initialized successfully")
            
            # Record health metric
            await self.record_health_metric("antipattern_detection_initialized", 1.0, {"service": "antipattern_detection"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("antipattern_detection_initialize_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "antipattern_detection_initialize")
            raise
    
    # ============================================================================
    # ANTI-PATTERN DETECTION
    
    async def detect_anti_patterns(self, service_code: str, file_path: str = None, user_context: Dict[str, Any] = None) -> List[AntiPatternViolation]:
        """Detect anti-patterns in service code."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("detect_anti_patterns_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "antipattern_detection", "read"):
                        await self.record_health_metric("detect_anti_patterns_access_denied", 1.0, {"file_path": file_path})
                        await self.log_operation_with_telemetry("detect_anti_patterns_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("detect_anti_patterns_tenant_denied", 1.0, {"file_path": file_path, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("detect_anti_patterns_complete", success=False)
                            return []
            
            violations = []
            lines = service_code.split('\n')
            
            # Get patterns from pattern validation service
            if self.pattern_validation_service:
                patterns = await self.pattern_validation_service.list_patterns()
                
                # Check each pattern
                for pattern_def in patterns:
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
            
            # Record health metric
            await self.record_health_metric("detect_anti_patterns_success", 1.0, {"file_path": file_path, "violations_count": len(violations)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("detect_anti_patterns_complete", success=True)
            
            return violations
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "detect_anti_patterns")
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
    
    def _check_rule(self, pattern: Dict[str, Any], rule: str) -> bool:
        """Check if pattern matches a specific rule."""
        try:
            import re
            
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
            self.logger.error(f"❌ Error checking rule '{rule}': {e}")
            return False
    
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
    # VIOLATION MANAGEMENT
    
    async def get_violations(self, pattern_name: str = None, severity: str = None, user_context: Dict[str, Any] = None) -> List[AntiPatternViolation]:
        """Get anti-pattern violations with optional filtering."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_violations_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "antipattern_detection", "read"):
                        await self.record_health_metric("get_violations_access_denied", 1.0, {"pattern_name": pattern_name, "severity": severity})
                        await self.log_operation_with_telemetry("get_violations_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_violations_tenant_denied", 1.0, {"pattern_name": pattern_name, "severity": severity, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_violations_complete", success=False)
                            return []
            
            violations = self.anti_pattern_violations
            
            if pattern_name:
                violations = [v for v in violations if v.pattern_name == pattern_name]
            
            if severity:
                violations = [v for v in violations if v.severity == severity]
            
            # Record health metric
            await self.record_health_metric("get_violations_success", 1.0, {"pattern_name": pattern_name, "severity": severity, "count": len(violations)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_violations_complete", success=True)
            
            return violations
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_violations")
            return []
    
    async def clear_violations(self, pattern_name: str = None):
        """Clear anti-pattern violations."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("clear_violations_start", success=True)
            
            if pattern_name:
                self.anti_pattern_violations = [
                    v for v in self.anti_pattern_violations 
                    if v.pattern_name != pattern_name
                ]
                self.logger.info(f"🧹 Cleared violations for pattern: {pattern_name}")
            else:
                self.anti_pattern_violations.clear()
                self.logger.info("🧹 Cleared all anti-pattern violations")
            
            # Record health metric
            await self.record_health_metric("clear_violations_success", 1.0, {"pattern_name": pattern_name})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("clear_violations_complete", success=True)
                
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "clear_violations")
    
    async def get_violation_summary(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get violation summary statistics."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_violation_summary_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "antipattern_detection", "read"):
                        await self.record_health_metric("get_violation_summary_access_denied", 1.0, {})
                        await self.log_operation_with_telemetry("get_violation_summary_complete", success=False)
                        return {}
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_violation_summary_tenant_denied", 1.0, {"tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_violation_summary_complete", success=False)
                            return {}
            
            violations_by_pattern = {}
            violations_by_severity = {}
            violations_by_file = {}
            
            for violation in self.anti_pattern_violations:
                # Count by pattern
                pattern = violation.pattern_name
                if pattern not in violations_by_pattern:
                    violations_by_pattern[pattern] = 0
                violations_by_pattern[pattern] += 1
                
                # Count by severity
                severity = violation.severity
                if severity not in violations_by_severity:
                    violations_by_severity[severity] = 0
                violations_by_severity[severity] += 1
                
                # Count by file
                file_path = violation.file_path
                if file_path not in violations_by_file:
                    violations_by_file[file_path] = 0
                violations_by_file[file_path] += 1
            
            summary = {
                "total_violations": len(self.anti_pattern_violations),
                "violations_by_pattern": violations_by_pattern,
                "violations_by_severity": violations_by_severity,
                "violations_by_file": violations_by_file,
                "last_updated": datetime.utcnow().isoformat()
            }
            
            # Record health metric
            await self.record_health_metric("get_violation_summary_success", 1.0, {"total_violations": len(self.anti_pattern_violations)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_violation_summary_complete", success=True)
            
            return summary
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_violation_summary")
            return {"error": str(e), "error_code": type(e).__name__}
    
    async def get_violations_for_file(self, file_path: str, user_context: Dict[str, Any] = None) -> List[AntiPatternViolation]:
        """Get all violations for a specific file."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_violations_for_file_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "antipattern_detection", "read"):
                        await self.record_health_metric("get_violations_for_file_access_denied", 1.0, {"file_path": file_path})
                        await self.log_operation_with_telemetry("get_violations_for_file_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_violations_for_file_tenant_denied", 1.0, {"file_path": file_path, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_violations_for_file_complete", success=False)
                            return []
            
            violations = [
                v for v in self.anti_pattern_violations 
                if v.file_path == file_path
            ]
            
            # Record health metric
            await self.record_health_metric("get_violations_for_file_success", 1.0, {"file_path": file_path, "count": len(violations)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_violations_for_file_complete", success=True)
            
            return violations
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_violations_for_file")
            return []
    
    async def get_violations_by_severity(self, severity: str, user_context: Dict[str, Any] = None) -> List[AntiPatternViolation]:
        """Get all violations of a specific severity."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("get_violations_by_severity_start", success=True)
            
            # Security validation (zero-trust: secure by design)
            if user_context:
                security = self.get_security()
                if security:
                    if not await security.check_permissions(user_context, "antipattern_detection", "read"):
                        await self.record_health_metric("get_violations_by_severity_access_denied", 1.0, {"severity": severity})
                        await self.log_operation_with_telemetry("get_violations_by_severity_complete", success=False)
                        return []
            
            # Tenant validation (multi-tenant support)
            if user_context:
                tenant = self.get_tenant()
                if tenant:
                    tenant_id = user_context.get("tenant_id")
                    if tenant_id:
                        if not await tenant.validate_tenant_access(tenant_id):
                            await self.record_health_metric("get_violations_by_severity_tenant_denied", 1.0, {"severity": severity, "tenant_id": tenant_id})
                            await self.log_operation_with_telemetry("get_violations_by_severity_complete", success=False)
                            return []
            
            violations = [
                v for v in self.anti_pattern_violations 
                if v.severity == severity
            ]
            
            # Record health metric
            await self.record_health_metric("get_violations_by_severity_success", 1.0, {"severity": severity, "count": len(violations)})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("get_violations_by_severity_complete", success=True)
            
            return violations
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "get_violations_by_severity")
            return []

    async def shutdown(self):
        """Shutdown the Anti-Pattern Detection Service."""
        try:
            # Start telemetry tracking
            await self.log_operation_with_telemetry("antipattern_detection_shutdown_start", success=True)
            
            self.logger.info("🛑 Shutting down Anti-Pattern Detection Service...")
            
            # Clear violations registry
            self.anti_pattern_violations.clear()
            
            self.logger.info("✅ Anti-Pattern Detection Service shutdown complete")
            
            # Record health metric
            await self.record_health_metric("antipattern_detection_shutdown", 1.0, {"service": "antipattern_detection"})
            
            # End telemetry tracking
            await self.log_operation_with_telemetry("antipattern_detection_shutdown_complete", success=True)
            
        except Exception as e:
            # Use enhanced error handling with audit
            await self.handle_error_with_audit(e, "antipattern_detection_shutdown")
            self.logger.error(f"❌ Error during Anti-Pattern Detection Service shutdown: {e}")


