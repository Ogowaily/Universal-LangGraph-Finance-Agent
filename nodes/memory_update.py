"""
Memory update node - orchestrates memory updates using Trustcall.

This node handles automatic extraction and updating of memories
based on conversation context, using Trustcall for structured extraction.
"""

import uuid
from datetime import datetime

from langchain_core.messages import SystemMessage, merge_message_runs
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.store.base import BaseStore

from trustcall import create_extractor

from configuration import Configuration
from utils.schema_registry import get_schema_for_memory_type, get_schema_name
from utils.formatting import Spy, extract_tool_info

# Import the custom LLM wrapper
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from safe_llm import LLM_chat


# Trustcall instruction template
TRUSTCALL_INSTRUCTION = """Reflect on the following interaction. 

Use the provided tools to retain any necessary memories about the user.

Use parallel tool calling to handle updates and insertions simultaneously.

System Time: {time}"""


def memory_update(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """
    Update memories based on conversation context.
    
    This node:
    1. Identifies which memory types need updating
    2. Uses Trustcall to extract structured data
    3. Saves updates to the store
    4. Returns a tool message confirming the update
    
    Args:
        state: Current conversation state
        config: Configuration with assistant type and user info
        store: Memory store for persistence
        
    Returns:
        Updated state with tool response message
    """
    
    # Extract configuration
    configurable = Configuration.from_runnable_config(config)
    user_id = configurable.user_id
    assistant_type = configurable.assistant_type
    category = configurable.category
    enabled_memory_types = configurable.enabled_memory_types
    
    # Track what we've updated to avoid duplicates
    updated_types = set()
    
    # Always update profile if enabled (but only once)
    if "profile" in enabled_memory_types and "profile" not in updated_types:
        _update_memory_type(
            state=state,
            store=store,
            memory_type="profile",
            assistant_type=assistant_type,
            user_id=user_id,
            enable_inserts=False  # Profile is typically patch-only
        )
        updated_types.add("profile")
    
    # Find the most recent AI message with tool calls to determine intent
    route_intent_message = None
    for msg in reversed(state["messages"]):
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            # Check if it's a RouteIntent call
            for tc in msg.tool_calls:
                if tc.get("name") == "RouteIntent":
                    route_intent_message = msg
                    break
        if route_intent_message:
            break
    
    # If we found a RouteIntent, determine what memories to update
    if route_intent_message:
        tool_call = route_intent_message.tool_calls[0]
        
        # If it's a RouteIntent, extract the intent
        if tool_call.get("name") == "RouteIntent":
            intent = tool_call.get("args", {}).get("intent", "other")
            
            # Map intent to memory types that might need updating
            memory_updates_needed = _get_memory_types_for_intent(intent, enabled_memory_types)
            
            for memory_type in memory_updates_needed:
                # Only update if we haven't already
                if memory_type not in updated_types:
                    _update_memory_type(
                        state=state,
                        store=store,
                        memory_type=memory_type,
                        assistant_type=assistant_type,
                        user_id=user_id,
                        enable_inserts=True
                    )
                    updated_types.add(memory_type)
    
    # Return empty state update (memories are saved in store, not state)
    return {"messages": []}


def _update_memory_type(
    state: MessagesState,
    store: BaseStore,
    memory_type: str,
    assistant_type: str,
    user_id: str,
    enable_inserts: bool = True
):
    """
    Update a specific memory type using Trustcall (with fallback).
    
    Args:
        state: Current conversation state
        store: Memory store
        memory_type: Type of memory to update
        assistant_type: Assistant type
        user_id: User identifier
        enable_inserts: Whether to allow new memory creation
    """
    
    # Get the schema for this memory type
    schema = get_schema_for_memory_type(assistant_type, memory_type)
    if not schema:
        return
    
    schema_name = get_schema_name(schema)
    
    # Define namespace
    namespace = (memory_type, assistant_type, user_id)
    
    # Retrieve existing memories
    existing_items = store.search(namespace)
    existing_memories = (
        [(item.key, schema_name, item.value) for item in existing_items]
        if existing_items
        else None
    )
    
    # Format instruction
    instruction = TRUSTCALL_INSTRUCTION.format(time=datetime.now().isoformat())
    
    # Merge messages
    updated_messages = list(
        merge_message_runs(
            messages=[SystemMessage(content=instruction)] + state["messages"][:-1]
        )
    )
    
    # Try Trustcall first, fall back to direct extraction if it fails
    try:
        # Create spy for tracking
        spy = Spy()
        
        # Create extractor
        extractor = create_extractor(
            LLM_chat,
            tools=[schema],
            tool_choice=schema_name,
            enable_inserts=enable_inserts
        )
        
        # Try to add listener (optional)
        try:
            extractor = extractor.with_listeners(on_end=spy)
        except:
            pass  # Listeners are optional
        
        # Invoke extractor
        result = extractor.invoke({
            "messages": updated_messages,
            "existing": existing_memories
        })
        
        # Save memories to store
        for r, rmeta in zip(result["responses"], result["response_metadata"]):
            store.put(
                namespace,
                rmeta.get("json_doc_id", str(uuid.uuid4())),
                r.model_dump(mode="json")
            )
            
    except Exception as e:
        # Trustcall failed, use direct extraction as fallback
        error_msg = str(e)
        print(f"⚠️  Trustcall error for {memory_type}, using direct extraction: {error_msg[:100]}")
        
        try:
            _direct_extraction_fallback(
                state, store, schema, schema_name, namespace, updated_messages, enable_inserts
            )
        except Exception as fallback_error:
            print(f"⚠️  Direct extraction also failed for {memory_type}: {fallback_error}")


def _direct_extraction_fallback(
    state: MessagesState,
    store: BaseStore,
    schema,
    schema_name: str,
    namespace: tuple,
    messages: list,
    enable_inserts: bool
):
    """
    Fallback method that uses the LLM directly to extract structured data.
    
    This is used when Trustcall has compatibility issues.
    """
    # Create a model bound with the schema as a tool
    model = LLM_chat.bind_tools([schema], tool_choice=schema_name)
    
    # Add extraction prompt
    extraction_prompt = f"""Extract {schema_name} information from the conversation.
    
Call the {schema_name} tool with the relevant information from the user's messages.
    
Be thorough and capture all relevant details."""
    
    extraction_messages = messages + [SystemMessage(content=extraction_prompt)]
    
    # Invoke the model
    response = model.invoke(extraction_messages)
    
    # Check if we got tool calls
    if response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call.get("name") == schema_name:
                # Create an instance of the schema
                data = tool_call.get("args", {})
                
                # Validate with Pydantic
                try:
                    validated = schema(**data)
                    
                    # Save to store
                    store.put(
                        namespace,
                        str(uuid.uuid4()),
                        validated.model_dump(mode="json")
                    )
                    print(f"✅ Successfully extracted {schema_name} via direct method")
                    
                except Exception as validation_error:
                    print(f"⚠️  Validation error: {validation_error}")


def _get_memory_types_for_intent(intent: str, enabled_memory_types: list[str]) -> list[str]:
    """
    Determine which memory types should be updated for a given intent.
    
    Args:
        intent: Intent name from router
        enabled_memory_types: List of enabled memory types
        
    Returns:
        List of memory types to update
    """
    
    # Mapping of intents to memory types
    intent_memory_map = {
        "add_transaction": ["finance_transactions"],
        "update_transaction": ["finance_transactions"],
        "set_budget": ["finance_budgets"],
        "create_goal": ["finance_goals"],
        "add_recurring_payment": ["finance_recurring_payments"],
        "debt_payoff_plan": ["finance_debt_plans"],  # NEW: Store calculated plans
    }
    
    # Get memory types for this intent
    memory_types = intent_memory_map.get(intent, [])
    
    # Filter to only enabled types
    return [mt for mt in memory_types if mt in enabled_memory_types]