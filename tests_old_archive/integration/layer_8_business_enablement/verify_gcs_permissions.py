#!/usr/bin/env python3
"""
GCS Permissions Verification Script

Verifies IAM permissions for GCS bucket access.
Checks:
1. Service account credentials file
2. Service account IAM roles
3. Bucket IAM policy
4. Actual upload test
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def resolve_credentials_path(relative_path: str) -> str:
    """Resolve relative credentials path to absolute."""
    if os.path.isabs(relative_path):
        return relative_path
    
    # Try project root
    project_root = Path.cwd()
    if (project_root / "symphainy-platform").exists():
        resolved = (project_root / relative_path).resolve()
        if resolved.exists():
            return str(resolved)
    
    # Try symphainy-platform/backend
    if (project_root / "symphainy-platform" / "backend" / Path(relative_path).name).exists():
        resolved = (project_root / "symphainy-platform" / "backend" / Path(relative_path).name).resolve()
        if resolved.exists():
            return str(resolved)
    
    # Try current directory
    resolved = (Path.cwd() / relative_path).resolve()
    if resolved.exists():
        return str(resolved)
    
    return relative_path

def check_credentials_file(credentials_path: str):
    """Check credentials file exists and is valid."""
    print("\n" + "="*70)
    print("1. CHECKING CREDENTIALS FILE")
    print("="*70)
    
    resolved_path = resolve_credentials_path(credentials_path)
    
    if not os.path.exists(resolved_path):
        print(f"❌ Credentials file not found: {resolved_path}")
        return None
    
    print(f"✅ Credentials file found: {resolved_path}")
    
    try:
        with open(resolved_path, 'r') as f:
            creds = json.load(f)
        
        print(f"   Project ID: {creds.get('project_id', 'NOT FOUND')}")
        print(f"   Client Email: {creds.get('client_email', 'NOT FOUND')}")
        print(f"   Type: {creds.get('type', 'NOT FOUND')}")
        print(f"   Has Private Key: {'Yes' if creds.get('private_key') else 'No'}")
        
        # Check scopes (may not be in service account JSON)
        if 'scopes' in creds:
            print(f"   Scopes: {creds.get('scopes')}")
        else:
            print(f"   Scopes: Not specified (uses default: https://www.googleapis.com/auth/cloud-platform)")
        
        return creds
    except Exception as e:
        print(f"❌ Error reading credentials file: {e}")
        return None

def check_service_account_iam(service_account_email: str, project_id: str):
    """Check service account IAM roles using gcloud."""
    print("\n" + "="*70)
    print("2. CHECKING SERVICE ACCOUNT IAM ROLES")
    print("="*70)
    
    print(f"   Service Account: {service_account_email}")
    print(f"   Project: {project_id}")
    
    # Check project-level IAM
    import subprocess
    try:
        result = subprocess.run(
            ['gcloud', 'projects', 'get-iam-policy', project_id,
             '--flatten=bindings[].members',
             '--filter=f"bindings.members:{service_account_email}"',
             '--format=json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            policy = json.loads(result.stdout)
            if policy:
                print("✅ Service account has project-level IAM roles:")
                for binding in policy:
                    role = binding.get('role', 'Unknown')
                    print(f"   - {role}")
            else:
                print("⚠️  No project-level IAM roles found for this service account")
        else:
            print(f"⚠️  Could not check IAM policy: {result.stderr}")
            print("   (This is OK if gcloud is not configured)")
    except FileNotFoundError:
        print("⚠️  gcloud CLI not found - skipping IAM check")
        print("   Install gcloud CLI to check IAM permissions")
    except subprocess.TimeoutExpired:
        print("⚠️  IAM check timed out")
    except Exception as e:
        print(f"⚠️  Error checking IAM: {e}")

def check_bucket_iam(bucket_name: str):
    """Check bucket IAM policy using gsutil."""
    print("\n" + "="*70)
    print("3. CHECKING BUCKET IAM POLICY")
    print("="*70)
    
    print(f"   Bucket: {bucket_name}")
    
    import subprocess
    try:
        result = subprocess.run(
            ['gsutil', 'iam', 'get', f'gs://{bucket_name}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            policy = json.loads(result.stdout)
            print("✅ Bucket IAM policy retrieved:")
            print(json.dumps(policy, indent=2))
        else:
            print(f"⚠️  Could not get bucket IAM policy: {result.stderr}")
            print("   (This is OK if gsutil is not configured)")
    except FileNotFoundError:
        print("⚠️  gsutil not found - skipping bucket IAM check")
        print("   Install gsutil to check bucket permissions")
    except subprocess.TimeoutExpired:
        print("⚠️  Bucket IAM check timed out")
    except Exception as e:
        print(f"⚠️  Error checking bucket IAM: {e}")

def test_gcs_upload(credentials_path: str, project_id: str, bucket_name: str):
    """Test actual GCS upload with credentials."""
    print("\n" + "="*70)
    print("4. TESTING GCS UPLOAD")
    print("="*70)
    
    resolved_path = resolve_credentials_path(credentials_path)
    
    if not os.path.exists(resolved_path):
        print(f"❌ Credentials file not found: {resolved_path}")
        return False
    
    try:
        from google.cloud import storage
        from google.cloud.exceptions import Forbidden, GoogleCloudError
        
        print(f"   Using credentials: {resolved_path}")
        print(f"   Project: {project_id}")
        print(f"   Bucket: {bucket_name}")
        
        # Create client with explicit credentials
        client = storage.Client.from_service_account_json(
            resolved_path,
            project=project_id
        )
        
        # Get bucket
        bucket = client.bucket(bucket_name)
        
        # Test upload
        test_blob_name = "permissions_test.txt"
        test_content = "GCS Permissions Test - This file can be deleted"
        
        print(f"   Uploading test file: {test_blob_name}")
        blob = bucket.blob(test_blob_name)
        blob.upload_from_string(
            test_content,
            content_type="text/plain"
        )
        
        print("✅ Upload successful!")
        print(f"   Test file uploaded: gs://{bucket_name}/{test_blob_name}")
        
        # Clean up test file
        try:
            blob.delete()
            print("✅ Test file deleted (cleanup successful)")
        except Exception as e:
            print(f"⚠️  Could not delete test file: {e}")
            print(f"   Please manually delete: gs://{bucket_name}/{test_blob_name}")
        
        return True
        
    except Forbidden as e:
        print(f"❌ Permission denied (403 Forbidden): {e}")
        print("\n   This indicates the service account lacks required permissions.")
        print("   Required IAM roles:")
        print("     - roles/storage.objectCreator (to upload)")
        print("     - roles/storage.objectViewer (to read)")
        print("   OR")
        print("   Bucket IAM policy must grant these permissions to the service account.")
        return False
        
    except GoogleCloudError as e:
        print(f"❌ GCS Error: {e}")
        return False
        
    except ImportError:
        print("❌ google-cloud-storage not installed")
        print("   Install with: pip install google-cloud-storage")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification function."""
    print("="*70)
    print("GCS PERMISSIONS VERIFICATION")
    print("="*70)
    
    # Get configuration
    credentials_path = os.getenv("GCS_CREDENTIALS_PATH", "backend/symphainymvp-devbox-40d941571d46.json")
    project_id = os.getenv("GCS_PROJECT_ID", "symphainymvp-devbox")
    bucket_name = os.getenv("GCS_BUCKET_NAME", "symphainy-bucket-2025")
    
    print(f"\nConfiguration:")
    print(f"   GCS_CREDENTIALS_PATH: {credentials_path}")
    print(f"   GCS_PROJECT_ID: {project_id}")
    print(f"   GCS_BUCKET_NAME: {bucket_name}")
    
    # Check credentials file
    creds = check_credentials_file(credentials_path)
    if not creds:
        print("\n❌ Cannot proceed without valid credentials file")
        return 1
    
    service_account_email = creds.get('client_email')
    if not service_account_email:
        print("\n❌ Credentials file missing client_email")
        return 1
    
    # Check IAM roles
    check_service_account_iam(service_account_email, project_id)
    
    # Check bucket IAM
    check_bucket_iam(bucket_name)
    
    # Test upload
    upload_success = test_gcs_upload(credentials_path, project_id, bucket_name)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    if upload_success:
        print("✅ All checks passed! GCS permissions are correctly configured.")
        return 0
    else:
        print("❌ Upload test failed. Check IAM permissions:")
        print(f"   1. Grant service account '{service_account_email}' these roles:")
        print(f"      - roles/storage.objectCreator")
        print(f"      - roles/storage.objectViewer")
        print(f"   2. OR add service account to bucket IAM policy with these permissions")
        print(f"   3. Run: gcloud projects add-iam-policy-binding {project_id} \\")
        print(f"      --member='serviceAccount:{service_account_email}' \\")
        print(f"      --role='roles/storage.objectCreator'")
        return 1

if __name__ == "__main__":
    sys.exit(main())


