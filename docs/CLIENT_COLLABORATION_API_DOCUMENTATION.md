# Client Collaboration API Documentation

**Version:** 1.0.0  
**Base URL:** `/api/v1/client-collaboration`  
**Status:** ✅ **IMPLEMENTED**

---

## 🎯 Overview

The Client Collaboration API enables clients to review, comment on, and approve artifacts created during MVP engagements. This API bridges MVP artifacts with client review/approval workflows.

**Authentication:** All endpoints require authentication via ForwardAuth (JWT token in Authorization header)

---

## 📋 API Endpoints

### **1. Share Artifact with Client**

Share an artifact with a client for review (updates status: draft → review).

**Endpoint:** `POST /api/v1/client-collaboration/share-artifact`

**Request Body:**
```json
{
  "artifact_id": "artifact_123",
  "artifact_type": "solution",
  "client_id": "client_456"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "artifact_id": "artifact_123",
  "artifact_type": "solution",
  "client_id": "client_456",
  "status": "review",
  "shared_at": "2024-12-16T21:30:00Z",
  "message": "Artifact shared successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request or artifact/client_id mismatch
- `503 Service Unavailable` - ClientCollaborationService not available

---

### **2. Get Client Artifacts**

Get all artifacts for a client (with optional filters).

**Endpoint:** `GET /api/v1/client-collaboration/client/{client_id}/artifacts`

**Query Parameters:**
- `artifact_type` (optional) - Filter by type: "solution" or "journey"
- `status` (optional) - Filter by status: "draft", "review", "approved", etc.

**Example:**
```
GET /api/v1/client-collaboration/client/client_456/artifacts?artifact_type=solution&status=review
```

**Response (200 OK):**
```json
{
  "success": true,
  "client_id": "client_456",
  "artifacts": {
    "artifact_123": {
      "artifact_id": "artifact_123",
      "artifact_type": "solution",
      "status": "review",
      "data": {...}
    }
  },
  "count": 1,
  "filters": {
    "artifact_type": "solution",
    "status": "review"
  },
  "message": "Artifacts retrieved successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request
- `503 Service Unavailable` - ClientCollaborationService not available

---

### **3. Add Client Comment**

Add a comment to an artifact.

**Endpoint:** `POST /api/v1/client-collaboration/artifacts/{artifact_id}/comments`

**Request Body:**
```json
{
  "comment": "This looks good, but we need to adjust Phase 2 timeline",
  "section": "phase_2",
  "user": "client_user",
  "artifact_type": "solution",
  "client_id": "client_456"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "artifact_id": "artifact_123",
  "comment": {
    "comment_id": "comment_789",
    "comment": "This looks good, but we need to adjust Phase 2 timeline",
    "section": "phase_2",
    "user": "client_user",
    "timestamp": "2024-12-16T21:35:00Z",
    "client_id": "client_456"
  },
  "total_comments": 1,
  "message": "Comment added successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request or artifact/client_id mismatch
- `503 Service Unavailable` - ClientCollaborationService not available

---

### **4. Approve Artifact**

Client approves an artifact (updates status: review → approved).

**Endpoint:** `POST /api/v1/client-collaboration/artifacts/{artifact_id}/approve`

**Request Body:**
```json
{
  "client_id": "client_456",
  "artifact_type": "solution"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "artifact_id": "artifact_123",
  "artifact_type": "solution",
  "client_id": "client_456",
  "status": "approved",
  "approved_at": "2024-12-16T21:40:00Z",
  "message": "Artifact approved successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request, wrong status, or artifact/client_id mismatch
- `503 Service Unavailable` - ClientCollaborationService not available

---

### **5. Reject Artifact**

Client rejects an artifact (updates status: review → draft, adds rejection comment).

**Endpoint:** `POST /api/v1/client-collaboration/artifacts/{artifact_id}/reject`

**Request Body:**
```json
{
  "client_id": "client_456",
  "rejection_reason": "Timeline is too aggressive, need more time for Phase 2",
  "artifact_type": "solution"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "artifact_id": "artifact_123",
  "artifact_type": "solution",
  "client_id": "client_456",
  "status": "draft",
  "rejection_reason": "Timeline is too aggressive, need more time for Phase 2",
  "rejected_at": "2024-12-16T21:45:00Z",
  "message": "Artifact rejected successfully"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid request, wrong status, or artifact/client_id mismatch
- `503 Service Unavailable` - ClientCollaborationService not available

---

### **6. Health Check**

Check health status of Client Collaboration API.

**Endpoint:** `GET /api/v1/client-collaboration/health`

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service_name": "ClientCollaborationService",
  "realm": "business_enablement",
  "solution_composer_available": true,
  "journey_orchestrator_available": true,
  "curator_available": true
}
```

---

## 🔐 Authentication

All endpoints require authentication via ForwardAuth:

**Header:**
```
Authorization: Bearer <jwt_token>
```

**User Context Headers (set by ForwardAuth):**
- `X-User-Id` - User ID
- `X-Tenant-Id` - Tenant ID
- `X-User-Email` - User email
- `X-User-Roles` - Comma-separated roles
- `X-User-Permissions` - Comma-separated permissions

---

## 📊 Status Lifecycle

**Artifact Status Flow:**
```
draft → review → approved → implemented → active
  ↓       ↓
rejected  cancelled
```

**Status Transitions:**
- `share_artifact_with_client`: draft → review
- `approve_artifact`: review → approved
- `reject_artifact`: review → draft

---

## 🎯 Use Cases

### **Use Case 1: Platform Team Shares Artifact**
```bash
POST /api/v1/client-collaboration/share-artifact
{
  "artifact_id": "roadmap_123",
  "artifact_type": "solution",
  "client_id": "insurance_client_1"
}
```

### **Use Case 2: Client Views Artifacts**
```bash
GET /api/v1/client-collaboration/client/insurance_client_1/artifacts?status=review
```

### **Use Case 3: Client Adds Comment**
```bash
POST /api/v1/client-collaboration/artifacts/roadmap_123/comments
{
  "comment": "Phase 2 timeline needs adjustment",
  "section": "phase_2",
  "artifact_type": "solution",
  "client_id": "insurance_client_1"
}
```

### **Use Case 4: Client Approves Artifact**
```bash
POST /api/v1/client-collaboration/artifacts/roadmap_123/approve
{
  "client_id": "insurance_client_1",
  "artifact_type": "solution"
}
```

---

## 🔄 Complete Workflow Example

**1. Platform team creates artifact (draft)**
```bash
# Via SolutionComposerService.create_solution_artifact()
# Status: "draft"
```

**2. Platform team shares with client**
```bash
POST /api/v1/client-collaboration/share-artifact
# Status: "review"
```

**3. Client views artifacts**
```bash
GET /api/v1/client-collaboration/client/{client_id}/artifacts?status=review
```

**4. Client adds comments**
```bash
POST /api/v1/client-collaboration/artifacts/{artifact_id}/comments
```

**5. Client approves**
```bash
POST /api/v1/client-collaboration/artifacts/{artifact_id}/approve
# Status: "approved"
```

**6. Artifact becomes operational solution (Week 5)**
```bash
# Via SolutionComposerService.create_solution_from_artifact()
# Status: "implemented" → "active"
```

---

## 📝 Notes

- All endpoints support both Solution and Journey artifacts
- Client ID validation ensures artifacts can only be accessed by their owning client
- Status transitions are validated (invalid transitions return 400)
- Comments are stored with artifacts and tracked with metadata
- All operations are auditable and tracked via telemetry

---

**Last Updated:** December 16, 2024  
**Status:** ✅ **API ENDPOINTS IMPLEMENTED**









