#!/usr/bin/env python3
"""
Configuration management for ask CLI

This module handles all configuration-related operations including API key
management, storage, validation, and user setup processes.
"""

import os
import sys
import json
import platform
from pathlib import Path
from typing import Optional

# Import constants
from constants import (
    CONFIG_FILE, AI_MODEL, CONFIG_FILE_PERMISSIONS, OS_NAME_MAP,
    API_KEY_URL, MAX_SETUP_ATTEMPTS, ERROR_MESSAGES, SUCCESS_MESSAGES,
    AI_TEST_PROMPT, AI_TEST_MAX_TOKENS
)

try:
    import google.generativeai as genai
except ImportError:
    print("📦 Installing required package...")
    os.system(f"{sys.executable} -m pip install -q google-generativeai")
    import google.generativeai as genai


def get_os_name() -> str:
    """
    Get user-friendly operating system name.
    
    Maps the system platform identifier to a human-readable OS name
    for display purposes and system-specific command generation.
    
    Returns:
        Human-readable operating system name (e.g., 'macOS', 'Linux', 'Windows')
    """
    return OS_NAME_MAP.get(platform.system().lower(), platform.system())


def load_api_key() -> Optional[str]:
    """
    Load API key from configuration file.
    
    Attempts to read and validate the API key from the user's configuration
    file, with comprehensive error handling for various failure scenarios.
    
    Returns:
        API key string if found and valid, None otherwise
        
    Side Effects:
        May print error messages to stdout for user feedback
    """
    if not CONFIG_FILE.exists():
        return None
        
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            api_key = config.get('api_key')
            if api_key and api_key.strip():
                return api_key.strip()
            return None
    except PermissionError:
        print("➜ Permission denied accessing config file. Please check file permissions.")
        return None
    except json.JSONDecodeError:
        print(f"⚠️ {ERROR_MESSAGES['config_corrupted']}")
        return None
    except (OSError, IOError) as e:
        print(f"➜ Error reading config file: {str(e)}")
        return None
    except Exception as e:
        print(f"➜ Unexpected error loading config: {str(e)}")
        return None


def save_api_key(api_key: str) -> None:
    """
    Save API key to configuration file with secure permissions.
    
    Stores the provided API key in the user's configuration file with
    appropriate file permissions for security.
    
    Args:
        api_key: The API key string to save
        
    Raises:
        ValueError: If API key is empty or None
        PermissionError: If unable to write to config file
        OSError: If file system operations fail
        RuntimeError: For other unexpected errors
    """
    if not api_key or not api_key.strip():
        raise ValueError("API key cannot be empty")
        
    try:
        # Ensure parent directory exists
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Save the API key
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'api_key': api_key.strip()}, f, indent=2)
        
        # Set secure permissions (Unix-like systems only)
        if platform.system().lower() != 'windows':
            try:
                os.chmod(CONFIG_FILE, CONFIG_FILE_PERMISSIONS)
            except OSError as e:
                print(f"⚠️ Warning: Could not set secure permissions on config file: {str(e)}")
                
    except PermissionError:
        raise PermissionError("Permission denied. Cannot save API key to config file.")
    except OSError as e:
        raise OSError(f"Error saving config file: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error saving API key: {str(e)}")


def test_api_key(api_key: str) -> bool:
    """
    Test if the provided API key is valid and working.
    
    Performs a lightweight API call to verify that the API key is valid
    and can successfully communicate with the AI service.
    
    Args:
        api_key: The API key string to test
        
    Returns:
        True if the API key is valid and working, False otherwise
        
    Side Effects:
        May print error messages for network or quota issues
    """
    if not api_key or not api_key.strip():
        return False
        
    try:
        genai.configure(api_key=api_key.strip())
        test_model = genai.GenerativeModel(AI_MODEL)
        response = test_model.generate_content(
            AI_TEST_PROMPT,
            generation_config=genai.GenerationConfig(
                temperature=0,
                max_output_tokens=AI_TEST_MAX_TOKENS
            )
        )
        return response and response.text and "ok" in response.text.lower()
    except Exception as e:
        # Log the specific error for debugging but don't expose it to user during setup
        error_str = str(e).lower()
        if "api_key" in error_str or "authentication" in error_str or "invalid" in error_str:
            return False
        elif "network" in error_str or "connection" in error_str:
            print(f"\n⚠️ Network error during API key test: {str(e)}")
            return False
        elif "quota" in error_str or "limit" in error_str:
            print(f"\n⚠️ API quota issue during test: {str(e)}")
            return False
        else:
            print(f"\n⚠️ Error testing API key: {str(e)}")
            return False


def setup_api_key() -> str:
    """
    Interactive API key setup with comprehensive error handling.
    
    Guides the user through the process of obtaining and configuring
    their API key, with validation and error recovery.
    
    Returns:
        The validated API key string
        
    Raises:
        SystemExit: On user cancellation or repeated failures
    """
    try:
        print("\n🚀 Quick setup (30 seconds, one-time only)")
        print("\n1️⃣  Get your free API key:")
        print(f"   {API_KEY_URL}")
        print("   (Sign in → Create API Key → Copy)\n")
        
        attempts = 0
        
        while attempts < MAX_SETUP_ATTEMPTS:
            try:
                key = input("2️⃣  Paste key here: ").strip()
                if not key:
                    print("\n👋 No key entered. Exiting.")
                    sys.exit(0)
                
                # Basic validation
                if len(key) < 10:
                    print("   ⚠️ API key seems too short. Please check and try again.\n")
                    attempts += 1
                    continue
                
                # Test the API key
                print("   Testing...", end="", flush=True)
                if test_api_key(key):
                    try:
                        save_api_key(key)
                        print(" ✅\n")
                        print(f"{SUCCESS_MESSAGES['setup_complete']}\n")
                        return key
                    except Exception as e:
                        print(f" ➜\n   Error saving API key: {str(e)}")
                        sys.exit(1)
                else:
                    print(" ➜\n   Invalid key or connection issue. Please try again.\n")
                    attempts += 1
                    
            except KeyboardInterrupt:
                print("\n\n👋 Setup cancelled by user.")
                sys.exit(0)
            except EOFError:
                print("\n\n👋 Setup cancelled.")
                sys.exit(0)
            except Exception as e:
                print(f"\n➜ Error during setup: {str(e)}")
                attempts += 1
        
        print(f"➜ {ERROR_MESSAGES['setup_failed']}")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n➜ Unexpected error during setup: {str(e)}")
        sys.exit(1)


def reset_config() -> None:
    """
    Reset API key configuration with comprehensive error handling.
    
    Removes the existing configuration file to allow the user to
    set up a new API key from scratch.
    
    Raises:
        SystemExit: On permission errors or other failures
        
    Side Effects:
        Deletes the configuration file and prints status messages
    """
    try:
        if CONFIG_FILE.exists():
            try:
                CONFIG_FILE.unlink()
                print(f"{SUCCESS_MESSAGES['reset_complete']}")
            except PermissionError:
                print("➜ Permission denied. Cannot delete config file.")
                print("   Please manually delete:", CONFIG_FILE)
                sys.exit(1)
            except OSError as e:
                print(f"➜ Error deleting config file: {str(e)}")
                sys.exit(1)
        else:
            print("ℹ️ No configuration found to reset.")
    except Exception as e:
        print(f"➜ Unexpected error during reset: {str(e)}")
        sys.exit(1)
