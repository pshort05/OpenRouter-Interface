#!/bin/bash
# Installation script for OpenRouter Interface
# Handles systems with disabled user site-packages

set -e

echo "🚀 OpenRouter Interface Installation Script"
echo "==========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3.7+"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv openrouter-venv

# Activate virtual environment  
echo "🔧 Activating virtual environment..."
source openrouter-venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install the package
echo "📥 Installing OpenRouter Interface..."
if [ "$1" = "web" ] || [ "$1" = "all" ]; then
    pip install -e ".[web]"
    echo "✅ Installed with web interface support"
elif [ "$1" = "dev" ]; then
    pip install -e ".[dev]"
    echo "✅ Installed with development tools"
elif [ "$1" = "all" ]; then
    pip install -e ".[all]"
    echo "✅ Installed with all features"
else
    pip install -e .
    echo "✅ Installed basic version"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To use OpenRouter Interface:"
echo "1. Activate the virtual environment:"
echo "   source openrouter-venv/bin/activate"
echo ""
echo "2. Set your API key:"
echo "   export OPENROUTER_API_KEY=\"your-api-key-here\""
echo ""
echo "3. Run the applications:"
echo "   openrouter-runner      # CLI interface"  
echo "   openrouter-web         # Web interface"
echo "   openrouter-chain       # Chain runner"
echo ""
echo "4. When done, deactivate:"
echo "   deactivate"
echo ""
echo "📚 See docs/QUICK-START.md for detailed usage instructions."