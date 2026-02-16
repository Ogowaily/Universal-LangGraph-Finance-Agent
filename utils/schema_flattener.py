"""
Schema flattening utilities for Groq compatibility.

Groq doesn't support $defs references in JSON schemas,
so we need to flatten Pydantic schemas before using them.
"""

from typing import Type, Any, Dict
from pydantic import BaseModel


def flatten_schema_for_groq(schema_class: Type[BaseModel]) -> Dict[str, Any]:
    """
    Flatten a Pydantic schema by removing $defs and inlining all references.
    
    Args:
        schema_class: Pydantic BaseModel class
        
    Returns:
        Flattened schema dictionary compatible with Groq
    """
    # Get the raw schema
    raw_schema = schema_class.model_json_schema()
    
    # Extract $defs if they exist
    defs = raw_schema.pop("$defs", {})
    
    # Recursively resolve all $ref references
    def resolve_refs(obj: Any) -> Any:
        if isinstance(obj, dict):
            if "$ref" in obj:
                # Extract reference name
                ref_path = obj["$ref"].split("/")[-1]
                if ref_path in defs:
                    # Return resolved definition
                    return resolve_refs(defs[ref_path].copy())
                else:
                    # Fallback to generic type
                    return {"type": "string"}
            else:
                # Recursively resolve all nested dicts
                return {k: resolve_refs(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [resolve_refs(item) for item in obj]
        else:
            return obj
    
    # Resolve all references in the schema
    flattened = resolve_refs(raw_schema)
    
    # Clean up additional Pydantic-specific fields that Groq doesn't like
    if "title" in flattened:
        del flattened["title"]
    
    # Ensure we have the basic structure Groq expects
    if "properties" not in flattened:
        flattened["properties"] = {}
    
    if "type" not in flattened:
        flattened["type"] = "object"
    
    # Simplify datetime fields to strings
    if "properties" in flattened:
        for prop_name, prop_def in flattened["properties"].items():
            if isinstance(prop_def, dict):
                # Convert datetime to string type
                if prop_def.get("format") == "date-time":
                    prop_def["type"] = "string"
                    prop_def["description"] = prop_def.get("description", "") + " (format: YYYY-MM-DD or ISO 8601)"
                    if "format" in prop_def:
                        del prop_def["format"]
                
                # Simplify anyOf/allOf to just the first type
                if "anyOf" in prop_def:
                    # Take the first non-null type
                    for option in prop_def["anyOf"]:
                        if isinstance(option, dict) and option.get("type") != "null":
                            prop_def.update(option)
                            break
                    del prop_def["anyOf"]
    
    return flattened


def create_groq_compatible_tool(schema_class: Type[BaseModel]) -> Dict[str, Any]:
    """
    Create a Groq-compatible tool definition from a Pydantic schema.
    
    Args:
        schema_class: Pydantic BaseModel class
        
    Returns:
        Tool definition dictionary for Groq API
    """
    flattened_schema = flatten_schema_for_groq(schema_class)
    
    return {
        "type": "function",
        "function": {
            "name": schema_class.__name__,
            "description": schema_class.__doc__.strip() if schema_class.__doc__ else schema_class.__name__,
            "parameters": flattened_schema
        }
    }