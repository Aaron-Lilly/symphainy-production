"""
Test Insurance Use Case Agents

Tests for:
1. Insurance Liaison Agent - Conversational guidance
2. Universal Mapper Specialist Agent - Pattern learning and AI-assisted mapping

Uses mocked dependencies to test agent logic without requiring full infrastructure.
"""

import os
import sys
import asyncio
import uuid
from typing import Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import pytest

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
symphainy_platform_path = os.path.join(project_root, 'symphainy-platform')
sys.path.insert(0, symphainy_platform_path)


# ============================================================================
# MOCK SERVICES
# ============================================================================

class MockService:
    """Mock service for testing."""
    def __init__(self, name: str):
        self.name = name
    
    async def __getattr__(self, name):
        async def mock_method(*args, **kwargs):
            return {"success": True, "message": f"Mock {self.name}.{name} executed"}
        return mock_method


class MockDIContainer:
    """Mock DI container."""
    def __init__(self):
        self.services = {}
        self.utilities = {}
        self.config = {}
    
    def get_service(self, service_name: str):
        if "Librarian" in service_name:
            return MockService("Librarian")
        elif "CanonicalModelService" in service_name:
            return MockService("CanonicalModelService")
        elif "SchemaMapperService" in service_name:
            return MockService("SchemaMapperService")
        return MockService(service_name)
    
    def get_logger(self, name: str):
        import logging
        return logging.getLogger(name)
    
    def get_config(self):
        """Return mock config."""
        return self.config


class MockFoundationServices:
    """Mock foundation services."""
    def __init__(self):
        self.di_container = MockDIContainer()
        self.curator_foundation = None
        self.metadata_foundation = None


class MockAgenticFoundation:
    """Mock agentic foundation."""
    async def create_agent(self, **kwargs):
        return kwargs.get("agent_class")(
            foundation_services=kwargs.get("di_container"),
            agentic_foundation=self,
            mcp_client_manager=MagicMock(),
            policy_integration=MagicMock(),
            tool_composition=MagicMock(),
            agui_formatter=MagicMock(),
            curator_foundation=kwargs.get("curator_foundation"),
            metadata_foundation=kwargs.get("metadata_foundation"),
            logger=kwargs.get("logger")
        )


# ============================================================================
# TEST INSURANCE LIAISON AGENT
# ============================================================================

class TestInsuranceLiaisonAgent:
    """Test Insurance Liaison Agent."""
    
    @pytest.fixture
    async def liaison_agent(self):
        """Create Insurance Liaison Agent for testing."""
        from backend.business_enablement.agents.insurance_liaison_agent import InsuranceLiaisonAgent
        
        foundation_services = MockFoundationServices()
        agentic_foundation = MockAgenticFoundation()
        
        agent = InsuranceLiaisonAgent(
            foundation_services=foundation_services.di_container,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=MagicMock(),
            policy_integration=MagicMock(),
            tool_composition=MagicMock(),
            agui_formatter=MagicMock(),
            curator_foundation=None,
            metadata_foundation=None,
            logger=None
        )
        
        await agent.initialize()
        return agent
    
    @pytest.mark.asyncio
    async def test_liaison_agent_initialization(self, liaison_agent):
        """Test that liaison agent initializes correctly."""
        print("\n--- Test: Liaison Agent Initialization ---")
        
        assert liaison_agent is not None
        assert liaison_agent.domain_name == "insurance_migration"
        assert len(liaison_agent.domain_config.get("capabilities", [])) > 0
        assert len(liaison_agent.domain_config.get("mcp_tools", [])) > 0
        
        print("✅ Liaison agent initialized successfully")
        print(f"   Capabilities: {len(liaison_agent.domain_config.get('capabilities', []))}")
        print(f"   MCP Tools: {len(liaison_agent.domain_config.get('mcp_tools', []))}")
    
    @pytest.mark.asyncio
    async def test_ingestion_guidance(self, liaison_agent):
        """Test ingestion guidance response."""
        print("\n--- Test: Ingestion Guidance ---")
        
        guidance = liaison_agent._get_ingestion_guidance()
        
        assert guidance is not None
        assert isinstance(guidance, str)
        assert len(guidance) > 0
        assert "ingestion" in guidance.lower() or "upload" in guidance.lower()
        
        print("✅ Ingestion guidance generated")
        print(f"   Length: {len(guidance)} characters")
    
    @pytest.mark.asyncio
    async def test_mapping_guidance(self, liaison_agent):
        """Test mapping guidance response."""
        print("\n--- Test: Mapping Guidance ---")
        
        guidance = liaison_agent._get_mapping_guidance()
        
        assert guidance is not None
        assert isinstance(guidance, str)
        assert len(guidance) > 0
        assert "mapping" in guidance.lower() or "canonical" in guidance.lower()
        
        print("✅ Mapping guidance generated")
    
    @pytest.mark.asyncio
    async def test_wave_guidance(self, liaison_agent):
        """Test wave planning guidance response."""
        print("\n--- Test: Wave Planning Guidance ---")
        
        guidance = liaison_agent._get_wave_guidance()
        
        assert guidance is not None
        assert isinstance(guidance, str)
        assert len(guidance) > 0
        assert "wave" in guidance.lower()
        
        print("✅ Wave planning guidance generated")
    
    @pytest.mark.asyncio
    async def test_tracking_guidance(self, liaison_agent):
        """Test policy tracking guidance response."""
        print("\n--- Test: Policy Tracking Guidance ---")
        
        guidance = liaison_agent._get_tracking_guidance()
        
        assert guidance is not None
        assert isinstance(guidance, str)
        assert len(guidance) > 0
        assert "track" in guidance.lower() or "policy" in guidance.lower()
        
        print("✅ Policy tracking guidance generated")
    
    @pytest.mark.asyncio
    async def test_general_guidance(self, liaison_agent):
        """Test general guidance response."""
        print("\n--- Test: General Guidance ---")
        
        guidance = liaison_agent._get_general_guidance()
        
        assert guidance is not None
        assert isinstance(guidance, str)
        assert len(guidance) > 0
        
        print("✅ General guidance generated")
    
    @pytest.mark.asyncio
    async def test_suggested_actions(self, liaison_agent):
        """Test suggested actions generation."""
        print("\n--- Test: Suggested Actions ---")
        
        actions = liaison_agent._get_suggested_actions("ingest")
        
        assert actions is not None
        assert isinstance(actions, list)
        assert len(actions) > 0
        
        print(f"✅ Suggested actions generated: {len(actions)} actions")
        for action in actions:
            print(f"   - {action}")


# ============================================================================
# TEST UNIVERSAL MAPPER SPECIALIST AGENT
# ============================================================================

class TestUniversalMapperSpecialist:
    """Test Universal Mapper Specialist Agent."""
    
    @pytest.fixture
    async def mapper_agent(self):
        """Create Universal Mapper Specialist Agent for testing."""
        from backend.business_enablement.agents.specialists.universal_mapper_specialist import UniversalMapperSpecialist
        
        foundation_services = MockFoundationServices()
        agentic_foundation = MockAgenticFoundation()
        
        # Mock Librarian
        mock_librarian = AsyncMock()
        mock_librarian.store_knowledge = AsyncMock(return_value="pattern_123")
        mock_librarian.get_knowledge_item = AsyncMock(return_value={"data": {"pattern_id": "pattern_123"}})
        
        # Mock Canonical Model Service
        mock_canonical = AsyncMock()
        mock_canonical.get_canonical_model = AsyncMock(return_value={
            "success": True,
            "model": {
                "schema": {
                    "name": "policy_v1",
                    "fields": [
                        {"name": "policy_id", "type": "string"},
                        {"name": "premium", "type": "number"},
                        {"name": "status", "type": "string"}
                    ]
                }
            }
        })
        
        agent = UniversalMapperSpecialist(
            foundation_services=foundation_services.di_container,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=MagicMock(),
            policy_integration=MagicMock(),
            tool_composition=MagicMock(),
            agui_formatter=MagicMock(),
            curator_foundation=None,
            metadata_foundation=None,
            logger=None
        )
        
        # Set mocked services
        agent.librarian = mock_librarian
        agent.canonical_model_service = mock_canonical
        
        await agent.initialize()
        return agent
    
    @pytest.mark.asyncio
    async def test_mapper_agent_initialization(self, mapper_agent):
        """Test that mapper agent initializes correctly."""
        print("\n--- Test: Mapper Agent Initialization ---")
        
        assert mapper_agent is not None
        assert mapper_agent.capability_name == "universal_mapping"
        assert mapper_agent.knowledge_base_namespace == "universal_mapping_kb"
        
        print("✅ Mapper agent initialized successfully")
    
    @pytest.mark.asyncio
    async def test_learn_from_mappings(self, mapper_agent):
        """Test learning from mappings."""
        print("\n--- Test: Learn From Mappings ---")
        
        source_schema = {
            "name": "legacy_policy",
            "fields": [
                {"name": "pol_id", "type": "string"},
                {"name": "prem_amt", "type": "number"}
            ]
        }
        
        target_schema = {
            "name": "policy_v1",
            "fields": [
                {"name": "policy_id", "type": "string"},
                {"name": "premium", "type": "number"}
            ]
        }
        
        mapping_rules = {
            "rules": [
                {"source": "pol_id", "target": "policy_id", "transformation": "direct"},
                {"source": "prem_amt", "target": "premium", "transformation": "direct"}
            ]
        }
        
        result = await mapper_agent.learn_from_mappings(
            source_schema=source_schema,
            target_schema=target_schema,
            mapping_rules=mapping_rules,
            client_id="client_001",
            mapping_metadata={"accuracy": 0.9, "quality_score": 0.85}
        )
        
        assert result["success"] is True
        assert "pattern_id" in result
        assert result["patterns_learned"] > 0
        assert result["confidence"] > 0.0
        
        print(f"✅ Learned {result['patterns_learned']} patterns")
        print(f"   Pattern ID: {result['pattern_id']}")
        print(f"   Confidence: {result['confidence']:.2f}")
    
    @pytest.mark.asyncio
    async def test_suggest_mappings(self, mapper_agent):
        """Test mapping suggestions."""
        print("\n--- Test: Suggest Mappings ---")
        
        # First, learn some patterns
        source_schema = {
            "name": "legacy_policy",
            "fields": [
                {"name": "pol_id", "type": "string"},
                {"name": "prem_amt", "type": "number"}
            ]
        }
        
        target_schema = {
            "name": "policy_v1",
            "fields": [
                {"name": "policy_id", "type": "string"},
                {"name": "premium", "type": "number"}
            ]
        }
        
        mapping_rules = {
            "rules": [
                {"source": "pol_id", "target": "policy_id", "transformation": "direct"},
                {"source": "prem_amt", "target": "premium", "transformation": "direct"}
            ]
        }
        
        await mapper_agent.learn_from_mappings(
            source_schema=source_schema,
            target_schema=target_schema,
            mapping_rules=mapping_rules,
            client_id="client_001"
        )
        
        # Now suggest mappings for a similar schema
        new_source_schema = {
            "name": "new_legacy_policy",
            "fields": [
                {"name": "policy_id", "type": "string"},
                {"name": "premium_amount", "type": "number"}
            ]
        }
        
        result = await mapper_agent.suggest_mappings(
            source_schema=new_source_schema,
            target_schema_name="policy_v1",
            client_id="client_001"
        )
        
        assert result["success"] is True
        assert "suggestions" in result
        assert len(result["suggestions"]) > 0
        assert result["total_suggestions"] > 0
        
        print(f"✅ Generated {result['total_suggestions']} mapping suggestions")
        print(f"   Highest confidence: {result['highest_confidence']:.2f}")
        for suggestion in result["suggestions"][:3]:
            print(f"   - {suggestion.get('source_field')} -> {suggestion.get('target_field')} (confidence: {suggestion.get('confidence', 0):.2f})")
    
    @pytest.mark.asyncio
    async def test_validate_mappings(self, mapper_agent):
        """Test mapping validation."""
        print("\n--- Test: Validate Mappings ---")
        
        source_schema = {
            "name": "legacy_policy",
            "fields": [
                {"name": "pol_id", "type": "string"},
                {"name": "prem_amt", "type": "number"}
            ]
        }
        
        target_schema = {
            "name": "policy_v1",
            "fields": [
                {"name": "policy_id", "type": "string"},
                {"name": "premium", "type": "number"}
            ]
        }
        
        mapping_rules = {
            "rules": [
                {"source": "pol_id", "target": "policy_id", "transformation": "direct"},
                {"source": "prem_amt", "target": "premium", "transformation": "direct"}
            ]
        }
        
        result = await mapper_agent.validate_mappings(
            source_schema=source_schema,
            target_schema=target_schema,
            mapping_rules=mapping_rules
        )
        
        assert result["success"] is True
        assert "is_valid" in result
        assert "completeness" in result
        assert "correctness" in result
        assert "pattern_validation" in result
        assert "recommendations" in result
        
        print(f"✅ Validation complete")
        print(f"   Valid: {result['is_valid']}")
        print(f"   Completeness: {result['completeness']['is_complete']}")
        print(f"   Correctness: {result['correctness']['is_correct']}")
        print(f"   Confidence: {result.get('confidence', 0):.2f}")
        if result["recommendations"]:
            print(f"   Recommendations: {len(result['recommendations'])}")
    
    @pytest.mark.asyncio
    async def test_learn_from_correction(self, mapper_agent):
        """Test learning from corrections."""
        print("\n--- Test: Learn From Correction ---")
        
        original_mapping = {
            "source_field": "pol_id",
            "target_field": "policy_number",
            "transformation": "direct"
        }
        
        corrected_mapping = {
            "source_field": "pol_id",
            "target_field": "policy_id",
            "transformation": "direct"
        }
        
        # Test with approval
        result = await mapper_agent.learn_from_correction(
            original_mapping=original_mapping,
            corrected_mapping=corrected_mapping,
            correction_reason="Field name mismatch",
            approve_learning=True
        )
        
        assert result["success"] is True
        assert result["learned"] is True
        assert "pattern_id" in result
        
        print(f"✅ Learned from correction (approved)")
        print(f"   Pattern ID: {result['pattern_id']}")
        
        # Test without approval
        result_no_approval = await mapper_agent.learn_from_correction(
            original_mapping=original_mapping,
            corrected_mapping=corrected_mapping,
            correction_reason="Field name mismatch",
            approve_learning=False
        )
        
        assert result_no_approval["success"] is True
        assert result_no_approval["learned"] is False
        
        print(f"✅ Skipped learning (not approved)")
    
    @pytest.mark.asyncio
    async def test_semantic_similarity(self, mapper_agent):
        """Test semantic similarity calculation."""
        print("\n--- Test: Semantic Similarity ---")
        
        # Test exact match
        similarity = mapper_agent._calculate_semantic_similarity("policy_id", "policy_id")
        assert similarity == 1.0
        print(f"✅ Exact match: {similarity:.2f}")
        
        # Test partial match
        similarity = mapper_agent._calculate_semantic_similarity("pol_id", "policy_id")
        assert similarity > 0.0
        print(f"✅ Partial match: {similarity:.2f}")
        
        # Test different fields
        similarity = mapper_agent._calculate_semantic_similarity("policy_id", "premium")
        assert similarity < 0.5
        print(f"✅ Different fields: {similarity:.2f}")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestAgentIntegration:
    """Test agent integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_liaison_to_mapper_flow(self):
        """Test flow from liaison agent to mapper agent."""
        print("\n--- Test: Liaison to Mapper Flow ---")
        
        # This would test the full flow:
        # 1. User asks liaison agent about mapping
        # 2. Liaison routes to mapper agent
        # 3. Mapper suggests mappings
        # 4. Results returned to user
        
        # For now, just verify both agents can be instantiated
        from backend.business_enablement.agents.insurance_liaison_agent import InsuranceLiaisonAgent
        from backend.business_enablement.agents.specialists.universal_mapper_specialist import UniversalMapperSpecialist
        
        foundation_services = MockFoundationServices()
        agentic_foundation = MockAgenticFoundation()
        
        liaison = InsuranceLiaisonAgent(
            foundation_services=foundation_services.di_container,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=MagicMock(),
            policy_integration=MagicMock(),
            tool_composition=MagicMock(),
            agui_formatter=MagicMock()
        )
        
        mapper = UniversalMapperSpecialist(
            foundation_services=foundation_services.di_container,
            agentic_foundation=agentic_foundation,
            mcp_client_manager=MagicMock(),
            policy_integration=MagicMock(),
            tool_composition=MagicMock(),
            agui_formatter=MagicMock()
        )
        
        assert liaison is not None
        assert mapper is not None
        
        print("✅ Both agents can be instantiated together")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

