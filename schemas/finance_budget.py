"""
Finance budget schema for setting spending limits.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class FinanceBudget(BaseModel):
    """
    Schema for budget limits.
    
    Allows users to set spending limits for different
    categories and time periods.
    """
    
    category: str = Field(
        description="Budget category (e.g., 'groceries', 'entertainment', 'utilities')"
    )
    
    limit_amount: float = Field(
        description="Maximum amount allowed for this budget (positive number)",
        gt=0
    )
    
    period: Literal["weekly", "monthly", "yearly"] = Field(
        description="Time period for the budget",
        default="monthly"
    )
    
    alert_threshold: Optional[float] = Field(
        description="Percentage (0-100) at which to alert user (e.g., 80 means alert at 80% of limit)",
        default=80,
        ge=0,
        le=100
    )
    
    notes: Optional[str] = Field(
        description="Additional notes about this budget",
        default=None
    )
