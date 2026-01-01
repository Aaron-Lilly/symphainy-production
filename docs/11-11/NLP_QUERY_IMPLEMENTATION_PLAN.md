# NLP Query Processing - Implementation Plan

**Date:** November 11, 2025  
**Purpose:** Detailed plan for implementing natural language query processing for Insights Pillar

---

## 🎯 Overview

Enable users to ask natural language questions about their analysis results and receive structured responses (text, tables, or charts).

**Example Queries:**
- "What were the top 3 revenue drivers in Q3?"
- "Show me a chart of profit margins by quarter"
- "Which metrics are trending downward?"
- "Summarize the key risks identified"
- "What recommendations have high priority?"

---

## 📋 Current State

### **Backend Placeholder:**
```python
# symphainy-platform/.../insights_orchestrator.py
async def query_analysis_results(
    self,
    query: str,
    analysis_id: str,
    query_type: Optional[str] = None
) -> Dict[str, Any]:
    # TODO: Implement actual NLP query processing
    return {
        "success": True,
        "query_id": query_id,
        "result": {
            "type": "text",
            "explanation": f"Query processed: '{query}'. NLP query processing will be implemented in future iteration.",
            "data": None
        }
    }
```

### **Frontend Integration:**
- Insights Liaison Agent configured in side panel
- API client method `queryAnalysisResults()` ready
- No UI for manual query input yet (agent handles it)

---

## 🏗️ Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ NLP Query Processing Pipeline                                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │ 1. Query Analysis (Intent Detection)                         │        │
│  │                                                               │        │
│  │  Input: "What were the top 3 revenue drivers in Q3?"         │        │
│  │                                                               │        │
│  │  Parser analyzes:                                             │        │
│  │  • Intent: top_n_query                                        │        │
│  │  • Entities: ["3", "revenue drivers", "Q3"]                  │        │
│  │  • Output Type: table                                         │        │
│  │  • Section: tabular/insights                                  │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                          ↓                                                │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │ 2. Context Retrieval                                          │        │
│  │                                                               │        │
│  │  • Fetch cached analysis by ID                               │        │
│  │  • Load relevant sections based on intent:                   │        │
│  │    - Textual summary                                          │        │
│  │    - Tabular data                                             │        │
│  │    - Visualizations                                           │        │
│  │    - Insights list                                            │        │
│  │    - AAR analysis (if applicable)                            │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                          ↓                                                │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │ 3. Query Execution                                            │        │
│  │                                                               │        │
│  │  Based on intent:                                             │        │
│  │  • top_n_query → Sort & filter tabular data                  │        │
│  │  • chart_request → Generate chart from data                  │        │
│  │  • trend_analysis → Analyze time-series patterns             │        │
│  │  • filter_query → Filter insights by criteria                │        │
│  │  • summarize → Aggregate across all sections                 │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                          ↓                                                │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │ 4. Response Generation                                        │        │
│  │                                                               │        │
│  │  Format:                                                      │        │
│  │  {                                                            │        │
│  │    type: "table",                                             │        │
│  │    data: [...top 3 items...],                                │        │
│  │    explanation: "The top 3 revenue drivers in Q3 were...",   │        │
│  │    follow_up_suggestions: [...]                              │        │
│  │  }                                                            │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Implementation Approaches

### **Option A: Simple Rule-Based (Recommended for Phase 1)**

**Pros:**
- Fast (no API calls)
- Predictable behavior
- No external dependencies
- Covers 70% of expected queries
- Can be built in 1-2 days

**Cons:**
- Limited to predefined patterns
- Doesn't handle varied phrasing well
- Requires manual pattern maintenance

**Implementation:**

```python
# symphainy-platform/backend/business_enablement/enabling_services/nlp_query_processor/
# nlp_query_processor.py

import re
from typing import Dict, Any, List, Optional, Tuple

class NLPQueryProcessor:
    """Rule-based NLP query processor for analytics queries."""
    
    # Query pattern definitions
    QUERY_PATTERNS = {
        # Top N queries
        r"(?:top|highest|best|largest)\s+(\d+)\s+(.+?)(?:\s+in\s+(.+))?$": "top_n_query",
        r"(?:bottom|lowest|worst|smallest)\s+(\d+)\s+(.+?)(?:\s+in\s+(.+))?$": "bottom_n_query",
        
        # Chart requests
        r"(?:show|display|create|generate|plot)\s+(?:me\s+)?(?:a\s+)?chart\s+(?:of\s+)?(.+)": "chart_request",
        r"(?:visualize|graph)\s+(.+)": "chart_request",
        
        # Trend analysis
        r"(?:what|which).*trend.*(?:up|down|increasing|decreasing)": "trend_analysis",
        r"(?:show|find).*(?:trends|patterns)\s+(?:in\s+)?(.+)": "trend_analysis",
        
        # Filter/search queries
        r"(?:show|find|get|list)\s+(?:all\s+)?(.+?)\s+(?:where|with|that have)\s+(.+)": "filter_query",
        r"which\s+(.+?)\s+(?:have|has)\s+(.+)": "filter_query",
        
        # Summarize
        r"(?:summarize|summary of)\s+(.+)": "summarize_section",
        r"(?:what are|what's)\s+(?:the\s+)?(?:key|main|important)\s+(.+)": "summarize_section",
        
        # Specific metric lookup
        r"(?:what is|what's|show me)\s+(?:the\s+)?(.+?)\s+(?:for|in)\s+(.+)": "metric_lookup",
        
        # Comparison
        r"(?:compare|comparison of)\s+(.+?)\s+(?:and|vs|versus)\s+(.+)": "comparison_query",
        
        # Recommendations
        r"(?:what|which).*recommendations.*high.*priority": "high_priority_recommendations",
        r"(?:show|list|get).*recommendations": "all_recommendations",
        
        # AAR specific
        r"(?:what|which).*(?:lessons|lessons learned)": "aar_lessons",
        r"(?:what|which).*risks": "aar_risks",
        r"(?:show|list).*timeline": "aar_timeline",
    }
    
    def __init__(self):
        """Initialize the NLP query processor."""
        pass
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse a natural language query into intent and entities.
        
        Args:
            query: User's natural language query
        
        Returns:
            Dict with:
            - intent: Query intent type
            - entities: Extracted entities (numbers, metrics, filters)
            - confidence: How confident we are in the parsing (0-1)
        """
        query_lower = query.lower().strip()
        
        # Try to match against known patterns
        for pattern, intent in self.QUERY_PATTERNS.items():
            match = re.search(pattern, query_lower, re.IGNORECASE)
            if match:
                entities = list(match.groups())
                return {
                    "intent": intent,
                    "entities": [e for e in entities if e],  # Remove None values
                    "confidence": 0.9,
                    "original_query": query
                }
        
        # Fallback: general question
        return {
            "intent": "general_question",
            "entities": [],
            "confidence": 0.5,
            "original_query": query
        }
    
    def execute_query(
        self,
        parsed_query: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a parsed query against analysis data.
        
        Args:
            parsed_query: Output from parse_query()
            analysis: Full analysis response (from cache)
        
        Returns:
            Query result with type, data, and explanation
        """
        intent = parsed_query["intent"]
        entities = parsed_query["entities"]
        
        # Route to appropriate handler
        if intent == "top_n_query":
            return self._handle_top_n_query(entities, analysis)
        elif intent == "bottom_n_query":
            return self._handle_bottom_n_query(entities, analysis)
        elif intent == "chart_request":
            return self._handle_chart_request(entities, analysis)
        elif intent == "trend_analysis":
            return self._handle_trend_analysis(entities, analysis)
        elif intent == "filter_query":
            return self._handle_filter_query(entities, analysis)
        elif intent == "summarize_section":
            return self._handle_summarize(entities, analysis)
        elif intent == "metric_lookup":
            return self._handle_metric_lookup(entities, analysis)
        elif intent == "comparison_query":
            return self._handle_comparison(entities, analysis)
        elif intent == "high_priority_recommendations":
            return self._handle_priority_recommendations(True, analysis)
        elif intent == "all_recommendations":
            return self._handle_priority_recommendations(False, analysis)
        elif intent == "aar_lessons":
            return self._handle_aar_section("lessons_learned", analysis)
        elif intent == "aar_risks":
            return self._handle_aar_section("risks", analysis)
        elif intent == "aar_timeline":
            return self._handle_aar_section("timeline", analysis)
        else:
            return self._handle_general_question(parsed_query["original_query"], analysis)
    
    # ====================================================================
    # QUERY HANDLERS
    # ====================================================================
    
    def _handle_top_n_query(self, entities: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle 'top N' queries."""
        try:
            n = int(entities[0]) if entities else 3
            metric = entities[1] if len(entities) > 1 else "items"
            
            # Extract tabular data
            tabular = analysis.get("summary", {}).get("tabular", {})
            if not tabular:
                return {
                    "type": "text",
                    "explanation": f"No tabular data available for '{metric}' analysis.",
                    "data": None
                }
            
            rows = tabular.get("rows", [])
            columns = tabular.get("columns", [])
            
            # TODO: Smart column matching based on metric name
            # For now, assume last column is the value to sort by
            if rows and len(rows[0]) > 1:
                sorted_rows = sorted(rows, key=lambda row: row[-1] if isinstance(row[-1], (int, float)) else 0, reverse=True)
                top_n_rows = sorted_rows[:n]
                
                return {
                    "type": "table",
                    "data": {
                        "columns": columns,
                        "rows": top_n_rows
                    },
                    "explanation": f"The top {n} {metric} are shown above, sorted by value.",
                    "confidence": 0.85
                }
            else:
                return {
                    "type": "text",
                    "explanation": f"Unable to determine top {n} {metric} from available data.",
                    "data": None
                }
        
        except Exception as e:
            return {"type": "text", "explanation": f"Error processing top N query: {str(e)}", "data": None}
    
    def _handle_chart_request(self, entities: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle chart generation requests."""
        try:
            metric = entities[0] if entities else "data"
            
            # Check if visualizations already exist
            visualizations = analysis.get("summary", {}).get("visualizations", [])
            if visualizations:
                # Return existing visualization
                viz = visualizations[0]
                return {
                    "type": "chart",
                    "data": viz,
                    "explanation": f"Chart showing {metric} (from existing visualizations).",
                    "confidence": 0.9
                }
            
            # Generate new chart from tabular data
            tabular = analysis.get("summary", {}).get("tabular", {})
            if not tabular:
                return {
                    "type": "text",
                    "explanation": f"No data available to generate chart for '{metric}'.",
                    "data": None
                }
            
            # Create simple bar chart from tabular data
            rows = tabular.get("rows", [])
            columns = tabular.get("columns", [])
            
            if rows and columns:
                chart_data = []
                for row in rows[:10]:  # Limit to 10 items for clarity
                    chart_data.append({
                        "name": str(row[0]),
                        "value": row[-1] if isinstance(row[-1], (int, float)) else 0
                    })
                
                chart_spec = {
                    "visualization_id": f"query_viz_{hash(metric) % 10000}",
                    "chart_type": "bar",
                    "library": "recharts",
                    "title": f"{metric.title()} Chart",
                    "rationale": f"Bar chart generated from query about {metric}",
                    "chart_data": chart_data,
                    "x_axis_key": "name",
                    "data_key": "value",
                    "colors": ["#3b82f6"]
                }
                
                return {
                    "type": "chart",
                    "data": chart_spec,
                    "explanation": f"Generated bar chart showing {metric}.",
                    "confidence": 0.8
                }
            
            return {
                "type": "text",
                "explanation": f"Insufficient data to generate chart for '{metric}'.",
                "data": None
            }
        
        except Exception as e:
            return {"type": "text", "explanation": f"Error generating chart: {str(e)}", "data": None}
    
    def _handle_summarize(self, entities: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle summarization requests."""
        section = entities[0] if entities else "analysis"
        
        # Return textual summary
        textual_summary = analysis.get("summary", {}).get("textual", "No summary available.")
        
        return {
            "type": "text",
            "data": None,
            "explanation": textual_summary,
            "confidence": 0.95
        }
    
    def _handle_priority_recommendations(self, high_priority_only: bool, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle recommendation queries."""
        insights = analysis.get("insights", [])
        
        recommendations = []
        for insight in insights:
            recs = insight.get("recommendations", [])
            for rec in recs:
                recommendations.append({
                    "insight_type": insight.get("type"),
                    "recommendation": rec,
                    "confidence": insight.get("confidence", 0.0)
                })
        
        if high_priority_only:
            # Filter to high confidence recommendations
            recommendations = [r for r in recommendations if r["confidence"] > 0.8]
        
        if not recommendations:
            return {
                "type": "text",
                "explanation": "No recommendations found in the analysis.",
                "data": None
            }
        
        return {
            "type": "table",
            "data": {
                "columns": ["Insight Type", "Recommendation", "Confidence"],
                "rows": [[r["insight_type"], r["recommendation"], f"{r['confidence']*100:.0f}%"] for r in recommendations]
            },
            "explanation": f"Found {len(recommendations)} recommendation{'s' if len(recommendations) != 1 else ''}.",
            "confidence": 0.9
        }
    
    def _handle_aar_section(self, section: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AAR-specific queries."""
        aar = analysis.get("aar_analysis", {})
        
        if not aar:
            return {
                "type": "text",
                "explanation": "No AAR analysis available. Enable AAR mode when analyzing unstructured content.",
                "data": None
            }
        
        section_data = aar.get(section, [])
        
        if not section_data:
            return {
                "type": "text",
                "explanation": f"No {section.replace('_', ' ')} found in AAR analysis.",
                "data": None
            }
        
        # Format as table
        if section == "lessons_learned":
            return {
                "type": "table",
                "data": {
                    "columns": ["Category", "Description", "Importance"],
                    "rows": [[l["category"], l["description"], l["importance"]] for l in section_data]
                },
                "explanation": f"Found {len(section_data)} lesson{'s' if len(section_data) != 1 else ''} learned.",
                "confidence": 0.95
            }
        elif section == "risks":
            return {
                "type": "table",
                "data": {
                    "columns": ["Category", "Description", "Severity"],
                    "rows": [[r["category"], r["description"], r["severity"]] for r in section_data]
                },
                "explanation": f"Identified {len(section_data)} risk{'s' if len(section_data) != 1 else ''}.",
                "confidence": 0.95
            }
        elif section == "timeline":
            return {
                "type": "table",
                "data": {
                    "columns": ["Timestamp", "Event", "Type"],
                    "rows": [[t["timestamp"], t["event"], t.get("event_type", "N/A")] for t in section_data]
                },
                "explanation": f"Timeline contains {len(section_data)} event{'s' if len(section_data) != 1 else ''}.",
                "confidence": 0.95
            }
        
        return {
            "type": "text",
            "explanation": f"AAR {section.replace('_', ' ')}: {section_data}",
            "data": section_data
        }
    
    def _handle_general_question(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general questions (fallback)."""
        # Return textual summary as best effort
        textual_summary = analysis.get("summary", {}).get("textual", "")
        
        return {
            "type": "text",
            "explanation": f"I understand you asked: '{query}'. Here's the analysis summary:\n\n{textual_summary}",
            "data": None,
            "confidence": 0.5
        }
    
    # Additional handlers for other intents...
    def _handle_bottom_n_query(self, entities: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
        # Similar to top_n but reverse sort
        pass
    
    def _handle_trend_analysis(self, entities: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
        # Analyze trends in time-series data
        pass
    
    def _handle_filter_query(self, entities: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
        # Filter insights/data by criteria
        pass
    
    def _handle_metric_lookup(self, entities: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
        # Look up specific metric value
        pass
    
    def _handle_comparison(self, entities: List[str], analysis: Dict[str, Any]) -> Dict[str, Any]:
        # Compare two metrics/entities
        pass
    
    def generate_follow_up_suggestions(
        self,
        intent: str,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate follow-up query suggestions based on intent and data."""
        suggestions = []
        
        # Base suggestions
        if analysis.get("summary", {}).get("tabular"):
            suggestions.append("What are the top 5 items by value?")
        
        if analysis.get("summary", {}).get("visualizations"):
            suggestions.append("Show me a chart of the key metrics")
        
        if analysis.get("insights"):
            suggestions.append("What recommendations do you have?")
        
        if analysis.get("aar_analysis"):
            suggestions.extend([
                "Show me the lessons learned",
                "What risks were identified?",
                "Display the timeline"
            ])
        
        return suggestions[:3]  # Return top 3
```

---

## 🔧 Integration with Orchestrator

**File:** `insights_orchestrator.py`

```python
from backend.business_enablement.enabling_services.nlp_query_processor.nlp_query_processor import NLPQueryProcessor

class InsightsOrchestrator:
    def __init__(self, ...):
        # ...
        self.nlp_processor = NLPQueryProcessor()
    
    async def query_analysis_results(
        self,
        query: str,
        analysis_id: str,
        query_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Query analysis results using natural language."""
        try:
            # 1. Get cached analysis
            analysis = await self.get_analysis_results(analysis_id)
            if not analysis.get("success"):
                return {
                    "success": False,
                    "error": "Analysis not found",
                    "query_id": f"query_{int(datetime.utcnow().timestamp())}"
                }
            
            analysis_data = analysis.get("analysis", {})
            
            # 2. Parse query
            parsed_query = self.nlp_processor.parse_query(query)
            
            # 3. Execute query
            result = self.nlp_processor.execute_query(parsed_query, analysis_data)
            
            # 4. Generate follow-ups
            follow_ups = self.nlp_processor.generate_follow_up_suggestions(
                parsed_query["intent"],
                analysis_data
            )
            
            # 5. Return response
            query_id = f"query_{int(datetime.utcnow().timestamp())}_{analysis_id[:8]}"
            
            return {
                "success": True,
                "query_id": query_id,
                "result": result,
                "follow_up_suggestions": follow_ups,
                "metadata": {
                    "intent": parsed_query["intent"],
                    "confidence": parsed_query["confidence"],
                    "analysis_id": analysis_id
                }
            }
        
        except Exception as e:
            self.logger.error(f"Query processing failed: {e}")
            return {
                "success": False,
                "error": "Query processing failed",
                "error_details": str(e),
                "query_id": f"query_{int(datetime.utcnow().timestamp())}"
            }
```

---

## 📊 Implementation Plan

### **Phase 1: Core Infrastructure (2-3 days)**

**Tasks:**
1. Create `NLPQueryProcessor` class
2. Implement query pattern matching (15-20 patterns)
3. Implement core handlers:
   - top_n_query
   - chart_request
   - summarize_section
   - filter_query
   - aar_sections
4. Integrate with orchestrator
5. Add unit tests for parser and handlers

**Deliverable:** Working rule-based NLP processor

### **Phase 2: Testing & Refinement (1-2 days)**

**Tasks:**
1. Test with real analysis data
2. Add more query patterns based on usage
3. Improve entity extraction
4. Add error handling for edge cases
5. Test with Insights Liaison Agent

**Deliverable:** Production-ready NLP processor

### **Phase 3: Enhancements (Future)**

**Tasks:**
1. Add LLM fallback for unmatched queries
2. Implement query history/caching
3. Add query suggestions based on analysis type
4. Implement advanced analytics (correlations, predictions)

**Deliverable:** Enhanced NLP capabilities

---

## 🧪 Testing Strategy

### **Unit Tests:**
```python
def test_parse_top_n_query():
    processor = NLPQueryProcessor()
    result = processor.parse_query("What are the top 5 revenue drivers?")
    assert result["intent"] == "top_n_query"
    assert result["entities"] == ["5", "revenue drivers"]

def test_execute_top_n_query():
    analysis = {...mock analysis data...}
    parsed = {"intent": "top_n_query", "entities": ["3", "metrics"]}
    result = processor.execute_query(parsed, analysis)
    assert result["type"] == "table"
    assert len(result["data"]["rows"]) == 3
```

### **Integration Tests:**
- Test full query flow (parse → execute → response)
- Test with real cached analysis data
- Test error cases (invalid analysis ID, malformed query)

### **User Acceptance Tests:**
- Test with Insights Liaison Agent
- Validate responses are helpful and accurate
- Gather feedback on query patterns that don't work

---

## 📈 Success Metrics

- **Coverage:** 70%+ of user queries matched by patterns
- **Accuracy:** 80%+ of matched queries return useful results
- **Performance:** <100ms per query processing
- **User Satisfaction:** Positive feedback from agent interactions

---

## 🚀 Deployment

**Steps:**
1. Create enabling service directory structure
2. Implement `NLPQueryProcessor` class
3. Add unit tests
4. Integrate with orchestrator
5. Update API documentation
6. Deploy to dev environment
7. Test with agent
8. Deploy to production

**Estimated Timeline:** 3-5 days for Phase 1 & 2

---

## ✅ Next Steps

1. **Review this plan** with stakeholders
2. **Approve approach** (rule-based vs LLM vs hybrid)
3. **Start implementation** of Phase 1
4. **Test with real data** during development
5. **Deploy and monitor** usage patterns

---

**Recommendation:** Start with Phase 1 (rule-based) to get working functionality quickly, then enhance with LLM capabilities in Phase 3 based on actual usage patterns.



