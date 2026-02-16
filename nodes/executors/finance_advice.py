"""
Finance Advice Executor.

Provides financial advice and insights based on user data.
"""

from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState
from langgraph.store.base import BaseStore

from configuration import Configuration
from utils.store_utils import get_all_memories_by_type

# Import the custom LLM wrapper
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from safe_llm import LLM_chat


def finance_advice_executor(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """
    Generate financial advice based on user's financial data.
    
    Analyzes transactions, budgets, and goals to provide
    personalized financial insights and recommendations.
    
    Args:
        state: Current conversation state
        config: Configuration
        store: Memory store
        
    Returns:
        Tool response with advice
    """
    
    # Get configuration
    configurable = Configuration.from_runnable_config(config)
    user_id = configurable.user_id
    assistant_type = configurable.assistant_type
    
    # Gather all financial data
    transactions = get_all_memories_by_type(store, "finance_transactions", assistant_type, user_id)
    budgets = get_all_memories_by_type(store, "finance_budgets", assistant_type, user_id)
    goals = get_all_memories_by_type(store, "finance_goals", assistant_type, user_id)
    recurring = get_all_memories_by_type(store, "finance_recurring_payments", assistant_type, user_id)
    
    # Build context for advice
    context_parts = []
    
    if transactions:
        context_parts.append(f"Transactions: {len(transactions)} recorded")
    if budgets:
        context_parts.append(f"Budgets: {[b.value for b in budgets]}")
    if goals:
        context_parts.append(f"Goals: {[g.value for g in goals]}")
    if recurring:
        context_parts.append(f"Recurring Payments: {[r.value for r in recurring]}")
    
    context = "\n".join(context_parts) if context_parts else "No financial data available yet."
    
    # Create advice prompt
    advice_prompt = f"""Based on the user's financial data below, provide helpful, actionable financial advice.

Financial Data:
{context}

User's Question/Request: {state['messages'][-2].content if len(state['messages']) > 1 else 'General advice'}

Provide:
1. Key insights about their financial situation
2. Specific recommendations
3. Any areas of concern or opportunity
4. Next steps they should consider

Be supportive, practical, and specific."""
    
    # Generate advice using LLM
    advice_response = LLM_chat.invoke([SystemMessage(content=advice_prompt)])
    
    # Get the last message with the tool call
    last_message = state["messages"][-1]
    
    if last_message.tool_calls:
        tool_call_id = last_message.tool_calls[0].get("id")
        
        # Return advice as tool response
        return {
            "messages": [{
                "role": "tool",
                "content": advice_response.content,
                "tool_call_id": tool_call_id
            }]
        }
    
    return {"messages": []}
