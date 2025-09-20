#!/usr/bin/env python3
"""
Main entry point for ask CLI

This module serves as the primary entry point for the ask CLI application,
handling argument parsing, command routing, and top-level error management.
"""

import sys
import os
import warnings
from typing import NoReturn

# Suppress Google AI warnings that appear in virtual environment
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '2'
warnings.filterwarnings('ignore', category=UserWarning, module='google')

# Import local modules
from argument_parser import parse_cli_arguments
from constants import ERROR_MESSAGES, INSTALL_SCRIPT_URL


def handle_argument_errors(errors: list) -> NoReturn:
    """
    Handle argument parsing and validation errors.
    
    Displays appropriate error messages for argument parsing failures
    and exits the application with proper error codes.
    
    Args:
        errors: List of error messages from argument validation
        
    Raises:
        SystemExit: Always exits with code 1 after displaying errors
    """
    print("➜ Error parsing command line arguments:")
    for error in errors:
        print(f"   {error}")
    
    from argument_parser import AskArgumentParser
    parser = AskArgumentParser()
    print(f"\n{parser.get_usage_message()}")
    sys.exit(1)


def route_command(args) -> None:
    """
    Route parsed arguments to appropriate command handlers.
    
    Determines which command handler to call based on the parsed
    arguments and delegates execution to the appropriate module.
    
    Args:
        args: Parsed command-line arguments namespace
        
    Raises:
        SystemExit: May exit based on command handler behavior
    """
    try:
        # Import command handlers
        from commands import handle_help, handle_reset, handle_update, handle_query
        
        # Route to appropriate handler
        if args.help:
            handle_help()
        elif args.reset:
            handle_reset()
        elif args.update:
            handle_update()
        elif args.interactive:
            # Handle interactive mode
            from interactive import start_interactive_session
            start_interactive_session(args)
        else:
            # Handle regular query
            query = ' '.join(args.query) if args.query else ''
            if not query.strip():
                # No query provided, show usage
                from argument_parser import AskArgumentParser
                parser = AskArgumentParser()
                print(parser.get_usage_message())
                sys.exit(1)
            handle_query(query, args.execute, args.force)
            
    except ImportError as e:
        print("➜ Failed to load required command modules.")
        print(f"   Error: {str(e)}")
        print(f"   Please ensure Ask CLI is properly installed.")
        print(f"   Reinstall using: {INSTALL_SCRIPT_URL}")
        sys.exit(1)


def main() -> None:
    """
    Main entry point with comprehensive exception handling.
    
    Coordinates the entire application flow from argument parsing
    through command execution, with robust error handling and
    user-friendly error messages.
    
    Raises:
        SystemExit: On various error conditions or successful completion
    """
    try:
        # Parse and validate command-line arguments
        args, validation_errors = parse_cli_arguments()
        
        # Handle argument parsing failures
        if args is None or validation_errors:
            handle_argument_errors(validation_errors or ["Unknown parsing error"])
        
        # Route to appropriate command handler
        route_command(args)
        
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user.")
        sys.exit(0)
    except SystemExit:
        # Allow normal sys.exit() calls to pass through
        raise
    except Exception as e:
        print(f"➜ Unexpected error in main application: {str(e)}")
        print("   Please report this issue on GitHub if it persists.")
        print(f"   GitHub Issues: {ERROR_MESSAGES.get('github_repo', 'https://github.com/sjdpk/ask-cli')}/issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
