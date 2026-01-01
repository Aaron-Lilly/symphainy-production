# HuggingFace Endpoint Quick Start Guide

## ✅ Your Current Configuration (Looks Perfect!)

Based on your screenshot, you have:

1. **Model:** `all-mpnet-base-v2` ✅
2. **Endpoint Name:** `symphainy / all-mpnet-base-v2-sao` ✅
3. **Authentication:** Private ✅ (Secure)
4. **Autoscaling:** 
   - Automatic Scale-to-Zero: **Enabled** ✅
   - Scale down: After 15 minutes ✅
   - Min replicas: 0 ✅
   - Max replicas: 1 ✅
5. **Inference Engine:** Text Embeddings Inference ✅ (Correct for embeddings)
6. **Cost:** $0.07/hour per running replica ✅

**Everything looks good!** You can click "Create Endpoint" now.

---

## After Creating the Endpoint

### Step 1: Get Endpoint URL

1. After creation, you'll be redirected to the endpoint details page
2. Look for the **"Endpoint URL"** field (usually at the top)
3. It will look like: `https://xxx.us-east-1.aws.endpoints.huggingface.cloud`
4. **Copy this URL** - this is your `HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL`

### Step 2: Get API Key (HuggingFace Token)

**Option A: Use Existing Token**
1. Go to: https://huggingface.co/settings/tokens
2. If you have a token, copy it
3. If not, create a new one (see Option B)

**Option B: Create New Token**
1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it: `symphainy-embeddings-endpoint`
4. Select "Read" permission (sufficient for inference)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)
7. This is your `HUGGINGFACE_EMBEDDINGS_API_KEY`

**Important:** The token starts with `hf_` - make sure you copy the full token.

---

## Set Environment Variables

### In Your Production Container

```bash
# Set endpoint URL (from Step 1)
export HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://xxx.us-east-1.aws.endpoints.huggingface.cloud"

# Set API key (from Step 2)
export HUGGINGFACE_EMBEDDINGS_API_KEY="hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Or Add to Your Environment Config File

**File:** `.env` or your environment config

```bash
HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL=https://xxx.us-east-1.aws.endpoints.huggingface.cloud
HUGGINGFACE_EMBEDDINGS_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Test the Endpoint

### Quick Test Script

**File:** `scripts/test_hf_endpoint_quick.py`

```python
#!/usr/bin/env python3
"""Quick test of HuggingFace endpoint."""

import os
import asyncio
import httpx

async def test_endpoint():
    endpoint_url = os.getenv("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
    api_key = os.getenv("HUGGINGFACE_EMBEDDINGS_API_KEY")
    
    if not endpoint_url or not api_key:
        print("❌ Environment variables not set!")
        print("   Set HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
        print("   Set HUGGINGFACE_EMBEDDINGS_API_KEY")
        return False
    
    print(f"🧪 Testing endpoint: {endpoint_url}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Scale-Up-Timeout": "600"  # Wait for cold start if needed
    }
    
    payload = {
        "inputs": "This is a test column for semantic embedding"
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            print("   Sending request (may take 30-60 seconds if cold start)...")
            response = await client.post(endpoint_url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                embedding = result[0] if isinstance(result[0], list) else result
            elif isinstance(result, dict) and "embedding" in result:
                embedding = result["embedding"]
            else:
                embedding = result
            
            if isinstance(embedding, list) and len(embedding) > 0:
                print(f"✅ Success! Embedding generated: {len(embedding)} dimensions")
                print(f"   First 5 values: {embedding[:5]}")
                return True
            else:
                print(f"❌ Unexpected response format: {result}")
                return False
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 503:
            print("⚠️ 503 Service Unavailable - endpoint may be scaling up (cold start)")
            print("   Wait 30-60 seconds and try again")
        else:
            print(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_endpoint())
    exit(0 if success else 1)
```

**Run:**
```bash
# Set environment variables first
export HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://xxx.us-east-1.aws.endpoints.huggingface.cloud"
export HUGGINGFACE_EMBEDDINGS_API_KEY="hf_xxx"

# Run test
python scripts/test_hf_endpoint_quick.py
```

---

## Configuration Checklist

### Before Creating Endpoint:
- [x] Model: `all-mpnet-base-v2` ✅
- [x] Authentication: Private ✅
- [x] Autoscaling: Enabled, Min 0, Max 1 ✅
- [x] Inference Engine: Text Embeddings Inference ✅

### After Creating Endpoint:
- [ ] Copy Endpoint URL
- [ ] Get/Create HuggingFace API Token
- [ ] Set environment variables
- [ ] Test endpoint with test script
- [ ] Verify embedding generation works

---

## Troubleshooting

### "503 Service Unavailable"
- **Cause:** Endpoint is scaling up from zero (cold start)
- **Solution:** Wait 30-60 seconds and retry, or use `X-Scale-Up-Timeout` header

### "401 Unauthorized"
- **Cause:** Invalid API key or token
- **Solution:** Check token is correct, starts with `hf_`, has Read permission

### "404 Not Found"
- **Cause:** Endpoint URL is incorrect
- **Solution:** Verify endpoint URL from HuggingFace UI

### "Timeout"
- **Cause:** Cold start taking longer than expected
- **Solution:** Increase timeout to 120 seconds, use `X-Scale-Up-Timeout` header

---

## Next Steps

Once endpoint is working:

1. ✅ Run Phase 1 tests from `CONTENT_PILLAR_CRITICAL_FEATURES_TESTING_PLAN.md`
2. ✅ Test embedding generation
3. ✅ Test Arango storage
4. ✅ Test end-to-end flow

**You're all set! Click "Create Endpoint" and then get the URL and API key.**






