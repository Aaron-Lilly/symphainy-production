#!/usr/bin/env python3
"""
AI Mock Responses for Business Enablement Tests

Provides mock LLM responses for testing without making real API calls.
Used in Phase 2 (Component Functionality) and Phase 3 (Integration Tests).

These responses simulate realistic AI behavior for:
- Agent decision-making
- Agent tool selection
- Agent coordination
- Content analysis
- Insights generation
- Operations optimization
"""

from typing import Dict, Any, List, Optional


# ============================================================================
# CONTENT ANALYSIS MOCK RESPONSES
# ============================================================================

def get_content_analysis_response(content: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Mock response for content analysis agent."""
    return {
        "role": "assistant",
        "content": f"I've analyzed the content and identified key themes: data processing, workflow management, and business intelligence. The content appears to be technical documentation with {len(content.split())} words.",
        "tool_calls": [
            {
                "id": "call_001",
                "type": "function",
                "function": {
                    "name": "store_knowledge",
                    "arguments": '{"knowledge_id": "analysis_001", "content": "Analysis complete"}'
                }
            }
        ]
    }


def get_content_processing_response(file_data: bytes, filename: str) -> Dict[str, Any]:
    """Mock response for content processing agent."""
    return {
        "role": "assistant",
        "content": f"I've processed the file {filename} and extracted structured content. The file contains relevant business information that should be stored and analyzed.",
        "tool_calls": [
            {
                "id": "call_002",
                "type": "function",
                "function": {
                    "name": "parse_file",
                    "arguments": f'{{"file_id": "{filename}_001", "format": "auto"}}'
                }
            }
        ]
    }


# ============================================================================
# INSIGHTS GENERATION MOCK RESPONSES
# ============================================================================

def get_insights_analysis_response(data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Mock response for insights analysis agent."""
    return {
        "role": "assistant",
        "content": "Based on the data provided, I've identified several key insights: 1) Performance trends show improvement, 2) There are opportunities for optimization, 3) User engagement is increasing. I recommend generating a detailed insights report.",
        "tool_calls": [
            {
                "id": "call_003",
                "type": "function",
                "function": {
                    "name": "generate_insights",
                    "arguments": '{"insight_type": "trend_analysis", "data_source": "provided_data"}'
                }
            }
        ]
    }


def get_insights_generation_response(request: Dict[str, Any]) -> Dict[str, Any]:
    """Mock response for insights generation."""
    return {
        "role": "assistant",
        "content": "I've generated comprehensive insights based on your request. The insights include trend analysis, correlation findings, and actionable recommendations. These insights are ready for review and can be formatted into a report.",
        "tool_calls": [
            {
                "id": "call_004",
                "type": "function",
                "function": {
                    "name": "create_insights_report",
                    "arguments": '{"report_format": "comprehensive", "include_recommendations": true}'
                }
            }
        ]
    }


# ============================================================================
# OPERATIONS OPTIMIZATION MOCK RESPONSES
# ============================================================================

def get_operations_analysis_response(process_data: Dict[str, Any]) -> Dict[str, Any]:
    """Mock response for operations specialist agent."""
    return {
        "role": "assistant",
        "content": "I've analyzed the operations data and identified several optimization opportunities: 1) Process bottlenecks can be reduced, 2) Automation opportunities exist, 3) Resource allocation can be improved. I recommend creating an SOP and workflow to address these.",
        "tool_calls": [
            {
                "id": "call_005",
                "type": "function",
                "function": {
                    "name": "create_sop",
                    "arguments": '{"sop_type": "process_optimization", "priority": "high"}'
                }
            },
            {
                "id": "call_006",
                "type": "function",
                "function": {
                    "name": "create_workflow",
                    "arguments": '{"workflow_type": "optimization", "steps": ["analyze", "optimize", "implement"]}'
                }
            }
        ]
    }


def get_operations_optimization_response(request: Dict[str, Any]) -> Dict[str, Any]:
    """Mock response for operations optimization."""
    return {
        "role": "assistant",
        "content": "I've completed the operations optimization analysis. The optimization plan includes: 1) Streamlined processes, 2) Automated workflows, 3) Improved resource utilization. An SOP has been created and a workflow has been generated to implement these optimizations.",
        "tool_calls": []
    }


# ============================================================================
# BUSINESS OUTCOMES MOCK RESPONSES
# ============================================================================

def get_business_outcomes_analysis_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mock response for business outcomes specialist agent."""
    return {
        "role": "assistant",
        "content": "I've analyzed the business outcomes data and calculated key metrics: 1) Revenue growth: +15%, 2) Customer satisfaction: 92%, 3) Operational efficiency: +20%. These metrics indicate strong performance. I recommend generating a comprehensive outcomes report.",
        "tool_calls": [
            {
                "id": "call_007",
                "type": "function",
                "function": {
                    "name": "calculate_metrics",
                    "arguments": '{"metrics": ["revenue", "satisfaction", "efficiency"], "timeframe": "quarterly"}'
                }
            },
            {
                "id": "call_008",
                "type": "function",
                "function": {
                    "name": "generate_outcomes_report",
                    "arguments": '{"report_type": "comprehensive", "include_trends": true}'
                }
            }
        ]
    }


# ============================================================================
# MULTI-AGENT COORDINATION MOCK RESPONSES
# ============================================================================

def get_agent_coordination_response(agent_id: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Mock response for agent coordination."""
    return {
        "role": "assistant",
        "content": f"As {agent_id}, I understand the task: {task}. I've reviewed the context from other agents and will coordinate my actions accordingly. I'll use the appropriate tools and share my results with the team.",
        "tool_calls": [
            {
                "id": f"call_{agent_id}_001",
                "type": "function",
                "function": {
                    "name": "coordinate_with_agents",
                    "arguments": f'{{"task": "{task}", "agent_id": "{agent_id}"}}'
                }
            }
        ]
    }


# ============================================================================
# LIAISON AGENT MOCK RESPONSES
# ============================================================================

def get_liaison_agent_response(user_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Mock response for liaison agent (user-facing)."""
    # Determine which specialist to route to
    if "insight" in user_message.lower() or "analyze" in user_message.lower():
        specialist = "insights_specialist_agent"
    elif "operation" in user_message.lower() or "optimize" in user_message.lower():
        specialist = "operations_specialist_agent"
    elif "content" in user_message.lower() or "document" in user_message.lower():
        specialist = "content_processing_agent"
    elif "outcome" in user_message.lower() or "metric" in user_message.lower():
        specialist = "business_outcomes_specialist_agent"
    else:
        specialist = "general_specialist_agent"
    
    return {
        "role": "assistant",
        "content": f"I understand your request: '{user_message}'. I'll route this to the {specialist} who specializes in this type of request. They will analyze your needs and provide a comprehensive solution.",
        "tool_calls": [
            {
                "id": "call_liaison_001",
                "type": "function",
                "function": {
                    "name": "route_to_specialist",
                    "arguments": f'{{"specialist": "{specialist}", "user_message": "{user_message}"}}'
                }
            }
        ]
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_mock_llm_response(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generic mock LLM response based on prompt content."""
    prompt_lower = prompt.lower()
    
    if "content" in prompt_lower or "document" in prompt_lower:
        return get_content_analysis_response(prompt, context)
    elif "insight" in prompt_lower:
        return get_insights_analysis_response({"data": prompt}, context)
    elif "operation" in prompt_lower or "optimize" in prompt_lower:
        return get_operations_analysis_response({"process": prompt})
    elif "outcome" in prompt_lower or "metric" in prompt_lower:
        return get_business_outcomes_analysis_response({"data": prompt})
    else:
        return {
            "role": "assistant",
            "content": f"I understand your request: {prompt}. I'll process this and provide a comprehensive response.",
            "tool_calls": []
        }


def get_mock_tool_response(tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
    """Mock response for tool calls."""
    return {
        "status": "success",
        "result": {
            "tool": tool_name,
            "arguments": tool_args,
            "output": f"Mock result from {tool_name}"
        }
    }

