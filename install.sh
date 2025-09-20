#!/bin/bash

# Advanced installer for 'ask' command with virtual environment

echo "Installing 'ask' command..."

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "Error: Python 3 required. Install from python.org"
    exit 1
fi

# Check if git is available
if ! command -v git &>/dev/null; then
    echo "Error: Git is required for installation"
    exit 1
fi

# Define installation directories
INSTALL_DIR="$HOME/.ask-cli"
TEMP_DIR="/tmp/ask-cli-install-$$"

echo "Setting up Ask CLI in $INSTALL_DIR..."

# Remove existing installation if it exists
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing existing installation..."
    rm -rf "$INSTALL_DIR"
fi

# Create temporary directory for cloning
mkdir -p "$TEMP_DIR"

# Clone the repository to temporary location
echo "Downloading Ask CLI..."
if ! git clone https://github.com/sjdpk/ask-cli.git "$TEMP_DIR" &>/dev/null; then
    echo "Error: Failed to clone repository"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Check if required files exist
if [ ! -f "$TEMP_DIR/ask" ] || [ ! -d "$TEMP_DIR/src" ]; then
    echo "Error: Required files not found in repository"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Create the installation directory
mkdir -p "$INSTALL_DIR"

# Copy source files
echo "Installing source files..."
cp -r "$TEMP_DIR/src" "$INSTALL_DIR/"

# Create virtual environment
echo "Creating isolated Python environment..."
if ! python3 -m venv "$INSTALL_DIR/venv" &>/dev/null; then
    echo "Error: Failed to create virtual environment"
    echo "Make sure python3-venv is installed:"
    echo "  Ubuntu/Debian: sudo apt install python3-venv"
    echo "  macOS: Should be included with Python 3"
    rm -rf "$INSTALL_DIR" "$TEMP_DIR"
    exit 1
fi

# Install dependencies in virtual environment
echo "Installing dependencies..."
if ! "$INSTALL_DIR/venv/bin/pip" install google-generativeai &>/dev/null; then
    echo "Warning: Failed to install google-generativeai"
    echo "You may need to install it manually later:"
    echo "  $INSTALL_DIR/venv/bin/pip install google-generativeai"
fi

# Create user's local bin directory
mkdir -p ~/.local/bin

# Create the wrapper script
echo "Creating CLI wrapper..."
cat > ~/.local/bin/ask << 'EOF'
#!/bin/bash
# Ask CLI wrapper script - activates virtual environment and runs the CLI

# Define paths
ASK_CLI_DIR="$HOME/.ask-cli"
VENV_PYTHON="$ASK_CLI_DIR/venv/bin/python"
SRC_DIR="$ASK_CLI_DIR/src"

# Check if installation exists
if [ ! -f "$VENV_PYTHON" ] || [ ! -d "$SRC_DIR" ]; then
    echo "➜ Ask CLI installation not found or corrupted."
    echo "   Please reinstall using:"
    echo "   curl -sSL https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.sh | bash"
    exit 1
fi

# Suppress Google AI warnings
export GRPC_VERBOSITY=ERROR
export GLOG_minloglevel=2

# Change to source directory and run with virtual environment Python
cd "$SRC_DIR"
exec "$VENV_PYTHON" main.py "$@"
EOF

chmod +x ~/.local/bin/ask

# Clean up temporary directory
rm -rf "$TEMP_DIR"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Adding ~/.local/bin to PATH..."
    
    # Detect shell
    if [[ "$SHELL" == *"zsh"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        echo "   Added to ~/.zshrc"
    elif [[ "$SHELL" == *"bash"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        echo "   Added to ~/.bashrc"
    else
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        echo "   Added to ~/.bashrc"
    fi
    
    export PATH="$HOME/.local/bin:$PATH"
    
    echo ""
    echo "Installation complete!"
    echo ""
    echo "IMPORTANT: Restart your terminal or run:"
    echo "   source ~/.bashrc  (or ~/.zshrc)"
    echo ""
else
    echo ""
    echo "Installation complete!"
    echo ""
fi

echo "Quick start:"
echo "   ask how to list files"
echo ""
echo "Installation details:"
echo "   CLI wrapper: ~/.local/bin/ask"
echo "   Source code: ~/.ask-cli/src/"
echo "   Virtual env: ~/.ask-cli/venv/"
echo "   Config: ~/.ask_config.json (created on first use)"
echo ""
echo "To uninstall:"
echo "   rm ~/.local/bin/ask && rm -rf ~/.ask-cli"
echo ""
echo "Help: ask --help"