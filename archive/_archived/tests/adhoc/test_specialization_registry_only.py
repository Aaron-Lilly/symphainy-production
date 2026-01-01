#!/usr/bin/env python3
"""
Test Specialization Registry Only

Test the specialization registry functionality without importing the full agent system.
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from agentic.specialization_registry import get_specialization_registry, SpecializationRegistry


async def test_specialization_registry():
    """Test specialization registry functionality."""
    print("🧪 Testing Specialization Registry...")
    
    try:
        # Create a test registry
        registry = SpecializationRegistry("test_specializations.json")
        
        # Test getting all specializations
        all_specs = registry.get_all_specializations()
        print(f"✅ Loaded {len(all_specs)} specializations")
        
        # Test getting specializations for insights pillar
        insights_specs = registry.get_specializations_for_pillar("insights")
        print(f"✅ Found {len(insights_specs)} insights specializations")
        
        # Test getting specific specialization
        call_center_spec = registry.get_specialization("call_center_volumetric_analysis")
        if call_center_spec:
            print(f"✅ Retrieved call center specialization: {call_center_spec['name']}")
        
        # Test registering a new specialization
        new_spec = {
            "name": "E-commerce Customer Analytics",
            "description": "Expert in e-commerce customer behavior, conversion optimization, and retention analysis",
            "pillar": "insights",
            "capabilities": ["customer_analytics", "conversion_optimization", "retention_analysis"],
            "system_prompt_template": "You are an expert in e-commerce customer analytics. You understand customer journey mapping, conversion funnels, A/B testing, and customer lifetime value optimization.",
            "keywords": ["ecommerce", "customer", "conversion", "retention", "analytics"]
        }
        
        success = registry.register_specialization("ecommerce_customer_analytics", new_spec)
        if success:
            print("✅ Successfully registered new specialization")
        
        # Test validation
        validation_result = registry.validate_specialization("ecommerce_customer_analytics")
        if validation_result["valid"]:
            print("✅ Specialization validation passed")
        else:
            print(f"❌ Specialization validation failed: {validation_result['errors']}")
        
        # Test search
        search_results = registry.search_specializations("customer", "insights")
        print(f"✅ Found {len(search_results)} specializations matching 'customer'")
        
        # Test stats
        stats = registry.get_specialization_stats()
        print(f"✅ Registry stats: {stats}")
        
        # Test removing specialization
        remove_success = registry.remove_specialization("ecommerce_customer_analytics")
        if remove_success:
            print("✅ Successfully removed specialization")
        
        # Cleanup
        if os.path.exists("test_specializations.json"):
            os.remove("test_specializations.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Specialization registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_specialization_configuration():
    """Test specialization configuration structure."""
    print("\n🧪 Testing Specialization Configuration...")
    
    try:
        registry = get_specialization_registry()
        
        # Test getting all specializations
        all_specs = registry.get_all_specializations()
        print(f"✅ Global registry loaded {len(all_specs)} specializations")
        
        # Test each specialization structure
        for spec in all_specs:
            spec_id = spec["id"]
            validation = registry.validate_specialization(spec_id)
            
            if validation["valid"]:
                print(f"✅ {spec_id}: Valid")
            else:
                print(f"❌ {spec_id}: Invalid - {validation['errors']}")
                return False
        
        # Test pillar organization
        for pillar in ["insights", "operations", "content", "experience"]:
            pillar_specs = registry.get_specializations_for_pillar(pillar)
            print(f"✅ {pillar} pillar: {len(pillar_specs)} specializations")
        
        return True
        
    except Exception as e:
        print(f"❌ Specialization configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_dynamic_specialization_management():
    """Test dynamic specialization management."""
    print("\n🧪 Testing Dynamic Specialization Management...")
    
    try:
        registry = get_specialization_registry()
        
        # Test creating a custom specialization
        custom_spec = {
            "name": "Custom Financial Analysis",
            "description": "Expert in custom financial analysis and risk assessment",
            "pillar": "insights",
            "capabilities": ["financial_analysis", "risk_assessment", "custom_modeling"],
            "system_prompt_template": "You are an expert in custom financial analysis. You understand complex financial models, risk assessment methodologies, and regulatory compliance requirements.",
            "keywords": ["financial", "analysis", "risk", "custom", "modeling"]
        }
        
        # Register the specialization
        success = registry.register_specialization("custom_financial_analysis", custom_spec)
        if not success:
            print("❌ Failed to register custom specialization")
            return False
        
        print("✅ Custom specialization registered")
        
        # Verify it was registered
        retrieved_spec = registry.get_specialization("custom_financial_analysis")
        if not retrieved_spec:
            print("❌ Failed to retrieve custom specialization")
            return False
        
        print(f"✅ Retrieved custom specialization: {retrieved_spec['name']}")
        
        # Test validation
        validation = registry.validate_specialization("custom_financial_analysis")
        if not validation["valid"]:
            print(f"❌ Custom specialization validation failed: {validation['errors']}")
            return False
        
        print("✅ Custom specialization validation passed")
        
        # Test search
        search_results = registry.search_specializations("financial", "insights")
        if len(search_results) == 0:
            print("❌ Search failed to find custom specialization")
            return False
        
        print(f"✅ Search found {len(search_results)} financial specializations")
        
        # Test removal
        remove_success = registry.remove_specialization("custom_financial_analysis")
        if not remove_success:
            print("❌ Failed to remove custom specialization")
            return False
        
        print("✅ Custom specialization removed successfully")
        
        # Verify removal
        retrieved_after_removal = registry.get_specialization("custom_financial_analysis")
        if retrieved_after_removal:
            print("❌ Specialization still exists after removal")
            return False
        
        print("✅ Specialization confirmed removed")
        
        return True
        
    except Exception as e:
        print(f"❌ Dynamic specialization management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all specialization registry tests."""
    print("🚀 Starting Specialization Registry Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test specialization registry
    test_results.append(await test_specialization_registry())
    
    # Test specialization configuration
    test_results.append(await test_specialization_configuration())
    
    # Test dynamic specialization management
    test_results.append(await test_dynamic_specialization_management())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Specialization Registry is working correctly!")
        print("\n📋 Specialization Registry System Complete:")
        print("  ✅ Dynamic Specialization Management")
        print("  ✅ Pillar-based Organization")
        print("  ✅ Validation and Search")
        print("  ✅ JSON Configuration Storage")
        print("  ✅ Extensible Architecture")
        print("\n🎯 Ready for agent integration!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)



