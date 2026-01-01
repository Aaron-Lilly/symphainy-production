#!/usr/bin/env python3
"""
Test Experience Server
Simple test server to verify Experience Layer Client integration
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Test Experience Server",
    description="Simple test server for Experience Layer Client integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MOCK DATA STORAGE
# ============================================================================

# In-memory storage for testing
mock_users = {}
mock_files = {}
mock_sessions = {}

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class UserContext:
    user_id: str
    email: str
    full_name: str
    session_id: str
    tenant_id: str
    permissions: list
    created_at: str
    last_active: str

@dataclass
class FileMetadata:
    file_id: str
    filename: str
    file_type: str
    file_size: int
    upload_timestamp: str
    user_id: str
    session_id: str
    status: str
    processing_status: str

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/login")
async def login(credentials: dict):
    """Mock login endpoint."""
    try:
        email = credentials.get("email")
        password = credentials.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")
        
        # Mock authentication - accept any email/password for testing
        user_id = f"user_{email.replace('@', '_').replace('.', '_')}"
        session_id = f"session_{int(datetime.now().timestamp())}"
        
        user_context = UserContext(
            user_id=user_id,
            email=email,
            full_name=email.split('@')[0].replace('_', ' ').title(),
            session_id=session_id,
            tenant_id=user_id,
            permissions=["user", "content:read", "content:write", "insights:read", "insights:analyze"],
            created_at=datetime.now().isoformat(),
            last_active=datetime.now().isoformat()
        )
        
        # Store user and session
        mock_users[user_id] = user_context
        mock_sessions[session_id] = user_context
        
        token = f"token_{session_id}"
        
        logger.info(f"✅ User logged in: {email}")
        
        return {
            "success": True,
            "user": asdict(user_context),
            "token": token
        }
        
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        raise HTTPException(status_code=401, detail="Login failed")

@app.post("/api/auth/register")
async def register(user_data: dict):
    """Mock registration endpoint."""
    try:
        name = user_data.get("name")
        email = user_data.get("email")
        password = user_data.get("password")
        
        if not all([name, email, password]):
            raise HTTPException(status_code=400, detail="Name, email and password required")
        
        # Mock registration - create user
        user_id = f"user_{email.replace('@', '_').replace('.', '_')}"
        session_id = f"session_{int(datetime.now().timestamp())}"
        
        user_context = UserContext(
            user_id=user_id,
            email=email,
            full_name=name,
            session_id=session_id,
            tenant_id=user_id,
            permissions=["user", "content:read", "content:write", "insights:read", "insights:analyze"],
            created_at=datetime.now().isoformat(),
            last_active=datetime.now().isoformat()
        )
        
        # Store user and session
        mock_users[user_id] = user_context
        mock_sessions[session_id] = user_context
        
        token = f"token_{session_id}"
        
        logger.info(f"✅ User registered: {email}")
        
        return {
            "success": True,
            "user": asdict(user_context),
            "token": token
        }
        
    except Exception as e:
        logger.error(f"❌ Registration failed: {e}")
        raise HTTPException(status_code=400, detail="Registration failed")

@app.get("/api/auth/me")
async def get_current_user(authorization: str = None):
    """Mock get current user endpoint."""
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token")
        
        token = authorization.replace("Bearer ", "")
        session_id = token.replace("token_", "")
        
        if session_id not in mock_sessions:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_context = mock_sessions[session_id]
        
        return {
            "success": True,
            "user": asdict(user_context)
        }
        
    except Exception as e:
        logger.error(f"❌ Get current user failed: {e}")
        raise HTTPException(status_code=401, detail="Get current user failed")

@app.post("/api/auth/logout")
async def logout(authorization: str = None):
    """Mock logout endpoint."""
    try:
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            session_id = token.replace("token_", "")
            
            if session_id in mock_sessions:
                del mock_sessions[session_id]
        
        logger.info("✅ User logged out")
        
        return {"success": True}
        
    except Exception as e:
        logger.error(f"❌ Logout failed: {e}")
        return {"success": False, "error": "Logout failed"}

# ============================================================================
# CONTENT PILLAR ENDPOINTS
# ============================================================================

@app.post("/api/content/upload")
async def content_upload(
    request: Request,
    file: UploadFile = File(...),
    file_type: str = Form("pdf"),
    ui_name: str = Form(None)
):
    """Mock content upload endpoint."""
    try:
        # Get authorization from headers
        authorization = request.headers.get("authorization")
        
        # Validate authorization
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token")
        
        token = authorization.replace("Bearer ", "")
        session_id = token.replace("token_", "")
        
        if session_id not in mock_sessions:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_context = mock_sessions[session_id]
        
        # Create file metadata
        file_id = f"file_{int(datetime.now().timestamp())}"
        file_metadata = FileMetadata(
            file_id=file_id,
            filename=ui_name or file.filename,
            file_type=file_type,
            file_size=file.size or 0,
            upload_timestamp=datetime.now().isoformat(),
            user_id=user_context.user_id,
            session_id=user_context.session_id,
            status="uploaded",
            processing_status="pending"
        )
        
        # Store file
        mock_files[file_id] = file_metadata
        
        logger.info(f"✅ File uploaded: {file_metadata.filename} by {user_context.email}")
        
        return {
            "success": True,
            "file_id": file_id,
            "data": asdict(file_metadata),
            "message": "File uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ File upload failed: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

@app.get("/api/content/files")
async def content_files(request: Request):
    """Mock list files endpoint."""
    try:
        # Get authorization from headers
        authorization = request.headers.get("authorization")
        
        # Validate authorization
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token")
        
        token = authorization.replace("Bearer ", "")
        session_id = token.replace("token_", "")
        
        if session_id not in mock_sessions:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_context = mock_sessions[session_id]
        
        # Get user's files
        user_files = [
            asdict(file_metadata) 
            for file_metadata in mock_files.values() 
            if file_metadata.user_id == user_context.user_id
        ]
        
        logger.info(f"✅ Listed {len(user_files)} files for {user_context.email}")
        
        return {
            "success": True,
            "files": user_files,
            "count": len(user_files)
        }
        
    except Exception as e:
        logger.error(f"❌ List files failed: {e}")
        raise HTTPException(status_code=500, detail="List files failed")

@app.post("/api/content/parse")
async def content_parse(request: dict, authorization: str = None):
    """Mock file parsing endpoint."""
    try:
        # Validate authorization
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token")
        
        token = authorization.replace("Bearer ", "")
        session_id = token.replace("token_", "")
        
        if session_id not in mock_sessions:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        file_id = request.get("file_id")
        if not file_id or file_id not in mock_files:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_metadata = mock_files[file_id]
        
        # Mock parsing result
        parse_result = {
            "file_id": file_id,
            "format": request.get("parse_options", {}).get("format", "json_structured"),
            "chunks": [
                {"chunk_id": 1, "content": "Sample parsed content", "metadata": {"type": "text"}},
                {"chunk_id": 2, "content": "More parsed content", "metadata": {"type": "data"}}
            ],
            "structured_data": {"key": "value", "parsed": True},
            "metadata": {"parsing_time": "0.5s", "confidence": 0.95}
        }
        
        logger.info(f"✅ File parsed: {file_metadata.filename}")
        
        return {
            "success": True,
            "parse_result": parse_result
        }
        
    except Exception as e:
        logger.error(f"❌ File parsing failed: {e}")
        raise HTTPException(status_code=500, detail="File parsing failed")

@app.post("/api/content/extract-metadata")
async def content_extract_metadata(request: dict, authorization: str = None):
    """Mock metadata extraction endpoint."""
    try:
        # Validate authorization
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token")
        
        token = authorization.replace("Bearer ", "")
        session_id = token.replace("token_", "")
        
        if session_id not in mock_sessions:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        file_id = request.get("file_id")
        if not file_id or file_id not in mock_files:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_metadata = mock_files[file_id]
        
        # Mock metadata extraction result
        metadata = {
            "file_id": file_id,
            "content_metadata": {
                "title": f"Extracted from {file_metadata.filename}",
                "summary": "This is a mock extracted summary",
                "keywords": ["test", "mock", "extraction"],
                "entities": ["Entity1", "Entity2"],
                "sentiment": "positive"
            },
            "extracted_insights": [
                "Insight 1: This file contains important information",
                "Insight 2: The content is well-structured",
                "Insight 3: Key themes identified"
            ],
            "quality_score": 0.87
        }
        
        logger.info(f"✅ Metadata extracted: {file_metadata.filename}")
        
        return {
            "success": True,
            "metadata": metadata
        }
        
    except Exception as e:
        logger.error(f"❌ Metadata extraction failed: {e}")
        raise HTTPException(status_code=500, detail="Metadata extraction failed")

# ============================================================================
# INSIGHTS PILLAR ENDPOINTS
# ============================================================================

@app.post("/api/insights/analyze")
async def insights_analyze(request: dict, authorization: str = None):
    """Mock insights analysis endpoint."""
    try:
        # Validate authorization
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token")
        
        token = authorization.replace("Bearer ", "")
        session_id = token.replace("token_", "")
        
        if session_id not in mock_sessions:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        file_ids = request.get("file_ids", [])
        analysis_type = request.get("analysis_type", "comprehensive")
        
        # Mock analysis result
        analysis = {
            "analysis_id": f"analysis_{int(datetime.now().timestamp())}",
            "insights": [
                "Insight 1: Data shows strong performance trends",
                "Insight 2: Key patterns identified in user behavior",
                "Insight 3: Opportunities for optimization detected"
            ],
            "patterns": [
                {"pattern": "Seasonal variation", "confidence": 0.92},
                {"pattern": "Growth trend", "confidence": 0.88},
                {"pattern": "Anomaly detection", "confidence": 0.75}
            ],
            "recommendations": [
                "Recommendation 1: Implement automated monitoring",
                "Recommendation 2: Optimize resource allocation",
                "Recommendation 3: Focus on high-impact areas"
            ],
            "confidence_score": 0.89
        }
        
        visualization = {
            "charts": [
                {"type": "line", "title": "Trend Analysis", "data": [1, 2, 3, 4, 5]},
                {"type": "bar", "title": "Category Breakdown", "data": [10, 20, 30, 40]}
            ],
            "tables": [
                {"title": "Summary Statistics", "data": [["Metric", "Value"], ["Total", "100"], ["Average", "25"]]}
            ],
            "interactive_elements": [
                {"type": "filter", "options": ["All", "Recent", "Historical"]}
            ]
        }
        
        logger.info(f"✅ Analysis completed for {len(file_ids)} files")
        
        return {
            "success": True,
            "analysis": analysis,
            "visualization": visualization
        }
        
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

# ============================================================================
# GUIDE AGENT ENDPOINTS
# ============================================================================

@app.post("/api/global/agent/analyze")
async def global_agent_analyze(request: dict, authorization: str = None):
    """Mock guide agent analysis endpoint."""
    try:
        # Validate authorization
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="No authorization token")
        
        token = authorization.replace("Bearer ", "")
        session_id = token.replace("token_", "")
        
        if session_id not in mock_sessions:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        intent = request.get("intent", "")
        context = request.get("context", {})
        
        # Mock guidance result
        guidance = {
            "intent_analysis": f"User intent: {intent}",
            "recommended_actions": [
                "Action 1: Upload your data files to the Content pillar",
                "Action 2: Use the Insights pillar to analyze your data",
                "Action 3: Generate SOPs and workflows in the Operations pillar"
            ],
            "suggested_data_types": [
                "CSV files for structured data",
                "PDF documents for text analysis",
                "Excel files for business metrics"
            ],
            "pillar_routing": "content",
            "next_steps": [
                "Start with the Content pillar to upload your files",
                "Move to Insights for analysis and visualization",
                "Use Operations to create processes and workflows"
            ]
        }
        
        logger.info(f"✅ Guidance provided for intent: {intent}")
        
        return {
            "success": True,
            "guidance": guidance
        }
        
    except Exception as e:
        logger.error(f"❌ Guidance request failed: {e}")
        raise HTTPException(status_code=500, detail="Guidance request failed")

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "test_experience_server"
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Test Experience Server is running",
        "endpoints": [
            "/health",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/me",
            "/api/auth/logout",
            "/api/content/upload",
            "/api/content/files",
            "/api/content/parse",
            "/api/content/extract-metadata",
            "/api/insights/analyze",
            "/api/global/agent/analyze"
        ]
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    logger.info("🚀 Starting Test Experience Server...")
    uvicorn.run(
        "test_experience_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
