@echo off
REM Windows batch installer for 'ask' command

echo Installing 'ask' command for Windows...

REM Check Python 3
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python 3 required. Please install from python.org
    exit /b 1
)

REM Check if git is available
git --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Git is required for installation. Please install Git for Windows.
    exit /b 1
)

REM Set installation directory
set INSTALL_DIR=%TEMP%\ask-cli-install
echo Cloning repository to %INSTALL_DIR%...

REM Remove existing installation directory if it exists
if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"

REM Clone the repository
git clone https://github.com/sjdpk/ask-cli.git "%INSTALL_DIR%" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to clone repository
    exit /b 1
)

REM Change to the cloned directory
cd /d "%INSTALL_DIR%"

echo Repository cloned successfully

REM Check if ask script exists
if not exist "ask" (
    echo Error: ask script not found in repository
    exit /b 1
)

REM Check if src directory exists
if not exist "src" (
    echo Error: src directory not found in repository
    exit /b 1
)

REM Install Python package
echo Installing dependencies...
python -m pip install --user google-generativeai >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Note: You may need to install manually:
    echo    pip install --user google-generativeai
)

REM Create user's local bin directory in AppData
set LOCAL_BIN=%APPDATA%\ask-cli
set SCRIPTS_DIR=%APPDATA%\Python\Scripts

REM Create directories
if not exist "%LOCAL_BIN%" mkdir "%LOCAL_BIN%"
if not exist "%SCRIPTS_DIR%" mkdir "%SCRIPTS_DIR%"

REM Copy files
xcopy /s /e /i /q "src" "%LOCAL_BIN%\src"

REM Create Windows batch file
echo @echo off > "%SCRIPTS_DIR%\ask.bat"
echo python "%LOCAL_BIN%\ask" %%* >> "%SCRIPTS_DIR%\ask.bat"

REM Create Python wrapper script (simplified for batch)
copy "ask" "%LOCAL_BIN%\ask" >nul

REM Clean up the cloned repository
echo Cleaning up...
cd /d %TEMP%
rmdir /s /q "%INSTALL_DIR%"

echo.
echo Installation complete!
echo.
echo Quick start:
echo    ask how to list files
echo.
echo Installed to: %LOCAL_BIN%
echo Config: %USERPROFILE%\.ask_config.json (created on first use)
echo.
echo Help: ask --help
echo.
echo Note: You may need to restart your command prompt for PATH changes to take effect.
