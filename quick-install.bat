@echo off
setlocal enabledelayedexpansion

echo Ask CLI Quick Installer for Windows
echo ====================================

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python 3 is required but not found.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found. Starting installation...
echo.

REM Run the Python cross-platform installer
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.py').read())"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Installation completed successfully!
    echo You can now use: ask --help
) else (
    echo.
    echo Installation failed. Please try manual installation.
)

pause
