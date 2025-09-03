#!/usr/bin/env python3
"""Command handlers for ask CLI"""

import sys
import subprocess
import os
from config import load_api_key, setup_api_key, reset_config
from ai import CommandGenerator
from ui import SpinnerContext

# Help text
HELP_TEXT = """
ask - instant terminal commands

Usage:
  ask <what you want to do>
  ask --execute <what you want to do>
  ask --execute --force <what you want to do>

Examples:
  ask list all files           → ls -la
  ask check disk space         → df -h
  ask find text in files       → grep -r "text" .
  ask kill port 3000          → lsof -ti:3000 | xargs kill -9
  ask compress folder         → tar -czf archive.tar.gz .

Options:
  -e, --execute   Execute the generated command (with confirmation)
  -f, --force     Force execution without confirmation (must be used with -e)
  --help          Show this help
  --reset         Reset API key
"""


def handle_help():
    """Display help information"""
    print(HELP_TEXT)
    sys.exit(0)


def handle_reset():
    """Reset API key configuration"""
    reset_config()
    sys.exit(0)


def get_user_confirmation(command):
    """Ask user for confirmation before executing a command"""
    print(f"\n💡 Generated command: {command}")
    while True:
        response = input("Do you want to execute this command? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no.")


def execute_command(command):
    """Execute a shell command after confirmation"""
    print(f"Executing: {command}")
    try:
        # Capture output and display it live
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        for line in process.stdout:
            print(line, end='')

        process.wait()

        if process.returncode == 0:
            print("\n✅ Command executed successfully.")
        else:
            print(f"\n⚠️ Command failed with exit code {process.returncode}.")

    except Exception as e:
        print(f"❌ Error executing command: {e}")


def handle_query(query, execute=False, force=False):
    """Process user query and generate command"""
    # Get API key (setup if needed)
    api_key = load_api_key()
    if not api_key:
        api_key = setup_api_key()

    # Generate command with spinner
    generator = CommandGenerator(api_key)
    with SpinnerContext():
        result = generator.get_command(query)

    # Find the line with the command
    command_to_execute = ""
    for line in result.split('\n'):
        if line.startswith("→"):
            command_to_execute = line.replace("→ ", "").strip()
            break

    if execute:
        if command_to_execute:
            # If force flag is not set, ask for confirmation
            if not force:
                if get_user_confirmation(command_to_execute):
                    execute_command(command_to_execute)
                else:
                    print("❌ Command execution cancelled.")
            else:
                # Force execution without confirmation
                execute_command(command_to_execute)
        else:
            print("🤔 No command generated to execute.")
    else:
        print(result)
