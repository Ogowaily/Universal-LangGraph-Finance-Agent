"""
Finance Add Transaction Executor.

Handles adding and updating financial transactions.
"""

from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.store.base import BaseStore

from configuration import Configuration


def finance_add_transaction_executor(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """
    Execute transaction addition/update operation.
    
    This executor handles requests to add or update financial transactions.
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
    
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        # Get tool call ID
        tool_call = last_message.tool_calls[0]
        tool_call_id = tool_call.get("id") if isinstance(tool_call, dict) else getattr(tool_call, "id", "unknown")
        
        # Return confirmation message as a dict (not ToolMessage object)
        return {
            "messages": [{
                "role": "tool",
                "content": "Transaction will be recorded. Processing...",
                "tool_call_id": tool_call_id
            }]
        }
    
    return {"messages": []}