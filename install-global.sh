#!/bin/bash
# OpenRouter Interface Global Installer
# Installs the package globally so CLI commands work from any directory

set -e

echo "🔧 OpenRouter Interface Global Installer"
echo "========================================"

# Check if we're in a virtual environment
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "⚠️  You are in a virtual environment: $VIRTUAL_ENV"
    echo "   This installer will install globally. Continue? (y/N)"
    read -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled"
        exit 1
    fi
fi

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
echo "📦 Installing OpenRouter Interface package globally..."

# First, uninstall any existing installation (both system and user)
pip3 uninstall openrouter-interface -y 2>/dev/null || echo "No previous system installation found"
pip3 uninstall openrouter-interface -y --user 2>/dev/null || echo "No previous user installation found"

# Install the package globally using pip (try different approaches)
if pip3 install . --user --force-reinstall --no-deps 2>/dev/null; then
    echo "✅ Installed to user directory (without dependencies)"
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo "⚠️  ~/.local/bin is not in your PATH"
        echo "   Add it by running: echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
        echo "   Then restart your terminal or run: source ~/.bashrc"
    else
        echo "✅ ~/.local/bin is already in your PATH"
    fi
elif pip3 install . --force-reinstall --break-system-packages --no-deps 2>/dev/null; then
    echo "✅ Installed using system packages override (without dependencies)"
    echo "ℹ️  Using existing system dependencies"
elif command -v pipx >/dev/null 2>&1 && pipx install . --force 2>/dev/null; then
    echo "✅ Installed using pipx"
    echo "ℹ️  pipx manages isolated environments automatically"
else
    echo "❌ Installation failed. Solutions:"
    echo "   1. Install to user directory: pip3 install . --user --no-deps"
    echo "   2. Use pipx: pipx install ."
    echo "   3. Create virtual environment: python3 -m venv venv && source venv/bin/activate && pip install ."
    echo "   4. Override system protection: pip3 install . --break-system-packages --no-deps"
    exit 1
fi

echo ""
echo "✅ Installation completed!"
echo ""
echo "🚀 Available Commands:"
echo "   • openrouter-runner    - CLI prompt runner"
echo "   • openrouter-chain     - Chain multiple prompts"
echo "   • openrouter-web       - Web interface"
echo "   • bookgen              - Book generation tool"
echo "   • split-chapters       - Split documents by chapters"
echo ""
echo "📖 Usage Examples:"
echo "   # Interactive mode (from any directory)"
echo "   openrouter-runner"
echo ""
echo "   # Batch mode with specific files"
echo "   openrouter-runner -p /path/to/prompt.json -i /path/to/input.md"
echo ""
echo "   # Chain processing"
echo "   openrouter-chain -c /path/to/chain_config.yaml"
echo ""
echo "   # Web interface"
echo "   openrouter-web --debug --foreground"
echo ""
echo "🔑 Setup Requirements:"
echo "   1. Set your OpenRouter API key:"
echo "      export OPENROUTER_API_KEY='your-api-key-here'"
echo "      echo 'export OPENROUTER_API_KEY=\"your-api-key-here\"' >> ~/.bashrc"
echo ""
echo "   2. File conversion support (optional):"
if command -v pandoc >/dev/null 2>&1; then
    echo "      ✅ Pandoc is installed - file conversion available"
else
    echo "      ⚠️  Pandoc not installed - file conversion disabled"
    echo "      Install: https://pandoc.org/installing.html"
fi
echo ""
echo "   3. Verify installation:"
echo "      openrouter-runner --help"
echo ""
echo "📁 Configuration Files:"
echo "   • Default config files will be looked for in the current directory"
echo "   • You can specify custom paths using the -c/--config option"
echo "   • Prompt files can be anywhere - specify full paths"
echo ""

# Test if the commands are available
echo "🧪 Testing installation..."
if command -v openrouter-runner >/dev/null 2>&1; then
    echo "✅ openrouter-runner command available"
else
    echo "❌ openrouter-runner command not found in PATH"
    echo "   You may need to restart your terminal or add ~/.local/bin to your PATH"
fi

if command -v openrouter-chain >/dev/null 2>&1; then
    echo "✅ openrouter-chain command available"
else
    echo "❌ openrouter-chain command not found in PATH"
fi

echo ""
echo "🎉 Installation complete! You can now use the OpenRouter tools from any directory."