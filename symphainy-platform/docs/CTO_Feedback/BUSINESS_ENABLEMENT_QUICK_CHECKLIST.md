# ✅ Business Enablement Refactoring - Quick Checklist

**Strategic Decision:** ENABLING SERVICES = FIRST-CLASS PLATFORM CITIZENS

---

## 🎯 THE BIG PICTURE

```
BEFORE (MVP-Centric):
Content Pillar Service → orchestrates features for MVP UI
  └─ Hidden micro-modules have the real capabilities

AFTER (Platform-Centric):
FileParserService (first-class) → atomic capability
MetadataExtractionService (first-class) → atomic capability
FormatConversionService (first-class) → atomic capability
  ↓
Business Orchestrator → composes services for use cases
  ├─ MVP: Content → Insights → Operations → Outcomes
  └─ Data Mash: Metadata → SchemaMap → VirtualView
```

---

## 📋 ENABLING SERVICES TO CREATE (15-20 services)

### **Content Intelligence (8 services)**
- [ ] FileParserService (umbrella + delegation)
- [ ] COBOLParserService
- [ ] MainframeParserService
- [ ] ExcelParserService (P2)
- [ ] PDFParserService (P2)
- [ ] MetadataExtractionService
- [ ] FormatConversionService
- [ ] ContentValidationService

### **Insights & Analysis (5 services)**
- [ ] DataAnalyzerService
- [ ] InsightsGeneratorService
- [ ] MetricsCalculatorService
- [ ] VisualizationService (consolidated)
- [ ] APGAnalyzerService (P2)

### **Process Optimization (3 services)**
- [ ] SOPAnalyzerService
- [ ] CoexistenceOptimizerService
- [ ] WorkflowBuilderService (new)

### **Business Strategy (4 services)**
- [ ] StrategicPlannerService
- [ ] POCGeneratorService
- [ ] FinancialAnalyzerService
- [ ] BusinessMetricsService

---

## ✅ EVERY ENABLING SERVICE MUST HAVE:

1. **Base Class:** `RealmServiceBase`
2. **SOA APIs:** 3-5 core capabilities
3. **MCP Server:** Wraps SOA APIs as tools (1:1 pattern)
4. **MCP Tools:** Exposed and working
5. **Curator Registration:** Complete metadata
6. **Platform Gateway:** Use `ctx.get_abstraction(name)`
7. **Smart City APIs:** Discover via `ctx.get_smart_city_api(name)`
8. **Complete Implementation:** NO stubs, NO placeholders

---

## 🏗️ SERVICE TEMPLATE (Copy for each service)

```python
# backend/business_enablement/services/[service_name]/[service_name]_service.py

from bases.realm_service_base import RealmServiceBase

class [ServiceName]Service(RealmServiceBase):
    """
    [Service Name] Service
    
    WHAT: I [core capability]
    HOW: I use Smart City ([services]) + abstractions
    """
    
    def __init__(self, context: RealmContext):
        super().__init__(context, "[ServiceName]Service")
        
        # Infrastructure abstractions (via Platform Gateway)
        self.[abstraction] = None
        
        # Smart City services (discovered via Curator)
        self.[smart_city_service] = None
        
        # Micro-modules
        self.[module]_module = [Module](self)
    
    async def initialize(self):
        """Initialize service."""
        await super().initialize()
        
        # Get abstractions
        self.[abstraction] = self.ctx.get_abstraction("[abstraction_name]")
        
        # Discover Smart City services
        self.[smart_city_service] = await self.ctx.get_smart_city_api("[ServiceName]")
        
        # Register with Curator
        await self.register_with_curator()
    
    # ==========================================
    # SOA APIs (3-5 core capabilities)
    # ==========================================
    
    async def [capability_1](self, params) -> Result:
        """[Description]"""
        # Complete implementation
        pass
    
    async def [capability_2](self, params) -> Result:
        """[Description]"""
        # Complete implementation
        pass

# MCP Server
# backend/business_enablement/services/[service_name]/mcp_server/[service_name]_mcp_server.py

from bases.mcp_server_base import MCPServerBase

class [ServiceName]MCPServer(MCPServerBase):
    """MCP Server for [ServiceName]Service"""
    
    def __init__(self, service, di_container):
        super().__init__(
            server_name="[service_name]_mcp",
            di_container=di_container,
            server_type="single_service"
        )
        self.service = service
        self._register_tools()
    
    def _register_tools(self):
        self.register_tool(
            name="[capability_1]_tool",
            description="[Description]",
            handler=self._[capability_1]_tool,
            input_schema={...}
        )
    
    async def _[capability_1]_tool(self, **kwargs):
        return await self.service.[capability_1](**kwargs)
```

---

## 🎯 BUSINESS ORCHESTRATOR TEMPLATE

```python
# backend/business_enablement/orchestration/business_orchestrator/business_orchestrator_service.py

class BusinessOrchestratorService(RealmServiceBase):
    """
    WHAT: I compose enabling services into use-case workflows
    HOW: I discover services via Curator, orchestrate via Conductor
    """
    
    # MVP USE CASE
    async def execute_mvp_workflow(self, user_files, user_goals):
        content = await self.orchestrate_content_phase(user_files)
        insights = await self.orchestrate_insights_phase(content)
        operations = await self.orchestrate_operations_phase(insights)
        outcomes = await self.orchestrate_business_outcomes_phase(operations)
        return outcomes
    
    async def orchestrate_content_phase(self, files):
        """Compose: FileParser + MetadataExtractor + ContentValidator"""
        file_parser = await self.get_enabling_service("FileParserService")
        metadata_extractor = await self.get_enabling_service("MetadataExtractionService")
        content_validator = await self.get_enabling_service("ContentValidationService")
        
        # Orchestrate
        results = []
        for file in files:
            parsed = await file_parser.parse_file(file)
            metadata = await metadata_extractor.extract_metadata(parsed)
            validated = await content_validator.validate_content(metadata)
            results.append({"parsed": parsed, "metadata": metadata})
        
        return results
    
    # DATA MASH USE CASE (Future)
    async def execute_data_mash_workflow(self, sources, target_schema):
        """Compose: MetadataExtractor → InsightsGenerator → DataAnalyzer"""
        metadata_extractor = await self.get_enabling_service("MetadataExtractionService")
        insights_generator = await self.get_enabling_service("InsightsGeneratorService")
        data_analyzer = await self.get_enabling_service("DataAnalyzerService")
        
        # Orchestrate Data Mash
        metadata = await metadata_extractor.extract_from_sources(sources)
        mappings = await insights_generator.generate_schema_mappings(metadata, target_schema)
        virtual_view = await data_analyzer.create_virtual_view(sources, mappings)
        
        return virtual_view
```

---

## 🚫 WHAT TO ELIMINATE

- [ ] ~~Content Pillar Service~~ → Business Orchestrator.orchestrate_content_phase()
- [ ] ~~Insights Pillar Service~~ → Business Orchestrator.orchestrate_insights_phase()
- [ ] ~~Operations Pillar Service~~ → Business Orchestrator.orchestrate_operations_phase()
- [ ] ~~Business Outcomes Pillar Service~~ → Business Orchestrator.orchestrate_business_outcomes_phase()

**Why:** Pillar services add no value. Business Orchestrator handles composition.

---

## 📅 WEEK-BY-WEEK PLAN

### **Week 7: Content + Insights Services**
- Days 1-3: Content Intelligence services (FileParser, Metadata, Format, Validation)
- Days 4-5: Insights & Analysis services (DataAnalyzer, InsightsGenerator, Metrics)

### **Week 8: Process + Strategy + Orchestration**
- Days 1-2: Process + Strategy services (SOP, Coexistence, POC, Planner)
- Days 3-5: Business Orchestrator (MVP flow + integration testing)

---

## ✅ TESTING CHECKLIST (Every Service)

- [ ] Service initializes successfully
- [ ] Gets abstractions via Platform Gateway
- [ ] Discovers Smart City APIs via Curator
- [ ] SOA APIs return real results (not {})
- [ ] MCP Server wraps SOA APIs
- [ ] MCP Tools executable via Agentic Foundation
- [ ] Registered with Curator (complete metadata)
- [ ] Works in Business Orchestrator composition

---

## 🎊 SUCCESS = PLATFORM NOT MVP

**BEFORE:** MVP features hardcoded in pillar services  
**AFTER:** Atomic capabilities composed for any use case  

**Your CTO can now say:**
> "Our platform has 15-20 enabling services that can be composed for MVP, Data Mash, or any future use case. Each service exposes SOA APIs and MCP Tools. Agents can use them. Clients can customize workflows. We're a platform, not just an MVP."

---

_Use `BUSINESS_ENABLEMENT_STRATEGIC_REFACTORING_PLAN.md` for full details.  
This checklist is your daily execution guide._ ✅










