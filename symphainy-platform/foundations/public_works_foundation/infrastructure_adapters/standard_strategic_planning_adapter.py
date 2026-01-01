#!/usr/bin/env python3
"""
Standard Strategic Planning Adapter

Infrastructure adapter for standard strategic planning using standard libraries.

WHAT (Infrastructure Adapter Role): I provide standard strategic planning capabilities
HOW (Adapter Implementation): I wrap standard libraries for roadmap generation and goal tracking
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging
import uuid

from ..abstraction_contracts.strategic_planning_protocol import StrategicPlanningResult


class StandardStrategicPlanningAdapter:
    """
    Standard Strategic Planning Adapter
    
    Provides standard strategic planning capabilities using built-in libraries.
    """
    
    def __init__(self):
        """Initialize Standard Strategic Planning Adapter."""
        self.logger = logging.getLogger("StandardStrategicPlanningAdapter")
        self.logger.info("🏗️ StandardStrategicPlanningAdapter initialized")
        
        # Roadmap templates
        self.roadmap_templates = {
            "agile": {
                "phases": ["Discovery", "Design", "Development", "Deployment", "Optimization"],
                "duration_weeks": [2, 3, 8, 2, 2],
                "milestones": ["Requirements", "Prototype", "MVP", "Production", "Scale"]
            },
            "waterfall": {
                "phases": ["Planning", "Analysis", "Design", "Implementation", "Testing", "Deployment"],
                "duration_weeks": [4, 6, 8, 12, 4, 2],
                "milestones": ["Project Charter", "Requirements", "Architecture", "Code Complete", "QA Complete", "Go-Live"]
            },
            "hybrid": {
                "phases": ["Foundation", "Iteration", "Integration", "Deployment", "Evolution"],
                "duration_weeks": [3, 6, 4, 2, 4],
                "milestones": ["Setup Complete", "Core Features", "Integration", "Production", "Enhancement"]
            }
        }
    
    async def generate_strategic_roadmap(self, business_context: Dict[str, Any], 
                                        roadmap_type: str = "hybrid") -> StrategicPlanningResult:
        """
        Generate a strategic roadmap based on business context.
        
        Args:
            business_context: Business context and requirements
            roadmap_type: Type of roadmap (agile, waterfall, hybrid)
            
        Returns:
            StrategicPlanningResult: Result of the roadmap generation
        """
        try:
            self.logger.info(f"Generating {roadmap_type} strategic roadmap...")
            
            # Get template for roadmap type
            template = self.roadmap_templates.get(roadmap_type, self.roadmap_templates["hybrid"])
            
            # Extract business context
            objectives = business_context.get("objectives", [])
            timeline = business_context.get("timeline", {})
            budget = business_context.get("budget", 0)
            resources = business_context.get("resources", {})
            
            # Generate roadmap phases
            phases = self._generate_roadmap_phases(template, objectives, timeline)
            
            # Generate milestones
            milestones = self._generate_milestones(template, objectives)
            
            # Generate timeline (pass phases for accurate duration calculation)
            timeline_details = self._generate_timeline_details(template, timeline, phases)
            
            # Generate resource allocation
            resource_allocation = self._generate_resource_allocation(resources, budget, phases)
            
            # Generate success metrics
            success_metrics = self._generate_success_metrics(objectives)
            
            roadmap = {
                "roadmap_id": str(uuid.uuid4()),
                "roadmap_type": roadmap_type,
                "business_name": business_context.get("business_name", "Strategic Initiative"),
                "objectives": objectives,
                "phases": phases,
                "milestones": milestones,
                "timeline": timeline_details,
                "resource_allocation": resource_allocation,
                "success_metrics": success_metrics,
                "created_at": datetime.utcnow().isoformat(),
                "status": "draft"
            }
            
            return StrategicPlanningResult(
                success=True,
                roadmap=roadmap,
                roadmap_id=roadmap["roadmap_id"],
                roadmap_type=roadmap_type,
                phases=phases,
                milestones=milestones,
                timeline=timeline_details,
                resource_allocation=resource_allocation,
                success_metrics=success_metrics,
                metadata={
                    "generation_method": "standard",
                    "template_used": roadmap_type,
                    "objectives_count": len(objectives),
                    "phases_count": len(phases),
                    "generated_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate strategic roadmap: {e}")
            return StrategicPlanningResult(
                success=False,
                roadmap={},
                roadmap_id="",
                roadmap_type=roadmap_type,
                phases=[],
                milestones=[],
                timeline={},
                resource_allocation={},
                success_metrics=[],
                metadata={},
                error=str(e)
            )
    
    async def track_goals(self, goals: List[Dict[str, Any]]) -> StrategicPlanningResult:
        """
        Track progress of strategic goals.
        
        Args:
            goals: List of goals to track
            
        Returns:
            StrategicPlanningResult: Result of goal tracking
        """
        try:
            self.logger.info("Tracking strategic goals...")
            
            # Analyze goal progress
            goal_analysis = self._analyze_goal_progress(goals)
            
            # Generate progress report
            progress_report = self._generate_progress_report(goal_analysis)
            
            # Generate recommendations
            recommendations = self._generate_goal_recommendations(goal_analysis)
            
            return StrategicPlanningResult(
                success=True,
                goal_tracking=goal_analysis,
                progress_report=progress_report,
                recommendations=recommendations,
                metadata={
                    "tracking_method": "standard",
                    "goals_tracked": len(goals),
                    "tracked_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to track goals: {e}")
            return StrategicPlanningResult(
                success=False,
                goal_tracking={},
                progress_report={},
                recommendations=[],
                metadata={},
                error=str(e)
            )
    
    async def analyze_strategic_performance(self, performance_data: Dict[str, Any]) -> StrategicPlanningResult:
        """
        Analyze strategic performance against goals and metrics.
        
        Args:
            performance_data: Performance data and metrics
            
        Returns:
            StrategicPlanningResult: Result of performance analysis
        """
        try:
            self.logger.info("Analyzing strategic performance...")
            
            # Analyze performance metrics
            performance_analysis = self._analyze_performance_metrics(performance_data)
            
            # Generate performance insights
            insights = self._generate_performance_insights(performance_analysis)
            
            # Generate improvement recommendations
            recommendations = self._generate_improvement_recommendations(performance_analysis)
            
            return StrategicPlanningResult(
                success=True,
                performance_analysis=performance_analysis,
                insights=insights,
                recommendations=recommendations,
                metadata={
                    "analysis_method": "standard",
                    "metrics_analyzed": len(performance_data.get("metrics", [])),
                    "analyzed_at": datetime.utcnow().isoformat()
                },
                error=None
            )
            
        except Exception as e:
            self.logger.error(f"❌ Failed to analyze strategic performance: {e}")
            return StrategicPlanningResult(
                success=False,
                performance_analysis={},
                insights=[],
                recommendations=[],
                metadata={},
                error=str(e)
            )
    
    def _generate_roadmap_phases(self, template: Dict[str, Any], objectives: List[str], timeline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate roadmap phases based on template and objectives."""
        phases = []
        template_phases = template.get("phases", [])
        duration_weeks = template.get("duration_weeks", [])
        
        # Adjust phases based on objectives and timeline
        num_objectives = len(objectives)
        timeline_days = timeline.get("timeline_days", 180)
        timeline_weeks = timeline_days / 7
        
        # Dynamic phase generation based on objectives
        if num_objectives <= 2:
            # Simple project - fewer phases
            phases_to_use = template_phases[:3]
            durations_to_use = duration_weeks[:3]
        elif num_objectives <= 4:
            # Medium project - standard phases
            phases_to_use = template_phases
            durations_to_use = duration_weeks
        else:
            # Complex project - more phases
            phases_to_use = template_phases + ["Integration", "Optimization"]
            durations_to_use = duration_weeks + [3, 2]
        
        # Adjust durations based on timeline
        total_template_weeks = sum(durations_to_use)
        if total_template_weeks > timeline_weeks:
            # Scale down durations
            scale_factor = timeline_weeks / total_template_weeks
            durations_to_use = [max(1, int(d * scale_factor)) for d in durations_to_use]
        elif total_template_weeks < timeline_weeks * 0.8:
            # Scale up durations
            scale_factor = (timeline_weeks * 0.8) / total_template_weeks
            durations_to_use = [int(d * scale_factor) for d in durations_to_use]
        
        for i, phase_name in enumerate(phases_to_use):
            # Assign objectives to phases dynamically
            objectives_for_phase = []
            if i < len(objectives):
                objectives_for_phase = [objectives[i]]
            elif i == len(phases_to_use) - 1 and len(objectives) > len(phases_to_use):
                # Last phase gets remaining objectives
                objectives_for_phase = objectives[len(phases_to_use)-1:]
            
            phase = {
                "phase_id": f"phase_{i+1}",
                "name": phase_name,
                "description": f"Execute {phase_name.lower()} activities for: {', '.join(objectives_for_phase) if objectives_for_phase else 'general objectives'}",
                "duration_weeks": durations_to_use[i] if i < len(durations_to_use) else 4,
                "objectives": objectives_for_phase,
                "status": "planned",
                "start_date": None,
                "end_date": None
            }
            phases.append(phase)
        
        return phases
    
    def _generate_milestones(self, template: Dict[str, Any], objectives: List[str]) -> List[Dict[str, Any]]:
        """Generate milestones based on template and objectives."""
        milestones = []
        template_milestones = template.get("milestones", [])
        
        # Adjust milestones based on objectives
        num_objectives = len(objectives)
        
        if num_objectives <= 2:
            # Simple project - fewer milestones
            milestones_to_use = template_milestones[:3]
        elif num_objectives <= 4:
            # Medium project - standard milestones
            milestones_to_use = template_milestones
        else:
            # Complex project - more milestones
            milestones_to_use = template_milestones + ["Integration Complete", "Optimization Complete"]
        
        for i, milestone_name in enumerate(milestones_to_use):
            # Create objective-specific milestone names
            if i < len(objectives):
                milestone_name = f"{milestone_name} - {objectives[i]}"
                success_criteria = objectives[i]
            else:
                success_criteria = f"Complete {milestone_name.lower()}"
            
            milestone = {
                "milestone_id": f"milestone_{i+1}",
                "name": milestone_name,
                "description": f"Complete {milestone_name.lower()}",
                "status": "pending",
                "target_date": None,
                "completed_date": None,
                "success_criteria": success_criteria
            }
            milestones.append(milestone)
        
        return milestones
    
    def _generate_timeline_details(self, template: Dict[str, Any], timeline: Dict[str, Any], phases: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate timeline details based on template and timeline constraints."""
        # Use actual phase durations if provided, otherwise use template
        if phases:
            total_weeks = sum(phase.get("duration_weeks", 4) for phase in phases)
            phase_durations = [phase.get("duration_weeks", 4) for phase in phases]
        else:
            total_weeks = sum(template.get("duration_weeks", []))
            phase_durations = template.get("duration_weeks", [])
        
        start_date = timeline.get("start_date", datetime.utcnow())
        
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        end_date = start_date + timedelta(weeks=total_weeks)
        
        return {
            "total_duration_weeks": total_weeks,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "phases": phase_durations,
            "timeline_type": "standard"
        }
    
    def _generate_resource_allocation(self, resources: Dict[str, Any], budget: float, phases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate resource allocation based on resources and budget."""
        total_weeks = sum(phase.get("duration_weeks", 4) for phase in phases)
        
        return {
            "total_budget": budget,
            "budget_per_week": budget / total_weeks if total_weeks > 0 else 0,
            "resource_requirements": {
                "team_size": resources.get("team_size", 5),
                "skill_requirements": resources.get("skills", ["Project Management", "Technical Development"]),
                "equipment": resources.get("equipment", ["Development Environment", "Testing Tools"])
            },
            "allocation_by_phase": [
                {
                    "phase": phase["name"],
                    "budget_allocation": (phase.get("duration_weeks", 4) / total_weeks) * budget if total_weeks > 0 else 0,
                    "resource_intensity": "high" if phase.get("duration_weeks", 4) > 6 else "medium"
                }
                for phase in phases
            ]
        }
    
    def _generate_success_metrics(self, objectives: List[str]) -> List[Dict[str, Any]]:
        """Generate success metrics based on objectives."""
        metrics = []
        
        for i, objective in enumerate(objectives):
            metric = {
                "metric_id": f"metric_{i+1}",
                "name": f"Objective {i+1} Achievement",
                "description": f"Measure progress toward: {objective}",
                "target_value": 100,
                "current_value": 0,
                "unit": "percentage",
                "status": "tracking"
            }
            metrics.append(metric)
        
        return metrics
    
    def _analyze_goal_progress(self, goals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze progress of strategic goals."""
        total_goals = len(goals)
        completed_goals = sum(1 for goal in goals if goal.get("status") == "completed")
        in_progress_goals = sum(1 for goal in goals if goal.get("status") == "in_progress")
        
        return {
            "total_goals": total_goals,
            "completed_goals": completed_goals,
            "in_progress_goals": in_progress_goals,
            "completion_rate": (completed_goals / total_goals * 100) if total_goals > 0 else 0,
            "on_track_goals": in_progress_goals,
            "at_risk_goals": sum(1 for goal in goals if goal.get("status") == "at_risk")
        }
    
    def _generate_progress_report(self, goal_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate progress report based on goal analysis."""
        return {
            "overall_progress": goal_analysis["completion_rate"],
            "status": "on_track" if goal_analysis["completion_rate"] >= 80 else "needs_attention",
            "key_achievements": f"{goal_analysis['completed_goals']} goals completed",
            "next_priorities": f"{goal_analysis['in_progress_goals']} goals in progress",
            "risk_areas": f"{goal_analysis['at_risk_goals']} goals at risk"
        }
    
    def _generate_goal_recommendations(self, goal_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on goal analysis."""
        recommendations = []
        
        if goal_analysis["completion_rate"] < 50:
            recommendations.append("Accelerate progress on key strategic goals")
        
        if goal_analysis["at_risk_goals"] > 0:
            recommendations.append("Address at-risk goals with additional resources")
        
        if goal_analysis["in_progress_goals"] > 5:
            recommendations.append("Prioritize goals to focus on most critical objectives")
        
        return recommendations
    
    def _analyze_performance_metrics(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics."""
        metrics = performance_data.get("metrics", [])
        
        return {
            "metrics_analyzed": len(metrics),
            "average_performance": sum(metric.get("value", 0) for metric in metrics) / len(metrics) if metrics else 0,
            "top_performers": [metric for metric in metrics if metric.get("value", 0) >= 80],
            "underperformers": [metric for metric in metrics if metric.get("value", 0) < 50]
        }
    
    def _generate_performance_insights(self, performance_analysis: Dict[str, Any]) -> List[str]:
        """Generate performance insights."""
        insights = []
        
        if performance_analysis["average_performance"] >= 80:
            insights.append("Strong overall performance across all metrics")
        elif performance_analysis["average_performance"] >= 60:
            insights.append("Moderate performance with room for improvement")
        else:
            insights.append("Performance below expectations - immediate attention needed")
        
        if len(performance_analysis["top_performers"]) > 0:
            insights.append(f"{len(performance_analysis['top_performers'])} metrics exceeding targets")
        
        if len(performance_analysis["underperformers"]) > 0:
            insights.append(f"{len(performance_analysis['underperformers'])} metrics below target")
        
        return insights
    
    def _generate_improvement_recommendations(self, performance_analysis: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if performance_analysis["average_performance"] < 70:
            recommendations.append("Implement performance improvement initiatives")
        
        if len(performance_analysis["underperformers"]) > 0:
            recommendations.append("Focus on underperforming metrics with targeted interventions")
        
        if len(performance_analysis["top_performers"]) > 0:
            recommendations.append("Leverage best practices from top-performing areas")
        
        return recommendations
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check for the Standard Strategic Planning Adapter.
        
        Returns:
            Dict: Health check result
        """
        try:
            # Test roadmap generation
            test_context = {
                "objectives": ["Test objective"],
                "business_name": "Test Business"
            }
            
            result = await self.generate_strategic_roadmap(test_context, "hybrid")
            
            if result.success and result.roadmap:
                return {"healthy": True, "message": "Standard Strategic Planning Adapter is operational"}
            else:
                return {"healthy": False, "message": f"Standard Strategic Planning Adapter failed test: {result.error}"}
        except Exception as e:
            return {"healthy": False, "message": f"Standard Strategic Planning Adapter health check failed: {str(e)}"}
