"""
Schema package for the Universal LangGraph Framework.
"""

from .profile import Profile
from .finance_transaction import FinanceTransaction
from .finance_budget import FinanceBudget
from .finance_goal import FinanceGoal
from .finance_recurring import FinanceRecurringPayment
from .finance_debt_plan import FinanceDebtPlan, MonthlyPaymentRow, OneTimePayment  # ← ADD OneTimePayment HERE

__all__ = [
    "Profile",
    "FinanceTransaction",
    "FinanceBudget",
    "FinanceGoal",
    "FinanceRecurringPayment",
    "FinanceDebtPlan",
    "MonthlyPaymentRow",
    "OneTimePayment"  # ← ADD THIS LINE
]