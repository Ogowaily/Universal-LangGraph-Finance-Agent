"""
Finance recurring payment schema for subscriptions and regular payments.
"""

from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FinanceRecurringPayment(BaseModel):
    """
    Schema for recurring payments and subscriptions.
    
    Tracks subscriptions, bills, and other regular payments
    with frequency and amount information.
    """
    
    name: str = Field(
        description="Name of the recurring payment (e.g., 'Netflix', 'Rent', 'Gym Membership')"
    )
    
    amount: float = Field(
        description="Amount of each payment (positive number)",
        gt=0
    )
    
    frequency: Literal["daily", "weekly", "monthly", "yearly"] = Field(
        description="How often the payment recurs"
    )
    
    category: str = Field(
        description="Category of the payment (e.g., 'subscriptions', 'utilities', 'rent')"
    )
    
    next_payment_date: str = Field(
        description="Date of the next scheduled payment in YYYY-MM-DD format (e.g., '2025-03-15')"
    )
    
    payment_method: Optional[str] = Field(
        description="Payment method (e.g., 'credit card', 'bank transfer')",
        default=None
    )
    
    auto_pay: bool = Field(
        description="Whether this payment is automatically charged",
        default=False
    )
    
    notes: Optional[str] = Field(
        description="Additional notes about the recurring payment",
        default=None
    )