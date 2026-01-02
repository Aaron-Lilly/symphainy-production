# Ad Hoc Test Scripts Archive

**Date:** January 2025  
**Purpose:** Archive ad hoc test scripts that are not part of the CI/CD aligned test suite

## Overview

This directory contains ad hoc test scripts that were created for debugging, investigation, or one-off testing purposes. These scripts are **not part of the official test suite** located in `tests/`.

## Archived Files

- `test_503_fix.py` - Ad hoc test for 503 error fix
- `test_e2e_flow.sh` - Ad hoc E2E flow test script
- `test_optimal_architecture.py` - Ad hoc architecture test
- `test_parse_direct.sh` - Ad hoc parsing test script
- `test_phase1_imports.py` - Ad hoc import test
- `test_permissions.txt` - Ad hoc permissions test data

## Official Test Suite

The official, CI/CD aligned test suite is located in:
- `tests/` - Comprehensive test suite with unit, integration, and E2E tests

## Note

These scripts are kept for historical reference but should not be used for production testing. Use the official test suite in `tests/` instead.
