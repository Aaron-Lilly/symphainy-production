#!/bin/bash
# Upload clean test files by running the script inside the backend container
# This ensures network access to the backend API

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLEAN_FILES_DIR="$SCRIPT_DIR/clean_test_files"

echo "============================================================"
echo "Uploading Clean Test Files via Backend Container"
echo "============================================================"
echo

# Check if files exist
if [ ! -f "$CLEAN_FILES_DIR/scenario3_annuity_data_clean.bin" ]; then
    echo "❌ Data file not found: $CLEAN_FILES_DIR/scenario3_annuity_data_clean.bin"
    echo "   Please run create_clean_test_files.py first"
    exit 1
fi

if [ ! -f "$CLEAN_FILES_DIR/scenario3_copybook_clean.cpy" ]; then
    echo "❌ Copybook file not found: $CLEAN_FILES_DIR/scenario3_copybook_clean.cpy"
    echo "   Please run create_clean_test_files.py first"
    exit 1
fi

# Copy files into container
echo "📋 Copying files into backend container..."
docker cp "$CLEAN_FILES_DIR/scenario3_annuity_data_clean.bin" symphainy-backend-prod:/tmp/
docker cp "$CLEAN_FILES_DIR/scenario3_copybook_clean.cpy" symphainy-backend-prod:/tmp/

# Create upload script inside container
docker exec symphainy-backend-prod python3 << 'PYTHON_SCRIPT'
import requests
import json
import os
from pathlib import Path

API_BASE_URL = "http://localhost:8000"

files_to_upload = [
    {
        "file_path": "/tmp/scenario3_annuity_data_clean.bin",
        "ui_name": "Annuity Policyholder Data (Clean)",
        "description": "Clean binary file containing annuity policyholder records (no header comments, 81-byte records). Corrected for Cobrix parsing.",
        "pillar": "insights",
        "file_type": "Binary"
    },
    {
        "file_path": "/tmp/scenario3_copybook_clean.cpy",
        "ui_name": "COBOL Copybook (Corrected)",
        "description": "Corrected COBOL copybook with only the data record structure (POLICYHOLDER-RECORD). Removed metadata tables that caused record size miscalculation.",
        "pillar": "content",
        "file_type": "Copybook"
    }
]

def upload_file(file_info):
    file_path = Path(file_info["file_path"])
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return None
    
    try:
        print(f"\n📤 Uploading: {file_info['ui_name']}")
        print(f"   File: {file_path.name}")
        print(f"   Size: {file_path.stat().st_size} bytes")
        
        # Determine MIME type
        ext = file_path.suffix.lower()
        mime_types = {
            '.bin': 'application/octet-stream',
            '.cpy': 'text/plain',
            '.txt': 'text/plain'
        }
        mime_type = mime_types.get(ext, 'application/octet-stream')
        
        # Prepare the file for upload
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, mime_type)
            }
            
            # Prepare metadata
            data = {
                'ui_name': file_info['ui_name'],
                'description': file_info['description'],
                'pillar': file_info['pillar'],
                'file_type': file_info['file_type']
            }
            
            # Try content-pillar upload endpoint
            upload_url = f"{API_BASE_URL}/api/v1/content-pillar/upload-file"
            print(f"   Endpoint: {upload_url}")
            
            response = requests.post(
                upload_url,
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Successfully uploaded: {file_info['ui_name']}")
                print(f"   UUID: {result.get('uuid', result.get('file_uuid', 'N/A'))}")
                return result
            else:
                print(f"❌ Failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:300]}")
                return None
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Upload files
uploaded = []
for file_info in files_to_upload:
    result = upload_file(file_info)
    if result:
        uploaded.append({
            "name": file_info["ui_name"],
            "uuid": result.get("uuid", result.get("file_uuid", "N/A"))
        })

# Summary
print("\n" + "=" * 60)
print("📊 UPLOAD SUMMARY")
print("=" * 60)
if uploaded:
    print(f"\n✅ Successfully uploaded {len(uploaded)} files:")
    for f in uploaded:
        print(f"   - {f['name']}")
        print(f"     UUID: {f['uuid']}")
else:
    print("\n❌ No files were uploaded successfully")
print("=" * 60)
PYTHON_SCRIPT

echo
echo "✅ Upload script completed"












