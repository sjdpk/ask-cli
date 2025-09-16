#!/usr/bin/env python3
"""
Command handlers for ask CLI

This module contains all command handler functions that implement the core
functionality of the ask CLI tool, including help, reset, update, and query processing.
"""

import sys
import subprocess
import os
import shutil
import tempfile
import time
from typing import Dict, Any, Optional, NoReturn

# Import local modules
from config import load_api_key, setup_api_key, reset_config
from ai import CommandGenerator
from ui import SpinnerContext
from constants import (
    HELP_TEXT, ERROR_MESSAGES, SUCCESS_MESSAGES, DANGEROUS_COMMAND_PATTERNS,
    INSTALL_DIR, ASK_SCRIPT_PATH, MAX_COMMAND_LENGTH, MAX_CONFIRMATION_ATTEMPTS,
    PROCESS_TERMINATION_TIMEOUT, GITHUB_REPO
)


def handle_help() -> NoReturn:
    """
    Display comprehensive help information for the ask CLI.
    
    Shows usage instructions, examples, options, and safety information
    to help users understand how to use the tool effectively.
    
    Raises:
        SystemExit: Always exits with code 0 after displaying help
    """
    print(HELP_TEXT)
    sys.exit(0)


def handle_reset() -> NoReturn:
    """
    Reset API key configuration to allow fresh setup.
    
    Delegates to the config module to remove existing configuration
    and allows the user to set up a new API key.
    
    Raises:
        SystemExit: Always exits with code 0 after reset
    """
    reset_config()
    sys.exit(0)


def show_update_spinner() -> 'UpdateSpinner':
    """
    Create and return a dynamic spinner for update process with changing text.
    
    Provides a specialized spinner that can update its display text during
    long-running update operations to keep users informed of progress.
    
    Returns:
        UpdateSpinner instance ready to use
    """
    import threading
    from constants import SPINNER_CHARS, SPINNER_DELAY
    
    class UpdateSpinner:
        """Dynamic spinner with changeable text for update operations."""
        
        def __init__(self):
            """Initialize the update spinner with default settings."""
            self.spinner_chars = SPINNER_CHARS
            self.current_text = "Loading"
            self.stop_event = threading.Event()
            self.spinner_thread: Optional[threading.Thread] = None
            
        def _spin(self) -> None:
            """Internal method to run the spinner animation."""
            i = 0
            while not self.stop_event.is_set():
                char = self.spinner_chars[i % len(self.spinner_chars)]
                print(f"\r{char} {self.current_text}...", end="", flush=True)
                time.sleep(0.1)
                i += 1
                
        def start(self) -> None:
            """Start the spinner animation in a separate thread."""
            self.spinner_thread = threading.Thread(target=self._spin)
            self.spinner_thread.daemon = True
            self.spinner_thread.start()
            
        def update_text(self, new_text: str) -> None:
            """
            Update the spinner display text.
            
            Args:
                new_text: New text to display with the spinner
            """
            self.current_text = new_text
            
        def stop(self, final_text: str = "Complete") -> None:
            """
            Stop the spinner and display final message.
            
            Args:
                final_text: Final text to display when stopping
            """
            self.stop_event.set()
            if self.spinner_thread:
                self.spinner_thread.join(timeout=0.3)
            print(f"\r✓ {final_text}!                    ")
            
    return UpdateSpinner()


def validate_command_safety(ai_response: str) -> Dict[str, Any]:
    """
    Check if AI response contains safety warnings or dangerous patterns.
    
    Analyzes the AI response to identify potentially dangerous commands
    and extracts warning messages for user notification.
    
    Args:
        ai_response: The complete AI response text to analyze
        
    Returns:
        Dictionary containing:
        - 'is_dangerous': Boolean indicating if command is potentially dangerous
        - 'warning': Warning message if dangerous, otherwise not present
    """
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


def handle_update() -> NoReturn:
    """
    Update ask CLI to the latest version with comprehensive error handling.
    
    Downloads and installs the latest version of the ask CLI from the GitHub
    repository, with backup and recovery mechanisms for safe updates.
    
    Raises:
        SystemExit: Always exits after update completion or failure
        
    Side Effects:
        - Creates temporary directories for download
        - Modifies installation directory
        - Updates executable script
        - Shows progress spinner
    """
    try:
        # Check if git is available
        if not shutil.which('git'):
            print("➜ Git is required for updating. Please install git and try again.")
            print("   Installation guide: https://git-scm.com/downloads")
            sys.exit(1)
        
        # Get the installation directory
        install_dir = INSTALL_DIR
        
        if not os.path.exists(install_dir):
            print("➜ Installation directory not found. Please reinstall using:")
            print("   curl -sSL https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.sh | bash")
            sys.exit(1)
        
        spinner = None
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
                
                try:
                    # Clone the latest version to temp directory
                    result = subprocess.run([
                        'git', 'clone', 'https://github.com/sjdpk/ask-cli.git', temp_dir
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode != 0:
                        spinner.stop("Failed")
                        error_msg = result.stderr.strip() if result.stderr else "Unknown git error"
                        if "network" in error_msg.lower() or "connection" in error_msg.lower():
                            print("➜ Network error: Cannot connect to GitHub.")
                            print("   Please check your internet connection and try again.")
                        elif "timeout" in error_msg.lower():
                            print("➜ Download timeout. Please try again later.")
                        else:
                            print(f"➜ Failed to download latest version: {error_msg}")
                        sys.exit(1)
                        
                except subprocess.TimeoutExpired:
                    spinner.stop("Failed")
                    print("➜ Download timeout. Please check your internet connection and try again.")
                    sys.exit(1)
                except Exception as e:
                    spinner.stop("Failed")
                    print(f"➜ Download failed: {str(e)}")
                    sys.exit(1)
                
                # Check if src directory exists in the downloaded version
                new_src_dir = os.path.join(temp_dir, 'src')
                if not os.path.exists(new_src_dir):
                    spinner.stop("Failed")
                    print("➜ Invalid repository structure. Update aborted.")
                    sys.exit(1)
                
                # Phase 3: Updating
                spinner.update_text("Updating")
                time.sleep(0.5)  # Brief pause to show updating text
                
                try:
                    # Backup current installation
                    backup_dir = f"{install_dir}.backup"
                    if os.path.exists(backup_dir):
                        shutil.rmtree(backup_dir)
                    shutil.copytree(install_dir, backup_dir)
                    
                    # Remove current installation and copy new version
                    shutil.rmtree(install_dir)
                    shutil.copytree(new_src_dir, install_dir)
                    
                    # Copy the main ask script
                    new_ask_script = os.path.join(temp_dir, 'ask')
                    ask_script_path = os.path.expanduser("~/.local/bin/ask")
                    
                    if os.path.exists(new_ask_script):
                        shutil.copy2(new_ask_script, ask_script_path)
                        os.chmod(ask_script_path, 0o755)
                    
                    # Remove backup on success
                    if os.path.exists(backup_dir):
                        shutil.rmtree(backup_dir)
                    
                    # Complete
                    spinner.stop("Ask CLI updated successfully")
                    
                except PermissionError:
                    spinner.stop("Failed")
                    print("➜ Permission denied during update. Try running with sudo or check file permissions.")
                    sys.exit(1)
                except OSError as e:
                    spinner.stop("Failed")
                    print(f"➜ File system error during update: {str(e)}")
                    # Try to restore backup
                    if os.path.exists(backup_dir):
                        try:
                            if os.path.exists(install_dir):
                                shutil.rmtree(install_dir)
                            shutil.move(backup_dir, install_dir)
                            print("✅ Backup restored successfully.")
                        except Exception:
                            print("⚠️ Could not restore backup. Please reinstall manually.")
                    sys.exit(1)
                except Exception as e:
                    spinner.stop("Failed")
                    print(f"➜ Update failed: {str(e)}")
                    sys.exit(1)
                
        except KeyboardInterrupt:
            if spinner:
                spinner.stop("Cancelled")
            print("\n\n👋 Update cancelled by user.")
            sys.exit(0)
        except Exception as e:
            if spinner:
                try:
                    spinner.stop("Failed")
                except:
                    pass
            print(f"➜ Update failed: {str(e)}")
            print("   Please try running the install script again if issues persist:")
            print("   curl -sSL https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.sh | bash")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Update cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"➜ Unexpected error during update: {str(e)}")
        sys.exit(1)
    
    sys.exit(0)


def get_user_confirmation(command: str, ai_response: str) -> bool:
    """
    Ask user for confirmation before executing a potentially dangerous command.
    
    Presents the command to the user and requests confirmation, with special
    handling for commands that have been flagged as potentially dangerous.
    
    Args:
        command: The command string to be executed
        ai_response: Full AI response containing potential warnings
        
    Returns:
        True if user confirms execution, False otherwise
        
    Side Effects:
        Prints command and warning information to stdout
        Reads user input from stdin
    """
    try:
        print(f"\nGenerated command: {command}")
        
        # Check if AI response contains safety warnings
        validation_result = validate_command_safety(ai_response)
        
        if validation_result['is_dangerous']:
            print(f"\n⚠️ WARNING: {validation_result['warning']}")
            print("This command could potentially cause harm to your system or data.")
            
            max_attempts = 3
            attempts = 0
            
            while attempts < max_attempts:
                try:
                    response = input("Are you sure you want to execute this command? [y/N]: ").strip().lower()
                    if response in ['y', 'yes']:
                        return True
                    elif response in ['n', 'no', '']:
                        return False
                    else:
                        print("Please enter 'y' for yes or 'n' for no.")
                        attempts += 1
                except KeyboardInterrupt:
                    print("\n\n👋 Operation cancelled by user.")
                    return False
                except EOFError:
                    print("\n\n👋 Input cancelled.")
                    return False
                except Exception as e:
                    print(f"\n➜ Input error: {str(e)}")
                    attempts += 1
            
            print("➜ Too many invalid attempts. Cancelling execution.")
            return False
        else:
            # Normal confirmation for safe commands
            max_attempts = 3
            attempts = 0
            
            while attempts < max_attempts:
                try:
                    response = input("Do you want to execute this command? [y/N]: ").strip().lower()
                    if response in ['y', 'yes']:
                        return True
                    elif response in ['n', 'no', '']:
                        return False
                    else:
                        print("Please enter 'y' for yes or 'n' for no.")
                        attempts += 1
                except KeyboardInterrupt:
                    print("\n\n👋 Operation cancelled by user.")
                    return False
                except EOFError:
                    print("\n\n👋 Input cancelled.")
                    return False
                except Exception as e:
                    print(f"\n➜ Input error: {str(e)}")
                    attempts += 1
            
            print("➜ Too many invalid attempts. Cancelling execution.")
            return False
            
    except Exception as e:
        print(f"\n➜ Error during confirmation: {str(e)}")
        return False


def execute_command(command: str) -> None:
    """
    Execute a shell command with comprehensive error handling and safety checks.
    
    Runs the provided command in a subprocess with timeout handling,
    output streaming, and graceful interruption support.
    
    Args:
        command: The shell command string to execute
        
    Side Effects:
        - Executes system command
        - Prints command output to stdout
        - May terminate processes on interruption
    """
    if not command or not command.strip():
        print("➜ No command to execute.")
        return
        
    print(f"Executing: {command}")
    
    try:
        # Validate command before execution
        if len(command) > MAX_COMMAND_LENGTH:
            print(f"➜ {ERROR_MESSAGES['command_too_long']}")
            return
            
        # Start the process with timeout
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Read output line by line with timeout handling
            try:
                for line in process.stdout:
                    print(line, end='')
            except KeyboardInterrupt:
                print("\n\n⚠️ Command interrupted by user. Terminating process...")
                try:
                    process.terminate()
                    # Wait a bit for graceful termination
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        # Force kill if it doesn't terminate gracefully
                        process.kill()
                        process.wait()
                    print("✅ Process terminated successfully.")
                except Exception as e:
                    print(f"➜ Error terminating process: {str(e)}")
                return

            # Wait for process to complete
            return_code = process.wait()

            if return_code == 0:
                print("\n✅ Command executed successfully.")
            else:
                print(f"\n➜ Command failed with exit code {return_code}.")
                
        except FileNotFoundError:
            print("➜ Command not found. Please check if the command is installed and in your PATH.")
        except PermissionError:
            print("➜ Permission denied. You may need to run with appropriate privileges.")
        except subprocess.SubprocessError as e:
            print(f"➜ Process error: {str(e)}")
        except OSError as e:
            error_str = str(e).lower()
            if "no such file" in error_str:
                print("➜ Command not found. Please check if the command is installed.")
            elif "permission denied" in error_str:
                print("➜ Permission denied. You may need to run with appropriate privileges.")
            else:
                print(f"➜ System error executing command: {str(e)}")
        except Exception as e:
            print(f"➜ Unexpected error during command execution: {str(e)}")
            
    except KeyboardInterrupt:
        print("\n\n👋 Command execution cancelled by user.")
    except Exception as e:
        print(f"➜ Error preparing command execution: {str(e)}")


def handle_query(query: str, execute: bool = False, force: bool = False) -> None:
    """
    Process user query and generate appropriate terminal command.
    
    Takes a natural language query, generates a terminal command using AI,
    and optionally executes it based on user flags and confirmation.
    
    Args:
        query: Natural language description of desired action
        execute: Whether to execute the generated command
        force: Whether to skip confirmation (requires execute=True)
        
    Side Effects:
        - Calls AI service for command generation
        - May execute system commands
        - Prints results and status messages
    """
    if not query or not query.strip():
        print("➜ Please provide a valid query.")
        return
        
    try:
        # Get API key (setup if needed)
        try:
            api_key = load_api_key()
            if not api_key:
                api_key = setup_api_key()
        except KeyboardInterrupt:
            print("\n\n👋 Setup cancelled by user.")
            return
        except Exception as e:
            print(f"➜ Error loading API key: {str(e)}")
            return

        # Initialize command generator
        try:
            generator = CommandGenerator(api_key)
        except Exception as e:
            print(f"➜ Error initializing AI service: {str(e)}")
            print("   Try running 'ask --reset' to update your API key.")
            return

        # Generate command with spinner
        try:
            with SpinnerContext():
                result = generator.get_command(query)
        except KeyboardInterrupt:
            print("\n\n👋 Query cancelled by user.")
            return
        except Exception as e:
            print(f"➜ Error generating command: {str(e)}")
            return

        # Check for error responses from AI
        if result.startswith("➜"):
            print(result)
            return

        # Check if the response indicates out of context
        if "out of context" in result.lower():
            print(result)
            return

        # Check if response looks like a valid command response
        if not result.startswith("→") and "→" not in result:
            print("➜ Out of context - this is not a terminal command request")
            return

        # Find the line with the command
        command_to_execute = ""
        try:
            for line in result.split('\n'):
                if line.startswith("→"):
                    command_to_execute = line.replace("→ ", "").strip()
                    break
        except Exception as e:
            print(f"➜ Error parsing command response: {str(e)}")
            return

        if execute:
            if command_to_execute:
                try:
                    # If force flag is not set, ask for confirmation
                    if not force:
                        try:
                            if get_user_confirmation(command_to_execute, result):
                                execute_command(command_to_execute)
                            else:
                                print("👋 Command execution cancelled.")
                        except KeyboardInterrupt:
                            print("\n\n👋 Operation cancelled by user.")
                    else:
                        # Force execution without confirmation (but still validate for warnings)
                        validation_result = validate_command_safety(result)
                        if validation_result['is_dangerous']:
                            print(f"⚠️ WARNING: {validation_result['warning']}")
                            print("Executing anyway due to --force flag...")
                        execute_command(command_to_execute)
                except KeyboardInterrupt:
                    print("\n\n👋 Operation cancelled by user.")
                except Exception as e:
                    print(f"➜ Error during command execution: {str(e)}")
            else:
                print("➜ No valid command found to execute.")
        else:
            # Show result (warnings are already included in AI response)
            try:
                print(result)
            except Exception as e:
                print(f"➜ Error displaying result: {str(e)}")
                
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user.")
    except Exception as e:
        print(f"➜ Unexpected error processing query: {str(e)}")
        print("   Please try again or report this issue if it persists.")
