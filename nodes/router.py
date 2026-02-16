"""
Router node - determines which executor to invoke.

This node examines the RouteIntent tool call from main_assistant
and routes to the appropriate executor based on the intent.
"""

from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState

from configuration import Configuration
from utils.intent_registry import get_executor_for_intent


def router(state: MessagesState, config: RunnableConfig):
    """
    Route to appropriate executor based on intent.
    
    This is a pass-through node that doesn't modify state.
    The actual routing is done via conditional edges.
    
    Args:
        state: Current conversation state
        config: Configuration with assistant type
        
    Returns:
        Empty dict (no state updates)
    """
    # Router doesn't update state, just determines next node via conditional edge
    return {}


def route_to_executor(state: MessagesState, config: RunnableConfig):
    """
    Determine which executor to invoke based on intent.
    
    This function is used in conditional edges to route to the
    appropriate executor node.
    
    Args:
        state: Current conversation state
        config: Configuration with assistant type
        
    Returns:
        Name of the executor node to invoke
    """
    
    # Extract configuration
    configurable = Configuration.from_runnable_config(config)
    assistant_type = configurable.assistant_type
    
    # Find the most recent AI message with RouteIntent tool call
    route_intent_call = None
    for msg in reversed(state["messages"]):
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc.get("name") == "RouteIntent":
                    route_intent_call = tc
                    break
        if route_intent_call:
            break
    
    # If no RouteIntent found, go to memory_update
    if not route_intent_call:
        return "memory_update"
    
    # Extract the intent
    intent = route_intent_call.get("args", {}).get("intent", "other")
    
    # Look up the executor for this intent
    executor_name = get_executor_for_intent(assistant_type, intent)
    
    if executor_name:
        return executor_name
    else:
        # Fallback to main_assistant for unknown intents
        return "main_assistant"