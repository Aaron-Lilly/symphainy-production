# Architecture Clarification - Agent-Orchestrator-Enabling Services Pattern

**Date**: November 12, 2025  
**Purpose**: Clarify the correct architecture pattern for agent interactions

---

## ✅ Correct Architecture Pattern

### Agent → Orchestrator → Enabling Services

```
Specialist Agent
    ↓ (calls orchestrator methods)
Orchestrator (e.g., ContentAnalysisOrchestrator)
    ↓ (calls enabling services)
Enabling Services (e.g., FileParserService, DataAnalyzerService)
```

### Key Points:

1. **Agents use Orchestrator methods**:
   - Agents have orchestrator reference via `set_orchestrator()`
   - Agents call `self.orchestrator.method_name()` directly
   - Orchestrator methods internally call enabling services

2. **MCP Servers expose Orchestrator methods as tools**:
   - MCP Server wraps orchestrator methods as MCP tools
   - Agents can use MCP tools OR call orchestrator methods directly
   - MCP tools delegate to orchestrator methods

3. **Orchestrators call Enabling Services**:
   - Orchestrator methods internally call enabling services
   - Example: `orchestrator.analyze_document()` → calls `FileParserService.parse_file()` + `DataAnalyzerService.extract_entities()`

---

## ❌ Incorrect Pattern (Old Architecture)

### Agent → Old Pillar Service (DEPRECATED)

```
Specialist Agent
    ↓ (calls old pillar service)
Old Pillar Service (e.g., ContentPillarService) ❌ ARCHIVED
```

**This is WRONG** - Old pillar services are archived/deprecated.

---

## Example: Content Analysis Orchestrator

### ✅ Correct Pattern:

```python
# In ContentProcessingAgent
async def enhance_metadata_extraction(self, parsed_result, file_id):
    # Use orchestrator method (which calls enabling services)
    if self.orchestrator:
        # Orchestrator method internally calls FileParserService + DataAnalyzerService
        analysis = await self.orchestrator.analyze_document(
            document_id=file_id,
            analysis_types=["metadata", "entities"]
        )
        # Agent enhances the results
        enhanced_metadata = self._enhance_with_agent_reasoning(analysis)
        return enhanced_metadata
```

### ❌ Wrong Pattern:

```python
# DON'T do this - old pillar service is archived
from backend.business_enablement.pillars.content_pillar.content_pillar_service import ContentPillarService
content_pillar = ContentPillarService(...)  # ❌ ARCHIVED
```

---

## Example: Insights Orchestrator

### ✅ Correct Pattern:

```python
# In InsightsSpecialistAgent
async def generate_grounded_insights(self, data_id, analysis_options):
    # Use orchestrator methods (which call enabling services)
    if self.insights_orchestrator:
        # Orchestrator internally calls DataAnalyzerService + MetricsCalculatorService
        analysis = await self.insights_orchestrator.calculate_metrics(
            resource_id=data_id,
            options=analysis_options
        )
        # Orchestrator internally calls VisualizationEngineService
        visualization = await self.insights_orchestrator.create_visualization(
            resource_id=data_id,
            options=analysis_options
        )
        # Agent generates business narrative from data science results
        narrative = self._generate_business_narrative(analysis, visualization)
        return narrative
```

### ❌ Wrong Pattern:

```python
# DON'T do this - old pillar service is archived
from backend.business_enablement.pillars.insights_pillar.insights_pillar_service import InsightsPillarService
insights_pillar = InsightsPillarService(...)  # ❌ ARCHIVED
```

---

## MCP Server Pattern

### MCP Server exposes Orchestrator methods:

```python
# In ContentAnalysisMCPServer
async def _analyze_document_tool(self, document_id, analysis_types):
    """MCP Tool: Analyze Document."""
    # Delegate to orchestrator method
    return await self.orchestrator.analyze_document(
        document_id=document_id,
        analysis_types=analysis_types
    )
```

### Agent can use MCP tool OR call orchestrator directly:

```python
# Option 1: Via MCP tool
result = await mcp_server.execute_tool("analyze_document_tool", {...})

# Option 2: Direct orchestrator call (preferred for specialist agents)
result = await self.orchestrator.analyze_document(document_id, analysis_types)
```

---

## Summary

**✅ DO**:
- Agents use orchestrator methods (`self.orchestrator.method_name()`)
- Orchestrators call enabling services internally
- MCP Servers expose orchestrator methods as tools

**❌ DON'T**:
- Agents call old archived pillar services
- Agents call enabling services directly (use orchestrator instead)
- Reference old pillar architecture

---

## File Locations

### ✅ New Architecture (Use These):
- Orchestrators: `backend/business_enablement/delivery_manager/mvp_pillar_orchestrators/`
  - `content_analysis_orchestrator/`
  - `insights_orchestrator/`
  - `operations_orchestrator/`
  - `business_outcomes_orchestrator/`
- Enabling Services: `backend/business_enablement/enabling_services/`
- MCP Servers: `{orchestrator}/mcp_server/`

### ❌ Old Architecture (Archived - Don't Use):
- Old Pillar Services: `backend/business_enablement/pillars/` (ARCHIVED)
- Old MCP Servers: `backend/business_enablement/pillars/{pillar}/mcp_server/` (ARCHIVED)

