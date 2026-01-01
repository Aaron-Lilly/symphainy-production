# HuggingFace Inference Endpoints: Management & Lifecycle

## How HuggingFace Inference Endpoints Work

### Always-On vs Scale-to-Zero

**Great News:** HuggingFace Inference Endpoints **DO** support automatic scale-to-zero!

**Autoscaling Behavior:**
- **Scale-to-Zero:** If endpoint is idle for 15+ minutes, it automatically scales down to zero replicas
- **Cost When Scaled to Zero:** No compute cost (you only pay for storage/config)
- **Cold Start:** When scaled to zero, next request triggers scale-up (takes time to load model)
- **Cold Start Handling:** Use `X-Scale-Up-Timeout` header to wait for scale-up

**Manual Control:** You can also manually pause/resume endpoints via UI or API.

---

## Endpoint States

### Running State (Active)
- **Status:** Endpoint is active and serving requests
- **Cost:** You pay for compute time (billed per hour)
- **Access:** Endpoint URL is active and can receive requests
- **Startup Time:** Already running (no startup delay)

### Scaled-to-Zero State (Auto)
- **Status:** Endpoint automatically scaled down (idle for 15+ minutes)
- **Cost:** **No compute cost** (you only pay for storage/config)
- **Access:** Endpoint URL available, but first request triggers cold start
- **Cold Start Time:** ~30 seconds to 2 minutes (depends on model size)
- **Configuration:** Preserved (model, instance type, etc.)
- **How to Enable:** Enable "Automatic Scale-to-Zero" in endpoint settings

### Paused State (Manual)
- **Status:** Endpoint is manually paused (not serving requests)
- **Cost:** **No compute cost** (you only pay for storage/config)
- **Access:** Endpoint URL returns error (endpoint unavailable)
- **Startup Time:** ~2-5 minutes to resume from paused state
- **Configuration:** Preserved (model, instance type, etc.)

### Deleted State
- **Status:** Endpoint is deleted
- **Cost:** No cost
- **Access:** Endpoint URL no longer exists
- **Startup Time:** ~5-10 minutes to recreate from scratch
- **Configuration:** Lost (must recreate)

---

## Automatic Scale-to-Zero (Recommended for MVP)

### Enable Autoscaling

**Via UI:**
1. Go to: https://huggingface.co/inference-endpoints
2. Select your endpoint
3. Go to "Settings" tab
4. Enable "Automatic Scale-to-Zero"
5. Set minimum replicas to 0
6. Set maximum replicas to 1 (for MVP)

**Behavior:**
- Endpoint automatically scales to zero after 15 minutes of inactivity
- No cost when scaled to zero
- First request after scale-to-zero triggers cold start (~30 seconds to 2 minutes)
- Subsequent requests are fast (endpoint is running)

**Handling Cold Starts:**

```python
# In HuggingFaceAdapter
async def inference(self, endpoint_url: str, model: str, **kwargs):
    """Call HF endpoint with cold start handling."""
    import httpx
    
    headers = {
        "Authorization": f"Bearer {self.api_key}",
        "X-Scale-Up-Timeout": "600"  # Wait up to 10 minutes for scale-up
    }
    
    # Retry logic for cold starts
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(endpoint_url, json=payload, headers=headers)
                
                # Handle 503 (cold start)
                if response.status_code == 503:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(10)  # Wait 10 seconds
                        continue
                
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503 and attempt < max_retries - 1:
                await asyncio.sleep(10)
                continue
            raise
```

## Manual Management (Alternative)

### Pause Endpoint (Manual Control)

**Via UI:**
1. Go to: https://huggingface.co/inference-endpoints
2. Find your endpoint
3. Click "Pause" button
4. Endpoint pauses (stops charging for compute)

**When to Use Manual Pause:**
- When you know you won't need it for extended period
- When you want guaranteed no cost (vs. 15-minute idle timeout)

### Resume Endpoint (Manual Restart)

**Via UI:**
1. Go to: https://huggingface.co/inference-endpoints
2. Find your paused endpoint
3. Click "Resume" button
4. Wait ~2-5 minutes for endpoint to start
5. Endpoint URL becomes active again

---

## Programmatic Management (Future Enhancement)

### HuggingFace API for Endpoint Management

**HuggingFace provides an API** for managing endpoints programmatically.

**API Endpoints:**
- `GET /api/inference-endpoints` - List endpoints
- `POST /api/inference-endpoints` - Create endpoint
- `PATCH /api/inference-endpoints/{endpoint_id}` - Update endpoint (pause/resume)
- `DELETE /api/inference-endpoints/{endpoint_id}` - Delete endpoint

**Example: Pause Endpoint via API**

```python
import requests

def pause_hf_endpoint(endpoint_id: str, api_token: str):
    """Pause HuggingFace inference endpoint."""
    url = f"https://api-inference.huggingface.co/api/inference-endpoints/{endpoint_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    data = {"status": "paused"}
    
    response = requests.patch(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

def resume_hf_endpoint(endpoint_id: str, api_token: str):
    """Resume HuggingFace inference endpoint."""
    url = f"https://api-inference.huggingface.co/api/inference-endpoints/{endpoint_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    data = {"status": "running"}
    
    response = requests.patch(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()
```

### Integration with Platform Startup/Shutdown

**Option 1: Manual Control (MVP)**
- Pause/resume manually via UI
- Simple, no code needed
- Good for MVP/testing phase

**Option 2: Script-Based Control (Post-MVP)**
- Create startup/shutdown scripts
- Scripts call HuggingFace API to resume/pause
- Run scripts as part of platform startup/shutdown

**Example Startup Script:**

```bash
#!/bin/bash
# scripts/start_hf_endpoints.sh

# Resume embeddings endpoint
python scripts/manage_hf_endpoints.py resume embeddings

# Wait for endpoint to be ready
sleep 30

# Test endpoint
python scripts/test_hf_endpoint_embeddings.py
```

**Example Shutdown Script:**

```bash
#!/bin/bash
# scripts/stop_hf_endpoints.sh

# Pause embeddings endpoint
python scripts/manage_hf_endpoints.py pause embeddings
```

**Option 3: Platform Integration (Future)**
- Add endpoint management to platform startup/shutdown
- Automatically resume endpoints when platform starts
- Automatically pause endpoints when platform stops
- Requires HuggingFace API integration

---

## Cost Implications

### Running 24/7
- **2 vCPU, 4GB:** ~$0.10-0.20/hour = ~$150-300/month
- **4 vCPU, 8GB:** ~$0.20-0.40/hour = ~$300-600/month

### Paused (Not Running)
- **Cost:** ~$0.01-0.02/hour (just storage/config)
- **Savings:** ~95% cost reduction when paused

### Recommendation for MVP
- **Keep paused** when not actively testing/developing
- **Resume** when needed (2-5 minute startup)
- **Manual control is fine** for MVP phase
- **Automate later** if endpoints become critical

---

## Startup/Shutdown Workflow

### Current Workflow (Manual - MVP)

**Before Testing/Development:**
1. Go to HuggingFace Inference Endpoints UI
2. Resume embeddings endpoint
3. Wait 2-5 minutes
4. Run tests/development

**After Testing/Development:**
1. Go to HuggingFace Inference Endpoints UI
2. Pause embeddings endpoint
3. Save costs

### Future Workflow (Automated - Post-MVP)

**Platform Startup:**
```bash
# In platform startup script
./scripts/start_hf_endpoints.sh
# Endpoints resume automatically
```

**Platform Shutdown:**
```bash
# In platform shutdown script
./scripts/stop_hf_endpoints.sh
# Endpoints pause automatically
```

---

## Comparison with GCE VMs

### GCE VMs
- **Control:** Full control (start/stop/delete)
- **Startup:** Fast (seconds)
- **Cost:** Pay only when running
- **Integration:** Easy (gcloud CLI, API)

### HuggingFace Endpoints
- **Control:** Managed service (pause/resume/delete)
- **Startup:** Slower (2-5 minutes from paused)
- **Cost:** Pay when running, minimal when paused
- **Integration:** Requires HuggingFace API

**Key Difference:** HuggingFace endpoints are managed services, not VMs you control directly. But you can pause/resume them to save costs.

---

## Recommendations

### For MVP (Now) - RECOMMENDED
1. **Set up endpoint** (2 vCPU, 4GB)
2. **Enable "Automatic Scale-to-Zero"** in endpoint settings
3. **Let it auto-scale** - no manual management needed!
4. **Handle cold starts** in code (use X-Scale-Up-Timeout header)
5. **No manual intervention needed** - endpoint manages itself

**Benefits:**
- ✅ Automatically saves costs when idle
- ✅ No manual pause/resume needed
- ✅ Works like serverless (scale-to-zero)
- ✅ First request after idle has cold start, but that's acceptable for MVP

### Alternative: Manual Control
1. **Set up endpoint** (2 vCPU, 4GB)
2. **Keep it paused** when not in use
3. **Resume manually** when testing/developing
4. **More control, but requires manual intervention**

### For Post-MVP (Later)
1. **Keep autoscaling enabled** (it works well)
2. **Optimize cold start handling** (retry logic, timeouts)
3. **Consider minimum replicas > 0** if latency is critical
4. **Monitor costs** - autoscaling should keep costs low

### Cost Optimization
- **Autoscaling (Recommended):** Automatically scales to zero after 15 min idle (saves ~95% cost)
- **Manual Pause:** Guaranteed no cost, but requires manual intervention
- **For production:** Keep autoscaling, set minimum replicas to 0, handle cold starts gracefully

---

## Quick Reference

### Manual Commands (UI)
- **Pause:** HuggingFace UI → Endpoint → Pause
- **Resume:** HuggingFace UI → Endpoint → Resume
- **Delete:** HuggingFace UI → Endpoint → Delete

### API Commands (Future)
```python
# Resume
pause_hf_endpoint(endpoint_id, api_token)

# Pause
resume_hf_endpoint(endpoint_id, api_token)
```

### Environment Variables
```bash
# Endpoint URL (changes when paused/resumed - stays same)
export HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://xxx.us-east-1.aws.endpoints.huggingface.cloud"

# API Key (stays same)
export HUGGINGFACE_EMBEDDINGS_API_KEY="hf_xxx"
```

---

## Summary

**Answer to Your Questions:**

1. **Can they scale to zero?** ✅ **YES!** Enable "Automatic Scale-to-Zero" - they auto-scale to zero after 15 min idle
2. **Can we start them like GCE VMs?** ✅ **YES!** They auto-start on first request (cold start ~30 sec to 2 min)
3. **Do we need to leave them on 24/7?** ❌ **NO!** They auto-scale to zero when idle (no cost)
4. **Can we shut them down programmatically?** ✅ **YES!** But you don't need to - autoscaling handles it automatically

**For MVP:** 
- ✅ **Enable autoscaling** - endpoint manages itself
- ✅ **No manual intervention needed** - it's like serverless
- ✅ **Handle cold starts in code** - use X-Scale-Up-Timeout header
- ✅ **Works like GCE VMs** - auto-starts when needed, auto-stops when idle

**This is perfect for MVP - set it and forget it!**

