#!/usr/bin/env python3
"""
Wave Orchestrator for Insurance Use Case

WHAT: Orchestrates wave-based migration execution with quality gates
HOW: Manages wave definition, candidate selection, execution, and rollback

This orchestrator provides wave-based migration capabilities:
- Wave planning and candidate selection
- Wave execution orchestration
- Quality gate enforcement
- Rollback capabilities
- Progress tracking and reporting
"""

import os
import sys
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../../../../../../../'))

from bases.orchestrator_base import OrchestratorBase


class WaveStatus(str, Enum):
    """Wave status enumeration."""
    PLANNED = "planned"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class WaveOrchestrator(OrchestratorBase):
    """
    Wave Orchestrator for Insurance Use Case.
    
    Manages wave-based migration execution with quality gates and rollback capabilities.
    Integrates with Insurance Migration Orchestrator, Routing Engine, and Policy Tracker.
    """
    
    def __init__(self, delivery_manager):
        """
        Initialize Wave Orchestrator.
        
        Args:
            delivery_manager: Reference to DeliveryManagerService for service access
        """
        super().__init__(
            service_name="WaveOrchestratorService",
            realm_name=delivery_manager.realm_name,
            platform_gateway=delivery_manager.platform_gateway,
            di_container=delivery_manager.di_container,
            business_orchestrator=delivery_manager
        )
        self.delivery_manager = delivery_manager
        self.orchestrator_name = "WaveOrchestrator"
        
        # Enabling services (lazy initialization)
        self._insurance_migration_orchestrator = None
        self._routing_engine_service = None
        self._policy_tracker_orchestrator = None
        self._data_steward = None  # For WAL integration
        
        # Specialist agents (lazy initialization)
        self._wave_planning_agent = None
        
        # Wave storage (in-memory for MVP, will move to State Management later)
        self._waves: Dict[str, Dict[str, Any]] = {}
        
        # MCP Server (initialized in initialize())
        self.mcp_server = None
    
    async def _get_insurance_migration_orchestrator(self):
        """Lazy initialization of Insurance Migration Orchestrator."""
        if self._insurance_migration_orchestrator is None:
            try:
                # Get from Delivery Manager
                orchestrators = self.delivery_manager.get_orchestrators()
                for orchestrator in orchestrators:
                    if hasattr(orchestrator, 'orchestrator_name') and orchestrator.orchestrator_name == "InsuranceMigrationOrchestrator":
                        self._insurance_migration_orchestrator = orchestrator
                        self.logger.info("✅ Insurance Migration Orchestrator discovered")
                        return orchestrator
                
                self.logger.warning("⚠️ Insurance Migration Orchestrator not found")
            except Exception as e:
                self.logger.error(f"❌ Insurance Migration Orchestrator initialization failed: {e}")
                return None
        
        return self._insurance_migration_orchestrator
    
    async def _get_routing_engine_service(self):
        """Lazy initialization of Routing Engine Service."""
        if self._routing_engine_service is None:
            try:
                routing_engine = await self.get_enabling_service("RoutingEngineService")
                if routing_engine:
                    self._routing_engine_service = routing_engine
                    self.logger.info("✅ Routing Engine Service discovered via Curator")
                    return routing_engine
            except Exception as e:
                self.logger.warning(f"⚠️ Routing Engine Service not available: {e}")
        
        return self._routing_engine_service
    
    async def _get_policy_tracker_orchestrator(self):
        """Lazy initialization of Policy Tracker Orchestrator."""
        if self._policy_tracker_orchestrator is None:
            try:
                # Get from Delivery Manager
                orchestrators = self.delivery_manager.get_orchestrators()
                for orchestrator in orchestrators:
                    if hasattr(orchestrator, 'orchestrator_name') and orchestrator.orchestrator_name == "PolicyTrackerOrchestrator":
                        self._policy_tracker_orchestrator = orchestrator
                        self.logger.info("✅ Policy Tracker Orchestrator discovered")
                        return orchestrator
                
                self.logger.warning("⚠️ Policy Tracker Orchestrator not found (may not be initialized yet)")
            except Exception as e:
                self.logger.warning(f"⚠️ Policy Tracker Orchestrator not available: {e}")
        
        return self._policy_tracker_orchestrator
    
    async def _get_data_steward(self):
        """Lazy initialization of Data Steward (for WAL)."""
        if self._data_steward is None:
            try:
                self._data_steward = await self.get_data_steward_api()
                if self._data_steward:
                    self.logger.info("✅ Data Steward discovered for WAL integration")
            except Exception as e:
                self.logger.warning(f"⚠️ Data Steward not available: {e}")
        
        return self._data_steward
    
    async def _get_wave_planning_agent(self):
        """Lazy initialization of Wave Planning Specialist Agent."""
        if self._wave_planning_agent is None:
            try:
                self._wave_planning_agent = await self.get_agent("WavePlanningSpecialist")
                if self._wave_planning_agent:
                    self.logger.debug("✅ Wave Planning Specialist Agent available")
            except Exception as e:
                self.logger.debug(f"Wave Planning Specialist Agent not available: {e}")
        
        return self._wave_planning_agent
    
    # ============================================================================
    # WAVE MANAGEMENT OPERATIONS
    # ============================================================================
    
    async def create_wave(
        self,
        wave_number: int,
        name: str,
        description: str,
        selection_criteria: Dict[str, Any],
        target_system: str,
        scheduled_start: Optional[datetime] = None,
        scheduled_end: Optional[datetime] = None,
        quality_gates: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new migration wave.
        
        Args:
            wave_number: Wave number (0 for clean candidates, 1+ for complex)
            name: Wave name
            description: Wave description
            selection_criteria: Routing rules for wave candidate selection
            target_system: Target system for migration
            scheduled_start: Scheduled start time
            scheduled_end: Scheduled end time
            quality_gates: List of quality gate definitions
            user_context: Optional user context
        
        Returns:
            Wave creation result with wave_id
        """
        # Write to WAL
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.record_wal_entry(
                entry_data={
                    "operation": "create_wave",
                    "wave_number": wave_number,
                    "name": name,
                    "target_system": target_system
                },
                user_context=user_context
            )
        
        try:
            # Get Wave Planning Agent for AI-powered wave planning
            wave_planning_agent = await self._get_wave_planning_agent()
            wave_plan = None
            ai_recommendations = None
            
            if wave_planning_agent:
                try:
                    # Get historical waves for learning
                    historical_waves = list(self._waves.values())
                    
                    # Get AI-powered wave plan
                    plan_result = await wave_planning_agent.plan_wave(
                        selection_criteria=selection_criteria,
                        historical_waves=historical_waves if historical_waves else None,
                        user_context=user_context
                    )
                    
                    if plan_result.get("success"):
                        wave_plan = plan_result.get("wave_plan", {})
                        ai_recommendations = wave_plan.get("recommendations", [])
                        
                        # Use AI-recommended quality gates if not provided
                        if not quality_gates and wave_plan.get("quality_gate_recommendations"):
                            quality_gates = wave_plan.get("quality_gate_recommendations")
                            self.logger.info(f"✅ Using AI-recommended quality gates: {len(quality_gates)} gates")
                        
                        self.logger.info(f"✅ Wave plan generated: Risk={wave_plan.get('risk_assessment', {}).get('risk_level', 'unknown')}, Confidence={wave_plan.get('confidence', 0.0):.2f}")
                except Exception as e:
                    self.logger.debug(f"Wave planning agent not available: {e}")
            
            wave_id = str(uuid.uuid4())
            
            wave = {
                "wave_id": wave_id,
                "wave_number": wave_number,
                "name": name,
                "description": description,
                "selection_criteria": selection_criteria,
                "target_system": target_system,
                "scheduled_start": scheduled_start.isoformat() if scheduled_start else None,
                "scheduled_end": scheduled_end.isoformat() if scheduled_end else None,
                "status": WaveStatus.PLANNED.value,
                "policies": [],
                "success_count": 0,
                "failure_count": 0,
                "quality_gates": quality_gates or [],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "wave_plan": wave_plan,  # Store AI-generated wave plan
                "ai_recommendations": ai_recommendations  # Store AI recommendations
            }
            
            self._waves[wave_id] = wave
            
            self.logger.info(f"✅ Created wave: {wave_id} ({name})")
            
            return {
                "success": True,
                "wave_id": wave_id,
                "wave": wave
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create wave: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def select_wave_candidates(
        self,
        wave_id: str,
        policy_pool: Optional[List[Dict[str, Any]]] = None,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Select candidates for a wave based on selection criteria.
        
        Args:
            wave_id: Wave ID
            policy_pool: Optional pool of policies to select from
            user_context: Optional user context
        
        Returns:
            Selection result with selected policy IDs
        """
        # Write to WAL
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.record_wal_entry(
                entry_data={
                    "operation": "select_wave_candidates",
                    "wave_id": wave_id
                },
                user_context=user_context
            )
        
        try:
            wave = self._waves.get(wave_id)
            if not wave:
                return {
                    "success": False,
                    "error": f"Wave {wave_id} not found"
                }
            
            selection_criteria = wave.get("selection_criteria", {})
            
            # Get Routing Engine to evaluate selection criteria
            routing_engine = await self._get_routing_engine_service()
            if not routing_engine:
                return {
                    "success": False,
                    "error": "Routing Engine Service not available"
                }
            
            # Evaluate selection criteria against policy pool
            selected_policies = []
            if policy_pool:
                for policy in policy_pool:
                    # Evaluate if policy matches selection criteria
                    routing_result = await routing_engine.evaluate_routing(
                        policy_data=policy,
                        namespace="wave_selection",
                        user_context=user_context
                    )
                    
                    # Check if routing matches wave target system
                    if routing_result.get("success") and routing_result.get("target_system") == wave.get("target_system"):
                        selected_policies.append(policy.get("policy_id"))
            
            # Update wave with selected policies
            wave["policies"] = selected_policies
            wave["updated_at"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"✅ Selected {len(selected_policies)} candidates for wave {wave_id}")
            
            return {
                "success": True,
                "wave_id": wave_id,
                "selected_count": len(selected_policies),
                "policy_ids": selected_policies
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to select wave candidates: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_wave(
        self,
        wave_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a migration wave.
        
        Orchestrates migration for all policies in the wave with quality gate enforcement.
        
        Args:
            wave_id: Wave ID
            user_context: Optional user context
        
        Returns:
            Execution result with success/failure counts
        """
        # Write to WAL
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.record_wal_entry(
                entry_data={
                    "operation": "execute_wave",
                    "wave_id": wave_id
                },
                user_context=user_context
            )
        
        try:
            wave = self._waves.get(wave_id)
            if not wave:
                return {
                    "success": False,
                    "error": f"Wave {wave_id} not found"
                }
            
            # Update wave status
            wave["status"] = WaveStatus.IN_PROGRESS.value
            wave["updated_at"] = datetime.utcnow().isoformat()
            
            # Get Insurance Migration Orchestrator
            migration_orchestrator = await self._get_insurance_migration_orchestrator()
            if not migration_orchestrator:
                return {
                    "success": False,
                    "error": "Insurance Migration Orchestrator not available"
                }
            
            # Execute migration for each policy
            success_count = 0
            failure_count = 0
            failed_policies = []
            
            policy_ids = wave.get("policies", [])
            self.logger.info(f"🚀 Executing wave {wave_id} with {len(policy_ids)} policies")
            
            for policy_id in policy_ids:
                try:
                    # TODO: Get policy data (will integrate with Policy Tracker when available)
                    # For now, use placeholder
                    policy_data = {"policy_id": policy_id}
                    
                    # Execute migration steps
                    # Step 1: Map to canonical (if not already done)
                    map_result = await migration_orchestrator.map_to_canonical(
                        source_data=policy_data,
                        user_context=user_context
                    )
                    
                    if not map_result.get("success"):
                        failure_count += 1
                        failed_policies.append(policy_id)
                        continue
                    
                    # Step 2: Route policy
                    route_result = await migration_orchestrator.route_policies(
                        policy_data=map_result.get("canonical_data", policy_data),
                        namespace="wave_execution",
                        user_context=user_context
                    )
                    
                    if not route_result.get("success"):
                        failure_count += 1
                        failed_policies.append(policy_id)
                        continue
                    
                    # Step 3: Check quality gates
                    quality_passed = await self._check_quality_gates(
                        wave_id=wave_id,
                        policy_id=policy_id,
                        migration_result=route_result,
                        user_context=user_context
                    )
                    
                    if not quality_passed:
                        failure_count += 1
                        failed_policies.append(policy_id)
                        continue
                    
                    success_count += 1
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to migrate policy {policy_id}: {e}")
                    failure_count += 1
                    failed_policies.append(policy_id)
            
            # Update wave status
            wave["success_count"] = success_count
            wave["failure_count"] = failure_count
            wave["status"] = WaveStatus.COMPLETED.value if failure_count == 0 else WaveStatus.FAILED.value
            wave["updated_at"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"✅ Wave {wave_id} execution complete: {success_count} success, {failure_count} failures")
            
            return {
                "success": True,
                "wave_id": wave_id,
                "success_count": success_count,
                "failure_count": failure_count,
                "failed_policies": failed_policies,
                "status": wave["status"]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to execute wave: {e}", exc_info=True)
            
            # Update wave status
            if wave_id in self._waves:
                self._waves[wave_id]["status"] = WaveStatus.FAILED.value
                self._waves[wave_id]["updated_at"] = datetime.utcnow().isoformat()
            
            return {
                "success": False,
                "error": str(e),
                "wave_id": wave_id
            }
    
    async def _check_quality_gates(
        self,
        wave_id: str,
        policy_id: str,
        migration_result: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check quality gates for a policy migration.
        
        Args:
            wave_id: Wave ID
            policy_id: Policy ID
            migration_result: Migration result to validate
            user_context: Optional user context
        
        Returns:
            True if all quality gates pass, False otherwise
        """
        try:
            wave = self._waves.get(wave_id)
            if not wave:
                return False
            
            quality_gates = wave.get("quality_gates", [])
            
            # If no quality gates defined, pass by default
            if not quality_gates:
                return True
            
            # Check each quality gate
            for gate in quality_gates:
                gate_type = gate.get("type")
                gate_criteria = gate.get("criteria", {})
                
                if gate_type == "data_quality":
                    # Check data quality score
                    quality_score = migration_result.get("data_quality_score", 0.0)
                    min_score = gate_criteria.get("min_score", 0.8)
                    if quality_score < min_score:
                        self.logger.warning(f"⚠️ Quality gate failed for policy {policy_id}: data quality score {quality_score} < {min_score}")
                        return False
                
                elif gate_type == "completeness":
                    # Check required fields completeness
                    required_fields = gate_criteria.get("required_fields", [])
                    canonical_data = migration_result.get("canonical_data", {})
                    for field in required_fields:
                        if field not in canonical_data or canonical_data[field] is None:
                            self.logger.warning(f"⚠️ Quality gate failed for policy {policy_id}: missing required field {field}")
                            return False
                
                elif gate_type == "validation":
                    # Run validation rules
                    validation_rules = gate_criteria.get("rules", [])
                    # TODO: Implement validation rule engine
                    pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Quality gate check failed: {e}")
            return False
    
    async def rollback_wave(
        self,
        wave_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Rollback a wave migration.
        
        Compensation handler for wave execution.
        
        Args:
            wave_id: Wave ID
            user_context: Optional user context
        
        Returns:
            Rollback result
        """
        # Write to WAL
        data_steward = await self._get_data_steward()
        if data_steward:
            await data_steward.record_wal_entry(
                entry_data={
                    "operation": "rollback_wave",
                    "wave_id": wave_id
                },
                user_context=user_context
            )
        
        try:
            wave = self._waves.get(wave_id)
            if not wave:
                return {
                    "success": False,
                    "error": f"Wave {wave_id} not found"
                }
            
            # Get Insurance Migration Orchestrator for compensation
            migration_orchestrator = await self._get_insurance_migration_orchestrator()
            if not migration_orchestrator:
                return {
                    "success": False,
                    "error": "Insurance Migration Orchestrator not available"
                }
            
            # Rollback each successfully migrated policy
            policy_ids = wave.get("policies", [])
            rolled_back_count = 0
            
            for policy_id in policy_ids:
                try:
                    # TODO: Implement rollback logic (will integrate with Policy Tracker)
                    # For now, just mark as rolled back
                    rolled_back_count += 1
                except Exception as e:
                    self.logger.warning(f"⚠️ Failed to rollback policy {policy_id}: {e}")
            
            # Update wave status
            wave["status"] = WaveStatus.ROLLED_BACK.value
            wave["updated_at"] = datetime.utcnow().isoformat()
            
            self.logger.info(f"✅ Rolled back wave {wave_id}: {rolled_back_count} policies")
            
            return {
                "success": True,
                "wave_id": wave_id,
                "rolled_back_count": rolled_back_count,
                "status": wave["status"]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to rollback wave: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "wave_id": wave_id
            }
    
    async def get_wave_status(
        self,
        wave_id: str
    ) -> Dict[str, Any]:
        """
        Get wave status and progress.
        
        Args:
            wave_id: Wave ID
        
        Returns:
            Wave status information
        """
        try:
            wave = self._waves.get(wave_id)
            if not wave:
                return {
                    "success": False,
                    "error": f"Wave {wave_id} not found"
                }
            
            return {
                "success": True,
                "wave": wave
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get wave status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ============================================================================
    # INITIALIZATION
    # ============================================================================
    
    async def initialize(self) -> bool:
        """
        Initialize Wave Orchestrator.
        
        Sets up:
        - Wave Planning Specialist Agent (AI-powered wave planning)
        - MCP Server (exposes orchestrator methods as MCP tools)
        """
        try:
            # Call parent initialize
            await super().initialize()
            
            # Initialize Wave Planning Specialist Agent (for AI-powered wave planning)
            # Using declarative implementation (configuration-driven, LLM-powered reasoning)
            from backend.business_enablement.agents.wave_planning_specialist import WavePlanningSpecialist
            
            self._wave_planning_agent = await self.initialize_agent(
                WavePlanningSpecialist,
                "WavePlanningSpecialist",
                agent_type="specialist",
                capabilities=["policy_cohort_analysis", "risk_assessment", "quality_gate_recommendations", "timeline_estimation"]
            )
            
            if self._wave_planning_agent:
                self.logger.info("✅ Wave Planning Specialist Agent initialized")
            
            # Initialize MCP Server (exposes orchestrator methods as MCP tools)
            from .mcp_server import WaveMCPServer
            
            self.mcp_server = WaveMCPServer(
                orchestrator=self,
                di_container=self.di_container
            )
            
            # MCP server registers tools in __init__, ready to use
            self.logger.info(f"✅ {self.orchestrator_name} MCP Server initialized")
            
            # Register with Curator (Phase 2 pattern with CapabilityDefinition structure)
            await self._realm_service.register_with_curator(
                capabilities=[
                    {
                        "name": "wave_planning",
                        "protocol": "WaveOrchestratorProtocol",
                        "description": "Create and manage migration waves",
                        "contracts": {
                            "soa_api": {
                                "api_name": "create_wave",
                                "endpoint": "/api/v1/wave-orchestration/create-wave",
                                "method": "POST",
                                "handler": self.create_wave,
                                "metadata": {
                                    "description": "Create a new migration wave",
                                    "parameters": ["wave_config", "user_context"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "create_wave_tool",
                                "tool_definition": {
                                    "name": "create_wave_tool",
                                    "description": "Create a new migration wave",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "wave_config": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "insurance.create_wave",
                            "semantic_api": "/api/v1/wave-orchestration/create-wave"
                        }
                    },
                    {
                        "name": "wave_execution",
                        "protocol": "WaveOrchestratorProtocol",
                        "description": "Execute and manage wave execution",
                        "contracts": {
                            "soa_api": {
                                "api_name": "execute_wave",
                                "endpoint": "/api/v1/wave-orchestration/execute-wave/{wave_id}",
                                "method": "POST",
                                "handler": self.execute_wave,
                                "metadata": {
                                    "description": "Execute a migration wave",
                                    "parameters": ["wave_id", "user_context"]
                                }
                            },
                            "mcp_tool": {
                                "tool_name": "execute_wave_tool",
                                "tool_definition": {
                                    "name": "execute_wave_tool",
                                    "description": "Execute a migration wave",
                                    "input_schema": {
                                        "type": "object",
                                        "properties": {
                                            "wave_id": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "semantic_mapping": {
                            "domain_capability": "insurance.execute_wave",
                            "semantic_api": "/api/v1/wave-orchestration/execute-wave"
                        }
                    }
                ],
                soa_apis=["create_wave", "get_wave_status", "execute_wave"],
                mcp_tools=["create_wave_tool", "get_wave_status_tool", "execute_wave_tool"]
            )
            
            self.logger.info(f"✅ {self.orchestrator_name} registered with Curator")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.orchestrator_name}: {e}", exc_info=True)
            return False

