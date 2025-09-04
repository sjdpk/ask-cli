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
    """Load API key from config file"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('api_key')
        except Exception:
            pass
    return None


def save_api_key(api_key):
    """Save API key to config file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'api_key': api_key}, f)
    
    # Set secure permissions (Unix-like systems only)
    if platform.system().lower() != 'windows':
        os.chmod(CONFIG_FILE, 0o600)


def test_api_key(api_key):
    """Test if API key is valid"""
    try:
        genai.configure(api_key=api_key)
        test_model = genai.GenerativeModel(AI_MODEL)
        test_model.generate_content("respond with ok")
        return True
    except Exception:
        return False


def setup_api_key():
    """Interactive API key setup"""
    print("\n🚀 Quick setup (30 seconds, one-time only)")
    print("\n1️⃣  Get your free API key:")
    print("   https://makersuite.google.com/app/apikey")
    print("   (Sign in → Create API Key → Copy)\n")
    
    while True:
        key = input("2️⃣  Paste key here: ").strip()
        if not key:
            print("\nNo key entered. Exiting.")
            sys.exit(1)
        
        # Test the API key
        print("   Testing...", end="", flush=True)
        if test_api_key(key):
            save_api_key(key)
            print(" ✅\n")
            print("✨ Setup complete! You're ready to go.\n")
            return key
        else:
            print(" \n   Invalid key. Try again.\n")


def reset_config():
    """Reset API key configuration"""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        print("✅ Reset complete. Run 'ask' again to set up.")
    else:
        print("No configuration found.")
