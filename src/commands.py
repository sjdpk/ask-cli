#!/usr/bin/env python3
"""Command handlers for ask CLI"""

import sys
from config import load_api_key, setup_api_key, reset_config
from ai import CommandGenerator
from ui import SpinnerContext

# Help text
HELP_TEXT = """
ask - instant terminal commands

Usage:
  ask <what you want to do>

Examples:
  ask list all files           → ls -la
  ask check disk space         → df -h  
  ask find text in files       → grep -r "text" .
  ask kill port 3000          → lsof -ti:3000 | xargs kill -9
  ask compress folder         → tar -czf archive.tar.gz .

Options:
  ask --help      Show this help
  ask --reset     Reset API key
"""


def handle_help():
    """Display help information"""
    print(HELP_TEXT)
    sys.exit(0)


def handle_reset():
    """Reset API key configuration"""
    reset_config()
    sys.exit(0)


def handle_query(query):
    """Process user query and generate command"""
    # Get API key (setup if needed)
    api_key = load_api_key()
    if not api_key:
        api_key = setup_api_key()
    
    # Generate command with spinner
    generator = CommandGenerator(api_key)
    with SpinnerContext():
        result = generator.get_command(query)
    
    print(result)
