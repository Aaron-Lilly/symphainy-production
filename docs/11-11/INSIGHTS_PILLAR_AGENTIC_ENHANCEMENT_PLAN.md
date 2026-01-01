# Insights Orchestrator - Agentic Enhancement Plan

**Date**: November 12, 2025  
**Focus**: AI Showcase Pillar - Agents using data science tools without hallucination  
**Principle**: Agents orchestrate data science tools to generate grounded insights

**Architecture**: Agents use **InsightsOrchestrator** methods (which internally call enabling services), NOT old archived pillar services.

---

## 🎯 Core Vision

**Insights Pillar Purpose**: **AI Showcase** - Demonstrate how agents use data science tools to generate insights **without hallucination**

**Key Differentiator**: 
- ✅ Agents use **grounded data science tools** (DataAnalyzer, MetricsCalculator, VisualizationEngine)
- ✅ Agents generate insights from **actual data analysis**, not LLM generation
- ✅ Agents provide **plain English explanations** of data science results
- ✅ Agents enable **"double-click"** exploration of insights

---

## 1. MVP Requirements Analysis

### From MVP Description:
> "Insights pillar starts with a file selection prompt (showing your parsed files) and then section 2 has a formatted text element to provide business analysis of about your file and a secondary (side by side) element that provides either a visual or tabular representation of your data depending on your preferred learning style. **the secondary chatbot (insight liaison) serves as a plain english guide to help you navigate your data and "double click on any initial analysis** (e.g. I see I have a lot of customers who are more than 90 days late. can you show me who those customers are?) and uses the side-by-side elements in Section 2 to display the results. finally once you've gotten your answers/analysis there's a bottom section **"insights summary" which recaps what you've learned on the page and supports it with an appropriate visual (chart or graph) and then provides recommendations based on the insights you've gained**."

### Key Requirements:
1. **Plain English Guide**: Agent explains data science results in business terms
2. **"Double-Click" Exploration**: Agent enables deep-dive queries on insights
3. **Insights Summary**: Agent generates comprehensive summary with recommendations
4. **Visual/Tabular Representation**: Agent orchestrates visualization based on learning style
5. **Business Analysis**: Agent provides business narrative from data analysis

---

## 2. Current State Analysis

### ✅ What We Have
- `InsightsLiaisonAgent` - Basic conversation support
- `DataAnalyzerService` - Data analysis capabilities
- `MetricsCalculatorService` - KPI/metrics calculation
- `VisualizationEngineService` - Chart/visualization creation
- `DataInsightsQueryService` - NLP query processing
- Basic MCP Server with 4 tools

### ❌ What's Missing
- **NO Specialist Agent** - This is the AI showcase pillar!
- **NO Agent Orchestration** - Agents should orchestrate data science tools
- **NO Grounded Insight Generation** - Insights should come from data, not LLM
- **NO "Double-Click" Agent Support** - Agent should enable deep exploration
- **NO Business Narrative Generation** - Agent should explain data science in business terms

---

## 3. Agentic Architecture Design

### 3.1 Specialist Agent Role

**InsightsSpecialistAgent** should be the **Data Science Orchestrator**:

```
User Query: "I see I have a lot of customers who are more than 90 days late. can you show me who those customers are?"

Agent Flow:
1. Understand query intent
2. Use DataAnalyzerService to query actual data
3. Use MetricsCalculatorService to calculate relevant metrics
4. Use VisualizationEngineService to create appropriate visualization
5. Generate plain English explanation of results
6. Provide "double-click" follow-up suggestions
```

### 3.2 Grounded Insight Generation Pattern

**Key Principle**: Insights come from **data analysis**, not LLM generation

```python
# ✅ CORRECT: Agent orchestrates data science tools
analysis_result = await data_analyzer.analyze_data(data_id, analysis_type="descriptive")
metrics_result = await metrics_calculator.calculate_kpi(data_id, kpi_name="late_customers")
visualization = await visualization_engine.create_visualization(data_id, chart_type="bar")
insight_narrative = agent.explain_data_science_results(analysis_result, metrics_result, visualization)

# ❌ WRONG: Agent generates insights from LLM
# insight = await llm.generate_insight(prompt)  # NO - this is hallucination
```

### 3.3 Agent Capabilities

**InsightsSpecialistAgent should provide:**

1. **Data Science Orchestration**:
   - Orchestrate DataAnalyzer, MetricsCalculator, VisualizationEngine
   - Combine multiple data science results
   - Generate comprehensive analysis

2. **Business Narrative Generation**:
   - Explain data science results in plain English
   - Translate statistical findings to business insights
   - Provide context and implications

3. **"Double-Click" Exploration**:
   - Enable deep-dive queries on insights
   - Generate follow-up analysis suggestions
   - Orchestrate additional data science queries

4. **Insights Summary Generation**:
   - Compile comprehensive insights summary
   - Generate recommendations based on data
   - Create appropriate visualizations

5. **Learning Style Adaptation**:
   - Adapt presentation to user's learning style
   - Generate visual or tabular representations
   - Provide multiple perspectives on same data

---

## 4. Implementation Plan

### Phase 1: Create Insights Specialist Agent (3 hours)

**File**: `insights_orchestrator/agents/insights_specialist_agent.py` (CREATE NEW)

```python
#!/usr/bin/env python3
"""
Insights Specialist Agent

AI Showcase Agent - Demonstrates how agents use data science tools to generate
grounded insights without hallucination.

WHAT: I orchestrate data science tools to generate business insights
HOW: I use DataAnalyzer, MetricsCalculator, and VisualizationEngine to analyze
     data, then explain results in plain English
"""

from backend.business_enablement.protocols.business_specialist_agent_protocol import (
    BusinessSpecialistAgentBase,
    SpecialistCapability
)
from typing import Dict, Any, List, Optional

class InsightsSpecialistAgent(BusinessSpecialistAgentBase):
    """
    Insights Specialist Agent - Data Science Orchestrator
    
    This agent showcases how AI can use data science tools to generate
    grounded insights without hallucination.
    """
    
    def __init__(self, utility_foundation=None, di_container=None):
        super().__init__(
            agent_name="InsightsSpecialistAgent",
            business_domain="insights_analysis",
            specialist_capability=SpecialistCapability.DATA_ANALYSIS,
            utility_foundation=utility_foundation
        )
        self.di_container = di_container
        self.insights_orchestrator = None
    
    def set_orchestrator(self, orchestrator):
        """Set orchestrator reference for MCP tool access."""
        self.insights_orchestrator = orchestrator
    
    async def generate_grounded_insights(
        self,
        data_id: str,
        analysis_options: Dict[str, Any],
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Generate grounded insights by orchestrating data science tools.
        
        This is the CORE capability - agents use data science tools, not LLM generation.
        
        **Architecture**: Uses InsightsOrchestrator methods (which call enabling services),
        NOT old archived pillar services.
        
        Flow:
        1. Use InsightsOrchestrator.calculate_metrics() → calls DataAnalyzerService + MetricsCalculatorService
        2. Use InsightsOrchestrator.generate_insights() → calls DataAnalyzerService + MetricsCalculatorService
        3. Use InsightsOrchestrator.create_visualization() → calls VisualizationEngineService
        4. Generate business narrative from data science results
        5. Provide "double-click" exploration suggestions
        
        Args:
            data_id: Data identifier (file_id or content_metadata_id)
            analysis_options: Analysis configuration
            user_id: User identifier
        
        Returns:
            Comprehensive insights with business narrative
        """
        try:
            # Step 1: Orchestrate data science tools via orchestrator methods
            if not self.insights_orchestrator:
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
            
            # Use orchestrator methods to call data science services
            # (Orchestrator internally calls enabling services)
            analysis_result = await self._orchestrate_data_analysis(data_id, analysis_options)
            metrics_result = await self._orchestrate_metrics_calculation(data_id, analysis_options)
            visualization_result = await self._orchestrate_visualization(data_id, analysis_options)
            
            # Step 2: Generate business narrative from data science results
            business_narrative = self._generate_business_narrative(
                analysis_result,
                metrics_result,
                visualization_result
            )
            
            # Step 3: Generate insights summary
            insights_summary = self._generate_insights_summary(
                analysis_result,
                metrics_result,
                business_narrative
            )
            
            # Step 4: Generate recommendations based on data
            recommendations = self._generate_data_driven_recommendations(
                analysis_result,
                metrics_result
            )
            
            # Step 5: Generate "double-click" exploration suggestions
            exploration_suggestions = self._generate_exploration_suggestions(
                analysis_result,
                metrics_result
            )
            
            return {
                "success": True,
                "insights": {
                    "business_narrative": business_narrative,
                    "insights_summary": insights_summary,
                    "recommendations": recommendations,
                    "exploration_suggestions": exploration_suggestions,
                    "data_science_results": {
                        "analysis": analysis_result,
                        "metrics": metrics_result,
                        "visualization": visualization_result
                    }
                },
                "agent_orchestrated": True,
                "grounded_in_data": True
            }
        except Exception as e:
            self.logger.error(f"❌ Grounded insights generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_double_click_query(
        self,
        query: str,
        analysis_id: str,
        context: Dict[str, Any],
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Process "double-click" query - deep exploration of insights.
        
        Example: "I see I have a lot of customers who are more than 90 days late.
                  can you show me who those customers are?"
        
        **Architecture**: Uses InsightsOrchestrator.query_analysis_results() which internally
        calls DataInsightsQueryService.
        
        Flow:
        1. Understand query intent
        2. Use InsightsOrchestrator.query_analysis_results() → calls DataInsightsQueryService
        3. Generate appropriate visualization/table
        4. Explain results in plain English
        
        Args:
            query: Natural language query
            analysis_id: Analysis identifier
            context: Analysis context
            user_id: User identifier
        
        Returns:
            Query results with visualization and explanation
        """
        try:
            # Use orchestrator method to query data
            # (Orchestrator internally calls DataInsightsQueryService)
            if self.insights_orchestrator:
                query_result = await self.insights_orchestrator.query_analysis_results(
                    query=query,
                    analysis_id=analysis_id,
                    query_type="auto"
                )
                
                # Generate plain English explanation
                explanation = self._explain_query_results(query_result, context)
                
                return {
                    "success": True,
                    "query_result": query_result,
                    "explanation": explanation,
                    "follow_up_suggestions": self._generate_follow_up_suggestions(query, query_result)
                }
            else:
                return {
                    "success": False,
                    "error": "Orchestrator not available"
                }
        except Exception as e:
            self.logger.error(f"❌ Double-click query processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_insights_summary(
        self,
        analysis_results: Dict[str, Any],
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive insights summary with recommendations.
        
        This is the "insights summary" section from MVP requirements.
        
        Args:
            analysis_results: Results from data science analysis
            user_id: User identifier
        
        Returns:
            Insights summary with recommendations and visualization
        """
        try:
            # Extract key findings from data science results
            key_findings = self._extract_key_findings(analysis_results)
            
            # Generate recommendations based on data
            recommendations = self._generate_data_driven_recommendations(
                analysis_results,
                key_findings
            )
            
            # Recommend appropriate visualization
            visualization_recommendation = self._recommend_visualization(
                analysis_results,
                key_findings
            )
            
            return {
                "success": True,
                "summary": {
                    "key_findings": key_findings,
                    "recommendations": recommendations,
                    "visualization_recommendation": visualization_recommendation,
                    "business_impact": self._assess_business_impact(key_findings)
                }
            }
        except Exception as e:
            self.logger.error(f"❌ Insights summary generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Helper methods for data science orchestration
    async def _orchestrate_data_analysis(self, data_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate DataAnalyzerService via InsightsOrchestrator.
        
        Uses orchestrator method which internally calls DataAnalyzerService.
        """
        if self.insights_orchestrator:
            return await self.insights_orchestrator.calculate_metrics(
                resource_id=data_id,
                options={"analysis_type": options.get("analysis_type", "descriptive")}
            )
        return {}
    
    async def _orchestrate_metrics_calculation(self, data_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate MetricsCalculatorService via InsightsOrchestrator.
        
        Uses orchestrator method which internally calls MetricsCalculatorService.
        """
        if self.insights_orchestrator:
            return await self.insights_orchestrator.calculate_metrics(
                resource_id=data_id,
                options=options
            )
        return {}
    
    async def _orchestrate_visualization(self, data_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate VisualizationEngineService via InsightsOrchestrator.
        
        Uses orchestrator method which internally calls VisualizationEngineService.
        """
        if self.insights_orchestrator:
            return await self.insights_orchestrator.create_visualization(
                resource_id=data_id,
                options=options
            )
        return {}
    
    def _generate_business_narrative(
        self,
        analysis_result: Dict[str, Any],
        metrics_result: Dict[str, Any],
        visualization_result: Dict[str, Any]
    ) -> str:
        """Generate plain English business narrative from data science results."""
        # Translate data science results to business language
        # This is where we showcase "no hallucination" - narrative is based on actual data
        pass
    
    def _generate_insights_summary(
        self,
        analysis_result: Dict[str, Any],
        metrics_result: Dict[str, Any],
        business_narrative: str
    ) -> Dict[str, Any]:
        """Generate insights summary from data science results."""
        pass
    
    def _generate_data_driven_recommendations(
        self,
        analysis_result: Dict[str, Any],
        metrics_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on actual data, not LLM generation."""
        pass
    
    def _generate_exploration_suggestions(
        self,
        analysis_result: Dict[str, Any],
        metrics_result: Dict[str, Any]
    ) -> List[str]:
        """Generate "double-click" exploration suggestions."""
        pass
    
    def _explain_query_results(self, query_result: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Explain query results in plain English."""
        pass
    
    def _generate_follow_up_suggestions(self, query: str, query_result: Dict[str, Any]) -> List[str]:
        """Generate follow-up query suggestions."""
        pass
    
    def _extract_key_findings(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key findings from data science results."""
        pass
    
    def _recommend_visualization(self, analysis_results: Dict[str, Any], key_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Recommend appropriate visualization based on data."""
        pass
    
    def _assess_business_impact(self, key_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess business impact of key findings."""
        pass
```

### Phase 2: Initialize Specialist Agent in Orchestrator (30 min)

**File**: `insights_orchestrator.py`

**In `initialize()` method** (after line 163):
```python
# 2. Initialize Specialist Agent (AI Showcase)
from .agents import InsightsSpecialistAgent

self.specialist_agent = await self.initialize_agent(
    InsightsSpecialistAgent,
    "InsightsSpecialistAgent",
    agent_type="specialist",
    capabilities=[
        "data_science_orchestration",
        "grounded_insight_generation",
        "business_narrative_generation",
        "double_click_exploration",
        "insights_summary_generation"
    ],
    required_roles=[],
    specialist_capability=SpecialistCapability.DATA_ANALYSIS
)

# Give specialist agent access to orchestrator (for MCP server access)
if self.specialist_agent and hasattr(self.specialist_agent, 'set_orchestrator'):
    self.specialist_agent.set_orchestrator(self)
```

### Phase 3: Integrate Agent into Key Methods (2 hours)

**Update `analyze_content_for_insights()` method**:

```python
async def analyze_content_for_insights(
    self,
    source_type: str,
    file_id: Optional[str] = None,
    content_metadata_id: Optional[str] = None,
    content_type: str = "structured",
    analysis_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze content for insights (semantic API).
    
    This is the PRIMARY method - showcases agent orchestration of data science tools.
    """
    try:
        # Step 1: Get data identifier
        data_id = file_id if source_type == "file" else content_metadata_id
        
        # Step 2: Generate grounded insights via specialist agent
        if self.specialist_agent and hasattr(self.specialist_agent, 'generate_grounded_insights'):
            try:
                self.logger.info("🤖 Invoking Insights Specialist Agent for grounded insights generation...")
                grounded_insights = await self.specialist_agent.generate_grounded_insights(
                    data_id=data_id,
                    analysis_options=analysis_options or {},
                    user_id=user_id
                )
                
                if grounded_insights.get("success"):
                    self.logger.info("✅ Specialist Agent generated grounded insights successfully")
                    
                    # Format for frontend (3-way summary: Text | Table | Charts)
                    return self._format_insights_for_frontend(grounded_insights)
                else:
                    self.logger.warning("⚠️ Agent generation failed, falling back to direct service calls")
            except Exception as e:
                self.logger.warning(f"⚠️ Agent generation failed: {e}, falling back to direct service calls")
        
        # Fallback: Direct service orchestration (if agent not available)
        return await self._analyze_content_direct(data_id, content_type, analysis_options)
        
    except Exception as e:
        self.logger.error(f"❌ Content analysis for insights failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

**Update `query_analysis_results()` method**:

```python
async def query_analysis_results(
    self,
    query: str,
    analysis_id: str,
    query_type: str = "auto"
) -> Dict[str, Any]:
    """
    Process NLP query on analysis results (semantic API).
    
    This enables "double-click" exploration.
    """
    try:
        # Use specialist agent for "double-click" query processing
        if self.specialist_agent and hasattr(self.specialist_agent, 'process_double_click_query'):
            try:
                self.logger.info(f"🤖 Processing double-click query: {query}")
                query_result = await self.specialist_agent.process_double_click_query(
                    query=query,
                    analysis_id=analysis_id,
                    context={},
                    user_id=user_id
                )
                
                if query_result.get("success"):
                    return query_result
            except Exception as e:
                self.logger.warning(f"⚠️ Agent query processing failed: {e}, falling back to direct service")
        
        # Fallback: Direct DataInsightsQueryService
        return await self.data_insights_query_service.query_analysis(
            query=query,
            analysis_id=analysis_id,
            query_type=query_type
        )
    except Exception as e:
        self.logger.error(f"❌ Query analysis results failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }
```

### Phase 4: Enhance MCP Server (1 hour)

**File**: `insights_mcp_server.py`

**Add tools**:
```python
# Tool 5: Generate Grounded Insights (Agent Orchestration)
self.register_tool(
    name="generate_grounded_insights_tool",
    description="Generate grounded insights by orchestrating data science tools. This showcases how agents use data science without hallucination.",
    handler=self._generate_grounded_insights_tool,
    input_schema={
        "type": "object",
        "properties": {
            "data_id": {"type": "string", "description": "Data identifier"},
            "analysis_options": {"type": "object", "description": "Analysis configuration"}
        },
        "required": ["data_id"]
    }
)

# Tool 6: Process Double-Click Query
self.register_tool(
    name="process_double_click_query_tool",
    description="Process 'double-click' query for deep exploration of insights. Example: 'Show me customers over 90 days late'",
    handler=self._process_double_click_query_tool,
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Natural language query"},
            "analysis_id": {"type": "string", "description": "Analysis identifier"}
        },
        "required": ["query", "analysis_id"]
    }
)

# Tool 7: Generate Insights Summary
self.register_tool(
    name="generate_insights_summary_tool",
    description="Generate comprehensive insights summary with recommendations based on data science results.",
    handler=self._generate_insights_summary_tool,
    input_schema={
        "type": "object",
        "properties": {
            "analysis_results": {"type": "object", "description": "Data science analysis results"}
        },
        "required": ["analysis_results"]
    }
)
```

### Phase 5: Integrate New DataAnalyzerService APIs (1 hour)

**Add methods to orchestrator**:
```python
async def categorize_content(
    self,
    data_id: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Categorize content using DataAnalyzerService."""
    data_analyzer = await self._get_data_analyzer_service()
    if data_analyzer:
        return await data_analyzer.categorize_content(data_id=data_id)
    return {"success": False, "error": "Data Analyzer not available"}

async def assess_content_quality(
    self,
    data_id: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Assess content quality using DataAnalyzerService."""
    data_analyzer = await self._get_data_analyzer_service()
    if data_analyzer:
        return await data_analyzer.assess_content_quality(data_id=data_id)
    return {"success": False, "error": "Data Analyzer not available"}

async def generate_semantic_summary(
    self,
    data_id: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate semantic summary using DataAnalyzerService."""
    data_analyzer = await self._get_data_analyzer_service()
    if data_analyzer:
        return await data_analyzer.generate_semantic_summary(data_id=data_id)
    return {"success": False, "error": "Data Analyzer not available"}
```

---

## 5. Key Principles

### ✅ DO:
- Agent orchestrates data science tools (DataAnalyzer, MetricsCalculator, VisualizationEngine)
- Insights come from actual data analysis, not LLM generation
- Agent explains data science results in plain English
- Agent enables "double-click" exploration
- Agent generates recommendations based on data

### ❌ DON'T:
- Agent does NOT generate insights from LLM (that's hallucination)
- Agent does NOT make up data or statistics
- Agent does NOT skip data science tools

---

## 6. Success Criteria

- ✅ Specialist agent created and initialized
- ✅ Agent orchestrates data science tools
- ✅ Grounded insights generation working
- ✅ "Double-click" query processing working
- ✅ Insights summary generation working
- ✅ Business narrative generation working
- ✅ MCP Server enhanced with agent tools
- ✅ Responses include `agent_orchestrated` and `grounded_in_data` flags

---

## 7. Implementation Timeline

- **Phase 1**: 3 hours (Create specialist agent)
- **Phase 2**: 30 min (Initialize agent)
- **Phase 3**: 2 hours (Integrate into methods)
- **Phase 4**: 1 hour (Enhance MCP Server)
- **Phase 5**: 1 hour (Integrate new APIs)

**Total**: ~7.5 hours

---

## 8. Showcase Value

This implementation will demonstrate:
- ✅ How agents use data science tools (no hallucination)
- ✅ How agents explain complex data in plain English
- ✅ How agents enable interactive exploration
- ✅ How agents generate actionable recommendations
- ✅ How agents adapt to user learning styles

**This is the AI Showcase Pillar!** 🎯

