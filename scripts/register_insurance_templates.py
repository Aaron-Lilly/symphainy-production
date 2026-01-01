#!/usr/bin/env python3
"""
Register Insurance Use Case Templates

This script registers Saga Journey and Solution Composer templates
for the Insurance Use Case with the platform services.

Run this during platform initialization or as a standalone script.
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../symphainy-platform')))

from backend.business_enablement.delivery_manager.insurance_use_case_orchestrators.insurance_templates.integration_helper import integrate_insurance_templates


async def main():
    """Main function to register templates."""
    print("🚀 Registering Insurance Use Case Templates...")
    
    # TODO: Get DI container from platform initialization
    # For now, this is a placeholder that shows the integration pattern
    # In production, this would be called during platform startup
    
    print("✅ Template registration script ready")
    print("   Templates will be registered during platform initialization")
    print("   Use integrate_insurance_templates() in platform startup")


if __name__ == "__main__":
    asyncio.run(main())











