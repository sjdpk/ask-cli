#!/usr/bin/env python3
"""
Argument parsing module for ask CLI

This module provides a centralized argument parser that handles all command-line
flags and options in a systematic way, improving maintainability and error handling.
"""

import argparse
import sys
from typing import Tuple, List


class AskArgumentParser:
    """
    Custom argument parser for the ask CLI tool.
    
    Handles all command-line arguments including flags, options, and queries
    with proper validation and error handling.
    """
    
    def __init__(self):
        """Initialize the argument parser with all supported options."""
        self.parser = argparse.ArgumentParser(
            prog='ask',
            description='Generate terminal commands from natural language',
            add_help=False,  # We'll handle help manually for consistency
            allow_abbrev=False  # Prevent ambiguous abbreviations
        )
        self._setup_arguments()
    
    def _setup_arguments(self):
        """
        Configure all command-line arguments and options.
        
        Sets up the argument parser with all supported flags, options,
        and positional arguments for the ask CLI tool.
        """
        # Help and version flags
        self.parser.add_argument(
            '-h', '--help',
            action='store_true',
            help='Show help information and exit'
        )
        
        # Configuration management
        self.parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset API key configuration'
        )
        
        self.parser.add_argument(
            '--update',
            action='store_true',
            help='Update ask CLI to the latest version'
        )
        
        # Execution control flags
        self.parser.add_argument(
            '-e', '--execute',
            action='store_true',
            help='Execute the generated command with confirmation'
        )
        
        self.parser.add_argument(
            '-f', '--force',
            action='store_true',
            help='Force execution without confirmation (requires --execute)'
        )
        
        # Interactive mode flags
        self.parser.add_argument(
            '-i', '--interactive',
            action='store_true',
            help='Enable interactive mode for follow-up queries'
        )
        
        self.parser.add_argument(
            '--context-limit',
            type=int,
            default=5,
            metavar='N',
            help='Set max number of previous queries to remember (default: 5)'
        )
        
        # Query (remaining arguments)
        self.parser.add_argument(
            'query',
            nargs='*',
            help='Natural language description of what you want to do'
        )
    
    def parse_arguments(self, args: List[str] = None) -> Tuple[argparse.Namespace, List[str]]:
        """
        Parse command-line arguments with comprehensive validation.
        
        Args:
            args: List of arguments to parse (defaults to sys.argv[1:])
            
        Returns:
            Tuple containing:
            - Parsed arguments namespace
            - List of validation errors (empty if no errors)
            
        Raises:
            SystemExit: If parsing fails or help is requested
        """
        if args is None:
            args = sys.argv[1:]
        
        try:
            parsed_args = self.parser.parse_args(args)
            validation_errors = self._validate_arguments(parsed_args)
            return parsed_args, validation_errors
            
        except argparse.ArgumentError as e:
            return None, [f"Argument error: {str(e)}"]
        except SystemExit as e:
            # argparse calls sys.exit on error or help
            if e.code == 0:
                # Help was requested
                raise
            else:
                # Parse error occurred
                return None, ["Invalid command-line arguments"]
    
    def _validate_arguments(self, args: argparse.Namespace) -> List[str]:
        """
        Validate parsed arguments for logical consistency.
        
        Args:
            args: Parsed arguments namespace
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Force flag requires execute flag
        if args.force and not args.execute:
            errors.append("--force flag requires --execute flag")
        
        # Context limit validation
        if args.context_limit < 1 or args.context_limit > 20:
            errors.append("--context-limit must be between 1 and 20")
        
        # Interactive mode validations
        if args.interactive and args.force:
            errors.append("--interactive mode cannot be used with --force flag")
        
        # Special commands shouldn't have queries or interactive mode
        special_commands = [args.help, args.reset, args.update]
        if any(special_commands) and args.query:
            errors.append("Special commands (--help, --reset, --update) cannot be combined with queries")
        
        if any(special_commands) and args.interactive:
            errors.append("Special commands cannot be used with --interactive mode")
        
        # Multiple special commands
        if sum(bool(cmd) for cmd in special_commands) > 1:
            errors.append("Only one special command can be used at a time")
        
        # Query required for normal operation (but handle empty args gracefully)
        if not any(special_commands) and not args.query:
            # If no arguments provided at all, this should be handled as a usage case
            # rather than an error - let the main function handle this gracefully
            pass
        
        return errors
    
    def get_usage_message(self) -> str:
        """
        Get formatted usage message for the CLI.
        
        Returns:
            Formatted usage string with examples
        """
        return """Usage: ask <what you want to do>
       ask --execute <what you want to do>
       ask --interactive <what you want to do>
       ask --help

Examples:
  ask list all files                    → Generate: ls -la
  ask --execute check disk              → Generate and run: df -h
  ask --interactive find large files    → Start interactive session
  ask -i --context-limit 3 list files  → Interactive with 3-query limit

Try: ask --help for more information"""


def parse_cli_arguments() -> Tuple[argparse.Namespace, List[str]]:
    """
    Convenience function to parse CLI arguments.
    
    Returns:
        Tuple containing parsed arguments and any validation errors
    """
    parser = AskArgumentParser()
    return parser.parse_arguments()
