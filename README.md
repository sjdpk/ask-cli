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

```bash
# Download and install
curl -sSL https://raw.githubusercontent.com/sjdpk/ask-cli/main/install.sh | bash
```

### Manual Install

```bash
# Clone repo
git clone https://github.com/sjdpk/ask-cli.git
cd ask-cli

# Run installer
./install.sh
```

## Usage

```bash
ask <what you want to do>
```

### Examples

```bash
ask list all files                    # → ls -la
ask check disk space                  # → df -h
ask find text in files                # → grep -r "text" .
ask kill process on port 3000         # → lsof -ti:3000 | xargs kill -9
ask compress folder                   # → tar -czf archive.tar.gz folder
```

### Additional Commands

```bash
ask --help      # Show help information
ask --reset     # Reset your API key
```

## Setup

1. **Get a free API key** from Google AI Studio: https://makersuite.google.com/app/apikey
2. **Run the ask command**: `ask list files`
3. **Enter your API key** when prompted

That's it!

## License

MIT License
