#!/usr/bin/env python3
"""
Insurance Use Case Templates Package

Contains Saga Journey and Solution Composer templates for Insurance Use Case.
"""

from .saga_journey_templates import (
    INSURANCE_WAVE_MIGRATION_SAGA,
    POLICY_MAPPING_SAGA,
    WAVE_VALIDATION_SAGA,
    register_saga_templates
)

from .solution_composer_templates import (
    INSURANCE_MIGRATION_SOLUTION,
    INSURANCE_DISCOVERY_JOURNEY,
    INSURANCE_VALIDATION_JOURNEY,
    register_solution_templates
)

__all__ = [
    "INSURANCE_WAVE_MIGRATION_SAGA",
    "POLICY_MAPPING_SAGA",
    "WAVE_VALIDATION_SAGA",
    "register_saga_templates",
    "INSURANCE_MIGRATION_SOLUTION",
    "INSURANCE_DISCOVERY_JOURNEY",
    "INSURANCE_VALIDATION_JOURNEY",
    "register_solution_templates"
]











