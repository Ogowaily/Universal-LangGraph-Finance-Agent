"""
Finance Summary Executor.

Generates monthly spending summaries and reports.
"""

from datetime import datetime, timedelta
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.store.base import BaseStore

from configuration import Configuration
from utils.store_utils import get_all_memories_by_type
from utils.formatting import format_transaction_summary


def finance_summary_executor(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """
    Generate financial summary report.
    
    Creates a summary of transactions, spending by category,
    and budget status for the requested time period.
    
    Args:
        state: Current conversation state
        config: Configuration
        store: Memory store
        
    Returns:
        Tool response with summary
    """
    
    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    user_id = configurable.user_id
    assistant_type = configurable.assistant_type
    
    # Retrieve all transactions
    transaction_memories = get_all_memories_by_type(
        store, "finance_transactions", assistant_type, user_id
    )
    
    # Convert to list of dicts
    transactions = [mem.value for mem in transaction_memories]
    
    # Filter for current month (optional - could be parameterized)
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    current_month_transactions = [
        t for t in transactions 
        if isinstance(t.get('date'), str) and datetime.fromisoformat(t['date']) >= current_month_start
    ]
    
    # Generate summary
    summary = format_transaction_summary(current_month_transactions)
    
    # Get the last message with the tool call
    last_message = state["messages"][-1]
    
    if last_message.tool_calls:
        tool_call_id = last_message.tool_calls[0].get("id")
        
        # Return summary as tool response
        return {
            "messages": [{
                "role": "tool",
                "content": f"Monthly Summary:\n\n{summary}",
                "tool_call_id": tool_call_id
            }]
        }
    
    return {"messages": []}
