# 🗺️ Journey Orchestrator Patterns

**Date:** November 4, 2024  
**Purpose:** Explain the three journey orchestrator patterns and when to use each

---

## 🎯 FOUR ORCHESTRATOR PATTERNS

We now have **FOUR distinct journey orchestrator patterns** to support different navigation styles and transaction requirements:

1. **Structured Journey Orchestrator** - Linear, guided flows
2. **Session Journey Orchestrator** - Free-form, user-driven navigation
3. **MVP Journey Orchestrator** - MVP-specific implementation (composes Session Journey Orchestrator)
4. **Saga Journey Orchestrator** - Saga-pattern with automatic compensation (composes Structured Journey Orchestrator)

---

## 📋 PATTERN 1: STRUCTURED JOURNEY ORCHESTRATOR

### **Use For:**
- ✅ Linear, guided workflows
- ✅ Enterprise migrations
- ✅ Onboarding processes
- ✅ Structured training flows
- ✅ Compliance workflows

### **Characteristics:**
- **Enforced progression:** Users must complete Step 1 before Step 2
- **Milestone-based:** Journey divided into sequential milestones
- **Template-driven:** Journey designed from templates
- **Branching support:** Milestones can have multiple `next_steps`

### **Example Use Case:**
```
Enterprise Content Migration Journey:
  Step 1: Upload Content → Step 2: Analyze Content → Step 3: Transform Data → Step 4: Validate Results

User MUST complete each step before moving to next.
```

### **API Pattern:**
```python
# Design journey from template
journey = await structured_orchestrator.design_journey(
    journey_type="content_migration",
    requirements={...}
)

# Execute journey (enforces order)
await structured_orchestrator.execute_journey(
    journey_id=journey["journey_id"],
    user_id="user_123",
    context={...}
)

# Advance to next step (only moves forward)
await structured_orchestrator.advance_journey_step(
    journey_id=journey["journey_id"],
    user_id="user_123",
    step_result={...}
)
```

---

## 📋 PATTERN 2: SESSION JOURNEY ORCHESTRATOR

### **Use For:**
- ✅ Free-form, user-driven navigation
- ✅ Exploratory solutions
- ✅ MVP websites (navbar navigation)
- ✅ Research/discovery workflows
- ✅ Non-linear user experiences

### **Characteristics:**
- **Free navigation:** Users can jump to any area at any time
- **Area-based:** Journey divided into independent areas/pillars
- **Context preservation:** Area state preserved when user leaves
- **Completion tracking:** Each area has its own completion criteria

### **Example Use Case:**
```
MVP Website Navigation:
  Areas: Content Pillar, Insights Pillar, Operations Pillar, Business Outcome Pillar

User can click any pillar at any time (navbar).
Progress in each pillar preserved independently.
```

### **API Pattern:**
```python
# Start session with defined areas
session = await session_orchestrator.start_session(
    user_id="user_123",
    session_config={
        "areas": [
            {"area_id": "content", "area_name": "Content Pillar", ...},
            {"area_id": "insights", "area_name": "Insights Pillar", ...},
            {"area_id": "operations", "area_name": "Operations Pillar", ...},
            {"area_id": "business_outcome", "area_name": "Business Outcome", ...}
        ],
        "initial_area": "content"
    }
)

# Navigate freely between areas (NO ENFORCEMENT!)
await session_orchestrator.navigate_to_area(
    session_id=session["session_id"],
    area_id="insights"  # Jump directly to Insights!
)

# Later, jump back to Content
await session_orchestrator.navigate_to_area(
    session_id=session["session_id"],
    area_id="content"  # Jump back!
)

# Update area progress
await session_orchestrator.update_area_state(
    session_id=session["session_id"],
    area_id="content",
    updates={"files_uploaded": True, "files_parsed": True}
)

# Check overall progress
progress = await session_orchestrator.get_session_progress(
    session_id=session["session_id"]
)
# Returns: {"completion_percent": 50, "completed_areas": 2, "visited_areas": 3}
```

---

## 📋 PATTERN 3: MVP JOURNEY ORCHESTRATOR

### **Use For:**
- ✅ **MVP-specific use case ONLY**
- ✅ 4-pillar navigation (Content, Insights, Operations, Business Outcome)
- ✅ Recommended flow with user freedom

### **Characteristics:**
- **Composes Session Journey Orchestrator:** Uses Session Orchestrator under the hood
- **MVP-specific configuration:** Pre-configured for 4 MVP pillars
- **Recommended flow:** Suggests Content → Insights → Operations → Business Outcome
- **User freedom preserved:** Users can still navigate freely
- **Pillar-specific APIs:** Simplified API for MVP use case

### **Example Use Case:**
```
MVP Website (Your Current MVP!):
  Content Pillar → Insights Pillar → Operations Pillar → Business Outcome Pillar

Recommended flow, but users can click any pillar at any time via navbar.
```

### **API Pattern:**
```python
# Start MVP journey (automatically configures 4 pillars)
mvp_journey = await mvp_orchestrator.start_mvp_journey(
    user_id="user_123",
    initial_pillar="content"  # Recommended starting point
)

# Navigate to any pillar (FREE NAVIGATION!)
await mvp_orchestrator.navigate_to_pillar(
    session_id=mvp_journey["session"]["session_id"],
    pillar_id="insights"  # User clicked Insights in navbar
)

# Update pillar progress
await mvp_orchestrator.update_pillar_progress(
    session_id=mvp_journey["session"]["session_id"],
    pillar_id="content",
    progress_updates={
        "files_uploaded": True,
        "files_parsed": True
    }
)

# Get recommended next pillar (Guide Agent can suggest)
recommendation = await mvp_orchestrator.get_recommended_next_pillar(
    session_id=mvp_journey["session"]["session_id"]
)
# Returns: {"recommended_pillar": "insights", "pillar_info": {...}}

# Check MVP completion
completion = await mvp_orchestrator.check_mvp_completion(
    session_id=mvp_journey["session"]["session_id"]
)
# Returns: {"mvp_complete": False, "pillar_status": {...}}
```

---

## 🎨 COMPOSITION RELATIONSHIPS

```
Structured Journey Orchestrator
  ↓ (independent, doesn't compose anything Journey-specific)
  Uses: Experience services directly


Session Journey Orchestrator
  ↓ (independent, general-purpose)
  Uses: Experience services directly


MVP Journey Orchestrator
  ↓ COMPOSES
Session Journey Orchestrator
  ↓ Uses
Experience services


Saga Journey Orchestrator
  ↓ COMPOSES
Structured Journey Orchestrator
  ↓ Uses
Experience services + Milestone Tracker
```

**Key Points:**
- MVP Journey Orchestrator is a **specialized wrapper** around Session Journey Orchestrator
- Saga Journey Orchestrator is a **specialized wrapper** around Structured Journey Orchestrator

---

## 📊 DECISION TREE: WHICH ORCHESTRATOR TO USE?

### **Question 1: Do you need Saga guarantees (automatic compensation on failure)?**
- **YES** → Use **Saga Journey Orchestrator** ✅
  - Multi-service workflows requiring atomicity
  - Financial transactions, order processing
  - Enterprise migrations with rollback requirements
  - Any workflow where partial failures must be compensated
- **NO** → Go to Question 2

### **Question 2: Is this the MVP use case?**
- **YES** → Use **MVP Journey Orchestrator**
- **NO** → Go to Question 3

### **Question 3: Do users need to follow a specific order?**
- **YES** (enforced progression) → Use **Structured Journey Orchestrator**
- **NO** (free navigation) → Use **Session Journey Orchestrator**

### **Question 4: Do you need custom areas/pillars?**
- **YES** (not the 4 MVP pillars) → Use **Session Journey Orchestrator** (configure custom areas)
- **NO** (4 MVP pillars) → Use **MVP Journey Orchestrator**

---

## 🎯 ARCHITECTURAL BENEFITS

### **1. Flexibility**
Solutions can choose the navigation style that fits their use case:
- Enterprise migration? → Structured
- Research tool? → Session
- MVP website? → MVP

### **2. Composability**
MVP Journey Orchestrator **composes** Session Journey Orchestrator:
- Reuses general-purpose free navigation logic
- Adds MVP-specific configuration
- Maintains single source of truth for free navigation

### **3. Extensibility**
Future solutions can:
- Create their own orchestrators composing Session Journey Orchestrator
- Use Structured Journey Orchestrator for guided flows
- Mix and match based on needs

---

## 📋 MVP PILLAR CONFIGURATION

**Pre-configured in MVP Journey Orchestrator:**

### **Content Pillar:**
- **Actions:** upload_file, parse_file, preview_data, chat_with_content_liaison
- **Completion:** files_uploaded=True AND files_parsed=True

### **Insights Pillar:**
- **Actions:** select_file, analyze_data, create_visualization, generate_insights_summary, chat_with_insights_liaison
- **Completion:** file_selected=True AND analysis_complete=True AND insights_summary_generated=True

### **Operations Pillar:**
- **Actions:** select_files, generate_workflow, generate_sop, create_coexistence_blueprint, chat_with_operations_liaison
- **Completion:** workflow_generated=True AND sop_generated=True AND coexistence_blueprint_created=True

### **Business Outcome Pillar:**
- **Actions:** review_summaries, add_context, generate_roadmap, generate_poc_proposal, chat_with_experience_liaison
- **Completion:** summaries_reviewed=True AND roadmap_generated=True AND poc_proposal_generated=True

---

## 🚀 USAGE EXAMPLES

### **Example 1: MVP Website (Your Current Use Case)**
```python
# Frontend initialization
mvp_journey = await mvp_orchestrator.start_mvp_journey(
    user_id=current_user.id,
    initial_pillar="content"
)

# User clicks "Insights" in navbar
await mvp_orchestrator.navigate_to_pillar(
    session_id=session_id,
    pillar_id="insights"
)

# User uploads file in Content pillar
await mvp_orchestrator.update_pillar_progress(
    session_id=session_id,
    pillar_id="content",
    progress_updates={"files_uploaded": True}
)

# Guide Agent gets recommendation for user
next_pillar = await mvp_orchestrator.get_recommended_next_pillar(session_id)
guide_agent.suggest(f"Great! Ready to move to {next_pillar['pillar_info']['area_name']}?")
```

### **Example 2: Custom Exploratory Solution**
```python
# Research platform with custom areas
session = await session_orchestrator.start_session(
    user_id=current_user.id,
    session_config={
        "areas": [
            {"area_id": "data_exploration", "area_name": "Data Exploration", ...},
            {"area_id": "hypothesis_testing", "area_name": "Hypothesis Testing", ...},
            {"area_id": "visualization", "area_name": "Visualization", ...},
            {"area_id": "reporting", "area_name": "Reporting", ...}
        ],
        "initial_area": "data_exploration"
    }
)

# User navigates freely
await session_orchestrator.navigate_to_area(session_id, "visualization")
await session_orchestrator.navigate_to_area(session_id, "hypothesis_testing")
await session_orchestrator.navigate_to_area(session_id, "data_exploration")
```

### **Example 3: Enterprise Migration (Structured)**
```python
# Guided enterprise migration
journey = await structured_orchestrator.design_journey(
    journey_type="content_migration",
    requirements={"source": "legacy_system", "target": "new_system"}
)

# Execute journey (enforced order)
await structured_orchestrator.execute_journey(
    journey_id=journey["journey_id"],
    user_id=current_user.id,
    context={"migration_id": "mig_001"}
)

# User completes Step 1, automatically advances to Step 2
await structured_orchestrator.advance_journey_step(
    journey_id=journey["journey_id"],
    user_id=current_user.id,
    step_result={"status": "complete", "files_uploaded": 150}
)
```

---

## 📋 PATTERN 4: SAGA JOURNEY ORCHESTRATOR

### **Use For:**
- ✅ Multi-service workflows requiring atomicity guarantees
- ✅ Enterprise migrations with rollback requirements
- ✅ Financial transactions (payment processing, order fulfillment)
- ✅ Critical business processes where partial failures must be compensated
- ✅ Any workflow where partial completion is unacceptable

### **Characteristics:**
- **Saga Pattern**: Implements distributed transaction pattern with compensation
- **Automatic Compensation**: When a milestone fails, previous milestones are automatically rolled back in reverse order
- **Compensation Handlers**: Domain-specific undo operations for each milestone
- **Saga State Tracking**: Tracks execution state (in_progress, compensating, completed, failed)
- **Idempotency**: Compensation operations are safe to retry
- **Composes Structured**: Uses Structured Journey Orchestrator for milestone execution

### **Example Use Case:**
```
Enterprise Migration Saga:
  Step 1: Upload Content → Step 2: Analyze Content → Step 3: Transform Data → Step 4: Validate Results

If Step 3 fails after retries:
  - Automatically compensate Step 2: revert_analysis()
  - Automatically compensate Step 1: delete_uploaded_content()
  - Saga state: COMPENSATING → COMPLETED
```

### **API Pattern:**
```python
# Design Saga journey with compensation handlers
saga_journey = await saga_orchestrator.design_saga_journey(
    journey_type="enterprise_migration",
    requirements={...},
    compensation_handlers={
        "upload_content": "delete_uploaded_content",
        "analyze_content": "revert_analysis",
        "transform_data": "revert_transformation"
    }
)

# Execute Saga journey
execution = await saga_orchestrator.execute_saga_journey(
    journey_id=saga_journey["journey_id"],
    user_id="user_123",
    context={...}
)

# Advance Saga steps (automatic compensation on failure)
await saga_orchestrator.advance_saga_step(
    saga_id=execution["saga_id"],
    journey_id=saga_journey["journey_id"],
    user_id="user_123",
    step_result={...}
)

# Check Saga status
status = await saga_orchestrator.get_saga_status(saga_id)
```

### **When to Use Saga:**
- ✅ Multi-service workflows spanning multiple realms
- ✅ Operations requiring atomicity (all-or-nothing)
- ✅ Financial transactions or order processing
- ✅ Enterprise migrations with rollback requirements
- ✅ Critical business processes with compliance requirements

### **When NOT to Use Saga:**
- ❌ Simple single-service operations
- ❌ Free-form navigation (use Session/MVP instead)
- ❌ No compensation needed (use Structured instead)
- ❌ Read-only operations

**See [Saga Journey Orchestrator Documentation](./docs/SAGA_JOURNEY_ORCHESTRATOR.md) for complete guide.**

---

## 🎉 BOTTOM LINE

**You now have FOUR orchestrator patterns to support ANY navigation style and transaction requirement:**

1. **Structured Journey Orchestrator** → Linear, guided flows (enterprise migrations)
2. **Session Journey Orchestrator** → Free-form navigation (exploratory, research)
3. **MVP Journey Orchestrator** → MVP-specific (your 4-pillar website)
4. **Saga Journey Orchestrator** → Saga-pattern with automatic compensation (multi-service atomicity)

**Key Architectural Wins:**
- MVP Journey Orchestrator **composes** Session Journey Orchestrator
- Saga Journey Orchestrator **composes** Structured Journey Orchestrator
- Solutions can choose the pattern that fits their use case
- All four patterns work with the same Journey Analytics and Milestone Tracker
- Extensible: Future solutions can create their own orchestrators

**For your MVP:** Use **MVP Journey Orchestrator** exclusively! It handles the 4-pillar free navigation perfectly! 🚀

**For multi-service atomicity:** Use **Saga Journey Orchestrator** when you need automatic compensation on failure! 🎭









