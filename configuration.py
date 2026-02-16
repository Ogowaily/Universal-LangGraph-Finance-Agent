"""
Configuration module for the Universal LangGraph Framework.

This module defines the configuration schema and provides predefined
configurations for different assistant types (finance, todo, etc.).
"""

from typing import Literal, Optional
from dataclasses import dataclass, field
from langchain_core.runnables import RunnableConfig


@dataclass(kw_only=True)
class Configuration:
    """
    Universal configuration schema for assistant behavior.
    
    Controls all aspects of the assistant including:
    - Assistant type and role
    - Enabled memory types
    - Router intents
    - System prompts
    """
    
    # User and session identifiers
    user_id: str = field(
        default="default_user",
        metadata={"description": "Unique identifier for the user"}
    )
    
    # Assistant type (finance, todo, legal, study, etc.)
    assistant_type: Literal["finance", "todo"] = field(
        default="finance",
        metadata={"description": "Type of assistant domain"}
    )
    
    # Role and behavior
    role_prompt: str = field(
        default="You are a helpful AI assistant.",
        metadata={"description": "Role description for the assistant"}
    )
    
    # Memory configuration
    enabled_memory_types: list[str] = field(
        default_factory=lambda: ["profile"],
        metadata={"description": "List of enabled memory collections (e.g., profile, transactions, budgets)"}
    )
    
    # Router configuration
    router_intents: list[str] = field(
        default_factory=lambda: ["other"],
        metadata={"description": "List of available intent options for the router"}
    )
    
    # Optional category/namespace for multi-tenancy
    category: str = field(
        default="default",
        metadata={"description": "Category or namespace for organizing data"}
    )
    
    @classmethod
    def from_runnable_config(cls, config: Optional[RunnableConfig] = None) -> "Configuration":
        """
        Create Configuration from RunnableConfig.
        
        Args:
            config: LangGraph RunnableConfig object
            
        Returns:
            Configuration instance
        """
        if not config or not config.get("configurable"):
            return cls()
        
        configurable = config["configurable"]
        return cls(**{k: v for k, v in configurable.items() if k in cls.__annotations__})


# ============================================================================
# Predefined Configurations
# ============================================================================

def get_finance_config(user_id: str = "default_user") -> dict:
    """
    Get configuration for Personal Finance Assistant.
    
    Args:
        user_id: User identifier
        
    Returns:
        Configuration dictionary
    """
    return {
        "configurable": {
            "user_id": user_id,
            "assistant_type": "finance",
            "category": "personal_finance",
            "role_prompt": """You are a Personal Finance Assistant. Your role is to help users:

- Track income and expenses
- Set and monitor budgets
- Create financial goals
- Manage recurring payments
- Provide financial advice and insights
- Generate spending summaries

You are knowledgeable, helpful, and focused on helping users achieve financial wellness.""",
            "enabled_memory_types": [
                "profile",
                "finance_transactions",
                "finance_budgets",
                "finance_goals",
                "finance_recurring_payments",
                "finance_debt_plans"
            ],
            "router_intents": [
                "add_transaction",
                "update_transaction",
                "monthly_summary",
                "set_budget",
                "create_goal",
                "add_recurring_payment",
                "debt_payoff_plan",
                "advice",
                "other"
            ]
        }
    }


def get_todo_config(user_id: str = "default_user") -> dict:
    """
    Get configuration for ToDo Assistant.
    
    Args:
        user_id: User identifier
        
    Returns:
        Configuration dictionary
    """
    return {
        "configurable": {
            "user_id": user_id,
            "assistant_type": "todo",
            "category": "tasks",
            "role_prompt": """You are a Task Management Assistant. Your role is to help users:

- Create and manage tasks
- Track task status
- Set deadlines and priorities
- Suggest solutions for completing tasks
- Organize tasks efficiently

You are organized, proactive, and focused on helping users be productive.""",
            "enabled_memory_types": [
                "profile",
                "todo_tasks",
                "todo_instructions"
            ],
            "router_intents": [
                "add_task",
                "update_task",
                "task_summary",
                "update_preferences",
                "other"
            ]
        }
    }