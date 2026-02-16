"""
Finance Budget Executor.

Handles budget creation and management.
"""

from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.store.base import BaseStore

from configuration import Configuration


def finance_budget_executor(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """
    Execute budget creation/update operation.
    
    Handles requests to set or modify budgets for spending categories.
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
                "content": "Budget will be set. Processing...",
                "tool_call_id": tool_call_id
            }]
        }
    
    return {"messages": []}
