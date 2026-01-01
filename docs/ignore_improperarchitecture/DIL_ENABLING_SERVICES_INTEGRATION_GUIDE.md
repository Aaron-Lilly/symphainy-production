# DIL SDK Integration Guide for Enabling Services Refactoring

**Date:** January 2025  
**Audience:** Enabling Services Refactoring Team  
**Purpose:** Guide for integrating DIL SDK into Content and Insights enabling services

---

## Executive Summary

This guide explains how to use the new DIL (Data Intelligence Layer) SDK pattern in your enabling services refactoring, specifically for **Content** and **Insights** services.

**Key Principle:** All data operations go through DIL SDK - services use semantic data, not raw client data.

---

## 1. DIL SDK Overview

### What is DIL SDK?

DIL SDK is the **single entry/exit point** for all data operations in the platform. It provides:
- **Data Operations:** Upload, parse, embed, store, query
- **Semantic Layer:** Semantic IDs, relationships, contracts (future)
- **Governance:** Lineage, classification, policies
- **Observability:** Platform data, telemetry, tracing

### Why Use DIL SDK?

**Before (Current Pattern):**
```python
# Service directly accesses infrastructure
file_metadata = await file_management_abstraction.create_file(...)
parse_result = await file_parser_service.parse_file(...)
embeddings = await hf_inference_agent.generate_embedding(...)
await content_metadata_abstraction.store_semantic_embeddings(...)
```

**After (DIL SDK Pattern):**
```python
# Service uses DIL SDK
file_metadata = await dil.data.upload_file(...)
parse_result = await dil.data.parse_file(...)
embeddings = await dil.data.embed_content(...)
await dil.data.store_semantic(...)
```

**Benefits:**
- ✅ Unified data governance
- ✅ Automatic lineage tracking
- ✅ Semantic-first data integration
- ✅ Platform vs client data distinction
- ✅ Future-proof (evolvable to contracts)

---

## 2. DIL SDK API Reference

### Data Operations Module

```python
from dil import data

# Upload file
file_metadata = await dil.data.upload_file(
    file_data: bytes,
    filename: str,
    metadata: Dict[str, Any],
    user_context: Dict[str, Any]
) -> Dict[str, Any]

# Parse file
parse_result = await dil.data.parse_file(
    file_id: str,
    parse_options: Dict[str, Any],
    user_context: Dict[str, Any]
) -> Dict[str, Any]

# Embed content
embeddings = await dil.data.embed_content(
    content: str | Dict[str, Any],
    embedding_type: str,  # "metadata", "meaning", "samples", "text", "entity"
    user_context: Dict[str, Any]
) -> Dict[str, Any]

# Store semantic data
await dil.data.store_semantic(
    content_id: str,
    embeddings: List[Dict[str, Any]],  # For structured
    semantic_graph: Dict[str, Any],  # For unstructured
    correlation_map: Dict[str, Any],  # For hybrid (NEW)
    user_context: Dict[str, Any]
) -> Dict[str, Any]

# Query semantic data
results = await dil.data.query_semantic(
    query: str,
    filters: Dict[str, Any],
    user_context: Dict[str, Any]
) -> List[Dict[str, Any]]

# Query by semantic ID
results = await dil.data.query_by_semantic_id(
    semantic_id: str,
    user_context: Dict[str, Any]
) -> List[Dict[str, Any]]

# Vector search
results = await dil.data.vector_search(
    query_vector: List[float],
    top_k: int = 10,
    filters: Dict[str, Any],
    user_context: Dict[str, Any]
) -> List[Dict[str, Any]]

# Get semantic graph
graph = await dil.data.get_semantic_graph(
    content_id: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]

# Query correlation map (NEW - for hybrid)
correlation_map = await dil.data.query_correlation_map(
    file_id: str,
    filters: Dict[str, Any],
    user_context: Dict[str, Any]
) -> Dict[str, Any]
```

### Governance Module

```python
from dil import governance

# Create semantic ID (realm creates, Data Steward curates)
semantic_id = await dil.governance.create_semantic_id(
    name: str,
    meaning: str,
    semantic_type: str,  # "metric", "dimension", "entity"
    data_type: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]

# Record lineage
await dil.governance.record_lineage(
    source_id: str,
    target_id: str,
    transformation: str,
    user_context: Dict[str, Any]
) -> Dict[str, Any]

# Classify data
await dil.governance.classify_data(
    data_id: str,
    classification: str,  # "platform" or "client"
    tenant_id: Optional[str],
    user_context: Dict[str, Any]
) -> Dict[str, Any]
```

---

## 3. Content Services Integration

### FileParserService

**Current Pattern:**
```python
class FileParserService:
    async def parse_file(self, file_id, parse_options, user_context):
        # Direct infrastructure access
        file_data = await file_management_abstraction.get_file(file_id)
        parse_result = await self._parse(file_data, parse_options)
        return parse_result
```

**New Pattern (DIL SDK):**
```python
class FileParserService:
    def __init__(self, ...):
        # Get DIL SDK via DI Container
        self.dil_sdk = None
    
    async def initialize(self):
        dil_foundation = self.di_container.get_foundation_service("DataIntelligenceFoundationService")
        if dil_foundation:
            self.dil_sdk = dil_foundation.get_sdk()
    
    async def parse_file(self, file_id, parse_options, user_context):
        # Use DIL SDK for parsing
        parse_result = await self.dil_sdk.data.parse_file(
            file_id=file_id,
            parse_options=parse_options,
            user_context=user_context
        )
        
        # Record lineage
        await self.dil_sdk.governance.record_lineage(
            source_id=file_id,
            target_id=parse_result.get("parse_id"),
            transformation="parse",
            user_context=user_context
        )
        
        return parse_result
```

**Key Changes:**
- ✅ Use `dil.data.parse_file()` instead of direct infrastructure
- ✅ Record lineage via `dil.governance.record_lineage()`
- ✅ All data operations go through DIL SDK

### ContentAnalysisOrchestrator (Hybrid Parsing)

**Current Pattern:**
```python
async def _process_hybrid_semantic(self, parse_result, user_context):
    # Process structured
    structured_result = await self._process_structured_semantic(...)
    
    # Process unstructured
    unstructured_result = await self._process_unstructured_semantic(...)
    
    return {
        "structured_result": structured_result,
        "unstructured_result": unstructured_result
    }
```

**New Pattern (DIL SDK + Correlation Map):**
```python
async def _process_hybrid_semantic(self, parse_result, user_context):
    # Process structured via DIL SDK
    structured_embeddings = []
    for column in columns:
        embedding = await self.dil_sdk.data.embed_content(
            content=column,
            embedding_type="metadata",
            user_context=user_context
        )
        structured_embeddings.append(embedding)
    
    # Process unstructured via DIL SDK
    unstructured_graph = await self.dil_sdk.data.embed_content(
        content=parse_result["text_content"],
        embedding_type="entity",
        user_context=user_context
    )
    
    # ✅ NEW: Generate correlation map
    correlation_map = await self._generate_correlation_map(
        structured_embeddings=structured_embeddings,
        unstructured_graph=unstructured_graph,
        parse_result=parse_result,
        user_context=user_context
    )
    
    # Store via DIL SDK
    await self.dil_sdk.data.store_semantic(
        content_id=content_id,
        embeddings=structured_embeddings,
        semantic_graph=unstructured_graph,
        correlation_map=correlation_map,  # ✅ NEW
        user_context=user_context
    )
    
    return {
        "structured_result": structured_embeddings,
        "unstructured_result": unstructured_graph,
        "correlation_map": correlation_map  # ✅ NEW
    }
```

**Key Changes:**
- ✅ Use `dil.data.embed_content()` for embeddings
- ✅ Use `dil.data.store_semantic()` for storage
- ✅ Generate correlation map (see correlation map spec)
- ✅ Store correlation map via DIL SDK

---

## 4. Insights Services Integration

### DataAnalyzerService

**Current Pattern:**
```python
class DataAnalyzerService:
    async def analyze_data(self, file_id, analysis_options, user_context):
        # Direct file access
        file_data = await file_management_abstraction.get_file(file_id)
        parsed_data = await file_parser_service.parse_file(file_id)
        
        # Analyze parsed data
        analysis_result = await self._analyze(parsed_data)
        return analysis_result
```

**New Pattern (DIL SDK - Semantic Data):**
```python
class DataAnalyzerService:
    def __init__(self, ...):
        self.dil_sdk = None
    
    async def initialize(self):
        dil_foundation = self.di_container.get_foundation_service("DataIntelligenceFoundationService")
        if dil_foundation:
            self.dil_sdk = dil_foundation.get_sdk()
    
    async def analyze_data(self, file_id, analysis_options, user_context):
        # ✅ Query semantic data instead of raw files
        semantic_data = await self.dil_sdk.data.query_semantic(
            query="",
            filters={"file_id": file_id},
            user_context=user_context
        )
        
        # Get semantic graph for unstructured analysis
        semantic_graph = await self.dil_sdk.data.get_semantic_graph(
            content_id=file_id,
            user_context=user_context
        )
        
        # Analyze semantic data (not raw files)
        analysis_result = await self._analyze_semantic_data(
            semantic_data=semantic_data,
            semantic_graph=semantic_graph,
            analysis_options=analysis_options
        )
        
        return analysis_result
```

**Key Changes:**
- ✅ Use `dil.data.query_semantic()` instead of direct file access
- ✅ Use `dil.data.get_semantic_graph()` for unstructured analysis
- ✅ Analyze semantic data, not raw client files

### MetricsCalculatorService

**Current Pattern:**
```python
async def calculate_metrics(self, file_id, metric_definitions, user_context):
    # Direct file access
    parsed_data = await file_parser_service.parse_file(file_id)
    
    # Calculate metrics from parsed data
    metrics = await self._calculate(parsed_data, metric_definitions)
    return metrics
```

**New Pattern (DIL SDK - Semantic IDs):**
```python
async def calculate_metrics(self, file_id, metric_definitions, user_context):
    # ✅ Query semantic data by semantic IDs
    semantic_data = []
    for metric_def in metric_definitions:
        semantic_id = metric_def.get("semantic_id")
        if semantic_id:
            # Query by semantic ID
            data = await self.dil_sdk.data.query_by_semantic_id(
                semantic_id=semantic_id,
                user_context=user_context
            )
            semantic_data.extend(data)
    
    # Calculate metrics from semantic data
    metrics = await self._calculate_from_semantic_data(
        semantic_data=semantic_data,
        metric_definitions=metric_definitions
    )
    
    return metrics
```

**Key Changes:**
- ✅ Use `dil.data.query_by_semantic_id()` for metric data
- ✅ Metrics defined by semantic IDs (not column names)
- ✅ Cross-file metric calculation enabled

### VisualizationEngineService

**Current Pattern:**
```python
async def create_visualization(self, file_id, visualization_options, user_context):
    # Direct file access
    parsed_data = await file_parser_service.parse_file(file_id)
    
    # Create visualization from parsed data
    visualization = await self._create(parsed_data, visualization_options)
    return visualization
```

**New Pattern (DIL SDK - Semantic Relationships):**
```python
async def create_visualization(self, file_id, visualization_options, user_context):
    # ✅ Query semantic data and relationships
    semantic_data = await self.dil_sdk.data.query_semantic(
        query="",
        filters={"file_id": file_id},
        user_context=user_context
    )
    
    # Get semantic graph for relationship visualization
    semantic_graph = await self.dil_sdk.data.get_semantic_graph(
        content_id=file_id,
        user_context=user_context
    )
    
    # Get correlation map for hybrid visualization
    correlation_map = await self.dil_sdk.data.query_correlation_map(
        file_id=file_id,
        filters={},
        user_context=user_context
    )
    
    # Create visualization from semantic data
    visualization = await self._create_from_semantic_data(
        semantic_data=semantic_data,
        semantic_graph=semantic_graph,
        correlation_map=correlation_map,
        visualization_options=visualization_options
    )
    
    return visualization
```

**Key Changes:**
- ✅ Use semantic data for visualization
- ✅ Use semantic graph for relationship visualization
- ✅ Use correlation map for hybrid visualization

### InsightsGeneratorService

**Current Pattern:**
```python
async def generate_insights(self, file_id, insight_options, user_context):
    # Direct file access
    parsed_data = await file_parser_service.parse_file(file_id)
    
    # Generate insights from parsed data
    insights = await self._generate(parsed_data, insight_options)
    return insights
```

**New Pattern (DIL SDK - Semantic Data):**
```python
async def generate_insights(self, file_id, insight_options, user_context):
    # ✅ Query semantic data
    semantic_data = await self.dil_sdk.data.query_semantic(
        query="",
        filters={"file_id": file_id},
        user_context=user_context
    )
    
    # Vector search for similar data
    similar_data = await self.dil_sdk.data.vector_search(
        query_vector=semantic_data[0].get("embedding"),
        top_k=10,
        filters={},
        user_context=user_context
    )
    
    # Generate insights from semantic data
    insights = await self._generate_from_semantic_data(
        semantic_data=semantic_data,
        similar_data=similar_data,
        insight_options=insight_options
    )
    
    return insights
```

**Key Changes:**
- ✅ Use semantic data for insights
- ✅ Use vector search for cross-file insights
- ✅ Enable semantic-first insights generation

### DataInsightsQueryService

**Current Pattern:**
```python
async def process_query(self, query, analysis_id, cached_analysis, user_context):
    # Query cached analysis (from direct file access)
    result = await self._execute_query(query, cached_analysis)
    return result
```

**New Pattern (DIL SDK - Semantic Queries):**
```python
async def process_query(self, query, analysis_id, cached_analysis, user_context):
    # ✅ Query semantic data layer
    semantic_results = await self.dil_sdk.data.query_semantic(
        query=query,
        filters={"analysis_id": analysis_id},
        user_context=user_context
    )
    
    # Vector search for semantic similarity
    query_embedding = await self.dil_sdk.data.embed_content(
        content=query,
        embedding_type="text",
        user_context=user_context
    )
    
    similar_results = await self.dil_sdk.data.vector_search(
        query_vector=query_embedding.get("embedding"),
        top_k=10,
        filters={},
        user_context=user_context
    )
    
    # Execute query on semantic data
    result = await self._execute_semantic_query(
        query=query,
        semantic_results=semantic_results,
        similar_results=similar_results
    )
    
    return result
```

**Key Changes:**
- ✅ Query semantic data layer (not cached analysis)
- ✅ Use vector search for semantic similarity
- ✅ Enable semantic-first query processing

---

## 5. Migration Checklist

### For Each Service:

- [ ] **Initialize DIL SDK**
  - [ ] Get DIL Foundation from DI Container
  - [ ] Get DIL SDK instance
  - [ ] Store in service instance

- [ ] **Replace Direct Infrastructure Access**
  - [ ] Replace `file_management_abstraction` calls with `dil.data.upload_file()`
  - [ ] Replace `file_parser_service` calls with `dil.data.parse_file()`
  - [ ] Replace `hf_inference_agent` calls with `dil.data.embed_content()`
  - [ ] Replace `content_metadata_abstraction` calls with `dil.data.store_semantic()`

- [ ] **Replace File Queries with Semantic Queries**
  - [ ] Replace direct file access with `dil.data.query_semantic()`
  - [ ] Replace column name queries with `dil.data.query_by_semantic_id()`
  - [ ] Add vector search for similarity queries

- [ ] **Add Lineage Tracking**
  - [ ] Record lineage for all data transformations
  - [ ] Use `dil.governance.record_lineage()`

- [ ] **Add Data Classification**
  - [ ] Classify data as "platform" or "client"
  - [ ] Use `dil.governance.classify_data()`

- [ ] **Update Tests**
  - [ ] Mock DIL SDK in unit tests
  - [ ] Test semantic data queries
  - [ ] Test lineage tracking
  - [ ] Test data classification

---

## 6. Common Patterns

### Pattern 1: Upload → Parse → Embed → Store

```python
# Upload
file_metadata = await dil.data.upload_file(file_data, filename, metadata, user_context)

# Parse
parse_result = await dil.data.parse_file(file_metadata["file_id"], parse_options, user_context)

# Embed
embeddings = await dil.data.embed_content(parse_result, embedding_type, user_context)

# Store
await dil.data.store_semantic(content_id, embeddings, semantic_graph, correlation_map, user_context)

# Record lineage
await dil.governance.record_lineage(file_id, content_id, "semantic_processing", user_context)
```

### Pattern 2: Query Semantic Data

```python
# Query by file_id
semantic_data = await dil.data.query_semantic("", {"file_id": file_id}, user_context)

# Query by semantic_id
metric_data = await dil.data.query_by_semantic_id("revenue_metric_v1", user_context)

# Vector search
similar_data = await dil.data.vector_search(query_vector, top_k=10, {}, user_context)
```

### Pattern 3: Hybrid Data Processing

```python
# Process structured
structured_embeddings = await dil.data.embed_content(columns, "metadata", user_context)

# Process unstructured
unstructured_graph = await dil.data.embed_content(text, "entity", user_context)

# Generate correlation map
correlation_map = await generate_correlation_map(structured_embeddings, unstructured_graph)

# Store all
await dil.data.store_semantic(content_id, structured_embeddings, unstructured_graph, correlation_map, user_context)
```

---

## 7. Testing Strategy

### Unit Tests

```python
# Mock DIL SDK
from unittest.mock import AsyncMock, MagicMock

class TestDataAnalyzerService:
    async def test_analyze_data_uses_dil_sdk(self):
        # Mock DIL SDK
        mock_dil_sdk = MagicMock()
        mock_dil_sdk.data.query_semantic = AsyncMock(return_value=[...])
        mock_dil_sdk.data.get_semantic_graph = AsyncMock(return_value={...})
        
        # Test service
        service = DataAnalyzerService(...)
        service.dil_sdk = mock_dil_sdk
        
        result = await service.analyze_data(file_id, options, user_context)
        
        # Verify DIL SDK called
        mock_dil_sdk.data.query_semantic.assert_called_once()
        mock_dil_sdk.data.get_semantic_graph.assert_called_once()
```

### Integration Tests

```python
# Test with real DIL SDK
async def test_analyze_data_integration(self):
    # Initialize DIL Foundation
    dil_foundation = await initialize_dil_foundation()
    dil_sdk = dil_foundation.get_sdk()
    
    # Test service with real DIL SDK
    service = DataAnalyzerService(...)
    service.dil_sdk = dil_sdk
    
    result = await service.analyze_data(file_id, options, user_context)
    
    # Verify semantic data returned
    assert result["semantic_data"] is not None
```

---

## 8. FAQ

### Q: Do I need to change all my service methods?

**A:** Yes, but incrementally. Start with data access methods, then add lineage tracking, then add classification.

### Q: What if DIL SDK doesn't have a method I need?

**A:** Request it from DIL Foundation team. DIL SDK should cover all data operations.

### Q: Can I still use direct infrastructure access?

**A:** No. All data operations must go through DIL SDK for governance and lineage tracking.

### Q: How do I handle errors from DIL SDK?

**A:** DIL SDK returns structured error responses. Handle them the same way you handle service errors.

### Q: What about backward compatibility?

**A:** We're using "break and fix" approach. Update services to use DIL SDK, fix what breaks.

---

## 9. Support

**Questions?** Contact:
- DIL Foundation Team: For DIL SDK API questions
- Data Steward Team: For governance questions
- Architecture Team: For integration questions

---

## Conclusion

**Key Takeaways:**
1. ✅ All data operations go through DIL SDK
2. ✅ Services use semantic data, not raw client files
3. ✅ Record lineage for all transformations
4. ✅ Classify data as platform or client
5. ✅ Test with mocked and real DIL SDK

**Next Steps:**
1. Review this guide
2. Identify services to refactor
3. Start with Content services (FileParserService, ContentAnalysisOrchestrator)
4. Then Insights services (DataAnalyzerService, MetricsCalculatorService, etc.)
5. Test thoroughly after each service


