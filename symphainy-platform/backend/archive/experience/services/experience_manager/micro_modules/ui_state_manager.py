#!/usr/bin/env python3
"""
UI State Manager Micro-Module

Manages user interface state synchronization and updates across the platform.

WHAT (Micro-Module): I manage UI state synchronization and updates
HOW (Implementation): I track UI state changes, synchronize across components, and manage state consistency
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from utilities import UserContext
from config.environment_loader import EnvironmentLoader


class UIStateManagerModule:
    """
    UI State Manager Micro-Module
    
    Provides functionality to manage and synchronize user interface state.
    """
    
    def __init__(self, environment: EnvironmentLoader, logger: Optional[logging.Logger] = None):
        """Initialize UI State Manager Module."""
        self.environment = environment
        self.logger = logger or logging.getLogger(__name__)
        self.is_initialized = False
        
        # UI state store (for MVP)
        # In a real system, this would be a persistent store or cache
        self.ui_states: Dict[str, Dict[str, Any]] = {}
        
        # State change history for debugging and rollback
        self.state_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # UI components that can be updated
        self.ui_components = [
            "dashboard",
            "file_upload",
            "data_visualization", 
            "workflow_builder",
            "chat_interface",
            "navigation",
            "pillar_content",
            "insights_panel",
            "operations_panel",
            "business_outcomes_panel"
        ]
        
        self.logger.info("🎨 UI State Manager Module initialized")
    
    async def initialize(self):
        """Initialize the UI State Manager Module."""
        self.logger.info("🚀 Initializing UI State Manager Module...")
        # Load any configurations or connect to persistent storage here
        self.is_initialized = True
        self.logger.info("✅ UI State Manager Module initialized successfully")
    
    async def shutdown(self):
        """Shutdown the UI State Manager Module."""
        self.logger.info("🛑 Shutting down UI State Manager Module...")
        # Clean up resources or close connections here
        self.is_initialized = False
        self.logger.info("✅ UI State Manager Module shutdown successfully")
    
    async def update_ui_state(self, session_id: str, ui_state: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Update UI state for a specific session.
        
        Args:
            session_id: The ID of the session.
            ui_state: The UI state data to update.
            user_context: Context of the user.
            
        Returns:
            A dictionary indicating the success of the update.
        """
        self.logger.debug(f"Updating UI state for session: {session_id}")
        
        try:
            # Validate UI state data
            validation_result = await self._validate_ui_state(ui_state)
            if not validation_result.get("valid"):
                return {"success": False, "error": "Invalid UI state data", "details": validation_result.get("errors")}
            
            # Get current UI state
            current_state = self.ui_states.get(session_id, {})
            
            # Create state change record
            state_change = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_context.user_id,
                "previous_state": current_state.copy(),
                "new_state": ui_state.copy(),
                "changes": self._calculate_state_changes(current_state, ui_state)
            }
            
            # Update UI state
            current_state.update(ui_state)
            self.ui_states[session_id] = current_state
            
            # Store state change in history
            if session_id not in self.state_history:
                self.state_history[session_id] = []
            self.state_history[session_id].append(state_change)
            
            # Keep only last 50 state changes per session
            if len(self.state_history[session_id]) > 50:
                self.state_history[session_id] = self.state_history[session_id][-50:]
            
            self.logger.info(f"✅ UI state updated for session: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "ui_state_updated": True,
                "state_change_id": len(self.state_history[session_id]) - 1,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update UI state: {e}")
            return {"success": False, "error": str(e), "message": "Failed to update UI state"}
    
    async def get_ui_state(self, session_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Get current UI state for a session.
        
        Args:
            session_id: The ID of the session.
            user_context: Context of the user.
            
        Returns:
            A dictionary containing the current UI state.
        """
        self.logger.debug(f"Getting UI state for session: {session_id}")
        
        try:
            ui_state = self.ui_states.get(session_id, {})
            
            return {
                "success": True,
                "session_id": session_id,
                "ui_state": ui_state,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get UI state: {e}")
            return {"success": False, "error": str(e), "message": "Failed to get UI state"}
    
    async def synchronize_ui_components(self, session_id: str, component_updates: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """
        Synchronize UI components across the platform.
        
        Args:
            session_id: The ID of the session.
            component_updates: Updates for specific UI components.
            user_context: Context of the user.
            
        Returns:
            A dictionary indicating the synchronization status.
        """
        self.logger.debug(f"Synchronizing UI components for session: {session_id}")
        
        try:
            synchronization_results = {}
            
            for component, update_data in component_updates.items():
                if component in self.ui_components:
                    # Update component state
                    component_result = await self._update_component_state(session_id, component, update_data, user_context)
                    synchronization_results[component] = component_result
                else:
                    synchronization_results[component] = {
                        "success": False,
                        "error": f"Unknown component: {component}"
                    }
            
            # Check if all synchronizations were successful
            all_successful = all(result.get("success", False) for result in synchronization_results.values())
            
            return {
                "success": all_successful,
                "session_id": session_id,
                "synchronization_results": synchronization_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to synchronize UI components: {e}")
            return {"success": False, "error": str(e), "message": "Failed to synchronize UI components"}
    
    async def rollback_ui_state(self, session_id: str, state_change_id: int, user_context: UserContext) -> Dict[str, Any]:
        """
        Rollback UI state to a previous state change.
        
        Args:
            session_id: The ID of the session.
            state_change_id: The ID of the state change to rollback to.
            user_context: Context of the user.
            
        Returns:
            A dictionary indicating the rollback status.
        """
        self.logger.debug(f"Rolling back UI state for session: {session_id} to change: {state_change_id}")
        
        try:
            if session_id not in self.state_history:
                return {"success": False, "error": "No state history found for session"}
            
            history = self.state_history[session_id]
            if state_change_id >= len(history) or state_change_id < 0:
                return {"success": False, "error": "Invalid state change ID"}
            
            # Get the state to rollback to
            target_state_change = history[state_change_id]
            previous_state = target_state_change.get("previous_state", {})
            
            # Update current UI state
            self.ui_states[session_id] = previous_state.copy()
            
            # Add rollback record to history
            rollback_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_context.user_id,
                "action": "rollback",
                "rollback_to_change_id": state_change_id,
                "state_after_rollback": previous_state.copy()
            }
            history.append(rollback_record)
            
            self.logger.info(f"✅ UI state rolled back for session: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "rolled_back_to_change_id": state_change_id,
                "ui_state": previous_state,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to rollback UI state: {e}")
            return {"success": False, "error": str(e), "message": "Failed to rollback UI state"}
    
    async def get_ui_state_history(self, session_id: str, user_context: UserContext) -> Dict[str, Any]:
        """
        Get UI state change history for a session.
        
        Args:
            session_id: The ID of the session.
            user_context: Context of the user.
            
        Returns:
            A dictionary containing the state change history.
        """
        self.logger.debug(f"Getting UI state history for session: {session_id}")
        
        try:
            history = self.state_history.get(session_id, [])
            
            # Return simplified history (without full state data for performance)
            simplified_history = [
                {
                    "change_id": i,
                    "timestamp": change.get("timestamp"),
                    "user_id": change.get("user_id"),
                    "action": change.get("action", "update"),
                    "changes": change.get("changes", {}),
                    "rollback_to_change_id": change.get("rollback_to_change_id")
                }
                for i, change in enumerate(history)
            ]
            
            return {
                "success": True,
                "session_id": session_id,
                "history": simplified_history,
                "history_count": len(history),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get UI state history: {e}")
            return {"success": False, "error": str(e), "message": "Failed to get UI state history"}
    
    async def _validate_ui_state(self, ui_state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate UI state data."""
        try:
            errors = []
            
            # Check for required fields
            if not isinstance(ui_state, dict):
                errors.append("UI state must be a dictionary")
            
            # Validate component states
            for component, state in ui_state.items():
                if component not in self.ui_components:
                    errors.append(f"Unknown UI component: {component}")
                
                if not isinstance(state, dict):
                    errors.append(f"Component state for {component} must be a dictionary")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }
    
    def _calculate_state_changes(self, previous_state: Dict[str, Any], new_state: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate changes between previous and new state."""
        changes = {}
        
        # Find added and modified keys
        for key, value in new_state.items():
            if key not in previous_state:
                changes[key] = {"action": "added", "new_value": value}
            elif previous_state[key] != value:
                changes[key] = {
                    "action": "modified",
                    "old_value": previous_state[key],
                    "new_value": value
                }
        
        # Find removed keys
        for key in previous_state:
            if key not in new_state:
                changes[key] = {"action": "removed", "old_value": previous_state[key]}
        
        return changes
    
    async def _update_component_state(self, session_id: str, component: str, update_data: Dict[str, Any], user_context: UserContext) -> Dict[str, Any]:
        """Update state for a specific UI component."""
        try:
            # Get current UI state
            current_state = self.ui_states.get(session_id, {})
            
            # Update component state
            if component not in current_state:
                current_state[component] = {}
            
            current_state[component].update(update_data)
            self.ui_states[session_id] = current_state
            
            return {
                "success": True,
                "component": component,
                "updated": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "component": component,
                "error": str(e)
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Get health status of the UI State Manager Module."""
        return {
            "module_name": "UIStateManagerModule",
            "status": "healthy" if self.is_initialized else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "active_sessions": len(self.ui_states),
            "total_state_changes": sum(len(history) for history in self.state_history.values()),
            "supported_components": self.ui_components,
            "message": "UI State Manager Module is operational."
        }
