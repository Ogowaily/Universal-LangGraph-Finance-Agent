"""
Agent module for LangGraph Studio.

This module exports the compiled graph for use with LangGraph Studio/Dev server.
"""

from graph import graph

# Export the compiled graph
__all__ = ["graph"]