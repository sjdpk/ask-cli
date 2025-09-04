#!/usr/bin/env python3
"""Command handlers for ask CLI"""

import sys
import subprocess
import os
import shutil
import tempfile
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
  --update        Update ask CLI to the latest version
"""


def handle_help():
    """Display help information"""
    print(HELP_TEXT)
    sys.exit(0)


def handle_reset():
    """Reset API key configuration"""
    reset_config()
    sys.exit(0)


def handle_update():
    """Update ask CLI to the latest version"""
    print("🔄 Updating ask CLI...")
    
    # Check if git is available
    if not shutil.which('git'):
        print("❌ Git is required for updating. Please install git and try again.")
        sys.exit(1)
    
    # Get the installation directory (where the current script is located)
    install_dir = os.path.expanduser("~/.local/bin/ask-src")
    
    if not os.path.exists(install_dir):
        print("❌ Installation directory not found. Please reinstall using the install script.")
        sys.exit(1)
    
    try:
        # Create a temporary directory for the update
        with tempfile.TemporaryDirectory() as temp_dir:
            print("📥 Downloading latest version...")
            
            # Clone the latest version to temp directory
            result = subprocess.run([
                'git', 'clone', 'https://github.com/sjdpk/ask-cli.git', temp_dir
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("❌ Failed to download latest version from GitHub")
                print(f"Error: {result.stderr}")
                sys.exit(1)
            
            # Check if src directory exists in the downloaded version
            new_src_dir = os.path.join(temp_dir, 'src')
            if not os.path.exists(new_src_dir):
                print("❌ Invalid repository structure")
                sys.exit(1)
            
            print("📂 Backing up current installation...")
            
            # Create backup of current installation
            backup_dir = install_dir + '.backup'
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            shutil.copytree(install_dir, backup_dir)
            
            print("📦 Installing updated version...")
            
            # Remove current installation
            shutil.rmtree(install_dir)
            
            # Copy new version
            shutil.copytree(new_src_dir, install_dir)
            
            # Copy the main ask script
            new_ask_script = os.path.join(temp_dir, 'ask')
            ask_script_path = os.path.expanduser("~/.local/bin/ask")
            
            if os.path.exists(new_ask_script):
                shutil.copy2(new_ask_script, ask_script_path)
                os.chmod(ask_script_path, 0o755)
            
            # Remove backup if update was successful
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            
            print("✅ Ask CLI updated successfully!")
            print("🎉 You're now running the latest version.")
            
    except Exception as e:
        print(f"❌ Update failed: {e}")
        
        # Restore backup if it exists
        backup_dir = install_dir + '.backup'
        if os.path.exists(backup_dir):
            print("🔄 Restoring previous version...")
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir)
            shutil.move(backup_dir, install_dir)
            print("✅ Previous version restored.")
        
        sys.exit(1)
    
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
