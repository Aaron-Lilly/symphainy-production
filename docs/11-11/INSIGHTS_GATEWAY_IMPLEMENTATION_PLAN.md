# Insights Pillar → FrontendGatewayService Implementation Plan

**Date**: November 11, 2025  
**Goal**: Wire Insights Pillar semantic router to use FrontendGatewayService  
**Estimated Time**: 2 hours

---

## 🎯 Current State

### Semantic Router (insights_pillar_router.py)
**Location**: `backend/experience/api/semantic/insights_pillar_router.py`

**9 Endpoints**:
1. POST `/api/insights-pillar/analyze-content`
2. POST `/api/insights-pillar/query-analysis`
3. GET  `/api/insights-pillar/get-available-content-metadata`
4. POST `/api/insights-pillar/validate-content-metadata`
5. GET  `/api/insights-pillar/get-analysis-results/{analysis_id}`
6. GET  `/api/insights-pillar/get-analysis-visualizations/{analysis_id}`
7. GET  `/api/insights-pillar/list-user-analyses`
8. GET  `/api/insights-pillar/pillar-summary`
9. GET  `/api/insights-pillar/health`

**Current Pattern** (WRONG):
```python
@router.post("/analyze-content")
async def analyze_content(...):
    # ❌ Directly calling orchestrator
    business_orchestrator = get_business_orchestrator()
    insights_orchestrator = business_orchestrator.insights_orchestrator
    result = await insights_orchestrator.analyze_content(...)
    return result
```

### FrontendGatewayService
**Location**: `backend/experience/services/frontend_gateway_service/frontend_gateway_service.py`

**Current Insights Handler**:
```python
async def handle_insights_request(
    self,
    data_id: str,
    insight_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Old generic insights handler"""
    result = await self.insights_orchestrator.generate_insights(...)
    return result
```

**Need**: Add 9 new semantic API handlers

---

## 📋 Implementation Steps

### Step 1: Add Handlers to FrontendGatewayService (1 hour)

**File**: `backend/experience/services/frontend_gateway_service/frontend_gateway_service.py`

Add new section after existing handlers (around line 644):

```python
# ========================================================================
# INSIGHTS PILLAR SEMANTIC API HANDLERS
# ========================================================================

async def handle_analyze_content_for_insights_request(
    self,
    content_metadata_ids: List[str],
    analysis_type: str = "auto",
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle analyze content request (Frontend API → InsightsOrchestrator).
    Semantic API: Analyze content metadata for insights.
    """
    try:
        if not self.insights_orchestrator:
            return {
                "success": False,
                "error": "Service Unavailable",
                "message": "Insights orchestrator not available"
            }
        
        # Call Business Enablement orchestrator (domain capability)
        result = await self.insights_orchestrator.analyze_content(
            content_metadata_ids=content_metadata_ids,
            analysis_type=analysis_type,
            user_id=user_id
        )
        
        self.logger.info(f"✅ Content analyzed for insights: {len(content_metadata_ids)} files")
        
        # Transform for frontend (REST layer)
        return await self.transform_for_frontend(result)
        
    except Exception as e:
        self.logger.error(f"❌ Analyze content for insights failed: {e}")
        return {
            "success": False,
            "error": "Analysis Failed",
            "message": str(e)
        }

async def handle_query_insights_analysis_request(
    self,
    query: str,
    analysis_id: str,
    query_type: str = "auto"
) -> Dict[str, Any]:
    """
    Handle query analysis request (Frontend API → InsightsOrchestrator).
    Semantic API: NLP query on analysis results.
    """
    try:
        if not self.insights_orchestrator:
            return {
                "success": False,
                "error": "Service Unavailable",
                "message": "Insights orchestrator not available"
            }
        
        # Call orchestrator
        result = await self.insights_orchestrator.query_analysis_results(
            query=query,
            analysis_id=analysis_id,
            query_type=query_type
        )
        
        self.logger.info(f"✅ Analysis queried: {query} on {analysis_id}")
        
        return await self.transform_for_frontend(result)
        
    except Exception as e:
        self.logger.error(f"❌ Query insights analysis failed: {e}")
        return {
            "success": False,
            "error": "Query Failed",
            "message": str(e)
        }

async def handle_get_available_content_metadata_request(
    self,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle get available content metadata request.
    Semantic API: List content available for analysis.
    """
    try:
        if not self.insights_orchestrator:
            return {
                "success": False,
                "error": "Service Unavailable",
                "message": "Insights orchestrator not available"
            }
        
        result = await self.insights_orchestrator.get_available_content_metadata(
            user_id=user_id
        )
        
        self.logger.info(f"✅ Available content metadata retrieved")
        
        return await self.transform_for_frontend(result)
        
    except Exception as e:
        self.logger.error(f"❌ Get available content metadata failed: {e}")
        return {
            "success": False,
            "error": "Retrieval Failed",
            "message": str(e)
        }

async def handle_validate_content_metadata_for_insights_request(
    self,
    content_metadata_ids: List[str]
) -> Dict[str, Any]:
    """
    Handle validate content metadata request.
    Semantic API: Validate content metadata for insights analysis.
    """
    try:
        if not self.insights_orchestrator:
            return {
                "success": False,
                "error": "Service Unavailable",
                "message": "Insights orchestrator not available"
            }
        
        result = await self.insights_orchestrator.validate_content_metadata(
            content_metadata_ids=content_metadata_ids
        )
        
        self.logger.info(f"✅ Content metadata validated: {len(content_metadata_ids)} items")
        
        return await self.transform_for_frontend(result)
        
    except Exception as e:
        self.logger.error(f"❌ Validate content metadata failed: {e}")
        return {
            "success": False,
            "error": "Validation Failed",
            "message": str(e)
        }

async def handle_get_insights_analysis_results_request(
    self,
    analysis_id: str
) -> Dict[str, Any]:
    """
    Handle get analysis results request.
    Semantic API: Get complete analysis results.
    """
    try:
        if not self.insights_orchestrator:
            return {
                "success": False,
                "error": "Service Unavailable",
                "message": "Insights orchestrator not available"
            }
        
        result = await self.insights_orchestrator.get_analysis_results(
            analysis_id=analysis_id
        )
        
        self.logger.info(f"✅ Analysis results retrieved: {analysis_id}")
        
        return await self.transform_for_frontend(result)
        
    except Exception as e:
        self.logger.error(f"❌ Get analysis results failed: {e}")
        return {
            "success": False,
            "error": "Retrieval Failed",
            "message": str(e)
        }

async def handle_get_insights_analysis_visualizations_request(
    self,
    analysis_id: str
) -> Dict[str, Any]:
    """
    Handle get analysis visualizations request.
    Semantic API: Get visualizations for analysis.
    """
    try:
        if not self.insights_orchestrator:
            return {
                "success": False,
                "error": "Service Unavailable",
                "message": "Insights orchestrator not available"
            }
        
        result = await self.insights_orchestrator.get_analysis_visualizations(
            analysis_id=analysis_id
        )
        
        self.logger.info(f"✅ Analysis visualizations retrieved: {analysis_id}")
        
        return await self.transform_for_frontend(result)
        
    except Exception as e:
        self.logger.error(f"❌ Get analysis visualizations failed: {e}")
        return {
            "success": False,
            "error": "Retrieval Failed",
            "message": str(e)
        }

async def handle_list_user_insights_analyses_request(
    self,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle list user analyses request.
    Semantic API: List all analyses for user.
    """
    try:
        if not self.insights_orchestrator:
            return {
                "success": False,
                "error": "Service Unavailable",
                "message": "Insights orchestrator not available"
            }
        
        result = await self.insights_orchestrator.list_user_analyses(
            user_id=user_id
        )
        
        self.logger.info(f"✅ User analyses listed")
        
        return await self.transform_for_frontend(result)
        
    except Exception as e:
        self.logger.error(f"❌ List user analyses failed: {e}")
        return {
            "success": False,
            "error": "Listing Failed",
            "message": str(e)
        }

async def handle_get_insights_pillar_summary_request(
    self,
    analysis_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle get pillar summary request.
    Semantic API: Get Insights Pillar summary for Business Outcomes.
    """
    try:
        if not self.insights_orchestrator:
            return {
                "success": False,
                "error": "Service Unavailable",
                "message": "Insights orchestrator not available"
            }
        
        result = await self.insights_orchestrator.get_pillar_summary(
            analysis_id=analysis_id
        )
        
        self.logger.info(f"✅ Insights pillar summary retrieved")
        
        return await self.transform_for_frontend(result)
        
    except Exception as e:
        self.logger.error(f"❌ Get pillar summary failed: {e}")
        return {
            "success": False,
            "error": "Summary Failed",
            "message": str(e)
        }

async def handle_insights_pillar_health_check_request(self) -> Dict[str, Any]:
    """
    Handle insights pillar health check request.
    Semantic API: Check if Insights Pillar is available.
    """
    try:
        if not self.insights_orchestrator:
            return {
                "status": "unavailable",
                "pillar": "insights",
                "message": "Insights orchestrator not available",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Call orchestrator health check
        result = await self.insights_orchestrator.health_check()
        
        return {
            "status": "healthy",
            "pillar": "insights",
            "orchestrator_status": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        self.logger.error(f"❌ Insights health check failed: {e}")
        return {
            "status": "unhealthy",
            "pillar": "insights",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

**Update `_expose_frontend_apis()` method** (around line 154):

```python
async def _expose_frontend_apis(self):
    """Expose frontend APIs for discovered orchestrators."""
    # ... existing code ...
    
    # Register Insights Pillar semantic API endpoints
    if self.insights_orchestrator:
        await self.register_api_endpoint("/api/insights-pillar/analyze-content", 
                                        self.handle_analyze_content_for_insights_request)
        await self.register_api_endpoint("/api/insights-pillar/query-analysis", 
                                        self.handle_query_insights_analysis_request)
        await self.register_api_endpoint("/api/insights-pillar/get-available-content-metadata", 
                                        self.handle_get_available_content_metadata_request)
        await self.register_api_endpoint("/api/insights-pillar/validate-content-metadata", 
                                        self.handle_validate_content_metadata_for_insights_request)
        await self.register_api_endpoint("/api/insights-pillar/get-analysis-results", 
                                        self.handle_get_insights_analysis_results_request)
        await self.register_api_endpoint("/api/insights-pillar/get-analysis-visualizations", 
                                        self.handle_get_insights_analysis_visualizations_request)
        await self.register_api_endpoint("/api/insights-pillar/list-user-analyses", 
                                        self.handle_list_user_insights_analyses_request)
        await self.register_api_endpoint("/api/insights-pillar/pillar-summary", 
                                        self.handle_get_insights_pillar_summary_request)
        await self.register_api_endpoint("/api/insights-pillar/health", 
                                        self.handle_insights_pillar_health_check_request)
```

### Step 2: Update insights_pillar_router.py (30 min)

**File**: `backend/experience/api/semantic/insights_pillar_router.py`

**Add gateway accessor at top** (after imports):

```python
# ========================================================================
# FRONTEND GATEWAY SERVICE ACCESSOR
# ========================================================================

_frontend_gateway = None

def set_frontend_gateway(gateway):
    """Set Frontend Gateway Service reference."""
    global _frontend_gateway
    _frontend_gateway = gateway
    logger.info("✅ Insights router connected to Frontend Gateway Service")

def get_frontend_gateway():
    """Get Frontend Gateway Service."""
    if not _frontend_gateway:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Frontend Gateway Service not initialized"
        )
    return _frontend_gateway
```

**Update all endpoints** to call gateway:

```python
@router.post("/analyze-content")
async def analyze_content(
    request: AnalyzeContentRequest,
    user_id: Optional[str] = Header(None, alias="X-User-ID"),
    session_token: Optional[str] = Header(None, alias="X-Session-Token")
):
    """
    Semantic API: Analyze content for insights.
    ✅ Routes through FrontendGatewayService
    """
    try:
        logger.info(f"📊 Semantic analyze-content: {len(request.content_metadata_ids)} files")
        
        # Get Frontend Gateway Service (Frontend Enabler layer)
        frontend_gateway = get_frontend_gateway()
        
        # Call gateway handler (which calls orchestrator & transforms)
        result = await frontend_gateway.handle_analyze_content_for_insights_request(
            content_metadata_ids=request.content_metadata_ids,
            analysis_type=request.analysis_type,
            user_id=user_id or request.user_id
        )
        
        if result.get("success"):
            logger.info(f"✅ Analysis complete: {result.get('analysis_id')}")
        else:
            logger.error(f"❌ Analysis failed: {result.get('error')}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ /analyze-content endpoint failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Similar updates for all 9 endpoints...
```

### Step 3: Wire FrontendGatewayService to Router (5 min)

**File**: `backend/experience/api/main_api.py`

After initializing routers, set gateway reference:

```python
# Import gateway setter
from backend.experience.api.semantic.insights_pillar_router import set_frontend_gateway

# Get FrontendGatewayService from DI container
frontend_gateway = di_container.get_service("FrontendGatewayService")

# Connect to router
set_frontend_gateway(frontend_gateway)
```

### Step 4: Test (25 min)

1. **Unit Test**: FrontendGatewayService handlers
2. **Integration Test**: Router → Gateway → Orchestrator
3. **E2E Test**: Frontend → Backend → Response

---

## 📊 Validation Checklist

- [ ] All 9 handlers added to FrontendGatewayService
- [ ] All 9 endpoints updated in insights_pillar_router
- [ ] Gateway reference wired to router
- [ ] All endpoints call gateway, not orchestrator directly
- [ ] Responses transformed via `transform_for_frontend()`
- [ ] Error handling consistent
- [ ] Logging at each layer
- [ ] End-to-end test passes

---

## 🎯 Success Criteria

### Before (Wrong):
```
Frontend → Router → Orchestrator → Services
```

### After (Correct):
```
Frontend → Router → FrontendGatewayService → Orchestrator → Services
                    (REST translation)      (capabilities) (SOA APIs)
```

### Validation:
- [ ] No direct orchestrator calls in router
- [ ] All calls go through FrontendGatewayService
- [ ] Responses are transformed
- [ ] Same functionality as before
- [ ] Better architecture, easier to maintain

---

## 📁 Files Modified

1. `backend/experience/services/frontend_gateway_service/frontend_gateway_service.py` (+300 lines)
2. `backend/experience/api/semantic/insights_pillar_router.py` (~50 lines modified)
3. `backend/experience/api/main_api.py` (+5 lines)

**Total**: ~355 lines changed across 3 files

---

## 🚀 Next: Content Pillar

Once Insights is complete and tested, we'll use it as a reference to implement the same pattern for Content Pillar.

Content will be easier because:
- We'll have a proven pattern to follow
- Fewer endpoints (5 vs 9)
- Fixes URL mismatch at the same time



