"""
Finance debt payoff plan schema for storing complete payment schedules.
"""

from typing import Optional
from pydantic import BaseModel, Field


class OneTimePayment(BaseModel):
    """One-time extra payment in a specific month."""
    
    month: int = Field(
        description="Month number when payment is made (1, 2, 3...)",
        gt=0
    )
    amount: float = Field(
        description="Amount of the one-time payment",
        gt=0
    )
    description: Optional[str] = Field(
        description="Optional description (e.g., 'Tax refund', 'Bonus')",
        default=None
    )


class MonthlyPaymentRow(BaseModel):
    """Single month in a debt payoff plan."""
    
    month: int = Field(description="Month number (1, 2, 3...)")
    salary: float = Field(description="Monthly salary")
    fixed_expenses: float = Field(description="Fixed monthly expenses")
    savings_amount: float = Field(description="Amount saved this month")
    debt_payment: float = Field(description="Regular debt payment amount")
    one_time_payment: float = Field(
        description="Additional one-time payment this month",
        default=0
    )
    total_payment: float = Field(
        description="Total payment (regular + one-time)",
        default=0
    )
    interest_charged: float = Field(description="Interest added this month")
    remaining_balance: float = Field(description="Debt balance at month end")


class FinanceDebtPlan(BaseModel):
    """
    Schema for debt payoff plans with deterministic calculations.
    
    Stores complete month-by-month schedule with all financial details.
    All calculations are done in Python for accuracy.
    
    CRITICAL: All numeric calculations are rounded to 2 decimals to prevent
    floating-point drift and ensure deterministic results.
    """
    
    plan_name: str = Field(
        description="Name/description of the debt payoff plan"
    )
    
    salary: float = Field(
        description="Monthly salary (positive number)",
        gt=0
    )
    
    fixed_expenses: float = Field(
        description="Fixed monthly expenses (positive number)",
        gt=0
    )
    
    initial_debt: float = Field(
        description="Starting debt amount (positive number)",
        gt=0
    )
    
    monthly_interest_rate: float = Field(
        description="Monthly interest rate as decimal (e.g., 0.025 for 2.5%)",
        ge=0,
        le=1
    )
    
    months: int = Field(
        description="Number of months in the plan",
        gt=0
    )
    
    savings_rate: float = Field(
        description="Percentage of salary to save as decimal (e.g., 0.10 for 10%)",
        ge=0,
        le=1
    )
    
    one_time_payments: list[OneTimePayment] = Field(
        description="List of one-time extra payments (bonuses, tax refunds, etc.)",
        default_factory=list
    )
    
    monthly_rows: list[MonthlyPaymentRow] = Field(
        description="Month-by-month breakdown of the plan",
        default_factory=list
    )
    
    final_balance: float = Field(
        description="Remaining debt balance at plan end",
        default=0
    )
    
    total_saved: float = Field(
        description="Total amount saved over the plan period",
        default=0
    )
    
    total_interest_paid: float = Field(
        description="Total interest paid over the plan period",
        default=0
    )
    
    total_regular_payments: float = Field(
        description="Total regular debt payments made",
        default=0
    )
    
    total_one_time_payments: float = Field(
        description="Total one-time payments made",
        default=0
    )
    
    is_debt_cleared: bool = Field(
        description="Whether debt is fully paid off within plan period",
        default=False
    )
    
    months_to_payoff: Optional[int] = Field(
        description="Actual number of months to clear debt (may be less than planned)",
        default=None
    )
    
    recommended_payment: Optional[float] = Field(
        description="Recommended monthly payment to clear debt in N months (if needed)",
        default=None
    )
    
    validation_errors: list[str] = Field(
        description="Any validation errors or warnings",
        default_factory=list
    )
    
    created_date: str = Field(
        description="Date plan was created (YYYY-MM-DD format)",
        default=""
    )
    
    payoff_strategy: str = Field(
        description="Strategy used: 'standard', 'snowball', 'avalanche'",
        default="standard"
    )