#!/usr/bin/env python3
"""
Simple Test Script for Insurance Agents

Tests agent methods directly without full initialization.
This is more effective for testing agent logic without complex mocking.
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
symphainy_platform_path = os.path.join(project_root, 'symphainy-platform')
sys.path.insert(0, symphainy_platform_path)


def print_header(title: str):
    """Print test section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_result(test_name: str, success: bool, message: str = ""):
    """Print test result."""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status}: {test_name}")
    if message:
        print(f"   {message}")


async def test_liaison_agent_guidance():
    """Test Insurance Liaison Agent guidance methods."""
    print_header("TEST: Insurance Liaison Agent Guidance")
    
    try:
        from backend.business_enablement.agents.insurance_liaison_agent import InsuranceLiaisonAgent
        
        # Create minimal agent instance (just for testing methods)
        # We'll test the guidance methods directly
        agent = InsuranceLiaisonAgent.__new__(InsuranceLiaisonAgent)
        agent.logger = None
        
        # Test all guidance methods
        tests = [
            ("Ingestion Guidance", agent._get_ingestion_guidance),
            ("Mapping Guidance", agent._get_mapping_guidance),
            ("Routing Guidance", agent._get_routing_guidance),
            ("Wave Guidance", agent._get_wave_guidance),
            ("Tracking Guidance", agent._get_tracking_guidance),
            ("Validation Guidance", agent._get_validation_guidance),
            ("Rollback Guidance", agent._get_rollback_guidance),
            ("General Guidance", agent._get_general_guidance)
        ]
        
        all_passed = True
        for test_name, method in tests:
            try:
                guidance = method()
                assert guidance is not None
                assert isinstance(guidance, str)
                assert len(guidance) > 0
                print_result(test_name, True, f"{len(guidance)} characters")
            except Exception as e:
                print_result(test_name, False, str(e))
                all_passed = False
        
        # Test suggested actions
        try:
            actions = agent._get_suggested_actions("ingest")
            assert actions is not None
            assert isinstance(actions, list)
            assert len(actions) > 0
            print_result("Suggested Actions", True, f"{len(actions)} actions")
        except Exception as e:
            print_result("Suggested Actions", False, str(e))
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_result("Liaison Agent Tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_mapper_agent_pattern_learning():
    """Test Universal Mapper Agent pattern learning."""
    print_header("TEST: Universal Mapper Agent - Pattern Learning")
    
    try:
        from backend.business_enablement.agents.specialists.universal_mapper_specialist import UniversalMapperSpecialist
        
        # Create minimal agent instance
        agent = UniversalMapperSpecialist.__new__(UniversalMapperSpecialist)
        agent.logger = None
        agent.pattern_cache = {}
        
        # Test semantic similarity
        tests = [
            ("Exact Match", ("policy_id", "policy_id"), 1.0),
            ("Partial Match", ("pol_id", "policy_id"), lambda x: x > 0.0),  # Any similarity is good for partial
            ("Different Fields", ("policy_id", "premium"), lambda x: x < 0.5)
        ]
        
        all_passed = True
        for test_name, (field1, field2), expected in tests:
            try:
                similarity = agent._calculate_semantic_similarity(field1, field2)
                if callable(expected):
                    result = expected(similarity)
                else:
                    result = abs(similarity - expected) < 0.1
                
                print_result(f"Semantic Similarity: {test_name}", result, f"{similarity:.2f}")
                if not result:
                    all_passed = False
            except Exception as e:
                print_result(f"Semantic Similarity: {test_name}", False, str(e))
                all_passed = False
        
        # Test pattern extraction
        try:
            source_schema = {
                "fields": [
                    {"name": "pol_id", "type": "string"},
                    {"name": "prem_amt", "type": "number"}
                ]
            }
            target_schema = {
                "fields": [
                    {"name": "policy_id", "type": "string"},
                    {"name": "premium", "type": "number"}
                ]
            }
            mapping_rules = {
                "rules": [
                    {"source": "pol_id", "target": "policy_id", "transformation": "direct"},
                    {"source": "prem_amt", "target": "premium", "transformation": "direct"}
                ]
            }
            
            patterns = agent._extract_mapping_patterns(source_schema, target_schema, mapping_rules)
            assert len(patterns) == 2
            assert patterns[0]["source_field"] == "pol_id"
            assert patterns[0]["target_field"] == "policy_id"
            
            print_result("Pattern Extraction", True, f"{len(patterns)} patterns extracted")
        except Exception as e:
            print_result("Pattern Extraction", False, str(e))
            all_passed = False
        
        # Test field type retrieval
        try:
            fields = [{"name": "test_field", "type": "string"}]
            field_type = agent._get_field_type(fields, "test_field")
            assert field_type == "string"
            print_result("Field Type Retrieval", True)
        except Exception as e:
            print_result("Field Type Retrieval", False, str(e))
            all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_result("Mapper Agent Tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_mapper_agent_validation():
    """Test Universal Mapper Agent validation methods."""
    print_header("TEST: Universal Mapper Agent - Validation")
    
    try:
        from backend.business_enablement.agents.specialists.universal_mapper_specialist import UniversalMapperSpecialist
        
        agent = UniversalMapperSpecialist.__new__(UniversalMapperSpecialist)
        agent.logger = None
        
        # Test completeness validation
        try:
            source_schema = {
                "fields": [
                    {"name": "field1", "type": "string"},
                    {"name": "field2", "type": "number"}
                ]
            }
            target_schema = {
                "fields": [
                    {"name": "field1", "type": "string"},
                    {"name": "field2", "type": "number"}
                ]
            }
            
            # Complete mapping
            complete_mapping = {
                "rules": [
                    {"source": "field1", "target": "field1"},
                    {"source": "field2", "target": "field2"}
                ]
            }
            completeness = agent._validate_completeness(source_schema, target_schema, complete_mapping)
            assert completeness["is_complete"] is True
            print_result("Completeness Validation (Complete)", True)
            
            # Incomplete mapping
            incomplete_mapping = {
                "rules": [
                    {"source": "field1", "target": "field1"}
                ]
            }
            completeness = agent._validate_completeness(source_schema, target_schema, incomplete_mapping)
            assert completeness["is_complete"] is False
            assert len(completeness["unmapped_source_fields"]) > 0
            print_result("Completeness Validation (Incomplete)", True)
            
        except Exception as e:
            print_result("Completeness Validation", False, str(e))
            return False
        
        # Test correctness validation
        try:
            correct_mapping = {
                "rules": [
                    {"source": "field1", "target": "field1"},
                    {"source": "field2", "target": "field2"}
                ]
            }
            correctness = agent._validate_correctness(source_schema, target_schema, correct_mapping)
            assert correctness["is_correct"] is True
            print_result("Correctness Validation (Correct)", True)
            
            # Incorrect mapping (non-existent field)
            incorrect_mapping = {
                "rules": [
                    {"source": "field1", "target": "nonexistent"}
                ]
            }
            correctness = agent._validate_correctness(source_schema, target_schema, incorrect_mapping)
            assert correctness["is_correct"] is False
            assert len(correctness["issues"]) > 0
            print_result("Correctness Validation (Incorrect)", True)
            
        except Exception as e:
            print_result("Correctness Validation", False, str(e))
            return False
        
        # Test type compatibility
        try:
            assert agent._are_types_compatible("string", "string") is True
            assert agent._are_types_compatible("number", "integer") is True
            assert agent._are_types_compatible("string", "number") is False
            print_result("Type Compatibility", True)
        except Exception as e:
            print_result("Type Compatibility", False, str(e))
            return False
        
        return True
        
    except Exception as e:
        print_result("Validation Tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_mapper_agent_correction_learning():
    """Test Universal Mapper Agent correction learning."""
    print_header("TEST: Universal Mapper Agent - Correction Learning")
    
    try:
        from backend.business_enablement.agents.specialists.universal_mapper_specialist import UniversalMapperSpecialist
        
        agent = UniversalMapperSpecialist.__new__(UniversalMapperSpecialist)
        agent.logger = None
        
        # Test correction pattern extraction
        try:
            original_mapping = {
                "source_field": "pol_id",
                "target_field": "policy_number",
                "transformation": "direct"
            }
            corrected_mapping = {
                "source_field": "pol_id",
                "target_field": "policy_id",
                "transformation": "direct"
            }
            
            correction_pattern = agent._extract_correction_pattern(
                original_mapping=original_mapping,
                corrected_mapping=corrected_mapping,
                correction_reason="Field name mismatch"
            )
            
            assert correction_pattern is not None
            assert "original" in correction_pattern
            assert "corrected" in correction_pattern
            assert "correction_reason" in correction_pattern
            assert "correction_type" in correction_pattern
            
            print_result("Correction Pattern Extraction", True)
        except Exception as e:
            print_result("Correction Pattern Extraction", False, str(e))
            return False
        
        # Test correction type classification
        try:
            correction_type = agent._classify_correction_type(original_mapping, corrected_mapping)
            assert correction_type == "field_mapping"
            print_result("Correction Type Classification", True)
        except Exception as e:
            print_result("Correction Type Classification", False, str(e))
            return False
        
        return True
        
    except Exception as e:
        print_result("Correction Learning Tests", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all agent tests."""
    print("\n" + "="*80)
    print("  INSURANCE AGENTS TEST SUITE")
    print("="*80)
    
    tests = [
        ("Liaison Agent Guidance", test_liaison_agent_guidance),
        ("Mapper Agent Pattern Learning", test_mapper_agent_pattern_learning),
        ("Mapper Agent Validation", test_mapper_agent_validation),
        ("Mapper Agent Correction Learning", test_mapper_agent_correction_learning)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            results.append((test_name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal Test Suites: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

