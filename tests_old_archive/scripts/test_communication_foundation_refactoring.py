#!/usr/bin/env python3
"""
Test Communication Foundation Refactoring

Verifies that the foundation services refactoring works correctly.
"""
import sys
import os
import asyncio
from pathlib import Path

def test_imports():
    """Test that all foundation services can be imported."""
    print("=" * 80)
    print("TEST 1: Import Foundation Services")
    print("=" * 80)
    
    try:
        from foundations.communication_foundation.foundation_services.websocket_foundation_service import WebSocketFoundationService
        from foundations.communication_foundation.foundation_services.messaging_foundation_service import MessagingFoundationService
        from foundations.communication_foundation.foundation_services.event_bus_foundation_service import EventBusFoundationService
        print("✅ All foundation services import successfully")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_di_container_methods():
    """Test that DI Container has the new methods."""
    print("\n" + "=" * 80)
    print("TEST 2: DI Container Methods")
    print("=" * 80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        
        assert hasattr(DIContainerService, 'get_websocket_foundation'), "Missing get_websocket_foundation"
        assert hasattr(DIContainerService, 'get_messaging_foundation'), "Missing get_messaging_foundation"
        assert hasattr(DIContainerService, 'get_event_bus_foundation'), "Missing get_event_bus_foundation"
        print("✅ All DI Container methods exist")
        
        import inspect
        source = inspect.getsource(DIContainerService.get_foundation_service)
        assert 'websocket_foundation' in source, "get_foundation_service missing websocket_foundation"
        assert 'messaging_foundation' in source, "get_foundation_service missing messaging_foundation"
        assert 'event_bus_foundation' in source, "get_foundation_service missing event_bus_foundation"
        print("✅ get_foundation_service supports new services")
        
        return True
    except Exception as e:
        print(f"❌ DI Container test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_foundation_service_creation():
    """Test that foundation services can be created with DI."""
    print("\n" + "=" * 80)
    print("TEST 3: Foundation Service Creation")
    print("=" * 80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        
        di_container = DIContainerService(realm_name="test")
        di_container.public_works_foundation = PublicWorksFoundationService(di_container=di_container)
        
        websocket_foundation = di_container.get_websocket_foundation()
        assert websocket_foundation is not None, "WebSocket foundation service is None"
        assert websocket_foundation.service_name == "websocket_foundation", "Wrong service name"
        print("✅ WebSocket foundation service created")
        
        messaging_foundation = di_container.get_messaging_foundation()
        assert messaging_foundation is not None, "Messaging foundation service is None"
        print("✅ Messaging foundation service created")
        
        event_bus_foundation = di_container.get_event_bus_foundation()
        assert event_bus_foundation is not None, "Event Bus foundation service is None"
        print("✅ Event Bus foundation service created")
        
        ws_from_get = di_container.get_foundation_service("websocket_foundation")
        assert ws_from_get is websocket_foundation, "get_foundation_service returned different instance"
        print("✅ get_foundation_service works correctly")
        
        return True
    except Exception as e:
        print(f"❌ Foundation service creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_communication_foundation_service():
    """Test that Communication Foundation Service uses foundation services."""
    print("\n" + "=" * 80)
    print("TEST 4: Communication Foundation Service Integration")
    print("=" * 80)
    
    try:
        from foundations.di_container.di_container_service import DIContainerService
        from foundations.communication_foundation.communication_foundation_service import CommunicationFoundationService
        from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
        from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
        
        di_container = DIContainerService(realm_name="test")
        di_container.public_works_foundation = PublicWorksFoundationService(di_container=di_container)
        curator_foundation = CuratorFoundationService(di_container)
        
        comm_foundation = CommunicationFoundationService(
            di_container=di_container,
            public_works_foundation=di_container.public_works_foundation,
            curator_foundation=curator_foundation
        )
        
        assert comm_foundation.websocket_foundation is None, "WebSocket foundation should be None before initialization"
        assert comm_foundation.messaging_foundation is None, "Messaging foundation should be None before initialization"
        assert comm_foundation.event_bus_foundation is None, "Event Bus foundation should be None before initialization"
        print("✅ Foundation services are None before initialization")
        
        assert hasattr(comm_foundation, '_initialize_infrastructure_adapters'), "Missing _initialize_infrastructure_adapters method"
        print("✅ Communication Foundation Service has initialization method")
        
        return True
    except Exception as e:
        print(f"❌ Communication Foundation Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_abstractions_updated():
    """Test that Communication Abstractions accept foundation services."""
    print("\n" + "=" * 80)
    print("TEST 5: Communication Abstractions Updated")
    print("=" * 80)
    
    try:
        from foundations.communication_foundation.infrastructure_abstractions.communication_abstraction import CommunicationAbstraction
        from foundations.communication_foundation.infrastructure_abstractions.websocket_abstraction import WebSocketAbstraction
        import inspect
        
        comm_init = inspect.signature(CommunicationAbstraction.__init__)
        params = list(comm_init.parameters.keys())
        assert 'websocket_foundation' in params, "CommunicationAbstraction missing websocket_foundation parameter"
        assert 'messaging_foundation' in params, "CommunicationAbstraction missing messaging_foundation parameter"
        assert 'event_bus_foundation' in params, "CommunicationAbstraction missing event_bus_foundation parameter"
        print("✅ CommunicationAbstraction accepts foundation services")
        
        ws_init = inspect.signature(WebSocketAbstraction.__init__)
        ws_params = list(ws_init.parameters.keys())
        assert 'websocket_foundation' in ws_params, "WebSocketAbstraction missing websocket_foundation parameter"
        print("✅ WebSocketAbstraction accepts foundation service")
        
        return True
    except Exception as e:
        print(f"❌ Abstractions test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_old_adapters_archived():
    """Test that old adapters are archived."""
    print("\n" + "=" * 80)
    print("TEST 6: Old Adapters Archived")
    print("=" * 80)
    
    try:
        archive_dir = project_root / "symphainy-platform" / "foundations" / "communication_foundation" / "infrastructure_adapters" / "archive"
        
        assert archive_dir.exists(), "Archive directory does not exist"
        print("✅ Archive directory exists")
        
        archived_files = ["websocket_adapter.py", "messaging_adapter.py", "event_bus_adapter.py"]
        
        for filename in archived_files:
            file_path = archive_dir / filename
            assert file_path.exists(), f"Archived file {filename} not found"
            print(f"✅ {filename} is archived")
        
        main_dir = project_root / "symphainy-platform" / "foundations" / "communication_foundation" / "infrastructure_adapters"
        for filename in archived_files:
            file_path = main_dir / filename
            assert not file_path.exists(), f"Old adapter {filename} still in main directory"
            print(f"✅ {filename} not in main directory")
        
        return True
    except Exception as e:
        print(f"❌ Archive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("COMMUNICATION FOUNDATION REFACTORING TEST SUITE")
    print("=" * 80)
    print()
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("DI Container Methods", test_di_container_methods()))
    results.append(("Foundation Service Creation", await test_foundation_service_creation()))
    results.append(("Communication Foundation Integration", await test_communication_foundation_service()))
    results.append(("Abstractions Updated", test_abstractions_updated()))
    results.append(("Old Adapters Archived", test_old_adapters_archived()))
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Refactoring is successful.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
