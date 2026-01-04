#!/usr/bin/env python3
"""
Data Quality Validation Service - Insights Realm

WHAT: Validates data quality and generates cleanup actions
HOW: Validates records against target schema and identifies quality issues

Use cases:
- Legacy policy records → New data model validation
- Any structured→structured mapping with quality requirements
"""

import os
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

sys.path.insert(0, os.path.abspath('../../../../../../'))

from bases.realm_service_base import RealmServiceBase


class DataQualityValidationService(RealmServiceBase):
    """
    Data Quality Validation Service - Validates data quality and generates cleanup actions.
    
    Provides:
    - Record-level validation against target schema
    - Quality issue identification
    - Quality metrics calculation
    - Cleanup action recommendations
    """
    
    def __init__(self, service_name: str, realm_name: str, platform_gateway: Any, di_container: Any):
        """Initialize Data Quality Validation Service."""
        super().__init__(service_name, realm_name, platform_gateway, di_container)
        
        # Smart City service APIs (will be initialized in initialize())
        self.data_steward = None
        self.data_steward = None
        self.nurse = None
    
    async def initialize(self) -> bool:
        """Initialize Data Quality Validation Service."""
        await super().initialize()
        
        try:
            self.logger.info("🚀 Initializing Data Quality Validation Service...")
            
            # Get Smart City services
            self.data_steward = await self.get_smart_city_service("DataStewardService")
            self.data_steward = await self.get_smart_city_service("DataStewardService")
            self.nurse = await self.get_smart_city_service("NurseService")
            
            self.logger.info("✅ Data Quality Validation Service initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Data Quality Validation Service: {e}")
            await self.handle_error_with_audit(e, "initialize")
            return False
    
    async def validate_records(
        self,
        records: List[Dict[str, Any]],
        target_schema: Dict[str, Any],
        mapping_rules: List[Dict[str, Any]],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate records against target schema.
        
        Args:
            records: List of source records to validate
            target_schema: Target schema definition
            mapping_rules: Mapping rules (source field → target field)
            user_context: User context
        
        Returns:
        {
            "success": True,
            "validation_results": [
                {
                    "record_id": "record_1",
                    "record_index": 0,
                    "is_valid": False,
                    "quality_score": 0.65,
                    "issues": [
                        {
                            "field": "policy_number",
                            "issue_type": "missing_required",
                            "severity": "error",
                            "message": "Required field 'policy_number' is missing",
                            "source_field": "POLICY-NUMBER",
                            "target_field": "policy_number"
                        },
                        ...
                    ],
                    "missing_fields": ["policy_number"],
                    "invalid_fields": ["premium_amount"],
                    "warnings": ["issue_date"]
                },
                ...
            ],
            "summary": {
                "total_records": 1000,
                "valid_records": 950,
                "invalid_records": 50,
                "overall_quality_score": 0.85,
                "common_issues": [...]
            }
        }
        """
        try:
            await self.log_operation_with_telemetry("validate_records_start", success=True, metadata={
                "record_count": len(records)
            })
            
            # Extract target schema fields
            target_fields = target_schema.get("fields", [])
            required_fields = [f["field_name"] for f in target_fields if f.get("required", False)]
            field_types = {f["field_name"]: f.get("field_type", "string") for f in target_fields}
            
            # Build mapping lookup (source_field → target_field)
            mapping_lookup = {}
            for rule in mapping_rules:
                source_field = rule.get("source_field")
                target_field = rule.get("target_field")
                if source_field and target_field:
                    mapping_lookup[source_field] = target_field
            
            validation_results = []
            total_issues = 0
            
            # Validate each record
            for idx, record in enumerate(records):
                record_id = record.get("record_id") or f"record_{idx}"
                record_issues = []
                missing_fields = []
                invalid_fields = []
                warnings = []
                
                # Check required fields
                for target_field in required_fields:
                    # Find source field that maps to this target field
                    source_field = None
                    for source, target in mapping_lookup.items():
                        if target == target_field:
                            source_field = source
                            break
                    
                    # Check if field exists in record
                    if source_field and source_field in record:
                        value = record[source_field]
                        if not value or (isinstance(value, str) and value.strip() == ""):
                            missing_fields.append(target_field)
                            record_issues.append({
                                "field": target_field,
                                "issue_type": "missing_required",
                                "severity": "error",
                                "message": f"Required field '{target_field}' is missing or empty",
                                "source_field": source_field,
                                "target_field": target_field
                            })
                    elif not source_field:
                        # No mapping found - field is missing
                        missing_fields.append(target_field)
                        record_issues.append({
                            "field": target_field,
                            "issue_type": "missing_required",
                            "severity": "error",
                            "message": f"Required field '{target_field}' has no source mapping",
                            "source_field": None,
                            "target_field": target_field
                        })
                
                # Check data types
                for source_field, target_field in mapping_lookup.items():
                    if source_field in record:
                        value = record[source_field]
                        expected_type = field_types.get(target_field, "string")
                        
                        # Type validation
                        type_valid = self._validate_type(value, expected_type)
                        if not type_valid:
                            invalid_fields.append(target_field)
                            record_issues.append({
                                "field": target_field,
                                "issue_type": "invalid_type",
                                "severity": "error",
                                "message": f"Field '{target_field}' must be {expected_type}, got: {type(value).__name__}",
                                "source_field": source_field,
                                "target_field": target_field,
                                "source_value": value,
                                "expected_type": expected_type
                            })
                        
                        # Format validation (for dates, emails, etc.)
                        if expected_type == "date":
                            format_valid = self._validate_date_format(value)
                            if not format_valid:
                                warnings.append(target_field)
                                record_issues.append({
                                    "field": target_field,
                                    "issue_type": "invalid_format",
                                    "severity": "warning",
                                    "message": f"Date format should be YYYY-MM-DD, got: {value}",
                                    "source_field": source_field,
                                    "target_field": target_field,
                                    "source_value": value,
                                    "expected_format": "YYYY-MM-DD"
                                })
                
                # Calculate quality score
                total_checks = len(required_fields) + len(mapping_lookup)
                passed_checks = total_checks - len(record_issues)
                quality_score = passed_checks / total_checks if total_checks > 0 else 0.0
                
                validation_results.append({
                    "record_id": record_id,
                    "record_index": idx,
                    "is_valid": len(record_issues) == 0,
                    "quality_score": quality_score,
                    "issues": record_issues,
                    "missing_fields": missing_fields,
                    "invalid_fields": invalid_fields,
                    "warnings": warnings
                })
                
                total_issues += len(record_issues)
            
            # Calculate summary
            valid_records = sum(1 for r in validation_results if r["is_valid"])
            invalid_records = len(validation_results) - valid_records
            overall_quality_score = sum(r["quality_score"] for r in validation_results) / len(validation_results) if validation_results else 0.0
            
            # Identify common issues
            issue_counts = {}
            for result in validation_results:
                for issue in result["issues"]:
                    issue_key = f"{issue['issue_type']}:{issue['field']}"
                    issue_counts[issue_key] = issue_counts.get(issue_key, 0) + 1
            
            common_issues = [
                {
                    "issue_type": key.split(":")[0],
                    "field": key.split(":")[1],
                    "count": count,
                    "percentage": (count / len(validation_results)) * 100
                }
                for key, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            await self.log_operation_with_telemetry("validate_records_complete", success=True, details={
                "total_records": len(records),
                "valid_records": valid_records,
                "invalid_records": invalid_records,
                "overall_quality_score": overall_quality_score
            })
            
            return {
                "success": True,
                "validation_results": validation_results,
                "summary": {
                    "total_records": len(records),
                    "valid_records": valid_records,
                    "invalid_records": invalid_records,
                    "overall_quality_score": overall_quality_score,
                    "pass_rate": valid_records / len(records) if records else 0.0,
                    "common_issues": common_issues
                },
                "has_issues": invalid_records > 0
            }
            
        except Exception as e:
            self.logger.error(f"❌ Record validation failed: {e}")
            await self.handle_error_with_audit(e, "validate_records")
            await self.log_operation_with_telemetry("validate_records_complete", success=False, details={"error": str(e)})
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type."""
        if value is None:
            return False
        
        type_mapping = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "float": float,
            "boolean": bool,
            "date": str,  # Dates are strings in ISO format
            "datetime": str
        }
        
        expected_python_type = type_mapping.get(expected_type.lower(), str)
        
        if isinstance(expected_python_type, tuple):
            return isinstance(value, expected_python_type)
        else:
            return isinstance(value, expected_python_type)
    
    def _validate_date_format(self, value: Any) -> bool:
        """Validate date format (YYYY-MM-DD)."""
        if not isinstance(value, str):
            return False
        
        import re
        # Check for YYYY-MM-DD format
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(date_pattern, value))
    
    async def generate_cleanup_actions(
        self,
        validation_results: Dict[str, Any],
        source_file_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate actionable cleanup recommendations.
        
        Returns:
        {
            "success": True,
            "cleanup_actions": [
                {
                    "action_id": "action_1",
                    "priority": "high",
                    "action_type": "fix_missing_fields",
                    "description": "Add missing 'policy_number' field to 25 records",
                    "affected_records": 25,
                    "affected_fields": ["policy_number"],
                    "recommendation": "Update source file to include 'policy_number' for records: [1, 5, 12, ...]",
                    "example_fix": {...}
                },
                ...
            ],
            "summary": {...}
        }
        """
        try:
            await self.log_operation_with_telemetry("generate_cleanup_actions_start", success=True)
            
            validation_data = validation_results.get("validation_results", [])
            summary = validation_results.get("summary", {})
            
            # Group issues by type and field
            issue_groups = {}
            for result in validation_data:
                for issue in result.get("issues", []):
                    issue_key = f"{issue['issue_type']}:{issue['field']}"
                    if issue_key not in issue_groups:
                        issue_groups[issue_key] = {
                            "issue_type": issue["issue_type"],
                            "field": issue["field"],
                            "severity": issue["severity"],
                            "affected_records": [],
                            "examples": []
                        }
                    issue_groups[issue_key]["affected_records"].append(result["record_id"])
                    if len(issue_groups[issue_key]["examples"]) < 3:
                        issue_groups[issue_key]["examples"].append({
                            "record_id": result["record_id"],
                            "issue": issue
                        })
            
            # Generate cleanup actions
            cleanup_actions = []
            action_id_counter = 1
            
            for issue_key, issue_group in issue_groups.items():
                issue_type = issue_group["issue_type"]
                field = issue_group["field"]
                affected_count = len(issue_group["affected_records"])
                severity = issue_group["severity"]
                
                # Determine priority
                if severity == "error" and affected_count > 10:
                    priority = "high"
                elif severity == "error":
                    priority = "medium"
                else:
                    priority = "low"
                
                # Generate action based on issue type
                if issue_type == "missing_required":
                    action = {
                        "action_id": f"action_{action_id_counter}",
                        "priority": priority,
                        "action_type": "fix_missing_fields",
                        "description": f"Add missing '{field}' field to {affected_count} records",
                        "affected_records": affected_count,
                        "affected_fields": [field],
                        "recommendation": f"Update source file to include '{field}' for records: {', '.join(issue_group['affected_records'][:10])}{'...' if affected_count > 10 else ''}",
                        "example_fix": {
                            "record_id": issue_group["examples"][0]["record_id"] if issue_group["examples"] else None,
                            "missing_field": field,
                            "suggested_value": None,  # Could be inferred in future
                            "location_hint": f"Check source system field mapping for '{field}'"
                        }
                    }
                elif issue_type == "invalid_type":
                    action = {
                        "action_id": f"action_{action_id_counter}",
                        "priority": priority,
                        "action_type": "fix_invalid_types",
                        "description": f"Fix invalid data types for '{field}' field",
                        "affected_records": affected_count,
                        "affected_fields": [field],
                        "recommendation": f"Convert '{field}' values to correct type. Check source system data type.",
                        "example_fix": {
                            "record_id": issue_group["examples"][0]["record_id"] if issue_group["examples"] else None,
                            "invalid_field": field,
                            "current_value": issue_group["examples"][0]["issue"].get("source_value") if issue_group["examples"] else None,
                            "expected_type": issue_group["examples"][0]["issue"].get("expected_type") if issue_group["examples"] else None,
                            "suggestion": f"Check source system for correct {field} data type"
                        }
                    }
                elif issue_type == "invalid_format":
                    action = {
                        "action_id": f"action_{action_id_counter}",
                        "priority": priority,
                        "action_type": "fix_date_format",
                        "description": f"Standardize date format for '{field}' field",
                        "affected_records": affected_count,
                        "affected_fields": [field],
                        "recommendation": f"Convert dates to 'YYYY-MM-DD' format",
                        "example_fix": {
                            "record_id": issue_group["examples"][0]["record_id"] if issue_group["examples"] else None,
                            "field": field,
                            "current_value": issue_group["examples"][0]["issue"].get("source_value") if issue_group["examples"] else None,
                            "expected_format": issue_group["examples"][0]["issue"].get("expected_format") if issue_group["examples"] else None,
                            "transformed_value": None  # Could be calculated in future
                        }
                    }
                else:
                    # Generic action
                    action = {
                        "action_id": f"action_{action_id_counter}",
                        "priority": priority,
                        "action_type": "fix_generic",
                        "description": f"Fix {issue_type} issues for '{field}' field",
                        "affected_records": affected_count,
                        "affected_fields": [field],
                        "recommendation": f"Review and fix {issue_type} issues for field '{field}'",
                        "example_fix": {
                            "record_id": issue_group["examples"][0]["record_id"] if issue_group["examples"] else None,
                            "field": field,
                            "issue": issue_group["examples"][0]["issue"] if issue_group["examples"] else None
                        }
                    }
                
                cleanup_actions.append(action)
                action_id_counter += 1
            
            # Sort by priority (high, medium, low)
            priority_order = {"high": 0, "medium": 1, "low": 2}
            cleanup_actions.sort(key=lambda x: priority_order.get(x["priority"], 3))
            
            # Calculate summary
            high_priority = sum(1 for a in cleanup_actions if a["priority"] == "high")
            medium_priority = sum(1 for a in cleanup_actions if a["priority"] == "medium")
            low_priority = sum(1 for a in cleanup_actions if a["priority"] == "low")
            
            # Estimate fix time (rough estimate)
            estimated_hours = high_priority * 2 + medium_priority * 1 + low_priority * 0.5
            estimated_time = f"{int(estimated_hours)}-{int(estimated_hours * 1.5)} hours" if estimated_hours > 0 else "Less than 1 hour"
            
            await self.log_operation_with_telemetry("generate_cleanup_actions_complete", success=True, details={
                "total_actions": len(cleanup_actions),
                "high_priority": high_priority
            })
            
            return {
                "success": True,
                "cleanup_actions": cleanup_actions,
                "summary": {
                    "total_actions": len(cleanup_actions),
                    "high_priority": high_priority,
                    "medium_priority": medium_priority,
                    "low_priority": low_priority,
                    "estimated_fix_time": estimated_time
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup action generation failed: {e}")
            await self.handle_error_with_audit(e, "generate_cleanup_actions")
            await self.log_operation_with_telemetry("generate_cleanup_actions_complete", success=False, details={"error": str(e)})
            return {
                "success": False,
                "error": str(e)
            }













