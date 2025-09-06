#!/bin/bash
"""
OpenRouter Interface Installation Script

This script installs the OpenRouter Interface package in development mode.
Follows Python best practices for package installation.
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -f "setup.py" ]; then
    print_error "This script must be run from the project root directory"
    print_error "Expected files: pyproject.toml, setup.py"
    exit 1
fi

print_status "Starting OpenRouter Interface installation..."

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
    print_success "Python $python_version is compatible (>= 3.7)"
else
    print_error "Python 3.7 or higher is required. Found: $python_version"
    exit 1
fi

# Create virtual environment if requested
if [ "$1" = "--venv" ] || [ "$1" = "--virtual-env" ]; then
    print_status "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
fi

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install the package in development mode
print_status "Installing OpenRouter Interface in development mode..."
pip install -e .

# Install optional dependencies based on arguments
if [ "$1" = "--web" ] || [ "$2" = "--web" ]; then
    print_status "Installing web dependencies..."
    pip install -e ".[web]"
fi

if [ "$1" = "--dev" ] || [ "$2" = "--dev" ]; then
    print_status "Installing development dependencies..."
    pip install -e ".[dev]"
fi

if [ "$1" = "--all" ] || [ "$2" = "--all" ]; then
    print_status "Installing all dependencies..."
    pip install -e ".[all]"
fi

# Verify installation
print_status "Verifying installation..."

# Check if console scripts are available
if command -v openrouter-runner >/dev/null 2>&1; then
    print_success "CLI tool installed: openrouter-runner"
else
    print_warning "CLI tool not found in PATH. You may need to add pip's bin directory to your PATH"
fi

# Test package import
if python3 -c "import openrouter_interface; print(f'Package version: {openrouter_interface.__version__}')" 2>/dev/null; then
    print_success "Package imports successfully"
else
    print_error "Package import failed"
    exit 1
fi

print_success "Installation completed successfully!"

echo
print_status "Usage examples:"
echo "  CLI: openrouter-runner --help"
echo "  Web: openrouter-web"
echo "  Chain: openrouter-chain --help" 
echo "  BookGen: bookgen --help"
echo
echo "  Or use Python module:"
echo "  python -m openrouter_interface.cli --help"
echo "  python -m openrouter_interface.web"

# Show next steps
echo
print_status "Next steps:"
echo "1. Set your API key: export OPENROUTER_API_KEY='your-key-here'"
echo "2. Run the quick start: openrouter-runner --help"
echo "3. Check the documentation in docs/"

# Deactivate virtual environment if we created one
if [ "$1" = "--venv" ] || [ "$1" = "--virtual-env" ]; then
    print_status "To activate the virtual environment later, run:"
    echo "  source venv/bin/activate"
fi