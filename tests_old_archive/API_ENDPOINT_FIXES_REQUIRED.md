# API Endpoint Fixes Required - Frontend Updates

**Date:** December 2024  
**Principle:** Backend is source of truth - frontend should adapt to backend architecture  
**Total Fixes:** 15 method calls across 5 API managers

---

## 🎯 Quick Summary

**Status:** ✅ Comparison complete - **GAP ANALYSIS COMPLETE**  
**Action Required:** 
- **Frontend:** 1 method needs update (Insights)
- **Backend:** 11 handlers need to be added to FrontendGatewayService
- **Then Frontend:** 11 more methods need updates after backend work

**Estimated Time:** 
- Frontend fix: ~5 minutes
- Backend work: ~2-3 hours (add handlers)
- Frontend updates after backend: ~30 minutes

**⚠️ IMPORTANT:** Most gaps are **functional gaps** (missing backend handlers), not just naming mismatches!

---

## 📋 Fix List by Priority

### **Priority 1: Critical Path Mismatches** (Must Fix Before Testing)

#### **1. OperationsAPIManager.ts** - 6 methods ❌
**File:** `symphainy-frontend/shared/managers/OperationsAPIManager.ts`

**Issue:** Frontend uses `/api/v1/business_enablement/operations/*` but backend uses `/api/v1/operations-pillar/*`

**Fixes needed:**

1. **Line 150** - `createSOP()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/v1/business_enablement/operations/create-standard-operating-procedure`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/operations-pillar/create-standard-operating-procedure`, {
   ```

2. **Line 188** - `listSOPs()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/v1/business_enablement/operations/list-standard-operating-procedures`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/operations-pillar/list-standard-operating-procedures`, {
   ```

3. **Line 214** - `createWorkflow()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/v1/business_enablement/operations/create-workflow`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/operations-pillar/create-workflow`, {
   ```

4. **Line 252** - `listWorkflows()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/v1/business_enablement/operations/list-workflows`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/operations-pillar/list-workflows`, {
   ```

5. **Line 278** - `convertSOPToWorkflow()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/v1/business_enablement/operations/create-workflow`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/operations-pillar/convert-sop-to-workflow`, {
   ```

6. **Line 318** - `convertWorkflowToSOP()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/v1/business_enablement/operations/create-standard-operating-procedure`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/operations-pillar/convert-workflow-to-sop`, {
   ```

---

#### **2. SessionAPIManager.ts** - 3 methods ❌
**File:** `symphainy-frontend/shared/managers/SessionAPIManager.ts`

**Issue:** Frontend uses `/api/session/*` but backend uses `/api/v1/session/*`

**Fixes needed:**

1. **Line 62** - `createUserSession()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/session/create-user-session`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/session/create-user-session`, {
   ```

2. **Line 118** - `getSessionDetails()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/session/get-session-details/${sessionId}`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/session/get-session-details/${sessionId}`, {
   ```

3. **Line 156** - `getSessionState()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/session/get-session-state/${sessionId}`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/session/get-session-state/${sessionId}`, {
   ```

---

#### **3. GuideAgentAPIManager.ts** - 3 methods ❌
**File:** `symphainy-frontend/shared/managers/GuideAgentAPIManager.ts`

**Issue:** Frontend uses `/api/v1/journey/guide-agent/*` but backend uses `/api/v1/guide-agent/*`

**Fixes needed:**

1. **Line 71** - `analyzeUserIntent()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/v1/journey/guide-agent/analyze-user-intent`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/guide-agent/analyze-user-intent`, {
   ```

2. **Line 117** - `getJourneyGuidance()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/v1/journey/guide-agent/get-journey-guidance`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/guide-agent/get-journey-guidance`, {
   ```

3. **Line 163** - `getConversationHistory()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/v1/journey/guide-agent/get-conversation-history/${sessionId}`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/guide-agent/get-conversation-history/${sessionId}`, {
   ```

---

#### **4. LiaisonAgentsAPIManager.ts** - 2 methods ❌
**File:** `symphainy-frontend/shared/managers/LiaisonAgentsAPIManager.ts`

**Issue:** Frontend uses `/api/liaison-agents/*` (no v1) but backend uses `/api/v1/liaison-agents/*`

**Fixes needed:**

1. **Line 59** - `sendMessageToPillarAgent()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/liaison-agents/send-message-to-pillar-agent`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/liaison-agents/send-message-to-pillar-agent`, {
   ```

2. **Line 108** - `getPillarConversationHistory()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/liaison-agents/get-pillar-conversation-history/${sessionId}/${pillar}`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/liaison-agents/get-pillar-conversation-history/${sessionId}/${pillar}`, {
   ```

---

#### **5. InsightsAPIManager.ts** - 1 method ❌
**File:** `symphainy-frontend/shared/managers/InsightsAPIManager.ts`

**Issue:** Frontend uses `/api/v1/insights-pillar/analyze-content-for-insights` but backend uses `/api/v1/insights-pillar/analyze-content`

**Fix needed:**

1. **Line 67** - `analyzeContentForInsights()`:
   ```typescript
   // OLD:
   const response = await fetch(`${this.baseURL}/api/v1/insights-pillar/analyze-content-for-insights`, {
   
   // NEW:
   const response = await fetch(`${this.baseURL}/api/v1/insights-pillar/analyze-content`, {
   ```

---

## 📊 Summary

| API Manager | Methods to Fix | Priority |
|-------------|----------------|----------|
| OperationsAPIManager.ts | 6 | 🔴 Critical |
| SessionAPIManager.ts | 3 | 🔴 Critical |
| GuideAgentAPIManager.ts | 3 | 🔴 Critical |
| LiaisonAgentsAPIManager.ts | 2 | 🔴 Critical |
| InsightsAPIManager.ts | 1 | 🔴 Critical |

**Total:** 15 method calls need updates

---

## ✅ What's Already Correct

- ✅ Content Pillar - All endpoints match perfectly
- ✅ Business Outcomes Pillar - All endpoints match perfectly
- ✅ Insights Pillar - Analysis results and visualizations match perfectly

---

**Last Updated:** December 2024

