"""
Utility functions for memory store operations.

Provides helpers for loading, saving, and formatting memories
from the LangGraph store.
"""

from typing import Optional, Any
from langgraph.store.base import BaseStore


def get_memory(
    store: BaseStore,
    memory_type: str,
    assistant_type: str,
    user_id: str,
    key: Optional[str] = None
) -> Optional[Any]:
    """
    Retrieve a memory from the store.
    
    Args:
        store: LangGraph BaseStore instance
        memory_type: Type of memory (e.g., 'profile', 'finance_transactions')
        assistant_type: Assistant type (e.g., 'finance', 'todo')
        user_id: User identifier
        key: Optional specific key to retrieve. If None, searches all.
        
    Returns:
        Memory value or None if not found
    """
    namespace = (memory_type, assistant_type, user_id)
    
    if key:
        # Get specific memory by key
        memory = store.get(namespace, key)
        return memory.value if memory else None
    else:
        # Search for all memories in namespace
        memories = store.search(namespace)
        if memories:
            return memories[0].value
        return None


def save_memory(
    store: BaseStore,
    memory_type: str,
    assistant_type: str,
    user_id: str,
    key: str,
    value: dict
) -> None:
    """
    Save a memory to the store.
    
    Args:
        store: LangGraph BaseStore instance
        memory_type: Type of memory
        assistant_type: Assistant type
        user_id: User identifier
        key: Memory key
        value: Memory value (dictionary)
    """
    namespace = (memory_type, assistant_type, user_id)
    store.put(namespace, key, value)


def format_memories(memories: list, separator: str = "\n\n") -> str:
    """
    Format a list of memories into a readable string.
    
    Args:
        memories: List of memory items from store
        separator: String to separate individual memories
        
    Returns:
        Formatted string representation
    """
    if not memories:
        return ""
    
    return separator.join(str(mem.value) for mem in memories)


def get_all_memories_by_type(
    store: BaseStore,
    memory_type: str,
    assistant_type: str,
    user_id: str
) -> list:
    """
    Get all memories of a specific type for a user.
    
    Args:
        store: LangGraph BaseStore instance
        memory_type: Type of memory to retrieve
        assistant_type: Assistant type
        user_id: User identifier
        
    Returns:
        List of memory items
    """
    namespace = (memory_type, assistant_type, user_id)
    return store.search(namespace)
