# HuggingFace Private Inference Endpoints Setup Guide

## Executive Summary

**For MVP/Demo:** Start with 1-2 lightweight CPU endpoints. Scale up later if needed.

**Recommended Setup:**
1. **Embedding Endpoint** (Primary) - 2 vCPU, 4GB RAM
2. **NER Endpoint** (Optional) - 2 vCPU, 4GB RAM (if using HF for NER instead of LLM)

---

## Required Endpoints

### Endpoint 1: Semantic Embeddings (REQUIRED)

**Purpose:** Generate embeddings for:
- Column metadata embeddings
- Semantic meaning embeddings
- Sample values embeddings
- Entity embeddings (for unstructured data)

**Model:** `sentence-transformers/all-mpnet-base-v2`
- **Dimensions:** 768
- **Quality:** High quality embeddings
- **Speed:** Moderate (faster than larger models, slower than MiniLM)

**Alternative (if needed):** `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions:** 384
- **Quality:** Good quality, faster
- **Speed:** Faster than mpnet-base-v2

**Instance Type:** **2 vCPU, 4GB RAM**
- Embedding models are relatively lightweight
- 2 vCPU handles concurrent requests well
- 4GB RAM is sufficient for model + inference
- Can scale to 4 vCPU, 8GB if we see performance issues

**Why not GPU?**
- Embedding models run fine on CPU
- GPU only needed for very high throughput or batch processing
- For MVP, CPU is more cost-effective

---

### Endpoint 2: NER/Entity Extraction (OPTIONAL)

**Purpose:** Extract named entities from unstructured text (if using HF instead of LLM)

**Model:** `dslim/bert-base-NER`
- **Purpose:** Named Entity Recognition for English
- **Output:** Entities with labels (PERSON, ORG, LOC, etc.)

**Instance Type:** **2 vCPU, 4GB RAM**
- BERT-based models are lightweight
- 2 vCPU sufficient for NER inference
- 4GB RAM sufficient

**Note:** We might use LLM abstraction for entity extraction instead (better quality, more flexible). This endpoint is only needed if we want to use HF for NER.

**Alternative:** Use LLM abstraction (GPT-4, Claude) for entity extraction - no HF endpoint needed.

---

## Setup Instructions

### Step 1: Create Embedding Endpoint

**In HuggingFace Inference Endpoints:**

1. Go to: https://huggingface.co/inference-endpoints
2. Click "New Endpoint"
3. Configure:
   - **Name:** `symphainy-embeddings-mpnet`
   - **Model:** `sentence-transformers/all-mpnet-base-v2`
   - **Instance Type:** `CPU - 2 vCPU, 4GB RAM`
   - **Region:** Choose closest to your infrastructure
   - **Autoscaling:** Disabled for MVP (enable later if needed)
4. Click "Create Endpoint"
5. Wait for deployment (~5-10 minutes)
6. Copy the endpoint URL and API key

**Environment Variables:**
```bash
export HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://xxx.us-east-1.aws.endpoints.huggingface.cloud"
export HUGGINGFACE_EMBEDDINGS_API_KEY="hf_xxx"
```

---

### Step 2: Create NER Endpoint (Optional)

**Only if using HF for NER instead of LLM:**

1. Go to: https://huggingface.co/inference-endpoints
2. Click "New Endpoint"
3. Configure:
   - **Name:** `symphainy-ner-bert`
   - **Model:** `dslim/bert-base-NER`
   - **Instance Type:** `CPU - 2 vCPU, 4GB RAM`
   - **Region:** Same as embeddings endpoint
   - **Autoscaling:** Disabled for MVP
4. Click "Create Endpoint"
5. Wait for deployment
6. Copy the endpoint URL and API key

**Environment Variables:**
```bash
export HUGGINGFACE_NER_ENDPOINT_URL="https://xxx.us-east-1.aws.endpoints.huggingface.cloud"
export HUGGINGFACE_NER_API_KEY="hf_xxx"
```

---

## Configuration in Platform

### Update HuggingFaceAdapter

**File:** `foundations/public_works_foundation/infrastructure_adapters/huggingface_adapter.py`

```python
class HuggingFaceAdapter:
    """HuggingFace model endpoint adapter."""
    
    def __init__(self, endpoint_url: str = None, api_key: str = None):
        # Support multiple endpoints
        self.embeddings_endpoint = endpoint_url or os.getenv("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
        self.ner_endpoint = os.getenv("HUGGINGFACE_NER_ENDPOINT_URL")
        self.api_key = api_key or os.getenv("HUGGINGFACE_EMBEDDINGS_API_KEY") or os.getenv("HUGGINGFACE_API_KEY")
        
        if not self.embeddings_endpoint:
            raise ValueError("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL not set")
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY not set")
    
    async def generate_embedding(
        self,
        text: str,
        model: str = "sentence-transformers/all-mpnet-base-v2"
    ) -> Dict[str, Any]:
        """Generate embedding using embeddings endpoint."""
        return await self.inference(
            endpoint_url=self.embeddings_endpoint,
            model=model,
            text=text
        )
    
    async def extract_entities(
        self,
        text: str,
        model: str = "dslim/bert-base-NER"
    ) -> Dict[str, Any]:
        """Extract entities using NER endpoint."""
        if not self.ner_endpoint:
            raise ValueError("NER endpoint not configured (use LLM abstraction instead)")
        
        return await self.inference(
            endpoint_url=self.ner_endpoint,
            model=model,
            text=text
        )
    
    async def inference(
        self,
        endpoint_url: str,
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Call HF model endpoint."""
        import httpx
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # HF Inference Endpoints API format
        payload = {
            "inputs": kwargs.get("text", kwargs.get("inputs", "")),
            **{k: v for k, v in kwargs.items() if k != "text" and k != "inputs"}
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                endpoint_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
```

---

## Testing Endpoints

### Test Embedding Endpoint

**Script:** `scripts/test_hf_endpoint_embeddings.py`

```python
#!/usr/bin/env python3
"""Test HuggingFace embeddings endpoint."""

import asyncio
import os
import httpx

async def test_embeddings_endpoint():
    endpoint_url = os.getenv("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
    api_key = os.getenv("HUGGINGFACE_EMBEDDINGS_API_KEY")
    
    if not endpoint_url or not api_key:
        print("❌ Endpoint URL or API key not set")
        return False
    
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": "This is a test column for semantic embedding"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(endpoint_url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            embedding = result[0] if isinstance(result[0], list) else result
            print(f"✅ Embedding generated: {len(embedding)} dimensions")
            print(f"   First 5 values: {embedding[:5]}")
            return True
        else:
            print(f"❌ Unexpected response format: {result}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_embeddings_endpoint())
    exit(0 if success else 1)
```

**Run:**
```bash
export HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://xxx.us-east-1.aws.endpoints.huggingface.cloud"
export HUGGINGFACE_EMBEDDINGS_API_KEY="hf_xxx"
python scripts/test_hf_endpoint_embeddings.py
```

---

## Scaling Recommendations

### When to Scale Up

**From 2 vCPU, 4GB → 4 vCPU, 8GB:**
- If you see high latency (>2 seconds per embedding)
- If you see memory pressure (check endpoint metrics)
- If you're processing many files concurrently

**From 4 vCPU, 8GB → 8 vCPU, 16GB:**
- If 4 vCPU still shows high latency
- If you're processing very large files (100K+ rows)

**To GPU (1 GPU, 14GB):**
- Only if you need very high throughput (1000+ embeddings/second)
- For batch processing large datasets
- **Not needed for MVP** - CPU is sufficient

### Cost Considerations

**MVP (2 endpoints, 2 vCPU each):**
- ~$0.10-0.20/hour per endpoint
- ~$150-300/month per endpoint (if running 24/7)
- Can pause endpoints when not in use to save costs

**Production (scaled up):**
- 4 vCPU, 8GB: ~$0.20-0.40/hour
- 8 vCPU, 16GB: ~$0.40-0.80/hour
- GPU: ~$1.00-2.00/hour

---

## Alternative: Single Multi-Model Endpoint

**Option:** Use one endpoint with multiple models (if HF supports it)

**Pros:**
- Single endpoint to manage
- Lower cost (one endpoint instead of two)

**Cons:**
- Models share resources
- Less flexible scaling

**For MVP:** Two separate endpoints are simpler and more flexible.

---

## Summary

### Required Setup (MVP):

1. **Embeddings Endpoint:**
   - Model: `sentence-transformers/all-mpnet-base-v2`
   - Instance: **2 vCPU, 4GB RAM**
   - Cost: ~$150-300/month (if running 24/7)

2. **NER Endpoint (Optional):**
   - Model: `dslim/bert-base-NER`
   - Instance: **2 vCPU, 4GB RAM**
   - Cost: ~$150-300/month
   - **Alternative:** Use LLM abstraction for NER (no endpoint needed)

### Environment Variables:

```bash
# Required
export HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://xxx.us-east-1.aws.endpoints.huggingface.cloud"
export HUGGINGFACE_EMBEDDINGS_API_KEY="hf_xxx"

# Optional (if using HF for NER)
export HUGGINGFACE_NER_ENDPOINT_URL="https://xxx.us-east-1.aws.endpoints.huggingface.cloud"
export HUGGINGFACE_NER_API_KEY="hf_xxx"
```

### Next Steps:

1. Create embeddings endpoint (required)
2. Test endpoint with test script
3. Update HuggingFaceAdapter to use endpoint
4. Run Phase 1 tests from `CONTENT_PILLAR_CRITICAL_FEATURES_TESTING_PLAN.md`
5. Create NER endpoint only if using HF for NER (otherwise use LLM)

**Start small (2 vCPU, 4GB), scale up if needed!**

