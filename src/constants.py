#!/usr/bin/env python3
"""
Constants and configuration values for ask CLI

This module centralizes all constants, configuration values, and static text
used throughout the ask CLI application for better maintainability.
"""

from pathlib import Path


# Application metadata
APP_NAME = "ask"
APP_DESCRIPTION = "instant terminal commands"
GITHUB_REPO = "https://github.com/sjdpk/ask-cli"
INSTALL_SCRIPT_URL = "https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.sh"

# AI Configuration
AI_MODEL = 'gemini-2.0-flash-exp'
AI_TEMPERATURE = 0.1
AI_MAX_OUTPUT_TOKENS = 150
AI_TEST_PROMPT = "respond with ok"
AI_TEST_MAX_TOKENS = 10

# File paths and directories
CONFIG_FILE = Path.home() / '.ask_config.json'
INSTALL_DIR = Path.home() / ".local" / "bin" / "ask-src"
ASK_SCRIPT_PATH = Path.home() / ".local" / "bin" / "ask"

# API and network configuration
API_KEY_URL = "https://makersuite.google.com/app/apikey"
MAX_API_RETRIES = 3
INITIAL_RETRY_DELAY = 1  # seconds
MAX_CONFIRMATION_ATTEMPTS = 3
MAX_SETUP_ATTEMPTS = 5

# Command execution limits
MAX_COMMAND_LENGTH = 1000
PROCESS_TERMINATION_TIMEOUT = 5  # seconds

# UI Configuration
SPINNER_CHARS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
SPINNER_DELAY = 0.08  # seconds
SPINNER_CLEAR_WIDTH = 20

# Interactive mode configuration
DEFAULT_CONTEXT_LIMIT = 5
MIN_CONTEXT_LIMIT = 1
MAX_CONTEXT_LIMIT = 20

# Interactive session commands
INTERACTIVE_COMMANDS = {
    '/exit': 'Exit interactive session',
    '/quit': 'Exit interactive session', 
    '/clear': 'Clear conversation context',
    '/history': 'Show query history',
    '/help': 'Show interactive help',
    '/last': 'Re-run last command'
}

# Help text
HELP_TEXT = f"""
{APP_NAME} - {APP_DESCRIPTION}

Usage:
  {APP_NAME} <what you want to do>
  {APP_NAME} --execute <what you want to do>
  {APP_NAME} --interactive <what you want to do>
  {APP_NAME} --execute --force <what you want to do>

Examples:
  {APP_NAME} list all files                    → ls -la
  {APP_NAME} check disk space                  → df -h
  {APP_NAME} find text in files                → grep -r "text" .
  {APP_NAME} kill port 3000                   → lsof -ti:3000 | xargs kill -9
  {APP_NAME} compress folder                  → tar -czf archive.tar.gz .
  {APP_NAME} --interactive find large files   → Start interactive session
  {APP_NAME} -i --context-limit 3 list files  → Interactive with 3-query limit

Options:
  -e, --execute      Execute the generated command (with confirmation)
  -f, --force        Force execution without confirmation (must be used with -e)
  -i, --interactive  Enable interactive mode for follow-up queries
  --context-limit N  Set max number of previous queries to remember (default: 5)
  --help            Show this help
  --reset           Reset API key
  --update          Update {APP_NAME} CLI to the latest version

Interactive Mode:
  In interactive mode, you can ask follow-up questions and refine commands.
  Use /exit to quit, /clear to reset context, /history to see past queries.

Safety:
  {APP_NAME.title()} CLI automatically detects potentially dangerous commands and shows
  warnings before execution to help protect your system and data.
"""

# Error messages
ERROR_MESSAGES = {
    'no_git': "Git is required for updating. Please install git and try again.\nInstallation guide: https://git-scm.com/downloads",
    'install_not_found': f"Installation directory not found. Please reinstall using:\n{INSTALL_SCRIPT_URL}",
    'network_error': "Network error: Cannot connect to GitHub.\nPlease check your internet connection and try again.",
    'download_timeout': "Download timeout. Please try again later.",
    'permission_denied': "Permission denied. You may need to run with appropriate privileges.",
    'command_not_found': "Command not found. Please check if the command is installed and in your PATH.",
    'config_corrupted': f"Config file corrupted. Run '{APP_NAME} --reset' to fix.",
    'api_key_invalid': f"Invalid API key. Run '{APP_NAME} --reset' to update your API key.",
    'quota_exceeded': "API quota exceeded. Please check your Google AI Studio quota or try again later.",
    'rate_limited': "Too many requests. Please wait a moment and try again.",
    'command_too_long': f"Command too long (>{MAX_COMMAND_LENGTH} chars). Execution cancelled for safety.",
    'too_many_attempts': f"Too many invalid attempts ({MAX_CONFIRMATION_ATTEMPTS}). Cancelling execution.",
    'setup_failed': f"Too many failed attempts ({MAX_SETUP_ATTEMPTS}). Please check your API key and try again later."
}

# Success messages
SUCCESS_MESSAGES = {
    'setup_complete': "✨ Setup complete! You're ready to go.",
    'reset_complete': f"➜ Reset complete. Run '{APP_NAME}' again to set up.",
    'update_complete': f"Ask CLI updated successfully",
    'command_success': "➜ Command executed successfully.",
    'process_terminated': "➜ Process terminated successfully."
}

# Warning prefixes for dangerous commands
DANGEROUS_COMMAND_PATTERNS = [
    'rm ', 'rmdir ', 'rm -', 'sudo ', 'chmod 777', 'chown ',
    'dd ', 'mkfs', 'fdisk', 'curl|sh', 'wget|bash', 'killall',
    'kill -9', 'shutdown', 'reboot', 'halt', 'DROP ', 'TRUNCATE',
    '>', '>>'
]

# OS name mapping
OS_NAME_MAP = {
    'darwin': 'macOS',
    'linux': 'Linux', 
    'windows': 'Windows'
}

# File permissions
CONFIG_FILE_PERMISSIONS = 0o600  # Read/write for owner only
