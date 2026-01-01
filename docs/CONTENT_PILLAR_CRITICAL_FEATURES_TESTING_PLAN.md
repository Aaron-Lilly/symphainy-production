# Content Pillar: Critical Features Testing Plan

## Executive Summary

**Approach:** Test critical incremental features in production containers/environment FIRST, then wire into platform, then proceed with full implementation.

**Principle:** Prove it works before building the whole thing. Break and fix once we know it works.

---

## Critical Features to Test

### 1. HuggingFace Model Inference (Embeddings)
**Why Critical:** If we can't generate embeddings, semantic processing fails.

### 2. Arango Storage/Retrieval (Embeddings)
**Why Critical:** If we can't store/retrieve embeddings, semantic layer fails.

### 3. Arango Storage/Retrieval (Semantic Graph)
**Why Critical:** If we can't store/retrieve semantic graphs, unstructured processing fails.

### 4. Agent → HF Model → Arango Flow
**Why Critical:** End-to-end flow must work for semantic processing.

### 5. Content Metadata Abstraction Integration
**Why Critical:** Need to integrate with existing metadata system.

---

## Phase 1: Test Critical Features in Isolation

### Test 1.1: HuggingFace Model Inference (Embeddings)

**Goal:** Prove we can call HF models and get embeddings.

**Test Script:** `scripts/test_hf_embedding.py`

```python
#!/usr/bin/env python3
"""
Test HuggingFace embedding generation in production container.

Run this in production container to verify HF model access works.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.public_works_foundation.infrastructure_adapters.huggingface_adapter import HuggingFaceAdapter

async def test_hf_embedding():
    """Test HF embedding generation."""
    print("🧪 Testing HuggingFace Embedding Generation...")
    
    # Initialize adapter (use real config from environment)
    hf_endpoint = os.getenv("HUGGINGFACE_ENDPOINT_URL", "https://api-inference.huggingface.co")
    hf_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
    
    if not hf_api_key:
        print("❌ HUGGINGFACE_API_KEY not set")
        return False
    
    adapter = HuggingFaceAdapter(hf_endpoint, hf_api_key)
    
    # Test embedding generation
    test_text = "This is a test column for semantic embedding"
    
    try:
        result = await adapter.inference(
            endpoint="embeddings",
            model="sentence-transformers/all-mpnet-base-v2",
            text=test_text
        )
        
        if result and "embedding" in result:
            embedding = result["embedding"]
            print(f"✅ Embedding generated: {len(embedding)} dimensions")
            print(f"   First 5 values: {embedding[:5]}")
            return True
        else:
            print(f"❌ Invalid response: {result}")
            return False
    
    except Exception as e:
        print(f"❌ HF embedding test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_hf_embedding())
    sys.exit(0 if success else 1)
```

**Run:**
```bash
# In production container
cd /home/founders/demoversion/symphainy_source
python scripts/test_hf_embedding.py
```

**Success Criteria:**
- ✅ Can connect to HF endpoint
- ✅ Can generate embeddings
- ✅ Embeddings have expected dimensions (768 for all-mpnet-base-v2)

---

### Test 1.2: Arango Storage/Retrieval (Embeddings)

**Goal:** Prove we can store and retrieve embeddings in Arango.

**Test Script:** `scripts/test_arango_embeddings.py`

```python
#!/usr/bin/env python3
"""
Test Arango storage/retrieval of embeddings in production container.

Run this in production container to verify Arango embedding storage works.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter

async def test_arango_embeddings():
    """Test Arango embedding storage/retrieval."""
    print("🧪 Testing Arango Embedding Storage/Retrieval...")
    
    # Initialize adapter (use real config)
    arango_config = {
        "hosts": os.getenv("ARANGODB_HOSTS", "http://localhost:8529"),
        "database": os.getenv("ARANGODB_DATABASE", "symphainy_metadata"),
        "username": os.getenv("ARANGODB_USERNAME", "root"),
        "password": os.getenv("ARANGODB_PASSWORD", "")
    }
    
    adapter = ArangoDBAdapter(
        hosts=arango_config["hosts"],
        database=arango_config["database"],
        username=arango_config["username"],
        password=arango_config["password"]
    )
    
    try:
        # Connect
        connected = await adapter.connect(timeout=10.0)
        if not connected:
            print("❌ Failed to connect to ArangoDB")
            return False
        
        print("✅ Connected to ArangoDB")
        
        # Test embedding storage
        test_embedding = {
            "_key": f"test_embedding_{datetime.utcnow().timestamp()}",
            "file_id": "test_file_123",
            "column_name": "test_column",
            "semantic_id": "test_semantic_id",
            "metadata_embedding": [0.1] * 768,  # Mock embedding
            "meaning_embedding": [0.2] * 768,
            "samples_embedding": [0.3] * 768,
            "tenant_id": "test_tenant",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Store
        result = await adapter.create_document("structured_embeddings", test_embedding)
        print(f"✅ Stored embedding: {result.get('_key')}")
        
        # Retrieve
        retrieved = await adapter.get_document("structured_embeddings", test_embedding["_key"])
        if retrieved:
            print(f"✅ Retrieved embedding: {retrieved.get('column_name')}")
            print(f"   Metadata embedding dimensions: {len(retrieved.get('metadata_embedding', []))}")
        else:
            print("❌ Failed to retrieve embedding")
            return False
        
        # Query by file_id
        query_result = await adapter.find_documents(
            "structured_embeddings",
            filter_conditions={"file_id": "test_file_123"}
        )
        print(f"✅ Query by file_id returned {len(query_result)} embeddings")
        
        # Cleanup
        await adapter.delete_document("structured_embeddings", test_embedding["_key"])
        print("✅ Cleaned up test embedding")
        
        return True
    
    except Exception as e:
        print(f"❌ Arango embedding test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_arango_embeddings())
    sys.exit(0 if success else 1)
```

**Run:**
```bash
# In production container
cd /home/founders/demoversion/symphainy_source
python scripts/test_arango_embeddings.py
```

**Success Criteria:**
- ✅ Can connect to ArangoDB
- ✅ Can store embeddings
- ✅ Can retrieve embeddings
- ✅ Can query by file_id

---

### Test 1.3: Arango Storage/Retrieval (Semantic Graph)

**Goal:** Prove we can store and retrieve semantic graphs in Arango.

**Test Script:** `scripts/test_arango_semantic_graph.py`

```python
#!/usr/bin/env python3
"""
Test Arango storage/retrieval of semantic graph in production container.

Run this in production container to verify Arango semantic graph storage works.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('../../'))

from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter

async def test_arango_semantic_graph():
    """Test Arango semantic graph storage/retrieval."""
    print("🧪 Testing Arango Semantic Graph Storage/Retrieval...")
    
    # Initialize adapter
    arango_config = {
        "hosts": os.getenv("ARANGODB_HOSTS", "http://localhost:8529"),
        "database": os.getenv("ARANGODB_DATABASE", "symphainy_metadata"),
        "username": os.getenv("ARANGODB_USERNAME", "root"),
        "password": os.getenv("ARANGODB_PASSWORD", "")
    }
    
    adapter = ArangoDBAdapter(
        hosts=arango_config["hosts"],
        database=arango_config["database"],
        username=arango_config["username"],
        password=arango_config["password"]
    )
    
    try:
        # Connect
        connected = await adapter.connect(timeout=10.0)
        if not connected:
            print("❌ Failed to connect to ArangoDB")
            return False
        
        print("✅ Connected to ArangoDB")
        
        # Test node storage
        test_node = {
            "_key": f"test_node_{datetime.utcnow().timestamp()}",
            "file_id": "test_file_456",
            "entity_id": "entity_1",
            "entity_text": "Test Entity",
            "entity_type": "person",
            "semantic_id": "test_semantic_id",
            "embedding": [0.1] * 768,
            "confidence": 0.85,
            "tenant_id": "test_tenant",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = await adapter.create_document("semantic_graph_nodes", test_node)
        print(f"✅ Stored node: {result.get('_key')}")
        
        # Test edge storage
        test_edge = {
            "_key": f"test_edge_{datetime.utcnow().timestamp()}",
            "file_id": "test_file_456",
            "source_entity_id": "entity_1",
            "target_entity_id": "entity_2",
            "relationship_type": "related_to",
            "confidence": 0.75,
            "tenant_id": "test_tenant",
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = await adapter.create_document("semantic_graph_edges", test_edge)
        print(f"✅ Stored edge: {result.get('_key')}")
        
        # Retrieve node
        retrieved_node = await adapter.get_document("semantic_graph_nodes", test_node["_key"])
        if retrieved_node:
            print(f"✅ Retrieved node: {retrieved_node.get('entity_text')}")
        else:
            print("❌ Failed to retrieve node")
            return False
        
        # Query nodes by file_id
        nodes_result = await adapter.find_documents(
            "semantic_graph_nodes",
            filter_conditions={"file_id": "test_file_456"}
        )
        print(f"✅ Query nodes by file_id returned {len(nodes_result)} nodes")
        
        # Query edges by file_id
        edges_result = await adapter.find_documents(
            "semantic_graph_edges",
            filter_conditions={"file_id": "test_file_456"}
        )
        print(f"✅ Query edges by file_id returned {len(edges_result)} edges")
        
        # Cleanup
        await adapter.delete_document("semantic_graph_nodes", test_node["_key"])
        await adapter.delete_document("semantic_graph_edges", test_edge["_key"])
        print("✅ Cleaned up test graph data")
        
        return True
    
    except Exception as e:
        print(f"❌ Arango semantic graph test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_arango_semantic_graph())
    sys.exit(0 if success else 1)
```

**Run:**
```bash
# In production container
cd /home/founders/demoversion/symphainy_source
python scripts/test_arango_semantic_graph.py
```

**Success Criteria:**
- ✅ Can store nodes
- ✅ Can store edges
- ✅ Can retrieve nodes/edges
- ✅ Can query by file_id

---

### Test 1.4: Agent → HF Model → Arango Flow

**Goal:** Prove end-to-end flow works (Agent calls HF, gets embedding, stores in Arango).

**Test Script:** `scripts/test_agent_hf_arango_flow.py`

```python
#!/usr/bin/env python3
"""
Test Agent → HF Model → Arango flow in production container.

Run this in production container to verify end-to-end semantic flow works.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('../../'))

# This test will need to be updated once StatelessHFInferenceAgent is created
# For now, test the components separately

async def test_agent_hf_arango_flow():
    """Test Agent → HF → Arango flow."""
    print("🧪 Testing Agent → HF Model → Arango Flow...")
    
    # Step 1: Initialize HF adapter
    from foundations.public_works_foundation.infrastructure_adapters.huggingface_adapter import HuggingFaceAdapter
    
    hf_endpoint = os.getenv("HUGGINGFACE_ENDPOINT_URL", "https://api-inference.huggingface.co")
    hf_api_key = os.getenv("HUGGINGFACE_API_KEY", "")
    
    hf_adapter = HuggingFaceAdapter(hf_endpoint, hf_api_key)
    
    # Step 2: Generate embedding via HF
    test_text = "policy_number"
    print(f"   Generating embedding for: {test_text}")
    
    embedding_result = await hf_adapter.inference(
        endpoint="embeddings",
        model="sentence-transformers/all-mpnet-base-v2",
        text=test_text
    )
    
    if not embedding_result or "embedding" not in embedding_result:
        print("❌ Failed to generate embedding")
        return False
    
    embedding = embedding_result["embedding"]
    print(f"✅ Generated embedding: {len(embedding)} dimensions")
    
    # Step 3: Store in Arango
    from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter
    
    arango_adapter = ArangoDBAdapter(
        hosts=os.getenv("ARANGODB_HOSTS", "http://localhost:8529"),
        database=os.getenv("ARANGODB_DATABASE", "symphainy_metadata"),
        username=os.getenv("ARANGODB_USERNAME", "root"),
        password=os.getenv("ARANGODB_PASSWORD", "")
    )
    
    connected = await arango_adapter.connect(timeout=10.0)
    if not connected:
        print("❌ Failed to connect to ArangoDB")
        return False
    
    test_embedding_doc = {
        "_key": f"test_flow_{datetime.utcnow().timestamp()}",
        "file_id": "test_file_flow",
        "column_name": test_text,
        "semantic_id": None,
        "metadata_embedding": embedding,
        "meaning_embedding": embedding,  # Same for test
        "samples_embedding": None,
        "tenant_id": "test_tenant",
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await arango_adapter.create_document("structured_embeddings", test_embedding_doc)
    print(f"✅ Stored embedding in Arango: {result.get('_key')}")
    
    # Step 4: Retrieve from Arango
    retrieved = await arango_adapter.get_document("structured_embeddings", test_embedding_doc["_key"])
    if retrieved:
        print(f"✅ Retrieved embedding from Arango: {retrieved.get('column_name')}")
        print(f"   Embedding dimensions: {len(retrieved.get('metadata_embedding', []))}")
    else:
        print("❌ Failed to retrieve embedding")
        return False
    
    # Cleanup
    await arango_adapter.delete_document("structured_embeddings", test_embedding_doc["_key"])
    print("✅ Cleaned up test data")
    
    print("✅ Agent → HF → Arango flow works!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_agent_hf_arango_flow())
    sys.exit(0 if success else 1)
```

**Run:**
```bash
# In production container
cd /home/founders/demoversion/symphainy_source
python scripts/test_agent_hf_arango_flow.py
```

**Success Criteria:**
- ✅ Can generate embedding via HF
- ✅ Can store embedding in Arango
- ✅ Can retrieve embedding from Arango
- ✅ End-to-end flow works

---

### Test 1.5: Content Metadata Abstraction Integration

**Goal:** Prove we can integrate semantic data with Content Metadata Abstraction.

**Test Script:** `scripts/test_content_metadata_semantic_integration.py`

```python
#!/usr/bin/env python3
"""
Test Content Metadata Abstraction integration with semantic data.

Run this in production container to verify integration works.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('../../'))

async def test_content_metadata_semantic_integration():
    """Test Content Metadata Abstraction with semantic data."""
    print("🧪 Testing Content Metadata Abstraction + Semantic Integration...")
    
    # This test will need to be updated once Content Metadata Abstraction
    # is evolved to handle semantic data
    
    # For now, test that we can:
    # 1. Create content metadata
    # 2. Store semantic embeddings separately
    # 3. Link them via content_id
    
    from foundations.public_works_foundation.infrastructure_adapters.arangodb_adapter import ArangoDBAdapter
    
    arango_adapter = ArangoDBAdapter(
        hosts=os.getenv("ARANGODB_HOSTS", "http://localhost:8529"),
        database=os.getenv("ARANGODB_DATABASE", "symphainy_metadata"),
        username=os.getenv("ARANGODB_USERNAME", "root"),
        password=os.getenv("ARANGODB_PASSWORD", "")
    )
    
    connected = await arango_adapter.connect(timeout=10.0)
    if not connected:
        print("❌ Failed to connect to ArangoDB")
        return False
    
    # Create content metadata
    content_id = f"test_content_{datetime.utcnow().timestamp()}"
    content_metadata = {
        "_key": content_id,
        "file_uuid": "test_file_789",
        "content_type": "structured",
        "semantic_processing_status": "completed",
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await arango_adapter.create_document("content_metadata", content_metadata)
    print(f"✅ Created content metadata: {result.get('_key')}")
    
    # Store semantic embedding linked to content_id
    embedding_doc = {
        "_key": f"test_embedding_{datetime.utcnow().timestamp()}",
        "content_id": content_id,  # Link to content metadata
        "file_id": "test_file_789",
        "column_name": "test_column",
        "metadata_embedding": [0.1] * 768,
        "meaning_embedding": [0.2] * 768,
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = await arango_adapter.create_document("structured_embeddings", embedding_doc)
    print(f"✅ Stored embedding linked to content_id: {result.get('_key')}")
    
    # Query embeddings by content_id
    embeddings = await arango_adapter.find_documents(
        "structured_embeddings",
        filter_conditions={"content_id": content_id}
    )
    print(f"✅ Query embeddings by content_id returned {len(embeddings)} embeddings")
    
    # Cleanup
    await arango_adapter.delete_document("content_metadata", content_id)
    await arango_adapter.delete_document("structured_embeddings", embedding_doc["_key"])
    print("✅ Cleaned up test data")
    
    print("✅ Content Metadata + Semantic integration works!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_content_metadata_semantic_integration())
    sys.exit(0 if success else 1)
```

**Run:**
```bash
# In production container
cd /home/founders/demoversion/symphainy_source
python scripts/test_content_metadata_semantic_integration.py
```

**Success Criteria:**
- ✅ Can create content metadata
- ✅ Can link semantic data to content metadata
- ✅ Can query semantic data by content_id

---

## Phase 2: Wire Into Platform (Integration Testing)

### Test 2.1: StatelessHFInferenceAgent Integration

**Goal:** Test StatelessHFInferenceAgent works within platform.

**Test:** Create agent, initialize in orchestrator, call via MCP tool.

**Test Script:** `scripts/test_hf_agent_integration.py`

```python
#!/usr/bin/env python3
"""
Test StatelessHFInferenceAgent integration with platform.

Run this to verify agent works within orchestrator context.
"""

# Test that:
# 1. Agent can be initialized
# 2. Agent can be called via orchestrator
# 3. Agent returns embeddings
# 4. Agent errors are handled gracefully
```

### Test 2.2: ContentAnalysisOrchestrator Semantic Processing

**Goal:** Test semantic processing integrated into parse_file().

**Test:** Call parse_file() with semantic processing enabled, verify flow.

**Test Script:** `scripts/test_orchestrator_semantic_integration.py`

```python
#!/usr/bin/env python3
"""
Test ContentAnalysisOrchestrator semantic processing integration.

Run this to verify parse_file() with semantic processing works.
"""

# Test that:
# 1. parse_file() calls semantic processing
# 2. Semantic processing generates embeddings
# 3. Embeddings are stored in Arango
# 4. Response includes semantic_result
```

### Test 2.3: Frontend Integration

**Goal:** Test frontend can display semantic results.

**Test:** Parse file, verify frontend receives and displays semantic data.

**Test Script:** Manual testing in browser

**Steps:**
1. Upload structured file
2. Parse file
3. Verify semantic extraction layer displays
4. Verify confidence scores display
5. Verify read-only mode works

---

## Phase 3: Full Implementation

**Once Phase 1 and Phase 2 pass, proceed with full implementation plan:**

- `CONTENT_PILLAR_E2E_IMPLEMENTATION_PLAN.md`
- `IMPLEMENTATION_PLANS_UPDATE_TRACKER.md`

---

## Testing Checklist

### Phase 1: Critical Features (Isolation)
- [ ] Test 1.1: HF Embedding Generation ✅
- [ ] Test 1.2: Arango Embedding Storage/Retrieval ✅
- [ ] Test 1.3: Arango Semantic Graph Storage/Retrieval ✅
- [ ] Test 1.4: Agent → HF → Arango Flow ✅
- [ ] Test 1.5: Content Metadata Integration ✅

### Phase 2: Platform Integration
- [ ] Test 2.1: StatelessHFInferenceAgent Integration ✅
- [ ] Test 2.2: ContentAnalysisOrchestrator Semantic Processing ✅
- [ ] Test 2.3: Frontend Integration ✅

### Phase 3: Full Implementation
- [ ] Proceed with full implementation plan
- [ ] Break and fix as needed
- [ ] No backward compatibility needed

---

## Key Principles

1. **Test in Production Container First:** Use real environment, not mocks
2. **Test Critical Features in Isolation:** Prove each piece works
3. **Wire Into Platform:** Test integration
4. **Then Build Full Implementation:** Once we know it works
5. **Break and Fix:** No backward compatibility, fix once we know it works

**This approach ensures we prove the critical pieces work before building the whole system.**






