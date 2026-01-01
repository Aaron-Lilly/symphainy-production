# 🤖 Agentic/AI Testing Strategy

**Date:** November 8, 2024  
**Priority:** 🔴 **CRITICAL - CORE VALUE PROPOSITION**  
**Status:** ✅ **COMPREHENSIVE STRATEGY READY**

---

## 🎯 The Challenge

**User Question:** "How are we accounting for/mocking agentic interaction? That's critical for business analysis and interactive SOP generation."

**The Problem:**
```
Traditional Testing:
Input → Function → Output (deterministic)
✅ Easy to test

Agentic Testing:
Input → AI/Agent → Output (non-deterministic)
❌ Hard to test:
  - Non-deterministic output
  - Slow (API calls)
  - Expensive (API costs)
  - Requires API keys
  - Quality varies
```

---

## 🎨 Testing Strategy Overview

**Hybrid Approach (RECOMMENDED):**

```
┌─────────────────────────────────────────────────────────────────┐
│                    TEST PYRAMID FOR AI                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                    [Slow, Expensive]                             │
│                    Real AI Tests                                 │
│                  (Functional/E2E)                                │
│                 Use Actual API Keys                              │
│              Test Quality & Integration                          │
│                                                                  │
│              ─────────────────────────                           │
│                                                                  │
│                 Contract Tests                                   │
│            Test AI Input/Output Handling                         │
│            Cached Responses (Golden Tests)                       │
│                                                                  │
│          ───────────────────────────────────                     │
│                                                                  │
│                Mock AI Tests                                     │
│           Fast, Deterministic Responses                          │
│         Test Business Logic, Not AI Quality                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Recommended Approach

### **Your Suggestion is CORRECT!**

> "I'm even open to adding the AI API secrets to our test environment so we can use actual AI"

**YES - This is the right approach for functional tests!**

**Why:**
1. ✅ Tests actual functionality (not mocks)
2. ✅ Catches quality issues
3. ✅ Validates AI prompt engineering
4. ✅ Tests real user experience
5. ✅ Builds confidence for production

**With Safeguards:**
1. ✅ Use cheaper models for testing (GPT-3.5-turbo)
2. ✅ Rate limit test execution
3. ✅ Cache responses for repeated runs
4. ✅ Have mock fallbacks
5. ✅ Budget alerts

---

## 🏗️ Implementation Strategy

### **Layer 1: Testing Protocol (Aligned with Platform Architecture)**

**IMPORTANT:** Your platform uses **Base Classes + Protocols** pattern, not Interfaces!

**Existing Architecture:**
- `AgentBase` - Base class with full foundation integration
- Agent Protocols - Define contracts for specific agent types
- Specific agents inherit from AgentBase and implement protocols

**Testing Strategy (Aligned):**

```python
# tests/fixtures/testing_agent_protocol.py

from typing import Protocol, Dict, Any
from dataclasses import dataclass

@dataclass
class AgentResponse:
    """Standardized response from any agent"""
    content: str | Dict[str, Any]
    response_type: str
    metadata: Dict[str, Any]
    confidence: float | None = None


class TestableAgentProtocol(Protocol):
    """
    Protocol for agents in testing scenarios.
    Defines minimal contract for test doubles.
    
    NOTE: This is ONLY for testing - production agents use AgentBase!
    """
    
    async def generate_sop(self, context: Dict[str, Any]) -> AgentResponse:
        """Generate SOP document"""
        ...
    
    async def generate_workflow(self, context: Dict[str, Any]) -> AgentResponse:
        """Generate workflow diagram"""
        ...
    
    async def generate_roadmap(self, context: Dict[str, Any]) -> AgentResponse:
        """Generate strategic roadmap"""
        ...
    
    async def generate_poc_proposal(self, context: Dict[str, Any]) -> AgentResponse:
        """Generate POC proposal"""
        ...
    
    async def analyze_data(self, data: Dict[str, Any], analysis_type: str) -> AgentResponse:
        """Analyze data and provide insights"""
        ...
    
    async def chat(self, message: str, history: list, context: Dict[str, Any]) -> AgentResponse:
        """Handle conversational interaction"""
        ...
```

```python
# tests/fixtures/mock_agent.py

from typing import Dict, Any
from tests.fixtures.testing_agent_protocol import TestableAgentProtocol, AgentResponse


class MockAgent:
    """
    Mock agent for fast deterministic tests.
    
    NOTE: Does NOT inherit from AgentBase (too heavyweight for unit tests).
    Implements TestableAgentProtocol for test compatibility.
    """
    
    def __init__(self):
        self.calls = []  # Track calls for assertions
    
    async def generate_sop(self, context: Dict[str, Any]) -> AgentResponse:
        self.calls.append(("generate_sop", context))
        
        title = context.get("title", "Standard Operating Procedure")
        return AgentResponse(
            content=f"""# {title}

## Purpose
Mock SOP for testing purposes

## Scope
Applies to test scenarios

## Procedures
1. Step one
2. Step two
3. Step three
""",
            response_type="sop",
            metadata={"source": "mock", "context": context},
            confidence=1.0
        )
    
    async def generate_workflow(self, context: Dict[str, Any]) -> AgentResponse:
        self.calls.append(("generate_workflow", context))
        
        return AgentResponse(
            content={
                "nodes": [
                    {"id": "1", "label": "Start"},
                    {"id": "2", "label": "Process"},
                    {"id": "3", "label": "End"}
                ],
                "edges": [
                    {"from": "1", "to": "2"},
                    {"from": "2", "to": "3"}
                ]
            },
            response_type="workflow",
            metadata={"source": "mock"},
            confidence=1.0
        )
    
    # ... other methods follow same pattern


# tests/fixtures/real_agent_wrapper.py

import os
import openai
from typing import Dict, Any
from tests.fixtures.testing_agent_protocol import TestableAgentProtocol, AgentResponse


class RealAgentWrapper:
    """
    Lightweight wrapper for real AI in tests.
    
    NOTE: This is a TEST WRAPPER, not a production agent!
    Production agents should use full AgentBase with foundation integration.
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        openai.api_key = self.api_key
    
    async def generate_sop(self, context: Dict[str, Any]) -> AgentResponse:
        """Generate SOP using real AI"""
        
        prompt = f"""Generate a professional Standard Operating Procedure (SOP) for:

Title: {context.get('title', 'Procedure')}
Department: {context.get('department', 'Operations')}
Purpose: {context.get('purpose', 'Standardize operations')}

The SOP must include:
- Purpose section
- Scope section
- Detailed procedures with numbered steps
- Responsibilities
- References (if applicable)

Make it professional and actionable."""

        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content
        
        return AgentResponse(
            content=content,
            response_type="sop",
            metadata={
                "source": "openai",
                "model": self.model,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            },
            confidence=None  # No confidence score from API
        )
    
    # ... other methods follow same pattern
```

---

### **Layer 2: Test Agent Factory**

```python
# tests/fixtures/test_agent_factory.py

import os
from tests.fixtures.mock_agent import MockAgent
from tests.fixtures.real_agent_wrapper import RealAgentWrapper
from tests.fixtures.cached_agent_wrapper import CachedAgentWrapper


class TestAgentFactory:
    """
    Factory to create appropriate agent for testing.
    
    NOTE: This is ONLY for testing infrastructure!
    Production code should use AgentBase and proper foundation integration.
    """
    
    @staticmethod
    def create_test_agent(agent_type: str = None):
        """
        Create test agent based on environment/config
        
        Priority:
        1. Explicit agent_type parameter
        2. TEST_AGENT_MODE environment variable
        3. Default based on test type
        """
        
        mode = agent_type or os.getenv("TEST_AGENT_MODE", "mock")
        
        if mode == "mock":
            return MockAgent()
        
        elif mode == "cached":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("⚠️  WARNING: OPENAI_API_KEY not set, falling back to mock")
                return MockAgent()
            real_agent = RealAgentWrapper(api_key, model="gpt-3.5-turbo")
            return CachedAgentWrapper(real_agent, cache_path="tests/fixtures/agent_cache.json")
        
        elif mode == "real":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY required for real agent mode")
            return RealAgentWrapper(api_key, model="gpt-3.5-turbo")
        
        else:
            raise ValueError(f"Unknown agent mode: {mode}")
```

**Key Architectural Points:**

1. **Testing != Production**
   - Test agents are lightweight wrappers (no AgentBase)
   - Production agents inherit from AgentBase with full foundation integration
   - This keeps tests fast and focused

2. **Protocol-Based Compatibility**
   - Test agents implement TestableAgentProtocol
   - Ensures consistent interface across mock/real/cached
   - Type-safe without heavyweight infrastructure

3. **Production Agent Integration**
   - Your production agents (GuideAgent, LiaisonAgents, etc.) inherit from AgentBase
   - They get full foundation integration (DI, telemetry, policy, etc.)
   - Tests verify behavior, not infrastructure

---

### **Layer 3: Test Configuration**

```python
# tests/conftest.py

import pytest
import os

@pytest.fixture
def mock_agent():
    """Mock agent for fast unit tests"""
    return MockAgent()

@pytest.fixture
def real_agent():
    """Real agent for integration tests"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set - skipping real AI test")
    return RealAgent(api_key, model="gpt-3.5-turbo")

@pytest.fixture
def cached_agent():
    """Cached agent for deterministic tests"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set")
    real = RealAgent(api_key, "gpt-3.5-turbo")
    return CachedAgent(real, "tests/fixtures/agent_cache.json")

@pytest.fixture
def agent_factory():
    """Agent factory for tests"""
    return AgentFactory()
```

---

## 🧪 Test Implementation Examples

### **Unit Tests (Mock Agent):**

```python
# tests/unit/test_sop_generation_mock.py

@pytest.mark.unit
async def test_sop_generation_structure(mock_agent):
    """Test SOP generation business logic (fast, deterministic)"""
    
    context = {
        "title": "Data Processing Procedure",
        "department": "Operations"
    }
    
    sop = await mock_agent.generate_sop(context)
    
    # Test structure (not AI quality)
    assert "Purpose" in sop
    assert "Scope" in sop
    assert "Procedures" in sop
    assert len(sop) > 100


@pytest.mark.unit
async def test_sop_includes_context(mock_agent):
    """Test that SOP includes provided context"""
    
    context = {
        "title": "Quantum Computing Procedure",
        "department": "Advanced Research"
    }
    
    sop = await mock_agent.generate_sop(context)
    
    # Mock should include context
    assert "quantum" in sop.lower() or "advanced" in sop.lower()
```

---

### **Integration Tests (Real Agent):**

```python
# tests/e2e/test_sop_generation_real_ai.py

@pytest.mark.e2e
@pytest.mark.ai
@pytest.mark.slow
@pytest.mark.costs_money
async def test_sop_generation_with_real_ai(real_agent):
    """Test SOP generation with actual AI (slow, costs money)"""
    
    context = {
        "title": "Customer Data Processing Procedure",
        "department": "Operations",
        "purpose": "Standardize how we handle customer data uploads"
    }
    
    sop = await real_agent.generate_sop(context)
    
    # Test actual AI output quality
    assert len(sop) > 500, "SOP should be comprehensive"
    
    # Check for key sections
    assert "purpose" in sop.lower()
    assert "procedure" in sop.lower() or "step" in sop.lower()
    
    # Check that AI understood context
    assert "customer" in sop.lower()
    assert "data" in sop.lower()
    
    # Check for professionalism
    assert not any(word in sop.lower() for word in ["test", "mock", "placeholder"])
    
    print(f"\n{'='*70}")
    print("REAL AI GENERATED SOP:")
    print('='*70)
    print(sop[:500] + "..." if len(sop) > 500 else sop)
    print('='*70)


@pytest.mark.e2e
@pytest.mark.ai
@pytest.mark.slow
async def test_workflow_generation_with_real_ai(real_agent):
    """Test workflow generation with actual AI"""
    
    context = {
        "process": "Customer Onboarding",
        "steps": ["Application", "Verification", "Approval", "Notification"]
    }
    
    workflow = await real_agent.generate_workflow(context)
    
    # Verify workflow has logical structure
    assert len(workflow["nodes"]) >= 4, "Should have at least 4 nodes"
    assert len(workflow["edges"]) >= 3, "Should have connecting edges"
    
    # Verify nodes match context
    node_labels = [node["label"].lower() for node in workflow["nodes"]]
    assert any("application" in label or "apply" in label for label in node_labels)
    assert any("verification" in label or "verify" in label for label in node_labels)
```

---

### **Cached Tests (Golden Tests):**

```python
# tests/e2e/test_sop_generation_cached.py

@pytest.mark.e2e
@pytest.mark.cached
async def test_sop_generation_cached(cached_agent):
    """Test SOP generation with cached AI responses (deterministic)"""
    
    # This will use cached response on subsequent runs
    context = {
        "title": "Standard Data Upload Procedure",
        "department": "Operations"
    }
    
    sop = await cached_agent.generate_sop(context)
    
    # First run: calls AI and caches
    # Subsequent runs: uses cache (fast, deterministic)
    
    assert len(sop) > 300
    assert "Purpose" in sop
    assert "Procedures" in sop
```

---

## 🎯 Recommended Test Markers

```python
# pytest.ini

[pytest]
markers =
    unit: Unit tests (fast, mock agents)
    integration: Integration tests (medium speed)
    e2e: End-to-end tests (slow)
    ai: Tests that use real AI (slow, costs money)
    slow: Slow tests (> 10 seconds)
    costs_money: Tests that incur API costs
    cached: Tests using cached AI responses
```

**Run strategies:**

```bash
# Fast tests only (CI on every commit)
pytest -m "not slow and not ai"

# Integration tests (CI on PR)
pytest -m "integration or cached"

# Full test suite including real AI (pre-deploy)
pytest -m "ai or e2e"

# Just AI tests
pytest -m "ai"
```

---

## 💰 Cost Management

### **Estimated Costs:**

```
GPT-3.5-turbo pricing (as of 2024):
- Input: $0.0010 / 1K tokens
- Output: $0.0020 / 1K tokens

Typical SOP generation:
- Input: ~500 tokens ($0.0005)
- Output: ~1000 tokens ($0.002)
- Total: ~$0.0025 per test

100 AI tests: ~$0.25
1000 AI tests: ~$2.50

Budget: ~$10/month for comprehensive testing
```

### **Cost Reduction Strategies:**

1. **Use GPT-3.5-turbo for tests** (20x cheaper than GPT-4)
2. **Cache responses** (free after first run)
3. **Rate limit** (don't run AI tests on every commit)
4. **Use mocks for unit tests** (free, fast)
5. **Batch test runs** (run AI tests once per PR, not per commit)

---

## 🔒 Security & Configuration

### **Environment Variables:**

```bash
# .env.test
TEST_AGENT_MODE=real  # or mock, cached
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...  # for Claude
TEST_AI_MODEL=gpt-3.5-turbo  # cheaper for tests
TEST_AI_MAX_TOKENS=1000  # limit response length
TEST_AI_TIMEOUT=30  # seconds
```

### **GitHub Secrets:**

```yaml
# .github/workflows/ai-tests.yml
name: AI Integration Tests

on:
  pull_request:
    branches: [main, develop]

jobs:
  ai-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run AI Integration Tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          TEST_AGENT_MODE: real
          TEST_AI_MODEL: gpt-3.5-turbo
        run: |
          pytest -m "ai" -v --tb=short
```

---

## 📊 Quality Validation

### **How to Test AI Output Quality:**

```python
# tests/e2e/test_ai_quality.py

@pytest.mark.ai
async def test_sop_quality_metrics(real_agent):
    """Test that AI-generated SOPs meet quality standards"""
    
    context = {"title": "Data Processing SOP"}
    sop = await real_agent.generate_sop(context)
    
    # Quantitative checks
    assert len(sop) > 500, "SOP too short"
    assert len(sop) < 5000, "SOP too long"
    
    # Structure checks
    sections = ["purpose", "scope", "procedure"]
    for section in sections:
        assert section in sop.lower(), f"Missing {section} section"
    
    # Professionalism checks
    unprofessional_words = ["lol", "idk", "test", "mock", "placeholder"]
    assert not any(word in sop.lower() for word in unprofessional_words)
    
    # Completeness check
    steps = sop.count("\n")
    assert steps > 10, "SOP should have multiple steps/lines"
```

---

## 🎯 Best Practices

### **DO:**
✅ Use real AI for E2E/functional tests  
✅ Use mocks for unit tests  
✅ Cache AI responses for deterministic tests  
✅ Add cost monitoring  
✅ Use cheaper models for testing  
✅ Test AI integration points  
✅ Validate AI output structure  
✅ Have fallback mocks  

### **DON'T:**
❌ Run AI tests on every commit  
❌ Use GPT-4 for tests (too expensive)  
❌ Test AI quality itself (test your integration)  
❌ Make tests dependent on exact AI output  
❌ Run AI tests in parallel (rate limits)  
❌ Skip validation (always check output)  

---

## 🚀 Implementation Roadmap

### **Phase 1: Foundation (1-2 hours)**
- [ ] Create AgentInterface abstraction
- [ ] Implement MockAgent
- [ ] Implement RealAgent
- [ ] Create AgentFactory
- [ ] Update pytest markers

### **Phase 2: Test Implementation (2-3 hours)**
- [ ] Add AI secrets to test environment
- [ ] Create unit tests with MockAgent
- [ ] Create E2E tests with RealAgent
- [ ] Add quality validation tests

### **Phase 3: Optimization (1-2 hours)**
- [ ] Implement CachedAgent
- [ ] Add cost monitoring
- [ ] Configure CI/CD for AI tests
- [ ] Document for team

---

## 💡 Key Insights

### **Your Roadmap is Increasingly Agentic:**
> "Most of our roadmap use cases are going to be increasingly agentic"

**This strategy scales:**
```
Today: SOP, Workflow, Roadmap, POC generation
Tomorrow: Multi-agent orchestration
Future: Autonomous decision-making

Same testing strategy applies!
```

### **The Foundation You're Building:**
1. ✅ Agent abstraction (swappable AI)
2. ✅ Mock for speed (unit tests)
3. ✅ Real for confidence (functional tests)
4. ✅ Cached for determinism (regression tests)
5. ✅ Quality validation (output checks)

---

## 🎉 Bottom Line

**Your suggestion to use real AI in tests is CORRECT!**

**Recommended Approach:**
1. Use **real AI** for functional/E2E tests
2. Use **mocks** for unit tests  
3. Use **cached responses** for deterministic tests
4. Budget **~$10/month** for comprehensive AI testing
5. Run AI tests on **PR merge**, not every commit

**Result:** Confidence that agentic features work in production! 🚀

---

**Next Step:** Implement agent abstraction layer and add OPENAI_API_KEY to test environment.

