#!/usr/bin/env python3
"""
Quick test script to verify Phase 1 imports work correctly.
Tests that there are no circular dependencies and imports succeed.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('symphainy-platform'))

def test_imports():
    """Test that all imports work without circular dependencies."""
    print("🧪 Testing Phase 1 imports...")
    print()
    
    # Test 1: Import ContentJourneyOrchestrator
    print("1. Testing ContentJourneyOrchestrator import...")
    try:
        from backend.journey.orchestrators.content_journey_orchestrator.content_analysis_orchestrator import ContentJourneyOrchestrator
        print("   ✅ ContentJourneyOrchestrator imported successfully")
        print(f"   ✅ Service name: {ContentJourneyOrchestrator.__name__}")
    except Exception as e:
        print(f"   ❌ Failed to import ContentJourneyOrchestrator: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Import DataSolutionOrchestrator
    print("2. Testing DataSolutionOrchestrator import...")
    try:
        from backend.solution.services.data_solution_orchestrator_service.data_solution_orchestrator_service import DataSolutionOrchestratorService
        print("   ✅ DataSolutionOrchestratorService imported successfully")
        print(f"   ✅ Service name: {DataSolutionOrchestratorService.__name__}")
    except Exception as e:
        print(f"   ❌ Failed to import DataSolutionOrchestratorService: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Verify no circular dependency
    print("3. Testing for circular dependencies...")
    try:
        # Try importing both together
        from backend.journey.orchestrators.content_journey_orchestrator.content_analysis_orchestrator import ContentJourneyOrchestrator
        from backend.solution.services.data_solution_orchestrator_service.data_solution_orchestrator_service import DataSolutionOrchestratorService
        print("   ✅ No circular dependencies detected")
    except Exception as e:
        print(f"   ❌ Circular dependency detected: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Check class attributes
    print("4. Checking class attributes...")
    try:
        # Check ContentJourneyOrchestrator __init__ signature
        import inspect
        sig = inspect.signature(ContentJourneyOrchestrator.__init__)
        params = list(sig.parameters.keys())
        print(f"   ✅ ContentJourneyOrchestrator.__init__ parameters: {params}")
        
        # Verify it takes platform_gateway and di_container (not content_manager)
        if 'content_manager' in params:
            print("   ⚠️  Warning: ContentJourneyOrchestrator still takes content_manager parameter")
        if 'platform_gateway' in params and 'di_container' in params:
            print("   ✅ ContentJourneyOrchestrator takes platform_gateway and di_container")
        else:
            print("   ⚠️  Warning: ContentJourneyOrchestrator doesn't take expected parameters")
    except Exception as e:
        print(f"   ⚠️  Could not check class attributes: {e}")
    
    print()
    print("✅ All import tests passed!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)



