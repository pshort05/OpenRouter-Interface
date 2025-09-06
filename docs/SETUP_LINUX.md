# Linux Setup Script Documentation

## Overview

The `setup_linux.sh` script provides comprehensive, one-command setup for all OpenRouter Interface tools on Linux systems. It handles everything from dependency verification to PATH configuration.

## Features

### ✅ Complete Environment Setup
- **Python Verification**: Checks for Python 3.7+ installation
- **Dependency Management**: Installs all required packages from requirements.txt
- **Permission Handling**: Makes all entry point scripts executable
- **Path Integration**: Copies modules to user or system PATH
- **Verification**: Tests installation and provides troubleshooting

### 🎯 Two Installation Modes

#### User Installation (Default)
```bash
./setup_linux.sh
```
- Installs to `~/.local/bin`
- No sudo required
- User-specific installation

#### System Installation
```bash
./setup_linux.sh --system
```
- Installs to `/usr/local/bin`
- Requires sudo privileges
- System-wide availability

## What Gets Installed

### Entry Point Scripts (Made Executable)
- `prompt_runner.py` - Main CLI interface
- `prompt_chain_runner.py` - Advanced chain processing
- `multi_file_prompt_runner.py` - Multi-file processing
- `prompt_runner_flask.py` - Web interface
- `openrouter_editor.py` - Legacy editor
- `generateProse.py` - Prose generation
- `bookGen.py` - Book generation
- `callAPI.py` - Basic API caller

### Support Modules
- `config_manager.py` - Configuration handling
- `logging_manager.py` - Logging system
- `prompt_scanner.py` - Prompt discovery
- `prompt_handler.py` - Prompt processing
- `input_handler.py` - File handling
- `prompt_runner_api_client.py` - API client
- `response_handler.py` - Response processing
- `file_handler.py` - File utilities
- And all other supporting modules

### Shell Scripts
- `prompt_runner_flask.sh` - Flask launcher
- `setup_prompt_runner.sh` - Legacy setup

## Usage Examples

### Basic User Installation
```bash
# Download the project
git clone <repository> && cd <directory>

# Run setup
chmod +x setup_linux.sh
./setup_linux.sh

# Add to PATH (if not already done)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Set API key
export OPENROUTER_API_KEY="your_api_key_here"

# Start using
prompt_runner.py --help
```

### System-Wide Installation
```bash
# Requires sudo for /usr/local/bin installation
./setup_linux.sh --system

# PATH typically already configured for /usr/local/bin
# Set API key
export OPENROUTER_API_KEY="your_api_key_here"

# Available system-wide
prompt_runner.py --help
```

## Post-Installation

### PATH Configuration
The script provides specific instructions for your installation:

**User Installation (`~/.local/bin`):**
```bash
export PATH="$HOME/.local/bin:$PATH"
# Add to ~/.bashrc for persistence
```

**System Installation (`/usr/local/bin`):**
- Usually already in PATH
- No additional configuration needed

### API Key Setup
```bash
# Set for current session
export OPENROUTER_API_KEY="your_api_key_here"

# Make permanent
echo 'export OPENROUTER_API_KEY="your_api_key_here"' >> ~/.bashrc
```

### Verification
```bash
# Test basic functionality
prompt_runner.py --help
prompt_chain_runner.py --help
multi_file_prompt_runner.py --help

# Test web interface
prompt_runner_flask.py
```

## Troubleshooting

### Externally-Managed Environment Error
**Modern Linux distributions (Ubuntu 22.04+, Debian 12+) protect the system Python:**
```
error: externally-managed-environment
```

**The setup script handles this automatically by:**
- Using `--user` flag for user installations
- Falling back to system packages (python3-requests, python3-yaml, python3-flask)
- Using `--break-system-packages` only when necessary

**Manual alternatives:**
```bash
# Option 1: Install system packages directly
sudo apt install python3-requests python3-yaml python3-flask

# Option 2: Use virtual environment
python3 -m venv openrouter-env
source openrouter-env/bin/activate
pip install requests pyyaml flask

# Option 3: Use pipx (if available)
pipx install requests pyyaml flask
```

### Python Issues
```bash
# Check Python version
python3 --version

# Install Python if needed
sudo apt install python3 python3-pip  # Ubuntu/Debian
sudo yum install python3 python3-pip  # CentOS/RHEL
```

### Permission Issues
```bash
# For user installation
mkdir -p ~/.local/bin

# For system installation
sudo mkdir -p /usr/local/bin
```

### PATH Issues
```bash
# Check current PATH
echo $PATH

# Add to PATH temporarily
export PATH="$HOME/.local/bin:$PATH"

# Check if script is found
which prompt_runner.py
```

### Package Installation Issues
```bash
# Update package lists first
sudo apt update  # Ubuntu/Debian

# Install pip if missing
sudo apt install python3-pip

# Manual package install
pip3 install --user requests pyyaml flask
```

## Advanced Usage

### Custom Installation Directory
The script supports standard directories, but you can modify the `INSTALL_DIR` variable for custom locations.

### Selective Installation
Modify the `PYTHON_MODULES` and `ENTRY_POINTS` arrays in the script to install only specific components.

### Development Setup
For development, consider using the user installation mode and symlinking instead of copying:
```bash
# After running setup_linux.sh
cd ~/.local/bin
ln -sf /path/to/dev/prompt_runner.py ./
```

## Requirements

### System Requirements
- Linux/Unix system with bash
- Python 3.7 or higher
- pip (python package installer)
- Internet connection for package downloads

### Privileges
- **User installation**: No special privileges needed
- **System installation**: sudo access required

The setup script is designed to be self-contained and doesn't require any additional programs beyond the standard Linux environment.