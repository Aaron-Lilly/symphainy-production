#!/usr/bin/env python3
"""
Check and display Supabase rate limit settings.

Uses Supabase Management API to:
1. Check current rate limit settings
2. Display current plan/tier
3. Attempt to adjust limits (if possible)
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
    # Try multiple possible locations
    possible_paths = [
        project_root / "symphainy-platform" / ".env.secrets",
        project_root / ".env.secrets",
        Path.cwd() / "symphainy-platform" / ".env.secrets",
        Path.cwd() / ".env.secrets"
    ]
    
    secrets_file = None
    for path in possible_paths:
        if path.exists():
            secrets_file = path
            break
    
    if not secrets_file:
        # Don't print error - just return empty dict (env vars might be set directly)
        return {}
    
    env_vars = {}
    with open(secrets_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def get_rate_limits(project_ref: str, access_token: str):
    """Get current rate limit settings from Supabase Management API."""
    url = f"https://api.supabase.com/v1/projects/{project_ref}/config/auth"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching rate limits: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def get_project_info(project_ref: str, access_token: str):
    """Get project information including plan/tier."""
    url = f"https://api.supabase.com/v1/projects/{project_ref}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching project info: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def update_rate_limits(project_ref: str, access_token: str, limits: dict):
    """Attempt to update rate limit settings."""
    url = f"https://api.supabase.com/v1/projects/{project_ref}/config/auth"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.patch(url, headers=headers, json=limits, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating rate limits: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None

def main():
    """Main function."""
    print("=" * 70)
    print("Supabase Rate Limit Checker")
    print("=" * 70)
    print()
    
    # Load environment variables
    env_vars = load_env_secrets()
    
    # Get credentials
    project_ref = os.getenv("SUPABASE_PROJECT_REF") or env_vars.get("SUPABASE_PROJECT_REF")
    access_token = os.getenv("SUPABASE_ACCESS_TOKEN") or env_vars.get("SUPABASE_ACCESS_TOKEN")
    
    if not project_ref:
        print("❌ SUPABASE_PROJECT_REF not found")
        print("   Set in .env.secrets or environment variable")
        return 1
    
    if not access_token:
        print("❌ SUPABASE_ACCESS_TOKEN not found")
        print("   Set in .env.secrets or environment variable")
        return 1
    
    print(f"✅ Project Ref: {project_ref[:8]}...")
    print(f"✅ Access Token: {access_token[:20]}...")
    print()
    
    # Get project info
    print("📊 Fetching project information...")
    project_info = get_project_info(project_ref, access_token)
    if project_info:
        print(f"✅ Project: {project_info.get('name', 'Unknown')}")
        print(f"   Region: {project_info.get('region', 'Unknown')}")
        print(f"   Organization: {project_info.get('organization_id', 'Unknown')}")
        # Plan/tier might be in different location
        print()
    
    # Get rate limits
    print("📊 Fetching rate limit settings...")
    auth_config = get_rate_limits(project_ref, access_token)
    
    if not auth_config:
        print("❌ Could not fetch rate limits")
        return 1
    
    # Display rate limits
    print("\n" + "=" * 70)
    print("Current Rate Limit Settings")
    print("=" * 70)
    
    rate_limit_keys = [k for k in auth_config.keys() if 'rate_limit' in k.lower()]
    
    if rate_limit_keys:
        for key in sorted(rate_limit_keys):
            value = auth_config[key]
            print(f"  {key}: {value}")
    else:
        print("  ⚠️  No rate limit settings found in response")
        print("\n  Full auth config (first 20 keys):")
        for i, key in enumerate(list(auth_config.keys())[:20]):
            print(f"    {key}: {auth_config[key]}")
    
    print("\n" + "=" * 70)
    print("Rate Limit Analysis")
    print("=" * 70)
    
    # Check if we can identify the plan
    # Free tier typically has lower limits
    anonymous_limit = auth_config.get('rate_limit_anonymous_users') or auth_config.get('RATE_LIMIT_ANONYMOUS_USERS')
    email_limit = auth_config.get('rate_limit_email_sent') or auth_config.get('RATE_LIMIT_EMAIL_SENT')
    
    if anonymous_limit:
        print(f"\n📈 Anonymous User Rate Limit: {anonymous_limit}")
        if anonymous_limit <= 60:
            print("   ⚠️  This appears to be Free tier (60 req/min limit)")
            print("   💡 Consider upgrading to Pro tier for higher limits")
        else:
            print("   ✅ Higher limit detected (likely Pro tier or higher)")
    
    if email_limit:
        print(f"\n📧 Email Sending Rate Limit: {email_limit}")
        if email_limit <= 2:
            print("   ⚠️  Very low email limit (2/hour on Free tier)")
            print("   💡 Consider using custom SMTP for higher limits")
    
    print("\n" + "=" * 70)
    print("Recommendations")
    print("=" * 70)
    
    print("\n1. **Check Plan/Tier in Dashboard:**")
    print("   - Go to: Settings → Billing")
    print("   - See current plan (Free/Pro/Team)")
    
    print("\n2. **If on Free Tier:**")
    print("   - Rate limits are typically hard-coded")
    print("   - May not be adjustable via API")
    print("   - Consider upgrading to Pro ($25/month)")
    
    print("\n3. **Alternative Workarounds:**")
    print("   - ✅ Already implemented: Graceful 429 handling")
    print("   - ✅ Already implemented: Test mode throttling")
    print("   - 💡 Add longer delays between test batches")
    print("   - 💡 Run tests in smaller groups")
    print("   - 💡 Use multiple test projects (rotate)")
    
    print("\n4. **Try to Update Limits (may not work on Free tier):**")
    response = input("\n   Attempt to increase limits? (y/N): ").strip().lower()
    
    if response == 'y':
        print("\n   Attempting to update rate limits...")
        # Try to increase common limits
        new_limits = {
            "rate_limit_anonymous_users": 100,
            "rate_limit_email_sent": 100,
            "rate_limit_verify": 100,
            "rate_limit_token_refresh": 100
        }
        
        result = update_rate_limits(project_ref, access_token, new_limits)
        if result:
            print("   ✅ Rate limits updated successfully!")
            print(f"   New settings: {json.dumps(result, indent=2)}")
        else:
            print("   ❌ Could not update rate limits")
            print("   This is expected on Free tier - limits are hard-coded")
    
    print("\n" + "=" * 70)
    print("✅ Rate limit check complete")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

