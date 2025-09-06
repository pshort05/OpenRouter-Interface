#!/bin/bash

# OpenRouter Prompt Runner Setup Script
# Installs and configures the OpenRouter Prompt Runner tools for system-wide use

set -e  # Exit on any error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/bin"
REQUIREMENTS=("requests" "pyyaml" "flask")

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    shift
    echo -e "${color}$*${NC}"
}

# Function to print section headers
print_header() {
    echo
    print_color $CYAN "========================================="
    print_color $CYAN "$1"
    print_color $CYAN "========================================="
}

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to check Python installation
check_python() {
    print_header "Checking Python Installation"
    
    local python_cmd=""
    local python_version=""
    
    # Check for python3 first (preferred)
    if command_exists python3; then
        python_cmd="python3"
        python_version=$(python3 --version 2>&1)
        print_color $GREEN "✓ Found python3: $python_version"
    elif command_exists python; then
        # Check if python is actually Python 3
        local version=$(python --version 2>&1)
        if echo "$version" | grep -q "Python 3"; then
            python_cmd="python"
            python_version="$version"
            print_color $GREEN "✓ Found python (Python 3): $python_version"
        else
            print_color $RED "✗ Found python but it's Python 2: $version"
            python_cmd=""
        fi
    fi
    
    if [ -z "$python_cmd" ]; then
        print_color $RED "Error: Python 3 is not installed or not found in PATH"
        print_color $YELLOW "Please install Python 3 first:"
        print_color $BLUE "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
        print_color $BLUE "  CentOS/RHEL:   sudo yum install python3 python3-pip"
        print_color $BLUE "  Fedora:        sudo dnf install python3 python3-pip"
        print_color $BLUE "  macOS:         brew install python3"
        print_color $BLUE "  Or download from: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Check pip3
    if command_exists pip3; then
        print_color $GREEN "✓ Found pip3"
    elif command_exists pip && python3 -m pip --version &>/dev/null; then
        print_color $GREEN "✓ Found pip (accessible via python3 -m pip)"
    else
        print_color $RED "Error: pip3 is not installed"
        print_color $YELLOW "Please install pip3:"
        print_color $BLUE "  Ubuntu/Debian: sudo apt install python3-pip"
        print_color $BLUE "  CentOS/RHEL:   sudo yum install python3-pip"
        print_color $BLUE "  Fedora:        sudo dnf install python3-pip"
        print_color $BLUE "  macOS:         python3 -m ensurepip --upgrade"
        exit 1
    fi
    
    return 0
}

# Function to install Python requirements
install_requirements() {
    print_header "Installing Python Requirements"
    
    print_color $BLUE "Installing required packages: ${REQUIREMENTS[*]}"
    
    # Try pip3 first, then fall back to python3 -m pip
    local pip_cmd=""
    if command_exists pip3; then
        pip_cmd="pip3"
    else
        pip_cmd="python3 -m pip"
    fi
    
    # Install each requirement
    for package in "${REQUIREMENTS[@]}"; do
        print_color $BLUE "Installing $package..."
        if $pip_cmd install --user "$package"; then
            print_color $GREEN "✓ Successfully installed $package"
        else
            print_color $RED "✗ Failed to install $package"
            print_color $YELLOW "You may need to install it manually:"
            print_color $BLUE "  $pip_cmd install --user $package"
            exit 1
        fi
    done
    
    print_color $GREEN "✓ All requirements installed successfully"
}

# Function to verify required files exist
check_required_files() {
    print_header "Checking Required Files"
    
    # List of required Python files
    local required_files=(
        "prompt_runner.py"
        "prompt_runner_flask.py"
        "config_manager.py"
        "logging_manager.py"
        "prompt_scanner.py"
        "prompt_handler.py"
        "input_handler.py"
        "prompt_runner_api_client.py"
        "response_handler.py"
        "file_handler.py"
    )
    
    # Optional files (warn if missing but don't fail)
    local optional_files=(
        "create_templates.py"
        "prompt_runner_flask.sh"
    )
    
    local missing_files=()
    
    # Check required files
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_color $GREEN "✓ Found $file"
        else
            print_color $RED "✗ Missing required file: $file"
            missing_files+=("$file")
        fi
    done
    
    # Check optional files
    for file in "${optional_files[@]}"; do
        if [ -f "$file" ]; then
            print_color $GREEN "✓ Found $file (optional)"
        else
            print_color $YELLOW "◦ Optional file not found: $file"
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        print_color $RED "Error: Missing required files: ${missing_files[*]}"
        print_color $YELLOW "Please ensure all required Python modules are in the current directory"
        exit 1
    fi
    
    return 0
}

# Function to make Python files executable
make_executable() {
    print_header "Making Python Files Executable"
    
    # List of main Python files to make executable
    local main_files=(
        "prompt_runner.py"
        "prompt_runner_flask.py"
        "create_templates.py"
    )
    
    for file in "${main_files[@]}"; do
        if [ -f "$file" ]; then
            chmod +x "$file"
            print_color $GREEN "✓ Made $file executable"
        else
            print_color $YELLOW "◦ File not found (skipping): $file"
        fi
    done
    
    # Make the shell script executable too
    if [ -f "prompt_runner_flask.sh" ]; then
        chmod +x "prompt_runner_flask.sh"
        print_color $GREEN "✓ Made prompt_runner_flask.sh executable"
    fi
}

# Function to create install directory
create_install_dir() {
    print_header "Creating Installation Directory"
    
    if [ ! -d "$INSTALL_DIR" ]; then
        mkdir -p "$INSTALL_DIR"
        print_color $GREEN "✓ Created directory: $INSTALL_DIR"
    else
        print_color $GREEN "✓ Directory already exists: $INSTALL_DIR"
    fi
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
        print_color $YELLOW "Warning: $INSTALL_DIR is not in your PATH"
        print_color $BLUE "Add the following line to your ~/.bashrc or ~/.profile:"
        print_color $CYAN "export PATH=\"\$HOME/.local/bin:\$PATH\""
        print_color $BLUE "Then run: source ~/.bashrc"
    else
        print_color $GREEN "✓ $INSTALL_DIR is already in PATH"
    fi
}

# Function to copy files to install directory
copy_files() {
    print_header "Installing Files to $INSTALL_DIR"
    
    # List of all Python files to copy
    local python_files=(
        "prompt_runner.py"
        "prompt_runner_flask.py"
        "config_manager.py"
        "logging_manager.py"
        "prompt_scanner.py"
        "prompt_handler.py"
        "input_handler.py"
        "prompt_runner_api_client.py"
        "response_handler.py"
        "file_handler.py"
        "create_templates.py"
    )
    
    # Copy Python files
    for file in "${python_files[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$INSTALL_DIR/"
            print_color $GREEN "✓ Copied $file to $INSTALL_DIR"
        else
            print_color $YELLOW "◦ File not found (skipping): $file"
        fi
    done
    
    # Copy shell script
    if [ -f "prompt_runner_flask.sh" ]; then
        cp "prompt_runner_flask.sh" "$INSTALL_DIR/"
        print_color $GREEN "✓ Copied prompt_runner_flask.sh to $INSTALL_DIR"
    fi
    
    print_color $GREEN "✓ All files copied successfully"
}

# Function to verify installation
verify_installation() {
    print_header "Verifying Installation"
    
    # Check if files exist in install directory
    local main_files=("prompt_runner.py" "prompt_runner_flask.py")
    
    for file in "${main_files[@]}"; do
        if [ -f "$INSTALL_DIR/$file" ]; then
            print_color $GREEN "✓ $file installed correctly"
        else
            print_color $RED "✗ $file not found in $INSTALL_DIR"
        fi
    done
    
    # Test if Python can import the modules
    print_color $BLUE "Testing Python module imports..."
    
    # Change to install directory and test imports
    if (cd "$INSTALL_DIR" && python3 -c "
import sys
try:
    import requests, yaml
    print('✓ Python dependencies working')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"); then
        print_color $GREEN "✓ Python dependencies are working"
    else
        print_color $RED "✗ Python dependency test failed"
    fi
}

# Function to show post-installation instructions
show_instructions() {
    print_header "Installation Complete!"
    
    print_color $GREEN "✓ OpenRouter Prompt Runner has been installed successfully"
    echo
    print_color $CYAN "Next Steps:"
    print_color $BLUE "1. Set your OpenRouter API key:"
    print_color $YELLOW "   export OPENROUTER_API_KEY=\"your_api_key_here\""
    print_color $BLUE "   (Add this to ~/.bashrc for persistence)"
    echo
    print_color $BLUE "2. If ~/.local/bin is not in your PATH, add it:"
    print_color $YELLOW "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
    print_color $YELLOW "   source ~/.bashrc"
    echo
    print_color $CYAN "Usage:"
    print_color $BLUE "• Command Line Interface:"
    print_color $YELLOW "  prompt_runner.py -p analysis.json -i document.md"
    print_color $YELLOW "  prompt_runner.py --help"
    echo
    print_color $BLUE "• Web Interface:"
    print_color $YELLOW "  prompt_runner_flask.py"
    print_color $YELLOW "  prompt_runner_flask.sh --setup"
    print_color $YELLOW "  prompt_runner_flask.sh --production"
    echo
    print_color $CYAN "Files installed to: $INSTALL_DIR"
    print_color $CYAN "Configuration files will be created in your working directory"
    echo
    print_color $GREEN "Happy prompting! 🎉"
}

# Main installation function
main() {
    print_color $CYAN "OpenRouter Prompt Runner Setup Script"
    print_color $CYAN "====================================="
    echo
    print_color $BLUE "This script will install the OpenRouter Prompt Runner tools"
    print_color $BLUE "Installation directory: $INSTALL_DIR"
    echo
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Run installation steps
    check_python
    check_required_files
    install_requirements
    make_executable
    create_install_dir
    copy_files
    verify_installation
    show_instructions
    
    print_color $GREEN "Setup completed successfully!"
}

# Function to show help
show_help() {
    cat << EOF
OpenRouter Prompt Runner Setup Script

This script installs the OpenRouter Prompt Runner tools for system-wide use.

What it does:
1. Checks for Python 3 installation
2. Installs required Python packages (requests, pyyaml, flask)
3. Makes main Python files executable
4. Copies all files to ~/.local/bin for system-wide access
5. Verifies the installation

Requirements:
- Python 3.x
- pip3 (Python package installer)
- Internet connection (for package installation)

Usage:
    setup_prompt_runner.sh [OPTIONS]

Options:
    -h, --help    Show this help message
    
Files that will be installed:
- prompt_runner.py (CLI interface)
- prompt_runner_flask.py (Web interface)
- All supporting Python modules
- prompt_runner_flask.sh (Flask launcher script)

After installation, you can run the tools from anywhere:
    prompt_runner.py --help
    prompt_runner_flask.sh --setup

EOF
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac