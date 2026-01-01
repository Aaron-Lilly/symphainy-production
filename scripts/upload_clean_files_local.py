#!/usr/bin/env python3
"""
Upload clean test files from your local machine.
This script uses your browser session token for authentication.

Usage:
1. Open your browser and log into the application
2. Open browser DevTools (F12) -> Network tab
3. Make any API request and copy the Authorization header value
4. Run this script with: python3 upload_clean_files_local.py --token YOUR_TOKEN
   OR set environment variable: export AUTH_TOKEN=YOUR_TOKEN
"""

import os
import sys
import requests
import argparse
from pathlib import Path

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://35.215.64.103")  # External URL from logs
CLEAN_FILES_DIR = Path(__file__).parent / "clean_test_files"

FILES_TO_UPLOAD = [
    {
        "file_path": CLEAN_FILES_DIR / "scenario3_annuity_data_clean.bin",
        "ui_name": "Annuity Policyholder Data (Clean)",
        "description": "Clean binary file containing annuity policyholder records (no header comments, 81-byte records). Corrected for Cobrix parsing.",
        "pillar": "insights",
        "file_type": "Binary"
    },
    {
        "file_path": CLEAN_FILES_DIR / "scenario3_copybook_clean.cpy",
        "ui_name": "COBOL Copybook (Corrected)",
        "description": "Corrected COBOL copybook with only the data record structure (POLICYHOLDER-RECORD). Removed metadata tables that caused record size miscalculation.",
        "pillar": "content",
        "file_type": "Copybook"
    }
]

def upload_file(file_path, ui_name, description, pillar, file_type, auth_token):
    """Upload a file via the API with authentication."""
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return None
    
    try:
        print(f"\n📤 Uploading: {ui_name}")
        print(f"   File: {file_path.name} ({file_path.stat().st_size} bytes)")
        
        # Determine MIME type
        ext = file_path.suffix.lower()
        mime_types = {
            '.bin': 'application/octet-stream',
            '.cpy': 'text/plain',
            '.txt': 'text/plain'
        }
        mime_type = mime_types.get(ext, 'application/octet-stream')
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {auth_token}"
        }
        
        # Prepare file and data
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, mime_type)
            }
            data = {
                'ui_name': ui_name,
                'description': description,
                'pillar': pillar,
                'file_type': file_type
            }
            
            # Upload
            response = requests.post(
                f"{API_BASE_URL}/api/v1/content-pillar/upload-file",
                files=files,
                data=data,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                uuid = result.get('uuid', result.get('file_uuid', 'N/A'))
                print(f"   ✅ Successfully uploaded!")
                print(f"   UUID: {uuid}")
                return uuid
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:300]}")
                return None
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Upload clean test files to the application")
    parser.add_argument("--token", help="Authorization token (Bearer token from browser)")
    parser.add_argument("--url", help="API base URL", default=API_BASE_URL)
    args = parser.parse_args()
    
    # Get token from args or environment
    auth_token = args.token or os.getenv("AUTH_TOKEN")
    
    if not auth_token:
        print("=" * 70)
        print("❌ Authentication token required!")
        print("=" * 70)
        print()
        print("To get your token:")
        print("  1. Open your browser and log into the application")
        print("  2. Open DevTools (F12) -> Network tab")
        print("  3. Make any API request (e.g., list files)")
        print("  4. Find the request and copy the 'Authorization' header value")
        print("     (It should look like: Bearer eyJhbGciOiJFUzI1NiIs...)")
        print("  5. Copy just the token part (after 'Bearer ')")
        print()
        print("Then run:")
        print(f"  python3 {sys.argv[0]} --token YOUR_TOKEN")
        print()
        print("Or set environment variable:")
        print("  export AUTH_TOKEN=YOUR_TOKEN")
        print("  python3", sys.argv[0])
        print()
        sys.exit(1)
    
    # Check files exist
    missing = [f for f in FILES_TO_UPLOAD if not f["file_path"].exists()]
    if missing:
        print("❌ Missing files:")
        for f in missing:
            print(f"   - {f['file_path']}")
        print("\nPlease run create_clean_test_files.py first.")
        sys.exit(1)
    
    print("=" * 70)
    print("Uploading Clean Test Files")
    print("=" * 70)
    print(f"API URL: {args.url or API_BASE_URL}")
    print()
    
    uploaded = []
    for file_info in FILES_TO_UPLOAD:
        uuid = upload_file(
            file_path=file_info["file_path"],
            ui_name=file_info["ui_name"],
            description=file_info["description"],
            pillar=file_info["pillar"],
            file_type=file_info["file_type"],
            auth_token=auth_token
        )
        if uuid:
            uploaded.append({
                "name": file_info["ui_name"],
                "uuid": uuid
            })
    
    print()
    print("=" * 70)
    print("📊 UPLOAD SUMMARY")
    print("=" * 70)
    if uploaded:
        print(f"\n✅ Successfully uploaded {len(uploaded)} files:")
        for f in uploaded:
            print(f"   - {f['name']}")
            print(f"     UUID: {f['uuid']}")
        print()
        print("🎯 Next steps:")
        print("   1. Go to Content Pillar in the UI")
        print("   2. Find 'Annuity Policyholder Data (Clean)'")
        print("   3. Use 'COBOL Copybook (Corrected)' as the copybook")
        print("   4. Test parsing - should work correctly now!")
    else:
        print("\n❌ No files uploaded successfully")
    print("=" * 70)

if __name__ == "__main__":
    main()












