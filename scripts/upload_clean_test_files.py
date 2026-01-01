#!/usr/bin/env python3
"""
Upload clean test files to the test tenant via the backend API.
This script uploads:
1. scenario3_annuity_data_clean.bin (clean data file, no header)
2. scenario3_copybook_clean.cpy (corrected copybook, only data record)
"""

import os
import sys
import requests
import json
from pathlib import Path

# Configuration
# Try to detect if we're inside a container or on the host
# If running inside backend container, use localhost; otherwise use backend service name
if os.path.exists("/.dockerenv"):
    API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")
else:
    # Try backend service name (if in docker network) or localhost
    API_BASE_URL = os.getenv("API_BASE_URL", "http://backend:8000")

CLEAN_FILES_DIR = Path(__file__).parent / "clean_test_files"

# Files to upload
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

def upload_file_via_api(file_path, ui_name, description, pillar, file_type):
    """Upload a file directly via the backend API."""
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return None
    
    try:
        print(f"\n📤 Uploading: {ui_name}")
        print(f"   File: {file_path}")
        print(f"   Size: {file_path.stat().st_size} bytes")
        
        # Determine MIME type
        ext = file_path.suffix.lower()
        mime_types = {
            '.bin': 'application/octet-stream',
            '.cpy': 'text/plain',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.json': 'application/json'
        }
        mime_type = mime_types.get(ext, 'application/octet-stream')
        
        # Prepare the file for upload
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, mime_type)
            }
            
            # Prepare metadata
            data = {
                'ui_name': ui_name,
                'description': description,
                'pillar': pillar,
                'file_type': file_type
            }
            
            # Try the content-pillar upload endpoint
            upload_url = f"{API_BASE_URL}/api/v1/content-pillar/upload-file"
            
            print(f"   Endpoint: {upload_url}")
            
            # Upload to backend
            response = requests.post(
                upload_url,
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Successfully uploaded: {ui_name}")
                print(f"   UUID: {result.get('uuid', result.get('file_uuid', 'N/A'))}")
                print(f"   Status: {result.get('status', 'success')}")
                return result
            else:
                print(f"❌ Failed to upload {ui_name}: HTTP {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                
                # Try alternative endpoint
                alt_url = f"{API_BASE_URL}/api/fms/upload"
                print(f"   Trying alternative endpoint: {alt_url}")
                
                response2 = requests.post(
                    alt_url,
                    files=files,
                    data=data,
                    timeout=60
                )
                
                if response2.status_code == 200:
                    result = response2.json()
                    print(f"✅ Successfully uploaded via alternative endpoint: {ui_name}")
                    print(f"   UUID: {result.get('uuid', 'N/A')}")
                    return result
                else:
                    print(f"❌ Alternative endpoint also failed: HTTP {response2.status_code}")
                    print(f"   Response: {response2.text[:500]}")
                    return None
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Could not connect to {API_BASE_URL}")
        print(f"   Make sure the backend is running and accessible")
        return None
    except Exception as e:
        print(f"❌ Error uploading {ui_name}: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Upload all clean test files."""
    
    print("=" * 70)
    print("Uploading Clean Test Files to Test Tenant")
    print("=" * 70)
    print()
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Files Directory: {CLEAN_FILES_DIR}")
    print()
    
    # Check if files exist
    missing_files = [f for f in FILES_TO_UPLOAD if not f["file_path"].exists()]
    if missing_files:
        print("❌ Missing files:")
        for f in missing_files:
            print(f"   - {f['file_path']}")
        print()
        print("Please run create_clean_test_files.py first to generate the files.")
        sys.exit(1)
    
    uploaded_files = []
    
    for file_info in FILES_TO_UPLOAD:
        result = upload_file_via_api(
            file_path=file_info["file_path"],
            ui_name=file_info["ui_name"],
            description=file_info["description"],
            pillar=file_info["pillar"],
            file_type=file_info["file_type"]
        )
        
        if result:
            uploaded_files.append({
                "name": file_info["ui_name"],
                "pillar": file_info["pillar"],
                "uuid": result.get("uuid", result.get("file_uuid", "N/A")),
                "file_path": str(file_info["file_path"])
            })
    
    # Print summary
    print()
    print("=" * 70)
    print("📊 UPLOAD SUMMARY")
    print("=" * 70)
    
    if uploaded_files:
        print(f"\n✅ Successfully uploaded {len(uploaded_files)} files:")
        for file_info in uploaded_files:
            print(f"   - {file_info['name']} ({file_info['pillar']} pillar)")
            print(f"     UUID: {file_info['uuid']}")
        
        # Save results
        results_file = CLEAN_FILES_DIR / "upload_results.json"
        with open(results_file, "w") as f:
            json.dump(uploaded_files, f, indent=2)
        
        print(f"\n📄 Upload results saved to: {results_file}")
        print()
        print("🎯 Next Steps:")
        print("   1. Go to the Content Pillar in the UI")
        print("   2. Find the uploaded files")
        print("   3. Use the corrected copybook with the clean data file")
        print("   4. Test parsing - it should work correctly now!")
    else:
        print("\n❌ No files were uploaded successfully.")
        print("   Check the error messages above and ensure:")
        print("   - Backend is running and accessible")
        print("   - API endpoint is correct")
        print("   - Files exist in the clean_test_files directory")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()

