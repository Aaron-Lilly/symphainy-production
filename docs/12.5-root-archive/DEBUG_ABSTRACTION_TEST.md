# Debug: Abstraction Access Issue

## Problem
`self.service.file_management_abstraction` is a coroutine instead of the abstraction object.

## Investigation
Content Steward is calling:
```python
self.service.file_management_abstraction = self.service.get_infrastructure_abstraction("file_management")
```

But `get_infrastructure_abstraction` is NOT async (it's `def`, not `async def`).

So the issue must be that something in the chain is returning a coroutine.

## Hypothesis
The `abstraction_map` in Public Works `get_abstraction()` might be storing coroutines instead of actual objects.

Let me check what's in `self.file_management_abstraction` in Public Works.

## Next Steps
1. Add debug logging to see what type `self.file_management_abstraction` is in Public Works
2. Check if it's being set to a coroutine during initialization






