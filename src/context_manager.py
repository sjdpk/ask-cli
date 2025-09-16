#!/usr/bin/env python3
"""
Memory-based context manager for interactive sessions

This module provides a simple, memory-based conversation context manager
that stores query history for interactive follow-up sessions with configurable limits.
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Import constants
from constants import DEFAULT_CONTEXT_LIMIT


@dataclass
class QueryContext:
    """
    Represents a single query and its context in the conversation.
    
    Stores all relevant information about a query including the original
    user input, generated command, execution status, and timing.
    """
    query: str
    command: str
    timestamp: str
    executed: bool = False
    execution_successful: bool = False
    
    def __post_init__(self):
        """Ensure timestamp is set if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the query context to a dictionary.
        
        Returns:
            Dictionary representation of the query context
        """
        return asdict(self)
    
    def get_summary(self) -> str:
        """
        Get a brief summary of this query context.
        
        Returns:
            Human-readable summary string
        """
        status = "✓" if self.executed and self.execution_successful else "○" if self.executed else "·"
        return f"{status} {self.query} → {self.command}"


class ConversationContext:
    """
    Memory-based conversation context manager with configurable limits.
    
    Maintains a rolling history of queries and responses for interactive
    sessions, automatically managing memory usage through size limits.
    """
    
    def __init__(self, context_limit: int = DEFAULT_CONTEXT_LIMIT):
        """
        Initialize the conversation context manager.
        
        Args:
            context_limit: Maximum number of query contexts to maintain
        """
        self.context_limit = max(1, min(context_limit, 20))  # Enforce reasonable bounds
        self.queries: List[QueryContext] = []
        self.session_start = datetime.now().isoformat()
    
    def add_query(self, query: str, command: str, executed: bool = False, 
                  execution_successful: bool = False) -> None:
        """
        Add a new query context to the conversation history.
        
        Automatically manages the context limit by removing oldest entries
        when the limit is exceeded.
        
        Args:
            query: Original user query
            command: Generated command
            executed: Whether the command was executed
            execution_successful: Whether execution was successful
        """
        context = QueryContext(
            query=query.strip(),
            command=command.strip(),
            timestamp=datetime.now().isoformat(),
            executed=executed,
            execution_successful=execution_successful
        )
        
        self.queries.append(context)
        
        # Maintain context limit by removing oldest entries
        while len(self.queries) > self.context_limit:
            self.queries.pop(0)
    
    def get_context_for_ai(self) -> str:
        """
        Get formatted context string for AI prompt inclusion.
        
        Formats the conversation history in a way that's useful for
        the AI to understand the context of follow-up queries.
        
        Returns:
            Formatted context string for AI prompt
        """
        if not self.queries:
            return ""
        
        context_lines = ["Previous conversation:"]
        for i, ctx in enumerate(self.queries, 1):
            status_indicator = "✓" if ctx.executed else "○"
            context_lines.append(f"{i}. User: {ctx.query}")
            context_lines.append(f"   Command: {ctx.command} {status_indicator}")
        
        context_lines.append("Current query:")
        return "\n".join(context_lines)
    
    def get_history_display(self) -> str:
        """
        Get formatted history for display to user.
        
        Creates a user-friendly display of the conversation history
        with execution status indicators.
        
        Returns:
            Formatted history string for display
        """
        if not self.queries:
            return "No history."
        
        history_lines = []
        
        for i, ctx in enumerate(self.queries, 1):
            history_lines.append(f"{i}. {ctx.query}")
            history_lines.append(f"   → {ctx.command}")
        
        return "\n".join(history_lines)
    
    def get_last_query(self) -> Optional[QueryContext]:
        """
        Get the most recent query context.
        
        Returns:
            Most recent QueryContext or None if no queries exist
        """
        return self.queries[-1] if self.queries else None
    
    def clear_context(self) -> None:
        """
        Clear all query history from the conversation context.
        
        Resets the conversation to a fresh state while maintaining
        the same context limit settings.
        """
        self.queries.clear()
        self.session_start = datetime.now().isoformat()
    
    def get_context_summary(self) -> str:
        """
        Get a brief summary of the current context state.
        
        Returns:
            Summary string with context statistics
        """
        query_count = len(self.queries)
        executed_count = sum(1 for q in self.queries if q.executed)
        
        return (f"📊 Context: {query_count}/{self.context_limit} queries, "
                f"{executed_count} executed")
    
    def is_empty(self) -> bool:
        """
        Check if the context is empty.
        
        Returns:
            True if no queries are stored, False otherwise
        """
        return len(self.queries) == 0
    
    def update_last_execution_status(self, executed: bool, successful: bool = False) -> bool:
        """
        Update the execution status of the most recent query.
        
        Args:
            executed: Whether the command was executed
            successful: Whether execution was successful
            
        Returns:
            True if update was successful, False if no queries exist
        """
        if not self.queries:
            return False
        
        self.queries[-1].executed = executed
        self.queries[-1].execution_successful = successful
        return True
