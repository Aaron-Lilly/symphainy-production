#!/usr/bin/env python3
"""
Simple test to verify imports work.
"""

print("🚀 Starting simple test...")

try:
    from backend.smart_city.services.traffic_cop import TrafficCopService
    print("✅ TrafficCopService import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")

try:
    from backend.smart_city.interfaces import ISessionManagement
    print("✅ ISessionManagement import successful")
except Exception as e:
    print(f"❌ Interface import failed: {e}")

try:
    from backend.smart_city.protocols import SOAServiceBase
    print("✅ SOAServiceBase import successful")
except Exception as e:
    print(f"❌ Protocol import failed: {e}")

print("🏁 Simple test completed!")
