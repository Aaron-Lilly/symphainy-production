# 🏗️ API Mapping Strategy - New Architecture

**Date:** November 7, 2024  
**Challenge:** Old API layer was built for direct pillar access. New architecture uses manager hierarchy + MVP Journey Orchestrator.  
**Solution:** Redesign API routing to match current architectural flow.

---

## 🎯 OLD vs NEW ARCHITECTURE

### **OLD (When API Was Built):**
```
Frontend → /api/content/upload
    ↓
Content Pillar Service.upload_file()
    ↓
Direct file processing logic
```

**Simple, direct mapping. No orchestration.**

### **NEW (Current Architecture):**
```
Frontend → /api/mvp/content/upload
    ↓
Experience Manager (FrontendGatewayService)
    ↓
MVP Journey Orchestrator
    ↓ (composes)
Session Journey Orchestrator
    ↓
Delivery Manager (Business Enablement)
    ↓
Business Orchestrator
    ↓
Specialist Agents + Enabling Services
```

**Hierarchical orchestration. MVP is ONE journey pattern.**

---

## 🔑 KEY ARCHITECTURAL INSIGHTS

### **1. MVP is a Journey, Not Direct Pillar Access**

The MVP Journey Orchestrator (`MVPJourneyOrchestratorService`) is specifically designed for the 4-pillar navigation:
- Content Pillar
- Insights Pillar
- Operations Pillar  
- Business Outcomes Pillar

**It composes:** `SessionJourneyOrchestratorService` for free navigation
**It provides:** MVP-specific pillar configurations and completion criteria

### **2. Entry Point: Experience Manager**

`FrontendGatewayService` is the proper entry point:
- Routes frontend requests
- Manages user context
- Delegates to appropriate orchestrators
- Returns responses formatted for frontend

### **3. Manager Hierarchy Bootstraps Journey**

```
City Manager
  ↓
Solution Manager (solution context)
  ↓
Journey Manager (MVP Journey Orchestrator)
  ↓
Experience Manager (Frontend Gateway)
  ↓
Delivery Manager (Business Orchestrator)
```

---

## 🎯 PROPER API ROUTING STRATEGY

### **Option A: Journey-First (Recommended)**

Route ALL MVP requests through the MVP Journey Orchestrator:

```python
# Frontend calls
POST /api/mvp/pillar/content/upload
POST /api/mvp/pillar/insights/analyze
POST /api/mvp/pillar/operations/sop
POST /api/mvp/pillar/business-outcomes/roadmap

# API Layer
class MVPAPIRouter:
    async def handle_request(self, pillar, action, data):
        # 1. Get MVP Journey Orchestrator from Journey Manager
        mvp_orchestrator = journey_manager.get_mvp_journey_orchestrator()
        
        # 2. Navigate to pillar
        await mvp_orchestrator.navigate_to_pillar(pillar, user_context)
        
        # 3. Execute pillar action
        result = await mvp_orchestrator.execute_pillar_action(
            pillar=pillar,
            action=action,
            action_data=data
        )
        
        # 4. Update progress
        await mvp_orchestrator.update_pillar_progress(pillar, progress)
        
        return result
```

**Benefits:**
- ✅ Respects architectural hierarchy
- ✅ Journey orchestration built-in
- ✅ Progress tracking automatic
- ✅ Navigation history preserved
- ✅ Completion criteria enforced

**Drawbacks:**
- Need to implement pillar action routing in MVP Journey Orchestrator
- More layers to traverse

---

### **Option B: Direct Orchestrator Access (Faster MVP)**

Route directly to Business Orchestrator for execution, use Experience Manager for context:

```python
# Frontend calls (simpler)
POST /api/content/upload
POST /api/insights/analyze
POST /api/operations/sop
POST /api/business-outcomes/roadmap

# API Layer
class SimplifiedAPIRouter:
    async def handle_content_upload(self, file_data, user_context):
        # 1. Get Experience Manager (manages user context)
        experience_mgr = city_manager.get_experience_manager()
        
        # 2. Create/get session
        session = await experience_mgr.session_manager.get_or_create_session(user_context)
        
        # 3. Get Delivery Manager (Business Enablement)
        delivery_mgr = city_manager.get_delivery_manager()
        
        # 4. Execute business logic via orchestrator
        result = await delivery_mgr.business_orchestrator.handle_content_upload(
            file_data=file_data,
            user_context=user_context,
            session=session
        )
        
        # 5. Update session state
        await experience_mgr.session_manager.update_session_state(session.id, result)
        
        return result
```

**Benefits:**
- ✅ Simpler implementation
- ✅ Fewer layers
- ✅ Faster to market
- ✅ Still uses proper services

**Drawbacks:**
- Doesn't leverage MVP Journey Orchestrator
- Manual progress tracking
- No automatic journey orchestration

---

### **Option C: Hybrid (Best of Both)**

Use Journey Orchestrator for navigation/progress, direct orchestrator for execution:

```python
# Frontend calls
POST /api/mvp/content/upload
POST /api/mvp/insights/analyze

# API Layer
class HybridAPIRouter:
    async def handle_content_upload(self, file_data, user_context):
        # 1. Get MVP Journey Orchestrator (for tracking/navigation)
        mvp_journey = journey_manager.get_mvp_journey_orchestrator()
        
        # 2. Navigate to content pillar (updates journey state)
        await mvp_journey.navigate_to_pillar("content", user_context)
        
        # 3. Get Delivery Manager for execution
        delivery_mgr = city_manager.get_delivery_manager()
        
        # 4. Execute via Business Orchestrator
        result = await delivery_mgr.business_orchestrator.handle_content_upload(
            file_data=file_data,
            user_context=user_context
        )
        
        # 5. Update pillar progress
        await mvp_journey.update_pillar_progress("content", {
            "files_uploaded": True,
            "last_action": "upload",
            "result": result
        })
        
        return result
```

**Benefits:**
- ✅ Journey tracking automatic
- ✅ Direct execution (fast)
- ✅ Best of both worlds
- ✅ Respects architecture

---

## 🎯 RECOMMENDED APPROACH: Option C (Hybrid)

### **Why Hybrid:**
1. **Respects Architecture:** Uses manager hierarchy properly
2. **Journey Tracking:** MVP Journey Orchestrator tracks progress
3. **Performance:** Direct execution, no unnecessary layers
4. **Flexibility:** Can add full journey orchestration later

### **Implementation Steps:**

#### **1. API Router Structure**
```
backend/experience/api/
├── __init__.py
├── mvp_router.py           # NEW - MVP-specific routes
├── auth_router.py          # NEW - Auth/session endpoints
└── base_router.py          # NEW - Base router class
```

#### **2. MVP Router (Example)**
```python
from fastapi import APIRouter, HTTPException, UploadFile
from typing import Dict, Any

router = APIRouter(prefix="/api/mvp", tags=["MVP"])

@router.post("/content/upload")
async def upload_file(file: UploadFile, user_id: str):
    """Upload file for content pillar."""
    # 1. Get managers from platform orchestrator
    city_manager = get_city_manager()
    journey_manager = city_manager.get_journey_manager()
    delivery_manager = city_manager.get_delivery_manager()
    
    # 2. Navigate to content pillar (journey tracking)
    mvp_journey = journey_manager.mvp_journey_orchestrator
    await mvp_journey.navigate_to_pillar("content", {"user_id": user_id})
    
    # 3. Execute upload via Business Orchestrator
    result = await delivery_manager.business_orchestrator.upload_and_parse_file(
        file_data=await file.read(),
        filename=file.filename,
        user_id=user_id
    )
    
    # 4. Update progress
    await mvp_journey.update_pillar_progress("content", {
        "files_uploaded": True,
        "file_id": result.get("file_id")
    })
    
    return result

@router.post("/insights/analyze")
async def analyze_data(file_ids: list[str], user_id: str):
    """Analyze data for insights pillar."""
    # Similar pattern...
    pass
```

#### **3. Auth Router**
```python
router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
async def register(name: str, email: str, password: str):
    """Register new user."""
    # Use Security Guard via City Manager
    city_manager = get_city_manager()
    security_guard = city_manager.get_smart_city_service("SecurityGuard")
    
    result = await security_guard.register_user({
        "name": name,
        "email": email,
        "password": password
    })
    
    return result

@router.post("/login")
async def login(email: str, password: str):
    """Login user."""
    # Similar to register...
    pass
```

#### **4. Session Router**
```python
router = APIRouter(prefix="/api/global", tags=["session"])

@router.post("/session")
async def create_session(user_id: str):
    """Create global session."""
    # Use Traffic Cop via City Manager
    city_manager = get_city_manager()
    traffic_cop = city_manager.get_smart_city_service("TrafficCop")
    
    session = await traffic_cop.create_session({
        "user_id": user_id,
        "session_type": "mvp"
    })
    
    return session
```

---

## 📊 SERVICE ACCESS PATTERN

### **Getting Services from Platform Orchestrator:**

```python
# In main.py, make platform_orchestrator globally accessible
_platform_orchestrator = None

def set_platform_orchestrator(orchestrator):
    global _platform_orchestrator
    _platform_orchestrator = orchestrator

def get_platform_orchestrator():
    if not _platform_orchestrator:
        raise RuntimeError("Platform not initialized")
    return _platform_orchestrator

# In routers
def get_city_manager():
    return get_platform_orchestrator().managers["city_manager"]

def get_journey_manager():
    city_mgr = get_city_manager()
    return city_mgr.manager_hierarchy["journey_manager"]["instance"]

def get_delivery_manager():
    city_mgr = get_city_manager()
    return city_mgr.manager_hierarchy["delivery_manager"]["instance"]
```

---

## 🚀 IMPLEMENTATION TIMELINE

| Task | Time | Priority |
|------|------|----------|
| 1. Create router structure | 10 min | High |
| 2. Implement auth router | 15 min | Critical |
| 3. Implement session router | 10 min | Critical |
| 4. Implement content pillar router | 20 min | High |
| 5. Implement insights pillar router | 15 min | Medium |
| 6. Implement operations pillar router | 15 min | Medium |
| 7. Implement business outcomes router | 15 min | Medium |
| 8. Wire into main.py | 15 min | Critical |
| 9. Test & validate | 30 min | Critical |
| **TOTAL** | **2.5 hours** | |

---

## ✅ SUCCESS CRITERIA

After implementation:
1. ✅ `/api/auth/register` → 200 (creates user via Security Guard)
2. ✅ `/api/global/session` → 200 (creates session via Traffic Cop)
3. ✅ `/api/mvp/content/upload` → 200 (uploads file + tracks journey)
4. ✅ `/api/mvp/insights/analyze` → 200 (analyzes data + tracks journey)
5. ✅ Frontend can create accounts
6. ✅ Frontend can upload files
7. ✅ Full MVP flow works end-to-end

---

## 🎯 RECOMMENDATION

**Use Option C (Hybrid)** with the following priority:

**Phase 1 (30 min):** Auth + Session
- Get users past login screen
- Basic functionality working

**Phase 2 (1 hour):** Content Pillar
- File upload working
- Core MVP flow enabled

**Phase 3 (1 hour):** Remaining Pillars
- Full MVP operational
- Ready for CTO demo

**Total:** 2.5 hours to production-ready MVP API! 🚀


