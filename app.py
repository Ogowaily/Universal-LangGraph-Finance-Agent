"""
Universal LangGraph Framework - Main Application.

This is the entry point for running the universal assistant framework.
"""

from langchain_core.messages import HumanMessage
from configuration import get_finance_config, get_todo_config
from graph import create_graph


# Create graph with persistence for standalone use
# (LangGraph Studio provides its own persistence automatically)
graph = create_graph(with_persistence=True)


def run_finance_assistant():
    """
    Run the Personal Finance Assistant.
    
    This function demonstrates how to use the universal framework
    with the finance configuration.
    """
    
    print("=" * 60)
    print("🏦 Personal Finance Assistant")
    print("=" * 60)
    print()
    
    # Get finance configuration
    config = get_finance_config(user_id="user_123")
    
    # Set thread ID for conversation history
    config["configurable"]["thread_id"] = "finance_thread_1"
    
    print("Assistant: Hi! I'm your Personal Finance Assistant.")
    print("I can help you track expenses, set budgets, create goals, and more.")
    print()
    
    # Example conversation
    test_messages = [
        "Hi, my name is Alex and I live in San Francisco. I work as a software engineer.",
        "I just spent $85 on groceries at Whole Foods using my credit card.",
        "Can you add another expense? I paid $15 for Netflix subscription.",
        "Set a monthly budget of $500 for groceries.",
        "I want to save $10,000 for a vacation by next December.",
        "Can you give me a summary of my spending this month?",
        "What's your advice on my finances so far?"
    ]
    
    for user_message in test_messages:
        print(f"You: {user_message}")
        print()
        
        # Invoke the graph
        result = graph.invoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=config
        )
        
        # Get the last assistant message
        last_message = result["messages"][-1]
        if hasattr(last_message, 'content'):
            print(f"Assistant: {last_message.content}")
        print()
        print("-" * 60)
        print()


def run_interactive_session(assistant_type="finance"):
    """
    Run an interactive chat session.
    
    Args:
        assistant_type: Type of assistant ('finance' or 'todo')
    """
    
    # Get configuration based on assistant type
    if assistant_type == "finance":
        config = get_finance_config(user_id="interactive_user")
        print("🏦 Starting Personal Finance Assistant")
    elif assistant_type == "todo":
        config = get_todo_config(user_id="interactive_user")
        print("✅ Starting ToDo Assistant")
    else:
        print(f"Unknown assistant type: {assistant_type}")
        return
    
    # Set thread ID
    config["configurable"]["thread_id"] = f"{assistant_type}_interactive"
    
    print("Type 'exit' to quit")
    print("=" * 60)
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            
            print()
            
            # Invoke the graph
            result = graph.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            
            # Get the last assistant message
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                print(f"Assistant: {last_message.content}")
            
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print()


def main():
    """
    Main entry point.
    
    Choose to run demo or interactive session.
    """
    
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     Universal LangGraph Framework                        ║")
    print("║     Config-Driven Multi-Domain AI Assistant              ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("Select mode:")
    print("1. Run Finance Demo (automated)")
    print("2. Interactive Finance Session")
    print("3. Interactive ToDo Session")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    print()
    
    if choice == "1":
        run_finance_assistant()
    elif choice == "2":
        run_interactive_session("finance")
    elif choice == "3":
        run_interactive_session("todo")
    else:
        print("Invalid choice. Running finance demo...")
        run_finance_assistant()


if __name__ == "__main__":
    main()