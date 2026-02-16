

"""
Main assistant node - primary conversational interface.

This node handles the main conversation flow, loads memories,
and routes requests to appropriate executors via the router.
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.store.base import BaseStore

from configuration import Configuration
from utils.store_utils import get_memory, format_memories, get_all_memories_by_type


# Import the custom LLM wrapper
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from safe_llm import LLM_chat


class RouteIntent(BaseModel):
    """
    Tool for routing user requests to appropriate executors.
    
    Use this tool to classify the user's request and route it to the correct handler.
    
    CRITICAL INTENT DEFINITIONS:
    
    - debt_payoff_plan: ANY request for calculated payment schedules, month-by-month breakdowns,
                        interest calculations, loan amortization, "how long to pay off", or
                        multi-month financial projections. Keywords: "debt", "payoff", "plan",
                        "schedule", "month-by-month", "interest calculation"
    
    - add_transaction: User reports a purchase, expense, or income
    
    - monthly_summary: User wants spending/income report
    
    - set_budget: User sets spending limits
    
    - create_goal: User creates savings goal
    
    - add_recurring_payment: User tracks subscription/repeating payment
    
    - advice: User asks for financial recommendations
    
    - other: General conversation
    
    IMPORTANT: If user mentions creating a "plan" or "schedule" with numbers and time periods,
    choose "debt_payoff_plan" NOT "other".
    """
    
    intent: str = Field(
        description="""The intent category for this request. Choose from:
        - debt_payoff_plan: For payment schedules, debt calculations, month-by-month plans
        - add_transaction: For reporting expenses/income
        - monthly_summary: For spending reports
        - set_budget: For setting spending limits
        - create_goal: For savings goals
        - add_recurring_payment: For subscriptions
        - advice: For financial recommendations
        - other: For general conversation"""
    )
    reasoning: str = Field(
        description="Brief explanation of why this intent was chosen. If choosing 'other' for a debt/plan request, explain why it's not 'debt_payoff_plan'."
    )


def main_assistant(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """
    Main conversational assistant node.
    
    Responsibilities:
    - Load relevant memories from store
    - Present memories in system prompt
    - Route requests via RouteIntent tool (first pass only)
    - Provide conversational responses
    
    Args:
        state: Current conversation state with messages
        config: Configuration containing assistant type and user info
        store: Memory store for persistence
        
    Returns:
        Updated state with assistant response
    """
    
    # Find the last HumanMessage to determine current turn
    last_human_idx = -1
    for i in range(len(state["messages"]) - 1, -1, -1):
        msg = state["messages"][i]
        if hasattr(msg, 'type') and msg.type == "human":
            last_human_idx = i
            break
    
    # Count how many AI messages with RouteIntent since last human message
    route_count_this_turn = 0
    if last_human_idx >= 0:
        for msg in state["messages"][last_human_idx:]:
            if hasattr(msg, 'type') and msg.type == "ai":
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    if any(tc.get("name") == "RouteIntent" for tc in msg.tool_calls):
                        route_count_this_turn += 1
    
    # Should route only on first pass (when route_count_this_turn == 0)
    should_route = route_count_this_turn == 0
    
    # Extract configuration
    configurable = Configuration.from_runnable_config(config)
    user_id = configurable.user_id
    assistant_type = configurable.assistant_type
    category = configurable.category
    role_prompt = configurable.role_prompt
    enabled_memory_types = configurable.enabled_memory_types
    router_intents = configurable.router_intents
    
    # Load memories for each enabled type
    memory_content_parts = []
    memory_descriptions = []
    
    for memory_type in enabled_memory_types:
        memories = get_all_memories_by_type(store, memory_type, assistant_type, user_id)
        
        if memory_type == "profile":
            memory_descriptions.append("- User Profile (general information about the user)")
            if memories:
                memory_content_parts.append(
                    f"<user_profile>\n{memories[0].value}\n</user_profile>"
                )
            else:
                memory_content_parts.append(
                    "<user_profile>\nNo profile information yet.\n</user_profile>"
                )
        
        elif memory_type.startswith("finance_"):
            display_name = memory_type.replace("finance_", "").replace("_", " ").title()
            memory_descriptions.append(f"- {display_name}")
            
            if memories:
                formatted = format_memories(memories)
                memory_content_parts.append(
                    f"<{memory_type}>\n{formatted}\n</{memory_type}>"
                )
            else:
                memory_content_parts.append(
                    f"<{memory_type}>\nNo {display_name.lower()} recorded yet.\n</{memory_type}>"
                )
    
    # Load system prompt template
    try:
        with open("prompts/universal_system_prompt.txt", "r") as f:
            system_prompt_template = f.read()
    except FileNotFoundError:
        # Fallback if file not found
        system_prompt_template = "{role_prompt}\n\n{memory_content}\n\nAvailable intents: {available_intents}"
    
    # Format system prompt
    if should_route:
        # First pass - include routing instructions
        system_msg = system_prompt_template.format(
            role_prompt=role_prompt,
            memory_descriptions="\n".join(memory_descriptions),
            memory_content="\n\n".join(memory_content_parts),
            available_intents=", ".join(router_intents),
            current_time=datetime.now().isoformat()
        )
    else:
        # Second pass - after action completed, provide confirmation response
        system_msg = f"""{role_prompt}

The user's request has been processed successfully.

CRITICAL: You will receive a JSON response from the system with calculated results.

YOUR JOB (formatting only - NO calculations):
1. Parse the JSON to understand what was calculated
2. Present the results in a clear, friendly way
3. Use markdown tables if appropriate
4. Explain what the numbers mean

⚠️ NEVER RECALCULATE ANY NUMBERS
⚠️ NEVER MODIFY THE JSON VALUES
⚠️ ONLY FORMAT AND EXPLAIN

If the JSON contains a debt payoff plan:
- Show the key results (debt cleared?, months needed, total interest)
- Display the month-by-month table
- Explain what it means for the user
- Offer to help with adjustments

DO NOT:
- Recalculate interest
- Change any balances
- Create your own tables
- "Fix" numbers you think are wrong

The calculations are done by Python and are 100% accurate.
Your role is PRESENTATION ONLY.

Current Date/Time: {datetime.now().isoformat()}"""
    
    # Create model - only bind RouteIntent tool if we should route
    if should_route:
        model = LLM_chat.bind_tools([RouteIntent], parallel_tool_calls=False)
    else:
        # Don't bind tools - just respond conversationally
        # Create a fresh instance without any tool bindings
        from safe_llm import SafeLLM
        model = SafeLLM(temperature=0)  # Fresh instance, no tools
    
    # Generate response
    response = model.invoke([SystemMessage(content=system_msg)] + state["messages"])
    
    # Ensure response has content
    if not response.content or len(response.content.strip()) == 0:
        # Fallback response if model returns empty
        response.content = "I've processed your request. How else can I help you with your finances?"
    
    return {"messages": [response]}