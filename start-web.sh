#!/bin/bash
# OpenRouter Web Interface Startup Script
# Starts the web interface in production mode with proper setup

set -e

echo "🌐 OpenRouter Web Interface Starter"
echo "=================================="

# Check if virtual environment exists and activate it
if [ -d "openrouter-venv" ]; then
    echo "🔧 Activating virtual environment..."
    source openrouter-venv/bin/activate
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Error: No virtual environment found"
    echo "Please run ./install.sh first to set up the environment"
    exit 1
fi

# Verify Flask is available
echo "🔍 Checking Flask installation..."
if ! python3 -c "import flask; print('Flask version:', flask.__version__)" 2>/dev/null; then
    echo "❌ Flask not found in virtual environment"
    echo "Installing Flask..."
    pip install flask werkzeug
    echo "✅ Flask installed"
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
import sys
sys.path.insert(0, 'src')
try:
    from openrouter_interface.create_templates import main
    main()
    print('✅ Templates created successfully')
except Exception as e:
    print('❌ Error creating templates:', str(e))
    import sys
    sys.exit(1)
    "
fi

echo ""
echo "🚀 Starting OpenRouter Web Interface..."

# Verify the command is available
echo "🔍 Checking openrouter-web command..."
if ! command -v openrouter-web >/dev/null 2>&1; then
    echo "❌ openrouter-web command not found"
    echo "🔧 Trying to reinstall the package..."
    pip install -e ".[web]"
    
    # Check again
    if ! command -v openrouter-web >/dev/null 2>&1; then
        echo "❌ Still cannot find openrouter-web command"
        echo "🔧 Running directly with Python..."
        
        # Run directly
        if [ "$1" = "--debug" ] || [ "$1" = "-d" ]; then
            echo "🛠️  Starting in debug mode..."
            python3 -m openrouter_interface.web --debug --foreground
        elif [ "$1" = "--foreground" ] || [ "$1" = "-f" ]; then
            echo "🖥️  Starting in foreground mode..."
            python3 -m openrouter_interface.web --foreground
        else
            echo "🏭 Starting in production mode (background)..."
            python3 -m openrouter_interface.web
        fi
        exit 0
    fi
fi

echo "✅ openrouter-web command found"

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
    echo "🌐 Network Access:"
    echo "  • The server is accessible from ANY device on your local network"
    echo "  • From other computers: http://$(hostname -I | awk '{print $1}'):5000"
    echo "  • From phones/tablets: Use the same URL above"
    echo "  • From this computer: http://localhost:5000"
    echo ""
    echo "🔧 Troubleshooting Network Access:"
    echo "  • If blocked by firewall, run: sudo ufw allow 5000"
    echo "  • Check your local IP: ip addr show | grep 'inet '"
    echo "  • Server logs: tail -f openrouter_web.log"
    echo ""
    echo "📖 Usage Options:"
    echo "  • To run in foreground: ./start-web.sh --foreground"
    echo "  • To run in debug mode: ./start-web.sh --debug"
    echo "  • To stop server: pkill -f 'flask\|openrouter-web\|run-flask-background'"
    echo "  • Direct background start: python3 run-flask-background.py"
    echo ""
fi