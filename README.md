# Ask CLI

**Instant terminal commands powered by AI**

Transform natural language into terminal commands instantly.

```bash
$ ask how to list all files
→ ls -la

$ ask find large files over 100MB
→ find . -type f -size +100M

$ ask compress this folder
→ tar -czf archive.tar.gz .
```

## Installation

### Quick Install

**Cross-Platform (Python):**
```bash
# Auto-detect platform and install
python3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.py').read())"
```

**macOS/Linux:**
```bash
# Download and install
curl -sSL https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
# Download and install
iwr -useb https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.ps1 | iex
```

**Windows (Command Prompt):**
```cmd
# Download and run installer
curl -L https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.bat -o install.bat && install.bat
```

### Manual Install

**All Platforms:**
```bash
# Clone repo
git clone https://github.com/sjdpk/ask-cli.git
cd ask-cli

# Run installer
# On Windows: .\install.ps1 or install.bat
# On macOS/Linux: ./install.sh
```

## Usage

```bash
ask <what you want to do>
```

### Examples

**macOS/Linux:**
```bash
ask list all files                    # → ls -la
ask check disk space                  # → df -h
ask find text in files                # → grep -r "text" .
ask kill process on port 3000         # → lsof -ti:3000 | xargs kill -9
ask compress folder                   # → tar -czf archive.tar.gz folder
```

**Windows:**
```cmd
ask list all files                    # → dir
ask check disk space                  # → dir
ask find text in files                # → findstr /s "text" *.*
ask kill process on port 3000         # → netstat -ano | findstr :3000
ask compress folder                   # → powershell Compress-Archive -Path . -DestinationPath archive.zip
```

### Additional Commands

```bash
ask --help      # Show help information
ask --reset     # Reset your API key
ask --update    # Update to the latest version
```

## Cross-Platform Support

Ask CLI works seamlessly across **Windows**, **macOS**, and **Linux**. It automatically detects your operating system and provides platform-appropriate commands.

### Supported Platforms

| Platform | Support | Installer |
|----------|---------|-----------|
| **macOS** | ✅ Full | `install.sh` |
| **Linux** | ✅ Full | `install.sh` |
| **Windows** | ✅ Full | `install.ps1` / `install.bat` |

### Platform-Specific Features

- **Automatic OS Detection**: Commands are tailored to your operating system
- **Cross-Platform Update**: `ask --update` works on all platforms
- **Native Command Generation**: Get Windows CMD/PowerShell or Unix shell commands
- **Safe Path Handling**: Proper file path handling for each platform

### Installation Locations

| Platform | Installation Path | Config File |
|----------|------------------|-------------|
| **macOS/Linux** | `~/.local/bin/ask` | `~/.ask_config.json` |
| **Windows** | `%APPDATA%\ask-cli\` | `%USERPROFILE%\.ask_config.json` |

## Setup

1. **Get a free API key** from Google AI Studio: https://makersuite.google.com/app/apikey
2. **Run the ask command**: `ask list files`
3. **Enter your API key** when prompted

That's it!

## Updating

Keep your Ask CLI up to date with the latest features and improvements:

```bash
ask --update
```

This command will automatically download and install the latest version from GitHub while preserving your configuration.

## License

MIT License
