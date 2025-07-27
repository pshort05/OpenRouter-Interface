#!/bin/bash

# OpenRouter Prompt Runner Flask Application Launcher
# A simple shell script to start the Flask web application with various options

set -e  # Exit on any error

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLASK_APP="prompt_runner_flask.py"
DEFAULT_HOST="127.0.0.1"
DEFAULT_PORT="5000"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    local color=$1
    shift
    echo -e "${color}$*${NC}"
}

# Function to print usage
show_usage() {
    cat << EOF
OpenRouter Prompt Runner Flask Application Launcher

Usage: prompt_runner_flask.sh [OPTIONS]

Options:
    -h, --help              Show this help message
    -H, --host HOST         Host to bind to (default: $DEFAULT_HOST)
    -p, --port PORT         Port to bind to (default: $DEFAULT_PORT)
    -d, --debug             Run in debug mode
    -b, --background        Run in background (daemon mode)
    -s, --setup             Run initial setup (create templates and config)
    -c, --check             Check dependencies and configuration
    -k, --kill              Kill any running instances
    -l, --logs              Show application logs (if running in background)
    --public               Run on all interfaces (0.0.0.0)
    --production           Run in production mode (host=0.0.0.0, no debug)

Examples:
    prompt_runner_flask.sh                      # Start with default settings
    prompt_runner_flask.sh -d                   # Start in debug mode
    prompt_runner_flask.sh -H 0.0.0.0 -p 8080   # Start on all interfaces, port 8080
    prompt_runner_flask.sh --setup              # Run initial setup
    prompt_runner_flask.sh --production         # Production mode
    prompt_runner_flask.sh --background         # Run in background
    prompt_runner_flask.sh --kill               # Stop background instances

Environment Variables:
    OPENROUTER_API_KEY      Required: Your OpenRouter API key
    FLASK_SECRET_KEY        Optional: Flask secret key (auto-generated if not set)

Files Created:
    flask_config.yaml       Application configuration
    prompts_registry.yaml   Prompts registry
    templates/              HTML template directory
    flask_app.log          Application log file (background mode)
    flask_app.pid          Process ID file (background mode)

EOF
}

# Function to check if API key is set
check_api_key() {
    if [ -z "$OPENROUTER_API_KEY" ]; then
        print_color $RED "Error: OPENROUTER_API_KEY environment variable is not set"
        print_color $YELLOW "Please set your OpenRouter API key:"
        print_color $BLUE "export OPENROUTER_API_KEY=\"your_api_key_here\""
        return 1
    fi
    print_color $GREEN "✓ API key is set"
    return 0
}

# Function to check Python dependencies
check_dependencies() {
    print_color $BLUE "Checking Python dependencies..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        print_color $RED "Error: Python 3 is not installed"
        return 1
    fi
    
    print_color $GREEN "✓ Python 3 is available: $(python3 --version)"
    
    # Check required Python packages
    local packages=("flask" "pyyaml" "requests")
    local missing_packages=()
    
    for package in "${packages[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            missing_packages+=("$package")
        else
            print_color $GREEN "✓ $package is installed"
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        print_color $RED "Error: Missing required packages: ${missing_packages[*]}"
        print_color $YELLOW "Install with: pip3 install ${missing_packages[*]}"
        return 1
    fi
    
    return 0
}

# Function to check required files
check_files() {
    print_color $BLUE "Checking required files..."
    
    # Check if Flask app exists
    if [ ! -f "$FLASK_APP" ]; then
        print_color $RED "Error: $FLASK_APP not found in current directory"
        return 1
    fi
    print_color $GREEN "✓ $FLASK_APP found"
    
    # Check for other required Python modules
    local modules=("config_manager.py" "logging_manager.py" "prompt_scanner.py" 
                   "prompt_handler.py" "prompt_runner_api_client.py")
    
    for module in "${modules[@]}"; do
        if [ ! -f "$module" ]; then
            print_color $YELLOW "Warning: $module not found (may be required)"
        else
            print_color $GREEN "✓ $module found"
        fi
    done
    
    # Check if templates directory exists
    if [ ! -d "templates" ]; then
        print_color $YELLOW "Warning: templates/ directory not found"
        print_color $YELLOW "Run with --setup to create templates"
    else
        print_color $GREEN "✓ templates/ directory found"
    fi
    
    return 0
}

# Function to run initial setup
run_setup() {
    print_color $BLUE "Running initial setup..."
    
    # Check if create_templates.py exists
    if [ -f "create_templates.py" ]; then
        print_color $BLUE "Creating templates and configuration..."
        python3 create_templates.py
        print_color $GREEN "✓ Setup completed"
    else
        print_color $YELLOW "Warning: create_templates.py not found"
        print_color $YELLOW "Templates and configuration files may need to be created manually"
    fi
}

# Function to kill running instances
kill_instances() {
    print_color $BLUE "Stopping Flask application instances..."
    
    # Check for PID file
    if [ -f "flask_app.pid" ]; then
        local pid=$(cat flask_app.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_color $GREEN "✓ Stopped background process (PID: $pid)"
        fi
        rm -f flask_app.pid
    fi
    
    # Kill any other Flask processes for this app
    local pids=$(pgrep -f "$FLASK_APP" || true)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill
        print_color $GREEN "✓ Stopped additional Flask processes"
    fi
    
    print_color $GREEN "All instances stopped"
}

# Function to show logs
show_logs() {
    if [ -f "flask_app.log" ]; then
        print_color $BLUE "Showing application logs (press Ctrl+C to exit):"
        tail -f flask_app.log
    else
        print_color $YELLOW "No log file found (flask_app.log)"
    fi
}

# Function to start Flask application
start_flask() {
    local host="$1"
    local port="$2"
    local debug="$3"
    local background="$4"
    
    # Build command
    local cmd="python3 $FLASK_APP --host $host --port $port"
    if [ "$debug" = "true" ]; then
        cmd="$cmd --debug"
    fi
    
    print_color $BLUE "Starting Flask application..."
    print_color $BLUE "Host: $host"
    print_color $BLUE "Port: $port"
    print_color $BLUE "Debug: $debug"
    print_color $BLUE "Background: $background"
    
    if [ "$background" = "true" ]; then
        # Run in background
        nohup $cmd > flask_app.log 2>&1 &
        local pid=$!
        echo $pid > flask_app.pid
        print_color $GREEN "✓ Flask application started in background (PID: $pid)"
        print_color $BLUE "Access at: http://$host:$port"
        print_color $BLUE "Logs: tail -f flask_app.log"
        print_color $BLUE "Stop with: prompt_runner_flask.sh --kill"
    else
        # Run in foreground
        print_color $GREEN "✓ Starting Flask application..."
        print_color $BLUE "Access at: http://$host:$port"
        print_color $BLUE "Press Ctrl+C to stop"
        echo
        exec $cmd
    fi
}

# Parse command line arguments
HOST="$DEFAULT_HOST"
PORT="$DEFAULT_PORT"
DEBUG="false"
BACKGROUND="false"
SETUP="false"
CHECK_ONLY="false"
KILL_ONLY="false"
SHOW_LOGS="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -H|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -d|--debug)
            DEBUG="true"
            shift
            ;;
        -b|--background)
            BACKGROUND="true"
            shift
            ;;
        -s|--setup)
            SETUP="true"
            shift
            ;;
        -c|--check)
            CHECK_ONLY="true"
            shift
            ;;
        -k|--kill)
            KILL_ONLY="true"
            shift
            ;;
        -l|--logs)
            SHOW_LOGS="true"
            shift
            ;;
        --public)
            HOST="0.0.0.0"
            shift
            ;;
        --production)
            HOST="0.0.0.0"
            DEBUG="false"
            shift
            ;;
        *)
            print_color $RED "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Change to script directory
cd "$SCRIPT_DIR"

# Handle special modes
if [ "$KILL_ONLY" = "true" ]; then
    kill_instances
    exit 0
fi

if [ "$SHOW_LOGS" = "true" ]; then
    show_logs
    exit 0
fi

if [ "$SETUP" = "true" ]; then
    run_setup
    if [ "$CHECK_ONLY" = "false" ]; then
        exit 0
    fi
fi

# Run checks
print_color $BLUE "OpenRouter Prompt Runner Flask Launcher"
print_color $BLUE "========================================="

if ! check_api_key; then
    exit 1
fi

if ! check_dependencies; then
    exit 1
fi

if ! check_files; then
    exit 1
fi

if [ "$CHECK_ONLY" = "true" ]; then
    print_color $GREEN "All checks passed!"
    exit 0
fi

# Generate Flask secret key if not set
if [ -z "$FLASK_SECRET_KEY" ]; then
    export FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")
    print_color $BLUE "Generated Flask secret key"
fi

# Start the application
start_flask "$HOST" "$PORT" "$DEBUG" "$BACKGROUND"