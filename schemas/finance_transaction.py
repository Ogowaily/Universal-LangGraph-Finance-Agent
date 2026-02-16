"""
Finance transaction schema for tracking income and expenses.
"""

from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class FinanceTransaction(BaseModel):
    """
    Schema for financial transactions (income or expenses).
    
    Tracks all monetary transactions with categorization,
    amounts, and metadata.
    """
    
    transaction_type: Literal["income", "expense"] = Field(
        description="Type of transaction: income or expense"
    )
    
    amount: float = Field(
        description="Transaction amount (positive number)",
        gt=0
    )
    
    category: str = Field(
        description="Category of the transaction (e.g., 'groceries', 'salary', 'entertainment', 'utilities')"
    )
    
    description: str = Field(
        description="Brief description of the transaction"
    )
    
    date: str = Field(
        description="Date and time of the transaction in YYYY-MM-DD format (e.g., '2025-02-14')",
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d")
    )
    
    payment_method: Optional[str] = Field(
        description="Payment method used (e.g., 'credit card', 'cash', 'bank transfer')",
        default=None
    )
    
    merchant: Optional[str] = Field(
        description="Merchant or source of transaction",
        default=None
    )
    
    tags: list[str] = Field(
        description="Additional tags for categorization",
        default_factory=list
    )