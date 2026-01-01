#!/usr/bin/env python3
"""
Test AGUI Schema Requirement

Test the AGUI schema requirement for agent creation.
Demonstrates that agents must define their AGUI output schemas.
"""

import sys
import os
import asyncio
from typing import Dict, Any
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from foundations.utility_foundation.utilities import UserContext
from agentic.agui_schema_registry import get_agui_schema_registry, AGUISchema, AGUIComponent
from agentic.agui_schema_helpers import create_data_analyst_agui_schema, create_business_analyst_agui_schema, create_insights_liaison_agui_schema


async def test_agui_schema_registry():
    """Test AGUI schema registry functionality."""
    print("🧪 Testing AGUI Schema Registry...")
    
    try:
        registry = get_agui_schema_registry()
        
        # Test getting component types
        component_types = registry.get_component_types()
        print(f"✅ Available component types: {len(component_types)}")
        
        # Test creating a custom schema
        custom_schema = AGUISchema(
            agent_name="TestAgent",
            version="1.0",
            description="Test agent schema",
            components=[
                AGUIComponent(
                    type="analysis_card",
                    title="Test Analysis",
                    description="Test analysis component",
                    required=True,
                    properties={
                        "data": {"type": "object", "description": "Test data"}
                    }
                ),
                AGUIComponent(
                    type="message_card",
                    title="Test Message",
                    description="Test message component",
                    required=True,
                    properties={
                        "message": {"type": "string", "description": "Test message"}
                    }
                )
            ]
        )
        
        # Test validation
        validation_result = registry.validate_schema(custom_schema)
        if validation_result["valid"]:
            print("✅ Custom schema validation passed")
        else:
            print(f"❌ Custom schema validation failed: {validation_result['errors']}")
            return False
        
        # Test registration
        success = registry.register_agent_schema("TestAgent", custom_schema)
        if success:
            print("✅ Custom schema registered successfully")
        else:
            print("❌ Failed to register custom schema")
            return False
        
        # Test retrieval
        retrieved_schema = registry.get_agent_schema("TestAgent")
        if retrieved_schema:
            print("✅ Custom schema retrieved successfully")
        else:
            print("❌ Failed to retrieve custom schema")
            return False
        
        # Test stats
        stats = registry.get_registry_stats()
        print(f"✅ Registry stats: {stats}")
        
        # Cleanup
        registry.schemas.pop("TestAgent", None)
        
        return True
        
    except Exception as e:
        print(f"❌ AGUI schema registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agui_schema_helpers():
    """Test AGUI schema helper functions."""
    print("\n🧪 Testing AGUI Schema Helpers...")
    
    try:
        # Test data analyst schema
        data_analyst_schema = create_data_analyst_agui_schema()
        print(f"✅ Data analyst schema created: {data_analyst_schema.agent_name}")
        print(f"   Components: {len(data_analyst_schema.components)}")
        
        # Test business analyst schema
        business_analyst_schema = create_business_analyst_agui_schema()
        print(f"✅ Business analyst schema created: {business_analyst_schema.agent_name}")
        print(f"   Components: {len(business_analyst_schema.components)}")
        
        # Test insights liaison schema
        insights_liaison_schema = create_insights_liaison_agui_schema()
        print(f"✅ Insights liaison schema created: {insights_liaison_schema.agent_name}")
        print(f"   Components: {len(insights_liaison_schema.components)}")
        
        # Test schema validation
        registry = get_agui_schema_registry()
        
        for schema in [data_analyst_schema, business_analyst_schema, insights_liaison_schema]:
            validation = registry.validate_schema(schema)
            if validation["valid"]:
                print(f"✅ {schema.agent_name} schema validation passed")
            else:
                print(f"❌ {schema.agent_name} schema validation failed: {validation['errors']}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ AGUI schema helpers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent_creation_with_agui_schema():
    """Test agent creation with AGUI schema requirement."""
    print("\n🧪 Testing Agent Creation with AGUI Schema...")
    
    try:
        # Test creating agent without AGUI schema (should fail)
        print("Testing agent creation without AGUI schema...")
        try:
            from agentic.agent_sdk import AgentBase
            from agentic.agui_schema_helpers import create_data_analyst_agui_schema
            
            # This should fail because AGUI schema is required
            agent = AgentBase(
                agent_name="TestAgent",
                capabilities=["test"],
                required_roles=["librarian"]
                # Missing agui_schema parameter
            )
            print("❌ Agent creation should have failed without AGUI schema")
            return False
        except TypeError as e:
            print("✅ Agent creation correctly failed without AGUI schema")
            print(f"   Error: {e}")
        
        # Test creating agent with AGUI schema (should succeed)
        print("Testing agent creation with AGUI schema...")
        try:
            agui_schema = create_data_analyst_agui_schema()
            agui_schema.agent_name = "TestAgent"  # Update for test
            
            agent = AgentBase(
                agent_name="TestAgent",
                capabilities=["test"],
                required_roles=["librarian"],
                agui_schema=agui_schema
            )
            print("✅ Agent creation succeeded with AGUI schema")
            
            # Test AGUI schema methods
            schema_info = agent.get_agui_schema_info()
            print(f"✅ AGUI schema info retrieved: {schema_info['component_count']} components")
            
            return True
            
        except Exception as e:
            print(f"❌ Agent creation with AGUI schema failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Agent creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agui_schema_validation():
    """Test AGUI schema validation."""
    print("\n🧪 Testing AGUI Schema Validation...")
    
    try:
        registry = get_agui_schema_registry()
        
        # Test valid schema
        valid_schema = AGUISchema(
            agent_name="ValidAgent",
            version="1.0",
            description="Valid test schema",
            components=[
                AGUIComponent(
                    type="analysis_card",
                    title="Valid Analysis",
                    description="Valid analysis component",
                    required=True,
                    properties={
                        "data": {"type": "object", "description": "Valid data"}
                    }
                )
            ]
        )
        
        validation = registry.validate_schema(valid_schema)
        if validation["valid"]:
            print("✅ Valid schema validation passed")
        else:
            print(f"❌ Valid schema validation failed: {validation['errors']}")
            return False
        
        # Test invalid schema (missing required fields)
        invalid_schema = AGUISchema(
            agent_name="",  # Missing agent name
            version="1.0",
            description="Invalid test schema",
            components=[]  # Empty components
        )
        
        validation = registry.validate_schema(invalid_schema)
        if not validation["valid"]:
            print("✅ Invalid schema correctly rejected")
            print(f"   Errors: {validation['errors']}")
        else:
            print("❌ Invalid schema should have been rejected")
            return False
        
        # Test schema with unknown component type
        unknown_component_schema = AGUISchema(
            agent_name="UnknownComponentAgent",
            version="1.0",
            description="Schema with unknown component",
            components=[
                AGUIComponent(
                    type="unknown_component_type",  # Unknown type
                    title="Unknown Component",
                    description="Unknown component",
                    required=True
                )
            ]
        )
        
        validation = registry.validate_schema(unknown_component_schema)
        if not validation["valid"]:
            print("✅ Schema with unknown component type correctly rejected")
            print(f"   Errors: {validation['errors']}")
        else:
            print("❌ Schema with unknown component type should have been rejected")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ AGUI schema validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all AGUI schema requirement tests."""
    print("🚀 Starting AGUI Schema Requirement Tests")
    print("=" * 60)
    
    test_results = []
    
    # Test AGUI schema registry
    test_results.append(await test_agui_schema_registry())
    
    # Test AGUI schema helpers
    test_results.append(await test_agui_schema_helpers())
    
    # Test agent creation with AGUI schema
    test_results.append(await test_agent_creation_with_agui_schema())
    
    # Test AGUI schema validation
    test_results.append(await test_agui_schema_validation())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ Tests Passed: {passed}/{total}")
    print(f"❌ Tests Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! AGUI Schema Requirement is working correctly!")
        print("\n📋 AGUI Schema Requirement System Complete:")
        print("  ✅ AGUI Schema Registry: Dynamic schema management")
        print("  ✅ Schema Validation: Comprehensive validation rules")
        print("  ✅ Agent SDK Integration: Required AGUI schema parameter")
        print("  ✅ Schema Helpers: Pre-built schemas for common agent types")
        print("  ✅ Component Types: Standardized AGUI component definitions")
        print("\n🎯 Agents must now define their AGUI output schemas!")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please check the implementation.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)


