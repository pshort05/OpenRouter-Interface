# OpenRouter Prompt Runner - Setup Guide

This guide provides detailed instructions for setting up the OpenRouter Prompt Runner tools on your system. Choose from automated setup or manual installation methods.

## 🚀 Quick Start (Recommended)

### Automated Setup Script

The easiest way to install everything is using the automated setup script:

```bash
# 1. Download or clone the project files
# 2. Make the setup script executable
chmod +x setup_prompt_runner.sh

# 3. Run the automated setup
./setup_prompt_runner.sh

# 4. Follow the post-installation instructions
```

**What the setup script does:**
- ✅ Checks for Python 3 installation
- ✅ Installs required packages (`requests`, `pyyaml`, `flask`)
- ✅ Makes Python files executable
- ✅ Copies all files to `~/.local/bin` for system-wide access
- ✅ Verifies the installation works

---

## 📋 Manual Setup Instructions

### Prerequisites

#### 1. Python 3 Installation

**Check if Python 3 is installed:**
```bash
python3 --version
# or
python --version
```

**Install Python 3 if needed:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-pip
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip
```

**macOS:**
```bash
# Using Homebrew
brew install python3

# Or download from python.org
# https://www.python.org/downloads/
```

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Or install via Microsoft Store
- Or use Windows Subsystem for Linux (WSL)

#### 2. Required Python Packages

**Install using pip:**
```bash
# Using pip3 (preferred)
pip3 install --user requests pyyaml flask

# Or using python3 -m pip
python3 -m pip install --user requests pyyaml flask

# Or without --user for system-wide installation (may require sudo)
sudo pip3 install requests pyyaml flask
```

**Package descriptions:**
- **`requests`**: HTTP client for OpenRouter API calls
- **`pyyaml`**: YAML configuration file handling
- **`flask`**: Web framework for the web interface

### Required Files

Ensure you have all the necessary Python modules in your project directory:

#### Core Files (Required)
```
prompt_runner.py                    # CLI interface
prompt_runner_flask.py              # Web interface
config_manager.py                   # Configuration management
logging_manager.py                  # Logging setup
prompt_scanner.py                   # JSON prompt discovery
prompt_handler.py                   # Prompt processing
input_handler.py                    # Input file handling
prompt_runner_api_client.py         # OpenRouter API client
response_handler.py                 # Output handling
file_handler.py                     # File operations
```

#### Optional Files
```
create_templates.py                 # Web template generator
prompt_runner_flask.sh             # Flask launcher script
setup_prompt_runner.sh             # This setup script
```

### Manual Installation Steps

#### 1. Make Python Files Executable
```bash
chmod +x prompt_runner.py
chmod +x prompt_runner_flask.py
chmod +x create_templates.py
chmod +x prompt_runner_flask.sh  # if present
```

#### 2. Create Installation Directory
```bash
mkdir -p ~/.local/bin
```

#### 3. Copy Files to System PATH
```bash
# Copy all Python files
cp *.py ~/.local/bin/

# Copy shell script (if present)
cp prompt_runner_flask.sh ~/.local/bin/
```

#### 4. Add to PATH (if needed)
```bash
# Check if ~/.local/bin is in PATH
echo $PATH | grep -q "$HOME/.local/bin" && echo "Already in PATH" || echo "Not in PATH"

# Add to PATH permanently
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# For other shells:
# ~/.zshrc for zsh
# ~/.profile for general shell
```

---

## 🔑 API Key Configuration

### Set OpenRouter API Key

**Get your API key:**
1. Sign up at [OpenRouter.ai](https://openrouter.ai/)
2. Go to your account settings
3. Generate an API key

**Set the environment variable:**

**Linux/macOS (Bash):**
```bash
# Temporary (current session only)
export OPENROUTER_API_KEY="your_api_key_here"

# Permanent (add to ~/.bashrc)
echo 'export OPENROUTER_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**Linux/macOS (Zsh):**
```bash
echo 'export OPENROUTER_API_KEY="your_api_key_here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (Command Prompt):**
```cmd
setx OPENROUTER_API_KEY "your_api_key_here"
```

**Windows (PowerShell):**
```powershell
[Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "your_api_key_here", "User")
```

### Alternative: Configuration File

You can also add the API key to configuration files (not recommended for security):

**CLI Config (`openrouter_editor.yaml`):**
```yaml
api_key: your_api_key_here  # Not recommended
model: anthropic/claude-4-sonnet-20250522
temperature: 0.8
max_tokens: 25000
```

**Web Config (`flask_config.yaml`):**
```yaml
api_key: your_api_key_here  # Not recommended
model: anthropic/claude-4-sonnet-20250522
temperature: 0.8
max_tokens: 10000
```

---

## ✅ Verification

### Test CLI Installation
```bash
# Check if prompt_runner is accessible
prompt_runner.py --help

# Test with a simple command
prompt_runner.py --check  # if available
```

### Test Web Interface Installation
```bash
# Check if Flask app is accessible
prompt_runner_flask.py --help

# Or using the shell script
prompt_runner_flask.sh --check
```

### Test Python Dependencies
```bash
# Test import of required packages
python3 -c "import requests, yaml, flask; print('All dependencies OK')"
```

### Test API Key
```bash
# Check if API key is set
echo $OPENROUTER_API_KEY

# Should output your API key (partially masked for security)
```

---

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### 1. "Command not found" Errors

**Problem:** `prompt_runner.py: command not found`

**Solutions:**
```bash
# Check if files are in ~/.local/bin
ls -la ~/.local/bin/prompt_runner*

# Check if ~/.local/bin is in PATH
echo $PATH | grep -q "$HOME/.local/bin" && echo "In PATH" || echo "Not in PATH"

# Add to PATH if missing
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or run with full path
~/.local/bin/prompt_runner.py --help
```

#### 2. Python Import Errors

**Problem:** `ModuleNotFoundError: No module named 'requests'`

**Solutions:**
```bash
# Install missing packages
pip3 install --user requests pyyaml flask

# Or try system-wide installation
sudo pip3 install requests pyyaml flask

# Check Python package location
python3 -c "import sys; print(sys.path)"
```

#### 3. Permission Errors

**Problem:** `Permission denied`

**Solutions:**
```bash
# Make files executable
chmod +x ~/.local/bin/prompt_runner.py
chmod +x ~/.local/bin/prompt_runner_flask.py

# Check file permissions
ls -la ~/.local/bin/prompt_runner*
```

#### 4. API Key Issues

**Problem:** `API key not found`

**Solutions:**
```bash
# Verify API key is set
echo $OPENROUTER_API_KEY

# Re-export API key
export OPENROUTER_API_KEY="your_api_key_here"

# Check if it's in your shell config
grep OPENROUTER_API_KEY ~/.bashrc ~/.zshrc ~/.profile
```

#### 5. Python Version Issues

**Problem:** `python3: command not found`

**Solutions:**
```bash
# Check available Python commands
which python
which python3
python --version
python3 --version

# Install Python 3 if missing (see prerequisites section)

# Create alias if needed
echo 'alias python=python3' >> ~/.bashrc
```

### Debug Mode

**Enable verbose output for troubleshooting:**
```bash
# CLI with debug logging
prompt_runner.py -v -l debug.log -p test.json -i input.md

# Web interface in debug mode
prompt_runner_flask.sh --debug

# Check logs
tail -f debug.log
```

---

## 🔧 Advanced Configuration

### Custom Installation Directory

**Install to a different directory:**
```bash
# Set custom directory
CUSTOM_DIR="/usr/local/bin"  # or any directory in PATH

# Copy files
sudo cp *.py "$CUSTOM_DIR/"
sudo chmod +x "$CUSTOM_DIR"/prompt_runner*.py
```

### Development Setup

**For development and testing:**
```bash
# Clone/download to a development directory
git clone [repository] ~/dev/prompt_runner
cd ~/dev/prompt_runner

# Install in development mode (creates symlinks)
ln -s "$(pwd)/prompt_runner.py" ~/.local/bin/
ln -s "$(pwd)/prompt_runner_flask.py" ~/.local/bin/

# Install packages in development mode
pip3 install --user -e .  # if setup.py exists
```

### Virtual Environment Setup

**For isolated package installation:**
```bash
# Create virtual environment
python3 -m venv prompt_runner_env

# Activate virtual environment
source prompt_runner_env/bin/activate

# Install packages
pip install requests pyyaml flask

# Deactivate when done
deactivate
```

---

## 📦 Distribution-Specific Notes

### Ubuntu/Debian
```bash
# Update package index
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Install system packages if needed
sudo apt install python3-requests python3-yaml python3-flask
```

### CentOS/RHEL
```bash
# Enable EPEL repository (for additional packages)
sudo yum install epel-release

# Install Python and pip
sudo yum install python3 python3-pip

# Or on newer versions
sudo dnf install python3 python3-pip
```

### macOS
```bash
# Using Homebrew (recommended)
brew install python3

# Packages install automatically with pip3
pip3 install --user requests pyyaml flask
```

### Windows (WSL)
```bash
# Update WSL
sudo apt update && sudo apt upgrade

# Install Python (usually pre-installed)
sudo apt install python3 python3-pip

# Follow Linux instructions from here
```

---

## 🆘 Getting Help

### Documentation
- **Main README**: [README.md](README.md) - Overview and usage
- **This Guide**: Complete setup instructions
- **CLI Help**: `prompt_runner.py --help`
- **Web Help**: `prompt_runner_flask.sh --help`

### Common Commands
```bash
# Setup script help
./setup_prompt_runner.sh --help

# Check system requirements
./setup_prompt_runner.sh  # runs full setup with checks

# Test installation
prompt_runner.py --help
prompt_runner_flask.py --help
```

### Support Resources
1. **Check prerequisites**: Ensure Python 3 and pip are installed
2. **Review error messages**: Most errors include specific solutions
3. **Test dependencies**: Verify all Python packages are installed
4. **Check file permissions**: Ensure scripts are executable
5. **Verify API key**: Confirm OpenRouter API key is set correctly

---

**Setup Complete!** 🎉

After successful setup, return to the [main README](README.md) for usage instructions and examples.