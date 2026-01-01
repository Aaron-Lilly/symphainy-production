#!/usr/bin/env python3
"""
Attempt to update Supabase rate limits via Management API.

Note: This may not work on Free tier as limits are often hard-coded.
"""

import os
import sys
import json
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def load_env_secrets():
    """Load environment variables from .env.secrets."""
    secrets_file = project_root / "symphainy-platform" / ".env.secrets"
    if not secrets_file.exists():
        return {}
    
    env_vars = {}
    with open(secrets_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def update_rate_limits(project_ref: str, access_token: str, limits: dict):
    """Attempt to update rate limit settings."""
    url = f"https://api.supabase.com/v1/projects/{project_ref}/config/auth"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"📤 Attempting to update rate limits...")
    print(f"   URL: {url}")
    print(f"   Limits: {json.dumps(limits, indent=2)}")
    print()
    
    try:
        response = requests.patch(url, headers=headers, json=limits, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Rate limits updated successfully!")
            print(f"   Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Update failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating rate limits: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return False

def main():
    """Main function."""
    print("=" * 70)
    print("Supabase Rate Limit Updater")
    print("=" * 70)
    print()
    
    # Load environment variables
    env_vars = load_env_secrets()
    
    # Get credentials
    project_ref = os.getenv("SUPABASE_PROJECT_REF") or env_vars.get("SUPABASE_PROJECT_REF")
    access_token = os.getenv("SUPABASE_ACCESS_TOKEN") or env_vars.get("SUPABASE_ACCESS_TOKEN")
    
    if not project_ref:
        print("❌ SUPABASE_PROJECT_REF not found")
        return 1
    
    if not access_token:
        print("❌ SUPABASE_ACCESS_TOKEN not found")
        return 1
    
    print(f"✅ Project Ref: {project_ref[:8]}...")
    print()
    
    # Try to increase limits
    # Note: These values may not work on Free tier
    new_limits = {
        "rate_limit_anonymous_users": 100,  # Try to increase from 30
        "rate_limit_email_sent": 100,        # Try to increase from 2
        "rate_limit_verify": 100,            # Try to increase from 30
        "rate_limit_token_refresh": 200,     # Try to increase from 150
        "rate_limit_otp": 100                # Try to increase from 30
    }
    
    success = update_rate_limits(project_ref, access_token, new_limits)
    
    print()
    print("=" * 70)
    if success:
        print("✅ Rate limit update completed")
        print()
        print("⚠️  Note: Even if the API accepted the update, Free tier")
        print("   may still enforce lower limits. Check if limits actually")
        print("   increased by running check_supabase_rate_limits.py again.")
    else:
        print("❌ Rate limit update failed")
        print()
        print("💡 This is expected on Free tier - limits are hard-coded.")
        print("   Options:")
        print("   1. Upgrade to Pro tier ($25/month) for higher limits")
        print("   2. Continue with current workarounds (graceful 429 handling)")
        print("   3. Optimize tests to use fewer requests")
    
    print("=" * 70)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())



