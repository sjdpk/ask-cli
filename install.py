#!/usr/bin/env python3
"""
Cross-platform installer for Ask CLI
Automatically detects the platform and runs the appropriate installer
"""

import os
import sys
import platform
import subprocess
import urllib.request
import tempfile

def get_platform():
    """Detect the current platform"""
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    elif system == 'linux':
        return 'linux'
    else:
        return 'unknown'

def download_file(url, filename):
    """Download a file from URL"""
    try:
        urllib.request.urlretrieve(url, filename)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def run_windows_installer():
    """Run Windows PowerShell installer"""
    print("Detected Windows - using PowerShell installer...")
    
    # Try PowerShell first
    try:
        result = subprocess.run([
            'powershell', '-ExecutionPolicy', 'Bypass', '-Command',
            'iwr -useb https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.ps1 | iex'
        ], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("PowerShell failed, trying batch installer...")
        
        # Fallback to batch file
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
                batch_url = 'https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.bat'
                if download_file(batch_url, f.name):
                    subprocess.run([f.name], check=True)
                    os.unlink(f.name)
                    return True
        except Exception as e:
            print(f"Batch installer failed: {e}")
    
    return False

def run_unix_installer():
    """Run Unix/Linux/macOS bash installer"""
    print("Detected Unix-like system - using bash installer...")
    
    try:
        # Use curl if available
        if subprocess.run(['which', 'curl'], capture_output=True).returncode == 0:
            result = subprocess.run([
                'bash', '-c',
                'curl -sSL https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.sh | bash'
            ], check=True)
            return True
        # Fall back to wget
        elif subprocess.run(['which', 'wget'], capture_output=True).returncode == 0:
            result = subprocess.run([
                'bash', '-c',
                'wget -qO- https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.sh | bash'
            ], check=True)
            return True
        else:
            print("Error: Neither curl nor wget found. Please install one of them.")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e}")
        return False

def main():
    """Main installer function"""
    print("Ask CLI Cross-Platform Installer")
    print("=" * 40)
    
    # Detect platform
    detected_platform = get_platform()
    print(f"Detected platform: {detected_platform}")
    
    if detected_platform == 'unknown':
        print("Error: Unsupported platform detected.")
        print("Please install manually from: https://github.com/sjdpk/ask-cli")
        sys.exit(1)
    
    # Check Python 3
    if sys.version_info[0] < 3:
        print("Error: Python 3 is required. Please install Python 3 and try again.")
        sys.exit(1)
    
    print(f"Using Python {sys.version}")
    
    # Run platform-specific installer
    success = False
    
    if detected_platform == 'windows':
        success = run_windows_installer()
    else:  # macOS or Linux
        success = run_unix_installer()
    
    if success:
        print("\n✅ Installation completed successfully!")
        print("\nQuick start:")
        print("   ask how to list files")
        print("\nFor help:")
        print("   ask --help")
    else:
        print("\n❌ Installation failed.")
        print("\nPlease try manual installation:")
        print("1. Clone: git clone https://github.com/sjdpk/ask-cli.git")
        print("2. Run the appropriate installer script for your platform")
        sys.exit(1)

if __name__ == "__main__":
    main()
