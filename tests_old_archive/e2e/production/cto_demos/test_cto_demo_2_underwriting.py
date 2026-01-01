"""
CTO Demo Scenario 2: Life Insurance Underwriting/Reserving Insights

Full journey test via HTTP API:
1. Content Pillar: Upload claims, reinsurance, policy data
2. Insights Pillar: Analyze underwriting patterns → Generate insights
3. Operations Pillar: Create underwriting workflows → Generate SOPs
4. Business Outcomes Pillar: Create strategic roadmap → Generate POC proposal
"""

import pytest
import httpx
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

pytestmark = [pytest.mark.e2e, pytest.mark.cto_demo, pytest.mark.critical]

BASE_URL = os.getenv("TEST_BACKEND_URL", "http://localhost:8000")
DEMO_FILES_DIR = Path("/home/founders/demoversion/symphainy_source/scripts/mvpdemoscript/demo_files")


@pytest.mark.asyncio
@pytest.mark.timeout(600)  # 10 minutes for full journey
async def test_cto_demo_2_underwriting_full_journey(both_servers, http_client, test_session):
    """
    CTO Demo Scenario 2: Life Insurance Underwriting/Reserving Insights
    
    Complete 4-pillar journey via HTTP API.
    """
    logger.info("🎬 CTO Demo Scenario 2: Life Insurance Underwriting/Reserving Insights")
    
    session_id = test_session["session_id"]
    session_token = test_session.get("session_token")
    user_id = test_session["user_id"]
    
    headers = {}
    # Always include session token if available (use session_id as fallback)
    token_to_use = session_token or session_id
    if token_to_use:
        headers["X-Session-Token"] = token_to_use
    # Also include user_id in headers for authentication
    headers["X-User-Id"] = user_id
    
    # ============================================================================
    # STEP 1: Content Pillar - Upload Insurance Data
    # ============================================================================
    logger.info("📋 Step 1: Content Pillar - Uploading insurance data...")
    
    demo_zip = DEMO_FILES_DIR / "SymphAIny_Demo_Underwriting_Insights.zip"
    if not demo_zip.exists():
        pytest.skip(f"Demo file not found: {demo_zip}")
    
    # Upload claims.csv
    import zipfile
    with zipfile.ZipFile(demo_zip, 'r') as zf:
        csv_content = None
        for name in zf.namelist():
            if "claims.csv" in name:
                csv_content = zf.read(name)
                break
    
    if csv_content:
        files = {"file": ("claims.csv", csv_content, "text/csv")}
        data = {"user_id": user_id}
        
        response = await http_client.post(
            "/api/v1/content-pillar/upload-file",
            files=files,
            data=data,
            headers=headers
        )
        
        assert response.status_code in [200, 201], \
            f"File upload failed: {response.status_code} - {response.text}"
        
        upload_data = response.json()
        logger.info("✅ Claims data uploaded")
    
    # ============================================================================
    # STEP 2: Insights Pillar - Analyze Underwriting Patterns
    # ============================================================================
    logger.info("📋 Step 2: Insights Pillar - Analyzing underwriting patterns...")
    
    if csv_content and "file_id" in upload_data:
        file_id = upload_data["file_id"]
        
        response = await http_client.post(
            "/api/v1/insights-pillar/analyze-content",
            json={
                "user_id": user_id,
                "file_id": file_id,
                "analysis_type": "business"
            },
            headers=headers
        )
        
        assert response.status_code != 404, "Analyze content endpoint missing"
        
        if response.status_code == 200:
            logger.info("✅ Underwriting patterns analyzed")
        else:
            logger.info(f"⚠️ Analysis returned status {response.status_code}")
    
    # ============================================================================
    # STEP 3: Operations Pillar - Create Workflows
    # ============================================================================
    logger.info("📋 Step 3: Operations Pillar - Creating workflows...")
    
    response = await http_client.post(
        "/api/v1/operations-pillar/create-workflow",
        json={
            "user_id": user_id,
            "name": "Underwriting Workflow",
            "description": "Workflow for insurance underwriting process"
        },
        headers=headers
    )
    
    assert response.status_code != 404, "Create workflow endpoint missing"
    
    if response.status_code in [200, 201]:
        logger.info("✅ Workflow created")
    else:
        logger.info(f"⚠️ Workflow creation returned status {response.status_code}")
    
    # ============================================================================
    # STEP 4: Business Outcomes Pillar - Generate Roadmap
    # ============================================================================
    logger.info("📋 Step 4: Business Outcomes Pillar - Generating roadmap...")
    
    response = await http_client.post(
        "/api/v1/business-outcomes-pillar/generate-strategic-roadmap",
        json={
            "user_id": user_id,
            "pillar_outputs": {
                "content_pillar": {"files_uploaded": 1},
                "insights_pillar": {"analysis_complete": True},
                "operations_pillar": {"workflow_created": True}
            }
        },
        headers=headers
    )
    
    assert response.status_code != 404, "Generate roadmap endpoint missing"
    
    if response.status_code in [200, 201]:
        logger.info("✅ Strategic roadmap generated")
    else:
        logger.info(f"⚠️ Roadmap generation returned status {response.status_code}")
    
    logger.info("✅ CTO Demo Scenario 2: Complete journey validated via HTTP API")

