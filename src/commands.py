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
    """Update ask CLI to the latest version with comprehensive error handling"""
    try:
        # Check if git is available
        if not shutil.which('git'):
            print("➜ Git is required for updating. Please install git and try again.")
            print("   Installation guide: https://git-scm.com/downloads")
            sys.exit(1)
        
        # Get the installation directory
        install_dir = os.path.expanduser("~/.local/bin/ask-src")
        
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


def get_user_confirmation(command, ai_response):
    """Ask user for confirmation before executing a command with comprehensive error handling"""
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


def execute_command(command):
    """Execute a shell command with comprehensive error handling"""
    if not command or not command.strip():
        print("➜ No command to execute.")
        return
        
    print(f"Executing: {command}")
    
    try:
        # Validate command before execution
        if len(command) > 1000:
            print("➜ Command too long. Execution cancelled for safety.")
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


def handle_query(query, execute=False, force=False):
    """Process user query and generate command with comprehensive error handling"""
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
