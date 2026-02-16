"""
Finance goal schema for tracking savings and financial objectives.
"""

from typing import Optional
from datetime import date
from pydantic import BaseModel, Field


class FinanceGoal(BaseModel):
    """
    Schema for financial goals.
    
    Tracks savings goals, target amounts, and progress
    toward financial objectives.
    """
    
    goal_name: str = Field(
        description="Name of the financial goal (e.g., 'Emergency Fund', 'Vacation', 'New Car')"
    )
    
    target_amount: float = Field(
        description="Target amount to save (positive number)",
        gt=0
    )
    
    current_amount: float = Field(
        description="Current amount saved toward the goal",
        default=0,
        ge=0
    )
    
    target_date: Optional[str] = Field(
        description="Target date to achieve the goal in YYYY-MM-DD format (e.g., '2025-12-31')",
        default=None
    )
    
    priority: Optional[str] = Field(
        description="Priority level (e.g., 'high', 'medium', 'low')",
        default="medium"
    )
    
    notes: Optional[str] = Field(
        description="Additional notes about the goal",
        default=None
    )