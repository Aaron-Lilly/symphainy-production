"""
AGUI Schema Helpers

Helper functions for creating AGUI schemas for different types of agents.
"""

import sys
import os
from typing import List, Dict, Any
from datetime import datetime

# Using absolute imports from project root

from agentic.agui_schema_registry import AGUISchema, AGUIComponent


def create_data_analyst_agui_schema() -> AGUISchema:
    """Create AGUI schema for data analyst agents."""
    return AGUISchema(
        agent_name="DataAnalystAgent",
        version="1.0",
        description="AGUI schema for data analyst agents providing statistical analysis and insights",
        components=[
            AGUIComponent(
                type="analysis_card",
                title="Analysis Results",
                description="Display statistical analysis results and key insights",
                required=True,
                properties={
                    "data": {"type": "object", "description": "Analysis data and metrics"},
                    "insights": {"type": "array", "description": "Key insights from analysis"},
                    "confidence_score": {"type": "number", "description": "Confidence in results"}
                },
                examples=[
                    {
                        "title": "Sales Analysis Q3",
                        "data": {"revenue": 100000, "growth": 15.5, "customers": 1250},
                        "insights": ["Revenue increased 15.5%", "Customer acquisition up 20%"],
                        "confidence_score": 0.95
                    }
                ]
            ),
            AGUIComponent(
                type="chart_card",
                title="Data Visualizations",
                description="Display charts and graphs for data analysis",
                required=True,
                properties={
                    "chart_type": {"type": "string", "description": "Type of chart (line, bar, pie, etc.)"},
                    "data": {"type": "object", "description": "Chart data"},
                    "options": {"type": "object", "description": "Chart configuration options"}
                }
            ),
            AGUIComponent(
                type="table_card",
                title="Data Summary",
                description="Display tabular data summary",
                required=False,
                properties={
                    "columns": {"type": "array", "description": "Table column definitions"},
                    "rows": {"type": "array", "description": "Table data rows"},
                    "sorting": {"type": "object", "description": "Sorting configuration"}
                }
            ),
            AGUIComponent(
                type="message_card",
                title="Analysis Communication",
                description="Display analysis messages and recommendations",
                required=True,
                properties={
                    "message": {"type": "string", "description": "Analysis message"},
                    "priority": {"type": "string", "description": "Message priority level"},
                    "recommendations": {"type": "array", "description": "Actionable recommendations"}
                }
            )
        ],
        metadata={
            "agent_type": "data_analyst",
            "capabilities": ["statistical_analysis", "data_visualization", "insights_generation"],
            "created_at": datetime.now().isoformat()
        }
    )


def create_operations_liaison_agui_schema() -> AGUISchema:
    """Create AGUI schema for operations liaison agents."""
    return AGUISchema(
        agent_name="OperationsLiaisonAgent",
        version="1.0",
        description="AGUI schema for operations liaison agents providing workflow and SOP guidance",
        components=[
            AGUIComponent(
                type="workflow_card",
                title="Workflow Management",
                description="Display workflow creation and management tools",
                required=True,
                properties={
                    "workflow_id": {"type": "string", "description": "Unique workflow identifier"},
                    "workflow_data": {"type": "object", "description": "Workflow structure and metadata"},
                    "sop_data": {"type": "object", "description": "SOP structure and metadata"},
                    "conversion_status": {"type": "string", "description": "Status of SOP/Workflow conversion"}
                },
                examples=[
                    {
                        "title": "Customer Onboarding Workflow",
                        "workflow_data": {"nodes": 5, "edges": 4, "complexity": "medium"},
                        "sop_data": {"steps": 8, "sections": 3, "completeness": 0.9},
                        "conversion_status": "completed"
                    }
                ]
            ),
            AGUIComponent(
                type="analysis_card",
                title="Coexistence Analysis",
                description="Display AI-human coexistence analysis and recommendations",
                required=True,
                properties={
                    "data": {"type": "object", "description": "Analysis data and metrics"},
                    "coexistence_blueprint": {"type": "object", "description": "Coexistence blueprint data"},
                    "ai_opportunities": {"type": "array", "description": "AI automation opportunities"},
                    "human_value_points": {"type": "array", "description": "Human value preservation points"},
                    "collaboration_patterns": {"type": "array", "description": "Recommended collaboration patterns"}
                },
                examples=[
                    {
                        "title": "Customer Service Coexistence",
                        "coexistence_blueprint": {"ai_handles": ["routing", "basic_queries"], "human_handles": ["complex_issues", "escalations"]},
                        "ai_opportunities": ["Automated ticket routing", "FAQ responses"],
                        "human_value_points": ["Empathy", "Complex problem solving"],
                        "collaboration_patterns": ["AI pre-screening", "Human escalation"]
                    }
                ]
            ),
            AGUIComponent(
                type="info_card",
                title="Process Optimization",
                description="Display process optimization recommendations and tools",
                required=True,
                properties={
                    "content": {"type": "string", "description": "Process optimization content and information"},
                    "optimization_goals": {"type": "array", "description": "Process optimization objectives"},
                    "bottlenecks": {"type": "array", "description": "Identified process bottlenecks"},
                    "recommendations": {"type": "array", "description": "Optimization recommendations"},
                    "platform_integration": {"type": "object", "description": "Platform-specific integration recommendations"}
                },
                examples=[
                    {
                        "title": "Order Processing Optimization",
                        "optimization_goals": ["Reduce processing time", "Improve accuracy"],
                        "bottlenecks": ["Manual data entry", "Approval delays"],
                        "recommendations": ["Automate data entry", "Streamline approvals"],
                        "platform_integration": {"content_pillar": "Document processing", "insights_pillar": "Performance analytics"}
                    }
                ]
            )
        ]
    )

def create_coexistence_analyzer_agui_schema() -> AGUISchema:
    """Create AGUI schema for coexistence analyzer agents."""
    return AGUISchema(
        agent_name="CoexistenceAnalyzerAgent",
        version="1.0",
        description="AGUI schema for coexistence analyzer agents providing AI-human collaboration analysis",
        components=[
            AGUIComponent(
                type="analysis_card",
                title="Coexistence Analysis",
                description="Display AI-human coexistence analysis results",
                required=True,
                properties={
                    "analysis_results": {"type": "object", "description": "Coexistence analysis data"},
                    "ai_capabilities": {"type": "array", "description": "Identified AI capabilities"},
                    "human_value": {"type": "array", "description": "Human value preservation points"},
                    "collaboration_score": {"type": "number", "description": "Collaboration effectiveness score"}
                },
                examples=[
                    {
                        "title": "Customer Service Coexistence Analysis",
                        "analysis_results": {"automation_potential": 0.7, "human_value": 0.8},
                        "ai_capabilities": ["Natural language processing", "Sentiment analysis"],
                        "human_value": ["Empathy", "Complex problem solving"],
                        "collaboration_score": 0.85
                    }
                ]
            )
        ]
    )

def create_process_optimizer_agui_schema() -> AGUISchema:
    """Create AGUI schema for process optimizer agents."""
    return AGUISchema(
        agent_name="ProcessOptimizerAgent",
        version="1.0",
        description="AGUI schema for process optimizer agents providing workflow optimization recommendations",
        components=[
            AGUIComponent(
                type="optimization_card",
                title="Process Optimization",
                description="Display process optimization recommendations and metrics",
                required=True,
                properties={
                    "optimization_goals": {"type": "array", "description": "Process optimization objectives"},
                    "bottlenecks": {"type": "array", "description": "Identified process bottlenecks"},
                    "recommendations": {"type": "array", "description": "Optimization recommendations"},
                    "efficiency_gain": {"type": "number", "description": "Expected efficiency improvement"}
                },
                examples=[
                    {
                        "title": "Order Processing Optimization",
                        "optimization_goals": ["Reduce processing time", "Improve accuracy"],
                        "bottlenecks": ["Manual data entry", "Approval delays"],
                        "recommendations": ["Automate data entry", "Streamline approvals"],
                        "efficiency_gain": 0.35
                    }
                ]
            )
        ]
    )

def create_business_analyst_agui_schema() -> AGUISchema:
    """Create AGUI schema for business analyst agents."""
    return AGUISchema(
        agent_name="BusinessAnalystAgent",
        version="1.0",
        description="AGUI schema for business analyst agents providing strategic insights and recommendations",
        components=[
            AGUIComponent(
                type="analysis_card",
                title="Business Analysis",
                description="Display business analysis results and strategic insights",
                required=True,
                properties={
                    "data": {"type": "object", "description": "Business analysis data and metrics"},
                    "analysis_type": {"type": "string", "description": "Type of business analysis"},
                    "key_findings": {"type": "array", "description": "Key business findings"},
                    "strategic_implications": {"type": "array", "description": "Strategic implications"}
                }
            ),
            AGUIComponent(
                type="workflow_card",
                title="Analysis Workflow",
                description="Display business analysis workflow status",
                required=True,
                properties={
                    "workflow_id": {"type": "string", "description": "Workflow identifier"},
                    "status": {"type": "string", "description": "Current workflow status"},
                    "progress": {"type": "number", "description": "Workflow progress percentage"}
                }
            ),
            AGUIComponent(
                type="form_card",
                title="Analysis Parameters",
                description="Display form for analysis parameter configuration",
                required=False,
                properties={
                    "fields": {"type": "array", "description": "Form field definitions"},
                    "validation": {"type": "object", "description": "Form validation rules"}
                }
            ),
            AGUIComponent(
                type="message_card",
                title="Business Communication",
                description="Display business insights and recommendations",
                required=True,
                properties={
                    "message": {"type": "string", "description": "Business message"},
                    "stakeholder": {"type": "string", "description": "Target stakeholder"},
                    "recommendations": {"type": "array", "description": "Strategic recommendations"}
                }
            )
        ],
        metadata={
            "agent_type": "business_analyst",
            "capabilities": ["strategic_analysis", "workflow_management", "stakeholder_communication"],
            "created_at": datetime.now().isoformat()
        }
    )


def create_insights_liaison_agui_schema() -> AGUISchema:
    """Create AGUI schema for insights liaison agents."""
    return AGUISchema(
        agent_name="InsightsLiaisonAgent",
        version="1.0",
        description="AGUI schema for insights liaison agents providing conversational interfaces and coordination",
        components=[
            AGUIComponent(
                type="message_card",
                title="Conversation Interface",
                description="Display conversational messages and responses",
                required=True,
                properties={
                    "message": {"type": "string", "description": "Conversation message"},
                    "sender": {"type": "string", "description": "Message sender"},
                    "timestamp": {"type": "string", "description": "Message timestamp"},
                    "conversation_id": {"type": "string", "description": "Conversation identifier"}
                }
            ),
            AGUIComponent(
                type="status_card",
                title="Agent Coordination Status",
                description="Display status of coordinated agents and workflows",
                required=True,
                properties={
                    "status": {"type": "string", "description": "Overall coordination status"},
                    "active_agents": {"type": "array", "description": "List of active agents"},
                    "health_scores": {"type": "object", "description": "Agent health scores"}
                }
            ),
            AGUIComponent(
                type="workflow_card",
                title="Orchestration Workflow",
                description="Display orchestration workflow status",
                required=True,
                properties={
                    "workflow_id": {"type": "string", "description": "Workflow identifier"},
                    "status": {"type": "string", "description": "Workflow status"},
                    "orchestrated_agents": {"type": "array", "description": "List of orchestrated agents"}
                }
            ),
            AGUIComponent(
                type="alert_card",
                title="System Alerts",
                description="Display system alerts and notifications",
                required=False,
                properties={
                    "alert_type": {"type": "string", "description": "Type of alert"},
                    "message": {"type": "string", "description": "Alert message"},
                    "priority": {"type": "string", "description": "Alert priority"},
                    "dismissible": {"type": "boolean", "description": "Whether alert can be dismissed"}
                }
            )
        ],
        metadata={
            "agent_type": "insights_liaison",
            "capabilities": ["conversation_management", "agent_orchestration", "workflow_coordination"],
            "created_at": datetime.now().isoformat()
        }
    )


def create_custom_agui_schema(agent_name: str, capabilities: List[str], 
                            custom_components: List[AGUIComponent] = None) -> AGUISchema:
    """
    Create a custom AGUI schema for an agent.
    
    Args:
        agent_name: Name of the agent
        capabilities: List of agent capabilities
        custom_components: Optional custom components
        
    Returns:
        Custom AGUI schema
    """
    components = custom_components or []
    
    # Add standard components based on capabilities
    if "data_analysis" in capabilities:
        components.append(AGUIComponent(
            type="analysis_card",
            title="Analysis Results",
            description="Display analysis results and insights",
            required=True
        ))
    
    if "workflow" in capabilities:
        components.append(AGUIComponent(
            type="workflow_card",
            title="Workflow Status",
            description="Display workflow execution status",
            required=True
        ))
    
    if "monitoring" in capabilities:
        components.append(AGUIComponent(
            type="status_card",
            title="System Status",
            description="Display system health and status",
            required=True
        ))
    
    # Always include message card for communication
    components.append(AGUIComponent(
        type="message_card",
        title="Agent Communication",
        description="Display agent messages and notifications",
        required=True
    ))
    
    return AGUISchema(
        agent_name=agent_name,
        version="1.0",
        description=f"Custom AGUI schema for {agent_name}",
        components=components,
        metadata={
            "agent_type": "custom",
            "capabilities": capabilities,
            "created_at": datetime.now().isoformat()
        }
    )


def get_agui_schema_for_agent_type(agent_type: str) -> AGUISchema:
    """
    Get AGUI schema for a specific agent type.
    
    Args:
        agent_type: Type of agent (data_analyst, business_analyst, insights_liaison)
        
    Returns:
        AGUI schema for the agent type
    """
    schema_functions = {
        "data_analyst": create_data_analyst_agui_schema,
        "business_analyst": create_business_analyst_agui_schema,
        "insights_liaison": create_insights_liaison_agui_schema
    }
    
    if agent_type in schema_functions:
        return schema_functions[agent_type]()
    else:
        raise ValueError(f"Unknown agent type: {agent_type}. Available types: {list(schema_functions.keys())}")

