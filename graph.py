"""
Universal LangGraph Framework - Graph Definition.

This module defines the universal graph structure that supports
multiple assistant domains through configuration.

Graph Flow:
START → main_assistant → router → executor → memory_update → main_assistant → END
"""

from typing import Literal

from langgraph.graph import StateGraph, MessagesState, START, END

from configuration import Configuration
from nodes.main_assistant import main_assistant
from nodes.router import router, route_to_executor
from nodes.memory_update import memory_update

# Import all executor nodes
from nodes.executors.finance_add_transaction import finance_add_transaction_executor
from nodes.executors.finance_summary import finance_summary_executor
from nodes.executors.finance_budget import finance_budget_executor
from nodes.executors.finance_goal import finance_goal_executor
from nodes.executors.finance_recurring import finance_recurring_executor
from nodes.executors.finance_advice import finance_advice_executor
from nodes.executors.finance_debt_payoff import finance_debt_payoff_executor


def create_graph(with_persistence=False):
    """
    Create and compile the universal LangGraph.
    
    This graph is domain-agnostic and routes to appropriate
    executors based on configuration and intent.
    
    Args:
        with_persistence: If True, adds MemorySaver and InMemoryStore.
                         Set to False for LangGraph Studio (default).
    
    Returns:
        Compiled graph ready for execution
    """
    
    # Initialize the state graph with configuration schema
    builder = StateGraph(
        MessagesState,
        config_schema=Configuration
    )
    
    # ========================================================================
    # Add Core Nodes (Universal)
    # ========================================================================
    
    builder.add_node("main_assistant", main_assistant)
    builder.add_node("router", router)
    builder.add_node("memory_update", memory_update)
    
    # ========================================================================
    # Add Executor Nodes (Domain-Specific)
    # ========================================================================
    
    # Finance executors
    builder.add_node("finance_add_transaction_executor", finance_add_transaction_executor)
    builder.add_node("finance_summary_executor", finance_summary_executor)
    builder.add_node("finance_budget_executor", finance_budget_executor)
    builder.add_node("finance_goal_executor", finance_goal_executor)
    builder.add_node("finance_recurring_executor", finance_recurring_executor)
    builder.add_node("finance_advice_executor", finance_advice_executor)
    builder.add_node("finance_debt_payoff_executor", finance_debt_payoff_executor)
    
    # TODO: Add more executor nodes for other domains (todo, legal, study, etc.)
    
    # ========================================================================
    # Define Graph Flow
    # ========================================================================
    
    # Entry point
    builder.add_edge(START, "main_assistant")
    
    # Main assistant has conditional edges (to router or END)
    # This is defined later with should_continue function
    
    # Router conditionally routes to executors or memory_update using route_to_executor
    builder.add_conditional_edges(
        "router",
        route_to_executor,
        {
            # Finance executors
            "finance_add_transaction_executor": "finance_add_transaction_executor",
            "finance_summary_executor": "finance_summary_executor",
            "finance_budget_executor": "finance_budget_executor",
            "finance_goal_executor": "finance_goal_executor",
            "finance_recurring_executor": "finance_recurring_executor",
            "finance_advice_executor": "finance_advice_executor",
            "finance_debt_payoff_executor": "finance_debt_payoff_executor",
            
            # Default paths
            "memory_update": "memory_update",
            "main_assistant": "main_assistant"
        }
    )
    
    # All executors flow to memory_update
    builder.add_edge("finance_add_transaction_executor", "memory_update")
    builder.add_edge("finance_summary_executor", "memory_update")
    builder.add_edge("finance_budget_executor", "memory_update")
    builder.add_edge("finance_goal_executor", "memory_update")
    builder.add_edge("finance_recurring_executor", "memory_update")
    builder.add_edge("finance_advice_executor", "memory_update")
    builder.add_edge("finance_debt_payoff_executor", "memory_update")
    
    # Memory update flows back to main assistant for final response
    builder.add_edge("memory_update", "main_assistant")
    
    # Define termination condition - END after main_assistant gives final response
    def should_continue(state: MessagesState) -> Literal["router", END]:
        """Determine if conversation should continue or end."""
        last_message = state["messages"][-1]
        
        # Check if last message is from assistant
        if hasattr(last_message, 'type') and last_message.type == "ai":
            # If it has tool calls, route them
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                # Check for RouteIntent tool calls
                has_route_intent = any(
                    tc.get("name") == "RouteIntent" 
                    for tc in last_message.tool_calls
                )
                
                if has_route_intent:
                    return "router"
            
            # No tool calls = final response, end conversation
            return END
        
        # Default to END if unsure (safety)
        return END
    
    # Add conditional edge from main_assistant
    builder.add_conditional_edges("main_assistant", should_continue)
    
    # Compile the graph
    # LangGraph Studio provides its own persistence
    # For standalone use, add checkpointer and store
    if with_persistence:
        from langgraph.checkpoint.memory import MemorySaver
        from langgraph.store.memory import InMemoryStore
        
        graph = builder.compile(
            checkpointer=MemorySaver(),
            store=InMemoryStore()
        )
    else:
        # No persistence - Studio will provide it
        graph = builder.compile()
    
    return graph


# Create the graph instance for LangGraph Studio (no persistence)
graph = create_graph(with_persistence=False)