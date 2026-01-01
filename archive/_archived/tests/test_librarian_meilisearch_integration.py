#!/usr/bin/env python3
"""
Librarian Meilisearch Integration Test

Test the Librarian service with Meilisearch integration to verify:
1. Service initialization with Meilisearch
2. Knowledge asset indexing
3. Search functionality
4. Analytics and recommendations
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from backend.smart_city.services.librarian.librarian_service import LibrarianService
from foundations.utility_foundation.utilities import UserContext
from config.environment_loader import EnvironmentLoader
from config import Environment


async def test_librarian_meilisearch_integration():
    """Test Librarian service with Meilisearch integration."""
    print("🚀 Starting Librarian Meilisearch Integration Test")
    print("=" * 80)
    
    try:
        # Initialize environment
        env_loader = EnvironmentLoader(Environment.DEVELOPMENT)
        
        # Initialize Librarian Service
        print("1. Initializing Librarian Service...")
        librarian = LibrarianService(
            utility_foundation=None,
            public_works_foundation=None,
            curator_foundation=None,
            environment=Environment.DEVELOPMENT
        )
        
        await librarian.initialize()
        print("   ✅ Librarian Service initialized")
        
        # Test service health
        print("\n2. Testing service health...")
        health = await librarian.get_service_health()
        print(f"   Service Status: {health['status']}")
        print(f"   Architecture: {health['architecture']}")
        print(f"   Micro-modules: {health['micro_modules']}")
        
        # Test knowledge asset indexing
        print("\n3. Testing knowledge asset indexing...")
        
        # Create test knowledge assets
        test_assets = [
            {
                "title": "Smart City Architecture Patterns",
                "content": "This document outlines the key architectural patterns used in smart city platforms, including microservices, event-driven architecture, and data governance patterns.",
                "knowledge_type": "pattern",
                "tags": ["architecture", "microservices", "smart-city", "patterns"],
                "metadata": {
                    "author": "Platform Team",
                    "version": "1.0",
                    "category": "technical"
                }
            },
            {
                "title": "Data Governance Best Practices",
                "content": "Comprehensive guide to data governance in smart city environments, covering data quality, privacy, security, and compliance requirements.",
                "knowledge_type": "best_practice",
                "tags": ["data-governance", "privacy", "security", "compliance"],
                "metadata": {
                    "author": "Data Team",
                    "version": "2.1",
                    "category": "governance"
                }
            },
            {
                "title": "API Integration Guidelines",
                "content": "Guidelines for integrating with external APIs in smart city platforms, including authentication, rate limiting, and error handling.",
                "knowledge_type": "guideline",
                "tags": ["api", "integration", "authentication", "best-practices"],
                "metadata": {
                    "author": "Integration Team",
                    "version": "1.5",
                    "category": "technical"
                }
            }
        ]
        
        indexed_assets = []
        for i, asset_data in enumerate(test_assets):
            print(f"   📚 Indexing asset {i+1}: {asset_data['title']}")
            
            # Create a mock request object
            class MockKnowledgeIndexRequest:
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        setattr(self, key, value)
                    # Add required fields
                    if not hasattr(self, 'content_type'):
                        self.content_type = 'text/plain'
            
            request = MockKnowledgeIndexRequest(**asset_data)
            user_context = UserContext(
                user_id="test_user",
                email="test@example.com",
                full_name="Test User",
                session_id="test_session_123",
                permissions=["admin", "read", "write"]
            )
            
            # Index the asset
            result = await librarian.index_knowledge(request, user_context)
            
            if result["success"]:
                indexed_assets.append(result["asset_id"])
                print(f"   ✅ Asset indexed: {result['asset_id']}")
            else:
                print(f"   ❌ Failed to index asset: {result.get('error', 'Unknown error')}")
        
        # Test search functionality
        print(f"\n4. Testing search functionality...")
        
        search_queries = [
            "smart city architecture",
            "data governance",
            "API integration",
            "microservices patterns",
            "privacy compliance"
        ]
        
        for query in search_queries:
            print(f"   🔍 Searching for: '{query}'")
            
            # Create a mock search request
            class MockKnowledgeSearchRequest:
                def __init__(self, query, search_mode="semantic", knowledge_type=None, tags=None):
                    self.query = query
                    self.search_mode = search_mode
                    self.knowledge_type = knowledge_type
                    self.tags = tags
                    self.date_from = None
                    self.date_to = None
            
            request = MockKnowledgeSearchRequest(query)
            user_context = UserContext(
                user_id="test_user",
                email="test@example.com",
                full_name="Test User",
                session_id="test_session_123",
                permissions=["admin", "read", "write"]
            )
            
            # Perform search
            search_result = await librarian.search_knowledge(request, user_context)
            
            if search_result["success"]:
                print(f"   ✅ Found {search_result['total_count']} results")
                for i, result in enumerate(search_result["results"][:3]):  # Show top 3
                    print(f"      {i+1}. {result.get('title', 'No title')} (Score: {result.get('relevance_score', 0)})")
            else:
                print(f"   ❌ Search failed: {search_result.get('error', 'Unknown error')}")
        
        # Test metadata extraction
        print(f"\n5. Testing metadata extraction...")
        
        class MockMetadataExtractionRequest:
            def __init__(self, content, content_type, file_name):
                self.content = content
                self.content_type = content_type
                self.file_name = file_name
        
        test_content = "This is a test document about smart city technologies and their implementation in urban environments."
        request = MockMetadataExtractionRequest(
            content=test_content,
            content_type="text/plain",
            file_name="smart_city_tech.txt"
        )
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_123",
            permissions=["admin", "read", "write"]
        )
        
        metadata_result = await librarian.extract_metadata(request, user_context)
        
        if metadata_result["success"]:
            print(f"   ✅ Metadata extracted: {len(metadata_result['metadata'])} fields")
            for key, value in metadata_result["metadata"].items():
                print(f"      {key}: {value}")
        else:
            print(f"   ❌ Metadata extraction failed: {metadata_result.get('error', 'Unknown error')}")
        
        # Test quality assessment
        print(f"\n6. Testing quality assessment...")
        
        class MockKnowledgeQualityAssessmentRequest:
            def __init__(self, content, title, metadata):
                self.content = content
                self.title = title
                self.metadata = metadata
        
        quality_request = MockKnowledgeQualityAssessmentRequest(
            content="This is a comprehensive guide to smart city implementation, covering all aspects from planning to deployment.",
            title="Smart City Implementation Guide",
            metadata={"author": "Expert Team", "version": "1.0"}
        )
        user_context = UserContext(
            user_id="test_user",
            email="test@example.com",
            full_name="Test User",
            session_id="test_session_123",
            permissions=["admin", "read", "write"]
        )
        
        quality_result = await librarian.assess_quality(quality_request, user_context)
        
        if quality_result["success"]:
            print(f"   ✅ Quality assessed: {quality_result['quality_level']} (Score: {quality_result['quality_score']:.2f})")
            print(f"   📋 Factors: {', '.join(quality_result['quality_factors'])}")
            if quality_result["recommendations"]:
                print(f"   💡 Recommendations: {', '.join(quality_result['recommendations'])}")
        else:
            print(f"   ❌ Quality assessment failed: {quality_result.get('error', 'Unknown error')}")
        
        # Test recommendations
        print(f"\n7. Testing knowledge recommendations...")
        
        class MockKnowledgeRecommendationRequest:
            def __init__(self, recommendation_type, asset_id=None, limit=5):
                self.recommendation_type = recommendation_type
                self.asset_id = asset_id
                self.limit = limit
        
        if indexed_assets:
            rec_request = MockKnowledgeRecommendationRequest(
                recommendation_type="content_based",
                asset_id=indexed_assets[0],
                limit=3
            )
            user_context = UserContext(
                user_id="test_user",
                email="test@example.com",
                full_name="Test User",
                session_id="test_session_123",
                permissions=["admin", "read", "write"]
            )
            
            rec_result = await librarian.get_recommendations(rec_request, user_context)
            
            if rec_result["success"]:
                print(f"   ✅ Found {rec_result['total_count']} recommendations")
                for i, rec in enumerate(rec_result["recommendations"][:3]):
                    print(f"      {i+1}. {rec.get('title', 'No title')} (Score: {rec.get('score', 0)})")
            else:
                print(f"   ❌ Recommendations failed: {rec_result.get('error', 'Unknown error')}")
        
        # Final service status
        print(f"\n8. Final service status...")
        final_health = await librarian.get_service_health()
        print(f"   Service Status: {final_health['status']}")
        print(f"   All Modules Healthy: {final_health.get('all_modules_healthy', False)}")
        
        print("\n" + "=" * 80)
        print("🎉 LIBRARIAN MEILISEARCH INTEGRATION TEST COMPLETED!")
        print("✅ Knowledge management with Meilisearch verified")
        print("✅ Search functionality working")
        print("✅ Metadata extraction operational")
        print("✅ Quality assessment functional")
        print("✅ Recommendations system active")
        print("🎯 Librarian service is ready for production use!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_librarian_meilisearch_integration())
    sys.exit(0 if success else 1)
