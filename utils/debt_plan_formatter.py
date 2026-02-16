"""
Debt Plan Presentation Formatter

Converts JSON debt plan data into beautiful markdown tables.

This ensures the LLM never does calculations - it only formats
pre-calculated data for presentation.
"""

import json


def format_debt_plan_as_markdown(plan_json: dict) -> str:
    """
    Format a debt payoff plan from JSON to markdown.
    
    Takes the deterministic Python-calculated plan and formats it
    for human-readable presentation. The LLM can use this function
    to display results without touching any numbers.
    
    Args:
        plan_json: The plan dictionary from FinanceDebtPlan.model_dump()
        
    Returns:
        Markdown-formatted string with tables and summary
    """
    
    plan = plan_json if isinstance(plan_json, dict) else json.loads(plan_json)
    currency = "EGP"  # Could be extracted from plan if needed
    
    # Header
    output = f"## 📊 {plan['plan_name']}\n\n"
    
    # Overview
    output += "**Plan Overview:**\n\n"
    output += f"- 💰 Monthly Salary: **{plan['salary']:,.0f} {currency}**\n"
    output += f"- 📌 Fixed Expenses: **{plan['fixed_expenses']:,.0f} {currency}**\n"
    output += f"- 💳 Initial Debt: **{plan['initial_debt']:,.0f} {currency}**\n"
    output += f"- 📈 Monthly Interest Rate: **{plan['monthly_interest_rate'] * 100:.2f}%**\n"
    output += f"- 💾 Savings Rate: **{plan['savings_rate'] * 100:.0f}%** of salary\n"
    output += f"- ⏱️ Plan Duration: **{plan['months']} months**\n\n"
    
    # One-time payments if any
    if plan.get('one_time_payments') and len(plan['one_time_payments']) > 0:
        output += "**Scheduled Bonuses/Extra Payments:**\n\n"
        for otp in plan['one_time_payments']:
            desc = otp.get('description', 'Extra payment')
            output += f"- Month {otp['month']}: **{otp['amount']:,.0f} {currency}** ({desc})\n"
        output += "\n"
    
    # Month-by-month table
    output += "### Monthly Breakdown\n\n"
    output += "| Month | Salary | Fixed Exp | Savings | Regular Payment | Bonus/Extra | Total Payment | Interest | Balance |\n"
    output += "|-------|--------|-----------|---------|-----------------|-------------|---------------|----------|----------|\n"
    
    for row in plan['monthly_rows']:
        output += f"| {row['month']} "
        output += f"| {row['salary']:,.0f} "
        output += f"| {row['fixed_expenses']:,.0f} "
        output += f"| {row['savings_amount']:,.0f} "
        output += f"| {row['debt_payment']:,.0f} "
        output += f"| {row['one_time_payment']:,.0f} " if row['one_time_payment'] > 0 else "| — "
        output += f"| **{row['total_payment']:,.0f}** "
        output += f"| {row['interest_charged']:.2f} "
        output += f"| {row['remaining_balance']:.2f} |\n"
    
    # Summary
    output += "\n### 📊 Summary\n\n"
    
    if plan['is_debt_cleared']:
        output += f"✅ **Debt Fully Cleared!**\n\n"
        if plan.get('months_to_payoff'):
            output += f"- 🎯 Paid off in: **{plan['months_to_payoff']} months** "
            if plan['months_to_payoff'] < plan['months']:
                output += f"(ahead of {plan['months']}-month plan!)"
            output += "\n"
    else:
        output += f"⚠️ **Debt Not Fully Cleared**\n\n"
        output += f"- Remaining balance: **{plan['final_balance']:,.2f} {currency}**\n"
        if plan.get('recommended_payment'):
            output += f"- 💡 To clear in {plan['months']} months, increase payment to: **{plan['recommended_payment']:,.2f} {currency}/month**\n"
    
    output += f"\n**Financial Results:**\n\n"
    output += f"- 💰 Total Saved: **{plan['total_saved']:,.0f} {currency}**\n"
    output += f"- 📈 Total Interest Paid: **{plan['total_interest_paid']:,.2f} {currency}**\n"
    output += f"- 💳 Total Regular Payments: **{plan['total_regular_payments']:,.2f} {currency}**\n"
    
    if plan.get('total_one_time_payments', 0) > 0:
        output += f"- 🎁 Total Bonus/Extra Payments: **{plan['total_one_time_payments']:,.0f} {currency}**\n"
    
    # Validation warnings
    if plan.get('validation_errors') and len(plan['validation_errors']) > 0:
        output += "\n### ⚠️ Warnings\n\n"
        for error in plan['validation_errors']:
            output += f"- {error}\n"
    
    # Metadata footer
    output += f"\n---\n"
    output += f"*Calculated by: {plan.get('payoff_strategy', 'standard').title()} Strategy*  \n"
    output += f"*Plan created: {plan.get('created_date', 'N/A')}*\n"
    
    return output


def format_debt_plan_summary(plan_json: dict) -> str:
    """
    Create a short summary of the debt plan (1-2 paragraphs).
    
    Perfect for the main_assistant to use in conversational responses.
    
    Args:
        plan_json: The plan dictionary
        
    Returns:
        Short summary text
    """
    plan = plan_json if isinstance(plan_json, dict) else json.loads(plan_json)
    
    months_actual = plan.get('months_to_payoff', plan['months'])
    debt_cleared = plan['is_debt_cleared']
    
    summary = f"Your {plan['months']}-month debt payoff plan is ready! "
    
    if debt_cleared:
        summary += f"Great news: you'll clear the {plan['initial_debt']:,.0f} EGP debt in just **{months_actual} months** "
        if months_actual < plan['months']:
            summary += f"(ahead of schedule!) "
        summary += f"while saving {plan['savings_rate'] * 100:.0f}% of your salary. "
    else:
        summary += f"With your current budget, you'll reduce the {plan['initial_debt']:,.0f} EGP debt to {plan['final_balance']:,.2f} EGP. "
        if plan.get('recommended_payment'):
            summary += f"To fully clear it, consider increasing your monthly payment to {plan['recommended_payment']:,.2f} EGP. "
    
    summary += f"\n\nYou'll pay {plan['total_interest_paid']:,.2f} EGP in total interest and save {plan['total_saved']:,.0f} EGP over the plan period."
    
    if plan.get('total_one_time_payments', 0) > 0:
        summary += f" Your bonus/extra payments of {plan['total_one_time_payments']:,.0f} EGP will significantly accelerate payoff!"
    
    return summary


# Example usage for testing
if __name__ == "__main__":
    # Test data
    test_plan = {
        "plan_name": "6-Month Debt Payoff Plan",
        "salary": 12000,
        "fixed_expenses": 7500,
        "initial_debt": 20000,
        "monthly_interest_rate": 0.025,
        "months": 6,
        "savings_rate": 0.1,
        "one_time_payments": [],
        "monthly_rows": [
            {
                "month": 1,
                "salary": 12000,
                "fixed_expenses": 7500,
                "savings_amount": 1200,
                "debt_payment": 3300,
                "one_time_payment": 0,
                "total_payment": 3300,
                "interest_charged": 500.00,
                "remaining_balance": 17200.00
            }
        ],
        "final_balance": 0,
        "total_saved": 7200,
        "total_interest_paid": 1914.34,
        "total_regular_payments": 19800,
        "total_one_time_payments": 0,
        "is_debt_cleared": True,
        "months_to_payoff": 6,
        "payoff_strategy": "standard",
        "created_date": "2026-02-16"
    }
    
    print(format_debt_plan_as_markdown(test_plan))
    print("\n" + "="*80 + "\n")
    print(format_debt_plan_summary(test_plan))