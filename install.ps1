# PowerShell installer for 'ask' command on Windows

Write-Host "Installing 'ask' command for Windows..." -ForegroundColor Green

# Check Python 3
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        Write-Host "✓ Python 3 found: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "Error: Python 3 required. Please install from python.org" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: Python 3 not found. Please install from python.org" -ForegroundColor Red
    exit 1
}

# Check if git is available
try {
    git --version | Out-Null
    Write-Host "✓ Git found" -ForegroundColor Green
} catch {
    Write-Host "Error: Git is required for installation. Please install Git for Windows." -ForegroundColor Red
    exit 1
}

# Set installation directory
$INSTALL_DIR = "$env:TEMP\ask-cli-install"
Write-Host "Cloning repository to $INSTALL_DIR..." -ForegroundColor Yellow

# Remove existing installation directory if it exists
if (Test-Path $INSTALL_DIR) {
    Remove-Item -Recurse -Force $INSTALL_DIR
}

# Clone the repository
try {
    git clone https://github.com/sjdpk/ask-cli.git $INSTALL_DIR 2>&1 | Out-Null
    Write-Host "✓ Repository cloned successfully" -ForegroundColor Green
} catch {
    Write-Host "Error: Failed to clone repository" -ForegroundColor Red
    exit 1
}

# Change to the cloned directory
Set-Location $INSTALL_DIR

# Check if ask script exists
if (-not (Test-Path "ask")) {
    Write-Host "Error: ask script not found in repository" -ForegroundColor Red
    exit 1
}

# Check if src directory exists
if (-not (Test-Path "src")) {
    Write-Host "Error: src directory not found in repository" -ForegroundColor Red
    exit 1
}

# Install Python package
Write-Host "Installing dependencies..." -ForegroundColor Yellow
try {
    python -m pip install --user google-generativeai 2>&1 | Out-Null
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "Note: You may need to install manually:" -ForegroundColor Yellow
    Write-Host "   pip install --user google-generativeai" -ForegroundColor Yellow
}

# Create user's local bin directory in AppData
$LOCAL_BIN = "$env:APPDATA\ask-cli"
$SCRIPTS_DIR = "$env:APPDATA\Python\Scripts"

# Create directories
New-Item -ItemType Directory -Force -Path $LOCAL_BIN | Out-Null
New-Item -ItemType Directory -Force -Path $SCRIPTS_DIR | Out-Null

# Copy files
Copy-Item -Recurse -Force "src" "$LOCAL_BIN\src"

# Create Windows batch file
$BATCH_CONTENT = @"
@echo off
python "$LOCAL_BIN\ask" %*
"@

$BATCH_CONTENT | Out-File -FilePath "$SCRIPTS_DIR\ask.bat" -Encoding ASCII

# Create Python wrapper script
$PYTHON_WRAPPER = @"
#!/usr/bin/env python3
"""Ask CLI entry point script for Windows"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
script_dir = Path(__file__).parent.resolve()
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

# Import and run main
try:
    from main import main
except ImportError:
    # Fallback for installed version
    src_dir = Path(os.getenv('APPDATA')) / "ask-cli" / "src"
    sys.path.insert(0, str(src_dir))
    from main import main

if __name__ == "__main__":
    main()
"@

$PYTHON_WRAPPER | Out-File -FilePath "$LOCAL_BIN\ask" -Encoding UTF8

# Clean up the cloned repository
Write-Host "Cleaning up..." -ForegroundColor Yellow
Set-Location $env:TEMP
Remove-Item -Recurse -Force $INSTALL_DIR

# Check if Scripts directory is in PATH
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*$SCRIPTS_DIR*") {
    Write-Host "Adding Python Scripts directory to PATH..." -ForegroundColor Yellow
    
    # Add to user PATH
    $newPath = "$currentPath;$SCRIPTS_DIR"
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    
    Write-Host "✓ Added $SCRIPTS_DIR to PATH" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Restart your command prompt or PowerShell" -ForegroundColor Yellow
    Write-Host "to use the updated PATH." -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "✓ Installation complete!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Quick start:" -ForegroundColor Cyan
Write-Host "   ask how to list files" -ForegroundColor White
Write-Host ""
Write-Host "Installed to: $LOCAL_BIN" -ForegroundColor Gray
Write-Host "Config: %USERPROFILE%\.ask_config.json (created on first use)" -ForegroundColor Gray
Write-Host ""
Write-Host "Help: ask --help" -ForegroundColor Gray
