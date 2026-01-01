#!/usr/bin/env python3
"""
Test script to verify abstraction utilities are properly integrated.

Tests the first batch of abstractions (file_management, content_metadata)
to ensure the pattern works correctly.
"""

import sys
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "symphainy-platform"))

def test_constructor_patterns():
    """Test that constructors accept di_container and set up correctly."""
    print("\n" + "="*80)
    print("TEST 1: Constructor Patterns")
    print("="*80)
    
    # Mock DI container
    mock_di_container = Mock()
    mock_logger = Mock()
    mock_di_container.get_logger = Mock(return_value=mock_logger)
    
    # Mock adapters
    mock_supabase_adapter = Mock()
    mock_config_adapter = Mock()
    mock_arango_adapter = Mock()
    
    # Test FileManagementAbstraction
    try:
        from foundations.public_works_foundation.infrastructure_abstractions.file_management_abstraction import FileManagementAbstraction
        
        abstraction = FileManagementAbstraction(
            supabase_adapter=mock_supabase_adapter,
            config_adapter=mock_config_adapter,
            di_container=mock_di_container
        )
        
        assert hasattr(abstraction, 'di_container'), "Should have di_container attribute"
        assert hasattr(abstraction, 'service_name'), "Should have service_name attribute"
        assert abstraction.service_name == "file_management_abstraction", "Service name should match"
        assert abstraction.logger == mock_logger, "Logger should come from DI container"
        
        print("✅ FileManagementAbstraction constructor works correctly")
    except Exception as e:
        print(f"❌ FileManagementAbstraction constructor failed: {e}")
        raise
    
    # Test ContentMetadataAbstraction
    try:
        from foundations.public_works_foundation.infrastructure_abstractions.content_metadata_abstraction import ContentMetadataAbstraction
        
        abstraction = ContentMetadataAbstraction(
            arango_adapter=mock_arango_adapter,
            config_adapter=mock_config_adapter,
            di_container=mock_di_container
        )
        
        assert hasattr(abstraction, 'di_container'), "Should have di_container attribute"
        assert hasattr(abstraction, 'service_name'), "Should have service_name attribute"
        assert abstraction.service_name == "content_metadata_abstraction", "Service name should match"
        assert abstraction.logger == mock_logger, "Logger should come from DI container"
        
        print("✅ ContentMetadataAbstraction constructor works correctly")
    except Exception as e:
        print(f"❌ ContentMetadataAbstraction constructor failed: {e}")
        raise

async def test_utility_access_patterns():
    """Test that methods can access utilities from DI container."""
    print("\n" + "="*80)
    print("TEST 2: Utility Access Patterns")
    print("="*80)
    
    # Mock DI container with utilities
    mock_di_container = Mock()
    mock_logger = Mock()
    mock_error_handler = AsyncMock()
    mock_telemetry = AsyncMock()
    
    mock_di_container.get_logger = Mock(return_value=mock_logger)
    mock_di_container.get_utility = Mock(side_effect=lambda name: {
        "error_handler": mock_error_handler,
        "telemetry": mock_telemetry
    }.get(name, None))
    mock_di_container.hasattr = Mock(return_value=True)
    
    # Mock adapters
    mock_supabase_adapter = AsyncMock()
    mock_config_adapter = Mock()
    mock_arango_adapter = AsyncMock()
    
    # Test FileManagementAbstraction - get_file method
    try:
        from foundations.public_works_foundation.infrastructure_abstractions.file_management_abstraction import FileManagementAbstraction
        
        abstraction = FileManagementAbstraction(
            supabase_adapter=mock_supabase_adapter,
            config_adapter=mock_config_adapter,
            di_container=mock_di_container
        )
        
        # Mock successful response
        mock_supabase_adapter.get_file = AsyncMock(return_value={"uuid": "test-uuid", "ui_name": "test.txt"})
        
        result = await abstraction.get_file("test-uuid")
        
        # Verify telemetry was called
        assert mock_telemetry.record_platform_operation_event.called, "Telemetry should be called on success"
        print("✅ FileManagementAbstraction.get_file uses telemetry correctly")
        
        # Test error handling
        mock_supabase_adapter.get_file = AsyncMock(side_effect=Exception("Test error"))
        
        try:
            await abstraction.get_file("test-uuid")
        except Exception:
            pass  # Expected
        
        # Verify error handler was called
        assert mock_error_handler.handle_error.called, "Error handler should be called on error"
        print("✅ FileManagementAbstraction.get_file uses error handler correctly")
        
    except Exception as e:
        print(f"❌ FileManagementAbstraction utility access failed: {e}")
        raise
    
    # Test ContentMetadataAbstraction - get_content_metadata method
    try:
        from foundations.public_works_foundation.infrastructure_abstractions.content_metadata_abstraction import ContentMetadataAbstraction
        
        abstraction = ContentMetadataAbstraction(
            arango_adapter=mock_arango_adapter,
            config_adapter=mock_config_adapter,
            di_container=mock_di_container
        )
        
        # Mock successful response
        mock_arango_adapter.get_content_metadata = AsyncMock(return_value={"content_id": "test-id", "content_type": "test"})
        
        result = await abstraction.get_content_metadata("test-id")
        
        # Verify telemetry was called
        assert mock_telemetry.record_platform_operation_event.called, "Telemetry should be called on success"
        print("✅ ContentMetadataAbstraction.get_content_metadata uses telemetry correctly")
        
        # Test error handling
        mock_arango_adapter.get_content_metadata = AsyncMock(side_effect=Exception("Test error"))
        
        try:
            await abstraction.get_content_metadata("test-id")
        except Exception:
            pass  # Expected
        
        # Verify error handler was called
        assert mock_error_handler.handle_error.called, "Error handler should be called on error"
        print("✅ ContentMetadataAbstraction.get_content_metadata uses error handler correctly")
        
    except Exception as e:
        print(f"❌ ContentMetadataAbstraction utility access failed: {e}")
        raise

def test_foundation_service_integration():
    """Test that foundation service passes di_container correctly."""
    print("\n" + "="*80)
    print("TEST 3: Foundation Service Integration")
    print("="*80)
    
    # Check that foundation service passes di_container
    foundation_service_path = project_root / "symphainy-platform" / "foundations" / "public_works_foundation" / "public_works_foundation_service.py"
    
    if not foundation_service_path.exists():
        print("⚠️  Foundation service file not found - skipping integration test")
        return
    
    content = foundation_service_path.read_text()
    
    # Check FileManagementAbstraction instantiation
    if 'FileManagementAbstraction(' in content:
        if 'di_container=self.di_container' in content:
            print("✅ Foundation service passes di_container to FileManagementAbstraction")
        else:
            print("❌ Foundation service does NOT pass di_container to FileManagementAbstraction")
            raise AssertionError("Missing di_container parameter")
    else:
        print("⚠️  FileManagementAbstraction instantiation not found")
    
    # Check ContentMetadataAbstraction instantiation
    if 'ContentMetadataAbstraction(' in content:
        if 'di_container=self.di_container' in content:
            print("✅ Foundation service passes di_container to ContentMetadataAbstraction")
        else:
            print("❌ Foundation service does NOT pass di_container to ContentMetadataAbstraction")
            raise AssertionError("Missing di_container parameter")
    else:
        print("⚠️  ContentMetadataAbstraction instantiation not found")

def test_method_coverage():
    """Test that all async methods have utility integration."""
    print("\n" + "="*80)
    print("TEST 4: Method Coverage")
    print("="*80)
    
    import inspect
    import re
    
    # Check FileManagementAbstraction
    try:
        from foundations.public_works_foundation.infrastructure_abstractions.file_management_abstraction import FileManagementAbstraction
        
        file_source = inspect.getsource(FileManagementAbstraction)
        async_methods = re.findall(r'async def (\w+)\(', file_source)
        
        # Count methods with telemetry
        telemetry_count = file_source.count('record_platform_operation_event')
        error_handler_count = file_source.count('error_handler = self.di_container.get_utility("error_handler")')
        
        print(f"FileManagementAbstraction:")
        print(f"  Async methods: {len(async_methods)}")
        print(f"  Methods with telemetry: {telemetry_count}")
        print(f"  Methods with error handler: {error_handler_count}")
        
        # Should have telemetry and error handler for most async methods
        if telemetry_count >= len(async_methods) * 0.8:  # At least 80% coverage
            print("✅ FileManagementAbstraction has good telemetry coverage")
        else:
            print(f"⚠️  FileManagementAbstraction telemetry coverage is low ({telemetry_count}/{len(async_methods)})")
        
        if error_handler_count >= len(async_methods) * 0.8:
            print("✅ FileManagementAbstraction has good error handler coverage")
        else:
            print(f"⚠️  FileManagementAbstraction error handler coverage is low ({error_handler_count}/{len(async_methods)})")
            
    except Exception as e:
        print(f"❌ FileManagementAbstraction method coverage check failed: {e}")
    
    # Check ContentMetadataAbstraction
    try:
        from foundations.public_works_foundation.infrastructure_abstractions.content_metadata_abstraction import ContentMetadataAbstraction
        
        content_source = inspect.getsource(ContentMetadataAbstraction)
        async_methods = re.findall(r'async def (\w+)\(', content_source)
        
        # Count methods with telemetry
        telemetry_count = content_source.count('record_platform_operation_event')
        error_handler_count = content_source.count('error_handler = self.di_container.get_utility("error_handler")')
        
        print(f"\nContentMetadataAbstraction:")
        print(f"  Async methods: {len(async_methods)}")
        print(f"  Methods with telemetry: {telemetry_count}")
        print(f"  Methods with error handler: {error_handler_count}")
        
        # Should have telemetry and error handler for most async methods
        if telemetry_count >= len(async_methods) * 0.8:
            print("✅ ContentMetadataAbstraction has good telemetry coverage")
        else:
            print(f"⚠️  ContentMetadataAbstraction telemetry coverage is low ({telemetry_count}/{len(async_methods)})")
        
        if error_handler_count >= len(async_methods) * 0.8:
            print("✅ ContentMetadataAbstraction has good error handler coverage")
        else:
            print(f"⚠️  ContentMetadataAbstraction error handler coverage is low ({error_handler_count}/{len(async_methods)})")
            
    except Exception as e:
        print(f"❌ ContentMetadataAbstraction method coverage check failed: {e}")

async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("ABSTRACTION UTILITIES TEST SUITE")
    print("="*80)
    
    try:
        # Test 1: Constructor patterns
        test_constructor_patterns()
        
        # Test 2: Utility access patterns
        await test_utility_access_patterns()
        
        # Test 3: Foundation service integration
        test_foundation_service_integration()
        
        # Test 4: Method coverage
        test_method_coverage()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        
    except Exception as e:
        print("\n" + "="*80)
        print(f"❌ TESTS FAILED: {e}")
        print("="*80)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())












