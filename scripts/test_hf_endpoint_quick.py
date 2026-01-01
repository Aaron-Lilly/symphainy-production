#!/usr/bin/env python3
"""
Quick test of HuggingFace endpoint.

Usage:
    export HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL="https://xxx.us-east-1.aws.endpoints.huggingface.cloud"
    export HUGGINGFACE_EMBEDDINGS_API_KEY="hf_xxx"
    python scripts/test_hf_endpoint_quick.py
"""

import os
import sys
import asyncio
import httpx

async def test_endpoint():
    endpoint_url = os.getenv("HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL")
    api_key = os.getenv("HUGGINGFACE_EMBEDDINGS_API_KEY")
    
    if not endpoint_url:
        print("❌ HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL not set!")
        print("   Set it with: export HUGGINGFACE_EMBEDDINGS_ENDPOINT_URL='https://xxx...'")
        return False
    
    if not api_key:
        print("❌ HUGGINGFACE_EMBEDDINGS_API_KEY not set!")
        print("   Get it from: https://huggingface.co/settings/tokens")
        print("   Set it with: export HUGGINGFACE_EMBEDDINGS_API_KEY='hf_xxx'")
        return False
    
    print(f"🧪 Testing endpoint: {endpoint_url}")
    print(f"   API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
    
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
                print(f"   Last 5 values: {embedding[-5:]}")
                return True
            else:
                print(f"❌ Unexpected response format: {result}")
                return False
    
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 503:
            print("⚠️  503 Service Unavailable - endpoint may be scaling up (cold start)")
            print("   Wait 30-60 seconds and try again")
            print(f"   Response: {e.response.text}")
        elif e.response.status_code == 401:
            print("❌ 401 Unauthorized - check your API key")
            print("   Get token from: https://huggingface.co/settings/tokens")
        elif e.response.status_code == 404:
            print("❌ 404 Not Found - check your endpoint URL")
        else:
            print(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
        return False
    
    except httpx.TimeoutException:
        print("❌ Timeout - endpoint may be taking too long to scale up")
        print("   Try again in a minute")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_endpoint())
    sys.exit(0 if success else 1)






