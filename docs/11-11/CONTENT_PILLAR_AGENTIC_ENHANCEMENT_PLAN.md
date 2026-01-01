# Content Analysis Orchestrator - Agentic Enhancement Plan

**Date**: November 12, 2025  
**Focus**: Post-parsing agentic interactions with AI-friendly formats  
**Principle**: Agents interact with parsed results, not raw files

**Architecture**: Agents use **ContentAnalysisOrchestrator** methods (which internally call enabling services), NOT old archived pillar services.

---

## 🎯 Core Principle

**Content Pillar Purpose**: Make content consumable for agents  
**Agentic Scope**: **POST-PARSING ONLY** - Agents work with:
- ✅ Parsed results (Parquet, JSON Structured, JSON Chunks)
- ✅ Metadata extraction results
- ✅ Content insights
- ❌ NOT raw file parsing (that's infrastructure)

---

## 1. Current State Analysis

### ✅ What We Have
- `ContentProcessingAgent` (specialist agent) - initialized but not used
- `FileParserService` - Full parsing logic (PDF, Word, Excel, COBOL, Mainframe, etc.)
- `DataAnalyzerService` - Content analysis capabilities
- `FormatComposerService` - Format conversion (Parquet, JSON Structured, JSON Chunks)
- Basic MCP Server with 3 tools

### ❌ What's Missing
- Agent refinement for parsed results
- Agent enhancement of metadata extraction
- Agent enhancement of content insights
- Missing frontend APIs: `list_files()`, `get_file_metadata()`, `process_documents()`, `convert_format()`
- MCP tools for agent-assisted enhancement

---

## 2. Agentic Enhancement Strategy

### 2.1 Post-Parsing Agent Interactions

**Agent works with parsed data, not raw files:**

```python
# ✅ CORRECT: Agent enhances parsed results
parsed_result = await file_parser.parse_file(file_id)
enhanced_metadata = await agent.enhance_metadata_extraction(parsed_result)
enhanced_insights = await agent.enhance_content_insights(parsed_result)

# ❌ WRONG: Agent does not parse files
# agent.parse_file()  # NO - that's infrastructure
```

### 2.2 Agent Capabilities

**ContentProcessingAgent should provide:**

1. **Metadata Enhancement**:
   - Enrich extracted metadata with semantic understanding
   - Add business context to metadata
   - Validate and correct metadata inconsistencies

2. **Content Insights Enhancement**:
   - Generate semantic summaries from parsed content
   - Identify key themes and topics
   - Extract business-relevant insights
   - Categorize content by domain/purpose

3. **Format Optimization**:
   - Recommend optimal format based on content type
   - Suggest format conversions for better AI consumption
   - Validate format compatibility

---

## 3. Implementation Plan

### Phase 1: Enable Specialist Agent (Quick Win - 30 min)

**File**: `content_analysis_orchestrator.py`

**In `initialize()` method** (after line 158):
```python
# Give specialist agent access to orchestrator (for MCP server access)
if self.processing_agent and hasattr(self.processing_agent, 'set_orchestrator'):
    self.processing_agent.set_orchestrator(self)
```

### Phase 2: Add Agent Enhancement Methods (2 hours)

**Add to `ContentProcessingAgent`** (`agents/content_processing_agent.py`):

```python
    async def enhance_metadata_extraction(
        self,
        parsed_result: Dict[str, Any],
        file_id: str,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Enhance metadata extraction with agent reasoning.
        
        Works with parsed results (AI-friendly formats) to:
        - Enrich metadata with semantic understanding
        - Add business context
        - Validate and correct inconsistencies
        
        **Architecture**: Uses ContentAnalysisOrchestrator methods (which call enabling services),
        NOT old archived pillar services.
        
        Args:
            parsed_result: Parsed file result from FileParserService (via orchestrator)
            file_id: File identifier
            user_id: User identifier
    
        Returns:
            Enhanced metadata with agent insights
        """
        try:
            # Extract base metadata
            base_metadata = parsed_result.get("metadata", {})
            
            # Use orchestrator methods to access enabling services
            # (Agent has orchestrator reference via set_orchestrator())
            if self.orchestrator:
                # Can call orchestrator methods directly:
                # - self.orchestrator.analyze_document() → calls FileParserService + DataAnalyzerService
                # - self.orchestrator.extract_entities() → calls DataAnalyzerService
                pass
            
            # Analyze parsed content for semantic enrichment
            parsed_content = parsed_result.get("content", {})
        
        # Generate enhanced metadata
        enhanced_metadata = {
            **base_metadata,
            "agent_enhanced": True,
            "semantic_tags": self._extract_semantic_tags(parsed_content),
            "business_context": self._infer_business_context(parsed_content),
            "quality_score": self._assess_metadata_quality(base_metadata),
            "recommendations": self._generate_metadata_recommendations(base_metadata, parsed_content)
        }
        
        return {
            "success": True,
            "metadata": enhanced_metadata,
            "enhancements": {
                "semantic_tags_added": len(enhanced_metadata.get("semantic_tags", [])),
                "business_context_added": enhanced_metadata.get("business_context") is not None,
                "quality_improved": enhanced_metadata.get("quality_score", 0) > base_metadata.get("quality_score", 0)
            }
        }
    except Exception as e:
        self.logger.error(f"❌ Metadata enhancement failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "metadata": parsed_result.get("metadata", {})
        }

async def enhance_content_insights(
    self,
    parsed_result: Dict[str, Any],
    analysis_result: Dict[str, Any],
    user_id: str = "anonymous"
) -> Dict[str, Any]:
    """
    Enhance content insights with agent reasoning.
    
    Works with parsed results and analysis to:
    - Generate semantic summaries
    - Identify key themes and topics
    - Extract business-relevant insights
    - Categorize content by domain
    
    Args:
        parsed_result: Parsed file result
        analysis_result: Analysis result from DataAnalyzerService
        user_id: User identifier
    
    Returns:
        Enhanced insights with agent reasoning
    """
    try:
        # Extract base insights
        base_insights = analysis_result.get("insights", {})
        parsed_content = parsed_result.get("content", {})
        
        # Generate enhanced insights
        enhanced_insights = {
            **base_insights,
            "agent_enhanced": True,
            "semantic_summary": self._generate_semantic_summary(parsed_content),
            "key_themes": self._identify_key_themes(parsed_content),
            "business_insights": self._extract_business_insights(parsed_content, base_insights),
            "domain_categorization": self._categorize_by_domain(parsed_content),
            "recommendations": self._generate_content_recommendations(parsed_content, base_insights)
        }
        
        return {
            "success": True,
            "insights": enhanced_insights,
            "enhancements": {
                "semantic_summary_generated": enhanced_insights.get("semantic_summary") is not None,
                "themes_identified": len(enhanced_insights.get("key_themes", [])),
                "business_insights_extracted": len(enhanced_insights.get("business_insights", [])),
                "domain_categorized": enhanced_insights.get("domain_categorization") is not None
            }
        }
    except Exception as e:
        self.logger.error(f"❌ Content insights enhancement failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "insights": analysis_result.get("insights", {})
        }

async def recommend_format_optimization(
    self,
    parsed_result: Dict[str, Any],
    current_format: str,
    user_id: str = "anonymous"
) -> Dict[str, Any]:
    """
    Recommend format optimization based on content analysis.
    
    Args:
        parsed_result: Parsed file result
        current_format: Current format (parquet, json_structured, json_chunks)
        user_id: User identifier
    
    Returns:
        Format recommendations
    """
    try:
        content_type = parsed_result.get("file_type", "")
        content_structure = parsed_result.get("structure", {})
        
        # Analyze content characteristics
        is_structured = content_structure.get("has_tables", False) or content_structure.get("has_schema", False)
        is_large = parsed_result.get("size_bytes", 0) > 1000000  # > 1MB
        has_text = content_structure.get("has_text", False)
        
        # Recommend optimal format
        if is_structured and is_large:
            recommended_format = "parquet"
        elif is_structured:
            recommended_format = "json_structured"
        else:
            recommended_format = "json_chunks"
        
        return {
            "success": True,
            "current_format": current_format,
            "recommended_format": recommended_format,
            "rationale": self._generate_format_rationale(content_type, is_structured, is_large, has_text),
            "conversion_available": recommended_format != current_format
        }
    except Exception as e:
        self.logger.error(f"❌ Format recommendation failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

### Phase 3: Integrate Agent Enhancement into Orchestrator (1 hour)

**Update `analyze_document()` method** (after line 248):

```python
# 3. Entity extraction via DataAnalyzer
if "entities" in analysis_types:
    data_analyzer = await self._get_data_analyzer_service()
    if data_analyzer:
        entities_result = await data_analyzer.extract_entities(document_id)
        if entities_result.get("success"):
            results["entities"] = entities_result.get("entities", [])
        else:
            results["entities"] = {"error": "Entity extraction failed"}
    else:
        results["entities"] = {"error": "Data Analyzer service not available"}

# 4. Agent Enhancement (POST-PARSING ONLY)
if self.processing_agent and hasattr(self.processing_agent, 'enhance_metadata_extraction'):
    try:
        # Enhance metadata extraction
        if "metadata" in results:
            metadata_enhancement = await self.processing_agent.enhance_metadata_extraction(
                parsed_result={
                    "metadata": results.get("metadata", {}),
                    "content": results.get("structure", {}).get("content_preview", ""),
                    "file_type": results.get("structure", {}).get("file_type")
                },
                file_id=document_id,
                user_id=user_id
            )
            if metadata_enhancement.get("success"):
                results["metadata"] = metadata_enhancement.get("metadata", results.get("metadata", {}))
                results["metadata_agent_enhanced"] = True
        
        # Enhance content insights
        if "entities" in results and results.get("entities"):
            insights_enhancement = await self.processing_agent.enhance_content_insights(
                parsed_result={
                    "content": results.get("structure", {}).get("content_preview", ""),
                    "file_type": results.get("structure", {}).get("file_type")
                },
                analysis_result={"insights": results.get("entities", [])},
                user_id=user_id
            )
            if insights_enhancement.get("success"):
                results["insights"] = insights_enhancement.get("insights", {})
                results["insights_agent_enhanced"] = True
    except Exception as e:
        self.logger.warning(f"⚠️ Agent enhancement failed: {e}, continuing with base results")

# 5. Use Smart City services for lineage tracking...
```

### Phase 4: Add Missing Frontend APIs (2 hours)

**Add methods to orchestrator**:

```python
async def list_files(
    self,
    user_id: str = "anonymous",
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """List uploaded files for user."""
    # Use FileManagementAbstraction or ContentSteward
    pass

async def get_file_metadata(
    self,
    file_id: str,
    user_id: str = "anonymous"
) -> Dict[str, Any]:
    """Get file metadata (with agent enhancement if available)."""
    # Get base metadata, then enhance with agent
    pass

async def process_documents(
    self,
    file_ids: List[str],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Batch process multiple documents."""
    pass

async def convert_format(
    self,
    file_id: str,
    target_format: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convert file format using FormatComposerService."""
    # Use FormatComposerService
    pass
```

### Phase 5: Enhance MCP Server (1 hour)

**File**: `content_analysis_mcp_server.py`

**Add tools**:
```python
# Tool 4: Enhance Metadata Extraction
self.register_tool(
    name="enhance_metadata_extraction_tool",
    description="Enhance metadata extraction with agent reasoning. Works with parsed results (AI-friendly formats).",
    handler=self._enhance_metadata_extraction_tool,
    input_schema={
        "type": "object",
        "properties": {
            "parsed_result": {
                "type": "object",
                "description": "Parsed file result from FileParserService"
            },
            "file_id": {"type": "string", "description": "File identifier"}
        },
        "required": ["parsed_result", "file_id"]
    }
)

# Tool 5: Enhance Content Insights
self.register_tool(
    name="enhance_content_insights_tool",
    description="Enhance content insights with agent reasoning. Works with parsed results and analysis.",
    handler=self._enhance_content_insights_tool,
    input_schema={
        "type": "object",
        "properties": {
            "parsed_result": {"type": "object"},
            "analysis_result": {"type": "object"}
        },
        "required": ["parsed_result", "analysis_result"]
    }
)

# Tool 6: Recommend Format Optimization
self.register_tool(
    name="recommend_format_optimization_tool",
    description="Recommend optimal format based on content analysis. Works with parsed results.",
    handler=self._recommend_format_optimization_tool,
    input_schema={
        "type": "object",
        "properties": {
            "parsed_result": {"type": "object"},
            "current_format": {"type": "string", "enum": ["parquet", "json_structured", "json_chunks"]}
        },
        "required": ["parsed_result", "current_format"]
    }
)

# Tool 7: Compose Format (FormatComposerService)
self.register_tool(
    name="compose_format_tool",
    description="Convert parsed data to target format (Parquet, JSON Structured, JSON Chunks).",
    handler=self._compose_format_tool,
    input_schema={
        "type": "object",
        "properties": {
            "parsed_data": {"type": "object"},
            "target_format": {"type": "string", "enum": ["parquet", "json_structured", "json_chunks"]}
        },
        "required": ["parsed_data", "target_format"]
    }
)
```

---

## 4. Key Principles

### ✅ DO:
- Agent works with parsed results (AI-friendly formats)
- Agent enhances metadata extraction
- Agent enhances content insights
- Agent recommends format optimization
- Agent uses MCP tools for orchestrator capabilities

### ❌ DON'T:
- Agent does NOT parse raw files (that's FileParserService)
- Agent does NOT handle file uploads (that's infrastructure)
- Agent does NOT do format detection (that's FileParserService)

---

## 5. Success Criteria

- ✅ Specialist agent initialized and integrated
- ✅ Agent enhancement methods implemented
- ✅ Agent works with parsed results only
- ✅ Metadata enhancement working
- ✅ Content insights enhancement working
- ✅ Format recommendation working
- ✅ All frontend APIs implemented
- ✅ MCP Server enhanced with agent tools
- ✅ Responses include `agent_enhanced` flags

---

## 6. Implementation Timeline

- **Phase 1**: 30 min (Enable agent)
- **Phase 2**: 2 hours (Agent methods)
- **Phase 3**: 1 hour (Orchestrator integration)
- **Phase 4**: 2 hours (Frontend APIs)
- **Phase 5**: 1 hour (MCP Server)

**Total**: ~6.5 hours

