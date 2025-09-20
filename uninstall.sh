#!/bin/bash

# Uninstaller for 'ask' command

echo "Uninstalling Ask CLI..."

# Remove the CLI wrapper
if [ -f ~/.local/bin/ask ]; then
    rm ~/.local/bin/ask
    echo "✓ Removed CLI wrapper: ~/.local/bin/ask"
else
    echo "  CLI wrapper not found: ~/.local/bin/ask"
fi

# Remove the installation directory
if [ -d ~/.ask-cli ]; then
    rm -rf ~/.ask-cli
    echo "✓ Removed installation: ~/.ask-cli/"
else
    echo "  Installation directory not found: ~/.ask-cli/"
fi

# Remove old installation if it exists
if [ -d ~/.local/bin/ask-src ]; then
    rm -rf ~/.local/bin/ask-src
    echo "✓ Removed old installation: ~/.local/bin/ask-src/"
fi

# Note about PATH
echo ""
echo "Note: PATH modifications in ~/.bashrc or ~/.zshrc were left unchanged."
echo "You can manually remove this line if desired:"
echo '   export PATH="$HOME/.local/bin:$PATH"'
echo ""
echo "Ask CLI has been uninstalled successfully!"