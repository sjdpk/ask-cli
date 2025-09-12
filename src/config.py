#!/usr/bin/env python3
"""Configuration management for ask CLI"""

import os
import sys
import json
import platform
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    print("📦 Installing required package...")
    os.system(f"{sys.executable} -m pip install -q google-generativeai")
    import google.generativeai as genai

# Configuration constants
CONFIG_FILE = Path.home() / '.ask_config.json'
AI_MODEL = 'gemini-2.0-flash-exp'


def get_os_name():
    """Get user-friendly OS name"""
    os_map = {
        'darwin': 'macOS',
        'linux': 'Linux', 
        'windows': 'Windows'
    }
    return os_map.get(platform.system().lower(), platform.system())


def load_api_key():
    """Load API key from config file with comprehensive error handling"""
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
        print("⚠️ Config file corrupted. Run 'ask --reset' to fix.")
        return None
    except (OSError, IOError) as e:
        print(f"➜ Error reading config file: {str(e)}")
        return None
    except Exception as e:
        print(f"➜ Unexpected error loading config: {str(e)}")
        return None


def save_api_key(api_key):
    """Save API key to config file with comprehensive error handling"""
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
                os.chmod(CONFIG_FILE, 0o600)
            except OSError as e:
                print(f"⚠️ Warning: Could not set secure permissions on config file: {str(e)}")
                
    except PermissionError:
        raise PermissionError("Permission denied. Cannot save API key to config file.")
    except OSError as e:
        raise OSError(f"Error saving config file: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error saving API key: {str(e)}")


def test_api_key(api_key):
    """Test if API key is valid with comprehensive error handling"""
    if not api_key or not api_key.strip():
        return False
        
    try:
        genai.configure(api_key=api_key.strip())
        test_model = genai.GenerativeModel(AI_MODEL)
        response = test_model.generate_content(
            "respond with ok",
            generation_config=genai.GenerationConfig(
                temperature=0,
                max_output_tokens=10
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


def setup_api_key():
    """Interactive API key setup with comprehensive error handling"""
    try:
        print("\n🚀 Quick setup (30 seconds, one-time only)")
        print("\n1️⃣  Get your free API key:")
        print("   https://makersuite.google.com/app/apikey")
        print("   (Sign in → Create API Key → Copy)\n")
        
        max_attempts = 5
        attempts = 0
        
        while attempts < max_attempts:
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
                        print("✨ Setup complete! You're ready to go.\n")
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
        
        print(f"➜ Too many failed attempts ({max_attempts}). Please check your API key and try again later.")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n➜ Unexpected error during setup: {str(e)}")
        sys.exit(1)


def reset_config():
    """Reset API key configuration with comprehensive error handling"""
    try:
        if CONFIG_FILE.exists():
            try:
                CONFIG_FILE.unlink()
                print("✅ Reset complete. Run 'ask' again to set up.")
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
