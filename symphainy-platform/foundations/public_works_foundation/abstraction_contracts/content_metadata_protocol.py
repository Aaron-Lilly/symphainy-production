#!/usr/bin/env python3
"""
Content Metadata Protocol - Abstraction Contract

Defines the contract for content metadata operations.
This is Layer 2 of the 5-layer infrastructure architecture.

WHAT (Infrastructure Role): I define the contract for content metadata operations
HOW (Infrastructure Implementation): I provide abstract methods for content metadata
"""

from typing import Protocol, Dict, Any, List, Optional

class ContentMetadataProtocol(Protocol):
    """Protocol for content metadata operations."""
    
    # ============================================================================
    # CORE CONTENT METADATA OPERATIONS
    # ============================================================================
    
    async def create_content_metadata(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create content metadata document.
        
        Args:
            content_data: Content metadata and information
            
        Returns:
            Dict containing created content metadata information
        """
        ...
    
    async def get_content_metadata(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Get content metadata by ID.
        
        Args:
            content_id: Unique identifier for the content metadata
            
        Returns:
            Dict containing content metadata information or None if not found
        """
        ...
    
    async def update_content_metadata(self, content_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update content metadata document.
        
        Args:
            content_id: Unique identifier for the content metadata
            updates: Dictionary of fields to update
            
        Returns:
            Dict containing updated content metadata information
        """
        ...
    
    async def delete_content_metadata(self, content_id: str) -> bool:
        """
        Delete content metadata document.
        
        Args:
            content_id: Unique identifier for the content metadata
            
        Returns:
            bool indicating success
        """
        ...
    
    async def search_content_metadata(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search content metadata by various criteria.
        
        Args:
            query: Dictionary of search criteria
            
        Returns:
            List of matching content metadata records
        """
        ...
    
    # ============================================================================
    # CONTENT STRUCTURE OPERATIONS
    # ============================================================================
    
    async def analyze_content_structure(self, content_id: str) -> Dict[str, Any]:
        """
        Analyze content structure and extract insights.
        
        Args:
            content_id: Unique identifier for the content
            
        Returns:
            Dict containing content structure analysis
        """
        ...
    
    async def extract_content_schema(self, content_id: str) -> Dict[str, Any]:
        """
        Extract schema information from content.
        
        Args:
            content_id: Unique identifier for the content
            
        Returns:
            Dict containing extracted schema information
        """
        ...
    
    async def generate_content_insights(self, content_id: str) -> Dict[str, Any]:
        """
        Generate AI-friendly insights about content.
        
        Args:
            content_id: Unique identifier for the content
            
        Returns:
            Dict containing generated insights
        """
        ...
    
    # ============================================================================
    # CONTENT RELATIONSHIP OPERATIONS
    # ============================================================================
    
    async def create_content_relationship(self, parent_id: str, child_id: str, 
                                        relationship_type: str) -> Dict[str, Any]:
        """
        Create relationship between content metadata documents.
        
        Args:
            parent_id: UUID of parent content
            child_id: UUID of child content
            relationship_type: Type of relationship
            
        Returns:
            Dict containing relationship information
        """
        ...
    
    async def get_content_relationships(self, content_id: str, direction: str = "both") -> List[Dict[str, Any]]:
        """
        Get content relationships.
        
        Args:
            content_id: UUID of the content
            direction: "parent", "child", or "both"
            
        Returns:
            List of content relationship records
        """
        ...
    
    # ============================================================================
    # CONTENT ANALYSIS OPERATIONS
    # ============================================================================
    
    async def perform_content_analysis(self, content_id: str) -> Dict[str, Any]:
        """
        Perform comprehensive content analysis.
        
        Args:
            content_id: Unique identifier for the content
            
        Returns:
            Dict containing analysis results
        """
        ...
    
    async def search_content_by_pattern(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search content by structural patterns.
        
        Args:
            pattern: Dictionary of pattern criteria
            
        Returns:
            List of matching content records
        """
        ...
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of the content metadata system.
        
        Returns:
            Dict containing health status information
        """
        ...




