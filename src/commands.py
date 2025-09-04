#!/usr/bin/env python3
"""Command handlers for ask CLI"""

import sys
import subprocess
import os
import shutil
import tempfile
import time
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

Safety:
  Ask CLI automatically detects potentially dangerous commands and shows
  warnings before execution to help protect your system and data.
"""


def handle_help():
    """Display help information"""
    print(HELP_TEXT)
    sys.exit(0)


def handle_reset():
    """Reset API key configuration"""
    reset_config()
    sys.exit(0)


def show_update_spinner():
    """Show a dynamic spinner for update process with changing text"""
    import threading
    
    class UpdateSpinner:
        def __init__(self):
            self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            self.current_text = "Loading"
            self.stop_event = threading.Event()
            self.spinner_thread = None
            
        def _spin(self):
            i = 0
            while not self.stop_event.is_set():
                char = self.spinner_chars[i % len(self.spinner_chars)]
                print(f"\r{char} {self.current_text}...", end="", flush=True)
                time.sleep(0.1)
                i += 1
                
        def start(self):
            self.spinner_thread = threading.Thread(target=self._spin)
            self.spinner_thread.daemon = True
            self.spinner_thread.start()
            
        def update_text(self, new_text):
            self.current_text = new_text
            
        def stop(self, final_text="Complete"):
            self.stop_event.set()
            if self.spinner_thread:
                self.spinner_thread.join(timeout=0.3)
            print(f"\r✓ {final_text}!                    ")
            
    return UpdateSpinner()


def validate_command_safety(ai_response):
    """Check if AI response contains safety warnings"""
    lines = ai_response.strip().split('\n')
    
    for line in lines:
        if line.strip().startswith('⚠️'):
            # Extract warning message (remove the warning emoji and clean up)
            warning_text = line.replace('⚠️', '').strip()
            return {
                'is_dangerous': True,
                'warning': warning_text
            }
    
    return {'is_dangerous': False}


def handle_update():
    """Update ask CLI to the latest version"""
    # Check if git is available
    if not shutil.which('git'):
        print("Error: Git is required for updating. Please install git and try again.")
        sys.exit(1)
    
    # Get the installation directory
    install_dir = os.path.expanduser("~/.local/bin/ask-src")
    
    if not os.path.exists(install_dir):
        print("Error: Installation directory not found. Please reinstall using the install script.")
        sys.exit(1)
    
    try:
        # Start the dynamic spinner
        spinner = show_update_spinner()
        spinner.start()
        
        # Create a temporary directory for the update
        with tempfile.TemporaryDirectory() as temp_dir:
            # Phase 1: Loading/Preparing
            time.sleep(0.5)  # Brief loading phase
            
            # Phase 2: Downloading
            spinner.update_text("Downloading")
            
            # Clone the latest version to temp directory
            result = subprocess.run([
                'git', 'clone', 'https://github.com/sjdpk/ask-cli.git', temp_dir
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                spinner.stop("Failed")
                print("Error: Failed to download latest version from GitHub")
                sys.exit(1)
            
            # Check if src directory exists in the downloaded version
            new_src_dir = os.path.join(temp_dir, 'src')
            if not os.path.exists(new_src_dir):
                spinner.stop("Failed")
                print("Error: Invalid repository structure")
                sys.exit(1)
            
            # Phase 3: Updating
            spinner.update_text("Updating")
            time.sleep(0.5)  # Brief pause to show updating text
            
            # Remove current installation and copy new version
            shutil.rmtree(install_dir)
            shutil.copytree(new_src_dir, install_dir)
            
            # Copy the main ask script
            new_ask_script = os.path.join(temp_dir, 'ask')
            ask_script_path = os.path.expanduser("~/.local/bin/ask")
            
            if os.path.exists(new_ask_script):
                shutil.copy2(new_ask_script, ask_script_path)
                os.chmod(ask_script_path, 0o755)
            
            # Complete
            spinner.stop("Ask CLI updated successfully")
            
    except Exception as e:
        try:
            spinner.stop("Failed")
        except:
            pass
        print(f"Update failed: {e}")
        print("Please try running the install script again if issues persist.")
        sys.exit(1)
    
    sys.exit(0)


def get_user_confirmation(command, ai_response):
    """Ask user for confirmation before executing a command"""
    print(f"\nGenerated command: {command}")
    
    # Check if AI response contains safety warnings
    validation_result = validate_command_safety(ai_response)
    
    if validation_result['is_dangerous']:
        print(f"\n WARNING: {validation_result['warning']}")
        print("This command could potentially cause harm to your system or data.")
        
        while True:
            response = input("Are you sure you want to execute this command? [y/N]: ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    else:
        # Normal confirmation for safe commands
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
            print("\nCommand executed successfully.")
        else:
            print(f"\nCommand failed with exit code {process.returncode}.")

    except Exception as e:
        print(f"Error executing command: {e}")


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
                if get_user_confirmation(command_to_execute, result):
                    execute_command(command_to_execute)
                else:
                    print("Command execution cancelled.")
            else:
                # Force execution without confirmation (but still validate for warnings)
                validation_result = validate_command_safety(result)
                if validation_result['is_dangerous']:
                    print(f" WARNING: {validation_result['warning']}")
                    print("Executing anyway due to --force flag...")
                execute_command(command_to_execute)
        else:
            print("No command generated to execute.")
    else:
        # Show result (warnings are already included in AI response)
        print(result)
