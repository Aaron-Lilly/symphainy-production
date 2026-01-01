"""
Test Script for Content Pillar MCP Tools
Tests that tools produce the correct data structure for frontend
"""

import asyncio
import pandas as pd
import json
from typing import Dict, Any

# Import our MCP tools
from tools.data_quality_tool import DataQualityTool
from tools.tabular_content_tool import TabularContentTool


async def test_data_quality_tool():
    """Test DataQualityTool produces correct structure."""
    print("🧪 Testing DataQualityTool...")
    
    # Create test data
    test_data = {
        "columns": ["customer_id", "name", "email", "transaction_amount", "date"],
        "rows": [
            ["C001", "John Doe", "john@example.com", "150.00", "2024-01-15"],
            ["C002", "Jane Smith", "jane@example.com", "275.50", "2024-01-16"],
            ["C003", "Bob Johnson", None, "89.99", "2024-01-17"],  # Missing email
            ["C001", "John Doe", "john@example.com", "200.00", "2024-01-18"],  # Duplicate
        ]
    }
    
    try:
        # Initialize tool
        quality_tool = DataQualityTool()
        
        # Test quality analysis
        result = await quality_tool.analyze_quality(test_data, context="Test analysis")
        
        # Verify structure matches frontend expectations
        expected_keys = ["overall_score", "status", "top_issues", "recommendation", "metadata"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
        
        # Verify data types
        assert isinstance(result["overall_score"], (int, float)), "overall_score should be numeric"
        assert result["status"] in ["good", "warning", "error"], "status should be valid"
        assert isinstance(result["top_issues"], list), "top_issues should be list"
        assert isinstance(result["recommendation"], str), "recommendation should be string"
        
        print("✅ DataQualityTool test passed!")
        print(f"   Score: {result['overall_score']}")
        print(f"   Status: {result['status']}")
        print(f"   Issues: {len(result['top_issues'])}")
        print(f"   Recommendation: {result['recommendation'][:50]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ DataQualityTool test failed: {e}")
        return None


async def test_tabular_content_tool():
    """Test TabularContentTool produces correct structure."""
    print("\n🧪 Testing TabularContentTool...")
    
    # Create test data
    test_data = {
        "columns": ["customer_id", "name", "email", "transaction_amount", "date"],
        "rows": [
            ["C001", "John Doe", "john@example.com", "150.00", "2024-01-15"],
            ["C002", "Jane Smith", "jane@example.com", "275.50", "2024-01-16"],
            ["C003", "Bob Johnson", "bob@example.com", "89.99", "2024-01-17"],
        ]
    }
    
    try:
        # Initialize tool
        tabular_tool = TabularContentTool()
        
        # Test structured data analysis
        result = await tabular_tool.analyze_structured_data(test_data, context="Test analysis")
        
        # Verify structure matches frontend expectations
        expected_keys = ["columns", "rows", "summary", "analysis", "metadata"]
        for key in expected_keys:
            assert key in result, f"Missing key: {key}"
        
        # Verify summary structure
        summary = result["summary"]
        expected_summary_keys = ["total_rows", "total_columns", "file_type", "status", "basic_insights"]
        for key in expected_summary_keys:
            assert key in summary, f"Missing summary key: {key}"
        
        # Verify data types
        assert isinstance(result["columns"], list), "columns should be list"
        assert isinstance(result["rows"], list), "rows should be list"
        assert isinstance(summary["basic_insights"], list), "basic_insights should be list"
        
        print("✅ TabularContentTool test passed!")
        print(f"   Columns: {len(result['columns'])}")
        print(f"   Rows: {len(result['rows'])}")
        print(f"   Summary: {summary['total_rows']} rows, {summary['total_columns']} columns")
        print(f"   Insights: {len(summary['basic_insights'])}")
        
        return result
        
    except Exception as e:
        print(f"❌ TabularContentTool test failed: {e}")
        return None


async def test_frontend_data_contract():
    """Test that tools produce data matching frontend interface."""
    print("\n🧪 Testing Frontend Data Contract...")
    
    # Test data
    test_data = {
        "columns": ["id", "name", "value"],
        "rows": [
            ["1", "Item A", "100"],
            ["2", "Item B", "200"],
            ["3", "Item C", "300"]
        ]
    }
    
    try:
        # Test both tools
        quality_tool = DataQualityTool()
        tabular_tool = TabularContentTool()
        
        # Get results
        quality_result = await quality_tool.analyze_quality(test_data)
        tabular_result = await tabular_tool.analyze_structured_data(test_data)
        
        # Verify quality result matches frontend interface
        quality_interface = {
            "overall_score": quality_result["overall_score"],
            "status": quality_result["status"],
            "top_issues": quality_result["top_issues"],
            "recommendation": quality_result["recommendation"]
        }
        
        # Verify tabular result matches frontend interface
        tabular_interface = {
            "columns": tabular_result["columns"],
            "rows": tabular_result["rows"],
            "summary": {
                "total_rows": tabular_result["summary"]["total_rows"],
                "total_columns": tabular_result["summary"]["total_columns"],
                "file_type": tabular_result["summary"]["file_type"],
                "status": tabular_result["summary"]["status"],
                "basic_insights": tabular_result["summary"]["basic_insights"]
            }
        }
        
        print("✅ Frontend data contract test passed!")
        print("   Quality interface: ✅")
        print("   Tabular interface: ✅")
        
        return {
            "quality": quality_interface,
            "tabular": tabular_interface
        }
        
    except Exception as e:
        print(f"❌ Frontend data contract test failed: {e}")
        return None


async def main():
    """Run all tests."""
    print("🚀 Starting Content Pillar MCP Tools Tests")
    print("=" * 50)
    
    # Test individual tools
    quality_result = await test_data_quality_tool()
    tabular_result = await test_tabular_content_tool()
    
    # Test frontend data contract
    contract_result = await test_frontend_data_contract()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    if quality_result:
        print("✅ DataQualityTool: PASSED")
    else:
        print("❌ DataQualityTool: FAILED")
    
    if tabular_result:
        print("✅ TabularContentTool: PASSED")
    else:
        print("❌ TabularContentTool: FAILED")
    
    if contract_result:
        print("✅ Frontend Data Contract: PASSED")
    else:
        print("❌ Frontend Data Contract: FAILED")
    
    print("\n🎯 Next Steps:")
    print("1. Tools produce correct data structure ✅")
    print("2. Ready for Experience layer integration")
    print("3. Frontend can consume data through Experience MCP")
    
    return {
        "quality_tool": quality_result is not None,
        "tabular_tool": tabular_result is not None,
        "frontend_contract": contract_result is not None
    }


if __name__ == "__main__":
    # Run tests
    results = asyncio.run(main())
    
    # Exit with appropriate code
    if all(results.values()):
        print("\n🎉 All tests passed! Content Pillar MCP Tools are ready.")
        exit(0)
    else:
        print("\n💥 Some tests failed. Please check the implementation.")
        exit(1)

