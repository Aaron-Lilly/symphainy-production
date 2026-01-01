#!/usr/bin/env python3
"""
State Promotion Abstraction - Business Logic Implementation

Implements the state promotion analysis and persistence decisions.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I analyze state data and determine persistence strategies
HOW (Infrastructure Implementation): I implement the sophisticated Traffic Cop state promotion logic
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from foundations.public_works_foundation.abstraction_contracts.state_promotion_protocol import (
    StatePromotionProtocol, PersistenceStrategy, PersistenceBackend
)

logger = logging.getLogger(__name__)

class StatePromotionAbstraction(StatePromotionProtocol):
    """
    State promotion abstraction with business logic.
    
    Implements the sophisticated Traffic Cop state promotion pattern
    that analyzes state complexity, size, and importance to determine
    the appropriate persistence strategy and backend.
    """
    
    def __init__(self, config_adapter, di_container=None):
        """Initialize state promotion abstraction."""
        self.config_adapter = config_adapter
        self.di_container = di_container
        self.service_name = "state_promotion_abstraction"
        
        # Get logger from DI container if available, otherwise use module logger
        if self.di_container and hasattr(self.di_container, 'get_logger'):
            self.logger = self.di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # Traffic Cop state promotion thresholds
        self.complexity_threshold = 10
        self.size_threshold = 1000
        self.importance_threshold = 8
        
        # Secondary thresholds for delayed persist
        self.complexity_threshold_secondary = 5
        self.size_threshold_secondary = 500
        self.importance_threshold_secondary = 5
        
        self.logger.info("✅ State Promotion Abstraction initialized")
    
    async def analyze_state_complexity(self, state_data: Dict[str, Any]) -> int:
        """
        Analyze the complexity of state data.
        
        Complexity is determined by:
        - Number of keys in the state
        - Depth of nested structures
        - Presence of complex data types
        """
        # Get utilities from DI container
        error_handler = None
        if self.di_container and hasattr(self.di_container, 'get_utility'):
            complexity_score = 0
            
            # Base complexity from number of keys
            complexity_score += len(state_data.keys()) * 2
            
            # Analyze nested structures
            for key, value in state_data.items():
                if isinstance(value, dict):
                    complexity_score += len(value) * 1.5
                elif isinstance(value, list):
                    complexity_score += len(value) * 1.2
                elif isinstance(value, (str, int, float, bool)):
                    complexity_score += 0.5
                else:
                    complexity_score += 2  # Complex types
            
            # Cap at 100
            complexity_score = min(int(complexity_score), 100)
            
            self.logger.debug(f"State complexity analyzed: {complexity_score}")
            return complexity_score
            
        """
        Analyze the size of state data.
        
        Size is estimated by serializing the state to JSON
        and measuring the byte length.
        """
        # Get utilities from DI container
        error_handler = None
        if self.di_container and hasattr(self.di_container, 'get_utility'):
            import json
            json_str = json.dumps(state_data, default=str)
            size_estimate = len(json_str.encode('utf-8'))
            
            self.logger.debug(f"State size analyzed: {size_estimate} bytes")
            return size_estimate
            
        """
        Analyze the importance of state data.
        
        Importance is determined by:
        - Explicit importance score in state
        - Presence of critical fields
        - State type and context
        """
        # Get utilities from DI container
        error_handler = None
        if self.di_container and hasattr(self.di_container, 'get_utility'):
            importance_score = 1  # Default importance
            
            # Check for explicit importance score
            if 'importance' in state_data:
                importance_score = max(importance_score, state_data['importance'])
            
            # Check for critical fields that increase importance
            critical_fields = ['user_id', 'session_id', 'transaction_id', 'workflow_id']
            for field in critical_fields:
                if field in state_data:
                    importance_score += 2
            
            # Check for state type importance
            state_type = state_data.get('type', 'unknown')
            if state_type in ['authentication', 'authorization', 'payment']:
                importance_score += 3
            elif state_type in ['workflow', 'session', 'user']:
                importance_score += 2
            elif state_type in ['cache', 'temporary']:
                importance_score += 0
            
            # Check for context importance
            if 'critical' in state_data.get('tags', []):
                importance_score += 3
            if 'persistent' in state_data.get('tags', []):
                importance_score += 2
            
            # Cap at 10
            importance_score = min(int(importance_score), 10)
            
            self.logger.debug(f"State importance analyzed: {importance_score}")
            return importance_score
            
        """
        Determine the persistence strategy based on analysis scores.
        
        Strategy decision logic:
        - IMMEDIATE_PERSIST: High complexity OR large size OR high importance
        - DELAYED_PERSIST: Medium complexity OR medium size OR medium importance  
        - CACHE_ONLY: Low complexity AND small size AND low importance
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        if self.di_container and hasattr(self.di_container, 'get_utility'):
            if (complexity_score > self.complexity_threshold or 
                size_estimate > self.size_threshold or 
                importance_score > self.importance_threshold):
                strategy = PersistenceStrategy.IMMEDIATE_PERSIST
                self.logger.debug(f"Strategy: IMMEDIATE_PERSIST (complexity: {complexity_score}, size: {size_estimate}, importance: {importance_score})")
            # Check for delayed persist conditions
            elif (complexity_score > self.complexity_threshold_secondary or 
                size_estimate > self.size_threshold_secondary or 
                importance_score > self.importance_threshold_secondary):
                strategy = PersistenceStrategy.DELAYED_PERSIST
                self.logger.debug(f"Strategy: DELAYED_PERSIST (complexity: {complexity_score}, size: {size_estimate}, importance: {importance_score})")
            else:
                # Default to cache only
                strategy = PersistenceStrategy.CACHE_ONLY
                self.logger.debug(f"Strategy: CACHE_ONLY (complexity: {complexity_score}, size: {size_estimate}, importance: {importance_score})")
            
            
            return strategy
            
        """
        Determine the persistence backend based on strategy and scores.
        
        Backend decision logic:
        - IMMEDIATE_PERSIST → ArangoDB (complex state persistence)
        - DELAYED_PERSIST → Redis (session state management)
        - CACHE_ONLY → Memory (temporary caching)
        """
        # Get utilities from DI container
        error_handler = None
        if self.di_container and hasattr(self.di_container, 'get_utility'):
            if strategy == PersistenceStrategy.IMMEDIATE_PERSIST:
                backend = PersistenceBackend.ARANGO_DB
                self.logger.debug(f"Backend: ARANGO_DB for immediate persist")
            elif strategy == PersistenceStrategy.DELAYED_PERSIST:
                backend = PersistenceBackend.REDIS
                self.logger.debug(f"Backend: REDIS for delayed persist")
            else:  # CACHE_ONLY
                backend = PersistenceBackend.MEMORY
                self.logger.debug(f"Backend: MEMORY for cache only")
            
            return backend
            
        """
        Calculate the time-to-live for state data.
        
        TTL calculation:
        - High importance (8-10): 7 days
        - Medium importance (5-7): 1 day
        - Low importance (1-4): 1 hour
        - Cache only: 15 minutes
        """
        # Get utilities from DI container
        error_handler = None
        if self.di_container and hasattr(self.di_container, 'get_utility'):
            if strategy == PersistenceStrategy.CACHE_ONLY:
                ttl = 15 * 60  # 15 minutes
            elif importance_score >= 8:
                ttl = 7 * 24 * 60 * 60  # 7 days
            elif importance_score >= 5:
                ttl = 24 * 60 * 60  # 1 day
            else:
                ttl = 60 * 60  # 1 hour
            
            self.logger.debug(f"TTL calculated: {ttl} seconds for importance {importance_score}")
            return ttl
            
        """
        Determine if state should be promoted to persistent storage.
        
        Promotion decision factors:
        - State has explicit promotion flag
        - Session is marked as persistent
        - State contains critical data
        - User has persistent session preference
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        if self.di_container and hasattr(self.di_container, 'get_utility'):
            should_promote = False
            reason = None
            
            # Check explicit promotion flag
            if state_data.get('promote', False):
                should_promote = True
                reason = "explicit_flag"
                self.logger.debug("State promotion: explicit flag set")
            # Check session persistence
            elif session_context.get('persistent_session', False):
                should_promote = True
                reason = "persistent_session"
                self.logger.debug("State promotion: persistent session")
            # Check for critical data
            elif any(field in state_data for field in ['user_id', 'session_id', 'transaction_id', 'workflow_id']):
                should_promote = True
                reason = "critical_data"
                self.logger.debug("State promotion: critical data present")
            # Check user preference
            elif session_context.get('user_preferences', {}).get('persistent_state', False):
                should_promote = True
                reason = "user_preference"
                self.logger.debug("State promotion: user preference")
            # Check state type
            elif state_data.get('type', 'unknown') in ['authentication', 'authorization', 'payment', 'workflow']:
                should_promote = True
                reason = "critical_state_type"
                self.logger.debug(f"State promotion: critical state type {state_data.get('type')}")
            else:
                self.logger.debug("State promotion: not recommended")
            
            # Record telemetry on decision
            
            return should_promote
            
        """
        Generate metadata for state promotion.
        
        Creates comprehensive metadata including:
        - Promotion timestamp
        - Strategy and backend information
        - State analysis results
        - Session context
        """
        # Get utilities from DI container
        error_handler = None
        telemetry = None
        if self.di_container and hasattr(self.di_container, 'get_utility'):
            metadata = {
                "promotion_timestamp": datetime.utcnow().isoformat(),
                "strategy": strategy.value,
                "backend": backend.value,
                "state_id": state_data.get('id', 'unknown'),
                "state_type": state_data.get('type', 'unknown'),
                "promotion_reason": "traffic_cop_analysis",
                "session_id": state_data.get('session_id', 'unknown'),
                "user_id": state_data.get('user_id', 'unknown'),
                "complexity_score": await self.analyze_state_complexity(state_data),
                "size_estimate": await self.analyze_state_size(state_data),
                "importance_score": await self.analyze_state_importance(state_data),
                "tags": state_data.get('tags', []),
                "created_at": state_data.get('created_at', datetime.utcnow().isoformat()),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.debug(f"Promotion metadata generated: {metadata['state_id']}")
            
            
            return metadata
            