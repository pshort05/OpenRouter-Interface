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

# Check pandoc installation
echo "📦 Checking pandoc installation..."
if command -v pandoc >/dev/null 2>&1; then
    PANDOC_VERSION=$(pandoc --version | head -n 1)
    echo "✅ Pandoc found: $PANDOC_VERSION"
else
    echo "⚠️  Pandoc not found - required for file conversion features"
    echo "   Installing pandoc..."

    # Detect OS and install pandoc
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get >/dev/null 2>&1; then
            echo "   Detected Debian/Ubuntu - installing via apt-get"
            sudo apt-get update && sudo apt-get install -y pandoc
        elif command -v yum >/dev/null 2>&1; then
            echo "   Detected RedHat/CentOS - installing via yum"
            sudo yum install -y pandoc
        elif command -v pacman >/dev/null 2>&1; then
            echo "   Detected Arch Linux - installing via pacman"
            sudo pacman -S --noconfirm pandoc
        else
            echo "   ⚠️  Could not auto-install pandoc on this Linux distribution"
            echo "      Please install manually: https://pandoc.org/installing.html"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew >/dev/null 2>&1; then
            echo "   Detected macOS - installing via Homebrew"
            brew install pandoc
        else
            echo "   ⚠️  Homebrew not found. Please install pandoc manually:"
            echo "      Visit: https://pandoc.org/installing.html"
        fi
    else
        echo "   ⚠️  Unsupported OS: $OSTYPE"
        echo "      Please install pandoc manually: https://pandoc.org/installing.html"
    fi

    # Verify pandoc was installed
    if command -v pandoc >/dev/null 2>&1; then
        PANDOC_VERSION=$(pandoc --version | head -n 1)
        echo "   ✅ Pandoc installed successfully: $PANDOC_VERSION"
    else
        echo "   ⚠️  Pandoc installation failed or not in PATH"
        echo "      File conversion features will not be available"
        echo "      Install manually from: https://pandoc.org/installing.html"
    fi
fi

echo ""
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
    echo "🌐 Installing web interface dependencies..."
    pip install flask werkzeug
    pip install -e ".[web]"
    echo "✅ Installed with web interface support"
elif [ "$1" = "dev" ]; then
    pip install -e ".[dev]"
    echo "✅ Installed with development tools"
elif [ "$1" = "all" ]; then
    echo "🌐 Installing all dependencies..."
    pip install flask werkzeug
    pip install -e ".[all]"
    echo "✅ Installed with all features"
else
    pip install -e .
    echo "✅ Installed basic version"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
if command -v pandoc >/dev/null 2>&1; then
    echo "✅ File conversion features available (pandoc installed)"
else
    echo "⚠️  File conversion disabled - pandoc not installed"
    echo "   Install from: https://pandoc.org/installing.html"
fi
echo ""
echo "🚀 Quick Start:"
echo "1. Set up your API key:"
echo "   ./setup-api-key.sh"
echo ""
echo "2. Start the web interface:"
echo "   ./start-web.sh"
echo ""
echo "🔧 Manual Usage:"
echo "1. Activate the virtual environment:"
echo "   source openrouter-venv/bin/activate"
echo ""
echo "2. Run individual applications:"
echo "   openrouter-runner      # CLI interface"
echo "   openrouter-web         # Web interface"
echo "   openrouter-chain       # Chain runner"
echo "   split-chapters         # Chapter splitter utility"
echo ""
echo "3. When done, deactivate:"
echo "   deactivate"
echo ""
echo "📚 See docs/QUICK-START.md for detailed usage instructions."