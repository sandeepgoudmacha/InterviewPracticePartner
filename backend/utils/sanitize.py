"""JSON sanitization utilities for handling NaN and infinity values."""
import json
import math
from typing import Any, Dict, List, Union


def sanitize_for_json(value: Any) -> Any:
    """
    Recursively sanitize values to be JSON-serializable.
    
    Replaces NaN and infinity values with appropriate substitutes.
    
    Args:
        value: Value to sanitize (can be dict, list, float, or any JSON-compatible type)
        
    Returns:
        Sanitized value safe for JSON serialization
    """
    if isinstance(value, dict):
        return {k: sanitize_for_json(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [sanitize_for_json(item) for item in value]
    elif isinstance(value, float):
        # Handle NaN and infinity
        if math.isnan(value):
            return 0.0
        elif math.isinf(value):
            return float('1e308') if value > 0 else float('-1e308')
        else:
            return value
    else:
        return value


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize an object to JSON, handling NaN and infinity values.
    
    Args:
        obj: Object to serialize
        **kwargs: Additional arguments to pass to json.dumps()
        
    Returns:
        JSON string
    """
    sanitized = sanitize_for_json(obj)
    return json.dumps(sanitized, **kwargs)
