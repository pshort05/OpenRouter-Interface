#!/bin/bash
"""
Development Environment Setup Script for OpenRouter Interface

Sets up a complete development environment with all tools and dependencies.
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_status "Setting up OpenRouter Interface development environment..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

# Create virtual environment
print_status "Creating virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Removing..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate
print_success "Virtual environment created and activated"

# Upgrade pip and install build tools
print_status "Upgrading pip and installing build tools..."
pip install --upgrade pip setuptools wheel build

# Install package in development mode with all dependencies
print_status "Installing package in development mode..."
pip install -e ".[all]"

# Install additional development tools
print_status "Installing additional development tools..."
pip install pre-commit tox-dev sphinx sphinx-rtd-theme

# Set up pre-commit hooks
print_status "Setting up pre-commit hooks..."
pre-commit install

# Create development directories
print_status "Creating development directories..."
mkdir -p tests/unit tests/integration tests/fixtures
mkdir -p docs/api docs/examples

# Create basic test files if they don't exist
if [ ! -f "tests/test_basic.py" ]; then
    cat > tests/test_basic.py << 'EOF'
"""Basic tests for OpenRouter Interface."""

import pytest
from openrouter_interface import ConfigManager, PromptScanner


def test_package_imports():
    """Test that main package imports work."""
    # This test passes if the imports above don't raise ImportError
    assert True


def test_config_manager_creation():
    """Test that ConfigManager can be created."""
    config = ConfigManager()
    assert config is not None


def test_prompt_scanner_creation():
    """Test that PromptScanner can be created.""" 
    scanner = PromptScanner()
    assert scanner is not None
EOF
    print_success "Created basic test file"
fi

# Create tox configuration
if [ ! -f "tox.ini" ]; then
    cat > tox.ini << 'EOF'
[tox]
envlist = py37,py38,py39,py310,py311,py312,flake8,mypy
isolated_build = True

[testenv]
deps = 
    pytest
    pytest-cov
commands = 
    pytest {posargs}

[testenv:flake8]
deps = flake8
commands = flake8 src tests

[testenv:mypy]
deps = 
    mypy
    types-PyYAML
    types-requests
commands = mypy src

[testenv:docs]
deps = 
    sphinx
    sphinx-rtd-theme
commands = 
    sphinx-build -b html docs docs/_build/html
EOF
    print_success "Created tox.ini configuration"
fi

# Create pre-commit configuration
if [ ! -f ".pre-commit-config.yaml" ]; then
    cat > .pre-commit-config.yaml << 'EOF'
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
    -   id: check-merge-conflict
    -   id: debug-statements

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black

-   repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
    -   id: flake8

-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
    -   id: mypy
        additional_dependencies: [types-PyYAML, types-requests]
EOF
    print_success "Created pre-commit configuration"
fi

# Run initial tests
print_status "Running initial tests..."
python -m pytest tests/ -v

# Run linting
print_status "Running code quality checks..."
flake8 src --statistics || print_warning "Flake8 found issues"
mypy src || print_warning "MyPy found issues"

print_success "Development environment setup completed!"

echo
print_status "Development tools available:"
echo "  pytest                 - Run tests"
echo "  flake8 src            - Check code style"
echo "  mypy src              - Check type annotations"
echo "  black src tests       - Format code"
echo "  pre-commit run --all  - Run all pre-commit hooks"
echo "  tox                   - Test across multiple Python versions"

echo
print_status "To activate this environment later:"
echo "  source venv/bin/activate"

echo
print_status "Project structure:"
echo "  src/openrouter_interface/  - Main package"
echo "  tests/                     - Test files"
echo "  docs/                      - Documentation"
echo "  prompts/                   - JSON prompt files"
echo "  config/                    - Configuration files"