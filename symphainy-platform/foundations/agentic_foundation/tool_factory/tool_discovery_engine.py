"""
Tool Discovery Engine

This module handles intelligent tool discovery across all domains,
including caching, filtering, and search capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import json
import re

logger = logging.getLogger(__name__)


class ToolDiscoveryEngine:
    """
    Engine for discovering tools across all domains with intelligent
    caching, filtering, and search capabilities.
    """
    
    def __init__(self, tool_factory_service):
        """
        Initialize the Tool Discovery Engine.
        
        Args:
            tool_factory_service: Reference to the Tool Factory Service
        """
        self.tool_factory = tool_factory_service
        self.discovery_cache = {}
        self.search_index = {}
        self.cache_ttl = 600  # 10 minutes TTL for discovery cache
        
        logger.info("Tool Discovery Engine initialized")
    
    async def discover_tools_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """
        Discover tools by capability.
        
        Args:
            capability: Capability to search for (e.g., "data_analysis", "visualization")
            
        Returns:
            List of tools with the specified capability
        """
        try:
            cache_key = f"capability:{capability}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                logger.debug(f"Cache hit for capability: {capability}")
                return self.discovery_cache[cache_key]["tools"]
            
            logger.debug(f"Discovering tools for capability: {capability}")
            
            # Search all domains
            all_tools = []
            for domain, manager in self.tool_factory.domain_managers.items():
                try:
                    tools = await manager.get_public_tools({"capability": capability})
                    all_tools.extend(tools)
                    logger.debug(f"Found {len(tools)} tools with capability '{capability}' in {domain}")
                    
                except Exception as e:
                    logger.error(f"Error discovering tools in {domain} for capability '{capability}': {e}")
                    continue
            
            # Cache the results
            self.discovery_cache[cache_key] = {
                "tools": all_tools,
                "timestamp": datetime.now()
            }
            
            logger.info(f"Discovered {len(all_tools)} tools for capability: {capability}")
            return all_tools
            
        except Exception as e:
            logger.error(f"Error discovering tools by capability '{capability}': {e}")
            return []
    
    async def discover_tools_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Discover tools by domain.
        
        Args:
            domain: Domain to search in
            
        Returns:
            List of tools from the specified domain
        """
        try:
            cache_key = f"domain:{domain}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                logger.debug(f"Cache hit for domain: {domain}")
                return self.discovery_cache[cache_key]["tools"]
            
            logger.debug(f"Discovering tools for domain: {domain}")
            
            if domain not in self.tool_factory.domain_managers:
                logger.warning(f"Domain {domain} not registered")
                return []
            
            manager = self.tool_factory.domain_managers[domain]
            tools = await manager.get_public_tools({})
            
            # Cache the results
            self.discovery_cache[cache_key] = {
                "tools": tools,
                "timestamp": datetime.now()
            }
            
            logger.info(f"Discovered {len(tools)} tools in domain: {domain}")
            return tools
            
        except Exception as e:
            logger.error(f"Error discovering tools by domain '{domain}': {e}")
            return []
    
    async def search_tools(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search tools using text query and filters.
        
        Args:
            query: Text search query
            filters: Additional filters (domain, capability, etc.)
            
        Returns:
            List of matching tools
        """
        try:
            filters = filters or {}
            cache_key = f"search:{query}:{json.dumps(filters, sort_keys=True)}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                logger.debug(f"Cache hit for search: {query}")
                return self.discovery_cache[cache_key]["tools"]
            
            logger.debug(f"Searching tools with query: {query}")
            
            # Get all tools from all domains
            all_tools = []
            for domain, manager in self.tool_factory.domain_managers.items():
                try:
                    # Apply domain filter if specified
                    if "domain" in filters and filters["domain"] != domain:
                        continue
                    
                    tools = await manager.get_public_tools(filters)
                    all_tools.extend(tools)
                    
                except Exception as e:
                    logger.error(f"Error searching tools in {domain}: {e}")
                    continue
            
            # Apply text search
            matching_tools = self._apply_text_search(all_tools, query)
            
            # Cache the results
            self.discovery_cache[cache_key] = {
                "tools": matching_tools,
                "timestamp": datetime.now()
            }
            
            logger.info(f"Found {len(matching_tools)} tools matching query: {query}")
            return matching_tools
            
        except Exception as e:
            logger.error(f"Error searching tools with query '{query}': {e}")
            return []
    
    async def discover_related_tools(self, tool_name: str) -> List[Dict[str, Any]]:
        """
        Discover tools related to a specific tool.
        
        Args:
            tool_name: Name of the tool to find related tools for
            
        Returns:
            List of related tools
        """
        try:
            cache_key = f"related:{tool_name}"
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                logger.debug(f"Cache hit for related tools: {tool_name}")
                return self.discovery_cache[cache_key]["tools"]
            
            logger.debug(f"Discovering related tools for: {tool_name}")
            
            # Get tool info first
            tool_info = await self.tool_factory.get_tool_info(tool_name)
            if not tool_info:
                logger.warning(f"Tool {tool_name} not found")
                return []
            
            # Find tools with similar capabilities or from same domain
            related_tools = []
            
            # Search by capability
            if "capabilities" in tool_info:
                for capability in tool_info["capabilities"]:
                    capability_tools = await self.discover_tools_by_capability(capability)
                    related_tools.extend(capability_tools)
            
            # Search by domain
            domain_tools = await self.discover_tools_by_domain(tool_info["domain"])
            related_tools.extend(domain_tools)
            
            # Remove the original tool and duplicates
            related_tools = [
                tool for tool in related_tools 
                if tool["tool_name"] != tool_name
            ]
            
            # Remove duplicates based on tool_name
            seen = set()
            unique_related_tools = []
            for tool in related_tools:
                if tool["tool_name"] not in seen:
                    seen.add(tool["tool_name"])
                    unique_related_tools.append(tool)
            
            # Cache the results
            self.discovery_cache[cache_key] = {
                "tools": unique_related_tools,
                "timestamp": datetime.now()
            }
            
            logger.info(f"Found {len(unique_related_tools)} related tools for: {tool_name}")
            return unique_related_tools
            
        except Exception as e:
            logger.error(f"Error discovering related tools for '{tool_name}': {e}")
            return []
    
    def _apply_text_search(self, tools: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Apply text search to tools.
        
        Args:
            tools: List of tools to search
            query: Search query
            
        Returns:
            List of matching tools
        """
        try:
            query_lower = query.lower()
            matching_tools = []
            
            for tool in tools:
                # Search in tool name
                if query_lower in tool.get("tool_name", "").lower():
                    matching_tools.append(tool)
                    continue
                
                # Search in description
                if "description" in tool and query_lower in tool["description"].lower():
                    matching_tools.append(tool)
                    continue
                
                # Search in capabilities
                if "capabilities" in tool:
                    for capability in tool["capabilities"]:
                        if query_lower in capability.lower():
                            matching_tools.append(tool)
                            break
                
                # Search in tags
                if "tags" in tool:
                    for tag in tool["tags"]:
                        if query_lower in tag.lower():
                            matching_tools.append(tool)
                            break
            
            return matching_tools
            
        except Exception as e:
            logger.error(f"Error applying text search: {e}")
            return tools
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached discovery result is still valid."""
        if cache_key not in self.discovery_cache:
            return False
        
        age = datetime.now() - self.discovery_cache[cache_key]["timestamp"]
        return age < timedelta(seconds=self.cache_ttl)
    
    def clear_cache(self):
        """Clear the discovery cache."""
        self.discovery_cache.clear()
        self.search_index.clear()
        logger.info("Discovery cache cleared")
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get discovery cache statistics."""
        return {
            "cached_queries": len(self.discovery_cache),
            "cache_ttl": self.cache_ttl,
            "search_index_size": len(self.search_index)
        }






