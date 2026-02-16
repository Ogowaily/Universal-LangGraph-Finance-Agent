"""
Schema registry for mapping memory types to Pydantic schemas.

This module provides dynamic schema lookup based on assistant type
and memory type, enabling the framework to support multiple domains.
"""

from typing import Type, Optional
from pydantic import BaseModel

from schemas import (
    Profile,
    FinanceTransaction,
    FinanceBudget,
    FinanceGoal,
    FinanceRecurringPayment,
    FinanceDebtPlan
)


# ============================================================================
# Schema Registry Mapping
# ============================================================================

SCHEMA_REGISTRY = {
    "finance": {
        "profile": Profile,
        "finance_transactions": FinanceTransaction,
        "finance_budgets": FinanceBudget,
        "finance_goals": FinanceGoal,
        "finance_recurring_payments": FinanceRecurringPayment,
        "finance_debt_plans": FinanceDebtPlan
    },
    "todo": {
        "profile": Profile,
        # Add ToDo schemas here when implemented
    }
}


def get_schema_for_memory_type(
    assistant_type: str,
    memory_type: str
) -> Optional[Type[BaseModel]]:
    """
    Get the Pydantic schema for a specific memory type and assistant.
    
    Args:
        assistant_type: Type of assistant (e.g., 'finance', 'todo')
        memory_type: Type of memory (e.g., 'profile', 'finance_transactions')
        
    Returns:
        Pydantic BaseModel class or None if not found
        
    Example:
        >>> schema = get_schema_for_memory_type('finance', 'finance_transactions')
        >>> # Returns FinanceTransaction class
    """
    return SCHEMA_REGISTRY.get(assistant_type, {}).get(memory_type)


def get_all_schemas_for_assistant(assistant_type: str) -> dict[str, Type[BaseModel]]:
    """
    Get all schemas available for a specific assistant type.
    
    Args:
        assistant_type: Type of assistant
        
    Returns:
        Dictionary mapping memory types to schema classes
        
    Example:
        >>> schemas = get_all_schemas_for_assistant('finance')
        >>> # Returns {'profile': Profile, 'finance_transactions': FinanceTransaction, ...}
    """
    return SCHEMA_REGISTRY.get(assistant_type, {})


def get_schema_name(schema_class: Type[BaseModel]) -> str:
    """
    Get the name of a schema class for use in tool calls.
    
    Args:
        schema_class: Pydantic BaseModel class
        
    Returns:
        Schema name as string
    """
    return schema_class.__name__