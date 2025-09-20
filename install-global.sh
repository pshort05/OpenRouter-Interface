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

echo "📦 Installing OpenRouter Interface package globally..."

# First, uninstall any existing installation
pip3 uninstall openrouter-interface -y 2>/dev/null || echo "No previous installation found"

# Install the package globally using pip (try different approaches)
if pip3 install . --force-reinstall 2>/dev/null; then
    echo "✅ Installed using standard pip install"
elif pip3 install . --user --force-reinstall 2>/dev/null; then
    echo "✅ Installed to user directory"
    echo "⚠️  Make sure ~/.local/bin is in your PATH"
else
    echo "❌ Installation failed. Try running with sudo or use virtual environment"
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
echo "   2. Verify installation:"
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