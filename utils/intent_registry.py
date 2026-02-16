"""
Intent registry for mapping router intents to executor nodes.

This module provides the mapping between intent strings and their
corresponding executor node names, enabling dynamic routing.
"""

from typing import Optional


# ============================================================================
# Intent to Executor Mapping
# ============================================================================

INTENT_REGISTRY = {
    "finance": {
        "add_transaction": "finance_add_transaction_executor",
        "update_transaction": "finance_add_transaction_executor",  # Same executor handles updates
        "monthly_summary": "finance_summary_executor",
        "set_budget": "finance_budget_executor",
        "create_goal": "finance_goal_executor",
        "add_recurring_payment": "finance_recurring_executor",
        "advice": "finance_advice_executor",
        "debt_payoff_plan": "finance_debt_payoff_executor",  # NEW: Deterministic calculations
        "other": "main_assistant"  # Route back to main assistant for general queries
    },
    "todo": {
        "add_task": "todo_add_task_executor",
        "update_task": "todo_update_task_executor",
        "task_summary": "todo_summary_executor",
        "update_preferences": "todo_preferences_executor",
        "other": "main_assistant"
    }
}


def get_executor_for_intent(assistant_type: str, intent: str) -> Optional[str]:
    """
    Get the executor node name for a specific intent.
    
    Args:
        assistant_type: Type of assistant (e.g., 'finance', 'todo')
        intent: Intent name from router (e.g., 'add_transaction', 'set_budget')
        
    Returns:
        Executor node name or None if not found
        
    Example:
        >>> executor = get_executor_for_intent('finance', 'add_transaction')
        >>> # Returns 'finance_add_transaction_executor'
    """
    return INTENT_REGISTRY.get(assistant_type, {}).get(intent)


def get_all_intents_for_assistant(assistant_type: str) -> list[str]:
    """
    Get all available intents for a specific assistant type.
    
    Args:
        assistant_type: Type of assistant
        
    Returns:
        List of intent names
    """
    return list(INTENT_REGISTRY.get(assistant_type, {}).keys())