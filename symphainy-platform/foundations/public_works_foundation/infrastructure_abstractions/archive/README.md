# Archived Abstractions

This directory contains legacy abstractions that are no longer used in the platform.

## TracingAbstraction

**Status**: Archived (unused)  
**Date**: November 13, 2025  
**Reason**: Not used in Public Works Foundation or anywhere else in the platform. Nurse service uses TelemetryAbstraction for tracing instead.

**Note**: This abstraction used the old pattern (creates adapters internally). If needed in the future, it should be refactored to use dependency injection pattern for consistency with other abstractions.
