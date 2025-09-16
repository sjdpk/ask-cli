#!/usr/bin/env python3
"""
Interactive session handler for ask CLI

This module provides the interactive session functionality that allows users
to have follow-up conversations with the AI for refining and building upon commands.
"""

import sys
from typing import Optional, NoReturn

# Import local modules
from context_manager import ConversationContext
from config import load_api_key, setup_api_key
from ai import CommandGenerator
from ui import SpinnerContext
from commands import get_user_confirmation, execute_command, validate_command_safety
from constants import INTERACTIVE_COMMANDS, ERROR_MESSAGES


class InteractiveSession:
    """
    Manages an interactive conversation session with context and follow-up queries.
    
    Provides a conversational interface where users can ask follow-up questions,
    refine commands, and build upon previous interactions within a single session.
    """
    
    def __init__(self, context_limit: int = 5, execute_mode: bool = False):
        """
        Initialize the interactive session.
        
        Args:
            context_limit: Maximum number of queries to remember
            execute_mode: Whether to execute commands by default
        """
        self.context = ConversationContext(context_limit)
        self.execute_mode = execute_mode
        self.generator: Optional[CommandGenerator] = None
        self.running = True
    
    def _setup_ai_generator(self) -> bool:
        """
        Set up the AI command generator with API key.
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            # Get API key (setup if needed)
            api_key = load_api_key()
            if not api_key:
                api_key = setup_api_key()
            
            # Initialize command generator
            self.generator = CommandGenerator(api_key)
            return True
            
        except KeyboardInterrupt:
            print("\n\n👋 Setup cancelled by user.")
            return False
        except Exception as e:
            print(f"➜ Error setting up AI service: {str(e)}")
            print("   Try running 'ask --reset' to update your API key.")
            return False
    
    def _show_interactive_help(self) -> None:
        """Display help information for interactive mode."""
        print("\nCommands:")
        for cmd, desc in INTERACTIVE_COMMANDS.items():
            print(f"  {cmd} - {desc}")
    
    def _handle_session_command(self, user_input: str) -> bool:
        """
        Handle special interactive session commands.
        
        Args:
            user_input: Raw user input to check for commands
            
        Returns:
            True if a session command was handled, False otherwise
        """
        command = user_input.strip().lower()
        
        if command in ['/exit', '/quit']:
            self.running = False
            return True
        
        elif command == '/clear':
            self.context.clear_context()
            print("Context cleared.")
            return True
        
        elif command == '/history':
            print(self.context.get_history_display())
            return True
        
        elif command == '/help':
            self._show_interactive_help()
            return True
        
        elif command == '/last':
            last_query = self.context.get_last_query()
            if last_query:
                if last_query.executed:
                    print(f"Re-executing: {last_query.command}")
                    execute_command(last_query.command)
                    self.context.update_last_execution_status(True, True)  # Assume success for re-run
                else:
                    print(f"Last command was: {last_query.command}")
                    if self.execute_mode:
                        if get_user_confirmation(last_query.command, f"→ {last_query.command}"):
                            execute_command(last_query.command)
                            self.context.update_last_execution_status(True, True)
                    else:
                        print("Use --execute mode to run commands directly.")
            else:
                print("No previous commands in this session.")
            return True
        
        return False
    
    def _process_query(self, query: str) -> None:
        """
        Process a user query with context awareness.
        
        Args:
            query: User's natural language query
        """
        if not self.generator:
            print("➜ AI generator not initialized.")
            return
        
        try:
            # Generate command with context
            with SpinnerContext():
                if self.context.is_empty():
                    # First query - no context needed
                    result = self.generator.get_command(query)
                else:
                    # Follow-up query - include context
                    result = self.generator.get_command_with_context(query, self.context)
            
            # Check for error responses
            if result.startswith("➜"):
                print(result)
                return
            
            # Check if response looks like a valid command response
            if not result.startswith("→") and "→" not in result:
                print("➜ Out of context - this is not a terminal command request")
                return
            
            # Extract command
            command_to_execute = ""
            for line in result.split('\n'):
                if line.startswith("→"):
                    command_to_execute = line.replace("→ ", "").strip()
                    break
            
            if not command_to_execute:
                print("➜ No valid command found in response.")
                return
            
            # Display the result
            print(result)
            
            # Add to context (not executed yet)
            self.context.add_query(query, command_to_execute, executed=False)
            
            # Handle execution if in execute mode
            if self.execute_mode:
                try:
                    if get_user_confirmation(command_to_execute, result):
                        execute_command(command_to_execute)
                        self.context.update_last_execution_status(True, True)
                        print()  # Add spacing after execution
                    else:
                        print("Cancelled.")
                        print()
                except KeyboardInterrupt:
                    print("\nCancelled.")
                    print()
            
        except KeyboardInterrupt:
            print("\nCancelled.")
        except Exception as e:
            print(f"➜ Error processing query: {str(e)}")
    
    def _get_user_input(self) -> Optional[str]:
        """
        Get user input with interactive prompt.
        
        Returns:
            User input string or None if interrupted
        """
        try:
            # Simple prompt - no context summary or extra info
            prompt = "\nFollow-up: "
            return input(prompt).strip()
            
        except (KeyboardInterrupt, EOFError):
            print("\n")
            return None
    
    def start_session(self, initial_query: str = "") -> None:
        """
        Start the interactive session with optional initial query.
        
        Args:
            initial_query: Optional initial query to start the conversation
        """
        # Setup AI generator
        if not self._setup_ai_generator():
            return
        
        # Minimal startup - no verbose welcome messages
        
        # Process initial query if provided
        if initial_query.strip():
            self._process_query(initial_query)
        
        # Main interactive loop
        while self.running:
            user_input = self._get_user_input()
            
            if user_input is None:
                # Interrupted
                break
            
            if not user_input:
                # Empty input, continue
                continue
            
            # Handle session commands
            if self._handle_session_command(user_input):
                continue
            
            # Process as query
            self._process_query(user_input)
        
        # Clean exit - no verbose end messages


def start_interactive_session(args) -> NoReturn:
    """
    Start an interactive session based on parsed command-line arguments.
    
    Args:
        args: Parsed command-line arguments containing interactive settings
        
    Raises:
        SystemExit: Always exits after session completion
    """
    try:
        # Get initial query if provided
        initial_query = ' '.join(args.query) if args.query else ''
        
        # Create and start session
        session = InteractiveSession(
            context_limit=args.context_limit,
            execute_mode=args.execute
        )
        
        session.start_session(initial_query)
        
    except KeyboardInterrupt:
        print("")
    except Exception as e:
        print(f"➜ Error: {str(e)}")
    finally:
        sys.exit(0)
