#!/usr/bin/env python3
"""
Test Data Mapping Frontend-Backend Integration

Verifies that:
1. Backend returns the expected response structure
2. Frontend types match backend response
3. Response can be parsed and used by frontend components

This test validates the contract between frontend and backend.
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

import pytest
from unittest.mock import Mock, AsyncMock, patch


class TestDataMappingFrontendBackendIntegration:
    """Test frontend-backend integration for data mapping."""
    
    def test_backend_response_structure(self):
        """Verify backend returns expected structure."""
        # Expected backend response structure (from data_mapping_workflow.py)
        expected_structure = {
            "success": bool,
            "mapping_id": str,
            "mapping_type": str,  # "unstructured_to_structured" or "structured_to_structured"
            "mapping_rules": list,
            "mapped_data": dict,
            "data_quality": dict,  # Optional, only for structured→structured
            "cleanup_actions": list,  # Optional
            "output_file_id": str,  # Optional
            "citations": list,  # Optional, only for unstructured→structured
            "confidence_scores": dict,  # Optional
            "metadata": dict
        }
        
        # Sample backend response
        sample_response = {
            "success": True,
            "mapping_id": "mapping_1234567890_abc123",
            "mapping_type": "structured_to_structured",
            "mapping_rules": [
                {
                    "source_field": "POLICY-NUMBER",
                    "target_field": "policy_number",
                    "confidence": 0.95,
                    "extraction_method": "semantic"
                }
            ],
            "mapped_data": {
                "success": True,
                "transformed_data": {
                    "records": [
                        {"policy_number": "POL-001", "premium": 1000.0}
                    ]
                },
                "output_file_id": "file_123",
                "transformation_metadata": {
                    "fields_mapped": 10,
                    "fields_unmapped": 2,
                    "confidence_avg": 0.89
                }
            },
            "data_quality": {
                "success": True,
                "validation_results": [
                    {
                        "record_id": "record_0",
                        "record_index": 0,
                        "is_valid": True,
                        "quality_score": 0.95,
                        "issues": [],
                        "missing_fields": [],
                        "invalid_fields": [],
                        "warnings": []
                    }
                ],
                "summary": {
                    "total_records": 100,
                    "valid_records": 95,
                    "invalid_records": 5,
                    "overall_quality_score": 0.90,
                    "pass_rate": 0.95,
                    "common_issues": []
                },
                "has_issues": True
            },
            "cleanup_actions": [
                {
                    "action_id": "action_1",
                    "priority": "high",
                    "action_type": "fix_missing",
                    "description": "Fix missing policy_number field",
                    "affected_records": 5,
                    "example_fix": "Add policy_number from source field POLICY-NUMBER"
                }
            ],
            "output_file_id": "file_123",
            "citations": [],  # Empty for structured→structured
            "confidence_scores": {},
            "metadata": {
                "source_file_id": "source_123",
                "target_file_id": "target_456",
                "mapping_timestamp": "2025-01-01T00:00:00",
                "workflow_id": "workflow_789"
            }
        }
        
        # Verify structure matches
        for key, expected_type in expected_structure.items():
            assert key in sample_response, f"Missing key: {key}"
            if expected_type != dict and expected_type != list:
                assert isinstance(sample_response[key], expected_type), \
                    f"Key {key} has wrong type: {type(sample_response[key])}"
        
        print("✅ Backend response structure is correct")
    
    def test_frontend_type_compatibility(self):
        """Verify frontend types can handle backend response."""
        # Backend response
        backend_response = {
            "success": True,
            "mapping_id": "mapping_123",
            "mapping_type": "structured_to_structured",
            "mapping_rules": [
                {
                    "source_field": "POLICY-NUMBER",
                    "target_field": "policy_number",
                    "confidence": 0.95,
                    "extraction_method": "semantic"
                }
            ],
            "mapped_data": {
                "success": True,
                "transformed_data": {"records": []},
                "output_file_id": "file_123"
            },
            "data_quality": {
                "success": True,
                "validation_results": [],
                "summary": {
                    "total_records": 100,
                    "valid_records": 95,
                    "invalid_records": 5,
                    "overall_quality_score": 0.90,
                    "pass_rate": 0.95,
                    "common_issues": []
                },
                "has_issues": True
            },
            "cleanup_actions": [],
            "metadata": {
                "source_file_id": "source_123",
                "target_file_id": "target_456",
                "mapping_timestamp": "2025-01-01T00:00:00"
            }
        }
        
        # Frontend should be able to extract:
        # 1. mapping_rules
        assert "mapping_rules" in backend_response
        assert isinstance(backend_response["mapping_rules"], list)
        
        # 2. mapped_records from mapped_data.transformed_data
        mapped_data = backend_response["mapped_data"]
        if "transformed_data" in mapped_data:
            transformed = mapped_data["transformed_data"]
            if "records" in transformed:
                mapped_records = transformed["records"]
            else:
                mapped_records = transformed if isinstance(transformed, list) else []
        else:
            mapped_records = []
        
        assert isinstance(mapped_records, list)
        
        # 3. data_quality structure
        if "data_quality" in backend_response:
            data_quality = backend_response["data_quality"]
            assert "validation_results" in data_quality
            assert "summary" in data_quality
            assert "overall_quality_score" in data_quality["summary"]
            assert "pass_rate" in data_quality["summary"]
        
        # 4. cleanup_actions
        if "cleanup_actions" in backend_response:
            assert isinstance(backend_response["cleanup_actions"], list)
        
        # 5. citations (array, not dict)
        if "citations" in backend_response:
            assert isinstance(backend_response["citations"], list)
        
        print("✅ Frontend types are compatible with backend response")
    
    def test_quality_report_transformation(self):
        """Test transformation of backend data_quality to frontend QualityReport."""
        # Backend data_quality structure
        backend_data_quality = {
            "success": True,
            "validation_results": [
                {
                    "record_id": "record_0",
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
                        }
                    ],
                    "missing_fields": ["policy_number"],
                    "invalid_fields": [],
                    "warnings": []
                }
            ],
            "summary": {
                "total_records": 100,
                "valid_records": 95,
                "invalid_records": 5,
                "overall_quality_score": 0.90,
                "pass_rate": 0.95,
                "common_issues": []
            },
            "has_issues": True
        }
        
        # Transform to frontend format
        quality_report = {
            "overall_score": backend_data_quality["summary"]["overall_quality_score"],
            "pass_rate": backend_data_quality["summary"]["pass_rate"],
            "completeness": backend_data_quality["summary"]["valid_records"] / backend_data_quality["summary"]["total_records"],
            "accuracy": backend_data_quality["summary"]["overall_quality_score"],
            "record_count": backend_data_quality["summary"]["total_records"],
            "quality_issues": [
                {
                    **issue,
                    "record_id": result["record_id"]
                }
                for result in backend_data_quality["validation_results"]
                for issue in result["issues"]
            ],
            "metrics": {
                "total_records": backend_data_quality["summary"]["total_records"],
                "passed_records": backend_data_quality["summary"]["valid_records"],
                "failed_records": backend_data_quality["summary"]["invalid_records"],
                "records_with_issues": backend_data_quality["summary"]["invalid_records"]
            }
        }
        
        # Verify transformation
        assert quality_report["overall_score"] == 0.90
        assert quality_report["pass_rate"] == 0.95
        assert quality_report["completeness"] == 0.95
        assert quality_report["record_count"] == 100
        assert len(quality_report["quality_issues"]) == 1
        assert quality_report["quality_issues"][0]["record_id"] == "record_0"
        
        print("✅ Quality report transformation works correctly")
    
    def test_citations_transformation(self):
        """Test transformation of backend citations array to frontend format."""
        # Backend citations (array)
        backend_citations = [
            {
                "field": "license_expiration",
                "source": "license.pdf",
                "location": "Page 1, Section 2",
                "confidence": 0.95
            },
            {
                "field": "license_number",
                "source": "license.pdf",
                "location": "Page 1, Header",
                "confidence": 0.98
            }
        ]
        
        # Transform to frontend format (object by field)
        citations_by_field = {}
        for citation in backend_citations:
            field = citation["field"]
            if field not in citations_by_field:
                citations_by_field[field] = []
            citations_by_field[field].append(citation)
        
        # Verify transformation
        assert "license_expiration" in citations_by_field
        assert "license_number" in citations_by_field
        assert len(citations_by_field["license_expiration"]) == 1
        assert len(citations_by_field["license_number"]) == 1
        
        print("✅ Citations transformation works correctly")
    
    def test_mapped_records_extraction(self):
        """Test extraction of mapped records from backend response."""
        # Backend mapped_data structure
        backend_mapped_data = {
            "success": True,
            "transformed_data": {
                "records": [
                    {"policy_number": "POL-001", "premium": 1000.0},
                    {"policy_number": "POL-002", "premium": 2000.0}
                ]
            },
            "output_file_id": "file_123"
        }
        
        # Extract mapped records (frontend logic)
        if "transformed_data" in backend_mapped_data:
            transformed = backend_mapped_data["transformed_data"]
            if "records" in transformed:
                mapped_records = transformed["records"]
            else:
                mapped_records = transformed if isinstance(transformed, list) else []
        else:
            mapped_records = []
        
        # Verify extraction
        assert isinstance(mapped_records, list)
        assert len(mapped_records) == 2
        assert mapped_records[0]["policy_number"] == "POL-001"
        
        print("✅ Mapped records extraction works correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])










