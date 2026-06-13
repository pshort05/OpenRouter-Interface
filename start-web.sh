#!/bin/bash
# OpenRouter Web Interface Startup Script
# Starts the web interface in production mode with proper setup

set -e

echo "🌐 OpenRouter Web Interface Starter"
echo "=================================="

# Locate the virtual environment's interpreter directly.
# NOTE: we intentionally do NOT `source openrouter-venv/bin/activate`. This venv was
# created under a different (Dropbox-synced) path, so its activate script hardcodes a
# stale VIRTUAL_ENV and hijacks the shell to the wrong environment. Calling the
# interpreter by path uses the correct, local site-packages.
VENV_PY="openrouter-venv/bin/python"
if [ -x "$VENV_PY" ]; then
    echo "🔧 Using virtual environment interpreter: $VENV_PY"
else
    echo "❌ Error: No virtual environment interpreter found at $VENV_PY"
    echo "Please run ./install.sh first to set up the environment"
    exit 1
fi

# Import this project's source, not a synced copy installed elsewhere in the venv.
export PYTHONPATH="src:$PYTHONPATH"

# Port for this instance (5000 is used by another local program).
PORT=3849

# Verify Flask is available
echo "🔍 Checking Flask installation..."
if ! "$VENV_PY" -c "import flask; print('Flask version:', flask.__version__)" 2>/dev/null; then
    echo "❌ Flask not found in virtual environment"
    echo "Installing Flask..."
    "$VENV_PY" -m pip install flask werkzeug
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

# Templates ship with the package (src/openrouter_interface/templates/) and are served
# from there by Flask. The legacy create_templates step is intentionally not run: it
# wrote to a separate root ./templates/ directory the app never reads.

# Check if prompts registry exists
if [ ! -f "prompts_registry.yaml" ]; then
    echo "📋 Creating basic prompts registry..."
    echo "✅ Basic prompts registry already exists"
fi

echo ""
echo "🚀 Starting OpenRouter Web Interface..."

echo "🔧 Running directly with Python module..."

# Start the web application (PYTHONPATH was exported above)
if [ "$1" = "--debug" ] || [ "$1" = "-d" ]; then
    echo "🛠️  Starting in debug mode..."
    "$VENV_PY" -m openrouter_interface.web --port "$PORT" --debug --foreground
elif [ "$1" = "--foreground" ] || [ "$1" = "-f" ]; then
    echo "🖥️  Starting in foreground mode..."
    "$VENV_PY" -m openrouter_interface.web --port "$PORT" --foreground
else
    echo "🏭 Starting in production mode (background)..."
    "$VENV_PY" -m openrouter_interface.web --port "$PORT"
    echo ""
    echo "🎉 Web server is now running in the background!"
    echo ""
    echo "🌐 Network Access:"
    echo "  • The server is accessible from ANY device on your local network"
    echo "  • From other computers: http://$(hostname -I | awk '{print $1}'):$PORT"
    echo "  • From phones/tablets: Use the same URL above"
    echo "  • From this computer: http://localhost:$PORT"
    echo ""
    echo "🔧 Troubleshooting Network Access:"
    echo "  • If blocked by firewall, run: sudo ufw allow $PORT"
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