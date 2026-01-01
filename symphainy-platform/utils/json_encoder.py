#!/usr/bin/env python3
"""
Custom JSON Encoder for FastAPI

Handles non-serializable types (numpy, pandas, etc.) that may appear in API responses.
This is a safety net to ensure all responses can be JSON-serialized, even if they contain
types that aren't natively JSON-serializable.

Future-proof: If we move away from numpy, this encoder will still handle other edge cases
like pandas DataFrames, custom objects, etc.
"""

import json
from typing import Any
from datetime import datetime
from decimal import Decimal


def sanitize_for_json(data: Any, visited: set = None) -> Any:
    """
    Recursively sanitize data for JSON serialization.
    
    Handles:
    - Numpy types (int64, float64, bool_, arrays, etc.)
    - Pandas types (DataFrame, Series, etc.)
    - Datetime objects
    - Decimal objects
    - Circular references
    - Other non-serializable types
    
    Args:
        data: Data to sanitize
        visited: Set of visited object IDs (for circular reference detection)
    
    Returns:
        JSON-serializable data
    """
    if visited is None:
        visited = set()
    
    # Handle None
    if data is None:
        return None
    
    # Handle circular references
    obj_id = id(data)
    if obj_id in visited:
        return "<circular_reference>"
    visited.add(obj_id)
    
    try:
        # Handle numpy types FIRST (before simple types)
        try:
            import numpy as np
            # Check by isinstance (catches all numpy integer/float types)
            if isinstance(data, np.integer):
                return int(data)
            if isinstance(data, np.floating):
                return float(data)
            if isinstance(data, np.bool_):
                return bool(data)
            # Check by module name (catches any numpy type)
            if hasattr(data, '__class__') and hasattr(data.__class__, '__module__'):
                if data.__class__.__module__ == 'numpy':
                    # Try .item() method (works for scalars)
                    if hasattr(data, 'item'):
                        try:
                            return data.item()
                        except (ValueError, AttributeError):
                            pass
                    # For arrays, convert to list
                    if isinstance(data, np.ndarray):
                        return [sanitize_for_json(item, visited) for item in data.tolist()]
                    # Fallback: try direct conversion
                    try:
                        if isinstance(data, (np.integer,)):
                            return int(data)
                        if isinstance(data, (np.floating,)):
                            return float(data)
                        if isinstance(data, (np.bool_,)):
                            return bool(data)
                    except (ValueError, TypeError):
                        return str(data)  # Last resort: convert to string
        except ImportError:
            pass  # numpy not available
        except (AttributeError, ValueError, TypeError) as e:
            # If numpy conversion fails, continue to other type checks
            pass
        
        # Handle pandas types
        try:
            import pandas as pd
            if isinstance(data, pd.DataFrame):
                return sanitize_for_json(data.to_dict('records'), visited)
            if isinstance(data, pd.Series):
                return sanitize_for_json(data.to_dict(), visited)
            if isinstance(data, pd.Index):
                return sanitize_for_json(data.tolist(), visited)
        except ImportError:
            pass  # pandas not available
        except (AttributeError, ValueError, TypeError):
            pass
        
        # Handle simple types (after numpy/pandas checks)
        if isinstance(data, (str, int, float, bool)):
            return data
        
        # Handle datetime
        if isinstance(data, datetime):
            return data.isoformat()
        
        # Handle Decimal
        if isinstance(data, Decimal):
            return float(data)
        
        # Handle dict
        if isinstance(data, dict):
            return {str(k): sanitize_for_json(v, visited) for k, v in data.items()}
        
        # Handle list/tuple
        if isinstance(data, (list, tuple)):
            return [sanitize_for_json(item, visited) for item in data]
        
        # Handle objects with __dict__
        if hasattr(data, '__dict__'):
            return sanitize_for_json(data.__dict__, visited)
        
        # Try to convert to string for other types
        try:
            return str(data)
        except Exception:
            return "<non_serializable>"
    
    finally:
        visited.discard(obj_id)


def custom_jsonable_encoder(
    obj: Any,
    *,
    include: set = None,
    exclude: set = None,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    custom_encoder: dict = None,
    sqlalchemy_safe: bool = True,
) -> Any:
    """
    Custom JSON encoder function for FastAPI.
    
    This is a drop-in replacement for FastAPI's jsonable_encoder that adds support
    for numpy/pandas types. It sanitizes numpy types FIRST, then uses FastAPI's
    original encoder for Pydantic models and other types.
    
    Args:
        obj: Object to encode
        include: Set of fields to include
        exclude: Set of fields to exclude
        by_alias: Use field aliases
        exclude_unset: Exclude unset fields
        exclude_defaults: Exclude default values
        exclude_none: Exclude None values
        custom_encoder: Custom encoder dictionary
        sqlalchemy_safe: SQLAlchemy safety mode
    
    Returns:
        JSON-serializable representation of the object
    """
    # FIRST: Sanitize numpy/pandas types to prevent FastAPI encoder from failing
    # This must happen before FastAPI's encoder, which can't handle numpy types
    sanitized_obj = sanitize_for_json(obj)
    
    # THEN: Use FastAPI's original encoder for Pydantic models, etc.
    # This handles Pydantic models, SQLAlchemy models, and other FastAPI-specific types
    try:
        from fastapi.encoders import jsonable_encoder as _original_encoder
        # Call original encoder on sanitized object
        encoded = _original_encoder(
            sanitized_obj,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            custom_encoder=custom_encoder,
            sqlalchemy_safe=sqlalchemy_safe,
        )
        # Final sanitization pass (in case encoder introduced new numpy types)
        return sanitize_for_json(encoded)
    except Exception as e:
        # If FastAPI's encoder fails, return sanitized object directly
        # This ensures we always return something JSON-serializable
        return sanitized_obj

