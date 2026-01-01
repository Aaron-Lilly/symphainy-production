# LLM Integration Tests

## Overview

These tests verify that:
1. **LLM abstraction works** with actual LLM providers (OpenAI, Anthropic)
2. **Agents can call LLMs** through the abstraction layer
3. **End-to-end flow works**: Agent → LLM Abstraction → Adapter → LLM Provider

## Key Features

✅ **No Backend Startup Required** - Tests create minimal components directly  
✅ **Real LLM Calls** - Uses actual API keys to make real LLM requests  
✅ **Comprehensive Coverage** - Tests abstraction, adapters, and agent integration  

## Setup

### 1. Set API Keys

```bash
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"  # Optional
```

### 2. Run Tests

```bash
# Run all LLM integration tests
cd symphainy-platform
python3 -m pytest tests/integration/llm/ -v -s

# Run specific test
python3 -m pytest tests/integration/llm/test_llm_abstraction_integration.py::TestLLMAbstractionIntegration::test_llm_abstraction_generates_response -v -s
```

## Test Structure

### TestLLMAbstractionIntegration
Tests the LLM abstraction layer directly:
- `test_llm_abstraction_generates_response` - Verifies basic LLM call works
- `test_llm_abstraction_with_different_models` - Tests multiple models

### TestAgentLLMIntegration
Tests that agents can use LLM abstraction:
- `test_agent_can_call_llm_through_abstraction` - Verifies agent → LLM flow
- `test_llm_abstraction_error_handling` - Tests error handling

### TestContentProcessingAgentLLMIntegration
Tests agent integration with minimal setup:
- `test_agent_uses_llm_for_processing` - End-to-end agent LLM usage

## What Gets Tested

1. **LLM Abstraction** - Direct calls to LLM abstraction
2. **Adapters** - OpenAI and Anthropic adapters
3. **Agent Integration** - How agents access and use LLM abstraction
4. **Error Handling** - Invalid requests, missing API keys, etc.

## Expected Output

When tests pass, you'll see:
```
✅ LLM Response: Hello, this is a test
✅ Model: gpt-4o-mini
✅ Usage: {'prompt_tokens': 15, 'completion_tokens': 8, 'total_tokens': 23}
```

## Notes

- Tests are **skipped automatically** if API keys are not set
- Tests make **real API calls** - will consume API credits
- Tests use **minimal setup** - no full backend required
- Tests verify **end-to-end flow** - from agent to LLM provider

## Troubleshooting

### Test Skipped
If tests are skipped, check:
```bash
echo $OPENAI_API_KEY  # Should show your API key
```

### Import Errors
Make sure you're running from the project root:
```bash
cd /home/founders/demoversion/symphainy_source/symphainy-platform
python3 -m pytest tests/integration/llm/ -v
```

### API Errors
- Verify API key is valid
- Check API rate limits
- Ensure you have API credits



