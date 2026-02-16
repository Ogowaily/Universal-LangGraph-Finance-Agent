"""
Formatting utilities for output messages and summaries.

Provides helpers for formatting tool calls, transaction summaries,
and other user-facing content.
"""

from datetime import datetime
from typing import Any


def extract_tool_info(tool_calls: list, schema_name: str = "Memory") -> str:
    """
    Extract information from tool calls for both patches and new memories.
    
    Used to create user-friendly messages about what was updated in memory.
    
    Args:
        tool_calls: List of tool calls from the model
        schema_name: Name of the schema tool (e.g., "Memory", "FinanceTransaction")
        
    Returns:
        Formatted string describing the changes
    """
    changes = []
    
    for call_group in tool_calls:
        for call in call_group:
            if call['name'] == 'PatchDoc':
                # Check if there are any patches
                if call['args']['patches']:
                    changes.append({
                        'type': 'update',
                        'doc_id': call['args']['json_doc_id'],
                        'planned_edits': call['args']['planned_edits'],
                        'value': call['args']['patches'][0]['value']
                    })
                else:
                    # Handle case where no changes were needed
                    changes.append({
                        'type': 'no_update',
                        'doc_id': call['args']['json_doc_id'],
                        'planned_edits': call['args']['planned_edits']
                    })
            elif call['name'] == schema_name:
                changes.append({
                    'type': 'new',
                    'value': call['args']
                })

    # Format results as a single string
    result_parts = []
    for change in changes:
        if change['type'] == 'update':
            result_parts.append(
                f"Document {change['doc_id']} updated:\n"
                f"Plan: {change['planned_edits']}\n"
                f"Added content: {change['value']}"
            )
        elif change['type'] == 'no_update':
            result_parts.append(
                f"Document {change['doc_id']} unchanged:\n"
                f"{change['planned_edits']}"
            )
        else:
            result_parts.append(
                f"New {schema_name} created:\n"
                f"Content: {change['value']}"
            )
    
    return "\n\n".join(result_parts) if result_parts else "No changes made"


def format_transaction_summary(transactions: list[dict]) -> str:
    """
    Format a list of transactions into a readable summary.
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Formatted string summary
    """
    if not transactions:
        return "No transactions found."
    
    total_income = sum(t.get('amount', 0) for t in transactions if t.get('transaction_type') == 'income')
    total_expenses = sum(t.get('amount', 0) for t in transactions if t.get('transaction_type') == 'expense')
    
    summary_parts = [
        f"Total Transactions: {len(transactions)}",
        f"Total Income: ${total_income:.2f}",
        f"Total Expenses: ${total_expenses:.2f}",
        f"Net: ${total_income - total_expenses:.2f}",
        "\nRecent Transactions:"
    ]
    
    # Show recent transactions
    for i, trans in enumerate(transactions[:5], 1):
        trans_type = trans.get('transaction_type', 'unknown').upper()
        amount = trans.get('amount', 0)
        category = trans.get('category', 'uncategorized')
        description = trans.get('description', 'No description')
        
        summary_parts.append(
            f"{i}. [{trans_type}] ${amount:.2f} - {category}: {description}"
        )
    
    return "\n".join(summary_parts)


def format_budget_status(budgets: list[dict], transactions: list[dict]) -> str:
    """
    Format budget status with spending comparison.
    
    Args:
        budgets: List of budget dictionaries
        transactions: List of transaction dictionaries
        
    Returns:
        Formatted budget status string
    """
    if not budgets:
        return "No budgets set."
    
    status_parts = ["Budget Status:\n"]
    
    for budget in budgets:
        category = budget.get('category', 'unknown')
        limit = budget.get('limit_amount', 0)
        
        # Calculate spending for this category
        spent = sum(
            t.get('amount', 0) 
            for t in transactions 
            if t.get('category') == category and t.get('transaction_type') == 'expense'
        )
        
        percentage = (spent / limit * 100) if limit > 0 else 0
        remaining = limit - spent
        
        status_parts.append(
            f"• {category}: ${spent:.2f} / ${limit:.2f} ({percentage:.1f}% used)\n"
            f"  Remaining: ${remaining:.2f}"
        )
    
    return "\n".join(status_parts)


class Spy:
    """
    Utility class to inspect tool calls made during Trustcall extraction.
    
    Used to track what tools were called and with what arguments.
    """
    
    def __init__(self):
        self.called_tools = []

    def __call__(self, run):
        q = [run]
        while q:
            r = q.pop()
            if r.child_runs:
                q.extend(r.child_runs)
            if r.run_type == "chat_model":
                self.called_tools.append(
                    r.outputs["generations"][0][0]["message"]["kwargs"]["tool_calls"]
                )
