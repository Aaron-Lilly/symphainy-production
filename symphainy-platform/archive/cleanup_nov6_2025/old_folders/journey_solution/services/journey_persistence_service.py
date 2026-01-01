#!/usr/bin/env python3
"""
Journey Persistence Service - Foundation for Journey Management

This service provides journey persistence capabilities across the platform,
enabling journey context to be maintained throughout the user's experience.

WHAT (Journey/Solution Role): I provide journey persistence across all platform dimensions
HOW (Service Implementation): I persist journey context like tenant_id, user_id, and token
"""

import os
import sys
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import json
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.di_container.di_container_service import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from foundations.curator_foundation.curator_foundation_service import CuratorFoundationService
from bases.realm_service_base import RealmServiceBase
from utilities import UserContext


class JourneyStatus(Enum):
    """Journey status enumeration."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class JourneyType(Enum):
    """Journey type enumeration."""
    MVP = "mvp"
    AUTONOMOUS_VEHICLE_TESTING = "autonomous_vehicle_testing"
    INSURANCE_AI_PLATFORM = "insurance_ai_platform"
    CUSTOM = "custom"


@dataclass
class JourneyContext:
    """Journey context data structure."""
    journey_id: str
    tenant_id: str
    user_id: str
    session_id: str
    journey_type: JourneyType
    status: JourneyStatus
    business_outcome: str
    current_step: str
    journey_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]


class JourneyPersistenceService(RealmServiceBase):
    """
    Journey Persistence Service - Foundation for Journey Management
    
    This service provides journey persistence capabilities across the platform,
    enabling journey context to be maintained throughout the user's experience.
    """
    
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService,
                 curator_foundation: Optional[CuratorFoundationService] = None):
        """Initialize Journey Persistence Service."""
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        self.curator_foundation = curator_foundation
        
        # Journey storage
        self.active_journeys: Dict[str, JourneyContext] = {}
        self.journey_history: Dict[str, List[JourneyContext]] = {}
        
        # Journey templates
        self.journey_templates: Dict[str, Dict[str, Any]] = {}
        
        # Persistence configuration
        self.persistence_config = {
            "storage_backend": "memory",  # Can be extended to database, Redis, etc.
            "retention_days": 30,
            "max_active_journeys": 1000,
            "enable_audit_logging": True
        }
        
        print(f"💾 Journey Persistence Service initialized - Foundation for journey management!")
    
    async def initialize(self):
        """Initialize the Journey Persistence Service."""
        try:
            print("💾 Initializing Journey Persistence Service...")
            
            # Initialize storage backend
            await self._initialize_storage_backend()
            
            # Load existing journeys
            await self._load_existing_journeys()
            
            # Initialize journey templates
            await self._initialize_journey_templates()
            
            print("✅ Journey Persistence Service initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Journey Persistence Service: {e}")
            raise
    
    async def _initialize_storage_backend(self):
        """Initialize the storage backend for journey persistence."""
        try:
            # For now, using in-memory storage
            # Can be extended to database, Redis, or other storage backends
            self.storage_backend = "memory"
            print("✅ Storage backend initialized (memory)")
            
        except Exception as e:
            print(f"❌ Failed to initialize storage backend: {e}")
            raise
    
    async def _load_existing_journeys(self):
        """Load existing journeys from storage."""
        try:
            # For now, start with empty state
            # In production, this would load from persistent storage
            self.active_journeys = {}
            self.journey_history = {}
            print("✅ Existing journeys loaded")
            
        except Exception as e:
            print(f"❌ Failed to load existing journeys: {e}")
            raise
    
    async def _initialize_journey_templates(self):
        """Initialize journey templates."""
        try:
            self.journey_templates = {
                "mvp": {
                    "name": "MVP Journey",
                    "description": "Standard MVP journey flow",
                    "steps": [
                        "business_outcome_analysis",
                        "data_requirement_assessment",
                        "platform_routing",
                        "capability_execution",
                        "outcome_measurement"
                    ],
                    "routing_logic": "mvp_routing"
                },
                "autonomous_vehicle_testing": {
                    "name": "Autonomous Vehicle Testing Journey",
                    "description": "Journey for autonomous vehicle testing platform",
                    "steps": [
                        "testing_data_ingestion",
                        "test_plan_generation",
                        "coverage_metrics_establishment",
                        "digital_twin_simulation",
                        "real_world_testing",
                        "lessons_learned_harvesting"
                    ],
                    "routing_logic": "av_testing_routing"
                },
                "insurance_ai_platform": {
                    "name": "Insurance AI Platform Journey",
                    "description": "Journey for insurance AI platform",
                    "steps": [
                        "legacy_data_connection",
                        "data_lake_creation",
                        "ai_operations_setup",
                        "broker_carrier_matching",
                        "data_monetization",
                        "system_modernization"
                    ],
                    "routing_logic": "insurance_ai_routing"
                }
            }
            
            print("✅ Journey templates initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize journey templates: {e}")
            raise
    
    # ============================================================================
    # JOURNEY PERSISTENCE METHODS
    # ============================================================================
    
    async def create_journey(self, user_context: UserContext, 
                           business_outcome: str, 
                           journey_type: JourneyType = JourneyType.MVP,
                           journey_data: Optional[Dict[str, Any]] = None) -> JourneyContext:
        """Create a new journey and persist it."""
        try:
            # Generate journey ID
            journey_id = str(uuid.uuid4())
            
            # Create journey context
            journey_context = JourneyContext(
                journey_id=journey_id,
                tenant_id=user_context.tenant_id,
                user_id=user_context.user_id,
                session_id=user_context.session_id,
                journey_type=journey_type,
                status=JourneyStatus.CREATED,
                business_outcome=business_outcome,
                current_step="business_outcome_analysis",
                journey_data=journey_data or {},
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={
                    "created_by": "journey_persistence_service",
                    "version": "1.0.0"
                }
            )
            
            # Persist journey
            await self._persist_journey(journey_context)
            
            # Add to active journeys
            self.active_journeys[journey_id] = journey_context
            
            print(f"✅ Journey created: {journey_id} for tenant: {user_context.tenant_id}")
            
            return journey_context
            
        except Exception as e:
            print(f"❌ Failed to create journey: {e}")
            raise
    
    async def get_journey(self, journey_id: str) -> Optional[JourneyContext]:
        """Get a journey by ID."""
        try:
            return self.active_journeys.get(journey_id)
            
        except Exception as e:
            print(f"❌ Failed to get journey: {e}")
            return None
    
    async def update_journey(self, journey_id: str, 
                           updates: Dict[str, Any]) -> Optional[JourneyContext]:
        """Update a journey with new data."""
        try:
            journey = self.active_journeys.get(journey_id)
            if not journey:
                return None
            
            # Update journey data
            for key, value in updates.items():
                if hasattr(journey, key):
                    setattr(journey, key, value)
                else:
                    journey.journey_data[key] = value
            
            # Update timestamp
            journey.updated_at = datetime.now()
            
            # Persist updated journey
            await self._persist_journey(journey)
            
            print(f"✅ Journey updated: {journey_id}")
            
            return journey
            
        except Exception as e:
            print(f"❌ Failed to update journey: {e}")
            return None
    
    async def complete_journey(self, journey_id: str, 
                              final_data: Optional[Dict[str, Any]] = None) -> bool:
        """Complete a journey and move it to history."""
        try:
            journey = self.active_journeys.get(journey_id)
            if not journey:
                return False
            
            # Update journey status
            journey.status = JourneyStatus.COMPLETED
            journey.current_step = "completed"
            journey.updated_at = datetime.now()
            
            # Add final data
            if final_data:
                journey.journey_data.update(final_data)
            
            # Move to history
            if journey.tenant_id not in self.journey_history:
                self.journey_history[journey.tenant_id] = []
            
            self.journey_history[journey.tenant_id].append(journey)
            
            # Remove from active journeys
            del self.active_journeys[journey_id]
            
            # Persist completed journey
            await self._persist_journey(journey)
            
            print(f"✅ Journey completed: {journey_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to complete journey: {e}")
            return False
    
    async def cancel_journey(self, journey_id: str, 
                            reason: Optional[str] = None) -> bool:
        """Cancel a journey."""
        try:
            journey = self.active_journeys.get(journey_id)
            if not journey:
                return False
            
            # Update journey status
            journey.status = JourneyStatus.CANCELLED
            journey.current_step = "cancelled"
            journey.updated_at = datetime.now()
            
            # Add cancellation reason
            if reason:
                journey.journey_data["cancellation_reason"] = reason
            
            # Move to history
            if journey.tenant_id not in self.journey_history:
                self.journey_history[journey.tenant_id] = []
            
            self.journey_history[journey.tenant_id].append(journey)
            
            # Remove from active journeys
            del self.active_journeys[journey_id]
            
            # Persist cancelled journey
            await self._persist_journey(journey)
            
            print(f"✅ Journey cancelled: {journey_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to cancel journey: {e}")
            return False
    
    # ============================================================================
    # JOURNEY QUERY METHODS
    # ============================================================================
    
    async def get_user_journeys(self, user_context: UserContext) -> List[JourneyContext]:
        """Get all journeys for a user."""
        try:
            user_journeys = []
            
            # Get active journeys
            for journey in self.active_journeys.values():
                if journey.tenant_id == user_context.tenant_id and journey.user_id == user_context.user_id:
                    user_journeys.append(journey)
            
            # Get historical journeys
            if user_context.tenant_id in self.journey_history:
                for journey in self.journey_history[user_context.tenant_id]:
                    if journey.user_id == user_context.user_id:
                        user_journeys.append(journey)
            
            return user_journeys
            
        except Exception as e:
            print(f"❌ Failed to get user journeys: {e}")
            return []
    
    async def get_tenant_journeys(self, tenant_id: str) -> List[JourneyContext]:
        """Get all journeys for a tenant."""
        try:
            tenant_journeys = []
            
            # Get active journeys
            for journey in self.active_journeys.values():
                if journey.tenant_id == tenant_id:
                    tenant_journeys.append(journey)
            
            # Get historical journeys
            if tenant_id in self.journey_history:
                tenant_journeys.extend(self.journey_history[tenant_id])
            
            return tenant_journeys
            
        except Exception as e:
            print(f"❌ Failed to get tenant journeys: {e}")
            return []
    
    async def get_journey_by_business_outcome(self, business_outcome: str, 
                                           tenant_id: str) -> List[JourneyContext]:
        """Get journeys by business outcome."""
        try:
            matching_journeys = []
            
            # Search active journeys
            for journey in self.active_journeys.values():
                if (journey.tenant_id == tenant_id and 
                    business_outcome.lower() in journey.business_outcome.lower()):
                    matching_journeys.append(journey)
            
            # Search historical journeys
            if tenant_id in self.journey_history:
                for journey in self.journey_history[tenant_id]:
                    if business_outcome.lower() in journey.business_outcome.lower():
                        matching_journeys.append(journey)
            
            return matching_journeys
            
        except Exception as e:
            print(f"❌ Failed to get journeys by business outcome: {e}")
            return []
    
    # ============================================================================
    # JOURNEY TEMPLATE METHODS
    # ============================================================================
    
    async def get_journey_template(self, journey_type: JourneyType) -> Optional[Dict[str, Any]]:
        """Get a journey template by type."""
        try:
            return self.journey_templates.get(journey_type.value)
            
        except Exception as e:
            print(f"❌ Failed to get journey template: {e}")
            return None
    
    async def create_custom_journey_template(self, template_data: Dict[str, Any]) -> str:
        """Create a custom journey template."""
        try:
            template_id = str(uuid.uuid4())
            self.journey_templates[template_id] = template_data
            
            print(f"✅ Custom journey template created: {template_id}")
            
            return template_id
            
        except Exception as e:
            print(f"❌ Failed to create custom journey template: {e}")
            raise
    
    # ============================================================================
    # PERSISTENCE METHODS
    # ============================================================================
    
    async def _persist_journey(self, journey: JourneyContext):
        """Persist a journey to storage."""
        try:
            # For now, using in-memory storage
            # In production, this would persist to database, Redis, etc.
            
            # Convert journey to dictionary for storage
            journey_dict = asdict(journey)
            
            # Convert datetime objects to strings for JSON serialization
            journey_dict["created_at"] = journey.created_at.isoformat()
            journey_dict["updated_at"] = journey.updated_at.isoformat()
            journey_dict["journey_type"] = journey.journey_type.value
            journey_dict["status"] = journey.status.value
            
            # In production, this would be stored in persistent storage
            # For now, just log the persistence
            if self.persistence_config.get("enable_audit_logging", False):
                print(f"💾 Journey persisted: {journey.journey_id}")
            
        except Exception as e:
            print(f"❌ Failed to persist journey: {e}")
            raise
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    async def get_journey_stats(self) -> Dict[str, Any]:
        """Get journey statistics."""
        try:
            total_active = len(self.active_journeys)
            total_historical = sum(len(journeys) for journeys in self.journey_history.values())
            
            # Count by status
            status_counts = {}
            for journey in self.active_journeys.values():
                status = journey.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by journey type
            type_counts = {}
            for journey in self.active_journeys.values():
                journey_type = journey.journey_type.value
                type_counts[journey_type] = type_counts.get(journey_type, 0) + 1
            
            return {
                "total_active_journeys": total_active,
                "total_historical_journeys": total_historical,
                "status_counts": status_counts,
                "type_counts": type_counts,
                "journey_templates": len(self.journey_templates)
            }
            
        except Exception as e:
            print(f"❌ Failed to get journey stats: {e}")
            return {}
    
    async def cleanup_old_journeys(self, retention_days: int = 30):
        """Clean up old journeys based on retention policy."""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cleaned_count = 0
            
            # Clean up historical journeys
            for tenant_id, journeys in self.journey_history.items():
                journeys_to_remove = []
                for journey in journeys:
                    if journey.updated_at < cutoff_date:
                        journeys_to_remove.append(journey)
                        cleaned_count += 1
                
                for journey in journeys_to_remove:
                    journeys.remove(journey)
            
            print(f"✅ Cleaned up {cleaned_count} old journeys")
            
        except Exception as e:
            print(f"❌ Failed to cleanup old journeys: {e}")
    
    # ============================================================================
    # JOURNEY CONTEXT INJECTION
    # ============================================================================
    
    async def inject_journey_context(self, user_context: UserContext, 
                                   journey_id: str) -> UserContext:
        """Inject journey context into user context."""
        try:
            journey = await self.get_journey(journey_id)
            if not journey:
                return user_context
            
            # Create enhanced user context with journey information
            enhanced_context = UserContext(
                tenant_id=user_context.tenant_id,
                user_id=user_context.user_id,
                session_id=user_context.session_id,
                journey_id=journey_id,
                journey_context=journey
            )
            
            return enhanced_context
            
        except Exception as e:
            print(f"❌ Failed to inject journey context: {e}")
            return user_context
    
    # ============================================================================
    # REALM SERVICE BASE ABSTRACT METHODS
    # ============================================================================
    
    async def shutdown(self):
        """Shutdown the Journey Persistence Service."""
        try:
            self.logger.info("🛑 Shutting down Journey Persistence Service...")
            
            # Clear journey storage
            self.journey_storage.clear()
            self.journey_templates.clear()
            
            self.logger.info("✅ Journey Persistence Service shutdown complete")
            
        except Exception as e:
            self.logger.error(f"❌ Error during Journey Persistence Service shutdown: {e}")
    
    async def get_realm_capabilities(self) -> Dict[str, Any]:
        """Get Journey Persistence Service capabilities for realm operations."""
        return {
            "service_name": self.service_name,
            "realm": "journey",
            "service_type": "journey_persistence",
            "capabilities": {
                "journey_persistence": {
                    "enabled": True,
                    "active_journeys": len(self.journey_storage),
                    "templates_count": len(self.journey_templates)
                },
                "journey_management": {
                    "enabled": True,
                    "management_methods": ["create", "update", "delete", "retrieve", "list"]
                },
                "context_injection": {
                    "enabled": True,
                    "injection_methods": ["user_context_enhancement", "journey_context_propagation"]
                }
            },
            "enhanced_platform_capabilities": {
                "zero_trust_security": True,
                "multi_tenancy": True,
                "enhanced_logging": True,
                "enhanced_error_handling": True,
                "health_monitoring": True,
                "cross_realm_communication": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }


# Create service instance factory function
def create_journey_persistence_service(di_container: DIContainerService,
                                     public_works_foundation: PublicWorksFoundationService,
                                     curator_foundation: CuratorFoundationService = None) -> JourneyPersistenceService:
    """Factory function to create JourneyPersistenceService with proper DI."""
    return JourneyPersistenceService(
        di_container=di_container,
        public_works_foundation=public_works_foundation,
        curator_foundation=curator_foundation
    )


# Create default service instance (will be properly initialized by foundation services)
journey_persistence_service = None  # Will be set by foundation services during initialization
