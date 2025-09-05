#!/bin/bash

# Cross-platform installer for 'ask' command (Unix-like systems)

echo "Installing 'ask' command..."

# Detect OS
OS_NAME=$(uname -s)
case "$OS_NAME" in
    Darwin)
        echo "✓ Detected macOS"
        ;;
    Linux)
        echo "✓ Detected Linux"
        ;;
    *)
        echo "⚠️  Detected $OS_NAME (experimental support)"
        ;;
esac

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

# Clone repository to hidden folder
INSTALL_DIR="$HOME/.ask-cli-install"
echo "Cloning repository to $INSTALL_DIR..."

# Remove existing installation directory if it exists
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
fi

# Clone the repository
if ! git clone https://github.com/sjdpk/ask-cli.git "$INSTALL_DIR" &>/dev/null; then
    echo "Error: Failed to clone repository"
    exit 1
fi

# Change to the cloned directory
cd "$INSTALL_DIR"

echo "Repository cloned successfully"

# Check if ask script exists
if [ ! -f "ask" ]; then
    echo "Error: ask script not found in repository"
    exit 1
fi

# Check if src directory exists
if [ ! -d "src" ]; then
    echo "Error: src directory not found in repository"
    exit 1
fi

# Install Python package
echo "Installing dependencies..."
if python3 -m pip install --user -q google-generativeai 2>/dev/null; then
    echo "✓ Dependencies installed successfully"
else
    echo "⚠️  Dependency installation failed. You may need to install manually:"
    echo "   pip3 install --user google-generativeai"
    echo "   or: python3 -m pip install --user google-generativeai"
fi

# Create user's local bin directory
mkdir -p ~/.local/bin

# Copy files
echo "Installing files..."
cp -r src ~/.local/bin/ask-src
cp ask ~/.local/bin/ask
chmod +x ~/.local/bin/ask
echo "✓ Files installed to ~/.local/bin/"

# Clean up the cloned repository
echo "Cleaning up..."
cd /
rm -rf "$INSTALL_DIR"

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
    echo "✅ Installation complete!"
    echo ""
    echo "IMPORTANT: Restart your terminal or run:"
    echo "   source ~/.bashrc  (or ~/.zshrc for zsh)"
    echo ""
else
    echo ""
    echo "✅ Installation complete!"
    echo ""
fi

echo "Quick start:"
echo "   ask how to list files"
echo ""
echo "Installed to: ~/.local/bin/ask"
echo "Config: ~/.ask_config.json (created on first use)"
echo ""
echo "Platform: $OS_NAME"
echo "Help: ask --help"