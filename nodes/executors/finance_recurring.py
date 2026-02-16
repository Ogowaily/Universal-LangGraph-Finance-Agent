"""
Finance Recurring Payment Executor.

Handles recurring payment and subscription management.
"""

from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.store.base import BaseStore

from configuration import Configuration


def finance_recurring_executor(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """
    Execute recurring payment creation/update operation.
    
    Handles requests to add or modify recurring payments and subscriptions.
    The actual extraction and storage is handled by the memory_update node.
    
    Args:
        state: Current conversation state
        config: Configuration
        store: Memory store
        
    Returns:
        Tool response message
    """
    
    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    
    # Get the last message with the tool call
    last_message = state["messages"][-1]
    
    if last_message.tool_calls:
        tool_call_id = last_message.tool_calls[0].get("id")
        
        # Return confirmation message
        return {
            "messages": [{
                "role": "tool",
                "content": "Recurring payment will be added. Processing...",
                "tool_call_id": tool_call_id
            }]
        }
    
    return {"messages": []}
