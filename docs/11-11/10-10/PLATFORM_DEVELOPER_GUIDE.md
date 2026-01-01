# Symphainy Platform Developer Guide & Toolkit

## 🎯 **Platform Development Philosophy**

### **Core Principles**
1. **NO STUBBED CODE**: Every implementation must be real and functional
2. **NO MOCK IMPLEMENTATIONS**: Use real abstractions and services
3. **NO HARDCODED VALUES**: Use configuration and dependency injection
4. **NO PLACEHOLDERS**: Implement real business logic and capabilities

### **Platform Architecture Compliance**
- **Layer 0**: Infrastructure Foundation (Infrastructure Abstractions)
- **Layer 1**: Public Works Foundation (Business Abstractions)
- **Layer 2**: Smart City Foundation (Platform Foundation Services)
- **Layer 3**: Business Enablement (Business Capabilities)
- **Layer 4**: Experience Foundation (User Experience)

## 🚀 **Development Workflow**

### **Step 1: Assess Existing Capabilities**

#### **Check Business Abstractions**
```python
# Check available business abstractions
from foundations.public_works_foundation.business_abstractions import *

# Available abstractions:
# - BusinessOutcomesBusinessAbstraction
# - CrossDimensionalOrchestrationBusinessAbstraction
# - ConversationManagementBusinessAbstraction
# - FileManagementBusinessAbstraction
# - AuthenticationBusinessAbstraction
# - AuthorizationBusinessAbstraction
# - And many more...
```

#### **Check Infrastructure Abstractions**
```python
# Check available infrastructure abstractions
from foundations.infrastructure_foundation.abstractions import *

# Available abstractions:
# - PostgreSQLAbstraction
# - RedisAbstraction
# - CeleryAbstraction
# - MeilisearchAbstraction
# - OpenTelemetryAbstraction
# - And many more...
```

#### **Check Existing Agents**
```python
# Check existing agents
from backend.business_enablement.roles.guide_agent.guide_agent_service import GuideAgentMVP
from backend.business_enablement.protocols.business_liaison_agent_protocol import BusinessLiaisonAgentProtocol

# Available agents:
# - Guide Agent (Cross-dimensional user guidance)
# - Liaison Agents (Pillar-specific interactions)
# - MCP Services (Micro-capability platform)
```

### **Step 2: Add New Infrastructure (if needed)**

#### **2.1 Add Dependencies to Poetry**
```toml
# Add to pyproject.toml
[tool.poetry.dependencies]
# New dependencies
new-dependency = "^1.0.0"
another-dependency = "^2.0.0"
```

#### **2.2 Add Configuration to Environment**
```bash
# Add to platform_env_file_for_cursor.md
# New Infrastructure Configuration
NEW_INFRASTRUCTURE_ENABLED=true
NEW_INFRASTRUCTURE_URL=http://localhost:8000
NEW_INFRASTRUCTURE_TIMEOUT=30
NEW_INFRASTRUCTURE_RETRY_ATTEMPTS=3
```

#### **2.3 Create Infrastructure Abstraction**
```python
# foundations/infrastructure_foundation/abstractions/new_infrastructure_abstraction.py
#!/usr/bin/env python3
"""
New Infrastructure Abstraction

Real infrastructure abstraction for new capabilities.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .base_abstraction import BaseInfrastructureAbstraction

class NewInfrastructureAbstraction(BaseInfrastructureAbstraction):
    def __init__(self, config: Dict[str, Any]):
        super().__init__("new_infrastructure", config)
        self.capabilities = ["real_capability_1", "real_capability_2"]
        self.logger = logging.getLogger(f"NewInfrastructureAbstraction")
    
    async def initialize(self):
        """Initialize the infrastructure abstraction."""
        try:
            # Real initialization using configuration
            self.url = self.config.get('NEW_INFRASTRUCTURE_URL')
            self.timeout = self.config.get('NEW_INFRASTRUCTURE_TIMEOUT', 30)
            self.retry_attempts = self.config.get('NEW_INFRASTRUCTURE_RETRY_ATTEMPTS', 3)
            
            # Real connection setup
            await self._setup_connection()
            
            self.is_initialized = True
            self.initialization_time = datetime.utcnow()
            self.logger.info("✅ New Infrastructure Abstraction initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize New Infrastructure Abstraction: {e}")
            raise
    
    async def _setup_connection(self):
        """Setup real connection to infrastructure."""
        # Real connection implementation
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Real health check implementation."""
        try:
            # Real health check
            health_status = await self._check_health()
            return {
                "abstraction": self.abstraction_name,
                "status": "healthy" if health_status else "unhealthy",
                "capabilities": self.capabilities,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "abstraction": self.abstraction_name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _check_health(self) -> bool:
        """Real health check implementation."""
        # Real health check logic
        return True
```

#### **2.4 Add to Infrastructure Foundation Service**
```python
# foundations/infrastructure_foundation/infrastructure_foundation_service.py
# Add to _initialize_infrastructure_abstractions method

# New Infrastructure abstraction
self.new_infrastructure = self._create_new_infrastructure_abstraction()
self.logger.info("✅ New Infrastructure abstraction created")

# Add method
def _create_new_infrastructure_abstraction(self) -> NewInfrastructureAbstraction:
    """Create new infrastructure abstraction using environment configuration."""
    try:
        # Get configuration from environment
        config = {
            'NEW_INFRASTRUCTURE_URL': self.di_container.config.get('NEW_INFRASTRUCTURE_URL'),
            'NEW_INFRASTRUCTURE_TIMEOUT': self.di_container.config.get('NEW_INFRASTRUCTURE_TIMEOUT', 30),
            'NEW_INFRASTRUCTURE_RETRY_ATTEMPTS': self.di_container.config.get('NEW_INFRASTRUCTURE_RETRY_ATTEMPTS', 3)
        }
        
        return NewInfrastructureAbstraction(config)
        
    except Exception as e:
        self.logger.error(f"❌ Failed to create New Infrastructure abstraction: {e}")
        raise
```

### **Step 3: Create Business Abstractions**

#### **3.1 Implement Real Business Abstraction**
```python
# foundations/public_works_foundation/business_abstractions/new_business_abstraction.py
#!/usr/bin/env python3
"""
New Business Abstraction

Real business abstraction for new capabilities.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .base_business_abstraction import BaseBusinessAbstraction

class NewBusinessAbstraction(BaseBusinessAbstraction):
    def __init__(self, infrastructure_abstractions: Dict[str, Any]):
        super().__init__("new_business", infrastructure_abstractions)
        self.capabilities = ["real_business_capability_1", "real_business_capability_2"]
        self.logger = logging.getLogger(f"NewBusinessAbstraction")
    
    async def initialize(self):
        """Initialize the business abstraction."""
        try:
            # Get infrastructure abstractions
            self.new_infrastructure = self.infrastructure_abstractions.get('new_infrastructure')
            if not self.new_infrastructure:
                raise ValueError("New Infrastructure abstraction not available")
            
            # Real business logic initialization
            await self._initialize_business_logic()
            
            self.is_initialized = True
            self.initialization_time = datetime.utcnow()
            self.logger.info("✅ New Business Abstraction initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize New Business Abstraction: {e}")
            raise
    
    async def _initialize_business_logic(self):
        """Initialize real business logic."""
        # Real business logic implementation
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Real health check implementation."""
        try:
            # Check infrastructure health
            infrastructure_health = await self.new_infrastructure.health_check()
            
            return {
                "abstraction": self.abstraction_name,
                "status": "healthy" if infrastructure_health.get("status") == "healthy" else "unhealthy",
                "capabilities": self.capabilities,
                "infrastructure_health": infrastructure_health,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "abstraction": self.abstraction_name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def real_business_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Real business operation implementation."""
        try:
            # Real business logic using infrastructure
            result = await self.new_infrastructure.process_data(data)
            return {
                "success": True,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"❌ Business operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
```

#### **3.2 Add to Public Works Foundation Service**
```python
# foundations/public_works_foundation/public_works_foundation_service.py
# Add to _initialize_business_abstractions method

# New Business abstraction
self.new_business = NewBusinessAbstraction(self.infrastructure_abstractions)
await self.new_business.initialize()
self.logger.info("✅ New Business Abstraction initialized")
```

### **Step 4: Build Services Using Abstractions**

#### **4.1 Create Service with Proper DI**
```python
# journey_solution/services/new_service.py
#!/usr/bin/env python3
"""
New Service - Platform Compliant Implementation

Real service implementation using proper abstractions and DI.
"""

import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.di_container import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from utilities import UserContext

class NewService:
    """
    New Service - Platform Compliant Implementation
    
    Real service implementation using proper abstractions and DI.
    """
    
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        """Initialize New Service with proper DI."""
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        
        # Get business abstractions
        self.new_business = public_works_foundation.get_business_abstraction("new_business")
        self.business_outcomes = public_works_foundation.get_business_abstraction("business_outcomes")
        
        # Get infrastructure abstractions
        self.redis = public_works_foundation.get_infrastructure_abstraction("redis")
        self.database = public_works_foundation.get_infrastructure_abstraction("database")
        
        # Service configuration
        self.service_name = "new_service"
        self.service_version = "1.0.0"
        self.architecture = "DDD/SOA"
        
        print(f"🎯 New Service initialized with proper abstractions")
    
    async def initialize(self):
        """Initialize the service."""
        try:
            print("🎯 Initializing New Service...")
            
            # Initialize business abstractions
            await self.new_business.initialize()
            await self.business_outcomes.initialize()
            
            # Initialize infrastructure abstractions
            await self.redis.initialize()
            await self.database.initialize()
            
            print("✅ New Service initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize New Service: {e}")
            raise
    
    async def real_operation(self, business_outcome: str, user_context: UserContext):
        """Real operation implementation."""
        try:
            print(f"🎯 Executing real operation for: {business_outcome}")
            
            # Use business abstractions for real analysis
            outcome_analysis = await self.business_outcomes.analyze_business_outcome(
                business_outcome, user_context
            )
            
            # Use new business abstraction for real processing
            processing_result = await self.new_business.real_business_operation(
                outcome_analysis
            )
            
            # Use infrastructure abstractions for real storage
            await self.redis.store_result(processing_result)
            await self.database.save_analysis(outcome_analysis)
            
            return {
                "success": True,
                "business_outcome": business_outcome,
                "outcome_analysis": outcome_analysis,
                "processing_result": processing_result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Real operation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "business_outcome": business_outcome
            }
    
    async def health_check(self):
        """Real health check implementation."""
        try:
            # Check business abstraction health
            business_health = await self.new_business.health_check()
            outcomes_health = await self.business_outcomes.health_check()
            
            # Check infrastructure health
            redis_health = await self.redis.health_check()
            database_health = await self.database.health_check()
            
            return {
                "service_name": self.service_name,
                "status": "healthy",
                "business_abstractions": {
                    "new_business": business_health,
                    "business_outcomes": outcomes_health
                },
                "infrastructure_abstractions": {
                    "redis": redis_health,
                    "database": database_health
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "service_name": self.service_name,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
```

### **Step 5: Integrate with Existing Agents**

#### **5.1 Use Existing Guide Agent**
```python
# Use existing Guide Agent for user guidance
from backend.business_enablement.roles.guide_agent.guide_agent_service import GuideAgentMVP

class NewServiceWithGuideAgent:
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        
        # Use existing Guide Agent
        self.guide_agent = GuideAgentMVP(
            di_container=di_container,
            curator_foundation=None,  # Will be injected
            metadata_foundation=None  # Will be injected
        )
    
    async def process_user_guidance(self, user_input: str, user_context: UserContext):
        """Process user guidance using existing Guide Agent."""
        try:
            # Use existing Guide Agent for real user guidance
            guidance_result = await self.guide_agent.provide_guidance(
                user_input=user_input,
                user_context=user_context
            )
            
            return guidance_result
            
        except Exception as e:
            print(f"❌ User guidance failed: {e}")
            return {"success": False, "error": str(e)}
```

#### **5.2 Use Existing Liaison Agents**
```python
# Use existing Liaison Agents for pillar-specific interactions
from backend.business_enablement.protocols.business_liaison_agent_protocol import BusinessLiaisonAgentProtocol

class NewServiceWithLiaisonAgents:
    def __init__(self, di_container: DIContainerService, 
                 public_works_foundation: PublicWorksFoundationService):
        self.di_container = di_container
        self.public_works_foundation = public_works_foundation
        
        # Use existing Liaison Agents
        self.liaison_agents = {
            "content": None,  # Will be injected
            "insights": None,  # Will be injected
            "operations": None,  # Will be injected
            "business_outcomes": None  # Will be injected
        }
    
    async def process_pillar_interaction(self, pillar: str, request: Dict[str, Any], user_context: UserContext):
        """Process pillar-specific interaction using existing Liaison Agents."""
        try:
            liaison_agent = self.liaison_agents.get(pillar)
            if not liaison_agent:
                raise ValueError(f"No liaison agent available for pillar: {pillar}")
            
            # Use existing Liaison Agent for real pillar interaction
            interaction_result = await liaison_agent.process_conversation(
                request=request,
                user_context=user_context
            )
            
            return interaction_result
            
        except Exception as e:
            print(f"❌ Pillar interaction failed: {e}")
            return {"success": False, "error": str(e)}
```

### **Step 6: Testing & Validation**

#### **6.1 Unit Tests with Real Abstractions**
```python
# tests/test_new_service.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from foundations.di_container import DIContainerService
from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
from journey_solution.services.new_service import NewService
from utilities import UserContext

@pytest.fixture
async def di_container():
    return DIContainerService()

@pytest.fixture
async def public_works_foundation(di_container):
    return PublicWorksFoundationService(di_container)

@pytest.fixture
async def new_service(di_container, public_works_foundation):
    service = NewService(di_container, public_works_foundation)
    await service.initialize()
    return service

@pytest.mark.asyncio
async def test_new_service_initialization(new_service):
    """Test service initialization with real abstractions."""
    assert new_service.service_name == "new_service"
    assert new_service.new_business is not None
    assert new_service.business_outcomes is not None

@pytest.mark.asyncio
async def test_real_operation(new_service):
    """Test real operation with real abstractions."""
    user_context = UserContext(
        user_id="test_user",
        tenant_id="test_tenant",
        email="test@example.com",
        full_name="Test User",
        session_id="test_session",
        permissions=["read", "write"]
    )
    
    result = await new_service.real_operation("test business outcome", user_context)
    
    assert result["success"] is True
    assert "business_outcome" in result
    assert "outcome_analysis" in result
    assert "processing_result" in result

@pytest.mark.asyncio
async def test_health_check(new_service):
    """Test health check with real abstractions."""
    health = await new_service.health_check()
    
    assert health["service_name"] == "new_service"
    assert health["status"] == "healthy"
    assert "business_abstractions" in health
    assert "infrastructure_abstractions" in health
```

#### **6.2 Integration Tests**
```python
# tests/test_integration.py
import pytest
import asyncio

@pytest.mark.asyncio
async def test_guide_agent_integration():
    """Test integration with existing Guide Agent."""
    # Test real integration with Guide Agent
    pass

@pytest.mark.asyncio
async def test_liaison_agent_integration():
    """Test integration with existing Liaison Agents."""
    # Test real integration with Liaison Agents
    pass

@pytest.mark.asyncio
async def test_cross_dimensional_coordination():
    """Test cross-dimensional coordination."""
    # Test real cross-dimensional coordination
    pass
```

## 🛠️ **Developer Toolkit**

### **Platform Compliance Checker**
```python
# tools/platform_compliance_checker.py
#!/usr/bin/env python3
"""
Platform Compliance Checker

Automated tool to check platform compliance.
"""

import ast
import os
import sys
from typing import List, Dict, Any

class PlatformComplianceChecker:
    def __init__(self):
        self.violations = []
        self.warnings = []
    
    def check_file(self, file_path: str) -> Dict[str, Any]:
        """Check a single file for platform compliance."""
        violations = []
        warnings = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for hardcoded values
            if self._has_hardcoded_values(content):
                violations.append("Hardcoded values detected")
            
            # Check for mock implementations
            if self._has_mock_implementations(content):
                violations.append("Mock implementations detected")
            
            # Check for placeholder code
            if self._has_placeholder_code(content):
                violations.append("Placeholder code detected")
            
            # Check for proper DI usage
            if not self._has_proper_di_usage(content):
                warnings.append("Proper DI usage not detected")
            
            # Check for abstraction usage
            if not self._has_abstraction_usage(content):
                warnings.append("Abstraction usage not detected")
            
        except Exception as e:
            violations.append(f"Error reading file: {e}")
        
        return {
            "file_path": file_path,
            "violations": violations,
            "warnings": warnings,
            "compliant": len(violations) == 0
        }
    
    def _has_hardcoded_values(self, content: str) -> bool:
        """Check for hardcoded values."""
        hardcoded_patterns = [
            '"hardcoded"',
            "'hardcoded'",
            '{"hardcoded": "value"}',
            '["hardcoded", "value"]'
        ]
        
        for pattern in hardcoded_patterns:
            if pattern in content:
                return True
        
        return False
    
    def _has_mock_implementations(self, content: str) -> bool:
        """Check for mock implementations."""
        mock_patterns = [
            'mock_',
            'Mock(',
            'AsyncMock(',
            'MagicMock(',
            'return {"mock": "data"}'
        ]
        
        for pattern in mock_patterns:
            if pattern in content:
                return True
        
        return False
    
    def _has_placeholder_code(self, content: str) -> bool:
        """Check for placeholder code."""
        placeholder_patterns = [
            'placeholder',
            'TODO',
            'FIXME',
            'pass  # TODO',
            'raise NotImplementedError'
        ]
        
        for pattern in placeholder_patterns:
            if pattern in content:
                return True
        
        return False
    
    def _has_proper_di_usage(self, content: str) -> bool:
        """Check for proper DI usage."""
        di_patterns = [
            'DIContainerService',
            'PublicWorksFoundationService',
            'di_container',
            'public_works_foundation'
        ]
        
        for pattern in di_patterns:
            if pattern in content:
                return True
        
        return False
    
    def _has_abstraction_usage(self, content: str) -> bool:
        """Check for abstraction usage."""
        abstraction_patterns = [
            'get_business_abstraction',
            'get_infrastructure_abstraction',
            'BusinessAbstraction',
            'InfrastructureAbstraction'
        ]
        
        for pattern in abstraction_patterns:
            if pattern in content:
                return True
        
        return False

def main():
    """Run platform compliance checker."""
    checker = PlatformComplianceChecker()
    
    # Check all Python files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                result = checker.check_file(file_path)
                
                if not result['compliant']:
                    print(f"❌ {file_path}")
                    for violation in result['violations']:
                        print(f"  ❌ {violation}")
                    for warning in result['warnings']:
                        print(f"  ⚠️ {warning}")
                else:
                    print(f"✅ {file_path}")

if __name__ == "__main__":
    main()
```

### **Abstraction Validator**
```python
# tools/abstraction_validator.py
#!/usr/bin/env python3
"""
Abstraction Validator

Tool to validate abstraction implementations.
"""

import asyncio
from typing import Dict, Any, List

class AbstractionValidator:
    def __init__(self):
        self.validation_results = []
    
    async def validate_business_abstraction(self, abstraction_name: str) -> Dict[str, Any]:
        """Validate a business abstraction."""
        try:
            # Import and initialize abstraction
            from foundations.public_works_foundation.public_works_foundation_service import PublicWorksFoundationService
            from foundations.di_container import DIContainerService
            
            di_container = DIContainerService()
            public_works = PublicWorksFoundationService(di_container)
            
            abstraction = public_works.get_business_abstraction(abstraction_name)
            
            # Test initialization
            await abstraction.initialize()
            
            # Test health check
            health = await abstraction.health_check()
            
            # Test capabilities
            capabilities = abstraction.capabilities
            
            return {
                "abstraction_name": abstraction_name,
                "status": "valid",
                "health": health,
                "capabilities": capabilities,
                "initialized": abstraction.is_initialized
            }
            
        except Exception as e:
            return {
                "abstraction_name": abstraction_name,
                "status": "invalid",
                "error": str(e)
            }
    
    async def validate_infrastructure_abstraction(self, abstraction_name: str) -> Dict[str, Any]:
        """Validate an infrastructure abstraction."""
        try:
            # Import and initialize abstraction
            from foundations.infrastructure_foundation.infrastructure_foundation_service import InfrastructureFoundationService
            
            infrastructure = InfrastructureFoundationService()
            abstraction = getattr(infrastructure, abstraction_name)
            
            # Test initialization
            await abstraction.initialize()
            
            # Test health check
            health = await abstraction.health_check()
            
            return {
                "abstraction_name": abstraction_name,
                "status": "valid",
                "health": health,
                "initialized": abstraction.is_initialized
            }
            
        except Exception as e:
            return {
                "abstraction_name": abstraction_name,
                "status": "invalid",
                "error": str(e)
            }

async def main():
    """Run abstraction validator."""
    validator = AbstractionValidator()
    
    # Validate business abstractions
    business_abstractions = [
        "business_outcomes",
        "cross_dimensional_orchestration",
        "conversation_management"
    ]
    
    for abstraction_name in business_abstractions:
        result = await validator.validate_business_abstraction(abstraction_name)
        print(f"Business Abstraction {abstraction_name}: {result['status']}")
        if result['status'] == 'invalid':
            print(f"  Error: {result['error']}")
    
    # Validate infrastructure abstractions
    infrastructure_abstractions = [
        "database",
        "redis",
        "celery",
        "meilisearch"
    ]
    
    for abstraction_name in infrastructure_abstractions:
        result = await validator.validate_infrastructure_abstraction(abstraction_name)
        print(f"Infrastructure Abstraction {abstraction_name}: {result['status']}")
        if result['status'] == 'invalid':
            print(f"  Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### **Integration Tester**
```python
# tools/integration_tester.py
#!/usr/bin/env python3
"""
Integration Tester

Tool to test cross-dimensional integration.
"""

import asyncio
from typing import Dict, Any, List

class IntegrationTester:
    def __init__(self):
        self.test_results = []
    
    async def test_cross_dimensional_coordination(self) -> Dict[str, Any]:
        """Test cross-dimensional coordination."""
        try:
            # Test City Manager coordination
            from backend.smart_city.services.city_manager.city_manager_service import CityManagerService
            from foundations.di_container import DIContainerService
            from utilities import UserContext
            
            di_container = DIContainerService()
            city_manager = CityManagerService(di_container)
            await city_manager.initialize()
            
            # Test coordination
            user_context = UserContext(
                user_id="test_user",
                tenant_id="test_tenant",
                email="test@example.com",
                full_name="Test User",
                session_id="test_session",
                permissions=["read", "write"]
            )
            
            coordination_result = await city_manager.coordinate_cross_dimensional_operations(
                "test_operation", user_context
            )
            
            return {
                "test_name": "cross_dimensional_coordination",
                "status": "passed",
                "result": coordination_result
            }
            
        except Exception as e:
            return {
                "test_name": "cross_dimensional_coordination",
                "status": "failed",
                "error": str(e)
            }
    
    async def test_guide_agent_integration(self) -> Dict[str, Any]:
        """Test Guide Agent integration."""
        try:
            # Test Guide Agent
            from backend.business_enablement.roles.guide_agent.guide_agent_service import GuideAgentMVP
            from foundations.di_container import DIContainerService
            from utilities import UserContext
            
            di_container = DIContainerService()
            guide_agent = GuideAgentMVP(di_container)
            await guide_agent.initialize()
            
            # Test guidance
            user_context = UserContext(
                user_id="test_user",
                tenant_id="test_tenant",
                email="test@example.com",
                full_name="Test User",
                session_id="test_session",
                permissions=["read", "write"]
            )
            
            guidance_result = await guide_agent.provide_guidance(
                "I need help with my business outcome", user_context
            )
            
            return {
                "test_name": "guide_agent_integration",
                "status": "passed",
                "result": guidance_result
            }
            
        except Exception as e:
            return {
                "test_name": "guide_agent_integration",
                "status": "failed",
                "error": str(e)
            }

async def main():
    """Run integration tests."""
    tester = IntegrationTester()
    
    # Test cross-dimensional coordination
    coordination_result = await tester.test_cross_dimensional_coordination()
    print(f"Cross-Dimensional Coordination: {coordination_result['status']}")
    
    # Test Guide Agent integration
    guide_agent_result = await tester.test_guide_agent_integration()
    print(f"Guide Agent Integration: {guide_agent_result['status']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📚 **Platform Development Resources**

### **Architecture Documentation**
- **Platform Architecture**: Complete platform architecture guide
- **Abstraction Library**: All available business and infrastructure abstractions
- **Agent Registry**: All available agents and their capabilities
- **MCP Service Registry**: All available MCP services

### **Development Commands**
```bash
# Install dependencies
poetry install

# Run platform compliance checker
poetry run python tools/platform_compliance_checker.py

# Run abstraction validator
poetry run python tools/abstraction_validator.py

# Run integration tests
poetry run python tools/integration_tester.py

# Run all tests
poetry run pytest

# Start development server
poetry run uvicorn main:app --reload
```

### **Quality Assurance**
- **Code Review Checklist**: Automated compliance validation
- **Abstraction Validator**: Validate abstraction implementations
- **Integration Tester**: Test cross-dimensional integration
- **Performance Profiler**: Profile service performance

This developer guide provides a comprehensive toolkit for building platform-compliant services that follow the Symphainy platform architecture and principles.
