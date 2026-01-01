#!/usr/bin/env python3
"""
State Management Abstraction - Business Logic Implementation

Implements state management operations across different backends.
This is Layer 3 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I manage state data storage and retrieval
HOW (Infrastructure Implementation): I coordinate between ArangoDB and Redis adapters
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from foundations.public_works_foundation.abstraction_contracts.state_management_protocol import StateManagementProtocol

logger = logging.getLogger(__name__)

class StateManagementAbstraction(StateManagementProtocol):
    """
    State management abstraction with business logic.
    
    Coordinates between ArangoDB (complex state) and Redis (session state)
    based on the Traffic Cop state promotion decisions.
    """
    
    def __init__(self, arango_adapter, redis_adapter, config_adapter, di_container=None):
        """Initialize state management abstraction."""
        self.arango_adapter = arango_adapter
        self.redis_adapter = redis_adapter
        self.config_adapter = config_adapter
        self.di_container = di_container
        self.service_name = "state_management_abstraction"
        
        # Get logger from DI container if available, otherwise use module logger
        if self.di_container and hasattr(self.di_container, 'get_logger'):
            self.logger = self.di_container.get_logger(self.service_name)
        else:
            self.logger = logging.getLogger(__name__)
        
        # State storage configuration
        self.arango_collection = "traffic_cop_states"
        self.redis_prefix = "traffic_cop:state:"
        self.memory_states = {}  # In-memory cache
        
        self.logger.info("✅ State Management Abstraction initialized")
    
    async def store_state(self, 
                         state_id: str,
                         state_data: Dict[str, Any],
                         metadata: Dict[str, Any] = None,
                         ttl: int = None) -> bool:
        """
        Store state data in the appropriate backend.
        
        Backend selection based on metadata:
        - ArangoDB: Complex state with immediate_persist strategy
        - Redis: Session state with delayed_persist strategy
        - Memory: Cache state with cache_only strategy
        """
        try:
            # Determine backend from metadata
            backend = metadata.get('backend', 'memory') if metadata else 'memory'
            strategy = metadata.get('strategy', 'cache_only') if metadata else 'cache_only'
            
            # Get TTL from parameter or metadata
            ttl_value = ttl if ttl is not None else (metadata.get('ttl') if metadata else None)
            
            # Add storage metadata
            storage_metadata = {
                "state_id": state_id,
                "stored_at": datetime.utcnow().isoformat(),
                "backend": backend,
                "strategy": strategy,
            }
            if ttl_value is not None:
                storage_metadata["ttl"] = ttl_value
            
            if metadata:
                storage_metadata.update(metadata)
            
            # Store in appropriate backend
            if backend == 'arango_db':
                result = await self._store_in_arango(state_id, state_data, storage_metadata, ttl_value)
            elif backend == 'redis':
                result = await self._store_in_redis(state_id, state_data, storage_metadata, ttl_value)
            else:  # memory
                result = await self._store_in_memory(state_id, state_data, storage_metadata, ttl_value)
            
            return result
                
        except Exception as e:
            self.logger.error(f"❌ Failed to store state {state_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _store_in_arango(self, state_id: str, state_data: Dict[str, Any],
                              metadata: Dict[str, Any], ttl: int = None) -> bool:
        """Store state in ArangoDB for complex persistence."""
        try:
            # Prepare document for ArangoDB
            document = {
                "_key": state_id,
                "state_data": state_data,
                "metadata": metadata,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Store in ArangoDB
            result = await self.arango_adapter.create_document(self.arango_collection, document)
            
            self.logger.debug(f"State stored in ArangoDB: {state_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store state in ArangoDB {state_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _store_in_redis(self, state_id: str, state_data: Dict[str, Any],
                            metadata: Dict[str, Any], ttl: int = None) -> bool:
        """Store state in Redis for session management."""
        try:
            # Prepare data for Redis
            redis_key = f"{self.redis_prefix}{state_id}"
            redis_data = {
                "state_data": state_data,
                "metadata": metadata,
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Store in Redis
            success = await self.redis_adapter.set_json(redis_key, redis_data, ttl)
            
            if success:
                self.logger.debug(f"State stored in Redis: {state_id}")
                return True
            else:
                self.logger.error(f"Failed to store state in Redis: {state_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to store state in Redis {state_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _store_in_memory(self, state_id: str, state_data: Dict[str, Any],
                             metadata: Dict[str, Any], ttl: int = None) -> bool:
        """Store state in memory for temporary caching."""
        try:
            # Store in memory cache
            self.memory_states[state_id] = {
                "state_data": state_data,
                "metadata": metadata,
                "created_at": datetime.utcnow().isoformat(),
                "ttl": ttl
            }
            
            self.logger.debug(f"State stored in memory: {state_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store state in memory {state_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def retrieve_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve state data from the appropriate backend.
        
        Tries backends in order of persistence:
        1. ArangoDB (most persistent)
        2. Redis (session storage)
        3. Memory (temporary cache)
        """
        try:
            # Try ArangoDB first
            arango_result = await self._retrieve_from_arango(state_id)
            if arango_result:
                return arango_result
            
            # Try Redis second
            redis_result = await self._retrieve_from_redis(state_id)
            if redis_result:
                return redis_result
            
            # Try memory last
            memory_result = await self._retrieve_from_memory(state_id)
            if memory_result:
                return memory_result
            
            self.logger.warning(f"State not found in any backend: {state_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to retrieve state {state_id}: {e}")
            raise  # Re-raise for service layer to handle
        """Retrieve state from ArangoDB."""
        try:
            result = await self.arango_adapter.get_document(self.arango_collection, state_id)
            if result:
                return result.get('state_data')
            return None
        except Exception as e:
            self.logger.error(f"❌ Error retrieving state from ArangoDB {state_id}: {e}")
            raise  # Re-raise for service layer to handle
        """Retrieve state from Redis."""
        try:
            redis_key = f"{self.redis_prefix}{state_id}"
            result = await self.redis_adapter.get_json(redis_key)
            if result:
                return result.get('state_data')
            return None
        except Exception as e:
            self.logger.error(f"❌ Error retrieving state from Redis {state_id}: {e}")
            raise  # Re-raise for service layer to handle
        """Retrieve state from memory."""
        try:
            if state_id in self.memory_states:
                state_info = self.memory_states[state_id]
                
                # Check TTL
                if state_info.get('ttl'):
                    created_at = datetime.fromisoformat(state_info['created_at'])
                    if datetime.utcnow() - created_at > timedelta(seconds=state_info['ttl']):
                        del self.memory_states[state_id]
                        return None
                
                return state_info.get('state_data')
            return None
        except Exception as e:
            self.logger.error(f"❌ Error retrieving state from memory {state_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def update_state(self,
                          state_id: str,
                          updates: Dict[str, Any],
                          metadata: Dict[str, Any] = None) -> bool:
        """
        Update existing state data.
        
        Updates the state in the backend where it's stored.
        """
        try:
            # Try to update in ArangoDB first
            arango_success = await self._update_in_arango(state_id, updates, metadata)
            if arango_success:
                return True
            
            # Try to update in Redis
            redis_success = await self._update_in_redis(state_id, updates, metadata)
            if redis_success:
                return True
            
            # Try to update in memory
            memory_success = await self._update_in_memory(state_id, updates, metadata)
            if memory_success:
                return True
            
            self.logger.warning(f"State not found for update: {state_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update state {state_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _update_in_arango(self, state_id: str, updates: Dict[str, Any],
                              metadata: Dict[str, Any] = None) -> bool:
        """Update state in ArangoDB."""
        try:
            # Get existing document
            existing = await self.arango_adapter.get_document(self.arango_collection, state_id)
            if not existing:
                return False
            
            # Update state data
            updated_state = existing.get('state_data', {})
            updated_state.update(updates)
            
            # Update metadata
            updated_metadata = existing.get('metadata', {})
            if metadata:
                updated_metadata.update(metadata)
            updated_metadata['updated_at'] = datetime.utcnow().isoformat()
            
            # Update document
            updated_doc = {
                "state_data": updated_state,
                "metadata": updated_metadata,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            await self.arango_adapter.update_document(self.arango_collection, state_id, updated_doc)
            self.logger.debug(f"State updated in ArangoDB: {state_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error updating state in ArangoDB {state_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _update_in_redis(self, state_id: str, updates: Dict[str, Any],
                             metadata: Dict[str, Any] = None) -> bool:
        """Update state in Redis."""
        try:
            redis_key = f"{self.redis_prefix}{state_id}"
            existing = await self.redis_adapter.get_json(redis_key)
            if not existing:
                return False
            
            # Update state data
            updated_state = existing.get('state_data', {})
            updated_state.update(updates)
            
            # Update metadata
            updated_metadata = existing.get('metadata', {})
            if metadata:
                updated_metadata.update(metadata)
            updated_metadata['updated_at'] = datetime.utcnow().isoformat()
            
            # Update in Redis
            updated_data = {
                "state_data": updated_state,
                "metadata": updated_metadata,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            success = await self.redis_adapter.set_json(redis_key, updated_data)
            if success:
                self.logger.debug(f"State updated in Redis: {state_id}")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error updating state in Redis {state_id}: {e}")
            raise  # Re-raise for service layer to handle

    async def _update_in_memory(self, state_id: str, updates: Dict[str, Any],
                             metadata: Dict[str, Any] = None) -> bool:
        """Update state in memory."""
        try:
            if state_id not in self.memory_states:
                return False
            
            # Update state data
            state_info = self.memory_states[state_id]
            updated_state = state_info.get('state_data', {})
            updated_state.update(updates)
            
            # Update metadata
            updated_metadata = state_info.get('metadata', {})
            if metadata:
                updated_metadata.update(metadata)
            updated_metadata['updated_at'] = datetime.utcnow().isoformat()
            
            # Update in memory
            self.memory_states[state_id] = {
                "state_data": updated_state,
                "metadata": updated_metadata,
                "created_at": state_info['created_at'],
                "ttl": state_info.get('ttl')
            }
            
            self.logger.debug(f"State updated in memory: {state_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error updating state in memory {state_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def delete_state(self, state_id: str) -> bool:
        """
        Delete state data from storage.
        
        Deletes from all backends where it might exist.
        """
        try:
            # Delete from all backends
            arango_success = await self.arango_adapter.delete_document(self.arango_collection, state_id)
            redis_success = await self.redis_adapter.delete_string(f"{self.redis_prefix}{state_id}")
            memory_success = state_id in self.memory_states
            if memory_success:
                del self.memory_states[state_id]
            
            # Return True if deleted from any backend
            success = arango_success or redis_success or memory_success
            if success:
                self.logger.debug(f"State deleted: {state_id}")
            else:
                self.logger.warning(f"State not found for deletion: {state_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to delete state {state_id}: {e}")
            raise  # Re-raise for service layer to handle

    async def list_states(self, filters: Dict[str, Any] = None,
                         limit: int = None) -> List[Dict[str, Any]]:
        """
        List states matching the given criteria.
        
        Searches across all backends and combines results.
        """
        try:
            states = []
            
            # Search ArangoDB
            arango_states = await self._list_from_arango(filters, limit, offset)
            states.extend(arango_states)
            
            # Search Redis
            redis_states = await self._list_from_redis(filters, limit, offset)
            states.extend(redis_states)
            
            # Search memory
            memory_states = await self._list_from_memory(filters, limit, offset)
            states.extend(memory_states)
            
            # Remove duplicates and apply limits
            unique_states = list({state['state_id']: state for state in states}.values())
            
            if limit:
                unique_states = unique_states[offset or 0:offset + limit if offset else limit]
            
            self.logger.debug(f"Listed {len(unique_states)} states")
            
            return unique_states
            
        except Exception as e:
            self.logger.error(f"❌ Failed to list states: {e}")
            raise  # Re-raise for service layer to handle

    async def _list_from_arango(self, filters: Dict[str, Any] = None,
                              limit: int = None, offset: int = None) -> List[Dict[str, Any]]:
        """List states from ArangoDB."""
        try:
            # Build AQL query
            query = f"FOR doc IN {self.arango_collection}"
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(f"doc.{key} == @{key}")
                if conditions:
                    query += f" FILTER {' AND '.join(conditions)}"
            
            query += " RETURN {state_id: doc._key, state_data: doc.state_data, metadata: doc.metadata}"
            
            if limit:
                query += f" LIMIT {offset or 0}, {limit}"
            
            # Execute query
            bind_vars = filters or {}
            results = await self.arango_adapter.execute_aql(query, bind_vars)
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error listing states from ArangoDB: {e}")
            raise  # Re-raise for service layer to handle

    async def _limit(self, int = None, offset: int = None) -> List[Dict[str, Any]]:
        """List states from Redis."""
        try:
            # Get all keys with prefix
            pattern = f"{self.redis_prefix}*"
            keys = await self.redis_adapter.get_keys(pattern)
            
            states = []
            for key in keys:
                state_data = await self.redis_adapter.get_json(key)
                if state_data:
                    state_id = key.replace(self.redis_prefix, "")
                    states.append({
                        "state_id": state_id,
                        "state_data": state_data.get('state_data', {}),
                        "metadata": state_data.get('metadata', {})
                    })
            
            # Apply filters
            if filters:
                filtered_states = []
                for state in states:
                    match = True
                    for key, value in filters.items():
                        if key in state['state_data'] and state['state_data'][key] != value:
                            match = False
                            break
                    if match:
                        filtered_states.append(state)
                states = filtered_states
            
            # Apply pagination
            if offset:
                states = states[offset:]
            if limit:
                states = states[:limit]
            
            return states
            
        except Exception as e:
            self.logger.error(f"❌ Error listing states from Redis: {e}")
            raise  # Re-raise for service layer to handle

    async def _limit(self, int = None, offset: int = None) -> List[Dict[str, Any]]:
        """List states from memory."""
        try:
            states = []
            for state_id, state_info in self.memory_states.items():
                states.append({
                    "state_id": state_id,
                    "state_data": state_info.get('state_data', {}),
                    "metadata": state_info.get('metadata', {})
                })
            
            # Apply filters
            if filters:
                filtered_states = []
                for state in states:
                    match = True
                    for key, value in filters.items():
                        if key in state['state_data'] and state['state_data'][key] != value:
                            match = False
                            break
                    if match:
                        filtered_states.append(state)
                states = filtered_states
            
            # Apply pagination
            if offset:
                states = states[offset:]
            if limit:
                states = states[:limit]
            
            return states
            
        except Exception as e:
            self.logger.error(f"❌ Error listing states from memory: {e}")
            raise  # Re-raise for service layer to handle

    async def _query(self, query: str,
                          fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search for states using a query string.
        
        Searches across all backends and combines results.
        """
        try:
            states = []
            
            # Search ArangoDB
            arango_states = await self._search_in_arango(query, fields, limit)
            states.extend(arango_states)
            
            # Search Redis
            redis_states = await self._search_in_redis(query, fields, limit)
            states.extend(redis_states)
            
            # Search memory
            memory_states = await self._search_in_memory(query, fields, limit)
            states.extend(memory_states)
            
            # Remove duplicates and apply limits
            unique_states = list({state['state_id']: state for state in states}.values())
            
            if limit:
                unique_states = unique_states[:limit]
            
            self.logger.debug(f"Found {len(unique_states)} states for query: {query}")
            
            return unique_states
            
        except Exception as e:
            self.logger.error(f"❌ Error querying states: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _search_in_arango(self, query: str, fields: List[str] = None, limit: int = None) -> List[Dict[str, Any]]:
        """Search states in ArangoDB."""
        try:
            # Build AQL query for text search
            search_fields = fields or ['state_data', 'metadata']
            conditions = []
            
            for field in search_fields:
                conditions.append(f"CONTAINS(doc.{field}, @query)")
            
            aql_query = f"""
            FOR doc IN {self.arango_collection}
            FILTER {' OR '.join(conditions)}
            RETURN {{state_id: doc._key, state_data: doc.state_data, metadata: doc.metadata}}
            """
            
            if limit:
                aql_query += f" LIMIT {limit}"
            
            bind_vars = {"query": query}
            results = await self.arango_adapter.execute_aql(aql_query, bind_vars)
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error searching states in ArangoDB: {e}")
            raise  # Re-raise for service layer to handle

    async def _limit(self, int = None) -> List[Dict[str, Any]]:
        """Search states in Redis."""
        try:
            # Get all keys with prefix
            pattern = f"{self.redis_prefix}*"
            keys = await self.redis_adapter.get_keys(pattern)
            
            states = []
            for key in keys:
                state_data = await self.redis_adapter.get_json(key)
                if state_data:
                    # Simple text search in state data
                    state_text = json.dumps(state_data, default=str).lower()
                    if query.lower() in state_text:
                        state_id = key.replace(self.redis_prefix, "")
                        states.append({
                            "state_id": state_id,
                            "state_data": state_data.get('state_data', {}),
                            "metadata": state_data.get('metadata', {})
                        })
            
            if limit:
                states = states[:limit]
            
            return states
            
        except Exception as e:
            self.logger.error(f"❌ Error searching states in Redis: {e}")
            raise  # Re-raise for service layer to handle

    async def _limit(self, int = None) -> List[Dict[str, Any]]:
        """Search states in memory."""
        try:
            states = []
            for state_id, state_info in self.memory_states.items():
                # Simple text search in state data
                state_text = json.dumps(state_info, default=str).lower()
                if query.lower() in state_text:
                    states.append({
                        "state_id": state_id,
                        "state_data": state_info.get('state_data', {}),
                        "metadata": state_info.get('metadata', {})
                    })
            
            if limit:
                states = states[:limit]
            
            return states
            
        except Exception as e:
            self.logger.error(f"❌ Error searching states in memory: {e}")
            raise  # Re-raise for service layer to handle
        """Get metadata for a specific state."""
        # Get utilities from DI container
        error_handler = None
        try:
            # Try to get from ArangoDB first
            arango_result = await self.arango_adapter.get_document(self.arango_collection, state_id)
            if arango_result:
                return arango_result.get('metadata')
            
            # Try to get from Redis
            redis_key = f"{self.redis_prefix}{state_id}"
            redis_result = await self.redis_adapter.get_json(redis_key)
            if redis_result:
                return redis_result.get('metadata')
            
            # Try to get from memory
            if state_id in self.memory_states:
                return self.memory_states[state_id].get('metadata')
            
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get state metadata {state_id}: {e}")
            raise  # Re-raise for service layer to handle

    async def update_state_metadata(self, state_id: str,
                                   metadata: Dict[str, Any]) -> bool:
        """Update metadata for a specific state."""
        try:
            # Try to update in ArangoDB first
            arango_success = await self._update_metadata_in_arango(state_id, metadata)
            if arango_success:
                return True
            
            # Try to update in Redis
            redis_success = await self._update_metadata_in_redis(state_id, metadata)
            if redis_success:
                return True
            
            # Try to update in memory
            memory_success = await self._update_metadata_in_memory(state_id, metadata)
            if memory_success:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update state metadata {state_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def _update_metadata_in_arango(self, state_id: str, metadata: Dict[str, Any]) -> bool:
        """Update metadata in ArangoDB."""
        try:
            existing = await self.arango_adapter.get_document(self.arango_collection, state_id)
            if not existing:
                return False
            
            updated_metadata = existing.get('metadata', {})
            updated_metadata.update(metadata)
            updated_metadata['updated_at'] = datetime.utcnow().isoformat()
            
            await self.arango_adapter.update_document(self.arango_collection, state_id, {
                "metadata": updated_metadata,
                "updated_at": datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error updating metadata in ArangoDB {state_id}: {e}")
            raise  # Re-raise for service layer to handle
        """Update metadata in Redis."""
        try:
            redis_key = f"{self.redis_prefix}{state_id}"
            existing = await self.redis_adapter.get_json(redis_key)
            if not existing:
                return False
            
            updated_metadata = existing.get('metadata', {})
            updated_metadata.update(metadata)
            updated_metadata['updated_at'] = datetime.utcnow().isoformat()
            
            existing['metadata'] = updated_metadata
            existing['updated_at'] = datetime.utcnow().isoformat()
            
            await self.redis_adapter.set_json(redis_key, existing)
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error updating metadata in Redis {state_id}: {e}")
            raise  # Re-raise for service layer to handle
        """Update metadata in memory."""
        try:
            if state_id not in self.memory_states:
                return False
            
            updated_metadata = self.memory_states[state_id].get('metadata', {})
            updated_metadata.update(metadata)
            updated_metadata['updated_at'] = datetime.utcnow().isoformat()
            
            self.memory_states[state_id]['metadata'] = updated_metadata
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error updating metadata in memory {state_id}: {e}")
            raise  # Re-raise for service layer to handle
        """Get the history of changes for a specific state."""
        # Get utilities from DI container
        error_handler = None
        try:
            # For now, return basic history from metadata
            metadata = await self.get_state_metadata(state_id)
            if metadata:
                history = []
                if 'created_at' in metadata:
                    history.append({
                        "timestamp": metadata['created_at'],
                        "action": "created",
                        "details": "State created"
                    })
                if 'updated_at' in metadata:
                    history.append({
                        "timestamp": metadata['updated_at'],
                        "action": "updated",
                        "details": "State updated"
                    })
                return history
            
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get state history {state_id}: {e}")
            raise  # Re-raise for service layer to handle
    
    async def create_state_backup(self, state_id: str) -> Dict[str, Any]:
        """Create a backup of state data."""
        try:
            # Get state data
            state_data = await self.retrieve_state(state_id)
            if not state_data:
                raise  # Re-raise for service layer to handle
            backup_doc = {
                "_key": backup_id,
                "original_state_id": state_id,
                "state_data": state_data,
                "backup_timestamp": datetime.utcnow().isoformat(),
                "backup_type": "manual"
            }
            
            await self.arango_adapter.create_document("state_backups", backup_doc)
            self.logger.debug(f"State backup created: {backup_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create state backup: {e}")
            raise  # Re-raise for service layer to handle
    
    async def restore_state_backup(self, backup_id: str) -> bool:
        """Restore state data from a backup."""
        try:
            backup_doc = await self.arango_adapter.get_document("state_backups", backup_id)
            if not backup_doc:
                return False
            
            # Restore state
            restored_state = backup_doc.get('state_data')
            if restored_state:
                # Store in appropriate backend based on original metadata
                metadata = await self.get_state_metadata(state_id)
                success = await self.store_state(state_id, restored_state, metadata)
                
                if success:
                    self.logger.debug(f"State restored from backup: {backup_id}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to restore state backup: {e}")
            raise  # Re-raise for service layer to handle
    
    async def get_state_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored states."""
        try:
            # Count states in each backend
            arango_count = len(await self._list_from_arango())
            redis_count = len(await self._list_from_redis())
            memory_count = len(self.memory_states)
            
            total_states = arango_count + redis_count + memory_count
            
            statistics = {
                "total_states": total_states,
                "arango_states": arango_count,
                "redis_states": redis_count,
                "memory_states": memory_count,
                "backends": {
                    "arango_db": {"count": arango_count, "type": "persistent"},
                    "redis": {"count": redis_count, "type": "session"},
                    "memory": {"count": memory_count, "type": "cache"}
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.logger.debug(f"State statistics: {total_states} total states")
            return statistics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get state statistics: {e}")
            raise  # Re-raise for service layer to handle
    
    async def cleanup_expired_states(self) -> int:
        """Clean up expired state data."""
        try:
            cleaned_count = 0
            
            # Clean up memory states
            current_time = datetime.utcnow()
            expired_memory_states = []
            
            for state_id, state_info in self.memory_states.items():
                if state_info.get('ttl'):
                    created_at = datetime.fromisoformat(state_info['created_at'])
                    if current_time - created_at > timedelta(seconds=state_info['ttl']):
                        expired_memory_states.append(state_id)
            
            for state_id in expired_memory_states:
                del self.memory_states[state_id]
                cleaned_count += 1
            
            self.logger.debug(f"Cleaned up {cleaned_count} expired states")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup expired states: {e}")
            raise  # Re-raise for service layer to handle
    
    async def migrate_state(self, state_id: str,
                          target_backend: str) -> bool:
        """Migrate state data to a different backend."""
        try:
            state_data = await self.retrieve_state(state_id)
            if not state_data:
                raise  # Re-raise for service layer to handle
            if not metadata:
                metadata = {}
            
            # Update metadata for target backend
            metadata['backend'] = target_backend
            metadata['migrated_at'] = datetime.utcnow().isoformat()
            
            # Store in target backend
            success = await self.store_state(state_id, state_data, metadata)
            
            if success:
                # Delete from old backend (this is simplified - in practice you'd track the old backend)
                await self.delete_state(state_id)
                self.logger.debug(f"State migrated to {target_backend}: {state_id}")
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Failed to migrate state {state_id}: {e}")
            raise  # Re-raise for service layer to handle