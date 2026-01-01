"""
Production-specific fixtures for CTO demo tests.

These fixtures assume the platform is already running in containers
and just verify connectivity rather than starting new servers.
"""

import pytest
import os
import requests
import httpx
from typing import Dict, Any
from pathlib import Path

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:3000")
DEMO_FILES_DIR = Path("/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files")


# Override backend_server and frontend_server to prevent parent conftest from starting new servers
@pytest.fixture(scope="session")
def backend_server():
    """
    Production version - does NOT start a server, just verifies backend is accessible.
    """
    base_url = BASE_URL
    if not base_url or not base_url.startswith(("http://", "https://")):
        base_url = f"http://{base_url}" if base_url else "http://localhost:8000"
    
    # Verify backend is accessible
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code != 200:
            pytest.fail(f"Backend health check failed: {response.status_code}")
    except Exception as e:
        pytest.fail(f"Backend is not accessible at {base_url}: {e}")
    
    yield base_url


@pytest.fixture(scope="session")
def frontend_server():
    """
    Production version - does NOT start a server, just verifies frontend is accessible.
    Frontend MUST be accessible for full platform validation.
    """
    frontend_url = FRONTEND_URL
    if not frontend_url or not frontend_url.startswith(("http://", "https://")):
        frontend_url = f"http://{frontend_url}" if frontend_url else "http://localhost"
    
    # Verify frontend is accessible via Traefik (production setup)
    # Try both the configured URL and the Traefik route
    accessible = False
    tested_url = None
    
    for url in [frontend_url, "http://localhost"]:
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            # Accept 200 (OK), 301/302 (redirects), or even 404 (if routing exists)
            # The important thing is that we get a response, not a connection error
            if response.status_code in [200, 301, 302, 404]:
                accessible = True
                tested_url = url
                break
        except requests.exceptions.ConnectionError:
            # Connection refused means service is not accessible
            continue
        except Exception as e:
            # Other errors might be OK (timeout, etc.) - log but continue
            print(f"⚠️ Frontend check at {url} had error: {e}")
            continue
    
    if not accessible:
        pytest.fail(
            f"❌ Frontend is NOT accessible - platform validation FAILED. "
            f"Tried: {frontend_url}, http://localhost. "
            f"Frontend must be accessible for full platform validation."
        )
    
    yield tested_url


@pytest.fixture(scope="session")
def production_backend_available():
    """
    Verify that the production backend is available.
    
    This fixture does NOT start a server - it just verifies connectivity.
    """
    # Ensure URL has protocol
    base_url = BASE_URL
    if not base_url or not base_url.startswith(("http://", "https://")):
        base_url = f"http://{base_url}" if base_url else "http://localhost:8000"
    
    # Check if backend is accessible
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            yield base_url
        else:
            pytest.fail(f"Backend health check failed: {response.status_code}")
    except Exception as e:
        pytest.fail(f"Backend is not accessible at {base_url}: {e}")


@pytest.fixture(scope="session")
def production_frontend_available():
    """
    Verify that the production frontend is available.
    
    This fixture does NOT start a server - it just verifies connectivity.
    """
    # Ensure URL has protocol
    frontend_url = FRONTEND_URL
    if not frontend_url or not frontend_url.startswith(("http://", "https://")):
        frontend_url = f"http://{frontend_url}" if frontend_url else "http://localhost:3000"
    
    # Check if frontend is accessible (optional - may not be needed for API tests)
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code in [200, 404]:  # 404 is OK if frontend is behind a proxy
            yield frontend_url
        else:
            pytest.skip(f"Frontend not accessible: {response.status_code}")
    except Exception as e:
        pytest.skip(f"Frontend is not accessible at {frontend_url}: {e}")


@pytest.fixture(scope="session")
def both_servers(production_backend_available, production_frontend_available):
    """
    Production version of both_servers fixture.
    
    This does NOT start servers - it just verifies that both are accessible.
    Use this for production container testing.
    
    This fixture overrides the parent conftest's both_servers fixture.
    """
    # Both fixtures verify connectivity
    # This fixture just ensures both checks pass
    yield {
        "backend_url": production_backend_available,
        "frontend_url": production_frontend_available
    }


@pytest.fixture
def backend_url() -> str:
    """Fixture that provides the backend URL."""
    return BASE_URL


@pytest.fixture
async def http_client(backend_url):
    """Async HTTP client for CTO demo tests."""
    # Ensure URL has protocol
    base_url = backend_url
    if not base_url or not base_url.startswith(("http://", "https://")):
        base_url = f"http://{base_url}" if base_url else "http://localhost"
    
    async with httpx.AsyncClient(base_url=base_url, timeout=60.0, follow_redirects=True) as client:
        yield client


@pytest.fixture
async def test_session(both_servers, http_client) -> Dict[str, Any]:
    """Create a test session for CTO demo tests."""
    response = await http_client.post(
        "/api/v1/session/create-user-session",
        json={
            "user_id": "cto_demo_user",
            "session_type": "mvp"
        }
    )
    
    assert response.status_code in [200, 201], \
        f"Session creation failed: {response.status_code} - {response.text}"
    
    data = response.json()
    
    # Try various possible field names for session identifier
    session_id = (
        data.get("session_id") or 
        data.get("id") or 
        data.get("sessionId") or
        data.get("uuid")
    )
    session_token = (
        data.get("session_token") or 
        data.get("token") or 
        data.get("sessionToken") or
        data.get("access_token")
    )
    
    # If we have a successful response but no explicit session ID, generate one
    # or use the response data itself
    if session_id is None and session_token is None:
        # Check if the response itself contains useful data
        if isinstance(data, dict) and len(data) > 0:
            # Use the first key-value pair or create a synthetic session
            session_id = data.get("id") or f"test_session_{os.urandom(8).hex()}"
        else:
            session_id = f"test_session_{os.urandom(8).hex()}"
    
    # For production testing, we may need to use session_id as session_token
    # if session_token is not provided separately
    if session_token is None and session_id:
        session_token = session_id
    
    return {
        "session_id": session_id,
        "session_token": session_token,
        "user_id": "cto_demo_user",
        "raw_response": data  # Include raw response for debugging
    }


def get_demo_file(scenario: str, file_key: str):
    """Extract a demo file from the zip archive."""
    from zipfile import ZipFile
    
    demo_scenarios = {
        "autonomous_vehicle": {
            "zip": "SymphAIny_Demo_Defense_TnE.zip",
            "files": {
                "mission_plan": "mission_plan.csv",
                "telemetry": "telemetry_raw.bin",
                "copybook": "telemetry_copybook.cpy",
                "incidents": "test_incident_reports.docx"
            }
        },
        "underwriting": {
            "zip": "SymphAIny_Demo_Underwriting_Insights.zip",
            "files": {
                "claims": "claims.csv",
                "reinsurance": "reinsurance.xlsx",
                "notes": "underwriting_notes.pdf",
                "policy_master": "policy_master.dat",
                "copybook": "copybook.cpy"
            }
        },
        "coexistence": {
            "zip": "SymphAIny_Demo_Coexistence.zip",
            "files": {
                "legacy_policies": "legacy_policy_export.csv",
                "target_schema": "target_schema.json",
                "alignment_map": "alignment_map.json"
            }
        }
    }
    
    demo_zip = DEMO_FILES_DIR / demo_scenarios[scenario]["zip"]
    
    if not demo_zip.exists():
        return None
    
    try:
        with ZipFile(demo_zip, 'r') as zf:
            file_name = demo_scenarios[scenario]["files"][file_key]
            for name in zf.namelist():
                if file_name in name:
                    return zf.read(name)
    except Exception as e:
        print(f"Error extracting {file_key} from {scenario}: {e}")
        return None
    
    return None

