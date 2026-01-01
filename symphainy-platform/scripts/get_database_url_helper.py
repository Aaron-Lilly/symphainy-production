#!/usr/bin/env python3
"""
Helper Script: Get DATABASE_URL from Supabase

This script helps you get the DATABASE_URL by:
1. Extracting project reference from SUPABASE_URL
2. Providing instructions to get password from Supabase Dashboard
3. Constructing the DATABASE_URL once you have the password
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Load environment secrets
secrets_file = project_root / ".env.secrets"
if not secrets_file.exists():
    secrets_file = project_root / "env_secrets_for_cursor.md"

if secrets_file.exists():
    load_dotenv(secrets_file)

def extract_project_ref(supabase_url: str) -> str:
    """Extract project reference from Supabase URL."""
    try:
        # Format: https://rmymvrifwvqpeffmxkwi.supabase.co
        if "supabase.co" in supabase_url:
            parts = supabase_url.replace("https://", "").replace("http://", "").split(".")
            return parts[0]
        return None
    except:
        return None

def main():
    """Main helper function."""
    print("=" * 70)
    print("Supabase DATABASE_URL Helper")
    print("=" * 70)
    print()
    
    # Get SUPABASE_URL
    supabase_url = os.getenv("SUPABASE_URL")
    
    if not supabase_url:
        print("❌ SUPABASE_URL not found in environment")
        print("   Check your .env.secrets file")
        sys.exit(1)
    
    print(f"✅ Found SUPABASE_URL: {supabase_url}")
    
    # Extract project reference
    project_ref = extract_project_ref(supabase_url)
    
    if not project_ref:
        print("⚠️  Could not extract project reference from SUPABASE_URL")
        print(f"   URL: {supabase_url}")
        print("   Please extract manually from Supabase Dashboard")
        sys.exit(1)
    
    print(f"✅ Project Reference: {project_ref}")
    print()
    
    # Check if DATABASE_URL already exists
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        print("✅ DATABASE_URL already set!")
        print(f"   {database_url[:50]}...")
        print()
        print("You can now run migrations:")
        print("   python3 scripts/run_supabase_migrations.py")
        return
    
    print("📋 To get DATABASE_URL:")
    print()
    print("1. Go to Supabase Dashboard:")
    print(f"   https://supabase.com/dashboard/project/{project_ref}")
    print()
    print("2. Navigate to:")
    print("   Settings → Database → Connection string")
    print()
    print("3. Select 'URI' tab")
    print()
    print("4. Copy the connection string")
    print("   It will look like:")
    print(f"   postgresql://postgres.{project_ref}:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres")
    print()
    print("5. Replace [PASSWORD] with your actual database password")
    print("   (Password may be shown or you may need to reset it)")
    print()
    print("6. Add to .env.secrets:")
    print("   DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-us-west-1.pooler.supabase.com:6543/postgres")
    print()
    
    # Construct template
    template_url = f"postgresql://postgres.{project_ref}:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
    
    print("📝 Template DATABASE_URL (replace [YOUR-PASSWORD]):")
    print(f"   {template_url}")
    print()
    
    # Ask if user wants to set it now
    print("💡 Once you have the password, you can:")
    print("   1. Add DATABASE_URL to .env.secrets manually")
    print("   2. Or run this script again with the password to set it")
    print()
    
    # Option to set password interactively
    response = input("Do you have the database password and want to set DATABASE_URL now? (yes/no): ").strip().lower()
    
    if response == 'yes':
        password = input("Enter database password: ").strip()
        
        if password:
            database_url = f"postgresql://postgres.{project_ref}:{password}@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
            
            print()
            print("📝 Add this to your .env.secrets file:")
            print(f"DATABASE_URL={database_url}")
            print()
            
            # Option to append to .env.secrets
            append_response = input("Append to .env.secrets file now? (yes/no): ").strip().lower()
            
            if append_response == 'yes':
                try:
                    with open(secrets_file, 'a') as f:
                        f.write(f"\n# Database connection string for migrations\n")
                        f.write(f"DATABASE_URL={database_url}\n")
                    print(f"✅ Added DATABASE_URL to {secrets_file}")
                    print()
                    print("You can now run migrations:")
                    print("   python3 scripts/run_supabase_migrations.py")
                except Exception as e:
                    print(f"❌ Failed to write to {secrets_file}: {e}")
                    print("   Please add it manually")
            else:
                print("   Please add it manually to .env.secrets")
        else:
            print("❌ Password cannot be empty")
    else:
        print()
        print("📋 Steps to complete:")
        print("   1. Get password from Supabase Dashboard")
        print("   2. Add DATABASE_URL to .env.secrets")
        print("   3. Run: python3 scripts/run_supabase_migrations.py")

if __name__ == "__main__":
    main()






