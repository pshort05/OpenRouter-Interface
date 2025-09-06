#!/bin/bash
# OpenRouter Web Interface Startup Script
# Starts the web interface in production mode with proper setup

set -e

echo "🌐 OpenRouter Web Interface Starter"
echo "=================================="

# Check if virtual environment exists and is activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "openrouter-venv" ]; then
        echo "🔧 Activating virtual environment..."
        source openrouter-venv/bin/activate
    else
        echo "❌ Error: No virtual environment found"
        echo "Please run ./install.sh first to set up the environment"
        exit 1
    fi
fi

# Check if API key is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️  Warning: OPENROUTER_API_KEY not set"
    read -p "Do you want to set it up now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./setup-api-key.sh
        # Source bashrc to get the new API key
        source ~/.bashrc
    else
        echo "❌ API key required. Run ./setup-api-key.sh first"
        exit 1
    fi
fi

# Check if templates exist
if [ ! -d "templates" ]; then
    echo "📋 Creating templates directory..."
    python3 -c "
try:
    from src.openrouter_interface.create_templates import main
    main()
    print('✅ Templates created successfully')
except Exception as e:
    print(f'❌ Error creating templates: {e}')
    exit(1)
    "
fi

echo ""
echo "🚀 Starting OpenRouter Web Interface..."

# Start the web application
if [ "$1" = "--debug" ] || [ "$1" = "-d" ]; then
    echo "🛠️  Starting in debug mode..."
    openrouter-web --debug --foreground
elif [ "$1" = "--foreground" ] || [ "$1" = "-f" ]; then
    echo "🖥️  Starting in foreground mode..."
    openrouter-web --foreground
else
    echo "🏭 Starting in production mode (background)..."
    openrouter-web
    echo ""
    echo "🎉 Web server is now running in the background!"
    echo ""
    echo "📖 Usage:"
    echo "  • Web interface is accessible from any device on your network"
    echo "  • Check flask_app.log for server logs"  
    echo "  • To run in foreground: ./start-web.sh --foreground"
    echo "  • To run in debug mode: ./start-web.sh --debug"
    echo ""
fi