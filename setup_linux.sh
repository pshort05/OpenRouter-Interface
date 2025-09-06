#!/bin/bash

# OpenRouter Interface - Linux Setup Script
# Comprehensive setup for all OpenRouter tools and utilities
# 
# This script:
# 1. Checks for Python 3 installation
# 2. Installs all Python requirements
# 3. Makes all entry point scripts executable
# 4. Copies all modules to user or system PATH
#
# Usage: ./setup_linux.sh [--system]
#   --system    Install to /usr/local/bin (requires sudo)
#   (default)   Install to ~/.local/bin (user installation)

set -e  # Exit on any error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_TO_SYSTEM=false
INSTALL_DIR=""
PYTHON_CMD=""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Entry point scripts that need to be executable
ENTRY_POINTS=(
    "prompt_runner.py"
    "prompt_chain_runner.py"
    "multi_file_prompt_runner.py"
    "prompt_runner_flask.py"
    "openrouter_editor.py"
    "generateProse.py"
    "bookGen.py"
    "callAPI.py"
)

# All Python files that need to be copied
PYTHON_MODULES=(
    "prompt_runner.py"
    "prompt_chain_runner.py"
    "multi_file_prompt_runner.py"
    "prompt_runner_flask.py"
    "config_manager.py"
    "logging_manager.py"
    "prompt_scanner.py"
    "prompt_handler.py"
    "input_handler.py"
    "prompt_runner_api_client.py"
    "response_handler.py"
    "file_handler.py"
    "api_client.py"
    "openrouter_client.py"
    "openrouter_editor.py"
    "openrouter_text_editor.py"
    "generateProse.py"
    "bookGen.py"
    "bookFileManager.py"
    "callAPI.py"
    "create_templates.py"
    "text_chunker.py"
    "prompt_builder.py"
)

# Shell scripts that need to be executable and copied
SHELL_SCRIPTS=(
    "prompt_runner_flask.sh"
    "setup_prompt_runner.sh"
)

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

# Function to print status
print_status() {
    print_color $GREEN "✓ $1"
}

print_warning() {
    print_color $YELLOW "⚠ $1"
}

print_error() {
    print_color $RED "✗ $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to check Python installation
check_python() {
    print_header "Checking Python Installation"
    
    local python_version=""
    
    # Check for python3 first (preferred)
    if command_exists python3; then
        PYTHON_CMD="python3"
        python_version=$(python3 --version 2>&1)
        print_status "Found Python 3: $python_version"
    elif command_exists python; then
        # Check if python is actually Python 3
        python_version=$(python --version 2>&1)
        if [[ "$python_version" == *"Python 3"* ]]; then
            PYTHON_CMD="python"
            print_status "Found Python 3: $python_version"
        else
            print_error "Python 3 is required but not found"
            print_error "Found: $python_version"
            print_error "Please install Python 3.7 or higher"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        print_error "Please install Python 3.7 or higher using your system package manager:"
        echo
        print_color $YELLOW "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
        print_color $YELLOW "  CentOS/RHEL:   sudo yum install python3 python3-pip"
        print_color $YELLOW "  Fedora:        sudo dnf install python3 python3-pip"
        print_color $YELLOW "  Arch Linux:    sudo pacman -S python python-pip"
        echo
        exit 1
    fi
    
    # Check Python version is 3.7+
    local version_check=$($PYTHON_CMD -c "import sys; print(1 if sys.version_info >= (3, 7) else 0)")
    if [ "$version_check" != "1" ]; then
        print_error "Python 3.7 or higher is required"
        print_error "Found: $python_version"
        exit 1
    fi
    
    # Check for pip
    if ! command_exists pip3 && ! command_exists pip; then
        print_error "pip is not installed"
        print_error "Please install pip using your system package manager"
        exit 1
    fi
    
    print_status "Python 3 installation verified"
}

# Function to parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --system)
                INSTALL_TO_SYSTEM=true
                shift
                ;;
            -h|--help)
                cat << EOF
OpenRouter Interface - Linux Setup Script

Usage: $0 [OPTIONS]

OPTIONS:
    --system        Install to /usr/local/bin (requires sudo privileges)
    (default)       Install to ~/.local/bin (user installation)
    -h, --help      Show this help message

DESCRIPTION:
    This script performs a complete setup of the OpenRouter Interface tools:
    
    1. Verifies Python 3.7+ installation
    2. Installs all required Python packages (requests, pyyaml, flask)
    3. Makes all entry point scripts executable
    4. Copies all Python modules to the specified installation directory
    5. Copies shell scripts and makes them executable
    6. Verifies the installation

EXAMPLES:
    $0                    # Install to ~/.local/bin (user installation)
    $0 --system          # Install to /usr/local/bin (system-wide, requires sudo)

AFTER INSTALLATION:
    Make sure the installation directory is in your PATH:
    
    For user installation (~/.local/bin):
        echo 'export PATH="\$HOME/.local/bin:\$PATH"' >> ~/.bashrc
        source ~/.bashrc
    
    For system installation (/usr/local/bin):
        PATH is usually already configured

EOF
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                print_error "Use --help for usage information"
                exit 1
                ;;
        esac
    done
}

# Function to set installation directory
set_install_directory() {
    if [ "$INSTALL_TO_SYSTEM" = true ]; then
        INSTALL_DIR="/usr/local/bin"
        print_header "System Installation Mode"
        print_color $YELLOW "Installing to: $INSTALL_DIR"
        print_color $YELLOW "This requires sudo privileges"
        
        # Check if we need sudo
        if [ "$EUID" -ne 0 ]; then
            print_color $YELLOW "Checking sudo access..."
            if ! sudo -n true 2>/dev/null; then
                print_color $YELLOW "Please enter your password for sudo access:"
            fi
        fi
    else
        INSTALL_DIR="$HOME/.local/bin"
        print_header "User Installation Mode"
        print_color $GREEN "Installing to: $INSTALL_DIR"
        
        # Create user bin directory if it doesn't exist
        mkdir -p "$INSTALL_DIR"
    fi
}

# Function to install Python requirements
install_requirements() {
    print_header "Installing Python Requirements"
    
    local requirements_file="$SCRIPT_DIR/requirements.txt"
    local pip_cmd=""
    
    # Determine pip command
    if command_exists pip3; then
        pip_cmd="pip3"
    elif command_exists pip; then
        pip_cmd="pip"
    else
        print_error "pip not found"
        exit 1
    fi
    
    # Add user flag for user installation
    local pip_flags=""
    if [ "$INSTALL_TO_SYSTEM" = false ]; then
        pip_flags="--user"
    fi
    
    # Install from requirements.txt if it exists
    if [ -f "$requirements_file" ]; then
        print_status "Installing from requirements.txt"
        if [ "$INSTALL_TO_SYSTEM" = true ] && [ "$EUID" -ne 0 ]; then
            sudo $pip_cmd install $pip_flags -r "$requirements_file"
        else
            $pip_cmd install $pip_flags -r "$requirements_file"
        fi
    else
        print_warning "requirements.txt not found, installing core packages manually"
        local packages=("requests>=2.25.0" "PyYAML>=5.4.0" "flask")
        
        for package in "${packages[@]}"; do
            print_status "Installing $package"
            if [ "$INSTALL_TO_SYSTEM" = true ] && [ "$EUID" -ne 0 ]; then
                sudo $pip_cmd install $pip_flags "$package"
            else
                $pip_cmd install $pip_flags "$package"
            fi
        done
    fi
    
    print_status "Python requirements installed successfully"
}

# Function to make entry points executable
make_executable() {
    print_header "Making Entry Point Scripts Executable"
    
    for script in "${ENTRY_POINTS[@]}"; do
        local script_path="$SCRIPT_DIR/$script"
        if [ -f "$script_path" ]; then
            chmod +x "$script_path"
            print_status "Made executable: $script"
        else
            print_warning "Entry point not found: $script"
        fi
    done
    
    # Also make shell scripts executable
    for script in "${SHELL_SCRIPTS[@]}"; do
        local script_path="$SCRIPT_DIR/$script"
        if [ -f "$script_path" ]; then
            chmod +x "$script_path"
            print_status "Made executable: $script"
        else
            print_warning "Shell script not found: $script"
        fi
    done
    
    print_status "Entry point scripts are now executable"
}

# Function to copy files with proper permissions
copy_file() {
    local src="$1"
    local dest="$2"
    local make_exec="$3"
    
    if [ "$INSTALL_TO_SYSTEM" = true ] && [ "$EUID" -ne 0 ]; then
        sudo cp "$src" "$dest"
        if [ "$make_exec" = "true" ]; then
            sudo chmod 755 "$dest"
        else
            sudo chmod 644 "$dest"
        fi
    else
        cp "$src" "$dest"
        if [ "$make_exec" = "true" ]; then
            chmod 755 "$dest"
        else
            chmod 644 "$dest"
        fi
    fi
}

# Function to copy Python modules
copy_modules() {
    print_header "Copying Python Modules to $INSTALL_DIR"
    
    # Ensure install directory exists
    if [ "$INSTALL_TO_SYSTEM" = true ] && [ "$EUID" -ne 0 ]; then
        sudo mkdir -p "$INSTALL_DIR"
    else
        mkdir -p "$INSTALL_DIR"
    fi
    
    local copied_count=0
    local missing_count=0
    
    # Copy Python modules
    for module in "${PYTHON_MODULES[@]}"; do
        local src_path="$SCRIPT_DIR/$module"
        local dest_path="$INSTALL_DIR/$module"
        
        if [ -f "$src_path" ]; then
            # Check if this is an entry point (should be executable)
            local is_entry_point=false
            for entry_point in "${ENTRY_POINTS[@]}"; do
                if [ "$module" = "$entry_point" ]; then
                    is_entry_point=true
                    break
                fi
            done
            
            copy_file "$src_path" "$dest_path" "$is_entry_point"
            print_status "Copied: $module"
            ((copied_count++))
        else
            print_warning "Module not found: $module"
            ((missing_count++))
        fi
    done
    
    # Copy shell scripts
    for script in "${SHELL_SCRIPTS[@]}"; do
        local src_path="$SCRIPT_DIR/$script"
        local dest_path="$INSTALL_DIR/$script"
        
        if [ -f "$src_path" ]; then
            copy_file "$src_path" "$dest_path" "true"
            print_status "Copied: $script"
            ((copied_count++))
        else
            print_warning "Shell script not found: $script"
            ((missing_count++))
        fi
    done
    
    print_status "Copied $copied_count files to $INSTALL_DIR"
    if [ $missing_count -gt 0 ]; then
        print_warning "$missing_count files were not found and skipped"
    fi
}

# Function to verify installation
verify_installation() {
    print_header "Verifying Installation"
    
    local verification_failed=false
    
    # Check if key entry points exist and are executable
    local key_scripts=("prompt_runner.py" "prompt_chain_runner.py" "multi_file_prompt_runner.py")
    
    for script in "${key_scripts[@]}"; do
        local script_path="$INSTALL_DIR/$script"
        if [ -f "$script_path" ] && [ -x "$script_path" ]; then
            print_status "Verified: $script is installed and executable"
        else
            print_error "Failed verification: $script"
            verification_failed=true
        fi
    done
    
    # Test Python imports
    print_status "Testing Python module imports..."
    
    local test_script="$INSTALL_DIR/config_manager.py"
    if [ -f "$test_script" ]; then
        if $PYTHON_CMD -c "import sys; sys.path.insert(0, '$INSTALL_DIR'); import config_manager" 2>/dev/null; then
            print_status "Python modules import successfully"
        else
            print_warning "Python modules may have import issues"
        fi
    fi
    
    if [ "$verification_failed" = true ]; then
        print_error "Installation verification failed"
        return 1
    else
        print_status "Installation verification passed"
        return 0
    fi
}

# Function to show post-installation instructions
show_post_install() {
    print_header "Installation Complete!"
    
    echo
    print_color $GREEN "${BOLD}OpenRouter Interface has been successfully installed!${NC}"
    echo
    
    print_color $CYAN "Installation Summary:"
    print_status "Python modules installed to: $INSTALL_DIR"
    print_status "Entry point scripts are executable"
    print_status "All requirements installed"
    
    echo
    print_color $CYAN "Next Steps:"
    
    # PATH configuration
    if [ "$INSTALL_TO_SYSTEM" = false ]; then
        echo "1. ${BOLD}Add $INSTALL_DIR to your PATH:${NC}"
        print_color $YELLOW "   echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
        print_color $YELLOW "   source ~/.bashrc"
        echo
        echo "   ${BOLD}OR for immediate use in current session:${NC}"
        print_color $YELLOW "   export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo
    else
        print_status "$INSTALL_DIR is typically already in your PATH"
    fi
    
    # API key setup
    echo "2. ${BOLD}Set up your OpenRouter API key:${NC}"
    print_color $YELLOW "   export OPENROUTER_API_KEY=\"your_api_key_here\""
    print_color $YELLOW "   # Add to ~/.bashrc to make it permanent"
    echo
    
    # Usage examples
    echo "3. ${BOLD}Start using the tools:${NC}"
    print_color $YELLOW "   prompt_runner.py                     # Interactive mode"
    print_color $YELLOW "   prompt_runner.py -p prompt.json -i input.md"
    print_color $YELLOW "   prompt_chain_runner.py -c config.yaml"
    print_color $YELLOW "   multi_file_prompt_runner.py"
    print_color $YELLOW "   prompt_runner_flask.py               # Web interface"
    echo
    
    # Help information
    echo "4. ${BOLD}Get help:${NC}"
    print_color $YELLOW "   prompt_runner.py --help"
    print_color $YELLOW "   prompt_chain_runner.py --help"
    print_color $YELLOW "   multi_file_prompt_runner.py --help"
    echo
    
    print_color $GREEN "Setup completed successfully! 🎉"
}

# Function to handle errors
cleanup_on_error() {
    print_error "Setup failed!"
    print_error "Check the error messages above for details"
    exit 1
}

# Main execution function
main() {
    print_color $CYAN "${BOLD}OpenRouter Interface - Linux Setup Script${NC}"
    print_color $CYAN "=========================================="
    echo
    
    # Set error trap
    trap cleanup_on_error ERR
    
    # Parse command line arguments
    parse_arguments "$@"
    
    # Main setup steps
    check_python
    set_install_directory
    install_requirements
    make_executable
    copy_modules
    
    # Verification and completion
    if verify_installation; then
        show_post_install
    else
        print_error "Installation completed with warnings"
        print_error "Some components may not work correctly"
        exit 1
    fi
    
    print_status "All setup steps completed successfully!"
}

# Run main function with all arguments
main "$@"