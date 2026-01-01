#!/usr/bin/env python3
"""
Comprehensive Test Suite for All Insurance Use Case Agents

Tests all 8 agents:
1. Insurance Liaison Agent
2. Universal Mapper Specialist Agent
3. Wave Planning Specialist Agent
4. Change Impact Assessment Specialist Agent
5. Routing Decision Specialist Agent
6. Quality Remediation Specialist Agent
7. Coexistence Strategy Specialist Agent
8. Saga/WAL Management Specialist Agent
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


async def test_liaison_agent():
    """Test Insurance Liaison Agent."""
    print_header("TEST: Insurance Liaison Agent")
    
    try:
        from backend.business_enablement.agents.insurance_liaison_agent import InsuranceLiaisonAgent
        
        agent = InsuranceLiaisonAgent.__new__(InsuranceLiaisonAgent)
        agent.logger = None
        
        # Test guidance methods
        guidance_methods = [
            ("Ingestion Guidance", agent._get_ingestion_guidance),
            ("Mapping Guidance", agent._get_mapping_guidance),
            ("Routing Guidance", agent._get_routing_guidance),
            ("Wave Guidance", agent._get_wave_guidance),
            ("Tracking Guidance", agent._get_tracking_guidance),
            ("General Guidance", agent._get_general_guidance)
        ]
        
        all_passed = True
        for test_name, method in guidance_methods:
            try:
                guidance = method()
                assert guidance is not None and len(guidance) > 0
                print_result(test_name, True)
            except Exception as e:
                print_result(test_name, False, str(e))
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_result("Liaison Agent", False, str(e))
        return False


async def test_universal_mapper_agent():
    """Test Universal Mapper Specialist Agent."""
    print_header("TEST: Universal Mapper Specialist Agent")
    
    try:
        from backend.business_enablement.agents.specialists.universal_mapper_specialist import UniversalMapperSpecialist
        
        agent = UniversalMapperSpecialist.__new__(UniversalMapperSpecialist)
        agent.logger = None
        agent.pattern_cache = {}
        
        # Test semantic similarity
        similarity = agent._calculate_semantic_similarity("policy_id", "policy_id")
        assert similarity == 1.0
        print_result("Semantic Similarity", True)
        
        # Test pattern extraction
        source_schema = {"fields": [{"name": "pol_id", "type": "string"}]}
        target_schema = {"fields": [{"name": "policy_id", "type": "string"}]}
        mapping_rules = {"rules": [{"source": "pol_id", "target": "policy_id", "transformation": "direct"}]}
        
        patterns = agent._extract_mapping_patterns(source_schema, target_schema, mapping_rules)
        assert len(patterns) == 1
        print_result("Pattern Extraction", True)
        
        # Test validation
        completeness = agent._validate_completeness(source_schema, target_schema, mapping_rules)
        assert completeness["is_complete"] is True
        print_result("Validation", True)
        
        return True
        
    except Exception as e:
        print_result("Universal Mapper Agent", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_wave_planning_agent():
    """Test Wave Planning Specialist Agent."""
    print_header("TEST: Wave Planning Specialist Agent")
    
    try:
        from backend.business_enablement.agents.specialists.wave_planning_specialist import WavePlanningSpecialist
        
        agent = WavePlanningSpecialist.__new__(WavePlanningSpecialist)
        agent.logger = None
        
        # Test cohort grouping
        policies = [
            {"organization_code": "ORG_A", "status": "active"},
            {"organization_code": "ORG_A", "status": "active"},
            {"organization_code": "ORG_B", "status": "inactive"}
        ]
        
        cohorts = agent._group_policies_into_cohorts(policies)
        assert len(cohorts) == 2
        print_result("Cohort Grouping", True)
        
        # Test cohort analysis
        cohort_analysis = agent._extract_cohort_characteristics(policies)
        assert cohort_analysis["policy_count"] == 3
        print_result("Cohort Analysis", True)
        
        # Test risk assessment
        cohort_data = {"cohorts": [{"risk_level": "high"}]}
        risk = await agent._assess_migration_risk(cohort_data, None)
        assert "risk_level" in risk
        print_result("Risk Assessment", True)
        
        return True
        
    except Exception as e:
        print_result("Wave Planning Agent", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_change_impact_agent():
    """Test Change Impact Assessment Specialist Agent."""
    print_header("TEST: Change Impact Assessment Specialist Agent")
    
    try:
        from backend.business_enablement.agents.specialists.change_impact_assessment_specialist import ChangeImpactAssessmentSpecialist
        
        agent = ChangeImpactAssessmentSpecialist.__new__(ChangeImpactAssessmentSpecialist)
        agent.logger = None
        
        # Test mapping rule impact
        change_details = {"affected_fields": ["field1", "field2"]}
        current_state = {"mappings": {}}
        
        impact = await agent._assess_mapping_rule_impact(change_details, current_state, None)
        assert impact["impact_type"] == "mapping_rule"
        print_result("Mapping Rule Impact", True)
        
        # Test schema evolution impact
        schema_changes = {
            "added_fields": ["new_field"],
            "removed_fields": ["old_field"],
            "modified_fields": []
        }
        impact = await agent._assess_schema_evolution_impact(
            {"schema_changes": schema_changes}, current_state, None
        )
        assert impact["impact_type"] == "schema_evolution"
        print_result("Schema Evolution Impact", True)
        
        return True
        
    except Exception as e:
        print_result("Change Impact Agent", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_routing_decision_agent():
    """Test Routing Decision Specialist Agent."""
    print_header("TEST: Routing Decision Specialist Agent")
    
    try:
        from backend.business_enablement.agents.specialists.routing_decision_specialist import RoutingDecisionSpecialist
        
        agent = RoutingDecisionSpecialist.__new__(RoutingDecisionSpecialist)
        agent.logger = None
        agent.routing_history = []
        
        # Test business context analysis
        policy_data = {"organization_code": "ORG_A", "status": "active", "data_quality_score": 0.9}
        context = await agent._analyze_business_context(policy_data, None)
        assert "policy_characteristics" in context
        print_result("Business Context Analysis", True)
        
        # Test option evaluation
        options = [
            {"target_system": "NewPlatformAPI", "confidence": 0.7, "priority": 1},
            {"target_system": "CoexistenceBridge", "confidence": 0.6, "priority": 2}
        ]
        evaluations = await agent._evaluate_routing_options(options, policy_data, context)
        assert len(evaluations) == 2
        print_result("Option Evaluation", True)
        
        # Test suitability scoring
        score = agent._calculate_suitability_score(options[0], policy_data, context)
        assert 0.0 <= score <= 1.0
        print_result("Suitability Scoring", True)
        
        return True
        
    except Exception as e:
        print_result("Routing Decision Agent", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_quality_remediation_agent():
    """Test Quality Remediation Specialist Agent."""
    print_header("TEST: Quality Remediation Specialist Agent")
    
    try:
        from backend.business_enablement.agents.specialists.quality_remediation_specialist import QualityRemediationSpecialist
        
        agent = QualityRemediationSpecialist.__new__(QualityRemediationSpecialist)
        agent.logger = None
        
        # Test anomaly interpretation
        quality_metrics = {
            "quality_score": 0.75,
            "issues": [
                {"type": "missing_required", "affected_fields": ["field1"], "severity_score": 0.8}
            ]
        }
        
        interpretation = await agent._interpret_anomalies(quality_metrics, None, None)
        assert "anomalies" in interpretation
        print_result("Anomaly Interpretation", True)
        
        # Test pattern detection
        pattern_detection = await agent._detect_quality_patterns(quality_metrics, None)
        assert "patterns" in pattern_detection
        print_result("Pattern Detection", True)
        
        # Test priority ranking
        ranking = await agent._rank_issues_by_priority(interpretation, pattern_detection, None)
        assert len(ranking) > 0
        print_result("Priority Ranking", True)
        
        return True
        
    except Exception as e:
        print_result("Quality Remediation Agent", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_coexistence_strategy_agent():
    """Test Coexistence Strategy Specialist Agent."""
    print_header("TEST: Coexistence Strategy Specialist Agent")
    
    try:
        from backend.business_enablement.agents.specialists.coexistence_strategy_specialist import CoexistenceStrategySpecialist
        
        agent = CoexistenceStrategySpecialist.__new__(CoexistenceStrategySpecialist)
        agent.logger = None
        
        # Test pattern analysis
        current_state = {"write_capability": True, "read_capability": True}
        target_state = {"write_capability": True, "read_capability": True}
        
        patterns = await agent._analyze_coexistence_patterns(current_state, target_state)
        assert "patterns" in patterns
        print_result("Pattern Analysis", True)
        
        # Test sync strategy recommendations
        strategies = await agent._recommend_sync_strategies(patterns, None)
        assert len(strategies) > 0
        print_result("Sync Strategy Recommendations", True)
        
        # Test retirement planning
        retirement = await agent._plan_retirement(current_state, target_state, strategies)
        assert "retirement_phase" in retirement
        print_result("Retirement Planning", True)
        
        return True
        
    except Exception as e:
        print_result("Coexistence Strategy Agent", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def test_saga_wal_management_agent():
    """Test Saga/WAL Management Specialist Agent."""
    print_header("TEST: Saga/WAL Management Specialist Agent")
    
    try:
        from backend.business_enablement.agents.specialists.saga_wal_management_specialist import SagaWALManagementSpecialist
        
        agent = SagaWALManagementSpecialist.__new__(SagaWALManagementSpecialist)
        agent.logger = None
        
        # Test execution analysis
        journey_data = {
            "status": "in_progress",
            "milestones": [
                {"status": "completed"},
                {"status": "in_progress", "started_at": "2024-01-01T00:00:00"}
            ]
        }
        
        analysis = await agent._analyze_execution_status("saga_123", journey_data)
        assert "status" in analysis
        print_result("Execution Analysis", True)
        
        # Test anomaly detection
        anomalies = await agent._detect_anomalies(analysis, journey_data)
        assert "anomalies" in anomalies
        print_result("Anomaly Detection", True)
        
        # Test WAL entry triage
        wal_entries = [
            {"operation": "test_op", "level": "error"},
            {"operation": "test_op2", "level": "info"}
        ]
        
        categorized = await agent._categorize_wal_entries(wal_entries)
        assert "errors" in categorized
        assert len(categorized["errors"]) == 1
        print_result("WAL Entry Triage", True)
        
        return True
        
    except Exception as e:
        print_result("Saga/WAL Management Agent", False, str(e))
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all agent tests."""
    print("\n" + "="*80)
    print("  COMPREHENSIVE INSURANCE AGENTS TEST SUITE")
    print("="*80)
    
    tests = [
        ("Insurance Liaison Agent", test_liaison_agent),
        ("Universal Mapper Specialist Agent", test_universal_mapper_agent),
        ("Wave Planning Specialist Agent", test_wave_planning_agent),
        ("Change Impact Assessment Specialist Agent", test_change_impact_agent),
        ("Routing Decision Specialist Agent", test_routing_decision_agent),
        ("Quality Remediation Specialist Agent", test_quality_remediation_agent),
        ("Coexistence Strategy Specialist Agent", test_coexistence_strategy_agent),
        ("Saga/WAL Management Specialist Agent", test_saga_wal_management_agent)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal Agents Tested: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    if passed == total:
        print("\n🎉 ALL AGENTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME AGENTS FAILED")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)











